from __future__ import annotations

import json
from pathlib import Path
from zipfile import ZipFile, ZIP_DEFLATED

from pk_radar.core.store import KnowledgeStore


def export_json(store: KnowledgeStore, out_path: Path) -> Path:
    out_path.parent.mkdir(parents=True, exist_ok=True)
    docs = store.export_documents()
    out_path.write_text(json.dumps(docs, ensure_ascii=False, indent=2), encoding="utf-8")
    return out_path


def _safe_name(value: str, fallback: str) -> str:
    safe = "".join(ch if ch.isalnum() or ch in "._-" else "_" for ch in value).strip("_")
    return (safe[:80] or fallback)


def export_markdown(store: KnowledgeStore, out_dir: Path) -> Path:
    out_dir.mkdir(parents=True, exist_ok=True)
    for row in store.export_documents():
        title = row.get("title") or f"document_{row['id']}"
        name = f"{row['id']:04d}_{_safe_name(title, 'doc_' + str(row['id']))}.md"
        body = [
            "---",
            f"id: {row['id']}",
            f"source_type: {row.get('source_type') or ''}",
            f"source_url: {row.get('source_url') or ''}",
            f"tags: {row.get('tags') or ''}",
            f"created_at: {row.get('created_at') or ''}",
            f"updated_at: {row.get('updated_at') or ''}",
            "---",
            "",
            f"# {title}",
            "",
            "## Summary",
            row.get("summary") or "",
            "",
            "## Content",
            row.get("content") or "",
        ]
        (out_dir / name).write_text("\n".join(body), encoding="utf-8")
    return out_dir


def backup_database(db_path: Path, out_path: Path) -> Path:
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with ZipFile(out_path, "w", compression=ZIP_DEFLATED) as zf:
        if db_path.exists():
            zf.write(db_path, arcname=db_path.name)
        wal = db_path.with_name(db_path.name + "-wal")
        shm = db_path.with_name(db_path.name + "-shm")
        if wal.exists():
            zf.write(wal, arcname=wal.name)
        if shm.exists():
            zf.write(shm, arcname=shm.name)
    return out_path
