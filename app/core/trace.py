from pathlib import Path
import json
from app.schemas import ExecutionTrace

PROJECT_ROOT = Path(__file__).resolve().parents[2]
TRACE_PATH = PROJECT_ROOT / "data" / "logs" / "trace.jsonl"
TRACE_PATH.parent.mkdir(parents=True, exist_ok=True)


def log_trace(trace: ExecutionTrace) -> None:
    with TRACE_PATH.open("a", encoding="utf-8") as f:
        f.write(trace.model_dump_json(ensure_ascii=False) + "\n")


def list_traces() -> list[dict]:
    if not TRACE_PATH.exists():
        return []
    rows = []
    for line in TRACE_PATH.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        try:
            rows.append(json.loads(line))
        except Exception:
            rows.append({"raw": line})
    return rows
