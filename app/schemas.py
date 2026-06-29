from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Literal
from pydantic import BaseModel, Field
import uuid


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def new_id(prefix: str) -> str:
    return f"{prefix}_{uuid.uuid4().hex[:12]}"


class CoreObject(BaseModel):
    id: str = Field(default_factory=lambda: new_id("obj"))
    object_type: str = "document"
    content: str
    source: str = "unknown"
    metadata: dict[str, Any] = Field(default_factory=dict)
    created_at: str = Field(default_factory=now_iso)
    attention_score: float = 0.0
    route: str | None = None


class AttentionDecision(BaseModel):
    route: Literal["KB", "IR", "TASK", "DROP", "REVIEW"]
    score: float
    reasons: list[str] = Field(default_factory=list)
    risk_level: Literal["low", "medium", "high"] = "low"


class ContextPack(BaseModel):
    query: str
    items: list[CoreObject] = Field(default_factory=list)
    summary: str = ""
    token_budget: int = 4000
    score: float = 0.0
    score_reasons: list[str] = Field(default_factory=list)


class TaskPack(BaseModel):
    id: str = Field(default_factory=lambda: new_id("task"))
    goal: str
    steps: list[dict[str, Any]] = Field(default_factory=list)
    constraints: list[str] = Field(default_factory=list)
    tools: list[str] = Field(default_factory=list)
    risk_level: Literal["low", "medium", "high"] = "low"
    success_criteria: list[str] = Field(default_factory=list)


class ExecutionTrace(BaseModel):
    id: str = Field(default_factory=lambda: new_id("trace"))
    task_id: str | None = None
    events: list[dict[str, Any]] = Field(default_factory=list)
    result: dict[str, Any] = Field(default_factory=dict)
    success: bool | None = None
    created_at: str = Field(default_factory=now_iso)


class EvalResult(BaseModel):
    success: bool
    score: float
    failure_reason: str = ""
    improvement: str = ""
    issues: list[str] = Field(default_factory=list)
    recommendations: list[str] = Field(default_factory=list)
    audit: dict[str, Any] = Field(default_factory=dict)


class MachineLesson(BaseModel):
    id: str = Field(default_factory=lambda: new_id("lesson"))
    pattern: str
    lesson_type: Literal["success", "failure", "anti_pattern", "constraint"]
    future_constraint: str
    evidence_trace_id: str | None = None
    created_at: str = Field(default_factory=now_iso)


class LearningCard(BaseModel):
    id: str = Field(default_factory=lambda: new_id("card"))
    front: str
    back: str
    source: str = "manual"
    source_object_id: str | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)
    stability: float = 1.0
    difficulty: float = 5.0
    interval_seconds: int = 0
    next_review_at: str = Field(default_factory=now_iso)
    last_review_at: str | None = None
    review_count: int = 0
    lapses: int = 0
    created_at: str = Field(default_factory=now_iso)


class ReviewEvent(BaseModel):
    id: str = Field(default_factory=lambda: new_id("review"))
    card_id: str
    score: float
    grade: int
    retrievability: float
    previous_interval_seconds: int = 0
    next_interval_seconds: int = 0
    created_at: str = Field(default_factory=now_iso)


class TeachBackSession(BaseModel):
    id: str = Field(default_factory=lambda: new_id("teach"))
    card_id: str
    method: str = "feynman"
    explanation: str
    total_score: float = 0.0
    dimension_scores: dict[str, float] = Field(default_factory=dict)
    gaps: list[str] = Field(default_factory=list)
    created_at: str = Field(default_factory=now_iso)
