from pathlib import Path
import json
from app.schemas import CoreObject, MachineLesson

PROJECT_ROOT = Path(__file__).resolve().parents[2]
MEMORY_PATH = PROJECT_ROOT / "data" / "memory" / "memory.jsonl"
LESSON_PATH = PROJECT_ROOT / "data" / "memory" / "lessons.jsonl"
MEMORY_PATH.parent.mkdir(parents=True, exist_ok=True)


def save_memory(obj: CoreObject) -> None:
    with MEMORY_PATH.open("a", encoding="utf-8") as f:
        f.write(obj.model_dump_json(ensure_ascii=False) + "\n")


def list_memory() -> list[CoreObject]:
    if not MEMORY_PATH.exists():
        return []
    items: list[CoreObject] = []
    for line in MEMORY_PATH.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        try:
            items.append(CoreObject(**json.loads(line)))
        except Exception:
            continue
    return items


def search_memory(query: str, top_k: int = 5) -> list[CoreObject]:
    # Simple v1 lexical search; replace with vector DB later.
    query_terms = set(query.lower().split())
    scored = []
    for item in list_memory():
        terms = set(item.content.lower().split())
        score = len(query_terms & terms)
        if score > 0:
            scored.append((score, item))
    scored.sort(key=lambda x: x[0], reverse=True)
    return [item for _, item in scored[:top_k]]


def save_lesson(lesson: MachineLesson) -> None:
    with LESSON_PATH.open("a", encoding="utf-8") as f:
        f.write(lesson.model_dump_json(ensure_ascii=False) + "\n")


def list_lessons() -> list[MachineLesson]:
    if not LESSON_PATH.exists():
        return []
    lessons: list[MachineLesson] = []
    for line in LESSON_PATH.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        try:
            lessons.append(MachineLesson(**json.loads(line)))
        except Exception:
            continue
    return lessons
