"""fsrs_optimizer.py — Gradient-free FSRS-5 weight optimizer.

Reads real review data from data/knowledge.db, simulates the FSRS-5 scheduler
on each card's review sequence, and uses random hill-climbing to find weights
that minimize the RMSE between predicted retrievability and actual recall (score).

Usage:
    python -m pk_radar.core.fsrs_optimizer
    # or from the backend directory:
    python pk_radar/core/fsrs_optimizer.py

Output:
    backend/optimized_fsrs_weights.json — optimized 19-weight tuple ready to
    replace DEFAULT_W in fsrs5.py.
"""
from __future__ import annotations

import json
import math
import random
import sqlite3
import sys
import time
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional

# ---------------------------------------------------------------------------
# Re-import the FSRS-5 logic from our sibling module so the optimizer stays
# in-sync with the production implementation.
# ---------------------------------------------------------------------------
from .fsrs5 import (
    DAY,
    DEFAULT_W,
    FACTOR,
    FSRS5,
    score_to_grade,
)

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------
DB_PATH = Path(__file__).resolve().parent.parent.parent.parent / "data" / "knowledge.db"
OUTPUT_PATH = Path(__file__).resolve().parent.parent.parent / "optimized_fsrs_weights.json"

# Search hyper-parameters
MAX_ITERATIONS = 2000
INITIAL_STEP_SIZE = 0.15
STEP_DECAY = 0.997
PATIENCE = 200  # stop if no improvement for this many iterations
SEED = 42

# ---------------------------------------------------------------------------
# Data loading
# ---------------------------------------------------------------------------


def load_review_sequences(db_path: Path) -> list[dict[str, Any]]:
    """Return one entry per card with its chronologically-sorted review list.

    Each entry:
        {
            "card_id": int,
            "created_at": str,          # ISO-8601
            "memory_strength": float,    # initial
            "reviews": [
                {
                    "score": float,       # 0.0-1.0
                    "strength_before": float,
                    "strength_after": float,
                    "created_at": str,    # ISO-8601
                },
                ...
            ]
        }
    """
    if not db_path.exists():
        raise FileNotFoundError(f"Database not found: {db_path}")

    conn = sqlite3.connect(str(db_path))
    conn.row_factory = sqlite3.Row

    # Fetch all cards with at least one review
    card_rows = conn.execute(
        """
        SELECT c.id, c.created_at, c.memory_strength
        FROM cards c
        WHERE c.id IN (SELECT DISTINCT card_id FROM reviews)
        ORDER BY c.id
        """
    ).fetchall()

    sequences: list[dict[str, Any]] = []
    for card_row in card_rows:
        review_rows = conn.execute(
            """
            SELECT score, strength_before, strength_after, created_at
            FROM reviews
            WHERE card_id = ?
            ORDER BY created_at ASC, id ASC
            """,
            (card_row["id"],),
        ).fetchall()

        if not review_rows:
            continue

        sequences.append({
            "card_id": card_row["id"],
            "created_at": card_row["created_at"],
            "initial_memory_strength": card_row["memory_strength"],
            "reviews": [
                {
                    "score": r["score"],
                    "strength_before": r["strength_before"],
                    "strength_after": r["strength_after"],
                    "created_at": r["created_at"],
                }
                for r in review_rows
            ],
        })

    conn.close()
    return sequences


# ---------------------------------------------------------------------------
# Simulation
# ---------------------------------------------------------------------------


def _parse_iso(ts: str) -> float:
    """Parse ISO-8601 timestamp string to Unix seconds (UTC)."""
    # Handle both 'Z' suffix and '+00:00' offset
    ts = ts.replace("Z", "+00:00")
    dt = datetime.fromisoformat(ts)
    return dt.timestamp()


def simulate_card(w: tuple[float, ...], card_seq: dict[str, Any]) -> list[float]:
    """Run the FSRS-5 scheduler on one card's review sequence.

    Returns a list of predicted retrievabilities, one per review, in order.
    """
    scheduler = FSRS5(w=w)

    # Build an initial card dict as fsrs5.review() expects
    card: dict[str, Any] = {
        "memory_strength": card_seq["initial_memory_strength"],
        "review_count": 0,
        "interval_seconds": DAY,   # default interval before first review
        "difficulty": 5.0,
        "last_review_at": _parse_iso(card_seq["created_at"]),
    }

    predicted_rs: list[float] = []
    for rev in card_seq["reviews"]:
        score = rev["score"]
        now = _parse_iso(rev["created_at"])

        result = scheduler.review(card, score, now=now)
        predicted_rs.append(result["retrievability"])

        # Update card state for the next review in the sequence
        card["memory_strength"] = result["memory_strength"]
        card["review_count"] = result["review_count"]
        card["interval_seconds"] = result["interval_seconds"]
        card["difficulty"] = result["difficulty"]
        card["last_review_at"] = now

    return predicted_rs


def compute_rmse(
    w: tuple[float, ...],
    sequences: list[dict[str, Any]],
) -> float:
    """Compute RMSE between predicted retrievability and actual score."""
    total_sq_error = 0.0
    total_n = 0

    for seq in sequences:
        try:
            predicted = simulate_card(w, seq)
        except Exception:
            # Numeric instability with extreme weights — return huge error
            return 1e9

        for pred_r, rev in zip(predicted, seq["reviews"]):
            actual = rev["score"]
            # Clamp predictions to [0,1] for stable comparison
            pred_r = max(0.0, min(1.0, pred_r))
            total_sq_error += (pred_r - actual) ** 2
            total_n += 1

    if total_n == 0:
        return 1e9
    return math.sqrt(total_sq_error / total_n)


# ---------------------------------------------------------------------------
# Random Hill-Climbing
# ---------------------------------------------------------------------------


def _perturb(w: tuple[float, ...], step: float) -> tuple[float, ...]:
    """Return a perturbed copy of w with Gaussian noise scaled by step."""
    new = list(w)
    for i in range(len(new)):
        delta = random.gauss(0, step)
        new[i] += delta
        # Keep weights in a reasonable range
        new[i] = max(0.001, min(20.0, new[i]))
    return tuple(new)


def random_hill_climb(
    sequences: list[dict[str, Any]],
    initial_w: tuple[float, ...],
    max_iter: int = MAX_ITERATIONS,
    initial_step: float = INITIAL_STEP_SIZE,
    step_decay: float = STEP_DECAY,
    patience: int = PATIENCE,
) -> tuple[tuple[float, ...], float, list[dict[str, Any]]]:
    """Random hill-climbing over the 19 FSRS weights.

    Returns (best_weights, best_rmse, history).
    """
    random.seed(SEED)

    current_w = tuple(initial_w)
    current_rmse = compute_rmse(current_w, sequences)
    best_w = current_w
    best_rmse = current_rmse
    step = initial_step

    history: list[dict[str, Any]] = []
    no_improve = 0
    accepted = 0

    for iteration in range(1, max_iter + 1):
        candidate = _perturb(current_w, step)
        candidate_rmse = compute_rmse(candidate, sequences)

        if candidate_rmse < current_rmse:
            # Improvement — always accept
            current_w = candidate
            current_rmse = candidate_rmse
            accepted += 1
            no_improve = 0

            if candidate_rmse < best_rmse:
                best_w = candidate
                best_rmse = candidate_rmse
        else:
            # Worse — probabilistic acceptance (Metropolis-like)
            delta = candidate_rmse - current_rmse
            temperature = step * 0.5
            if temperature > 0 and random.random() < math.exp(-delta / temperature):
                current_w = candidate
                current_rmse = candidate_rmse
                accepted += 1
            no_improve += 1

        step *= step_decay

        if iteration % 100 == 0 or iteration == 1 or iteration == max_iter:
            history.append({
                "iteration": iteration,
                "rmse": round(current_rmse, 6),
                "best_rmse": round(best_rmse, 6),
                "step": round(step, 6),
                "accepted": accepted,
            })

        if no_improve >= patience:
            history.append({
                "iteration": iteration,
                "rmse": round(current_rmse, 6),
                "best_rmse": round(best_rmse, 6),
                "step": round(step, 6),
                "accepted": accepted,
                "stopped_early": True,
            })
            break

    return best_w, best_rmse, history


# ---------------------------------------------------------------------------
# Main entry point
# ---------------------------------------------------------------------------


def optimize(db_path: Optional[Path] = None, output_path: Optional[Path] = None) -> dict[str, Any]:
    """Run the full optimization pipeline.

    Returns a dict suitable for JSON serialization.
    """
    _db = db_path or DB_PATH
    _out = output_path or OUTPUT_PATH

    print(f"Loading review sequences from {_db} ...")
    sequences = load_review_sequences(_db)
    print(f"  Found {len(sequences)} cards with {sum(len(s['reviews']) for s in sequences)} total reviews")

    if not sequences:
        print("No review data found. Exiting.")
        return {"error": "No review data"}

    # Baseline RMSE with default weights
    baseline_rmse = compute_rmse(DEFAULT_W, sequences)
    print(f"\nBaseline RMSE (default weights): {baseline_rmse:.6f}")

    # Optimize
    print(f"\nRunning random hill-climb ({MAX_ITERATIONS} max iterations, step={INITIAL_STEP_SIZE}) ...")
    t0 = time.time()
    best_w, best_rmse, history = random_hill_climb(sequences, DEFAULT_W)
    elapsed = time.time() - t0

    improvement = baseline_rmse - best_rmse
    pct = (improvement / baseline_rmse * 100) if baseline_rmse > 0 else 0.0

    print(f"\n{'='*60}")
    print(f"Optimization complete in {elapsed:.1f}s ({len(history)} checkpoints)")
    print(f"Baseline RMSE:  {baseline_rmse:.6f}")
    print(f"Optimized RMSE: {best_rmse:.6f}")
    print(f"Improvement:    {improvement:.6f} ({pct:+.1f}%)")
    print(f"{'='*60}")

    # Build output
    result: dict[str, Any] = {
        "version": "fsrs-5-optimized",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "num_cards": len(sequences),
        "num_reviews": sum(len(s["reviews"]) for s in sequences),
        "baseline_rmse": round(baseline_rmse, 6),
        "optimized_rmse": round(best_rmse, 6),
        "improvement_pct": round(pct, 2),
        "weights": [round(v, 6) for v in best_w],
        "weights_tuple": f"({', '.join(f'{v:.4f}' for v in best_w)})",
        "optimization_history": history,
        "hyperparameters": {
            "max_iterations": MAX_ITERATIONS,
            "initial_step_size": INITIAL_STEP_SIZE,
            "step_decay": STEP_DECAY,
            "patience": PATIENCE,
            "seed": SEED,
        },
    }

    # Persist
    _out.parent.mkdir(parents=True, exist_ok=True)
    _out.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"\nOptimized weights saved to {_out}")

    return result


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    # Allow running as script from any directory
    optimize()