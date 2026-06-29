-- Migration 003: Isolation Layer - Review Queue
CREATE TABLE IF NOT EXISTS review_queue (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    content TEXT NOT NULL,
    source_type TEXT NOT NULL DEFAULT '',
    review_status TEXT NOT NULL DEFAULT 'candidate',
    trust_level TEXT NOT NULL DEFAULT 'unknown',
    scope TEXT NOT NULL DEFAULT 'ai',
    created_by TEXT NOT NULL DEFAULT 'ai',
    reviewed_by TEXT NOT NULL DEFAULT '',
    review_reason TEXT NOT NULL DEFAULT '',
    metadata_json TEXT NOT NULL DEFAULT '{}',
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_review_status ON review_queue(review_status);
CREATE INDEX IF NOT EXISTS idx_review_scope ON review_queue(scope);