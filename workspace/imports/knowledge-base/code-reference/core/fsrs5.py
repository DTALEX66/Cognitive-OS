"""fsrs5.py — FSRS-5 (Free Spaced Repetition Scheduler) 纯Python实现
替换 legacy SM-2 算法，基于 open-spaced-repetition 规范。

参考资料:
  https://github.com/open-spaced-repetition/py-fsrs
  https://github.com/open-spaced-repetition/fsrs4anki/wiki/The-Algorithm

FSRS-5 核心概念:
  - R (Retrievability): 记忆可提取概率，随时间衰减
  - S (Stability): 记忆稳定性，决定衰减速度
  - D (Difficulty): 卡片难度，影响稳定度增长
  - w[]: 19个权重参数控制遗忘曲线形状

与 SM-2 区别:
  - FSRS 使用指数遗忘曲线，而非 SM-2 的固定倍数增长
  - FSRS 支持 target retention 设定（默认90%）
  - FSRS 分离了难度和稳定度两个维度
  - FSRS 基于真实用户数据优化（百万级）, SM-2 是启发式经验
"""
from __future__ import annotations
import math
import time
from datetime import datetime, timezone
from dataclasses import dataclass, field
from typing import Optional


# FSRS-5 默认权重 (19个参数)
# 来源: https://github.com/open-spaced-repetition/fsrs4anki
# ═══════════════════════════════════════════════════════════════════════════
# OPTIMIZED WEIGHTS (generated 2026-06-23 via fsrs_optimizer.py)
# Source: backend/optimized_fsrs_weights.json
# Improved RMSE from 0.3748 to 0.3628 (3.2% improvement on 50 reviews)
# ═══════════════════════════════════════════════════════════════════════════
DEFAULT_W = (
    0.7321,   # w[0]: initial stability, again
    0.2523,   # w[1]: initial stability, hard
    3.3699,   # w[2]: initial stability, good
    6.3331,   # w[3]: initial stability, easy
    4.6525,   # w[4]: initial difficulty
    0.5091,   # w[5]: difficulty linear term
    0.6121,   # w[6]: difficulty update: d += w[6]*(grade-3)
    0.1827,   # w[7]: mean reversion strength
    2.6131,   # w[8]: stability exponent for success
    0.7642,   # w[9]: difficulty factor for stability
    0.4919,   # w[10]: S exponent for stability growth
    2.7340,   # w[11]: short-term stability exponent
    0.0010,   # w[12]: short-term stability grade factor
    0.3602,   # w[13]: short-term difficulty factor
    0.4679,   # w[14]: retrievability influence on S
    0.0010,   # w[15]: post-lapse stability multiplier
    3.1727,   # w[16]: post-lapse stability exponent
    0.2386,   # w[17]: forgetting index (decay control)
    0.6138,   # w[18]: same-day review bonus
)

SCORE_BREAKPOINTS = (0.3, 0.6, 0.9)

DECAY = -0.5  # 遗忘曲线指数参数
FACTOR = 19.0 / 81.0  # 稳定度增长因子

MINUTE = 60
HOUR = 3600
DAY = 86400


def score_to_grade(score: float) -> int:
    """SM-2 score (0.0-1.0) -> FSRS grade (1-4: again/hard/good/easy)"""
    if score < SCORE_BREAKPOINTS[0]:
        return 1  # again
    elif score < SCORE_BREAKPOINTS[1]:
        return 2  # hard
    elif score < SCORE_BREAKPOINTS[2]:
        return 3  # good
    else:
        return 4  # easy


def _ts() -> str:
    return datetime.now(timezone.utc).isoformat()


def _now_sec() -> float:
    return time.time()


@dataclass
class FSRSState:
    """FSRS 卡片状态，存储在 cards 表的扩展列或 metadata 中"""
    stability: float = 1.0       # S: 记忆稳定性
    difficulty: float = 5.0      # D: 难度 (1-10, 初始5)
    elapsed_days: float = 0.0
    scheduled_days: float = 0.0
    reps: int = 0
    lapses: int = 0
    last_review: float = 0.0     # unix timestamp
    state: int = 0               # 0=new, 1=learning, 2=review, 3=relearning

    @staticmethod
    def from_card(card: dict) -> "FSRSState":
        """从卡片数据恢复FSRS状态"""
        s = FSRSState()
        s.reps = card.get("review_count", 0)
        # 从 memory_strength 反向映射 stability (近似)
        str_val = card.get("memory_strength", 0.0)
        s.stability = max(0.1, str_val * 30.0)  # 将0-1映射到1-30天
        s.difficulty = card.get("difficulty", 5.0)
        s.elapsed_days = 0.0
        s.scheduled_days = float(card.get("interval_seconds", DAY)) / DAY
        s.state = 2 if s.reps > 0 else 0
        s.lapses = card.get("lapses", 0)
        # last_review
        la = card.get("last_review_at")
        if la:
            try:
                dt = datetime.fromisoformat(str(la).replace("Z", "+00:00"))
                s.last_review = dt.timestamp()
            except (ValueError, TypeError):
                s.last_review = _now_sec()
        else:
            s.last_review = _now_sec()
        return s


class FSRS5:
    """FSRS-5 调度器"""

    def __init__(
        self,
        w: tuple[float, ...] = DEFAULT_W,
        request_retention: float = 0.9,
        maximum_interval: int = 36500,
        enable_short_term: bool = True,
    ):
        self.w = w
        self.request_retention = request_retention
        self.maximum_interval = maximum_interval
        self.enable_short_term = enable_short_term

    # ---- Retrievability ----
    def retrievability(self, elapsed_days: float, stability: float) -> float:
        """计算在给定天数后可提取的概率 R(t) = exp(-t/S)"""
        if stability <= 0:
            return 0.0
        return math.exp(math.log(self.request_retention) * elapsed_days / stability)

    # ---- Stability update ----
    def _next_stability(
        self, difficulty: float, stability: float, retrievability: float,
        grade: int, is_short_term: bool = False
    ) -> float:
        """计算下一次复习后的稳定度"""
        if grade == 1:
            # Again: 稳定度重置
            s = self.w[0] * (11.0 - difficulty) ** (-self.w[1])
            s = max(0.1, min(s, 36500))
            return s

        if is_short_term:
            # 短期记忆的稳定性增长
            s = stability * math.exp(self.w[12] * (difficulty + self.w[13]))
        else:
            # 长期记忆: S' = S * (1 + exp(w[9]) * (11-D)^w[10] * S^(-w[11]) * (R-1))
            hard_penalty = 1.0 if grade >= 3 else self.w[14]
            bonus = math.exp(self.w[9]) * (11.0 - difficulty) ** self.w[10]
            bonus *= stability ** (-self.w[11])
            bonus *= math.exp((1.0 - retrievability) * self.w[15]) - 1.0
            bonus *= hard_penalty

            s = stability * (1.0 + max(0.0, bonus))

        s = max(0.1, min(s, self.maximum_interval))
        return s

    # ---- Difficulty update ----
    def _next_difficulty(self, difficulty: float, grade: int) -> float:
        """更新卡片难度 D' = D + w[4] * (grade-3) + w[5]"""
        # Mean reversion
        mean_reversion = self.w[7] * (self.w[4] - difficulty)
        # Grade effect
        grade_effect = -self.w[6] * (grade - 3.0)
        d = difficulty + grade_effect + mean_reversion
        d = max(1.0, min(10.0, d))
        return d

    # ---- Next interval ----
    def _next_interval(self, stability: float) -> int:
        """计算下一次复习间隔 (秒)"""
        # I = S * ln(request_retention) / ln(0.9)
        interval_days = stability / FACTOR * (self.request_retention ** (1.0 / DECAY) - 1.0)
        interval_days = min(interval_days, self.maximum_interval)
        interval_days = max(1.0, interval_days)
        return int(interval_days * DAY)

    # ---- Main review method ----
    def review(
        self,
        card: dict,
        score: float,
        now: Optional[float] = None,
    ) -> dict:
        """
        执行一次复习，返回更新后的卡片状态。

        Args:
            card: 数据库卡片字典 (需包含 memory_strength, review_count, interval_seconds, last_review_at)
            score: 复习评分 0.0(全忘) ~ 1.0(完美)
            now: 当前时间戳 (None则使用当前时间)

        Returns:
            dict with: strength, difficulty, interval_seconds, next_review_at, grade
        """
        if now is None:
            now = _now_sec()

        state = FSRSState.from_card(card)
        grade = score_to_grade(score)

        # 计算已过天数
        elapsed_sec = now - state.last_review
        elapsed_days = max(0.0, elapsed_sec / DAY)

        # 可提取性
        r = self.retrievability(elapsed_days, state.stability)

        # 短/长期判断
        is_short_term = state.reps == 0 or elapsed_days < 1.0

        # 更新难度
        difficulty = self._next_difficulty(state.difficulty, grade)

        # 更新稳定度
        stability = self._next_stability(difficulty, state.stability, r, grade, is_short_term)

        # 更新lapses
        lapses = state.lapses + (1 if grade == 1 else 0)

        # 计算下次间隔
        if grade == 1:
            # Again: 短间隔重学
            interval_seconds = DAY
        else:
            interval_seconds = self._next_interval(stability)

        next_review = datetime.fromtimestamp(now + interval_seconds, tz=timezone.utc).isoformat()

        # 将 stability 映射回 0-1 范围给 memory_strength
        memory_strength = min(1.0, stability / 30.0)

        return {
            "memory_strength": round(memory_strength, 4),
            "difficulty": round(difficulty, 2),
            "stability": round(stability, 2),
            "interval_seconds": interval_seconds,
            "next_review_at": next_review,
            "grade": grade,
            "retrievability": round(r, 4),
            "lapses": lapses,
            "review_count": state.reps + 1,
        }

    def review_all_ratings(self, card, score, now=None):
        ratings = {"again": 0.0, "hard": 0.3, "good": 0.6, "easy": 1.0}
        return {r: self.review(card, s, now) for r, s in ratings.items()}

