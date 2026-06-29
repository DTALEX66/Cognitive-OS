-- 007_p0_gaps.sql
-- P0缺口: 诊断系统 + 评估层 + 回流层 + A转B

CREATE TABLE IF NOT EXISTS diagnostics (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  target_type TEXT NOT NULL DEFAULT 'knowledge',
  target_id INTEGER NOT NULL DEFAULT 0,
  diag_type TEXT NOT NULL DEFAULT 'prerequisite',
  score REAL NOT NULL DEFAULT 0,
  details TEXT NOT NULL DEFAULT '{}',
  recommendations TEXT NOT NULL DEFAULT '[]',
  created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS eval_runs (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  eval_type TEXT NOT NULL DEFAULT 'rag',
  target TEXT NOT NULL DEFAULT '',
  input_data TEXT NOT NULL DEFAULT '',
  expected_output TEXT NOT NULL DEFAULT '',
  actual_output TEXT NOT NULL DEFAULT '',
  score REAL NOT NULL DEFAULT 0,
  metric_scores TEXT NOT NULL DEFAULT '{}',
  model_used TEXT NOT NULL DEFAULT '',
  created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS anti_patterns (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  title TEXT NOT NULL,
  pattern TEXT NOT NULL DEFAULT '',
  symptoms TEXT NOT NULL DEFAULT '',
  root_cause TEXT NOT NULL DEFAULT '',
  solution TEXT NOT NULL DEFAULT '',
  severity INTEGER NOT NULL DEFAULT 3,
  source_project TEXT NOT NULL DEFAULT '',
  source_trace_id INTEGER DEFAULT 0,
  created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS a_to_b_candidates (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  a_source_type TEXT NOT NULL DEFAULT 'card',
  a_source_id INTEGER NOT NULL DEFAULT 0,
  a_title TEXT NOT NULL DEFAULT '',
  a_content TEXT NOT NULL DEFAULT '',
  a_strength REAL NOT NULL DEFAULT 0,
  a_review_count INTEGER NOT NULL DEFAULT 0,
  b_title TEXT NOT NULL DEFAULT '',
  b_content TEXT NOT NULL DEFAULT '',
  b_unit_type TEXT NOT NULL DEFAULT 'rule',
  status TEXT NOT NULL DEFAULT 'pending',
  created_at TEXT NOT NULL,
  updated_at TEXT NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_diag_target ON diagnostics(target_type, target_id);
CREATE INDEX IF NOT EXISTS idx_eval_type ON eval_runs(eval_type);
CREATE INDEX IF NOT EXISTS idx_anti_patterns_severity ON anti_patterns(severity);
CREATE INDEX IF NOT EXISTS idx_a2b_status ON a_to_b_candidates(status);
