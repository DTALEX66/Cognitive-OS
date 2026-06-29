-- 009_palace_phase3.sql
-- Phase 3: Knowledge Palace - Routes (route walk) and visual anchors
-- Depends on: 004_ab_line_tables.sql (palace_nodes)

CREATE TABLE IF NOT EXISTS palace_routes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    description TEXT NOT NULL DEFAULT '',
    space TEXT NOT NULL DEFAULT '',
    created_at TEXT NOT NULL DEFAULT (datetime('now')),
    updated_at TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS palace_route_steps (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    route_id INTEGER NOT NULL,
    node_id INTEGER NOT NULL,
    step_order INTEGER NOT NULL DEFAULT 0,
    instruction TEXT NOT NULL DEFAULT '',
    FOREIGN KEY (route_id) REFERENCES palace_routes(id) ON DELETE CASCADE,
    FOREIGN KEY (node_id) REFERENCES palace_nodes(id) ON DELETE CASCADE
);
