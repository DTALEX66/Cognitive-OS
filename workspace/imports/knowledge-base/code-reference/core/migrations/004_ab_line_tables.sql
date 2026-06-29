-- Migration 004: A线 + B线 数据表
-- A线: cards, reviews, learning_routes, route_steps, palace_nodes
-- B线: ai_candidate_memories, task_packs

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
    next_review_at TEXT NOT NULL,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_cards_review ON cards(next_review_at);
CREATE INDEX IF NOT EXISTS idx_cards_deck ON cards(deck);

CREATE TABLE IF NOT EXISTS reviews (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    card_id INTEGER NOT NULL REFERENCES cards(id) ON DELETE CASCADE,
    score REAL NOT NULL DEFAULT 0.0,
    strength_before REAL NOT NULL DEFAULT 0.0,
    strength_after REAL NOT NULL DEFAULT 0.0,
    created_at TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_reviews_card ON reviews(card_id);

CREATE TABLE IF NOT EXISTS learning_routes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    description TEXT NOT NULL DEFAULT '',
    goal TEXT NOT NULL DEFAULT '',
    scope TEXT NOT NULL DEFAULT 'human',
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS route_steps (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    route_id INTEGER NOT NULL REFERENCES learning_routes(id) ON DELETE CASCADE,
    title TEXT NOT NULL,
    step_type TEXT NOT NULL DEFAULT 'read',
    resource_url TEXT NOT NULL DEFAULT '',
    order_num INTEGER NOT NULL DEFAULT 0,
    completed INTEGER NOT NULL DEFAULT 0,
    created_at TEXT NOT NULL
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

CREATE TABLE IF NOT EXISTS ai_candidate_memories (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    content TEXT NOT NULL,
    source_type TEXT NOT NULL DEFAULT 'ai',
    proposed_by TEXT NOT NULL DEFAULT 'ai',
    trust_level TEXT NOT NULL DEFAULT 'unknown',
    review_status TEXT NOT NULL DEFAULT 'candidate',
    created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS task_packs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    content TEXT NOT NULL,
    pack_type TEXT NOT NULL DEFAULT 'codex',
    source_project TEXT NOT NULL DEFAULT '',
    created_by TEXT NOT NULL DEFAULT 'ai',
    review_status TEXT NOT NULL DEFAULT 'candidate',
    created_at TEXT NOT NULL
);