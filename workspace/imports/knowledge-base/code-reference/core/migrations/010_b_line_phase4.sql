-- 010_b_line_phase4.sql
-- Phase 4: B-Line Machine Enhancement
-- Adds: mcp_permissions, machine_lessons, enhanced route states, role capabilities

-- MCP Permission guard: tool whitelist + rate limits per role
CREATE TABLE IF NOT EXISTS mcp_permissions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    role_name TEXT NOT NULL,
    tool_name TEXT NOT NULL,
    allowed INTEGER NOT NULL DEFAULT 1,
    rate_limit_per_min INTEGER NOT NULL DEFAULT 60,
    rate_limit_per_hour INTEGER NOT NULL DEFAULT 1000,
    max_concurrent INTEGER NOT NULL DEFAULT 5,
    require_approval INTEGER NOT NULL DEFAULT 0,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    UNIQUE(role_name, tool_name)
);

-- MCP audit log for permission checks
CREATE TABLE IF NOT EXISTS mcp_audit_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    role_name TEXT NOT NULL,
    tool_name TEXT NOT NULL,
    action TEXT NOT NULL DEFAULT 'call',
    allowed INTEGER NOT NULL DEFAULT 1,
    reason TEXT NOT NULL DEFAULT '',
    request_params_hash TEXT NOT NULL DEFAULT '',
    ip_address TEXT NOT NULL DEFAULT '',
    created_at TEXT NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_mcp_audit_role ON mcp_audit_log(role_name, created_at);
CREATE INDEX IF NOT EXISTS idx_mcp_audit_tool ON mcp_audit_log(tool_name, created_at);

-- Rate limit tracking (token bucket state)
CREATE TABLE IF NOT EXISTS mcp_rate_buckets (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    role_name TEXT NOT NULL,
    tool_name TEXT NOT NULL,
    window_start TEXT NOT NULL,
    call_count INTEGER NOT NULL DEFAULT 1,
    UNIQUE(role_name, tool_name, window_start)
);

-- Machine lessons: experience extracted from B-line execution
CREATE TABLE IF NOT EXISTS machine_lessons (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    lesson_type TEXT NOT NULL DEFAULT 'pattern',
    category TEXT NOT NULL DEFAULT 'general',
    trigger_condition TEXT NOT NULL DEFAULT '',
    recommended_action TEXT NOT NULL DEFAULT '',
    source_trace_ids TEXT NOT NULL DEFAULT '[]',
    source_eval_ids TEXT NOT NULL DEFAULT '[]',
    success_count INTEGER NOT NULL DEFAULT 1,
    failure_count INTEGER NOT NULL DEFAULT 0,
    confidence REAL NOT NULL DEFAULT 0.5,
    impact_score REAL NOT NULL DEFAULT 0.0,
    applied_count INTEGER NOT NULL DEFAULT 0,
    last_applied_at TEXT NOT NULL DEFAULT '',
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_machine_lessons_type ON machine_lessons(lesson_type, confidence DESC);
CREATE INDEX IF NOT EXISTS idx_machine_lessons_category ON machine_lessons(category, impact_score DESC);

-- Lesson-to-route feedback links
CREATE TABLE IF NOT EXISTS lesson_route_links (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    lesson_id INTEGER NOT NULL,
    route_id INTEGER NOT NULL,
    effect TEXT NOT NULL DEFAULT 'neutral',
    applied_at TEXT NOT NULL,
    FOREIGN KEY (lesson_id) REFERENCES machine_lessons(id) ON DELETE CASCADE,
    FOREIGN KEY (route_id) REFERENCES machine_routes(id) ON DELETE CASCADE
);

-- Eval batch runs
CREATE TABLE IF NOT EXISTS eval_batches (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    batch_name TEXT NOT NULL,
    description TEXT NOT NULL DEFAULT '',
    eval_type TEXT NOT NULL DEFAULT 'rag',
    total_cases INTEGER NOT NULL DEFAULT 0,
    passed_cases INTEGER NOT NULL DEFAULT 0,
    avg_score REAL NOT NULL DEFAULT 0.0,
    min_score REAL NOT NULL DEFAULT 0.0,
    max_score REAL NOT NULL DEFAULT 0.0,
    pass_threshold REAL NOT NULL DEFAULT 0.7,
    status TEXT NOT NULL DEFAULT 'running',
    report_json TEXT NOT NULL DEFAULT '{}',
    created_at TEXT NOT NULL,
    completed_at TEXT NOT NULL DEFAULT ''
);

-- Eval batch items (individual test cases within a batch)
CREATE TABLE IF NOT EXISTS eval_batch_items (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    batch_id INTEGER NOT NULL,
    run_id INTEGER NOT NULL DEFAULT 0,
    case_name TEXT NOT NULL DEFAULT '',
    input_data TEXT NOT NULL DEFAULT '',
    expected_output TEXT NOT NULL DEFAULT '',
    actual_output TEXT NOT NULL DEFAULT '',
    score REAL NOT NULL DEFAULT 0.0,
    passed INTEGER NOT NULL DEFAULT 0,
    FOREIGN KEY (batch_id) REFERENCES eval_batches(id) ON DELETE CASCADE
);

-- Enhanced route with FSM state (add columns if not exist)
-- These use ALTER TABLE which may fail if columns already exist;
-- the test runner handles this by running each script against a fresh DB.
ALTER TABLE machine_routes ADD COLUMN fsm_state TEXT NOT NULL DEFAULT 'idle';
ALTER TABLE machine_routes ADD COLUMN fallback_route_id INTEGER DEFAULT 0;
ALTER TABLE machine_routes ADD COLUMN priority INTEGER NOT NULL DEFAULT 5;
ALTER TABLE machine_routes ADD COLUMN tags TEXT NOT NULL DEFAULT '';

-- Enhanced route steps with conditional branching
ALTER TABLE route_steps_b ADD COLUMN condition_expr TEXT NOT NULL DEFAULT '';
ALTER TABLE route_steps_b ADD COLUMN on_success_step_id INTEGER DEFAULT 0;
ALTER TABLE route_steps_b ADD COLUMN on_failure_step_id INTEGER DEFAULT 0;
ALTER TABLE route_steps_b ADD COLUMN retry_count INTEGER NOT NULL DEFAULT 0;
ALTER TABLE route_steps_b ADD COLUMN max_retries INTEGER NOT NULL DEFAULT 3;
ALTER TABLE route_steps_b ADD COLUMN timeout_ms INTEGER NOT NULL DEFAULT 30000;

-- Enhanced agent_roles with permission matrix
ALTER TABLE agent_roles ADD COLUMN permission_matrix TEXT NOT NULL DEFAULT '{}';
ALTER TABLE agent_roles ADD COLUMN max_concurrent_tasks INTEGER NOT NULL DEFAULT 5;
ALTER TABLE agent_roles ADD COLUMN rate_limit_per_min INTEGER NOT NULL DEFAULT 60;
ALTER TABLE agent_roles ADD COLUMN enabled INTEGER NOT NULL DEFAULT 1;

-- Enhanced execution traces with step snapshots
ALTER TABLE execution_traces ADD COLUMN input_snapshot TEXT NOT NULL DEFAULT '';
ALTER TABLE execution_traces ADD COLUMN output_snapshot TEXT NOT NULL DEFAULT '';
ALTER TABLE execution_traces ADD COLUMN step_order INTEGER NOT NULL DEFAULT 0;
ALTER TABLE execution_traces ADD COLUMN parent_trace_id INTEGER NOT NULL DEFAULT 0;
ALTER TABLE execution_traces ADD COLUMN tags TEXT NOT NULL DEFAULT '';
ALTER TABLE execution_traces ADD COLUMN metadata_json TEXT NOT NULL DEFAULT '{}';
