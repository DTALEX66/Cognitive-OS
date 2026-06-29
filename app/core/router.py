from __future__ import annotations

from typing import Literal

from app.schemas import AttentionDecision, CoreObject
from app.ingestion.quality import ContentQuality, assess_content_quality

RouteName = Literal['KB', 'IR', 'TASK']

RISK_KEYWORDS = [
    'rm -rf', 'delete system', 'format disk', 'registry', 'regedit', 'erase disk', 'wipe disk',
    'credential', 'secret', 'private key', 'api key', 'token', 'password', 'force push',
    '跨盘删除', '删除系统', '删除目录', '清空目录', '格式化', '注册表', '环境变量',
    '凭据', '密钥', '私钥', '密码', '强制推送', '重置仓库', '卸载软件',
]

MODERATE_RISK_KEYWORDS = [
    'write file', 'overwrite', 'install', 'deploy', 'shell', 'command', 'script',
    '写入', '覆盖', '安装', '部署', '脚本', '命令', '修改文件', '删除文件',
]

LOW_VALUE_TEXTS = {
    'ok', 'hi', 'hello', 'test', 'ping', '.', '。', '嗯', '好', '好的', '收到', '测试',
}

COMMAND_MARKERS = [
    '请', '帮我', '给我', '把', '按照', '开始', '继续', '执行', '运行', '修复', '实现',
    '生成', '写', '整理', '转成', '转换', '抽取', '提取', '产出', '输出',
    'create', 'build', 'fix', 'run', 'execute', 'continue', 'implement',
]

ROUTE_KEYWORDS: dict[RouteName, list[str]] = {
    'TASK': [
        '执行', '运行', '修改', '生成', '部署', '修复', '打包', '写代码', '任务', '行动', '流程',
        '转成', '转换', '抽取', '提取', '产出', '输出', 'codex', 'agent', 'task', 'action',
        'plan', 'execute', 'build', 'fix', 'generate', 'workflow', 'implement',
    ],
    'IR': [
        '调研', '研究', 'github', '项目', '论文', '开源', '对比', '框架', '方案', '竞品', '资料源',
        'research', 'paper', 'architecture', 'framework', 'blueprint', 'compare', 'open source', 'benchmark',
    ],
    'KB': [
        '学习', '资料', '笔记', '总结', '卡片', '复习', '知识', '文档', '概念', '记忆', '理解',
        'learn', 'study', 'note', 'knowledge', 'document', 'summary', 'card', 'review', 'memory',
    ],
}

SOURCE_HINTS: dict[RouteName, list[str]] = {
    'TASK': ['task', 'todo', 'action', 'codex', 'agent', 'execution'],
    'IR': ['research', 'paper', 'github', 'repo', 'benchmark', 'inspiration'],
    'KB': ['obsidian', 'vault', 'note', 'kb', 'knowledge', '学习', '笔记'],
}

ROUTE_BASE_SCORE: dict[RouteName, float] = {'TASK': 0.22, 'IR': 0.20, 'KB': 0.18}
ROUTE_PRIORITY: tuple[RouteName, ...] = ('TASK', 'IR', 'KB')


def _normalize(text: str) -> str:
    return ' '.join(text.strip().lower().split())


def _matched_keywords(haystack: str, keywords: list[str]) -> list[str]:
    normalized = _normalize(haystack)
    return [keyword for keyword in keywords if keyword.lower() in normalized]


def _compact_terms(terms: list[str], limit: int = 6) -> str:
    shown = terms[:limit]
    suffix = '' if len(terms) <= limit else f' +{len(terms) - limit}'
    return ', '.join(shown) + suffix


def _metadata_text(doc: CoreObject) -> str:
    parts: list[str] = [doc.source, doc.object_type]
    for key, value in doc.metadata.items():
        parts.append(str(key))
        if isinstance(value, (str, int, float, bool)):
            parts.append(str(value))
        elif isinstance(value, dict):
            parts.extend(str(item) for item in list(value.keys())[:6])
        elif isinstance(value, (list, tuple, set)):
            parts.extend(str(item) for item in list(value)[:6])
    return ' '.join(parts)


def _length_signal(text: str) -> float:
    if not text.strip():
        return 0.0
    return min(len(text.strip()) / 1200, 1.0)


def _quality_signal(doc: CoreObject) -> ContentQuality:
    score = doc.metadata.get('quality_score')
    issues = doc.metadata.get('quality_issues')
    looks_blocked = doc.metadata.get('looks_blocked')
    if isinstance(score, (int, float)) and isinstance(issues, list):
        return ContentQuality(
            score=max(0.0, min(float(score), 1.0)),
            issues=[str(issue) for issue in issues],
            looks_blocked=bool(looks_blocked),
        )

    source_type = str(doc.metadata.get('input_type', doc.object_type or 'text'))
    return assess_content_quality(doc.content or '', source_type=source_type)


def _route_signals(doc: CoreObject) -> tuple[
    dict[RouteName, list[str]], dict[RouteName, list[str]], list[str], dict[RouteName, float]
]:
    text = doc.content or ''
    source_text = _metadata_text(doc)
    keyword_matches = {route: _matched_keywords(text, ROUTE_KEYWORDS[route]) for route in ROUTE_PRIORITY}
    source_matches = {route: _matched_keywords(source_text, SOURCE_HINTS[route]) for route in ROUTE_PRIORITY}
    command_matches = _matched_keywords(text, COMMAND_MARKERS)

    strengths: dict[RouteName, float] = {}
    for route in ROUTE_PRIORITY:
        strengths[route] = len(keyword_matches[route]) + len(source_matches[route]) * 0.30

    if command_matches:
        strengths['TASK'] += min(len(command_matches) * 0.35, 1.50)
        if keyword_matches['TASK']:
            strengths['TASK'] += 0.50

    return keyword_matches, source_matches, command_matches, strengths


def _select_route(strengths: dict[RouteName, float]) -> RouteName:
    best = max(ROUTE_PRIORITY, key=lambda route: (strengths[route], -ROUTE_PRIORITY.index(route)))
    if strengths[best] <= 0:
        return 'KB'
    return best


def _risk_level(route_name: RouteName, text: str) -> Literal['low', 'medium', 'high']:
    if route_name == 'TASK' and _matched_keywords(text, MODERATE_RISK_KEYWORDS):
        return 'medium'
    return 'low'


def route(doc: CoreObject) -> AttentionDecision:
    text = doc.content or ''
    normalized = _normalize(text)
    length_signal = _length_signal(text)

    if not normalized:
        return AttentionDecision(route='DROP', score=0.0, reasons=['empty content'])

    if normalized in LOW_VALUE_TEXTS:
        return AttentionDecision(route='DROP', score=0.0, reasons=['low-value short input'])

    risk_matches = _matched_keywords(text, RISK_KEYWORDS)
    if risk_matches:
        return AttentionDecision(
            route='REVIEW',
            score=0.95,
            reasons=[
                f'high risk keywords: {_compact_terms(risk_matches)}',
                f'length_signal={length_signal:.2f}',
            ],
            risk_level='high',
        )

    quality = _quality_signal(doc)
    if quality.looks_blocked:
        return AttentionDecision(
            route='REVIEW',
            score=max(0.70, round(quality.score, 3)),
            reasons=[
                quality.compact_report(),
                f'length_signal={length_signal:.2f}',
            ],
            risk_level='medium',
        )

    if quality.score <= 0.20:
        return AttentionDecision(
            route='DROP',
            score=round(quality.score, 3),
            reasons=[quality.compact_report()],
        )

    keyword_matches, source_matches, command_matches, strengths = _route_signals(doc)
    route_name = _select_route(strengths)
    selected_strength = strengths[route_name]

    score = ROUTE_BASE_SCORE[route_name] + length_signal * 0.25
    if selected_strength > 0:
        score += min(selected_strength * 0.12, 0.45)
    else:
        score += 0.10
    score = min(round(score, 3), 1.0)

    reasons = [f'length_signal={length_signal:.2f}']
    if quality.issues:
        reasons.append(quality.compact_report())
    if keyword_matches[route_name]:
        reasons.append(f'{route_name.lower()} keywords: {_compact_terms(keyword_matches[route_name])}')
    if source_matches[route_name]:
        reasons.append(f'source hints: {_compact_terms(source_matches[route_name])}')
    if route_name == 'TASK' and command_matches:
        reasons.append(f'command intent: {_compact_terms(command_matches)}')
    if selected_strength <= 0:
        reasons.append('default non-empty material')
    reasons.append(f'selected route={route_name}')

    return AttentionDecision(
        route=route_name,
        score=score,
        reasons=reasons,
        risk_level=_risk_level(route_name, text),
    )
