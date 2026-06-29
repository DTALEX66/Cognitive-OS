from __future__ import annotations

import json
import sqlite3
from dataclasses import dataclass
from pathlib import Path
from datetime import datetime, timezone
from typing import Any


SCHEMA = """
PRAGMA journal_mode=WAL;

CREATE TABLE IF NOT EXISTS documents (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    source_type TEXT NOT NULL,
    source_url TEXT,
    title TEXT NOT NULL DEFAULT '',
    content TEXT NOT NULL DEFAULT '',
    summary TEXT NOT NULL DEFAULT '',
    tags TEXT NOT NULL DEFAULT '',
    content_hash TEXT NOT NULL DEFAULT '',
    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT DEFAULT NULL
);

CREATE UNIQUE INDEX IF NOT EXISTS idx_documents_source_url ON documents(source_url) WHERE source_url IS NOT NULL;
CREATE INDEX IF NOT EXISTS idx_documents_updated_at ON documents(updated_at);
CREATE INDEX IF NOT EXISTS idx_documents_hash ON documents(content_hash);

CREATE VIRTUAL TABLE IF NOT EXISTS documents_fts USING fts5(
    title,
    content,
    summary,
    tags,
    content='documents',
    content_rowid='id'
);

CREATE TRIGGER IF NOT EXISTS documents_ai AFTER INSERT ON documents BEGIN
  INSERT INTO documents_fts(rowid, title, content, summary, tags)
  VALUES (new.id, new.title, new.content, new.summary, new.tags);
END;

CREATE TRIGGER IF NOT EXISTS documents_ad AFTER DELETE ON documents BEGIN
  INSERT INTO documents_fts(documents_fts, rowid, title, content, summary, tags)
  VALUES('delete', old.id, old.title, old.content, old.summary, old.tags);
END;

CREATE TRIGGER IF NOT EXISTS documents_au AFTER UPDATE ON documents BEGIN
  INSERT INTO documents_fts(documents_fts, rowid, title, content, summary, tags)
  VALUES('delete', old.id, old.title, old.content, old.summary, old.tags);
  INSERT INTO documents_fts(rowid, title, content, summary, tags)
  VALUES (new.id, new.title, new.content, new.summary, new.tags);
END;

CREATE TABLE IF NOT EXISTS sources (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    url TEXT NOT NULL UNIQUE,
    title TEXT NOT NULL DEFAULT '',
    tags TEXT NOT NULL DEFAULT '',
    mode TEXT NOT NULL DEFAULT 'auto',
    enabled INTEGER NOT NULL DEFAULT 1,
    last_document_id INTEGER,
    last_error TEXT NOT NULL DEFAULT '',
    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT DEFAULT NULL,
    last_checked_at TEXT
);



CREATE TABLE IF NOT EXISTS entities (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE,
    entity_type TEXT NOT NULL DEFAULT "concept",
    description TEXT NOT NULL DEFAULT "",
    metadata TEXT NOT NULL DEFAULT "{}",
    pinned INTEGER NOT NULL DEFAULT 0,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT DEFAULT NULL
);

CREATE INDEX IF NOT EXISTS idx_entities_name ON entities(name);
CREATE INDEX IF NOT EXISTS idx_entities_type ON entities(entity_type);

CREATE TABLE IF NOT EXISTS relations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    source_entity_id INTEGER NOT NULL,
    target_entity_id INTEGER NOT NULL,
    relation_type TEXT NOT NULL,
    weight REAL NOT NULL DEFAULT 1.0,
    description TEXT NOT NULL DEFAULT "",
    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (source_entity_id) REFERENCES entities(id) ON DELETE CASCADE,
    FOREIGN KEY (target_entity_id) REFERENCES entities(id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_relations_source ON relations(source_entity_id);
CREATE INDEX IF NOT EXISTS idx_relations_target ON relations(target_entity_id);
CREATE INDEX IF NOT EXISTS idx_relations_type ON relations(relation_type);
CREATE UNIQUE INDEX IF NOT EXISTS idx_relations_unique ON relations(source_entity_id, target_entity_id, relation_type);

CREATE TABLE IF NOT EXISTS observations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id TEXT NOT NULL DEFAULT "",
    entity_id INTEGER,
    observation_type TEXT NOT NULL DEFAULT "note",
    title TEXT NOT NULL,
    content TEXT NOT NULL,
    source TEXT NOT NULL DEFAULT "",
    topic_key TEXT NOT NULL DEFAULT "",
    revision_count INTEGER NOT NULL DEFAULT 1,
    duplicate_count INTEGER NOT NULL DEFAULT 0,
    content_hash TEXT NOT NULL DEFAULT "",
    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT DEFAULT NULL,
    FOREIGN KEY (entity_id) REFERENCES entities(id) ON DELETE SET NULL
);

CREATE INDEX IF NOT EXISTS idx_observations_session ON observations(session_id);
CREATE INDEX IF NOT EXISTS idx_observations_entity ON observations(entity_id);
CREATE INDEX IF NOT EXISTS idx_observations_topic ON observations(topic_key);
CREATE INDEX IF NOT EXISTS idx_observations_hash ON observations(content_hash);

CREATE VIRTUAL TABLE IF NOT EXISTS observations_fts USING fts5(
    title, content, topic_key,
    content="observations",
    content_rowid="id"
);

CREATE TRIGGER IF NOT EXISTS observations_ai AFTER INSERT ON observations BEGIN
  INSERT INTO observations_fts(rowid, title, content, topic_key)
  VALUES (new.id, new.title, new.content, new.topic_key);
END;

CREATE TRIGGER IF NOT EXISTS observations_ad AFTER DELETE ON observations BEGIN
  INSERT INTO observations_fts(observations_fts, rowid, title, content, topic_key)
  VALUES("delete", old.id, old.title, old.content, old.topic_key);
END;

CREATE TRIGGER IF NOT EXISTS observations_au AFTER UPDATE ON observations BEGIN
  INSERT INTO observations_fts(observations_fts, rowid, title, content, topic_key)
  VALUES("delete", old.id, old.title, old.content, old.topic_key);
  INSERT INTO observations_fts(rowid, title, content, topic_key)
  VALUES (new.id, new.title, new.content, new.topic_key);
END;

CREATE TABLE IF NOT EXISTS sessions (
    id TEXT PRIMARY KEY,
    project TEXT NOT NULL DEFAULT "",
    directory TEXT NOT NULL DEFAULT "",
    summary TEXT NOT NULL DEFAULT "",
    status TEXT NOT NULL DEFAULT "active",
    started_at TEXT NOT NULL,
    ended_at TEXT
);

CREATE INDEX IF NOT EXISTS idx_sessions_project ON sessions(project);
CREATE INDEX IF NOT EXISTS idx_sessions_status ON sessions(status);


CREATE TABLE IF NOT EXISTS events (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    event_type TEXT NOT NULL,
    message TEXT NOT NULL DEFAULT '',
    payload_json TEXT NOT NULL DEFAULT '{}',
    created_at TEXT DEFAULT CURRENT_TIMESTAMP
);

-- ===== A线: 人类学习系统 =====
CREATE TABLE IF NOT EXISTS cards (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    content TEXT NOT NULL DEFAULT '',
    deck TEXT NOT NULL DEFAULT 'default',
    tags TEXT NOT NULL DEFAULT '',
    source_id INTEGER NOT NULL DEFAULT 0,
    memory_strength REAL NOT NULL DEFAULT 0.0,
    review_count INTEGER NOT NULL DEFAULT 0,
    interval_seconds INTEGER NOT NULL DEFAULT 86400,
    next_review_at TEXT DEFAULT NULL,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT DEFAULT NULL,
    last_reviewed_at TEXT DEFAULT NULL,
    difficulty REAL NOT NULL DEFAULT 5.0,
    lapses INTEGER NOT NULL DEFAULT 0
);

CREATE TABLE IF NOT EXISTS reviews (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    card_id INTEGER NOT NULL,
    score REAL NOT NULL,
    strength_before REAL NOT NULL DEFAULT 0.0,
    strength_after REAL NOT NULL DEFAULT 0.0,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (card_id) REFERENCES cards(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS learning_routes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    description TEXT NOT NULL DEFAULT '',
    goal TEXT NOT NULL DEFAULT '',
    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT DEFAULT NULL
);

CREATE TABLE IF NOT EXISTS route_steps (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    route_id INTEGER NOT NULL,
    title TEXT NOT NULL,
    step_type TEXT NOT NULL DEFAULT 'read',
    resource_url TEXT NOT NULL DEFAULT '',
    order_num INTEGER NOT NULL DEFAULT 0,
    completed INTEGER NOT NULL DEFAULT 0,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (route_id) REFERENCES learning_routes(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS palace_nodes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    node_type TEXT NOT NULL DEFAULT 'concept',
    space TEXT NOT NULL DEFAULT '',
    room TEXT NOT NULL DEFAULT '',
    parent_id INTEGER DEFAULT NULL,
    visual_cue TEXT NOT NULL DEFAULT '',
    entity_id INTEGER NOT NULL DEFAULT 0,
    x REAL NOT NULL DEFAULT 0,
    y REAL NOT NULL DEFAULT 0,
    metadata_json TEXT NOT NULL DEFAULT '{}'
);

-- Palace Routes (route walk)
CREATE TABLE IF NOT EXISTS palace_routes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    description TEXT NOT NULL DEFAULT '',
    space TEXT NOT NULL DEFAULT '',
    created_at TEXT DEFAULT CURRENT_TIMESTAMP DEFAULT (datetime('now')),
    updated_at TEXT DEFAULT NULL DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS palace_route_steps (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    route_id INTEGER NOT NULL,
    node_id INTEGER NOT NULL,
    step_order INTEGER NOT NULL DEFAULT 0,
    instruction TEXT NOT NULL DEFAULT '',
    FOREIGN KEY (route_id) REFERENCES palace_routes(id),
    FOREIGN KEY (node_id) REFERENCES palace_nodes(id)
);

-- ===== B线: 机器知识系统 =====
CREATE TABLE IF NOT EXISTS machine_knowledge_units (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    content TEXT NOT NULL DEFAULT '',
    unit_type TEXT NOT NULL DEFAULT 'rule',
    source_type TEXT NOT NULL DEFAULT '',
    tags TEXT NOT NULL DEFAULT '',
    confidence REAL NOT NULL DEFAULT 0.5,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT DEFAULT NULL
);

CREATE TABLE IF NOT EXISTS machine_routes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    goal TEXT NOT NULL,
    context_requirements TEXT NOT NULL DEFAULT '',
    knowledge_requirements TEXT NOT NULL DEFAULT '',
    tool_requirements TEXT NOT NULL DEFAULT '',
    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT DEFAULT NULL
);

CREATE TABLE IF NOT EXISTS route_steps_b (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    route_id INTEGER NOT NULL,
    step_type TEXT NOT NULL,
    description TEXT NOT NULL DEFAULT '',
    expected_output TEXT NOT NULL DEFAULT '',
    order_num INTEGER NOT NULL DEFAULT 0,
    completed INTEGER NOT NULL DEFAULT 0,
    FOREIGN KEY (route_id) REFERENCES machine_routes(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS a_to_b_candidates (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    a_source_type TEXT NOT NULL,
    a_source_id INTEGER NOT NULL,
    a_title TEXT NOT NULL DEFAULT '',
    a_content TEXT NOT NULL DEFAULT '',
    a_strength REAL NOT NULL DEFAULT 0.0,
    a_review_count INTEGER NOT NULL DEFAULT 0,
    b_title TEXT NOT NULL DEFAULT '',
    b_content TEXT NOT NULL DEFAULT '',
    b_unit_type TEXT NOT NULL DEFAULT 'rule',
    status TEXT NOT NULL DEFAULT 'pending',
    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT DEFAULT NULL
);

-- ===== Agent/Role系统 =====
CREATE TABLE IF NOT EXISTS agent_roles (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE,
    role_type TEXT NOT NULL DEFAULT 'worker',
    description TEXT NOT NULL DEFAULT '',
    capabilities TEXT NOT NULL DEFAULT '[]',
    priority INTEGER NOT NULL DEFAULT 0,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS agent_task_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    agent_role TEXT NOT NULL,
    task_type TEXT NOT NULL DEFAULT 'execute',
    goal TEXT NOT NULL DEFAULT '',
    input_summary TEXT NOT NULL DEFAULT '',
    output_summary TEXT NOT NULL DEFAULT '',
    status TEXT NOT NULL DEFAULT 'pending',
    duration_ms INTEGER NOT NULL DEFAULT 0,
    error_message TEXT NOT NULL DEFAULT '',
    traceback_json TEXT NOT NULL DEFAULT '[]',
    created_at TEXT DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS execution_traces (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    trace_type TEXT NOT NULL DEFAULT 'mcp_call',
    agent_role TEXT NOT NULL DEFAULT '',
    tool_name TEXT NOT NULL DEFAULT '',
    input_summary TEXT NOT NULL DEFAULT '',
    output_summary TEXT NOT NULL DEFAULT '',
    success INTEGER NOT NULL DEFAULT 1,
    duration_ms INTEGER NOT NULL DEFAULT 0,
    project_name TEXT NOT NULL DEFAULT '',
    created_at TEXT DEFAULT CURRENT_TIMESTAMP
);

-- ===== AI系统 =====
CREATE TABLE IF NOT EXISTS ai_candidate_memories (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    content TEXT NOT NULL,
    source_type TEXT NOT NULL DEFAULT 'ai',
    proposed_by TEXT NOT NULL DEFAULT 'ai',
    trust_level TEXT NOT NULL DEFAULT 'unknown',
    review_status TEXT NOT NULL DEFAULT 'candidate',
    created_at TEXT DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS task_packs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    content TEXT NOT NULL DEFAULT '',
    pack_type TEXT NOT NULL DEFAULT 'codex',
    source_project TEXT NOT NULL DEFAULT '',
    created_by TEXT NOT NULL DEFAULT 'ai',
    review_status TEXT NOT NULL DEFAULT 'candidate',
    created_at TEXT DEFAULT CURRENT_TIMESTAMP
);

-- ===== 审核门禁 =====
CREATE TABLE IF NOT EXISTS review_queue (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    content TEXT NOT NULL,
    source_type TEXT NOT NULL,
    review_status TEXT NOT NULL DEFAULT 'candidate',
    trust_level TEXT NOT NULL DEFAULT 'unknown',
    scope TEXT NOT NULL DEFAULT 'ai',
    created_by TEXT NOT NULL DEFAULT 'ai',
    reviewed_by TEXT NOT NULL DEFAULT '',
    review_reason TEXT NOT NULL DEFAULT '',
    metadata_json TEXT NOT NULL DEFAULT '{}',
    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT DEFAULT NULL
);

-- ===== 评估系统 =====
CREATE TABLE IF NOT EXISTS eval_runs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    eval_type TEXT NOT NULL,
    target TEXT NOT NULL DEFAULT '',
    input_data TEXT NOT NULL DEFAULT '',
    expected_output TEXT NOT NULL DEFAULT '',
    actual_output TEXT NOT NULL DEFAULT '',
    score REAL NOT NULL DEFAULT 0.0,
    metric_scores TEXT NOT NULL DEFAULT '{}',
    model_used TEXT NOT NULL DEFAULT '',
    created_at TEXT DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS anti_patterns (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    pattern TEXT NOT NULL DEFAULT '',
    symptoms TEXT NOT NULL DEFAULT '',
    root_cause TEXT NOT NULL DEFAULT '',
    solution TEXT NOT NULL DEFAULT '',
    severity INTEGER NOT NULL DEFAULT 3,
    source_trace_id INTEGER NOT NULL DEFAULT 0,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP
);

-- ===== 上下文引擎 =====
CREATE TABLE IF NOT EXISTS context_packs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    goal TEXT NOT NULL,
    knowledge_ids TEXT NOT NULL DEFAULT '[]',
    route_id INTEGER NOT NULL DEFAULT 0,
    pack_data TEXT NOT NULL DEFAULT '{}',
    confidence_score REAL NOT NULL DEFAULT 0.0,
    token_estimate INTEGER NOT NULL DEFAULT 0,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP
);

-- ===== 学习引擎模块 =====
CREATE TABLE IF NOT EXISTS cognitive_load_events (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    source_type TEXT NOT NULL DEFAULT 'evaluate',
    source_id INTEGER NOT NULL DEFAULT 0,
    load_score REAL NOT NULL DEFAULT 0.0,
    factors_json TEXT NOT NULL DEFAULT '{}',
    created_at TEXT DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS memory_encodings (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    source_type TEXT NOT NULL,
    source_id INTEGER NOT NULL,
    encoding_type TEXT NOT NULL,
    content TEXT NOT NULL,
    fit_score REAL NOT NULL DEFAULT 0.0,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS encoding_strategies (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE,
    description TEXT NOT NULL DEFAULT '',
    modality TEXT NOT NULL DEFAULT 'visual',
    default_fit_score REAL NOT NULL DEFAULT 0.5,
    metadata_json TEXT NOT NULL DEFAULT '{}',
    created_at TEXT DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS skill_tasks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    task_type TEXT NOT NULL DEFAULT 'practice',
    target_skill TEXT NOT NULL DEFAULT '',
    expected_output TEXT NOT NULL DEFAULT '',
    rubric_json TEXT NOT NULL DEFAULT '{}',
    difficulty INTEGER NOT NULL DEFAULT 3,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT DEFAULT NULL
);

CREATE TABLE IF NOT EXISTS skill_attempts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    task_id INTEGER NOT NULL,
    output_text TEXT NOT NULL,
    rubric_score REAL NOT NULL DEFAULT 0.0,
    feedback_json TEXT NOT NULL DEFAULT '{}',
    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (task_id) REFERENCES skill_tasks(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS rubric_templates (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE,
    description TEXT NOT NULL DEFAULT '',
    weights_json TEXT NOT NULL DEFAULT '{}',
    dimensions_json TEXT NOT NULL DEFAULT '[]',
    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT DEFAULT NULL
);

CREATE TABLE IF NOT EXISTS teach_back_sessions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    source_type TEXT NOT NULL DEFAULT 'knowledge',
    source_id INTEGER NOT NULL DEFAULT 0,
    audience_level TEXT NOT NULL DEFAULT 'beginner',
    explanation TEXT NOT NULL,
    feynman_score REAL NOT NULL DEFAULT 0.0,
    gaps_json TEXT NOT NULL DEFAULT '[]',
    created_at TEXT DEFAULT CURRENT_TIMESTAMP
);

-- ===== 诊断与元认知 =====
CREATE TABLE IF NOT EXISTS diagnostics (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    target_type TEXT NOT NULL,
    target_id INTEGER NOT NULL,
    diag_type TEXT NOT NULL,
    score REAL NOT NULL DEFAULT 0.0,
    details TEXT NOT NULL DEFAULT '{}',
    recommendations TEXT NOT NULL DEFAULT '[]',
    created_at TEXT DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS metacognition_events (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    event_type TEXT NOT NULL,
    card_id INTEGER NOT NULL DEFAULT 0,
    predicted_score REAL NOT NULL DEFAULT 0.0,
    actual_score REAL NOT NULL DEFAULT 0.0,
    reflection TEXT NOT NULL DEFAULT '',
    created_at TEXT DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS learner_profile (
    id INTEGER PRIMARY KEY,
    profile_json TEXT NOT NULL DEFAULT '{}',
    updated_at TEXT DEFAULT NULL
);

-- ===== 掌握度评估 =====
CREATE TABLE IF NOT EXISTS mastery_assessments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    target_type TEXT NOT NULL DEFAULT 'card',
    target_id INTEGER NOT NULL DEFAULT 0,
    assessment_type TEXT NOT NULL DEFAULT 'auto',
    mastery_score REAL NOT NULL DEFAULT 0.0,
    dimension_scores TEXT NOT NULL DEFAULT '{}',
    gap_analysis TEXT NOT NULL DEFAULT '[]',
    recommendations TEXT NOT NULL DEFAULT '[]',
    created_at TEXT DEFAULT CURRENT_TIMESTAMP
);

-- ===== 索引 =====
CREATE INDEX IF NOT EXISTS idx_cards_deck ON cards(deck);
CREATE INDEX IF NOT EXISTS idx_cards_next_review ON cards(next_review_at);
CREATE INDEX IF NOT EXISTS idx_reviews_card ON reviews(card_id);
CREATE INDEX IF NOT EXISTS idx_cognitive_load_created ON cognitive_load_events(created_at);
CREATE INDEX IF NOT EXISTS idx_skill_tasks_type ON skill_tasks(task_type);
CREATE INDEX IF NOT EXISTS idx_skill_attempts_task ON skill_attempts(task_id);
CREATE INDEX IF NOT EXISTS idx_execution_traces_type ON execution_traces(trace_type);
CREATE INDEX IF NOT EXISTS idx_execution_traces_time ON execution_traces(created_at);
CREATE INDEX IF NOT EXISTS idx_eval_runs_type ON eval_runs(eval_type);
CREATE INDEX IF NOT EXISTS idx_agent_task_history_role ON agent_task_history(agent_role);
CREATE INDEX IF NOT EXISTS idx_machine_knowledge_type ON machine_knowledge_units(unit_type);
CREATE INDEX IF NOT EXISTS idx_machine_knowledge_confidence ON machine_knowledge_units(confidence);
CREATE INDEX IF NOT EXISTS idx_memory_encodings_source ON memory_encodings(source_type, source_id);
CREATE INDEX IF NOT EXISTS idx_teach_back_source ON teach_back_sessions(source_type, source_id);
CREATE INDEX IF NOT EXISTS idx_mastery_target ON mastery_assessments(target_type, target_id);
"""


@dataclass
class Document:
    id: int | None
    source_type: str
    title: str
    content: str
    source_url: str | None = None
    summary: str = ""
    tags: str = ""
    content_hash: str = ""
    created_at: str = ""
    updated_at: str = ""


@dataclass
class Source:
    id: int | None
    url: str
    title: str = ""
    tags: str = ""
    mode: str = "auto"
    enabled: bool = True
    last_document_id: int | None = None
    last_error: str = ""


class KnowledgeStore:
    def __init__(self, db_path: Path):
        self.db_path = db_path
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._conn: sqlite3.Connection | None = None

    @property
    def conn(self) -> sqlite3.Connection:
        if self._conn is None:
            self._conn = sqlite3.connect(str(self.db_path), check_same_thread=False)
            self._conn.row_factory = sqlite3.Row
        return self._conn

    def close(self) -> None:
        if self._conn is not None:
            self._conn.close()
            self._conn = None

    def _fetch(self, sql: str, params: tuple = ()) -> list[sqlite3.Row]:
        with self.connect() as conn:
            return list(conn.execute(sql, params))

    def _fetch_one(self, sql: str, params: tuple = ()) -> sqlite3.Row | None:
        rows = self._fetch(sql, params)
        return rows[0] if rows else None

    def connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def init(self) -> None:
        with self.connect() as conn:
            conn.executescript(SCHEMA)
        self._migrate()

    def _migrate(self) -> None:
        """Run schema migrations for existing databases."""
        with self.connect() as conn:
            # Migration v1: add pinned column to entities
            try:
                conn.execute("ALTER TABLE entities ADD COLUMN pinned INTEGER NOT NULL DEFAULT 0")
            except Exception:
                pass  # Column already exists

    @staticmethod
    def utc_now() -> str:
        return datetime.now(timezone.utc).isoformat()

    def log_event(self, event_type: str, message: str = "", payload: dict[str, Any] | None = None) -> int:
        now = self.utc_now()
        with self.connect() as conn:
            cur = conn.execute(
                "INSERT INTO events(event_type, message, payload_json, created_at) VALUES (?, ?, ?, ?)",
                (event_type, message, json.dumps(payload or {}, ensure_ascii=False), now),
            )
            return int(cur.lastrowid)

    def upsert_document(self, doc: Document) -> int:
        now = self.utc_now()
        with self.connect() as conn:
            existing = None
            if doc.source_url:
                existing = conn.execute("SELECT id, content_hash FROM documents WHERE source_url = ?", (doc.source_url,)).fetchone()
            if existing:
                doc_id = int(existing["id"])
                conn.execute(
                    """
                    UPDATE documents
                    SET source_type=?, title=?, content=?, summary=?, tags=?, content_hash=?, updated_at=?
                    WHERE id=?
                    """,
                    (
                        doc.source_type,
                        doc.title,
                        doc.content,
                        doc.summary,
                        doc.tags,
                        doc.content_hash,
                        now,
                        doc_id,
                    ),
                )
                return doc_id

            cur = conn.execute(
                """
                INSERT INTO documents(source_type, source_url, title, content, summary, tags, content_hash, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    doc.source_type,
                    doc.source_url,
                    doc.title,
                    doc.content,
                    doc.summary,
                    doc.tags,
                    doc.content_hash,
                    now,
                    now,
                ),
            )
            return int(cur.lastrowid)

    @staticmethod
    def _fts_query(query: str) -> str:
        # FTS5 has a strict query syntax. For personal users, a phrase search is
        # more forgiving than surfacing syntax errors for punctuation-heavy text.
        cleaned = query.strip().replace('"', ' ')
        if not cleaned:
            return '""'
        terms = [term for term in cleaned.split() if term]
        return " OR ".join(f'"{term}"' for term in terms)

    def search(self, query: str, limit: int = 20) -> list[sqlite3.Row]:
        fts_query = self._fts_query(query)
        with self.connect() as conn:
            try:
                return list(
                    conn.execute(
                        """
                        SELECT d.id, d.title, d.source_type, d.source_url, d.summary, d.tags, d.updated_at,
                               snippet(documents_fts, 1, '[', ']', '...', 16) AS snippet
                        FROM documents_fts
                        JOIN documents d ON d.id = documents_fts.rowid
                        WHERE documents_fts MATCH ?
                        ORDER BY rank
                        LIMIT ?
                        """,
                        (fts_query, limit),
                    )
                )
            except sqlite3.OperationalError:
                # Safe fallback for unusual FTS environments.
                like = f"%{query}%"
                return list(
                    conn.execute(
                        """
                        SELECT id, title, source_url, summary, tags, updated_at,
                               substr(content, 1, 240) AS snippet
                        FROM documents
                        WHERE title LIKE ? OR content LIKE ? OR summary LIKE ? OR tags LIKE ?
                        ORDER BY updated_at DESC
                        LIMIT ?
                        """,
                        (like, like, like, like, limit),
                    )
                )

    def list_recent(self, limit: int = 20) -> list[sqlite3.Row]:
        with self.connect() as conn:
            return list(
                conn.execute(
                    "SELECT id, source_type, title, source_url, summary, tags, updated_at FROM documents ORDER BY updated_at DESC LIMIT ?",
                    (limit,),
                )
            )

    def get_document(self, doc_id: int) -> sqlite3.Row | None:
        with self.connect() as conn:
            return conn.execute(
                "SELECT id, source_type, source_url, title, content, summary, tags, created_at, updated_at FROM documents WHERE id=?",
                (doc_id,),
            ).fetchone()

    def delete_document(self, doc_id: int) -> bool:
        with self.connect() as conn:
            cur = conn.execute("DELETE FROM documents WHERE id=?", (doc_id,))
            return cur.rowcount > 0

    def count_documents(self) -> int:
        with self.connect() as conn:
            row = conn.execute("SELECT COUNT(*) AS n FROM documents").fetchone()
            return int(row["n"] if row else 0)

    def rebuild_fts_index(self) -> None:
        with self.connect() as conn:
            conn.execute("INSERT INTO documents_fts(documents_fts) VALUES('rebuild')")

    def export_documents(self) -> list[dict[str, Any]]:
        with self.connect() as conn:
            return [dict(row) for row in conn.execute("SELECT * FROM documents ORDER BY updated_at DESC")]

    def add_source(self, source: Source) -> int:
        now = self.utc_now()
        with self.connect() as conn:
            cur = conn.execute(
                """
                INSERT INTO sources(url, title, tags, mode, enabled, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(url) DO UPDATE SET
                    title=excluded.title,
                    tags=excluded.tags,
                    mode=excluded.mode,
                    enabled=excluded.enabled,
                    updated_at=excluded.updated_at
                RETURNING id
                """,
                (source.url, source.title, source.tags, source.mode, int(source.enabled), now, now),
            )
            row = cur.fetchone()
            return int(row["id"])

    def list_sources(self, enabled_only: bool = False) -> list[sqlite3.Row]:
        sql = "SELECT * FROM sources"
        params: tuple[Any, ...] = ()
        if enabled_only:
            sql += " WHERE enabled=1"
        sql += " ORDER BY updated_at DESC"
        with self.connect() as conn:
            return list(conn.execute(sql, params))



    # === Conflict Detection ===

    def find_conflicts(self, name: str, threshold: float = 0.3) -> list[dict]:
        """Find entities with similar names (potential conflicts)."""
        import difflib
        all_entities = self._fetch("SELECT id, name, entity_type, description FROM entities")
        conflicts = []
        for row in all_entities:
            if row["name"].lower() == name.lower():
                continue
            ratio = difflib.SequenceMatcher(None, name.lower(), row["name"].lower()).ratio()
            if ratio >= threshold:
                conflicts.append({**dict(row), "similarity": round(ratio, 3)})
        return sorted(conflicts, key=lambda x: -x["similarity"])

    def resolve_conflict(self, keep_id: int, merge_id: int) -> dict:
        """Merge two entities into one, keeping keep_id."""
        target = self.get_entity(merge_id)
        if not target:
            return {"error": f"Entity {merge_id} not found"}
        # Move all relations
        with self.connect() as conn:
            conn.execute("UPDATE relations SET source_entity_id=? WHERE source_entity_id=?", (keep_id, merge_id))
            conn.execute("UPDATE relations SET target_entity_id=? WHERE target_entity_id=?", (keep_id, merge_id))
            conn.execute("UPDATE observations SET entity_id=? WHERE entity_id=?", (keep_id, merge_id))
            conn.execute("DELETE FROM entities WHERE id=?", (merge_id,))
        return {"merged": target["name"], "kept_id": keep_id, "deleted_id": merge_id}

    # === Pin/Unpin ===

    def pin_entity(self, name: str) -> bool:
        with self.connect() as conn:
            cur = conn.execute("UPDATE entities SET pinned=1 WHERE name=?", (name,))
            return cur.rowcount > 0

    def unpin_entity(self, name: str) -> bool:
        with self.connect() as conn:
            cur = conn.execute("UPDATE entities SET pinned=0 WHERE name=?", (name,))
            return cur.rowcount > 0

    def list_pinned(self) -> list[dict]:
        rows = self._fetch("SELECT * FROM entities WHERE pinned=1 ORDER BY updated_at DESC")
        return [dict(r) for r in rows]



    def upsert_entity(self, name: str, entity_type: str = "concept", description: str = "", metadata: dict | None = None) -> int:
        """Create or update an entity. Returns entity ID."""
        now = self.utc_now()
        meta_json = json.dumps(metadata or {})
        with self.connect() as conn:
            cur = conn.execute(
                """INSERT INTO entities(name, entity_type, description, metadata, created_at, updated_at)
                   VALUES (?, ?, ?, ?, ?, ?)
                   ON CONFLICT(name) DO UPDATE SET
                       entity_type=CASE WHEN excluded.entity_type != "concept" THEN excluded.entity_type ELSE entity_type END,
                       description=excluded.description,
                       metadata=excluded.metadata,
                       updated_at=excluded.updated_at
                   RETURNING id""",
                (name, entity_type, description, meta_json, now, now),
            )
            row = cur.fetchone()
            return int(row["id"])

    def get_entity(self, entity_id: int) -> dict | None:
        row = self._fetch_one("SELECT * FROM entities WHERE id=?", (entity_id,))
        return dict(row) if row else None

    def find_entity(self, name: str) -> dict | None:
        row = self._fetch_one("SELECT * FROM entities WHERE name=?", (name,))
        return dict(row) if row else None

    def search_entities(self, query: str, limit: int = 20) -> list[dict]:
        like = f"%{query}%"
        rows = self._fetch(
            "SELECT * FROM entities WHERE name LIKE ? OR description LIKE ? ORDER BY updated_at DESC LIMIT ?",
            (like, like, limit),
        )
        return [dict(r) for r in rows]

    def add_relation(self, source_name: str, target_name: str, relation_type: str, weight: float = 1.0, description: str = "") -> int | None:
        """Create a relation between two entities (auto-creates entities if needed)."""
        src_id = self.upsert_entity(source_name)
        tgt_id = self.upsert_entity(target_name)
        now = self.utc_now()
        with self.connect() as conn:
            try:
                cur = conn.execute(
                    """INSERT INTO relations(source_entity_id, target_entity_id, relation_type, weight, description, created_at)
                       VALUES (?, ?, ?, ?, ?, ?)
                       ON CONFLICT(source_entity_id, target_entity_id, relation_type) DO UPDATE SET
                           weight=excluded.weight,
                           description=CASE WHEN excluded.description != "" THEN excluded.description ELSE description END
                       RETURNING id""",
                    (src_id, tgt_id, relation_type, weight, description, now),
                )
                row = cur.fetchone()
                return int(row["id"]) if row else None
            except Exception:
                return None

    def get_relations(self, entity_name: str, relation_type: str | None = None) -> list[dict]:
        entity = self.find_entity(entity_name)
        if not entity:
            return []
        eid = entity["id"]
        sql = """SELECT r.*, src.name AS source_name, tgt.name AS target_name
                 FROM relations r
                 JOIN entities src ON r.source_entity_id = src.id
                 JOIN entities tgt ON r.target_entity_id = tgt.id
                 WHERE (r.source_entity_id = ? OR r.target_entity_id = ?)"""
        params: list = [eid, eid]
        if relation_type:
            sql += " AND r.relation_type = ?"
            params.append(relation_type)
        rows = self._fetch(sql, tuple(params))
        return [dict(r) for r in rows]

    def query_knowledge_graph(self, entity_name: str, depth: int = 1) -> dict:
        """Query the knowledge graph around an entity."""
        entity = self.find_entity(entity_name)
        if not entity:
            return {"entity": None, "relations": [], "related_entities": []}
        relations = self.get_relations(entity_name)
        related_ids = set()
        for r in relations:
            related_ids.add(r["source_entity_id"])
            related_ids.add(r["target_entity_id"])
        related_ids.discard(entity["id"])
        related = []
        for rid in related_ids:
            e = self.get_entity(rid)
            if e:
                related.append(e)
        return {"entity": dict(entity), "relations": relations, "related_entities": related}

    def delete_entity(self, name: str) -> bool:
        entity = self.find_entity(name)
        if not entity:
            return False
        with self.connect() as conn:
            conn.execute("DELETE FROM relations WHERE source_entity_id=? OR target_entity_id=?", (entity["id"], entity["id"]))
            conn.execute("DELETE FROM entities WHERE id=?", (entity["id"],))
        return True

    # === Session Methods ===

    def create_session(self, session_id: str, project: str = "", directory: str = "") -> bool:
        now = self.utc_now()
        with self.connect() as conn:
            try:
                conn.execute(
                    "INSERT INTO sessions(id, project, directory, status, started_at) VALUES (?, ?, ?, 'active', ?)",
                    (session_id, project, directory, now),
                )
                return True
            except Exception:
                return False

    def end_session(self, session_id: str, summary: str = "") -> bool:
        now = self.utc_now()
        with self.connect() as conn:
            cur = conn.execute(
                "UPDATE sessions SET status='ended', ended_at=?, summary=? WHERE id=? AND status='active'",
                (now, summary, session_id),
            )
            return cur.rowcount > 0

    def get_session_context(self, session_id: str) -> dict | None:
        session = self._fetch_one("SELECT * FROM sessions WHERE id=?", (session_id,))
        if not session:
            return None
        obs = self._fetch(
            "SELECT id, observation_type, title, content, topic_key, created_at FROM observations WHERE session_id=? ORDER BY created_at DESC LIMIT 20",
            (session_id,),
        )
        return {"session": dict(session), "observations": [dict(r) for r in obs]}

    def list_sessions(self, limit: int = 20) -> list[dict]:
        rows = self._fetch("SELECT * FROM sessions ORDER BY started_at DESC LIMIT ?", (limit,))
        return [dict(r) for r in rows]

    # === Observation Methods ===

    def add_observation(self, session_id: str, title: str, content: str, observation_type: str = "note",
                        entity_name: str | None = None, topic_key: str = "", source: str = "") -> int:
        now = self.utc_now()
        entity_id = None
        if entity_name:
            entity_id = self.upsert_entity(entity_name)
        content_hash = str(hash(content))
        # Check for duplicates
        existing = self._fetch_one(
            "SELECT id, duplicate_count FROM observations WHERE content_hash=? AND session_id=?",
            (content_hash, session_id),
        )
        if existing:
            with self.connect() as conn:
                conn.execute("UPDATE observations SET duplicate_count=duplicate_count+1, updated_at=? WHERE id=?", (now, existing["id"]))
            return int(existing["id"])
        with self.connect() as conn:
            cur = conn.execute(
                """INSERT INTO observations(session_id, entity_id, observation_type, title, content, source, topic_key, content_hash, created_at, updated_at)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?) RETURNING id""",
                (session_id, entity_id, observation_type, title, content, source, topic_key, content_hash, now, now),
            )
            row = cur.fetchone()
            return int(row["id"])

    def search_observations(self, query: str, limit: int = 20) -> list[dict]:
        fts_query = " OR ".join(f'"{t}"' for t in query.strip().split() if t) or '""'
        try:
            rows = self._fetch(
                """SELECT o.id, o.title, o.content, o.observation_type, o.topic_key, o.created_at, o.session_id,
                          snippet(observations_fts, 1, "[", "]", "...", 32) AS snippet
                   FROM observations_fts
                   JOIN observations o ON o.id = observations_fts.rowid
                   WHERE observations_fts MATCH ?
                   ORDER BY rank
                   LIMIT ?""",
                (fts_query, limit),
            )
            return [dict(r) for r in rows]
        except Exception:
            like = f"%{query}%"
            rows = self._fetch(
                "SELECT * FROM observations WHERE title LIKE ? OR content LIKE ? ORDER BY updated_at DESC LIMIT ?",
                (like, like, limit),
            )
            return [dict(r) for r in rows]



    # === MVP CRUD methods ===

    def insert_document(self, title: str, content: str, source_type: str = "manual", source_url: str = "", tags: str = "", content_hash: str = "") -> int:
        now = self.utc_now()
        with self.connect() as conn:
            cur = conn.execute(
                "INSERT INTO documents (source_type, source_url, title, content, summary, tags, content_hash, created_at, updated_at) VALUES (?,?,?,?,?,?,?,?,?)",
                (source_type, source_url, title, content, content[:200], tags, content_hash, now, now))
            return cur.lastrowid

    def insert_card(self, title: str, content: str, tags: str = "", source_id: int = 0, deck: str = "default") -> int:
        now = self.utc_now()
        with self.connect() as conn:
            cur = conn.execute(
                "INSERT INTO cards (title, content, deck, tags, source_id, memory_strength, review_count, interval_seconds, next_review_at, created_at, updated_at) VALUES (?,?,?,?,?,0.0,0,86400,?,?,?)",
                (title, content, deck, tags, source_id, now, now, now))
            return cur.lastrowid

    def insert_review(self, card_id: int, score: float, strength_before: float = 0.0, strength_after: float = 0.0) -> int:
        now = self.utc_now()
        with self.connect() as conn:
            cur = conn.execute(
                "INSERT INTO reviews (card_id, score, strength_before, strength_after, created_at) VALUES (?,?,?,?,?)",
                (card_id, score, strength_before, strength_after, now))
            # Update card review schedule
            card = conn.execute("SELECT * FROM cards WHERE id=?", (card_id,)).fetchone()
            if card:
                rc = card["review_count"] + 1
                ms = min(1.0, card["memory_strength"] + score * 0.1)
                interval = int(card["interval_seconds"] * (1.2 if score >= 3.0 else 0.5))
                interval = max(60, min(interval, 365 * 86400))
                conn.execute("UPDATE cards SET review_count=?, memory_strength=?, interval_seconds=?, next_review_at=datetime(?, '+' || ? || ' seconds'), updated_at=? WHERE id=?",
                    (rc, ms, interval, now, interval, now, card_id))
            return cur.lastrowid

    def get_due_cards(self, limit: int = 20) -> list:
        now = self.utc_now()
        return [dict(r) for r in self._fetch(
            "SELECT * FROM cards WHERE next_review_at <= ? ORDER BY next_review_at ASC LIMIT ?", (now, limit))]


    def update_source_result(self, source_id: int, document_id: int | None, error: str = "") -> None:
        now = self.utc_now()
        with self.connect() as conn:
            conn.execute(
                """
                UPDATE sources
                SET last_document_id=?, last_error=?, last_checked_at=?, updated_at=?
                WHERE id=?
                """,
                (document_id, error, now, now, source_id),
            )

