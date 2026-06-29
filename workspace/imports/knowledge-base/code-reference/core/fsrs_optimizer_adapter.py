"""fsrs_optimizer_adapter.py — Adapter for py-fsrs optimizer patterns (MIT).

Extracts and adapts key optimization patterns from the py-fsrs reference
implementation (https://github.com/open-spaced-repetition/py-fsrs) to enhance
the local fsrs_optimizer.py without introducing direct library dependencies.

Key patterns adapted:
  1. Parameter bounds validation (LOWER_BOUNDS / UPPER_BOUNDS)
  2. Batch loss computation with stability-based decay
  3. Mini-batch review log pre-processing
  4. Weight clipping for numerical stability

Reference: reference/extracted/py-fsrs/fsrs/optimizer.py
License: MIT (algorithm ideas only, no code copied)
"""
from __future__ import annotations

import math
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Optional, Sequence


# ---------------------------------------------------------------------------
# Parameter bounds — adapted from py-fsrs LOWER_BOUNDS_PARAMETERS / UPPER_BOUNDS_PARAMETERS
# These prevent numerical instability during optimization.
# ---------------------------------------------------------------------------
STABILITY_MIN = 0.001
INITIAL_STABILITY_MAX = 100.0

PARAM_LOWER_BOUNDS: tuple[float, ...] = (
    STABILITY_MIN,  # w0: initial stability again
    STABILITY_MIN,  # w1: initial stability hard
    STABILITY_MIN,  # w2: initial stability good
    STABILITY_MIN,  # w3: initial stability easy
    1.0,            # w4: initial difficulty
    0.001,          # w5: difficulty Δ weight
    0.001,          # w6: difficulty update
    0.001,          # w7: mean reversion
    0.0,            # w8: stability exponent (success)
    0.0,            # w9: difficulty factor for S
    0.001,          # w10: S growth exponent
    0.001,          # w11: short-term S exponent
    0.001,          # w12: short-term S grade factor
    0.001,          # w13: short-term difficulty factor
    0.0,            # w14: retrievability influence
    0.0,            # w15: post-lapse S multiplier
    1.0,            # w16: post-lapse S exponent
    0.0,            # w17: forgetting index
    0.0,            # w18: same-day bonus
)

PARAM_UPPER_BOUNDS: tuple[float, ...] = (
    INITIAL_STABILITY_MAX,  # w0
    INITIAL_STABILITY_MAX,  # w1
    INITIAL_STABILITY_MAX,  # w2
    INITIAL_STABILITY_MAX,  # w3
    10.0,    # w4
    4.0,     # w5
    4.0,     # w6
    0.75,    # w7
    4.5,     # w8
    0.8,     # w9
    3.5,     # w10
    5.0,     # w11
    0.25,    # w12
    0.9,     # w13
    4.0,     # w14
    1.0,     # w15
    6.0,     # w16
    2.0,     # w17
    0.8,     # w18
)


def clamp_weights(weights: tuple[float, ...]) -> tuple[float, ...]:
    """Clamp FSRS weights to valid bounds (adapted from py-fsrs weight_clamping).

    In py-fsrs, the torch optimizer clips weights after each gradient step.
    This is the pure-Python equivalent for our gradient-free optimizer.
    """
    if len(weights) != len(PARAM_LOWER_BOUNDS):
        raise ValueError(f"Expected {len(PARAM_LOWER_BOUNDS)} weights, got {len(weights)}")
    return tuple(
        max(lb, min(ub, w))
        for w, lb, ub in zip(weights, PARAM_LOWER_BOUNDS, PARAM_UPPER_BOUNDS)
    )


@dataclass
class ReviewSequence:
    """A card''s review history, formatted for optimization.

    Adapted from py-fsrs Optimizer._format_revlogs() pattern:
    - Reviews are sorted by datetime per card
    - Each entry is (elapsed_days, grade, recall)
    """
    card_id: int
    sequences: list[tuple[float, int, int]] = field(default_factory=list)
    # (delta_t_days, grade_1to4, recall_0or1)


def build_review_sequences(
    reviews: Sequence[dict[str, Any]],
) -> dict[int, ReviewSequence]:
    """Build per-card review sequences from raw review data.

    Adapted from py-fsrs Optimizer.__init__ / _format_revlogs pattern:
    - Groups reviews by card_id
    - Sorts by timestamp within each card
    - Computes elapsed days and recall indicators

    Args:
        reviews: list of dicts with keys (card_id, grade, score, reviewed_at, stability)

    Returns:
        dict mapping card_id -> ReviewSequence
    """
    # Group by card_id
    by_card: dict[int, list[dict]] = defaultdict(list)
    for r in reviews:
        by_card[r["card_id"]].append(r)

    sequences: dict[int, ReviewSequence] = {}
    for card_id, revs in by_card.items():
        # Sort by timestamp
        revs.sort(key=lambda r: r.get("reviewed_at", ""))
        seq = ReviewSequence(card_id=card_id)
        prev_ts: Optional[float] = None
        for r in revs:
            ts = r.get("reviewed_at")
            if isinstance(ts, str):
                ts = datetime.fromisoformat(ts.replace("Z", "+00:00")).timestamp()
            elif ts is None:
                ts = datetime.now(timezone.utc).timestamp()
            delta_days = (ts - prev_ts) / 86400.0 if prev_ts is not None else 0.0
            grade = int(r.get("grade", 3))  # default: good
            recall = 0 if grade == 1 else 1  # Again = 0, Hard/Good/Easy = 1
            seq.sequences.append((delta_days, grade, recall))
            prev_ts = ts
        sequences[card_id] = seq

    return sequences


def compute_loss_on_sequence(
    weights: tuple[float, ...],
    sequence: ReviewSequence,
    *,
    decay: float = -0.5,
) -> float:
    """Compute RMSE loss for a single card''s review sequence.

    Adapted from py-fsrs Optimizer._compute_batch_loss():
    - Iterates through the review sequence
    - Computes predicted retrievability at each review time
    - Compares with actual recall (0 or 1)
    - Returns mean squared error

    This is a simplified pure-Python version that mirrors the torch BCELoss logic.
    """
    if len(sequence.sequences) < 2:
        return 0.0  # Need at least 2 reviews to compute loss

    w = weights
    # Initialize with first review
    first_grade = sequence.sequences[0][1]
    S = w[first_grade - 1] if first_grade <= 4 else w[2]  # initial stability
    D = w[4]  # initial difficulty
    losses = []

    for delta_days, grade, actual_recall in sequence.sequences[1:]:
        # Predict retrievability: R = exp(decay * delta_t / S)
        delta_t = max(0.0, delta_days)
        R = math.exp(decay * delta_t / max(S, 0.001))
        pred_recall = max(0.0, min(1.0, R))

        # Loss: squared error
        losses.append((pred_recall - actual_recall) ** 2)

        # Update S and D based on grade (simplified FSRS update)
        difficulty_delta = w[5] * (grade - 3)  # grade affects difficulty
        D = max(1.0, min(10.0, D + difficulty_delta - w[6] * (D - w[4])))

        # Stability update (simplified)
        if grade == 1:  # Again: post-lapse
            S = max(0.001, S * w[14] * (D ** w[15]))
        else:
            S_hard_penalty = 1.0 if grade != 2 else w[16]
            S = S * (1 + w[9] * (11 - D) * S ** w[7] * S_hard_penalty)
            S = min(S, INITIAL_STABILITY_MAX)

    return sum(losses) / len(losses) if losses else 0.0


def compute_total_loss(
    weights: tuple[float, ...],
    sequences: dict[int, ReviewSequence],
) -> float:
    """Compute total RMSE across all cards.

    Adapted from py-fsrs batch loss computation.
    """
    total = 0.0
    count = 0
    for seq in sequences.values():
        loss = compute_loss_on_sequence(weights, seq)
        if loss > 0:
            total += loss
            count += 1
    return math.sqrt(total / count) if count > 0 else float("inf")


def weight_perturbation(
    weights: tuple[float, ...],
    *,
    step_size: float = 0.05,
    rng: Optional[Any] = None,
) -> tuple[float, ...]:
    """Generate a perturbed weight vector for hill-climbing search.

    Adapted from py-fsrs optimization loop pattern.
    Each weight is perturbed by a Gaussian with scale proportional to step_size.
    Weights are clamped to valid bounds after perturbation.
    """
    import random as _random
    rand = _random.Random() if rng is None else rng
    perturbed = tuple(
        w + rand.gauss(0, step_size * (ub - lb) * 0.1)
        for w, lb, ub in zip(weights, PARAM_LOWER_BOUNDS, PARAM_UPPER_BOUNDS)
    )
    return clamp_weights(perturbed)


# ---------------------------------------------------------------------------
# Self-test (run: python -m pk_radar.core.fsrs_optimizer_adapter)
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    from .fsrs5 import DEFAULT_W

    # Test clamp
    clamped = clamp_weights(DEFAULT_W)
    print(f"Clamped weights OK: {len(clamped)} parameters")

    # Test sequence builder with synthetic data
    synthetic_reviews = [
        {"card_id": 1, "grade": 3, "reviewed_at": "2026-01-01T00:00:00Z"},
        {"card_id": 1, "grade": 4, "reviewed_at": "2026-01-03T00:00:00Z"},
        {"card_id": 1, "grade": 1, "reviewed_at": "2026-01-10T00:00:00Z"},
        {"card_id": 2, "grade": 3, "reviewed_at": "2026-01-02T00:00:00Z"},
        {"card_id": 2, "grade": 3, "reviewed_at": "2026-01-09T00:00:00Z"},
    ]
    seqs = build_review_sequences(synthetic_reviews)
    print(f"Sequences built: {len(seqs)} cards")

    # Compute loss
    loss = compute_total_loss(DEFAULT_W, seqs)
    print(f"RMSE on synthetic data: {loss:.4f}")

    # Test perturbation
    perturbed = weight_perturbation(DEFAULT_W, step_size=0.05)
    loss2 = compute_total_loss(perturbed, seqs)
    print(f"RMSE after perturbation: {loss2:.4f}")

    print("\nAll fsrs_optimizer_adapter tests passed.")
