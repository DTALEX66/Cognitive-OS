-- 011_agent_os.sql
-- Agent OS: Orchestration runtime tables for agent execution, model calls,
-- sandbox executions, and observability tracing.

-- Core orchestration run record: tracks each agent workflow execution
CREATE TABLE IF NOT EXISTS agent_runs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    run_key TEXT NOT NULL UNIQUE,
    goal TEXT NOT NULL DEFAULT '',
    agent_role TEXT NOT NULL DEFAULT '',
    route_id INTEGER NOT NULL DEFAULT 0,
    parent_run_id INTEGER NOT NULL DEFAULT 0,
    status TEXT NOT NULL DEFAULT 'pending',
    started_at TEXT NOT NULL DEFAULT '',
    completed_at TEXT NOT NULL DEFAULT '',
    duration_ms INTEGER NOT NULL DEFAULT 0,
    total_steps INTEGER NOT NULL DEFAULT 0,
    completed_steps INTEGER NOT NULL DEFAULT 0,
    failed_steps INTEGER NOT NULL DEFAULT 0,
    input_snapshot TEXT NOT NULL DEFAULT '{}',
    output_snapshot TEXT NOT NULL DEFAULT '{}',
    error_message TEXT NOT NULL DEFAULT '',
    metadata_json TEXT NOT NULL DEFAULT '{}',
    created_at TEXT NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_agent_runs_status ON agent_runs(status, created_at DESC);
CREATE INDEX IF NOT EXISTS idx_agent_runs_goal ON agent_runs(goal);
CREATE INDEX IF NOT EXISTS idx_agent_runs_role ON agent_runs(agent_role, created_at DESC);

-- State node execution records within an orchestration run
CREATE TABLE IF NOT EXISTS agent_nodes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    run_id INTEGER NOT NULL,
    node_name TEXT NOT NULL DEFAULT '',
    node_type TEXT NOT NULL DEFAULT 'action',
    parent_node_id INTEGER NOT NULL DEFAULT 0,
    state_before TEXT NOT NULL DEFAULT '{}',
    state_after TEXT NOT NULL DEFAULT '{}',
    status TEXT NOT NULL DEFAULT 'pending',
    attempt_number INTEGER NOT NULL DEFAULT 1,
    max_attempts INTEGER NOT NULL DEFAULT 3,
    started_at TEXT NOT NULL DEFAULT '',
    completed_at TEXT NOT NULL DEFAULT '',
    duration_ms INTEGER NOT NULL DEFAULT 0,
    error_message TEXT NOT NULL DEFAULT '',
    retry_backoff_ms INTEGER NOT NULL DEFAULT 1000,
    metadata_json TEXT NOT NULL DEFAULT '{}',
    created_at TEXT NOT NULL,
    FOREIGN KEY (run_id) REFERENCES agent_runs(id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_agent_nodes_run ON agent_nodes(run_id, created_at);
CREATE INDEX IF NOT EXISTS idx_agent_nodes_status ON agent_nodes(status, created_at DESC);
CREATE INDEX IF NOT EXISTS idx_agent_nodes_parent ON agent_nodes(parent_node_id);

-- Model call log: tracks every LLM invocation with token usage and latency
CREATE TABLE IF NOT EXISTS model_calls (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    run_id INTEGER NOT NULL DEFAULT 0,
    node_id INTEGER NOT NULL DEFAULT 0,
    model_name TEXT NOT NULL DEFAULT '',
    provider TEXT NOT NULL DEFAULT '',
    call_type TEXT NOT NULL DEFAULT 'completion',
    prompt_tokens INTEGER NOT NULL DEFAULT 0,
    completion_tokens INTEGER NOT NULL DEFAULT 0,
    total_tokens INTEGER NOT NULL DEFAULT 0,
    latency_ms INTEGER NOT NULL DEFAULT 0,
    cost_estimate REAL NOT NULL DEFAULT 0.0,
    temperature REAL NOT NULL DEFAULT 0.7,
    status TEXT NOT NULL DEFAULT 'success',
    error_message TEXT NOT NULL DEFAULT '',
    request_hash TEXT NOT NULL DEFAULT '',
    created_at TEXT NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_model_calls_run ON model_calls(run_id, created_at);
CREATE INDEX IF NOT EXISTS idx_model_calls_model ON model_calls(model_name, created_at DESC);
CREATE INDEX IF NOT EXISTS idx_model_calls_status ON model_calls(status);

-- Sandbox execution records: tracks command/script runs in isolated environments
CREATE TABLE IF NOT EXISTS sandbox_executions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    run_id INTEGER NOT NULL DEFAULT 0,
    node_id INTEGER NOT NULL DEFAULT 0,
    sandbox_type TEXT NOT NULL DEFAULT 'docker',
    command TEXT NOT NULL DEFAULT '',
    working_dir TEXT NOT NULL DEFAULT '',
    exit_code INTEGER,
    stdout_snippet TEXT NOT NULL DEFAULT '',
    stderr_snippet TEXT NOT NULL DEFAULT '',
    status TEXT NOT NULL DEFAULT 'pending',
    started_at TEXT NOT NULL DEFAULT '',
    completed_at TEXT NOT NULL DEFAULT '',
    duration_ms INTEGER NOT NULL DEFAULT 0,
    timeout_ms INTEGER NOT NULL DEFAULT 30000,
    memory_mb INTEGER NOT NULL DEFAULT 0,
    cpu_percent REAL NOT NULL DEFAULT 0.0,
    metadata_json TEXT NOT NULL DEFAULT '{}',
    created_at TEXT NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_sandbox_exec_run ON sandbox_executions(run_id, created_at);
CREATE INDEX IF NOT EXISTS idx_sandbox_exec_status ON sandbox_executions(status);

-- Observability spans: hierarchical tracing for distributed agent operations
CREATE TABLE IF NOT EXISTS observability_spans (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    trace_id TEXT NOT NULL DEFAULT '',
    span_id TEXT NOT NULL DEFAULT '',
    parent_span_id TEXT NOT NULL DEFAULT '',
    run_id INTEGER NOT NULL DEFAULT 0,
    node_id INTEGER NOT NULL DEFAULT 0,
    operation_name TEXT NOT NULL DEFAULT '',
    span_kind TEXT NOT NULL DEFAULT 'INTERNAL',
    status_code TEXT NOT NULL DEFAULT 'UNSET',
    status_message TEXT NOT NULL DEFAULT '',
    started_at TEXT NOT NULL DEFAULT '',
    completed_at TEXT NOT NULL DEFAULT '',
    duration_ms INTEGER NOT NULL DEFAULT 0,
    attributes_json TEXT NOT NULL DEFAULT '{}',
    events_json TEXT NOT NULL DEFAULT '[]',
    links_json TEXT NOT NULL DEFAULT '[]',
    resource_json TEXT NOT NULL DEFAULT '{}',
    created_at TEXT NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_obs_spans_trace ON observability_spans(trace_id, started_at);
CREATE INDEX IF NOT EXISTS idx_obs_spans_run ON observability_spans(run_id);
CREATE INDEX IF NOT EXISTS idx_obs_spans_parent ON observability_spans(parent_span_id);
CREATE INDEX IF NOT EXISTS idx_obs_spans_operation ON observability_spans(operation_name);
