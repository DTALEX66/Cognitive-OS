-- 012_palace_governance.sql: 知识宫殿 + 学习治理表
CREATE TABLE IF NOT EXISTS palace_rooms (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    knowledge_type TEXT NOT NULL,
    parent_id INTEGER REFERENCES palace_rooms(id),
    created_at TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS palace_items (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    room_id INTEGER NOT NULL REFERENCES palace_rooms(id),
    card_id INTEGER REFERENCES cards(id),
    title TEXT NOT NULL,
    knowledge_type TEXT NOT NULL,
    created_at TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS profile_records (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    date TEXT NOT NULL UNIQUE,
    data TEXT NOT NULL DEFAULT '{}',
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS teach_outputs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    topic TEXT NOT NULL,
    method TEXT NOT NULL,
    prompt TEXT NOT NULL,
    created_at TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE INDEX IF NOT EXISTS idx_profile_records_date ON profile_records(date);
CREATE INDEX IF NOT EXISTS idx_palace_rooms_parent ON palace_rooms(parent_id);
CREATE INDEX IF NOT EXISTS idx_teach_outputs_topic ON teach_outputs(topic);
