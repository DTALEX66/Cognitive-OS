-- 006_b_line_os.sql
CREATE TABLE IF NOT EXISTS machine_knowledge_units (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  title TEXT NOT NULL,
  content TEXT NOT NULL DEFAULT '',
  unit_type TEXT NOT NULL DEFAULT 'rule',
  source_type TEXT NOT NULL DEFAULT 'external',
  source_url TEXT NOT NULL DEFAULT '',
  tags TEXT NOT NULL DEFAULT '',
  confidence REAL NOT NULL DEFAULT 0.5,
  version INTEGER NOT NULL DEFAULT 1,
  created_at TEXT NOT NULL,
  updated_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS machine_routes (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  goal TEXT NOT NULL,
  context_requirements TEXT NOT NULL DEFAULT '',
  knowledge_requirements TEXT NOT NULL DEFAULT '',
  tool_requirements TEXT NOT NULL DEFAULT '',
  status TEXT NOT NULL DEFAULT 'active',
  created_at TEXT NOT NULL,
  updated_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS route_steps_b (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  route_id INTEGER NOT NULL,
  step_type TEXT NOT NULL DEFAULT 'retrieve',
  description TEXT NOT NULL DEFAULT '',
  expected_output TEXT NOT NULL DEFAULT '',
  order_num INTEGER NOT NULL DEFAULT 0,
  completed INTEGER NOT NULL DEFAULT 0,
  FOREIGN KEY (route_id) REFERENCES machine_routes(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS agent_roles (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  name TEXT NOT NULL UNIQUE,
  role_type TEXT NOT NULL DEFAULT 'worker',
  description TEXT NOT NULL DEFAULT '',
  capabilities TEXT NOT NULL DEFAULT '[]',
  priority INTEGER NOT NULL DEFAULT 5,
  created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS context_packs (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  goal TEXT NOT NULL DEFAULT '',
  knowledge_ids TEXT NOT NULL DEFAULT '[]',
  route_id INTEGER DEFAULT 0,
  pack_data TEXT NOT NULL DEFAULT '{}',
  confidence_score REAL NOT NULL DEFAULT 0,
  token_estimate INTEGER NOT NULL DEFAULT 0,
  created_at TEXT NOT NULL
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
  created_at TEXT NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_machine_knowledge_tags ON machine_knowledge_units(tags);
CREATE INDEX IF NOT EXISTS idx_route_steps_b_route ON route_steps_b(route_id);
CREATE INDEX IF NOT EXISTS idx_execution_traces_type ON execution_traces(trace_type);
