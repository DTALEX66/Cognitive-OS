-- 005_a_line_ultimate.sql
-- A线极限增强: 认知负荷、记忆编码、技能实战、费曼输出等8张新表
-- 依赖: 已存在 cards/reviews/learning_routes/route_steps/palace_nodes 表

CREATE TABLE IF NOT EXISTS cognitive_load_events (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  source_type TEXT NOT NULL DEFAULT 'session',
  source_id INTEGER DEFAULT 0,
  load_score REAL NOT NULL DEFAULT 0,
  factors_json TEXT NOT NULL DEFAULT '{}',
  created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS memory_encodings (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  source_type TEXT NOT NULL,
  source_id INTEGER NOT NULL,
  encoding_type TEXT NOT NULL DEFAULT 'visual',
  content TEXT NOT NULL DEFAULT '',
  fit_score REAL NOT NULL DEFAULT 0,
  created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS skill_tasks (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  title TEXT NOT NULL,
  task_type TEXT NOT NULL DEFAULT 'practice',
  target_skill TEXT NOT NULL DEFAULT '',
  expected_output TEXT NOT NULL DEFAULT '',
  rubric_json TEXT NOT NULL DEFAULT '{}',
  difficulty INTEGER NOT NULL DEFAULT 3,
  created_at TEXT NOT NULL,
  updated_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS skill_attempts (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  task_id INTEGER NOT NULL,
  output_text TEXT NOT NULL DEFAULT '',
  rubric_score REAL NOT NULL DEFAULT 0,
  feedback_json TEXT NOT NULL DEFAULT '{}',
  created_at TEXT NOT NULL,
  FOREIGN KEY (task_id) REFERENCES skill_tasks(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS teach_back_sessions (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  source_type TEXT NOT NULL DEFAULT 'knowledge',
  source_id INTEGER NOT NULL DEFAULT 0,
  audience_level TEXT NOT NULL DEFAULT 'beginner',
  explanation TEXT NOT NULL DEFAULT '',
  feynman_score REAL NOT NULL DEFAULT 0,
  gaps_json TEXT NOT NULL DEFAULT '[]',
  created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS learning_experiments (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  title TEXT NOT NULL,
  target_metric TEXT NOT NULL DEFAULT '',
  status TEXT NOT NULL DEFAULT 'active',
  created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS learner_profile (
  id INTEGER PRIMARY KEY CHECK (id = 1),
  profile_json TEXT NOT NULL DEFAULT '{}',
  updated_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS metacognition_events (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  event_type TEXT NOT NULL DEFAULT 'predict',
  card_id INTEGER DEFAULT 0,
  predicted_score REAL DEFAULT 0,
  actual_score REAL DEFAULT 0,
  reflection TEXT NOT NULL DEFAULT '',
  created_at TEXT NOT NULL
);
