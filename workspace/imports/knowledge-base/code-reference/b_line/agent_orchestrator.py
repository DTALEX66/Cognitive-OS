from __future__ import annotations
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Callable
import json, uuid, sqlite3, threading, time

DEFAULT_ROLES = {
    "planner": ["task_decomposition", "route_planning"],
    "researcher": ["knowledge_retrieval", "context_assembly"],
    "coder": ["code_generation", "patch_creation"],
    "tester": ["test_generation", "validation"],
    "reviewer": ["code_review", "quality_check"],
    "security": ["security_audit", "permission_check"],
    "memory_curator": ["experience_tracking", "lesson_extraction"],
}


class NodeType(str, Enum):
    """Agent node types - think/act/observe/evaluate/decide primitives."""
    THINK = "think"
    ACT = "act"
    OBSERVE = "observe"
    EVALUATE = "evaluate"
    DECIDE = "decide"


class RunStatus(str, Enum):
    PENDING = "pending"
    THINKING = "thinking"
    ACTING = "acting"
    OBSERVING = "observing"
    EVALUATING = "evaluating"
    DECIDING = "deciding"
    DONE = "done"
    FAILED = "failed"
    CANCELLED = "cancelled"


class ExecMode(str, Enum):
    SEQUENTIAL = "sequential"
    PARALLEL = "parallel"
    CONDITIONAL = "conditional"
    LOOP = "loop"


@dataclass
class AgentNode:
    """A node in the state graph representing an executable agent step."""
    node_id: str
    node_type: NodeType
    name: str
    description: str = ""
    handler: Any = None
    next_nodes: list = None
    parallel_forks: list = None
    condition: str = ""
    max_loops: int = 1
    loop_counter: int = 0
    config: dict = None

    def __post_init__(self):
        if self.next_nodes is None:
            self.next_nodes = []
        if self.parallel_forks is None:
            self.parallel_forks = []
        if self.config is None:
            self.config = {}


@dataclass
class StateGraph:
    """State graph: nodes + transitions + fork/join semantics."""
    graph_id: str
    name: str
    nodes: dict = None
    start_node_id: str = ""
    end_node_ids: list = None
    transitions: list = None

    def __post_init__(self):
        if self.nodes is None:
            self.nodes = {}
        if self.end_node_ids is None:
            self.end_node_ids = []
        if self.transitions is None:
            self.transitions = []

    def add_node(self, node):
        self.nodes[node.node_id] = node
        return self

    def add_transition(self, from_id, to_id, condition="", mode=ExecMode.SEQUENTIAL):
        self.transitions.append({
            "from": from_id, "to": to_id,
            "condition": condition, "mode": mode.value
        })
        return self

    def set_entry(self, node_id):
        self.start_node_id = node_id
        return self

    def set_exit(self, node_ids):
        self.end_node_ids = node_ids
        return self

    def get_next_nodes(self, current_node_id, context):
        candidates = []
        for t in self.transitions:
            if t["from"] == current_node_id:
                if t["condition"]:
                    try:
                        if not eval(t["condition"], {"__builtins__": {}, "context": context}, context):
                            continue
                    except Exception:
                        continue
                candidates.append(t["to"])
        if not candidates and current_node_id in self.nodes:
            node = self.nodes[current_node_id]
            candidates = list(node.next_nodes)
        return candidates

    def to_dict(self):
        return {
            "graph_id": self.graph_id,
            "name": self.name,
            "start_node_id": self.start_node_id,
            "end_node_ids": self.end_node_ids,
            "nodes": {
                nid: {
                    "node_id": n.node_id,
                    "node_type": n.node_type.value,
                    "name": n.name,
                    "description": n.description,
                    "next_nodes": n.next_nodes,
                    "parallel_forks": n.parallel_forks,
                    "condition": n.condition,
                    "max_loops": n.max_loops,
                }
                for nid, n in self.nodes.items()
            },
            "transitions": self.transitions,
        }


@dataclass
class RunState:
    """Full state of a single orchestration run."""
    run_id: str
    graph_id: str
    status: RunStatus = RunStatus.PENDING
    current_node_id: str = ""
    context: dict = None
    node_results: dict = None
    history: list = None
    error_message: str = ""
    started_at: str = ""
    updated_at: str = ""
    completed_at: str = ""

    def __post_init__(self):
        if self.context is None:
            self.context = {}
        if self.node_results is None:
            self.node_results = {}
        if self.history is None:
            self.history = []


SCHEMA_AGENT_RUNS = """
CREATE TABLE IF NOT EXISTS agent_state_runs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    run_id TEXT NOT NULL UNIQUE,
    graph_id TEXT NOT NULL,
    graph_name TEXT NOT NULL DEFAULT '',
    goal TEXT NOT NULL DEFAULT '',
    status TEXT NOT NULL DEFAULT 'pending',
    current_node_id TEXT NOT NULL DEFAULT '',
    context_json TEXT NOT NULL DEFAULT '{}',
    node_results_json TEXT NOT NULL DEFAULT '{}',
    history_json TEXT NOT NULL DEFAULT '[]',
    error_message TEXT NOT NULL DEFAULT '',
    started_at TEXT NOT NULL DEFAULT '',
    updated_at TEXT NOT NULL DEFAULT '',
    completed_at TEXT NOT NULL DEFAULT ''
);

CREATE TABLE IF NOT EXISTS agent_state_events (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    run_id TEXT NOT NULL,
    event_type TEXT NOT NULL,
    node_id TEXT NOT NULL DEFAULT '',
    payload_json TEXT NOT NULL DEFAULT '{}',
    created_at TEXT NOT NULL,
    FOREIGN KEY (run_id) REFERENCES agent_state_runs(run_id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_agent_state_runs_status ON agent_state_runs(status);
CREATE INDEX IF NOT EXISTS idx_agent_state_events_run ON agent_state_events(run_id);
"""


class AgentOrchestrator:
    """Agent state machine orchestration engine - LangGraph style.

    Accepts tasks -> decomposes -> assigns agents -> executes -> aggregates.
    Supports: sequential, parallel fork/join, conditional branch, loops (max N).
    State persisted to SQLite.
    """

    def __init__(self, store):
        self._store = store
        self._graphs = {}
        self._active_runs = {}
        self._lock = threading.Lock()
        self._ensure_tables()
        self._ensure_default_roles()
        self._register_default_graphs()

    # -- DB init --

    def _ensure_tables(self):
        cur = self._store.conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='agent_state_runs'"
        )
        if not cur.fetchone():
            self._store.conn.executescript(SCHEMA_AGENT_RUNS)
            self._store.conn.commit()

    def _ensure_default_roles(self):
        existing = {r["name"] for r in self.list_roles()}
        ts = datetime.now(timezone.utc).isoformat()
        for name, caps in DEFAULT_ROLES.items():
            if name not in existing:
                self._store.conn.execute(
                    "INSERT INTO agent_roles (name, role_type, description, capabilities, priority, created_at) "
                    "VALUES (?, ?, ?, ?, ?, ?)",
                    (name, "worker", f"{name.capitalize()} agent",
                     json.dumps(caps), list(DEFAULT_ROLES.keys()).index(name) + 1, ts))
        self._store.conn.commit()

    # -- Default state graphs --

    def _register_default_graphs(self):
        # Default sequential: think -> research -> observe -> code -> review -> decide -> done
        g = self.create_graph("default-research-code-review", "Research -> Code -> Review")
        g.add_node(AgentNode("think", NodeType.THINK, "Think", "Analyze task"))
        g.add_node(AgentNode("research", NodeType.ACT, "Research", "Gather context"))
        g.add_node(AgentNode("observe", NodeType.OBSERVE, "Observe", "Check results"))
        g.add_node(AgentNode("code", NodeType.ACT, "Code", "Implement solution"))
        g.add_node(AgentNode("review", NodeType.EVALUATE, "Review", "Quality check"))
        g.add_node(AgentNode("decide", NodeType.DECIDE, "Decide", "Accept or loop"))
        g.add_node(AgentNode("done", NodeType.DECIDE, "Done", "Complete"))
        g.set_entry("think")
        g.add_transition("think", "research")
        g.add_transition("research", "observe")
        g.add_transition("observe", "code")
        g.add_transition("code", "review")
        g.add_transition("review", "decide")
        g.add_transition("decide", "done", condition="approved")
        g.add_transition("decide", "code", condition="not approved")
        g.set_exit(["done"])

        # Parallel fork/join graph
        g2 = self.create_graph("parallel-research-code", "Parallel Research + Code")
        g2.add_node(AgentNode("plan", NodeType.THINK, "Plan", "Decompose into subtasks"))
        g2.add_node(AgentNode("fork", NodeType.DECIDE, "Fork", "Split to parallel",
                              parallel_forks=["research_a", "code_a"]))
        g2.add_node(AgentNode("research_a", NodeType.ACT, "Research-A", "Research subtask A"))
        g2.add_node(AgentNode("code_a", NodeType.ACT, "Code-A", "Code subtask A"))
        g2.add_node(AgentNode("join", NodeType.OBSERVE, "Join", "Merge results"))
        g2.add_node(AgentNode("evaluate", NodeType.EVALUATE, "Evaluate", "Check merged output"))
        g2.add_node(AgentNode("done", NodeType.DECIDE, "Done", "Complete"))
        g2.set_entry("plan")
        g2.add_transition("plan", "fork")
        g2.add_transition("fork", "research_a", mode=ExecMode.PARALLEL)
        g2.add_transition("fork", "code_a", mode=ExecMode.PARALLEL)
        g2.add_transition("research_a", "join")
        g2.add_transition("code_a", "join")
        g2.add_transition("join", "evaluate")
        g2.add_transition("evaluate", "done")
        g2.set_exit(["done"])

    # -- Graph management --

    def create_graph(self, graph_id, name):
        g = StateGraph(graph_id=graph_id, name=name)
        self._graphs[graph_id] = g
        return g

    def get_graph(self, graph_id):
        return self._graphs.get(graph_id)

    def list_graphs(self):
        return [g.to_dict() for g in self._graphs.values()]

    # -- Agent roles --

    def list_roles(self):
        cur = self._store.conn.execute("SELECT * FROM agent_roles ORDER BY priority")
        return [dict(r) for r in cur.fetchall()]

    def assign_for_task(self, goal):
        roles = self.list_roles()
        if not roles:
            return []
        result = []
        for r in roles:
            caps = json.loads(r.get("capabilities", "[]"))
            result.append({"role": r["name"], "capabilities": caps})
        return result

    # -- Run management --

    def start_run(self, graph_id, goal="", initial_context=None):
        graph = self._graphs.get(graph_id)
        if not graph:
            raise ValueError(f"Unknown graph: {graph_id}")

        run_id = str(uuid.uuid4())[:12]
        now = datetime.now(timezone.utc).isoformat()

        state = RunState(
            run_id=run_id,
            graph_id=graph_id,
            status=RunStatus.PENDING,
            current_node_id=graph.start_node_id,
            context=initial_context or {"goal": goal},
            started_at=now,
            updated_at=now,
        )

        self._active_runs[run_id] = state
        self._persist_run(state)
        self._log_event(run_id, "run_started", "", {"goal": goal})
        return state

    def advance_run(self, run_id):
        state = self._get_run(run_id)
        if state.status in (RunStatus.DONE, RunStatus.FAILED, RunStatus.CANCELLED):
            return state

        graph = self._graphs.get(state.graph_id)
        if not graph:
            state.status = RunStatus.FAILED
            state.error_message = f"Graph {state.graph_id} not found"
            self._persist_run(state)
            return state

        current_id = state.current_node_id
        current_node = graph.nodes.get(current_id)

        # Execute current node
        if current_node:
            node_result = self._execute_node(current_node, state)
            state.node_results[current_id] = node_result
            state.history.append({
                "node_id": current_id,
                "node_type": current_node.node_type.value,
                "result": node_result,
                "timestamp": datetime.now(timezone.utc).isoformat(),
            })

        # Determine next node(s)
        next_nodes = graph.get_next_nodes(current_id, state.context)

        if not next_nodes and current_id in graph.end_node_ids:
            state.status = RunStatus.DONE
            state.completed_at = datetime.now(timezone.utc).isoformat()
        elif not next_nodes:
            state.status = RunStatus.DONE
            state.completed_at = datetime.now(timezone.utc).isoformat()
        else:
            # Parallel fork handling
            if current_node and current_node.parallel_forks:
                for fork_id in current_node.parallel_forks:
                    fork_node = graph.nodes.get(fork_id)
                    if fork_node:
                        fork_result = self._execute_node(fork_node, state)
                        state.node_results[fork_id] = fork_result
                        state.history.append({
                            "node_id": fork_id,
                            "node_type": fork_node.node_type.value,
                            "result": fork_result,
                            "timestamp": datetime.now(timezone.utc).isoformat(),
                        })
                state.current_node_id = next_nodes[0] if next_nodes else current_id
            else:
                state.current_node_id = next_nodes[0]

            # Loop counter
            if current_node and current_node.max_loops > 1:
                current_node.loop_counter += 1
                if current_node.loop_counter >= current_node.max_loops:
                    non_loop = [n for n in next_nodes
                               if graph.nodes.get(n) and graph.nodes[n].max_loops <= 1]
                    if non_loop:
                        state.current_node_id = non_loop[0]

            self._map_status_from_node(state, state.current_node_id, graph)

        state.updated_at = datetime.now(timezone.utc).isoformat()
        self._persist_run(state)
        return state

    def run_to_completion(self, run_id, max_steps=50):
        for _ in range(max_steps):
            state = self.advance_run(run_id)
            if state.status in (RunStatus.DONE, RunStatus.FAILED, RunStatus.CANCELLED):
                return state
        state = self._get_run(run_id)
        state.status = RunStatus.FAILED
        state.error_message = f"Exceeded max steps ({max_steps})"
        self._persist_run(state)
        return state

    def cancel_run(self, run_id):
        state = self._get_run(run_id)
        if state.status not in (RunStatus.DONE, RunStatus.FAILED, RunStatus.CANCELLED):
            state.status = RunStatus.CANCELLED
            state.completed_at = datetime.now(timezone.utc).isoformat()
            state.updated_at = state.completed_at
            self._persist_run(state)
            self._log_event(run_id, "run_cancelled")
        return state

    def get_run_status(self, run_id):
        state = self._get_run(run_id)
        return self._state_to_dict(state)

    def list_runs(self, limit=50):
        cur = self._store.conn.execute(
            "SELECT * FROM agent_state_runs ORDER BY updated_at DESC LIMIT ?", (limit,)
        )
        return [dict(r) for r in cur.fetchall()]

    def get_run_events(self, run_id, limit=100):
        cur = self._store.conn.execute(
            "SELECT * FROM agent_state_events WHERE run_id = ? ORDER BY created_at ASC LIMIT ?",
            (run_id, limit),
        )
        return [dict(r) for r in cur.fetchall()]

    # -- Internal helpers --

    def _get_run(self, run_id):
        if run_id in self._active_runs:
            return self._active_runs[run_id]
        cur = self._store.conn.execute(
            "SELECT * FROM agent_state_runs WHERE run_id = ?", (run_id,)
        )
        row = cur.fetchone()
        if not row:
            raise ValueError(f"Run not found: {run_id}")
        state = self._row_to_state(row)
        self._active_runs[run_id] = state
        return state

    def _execute_node(self, node, state):
        ts = time.time()
        result = {"node_id": node.node_id, "node_type": node.node_type.value}

        if node.handler:
            try:
                output = node.handler(state.context, state.node_results)
                result["output"] = output
                result["success"] = True
                if isinstance(output, dict):
                    state.context.update(output)
            except Exception as exc:
                result["success"] = False
                result["error"] = str(exc)
        else:
            default_output = self._default_node_execute(node, state)
            result["output"] = default_output
            result["success"] = True
            if isinstance(default_output, dict):
                state.context.update(default_output)

        result["duration_ms"] = int((time.time() - ts) * 1000)
        return result

    def _default_node_execute(self, node, state):
        if node.node_type == NodeType.THINK:
            return {"thought": f"Analyzing task: {state.context.get('goal', 'N/A')}"}
        elif node.node_type == NodeType.ACT:
            return {"action": f"Executing: {node.name}", "node": node.node_id}
        elif node.node_type == NodeType.OBSERVE:
            prev = state.history[-1] if state.history else {}
            return {"observation": f"Observed result from {prev.get('node_id', 'N/A')}"}
        elif node.node_type == NodeType.EVALUATE:
            return {"evaluation": "pass", "score": 0.85, "approved": True}
        elif node.node_type == NodeType.DECIDE:
            return {"decision": "proceed", "next_action": "continue"}
        return {"result": "ok"}

    def _map_status_from_node(self, state, node_id, graph):
        node = graph.nodes.get(node_id)
        if not node:
            return
        status_map = {
            NodeType.THINK: RunStatus.THINKING,
            NodeType.ACT: RunStatus.ACTING,
            NodeType.OBSERVE: RunStatus.OBSERVING,
            NodeType.EVALUATE: RunStatus.EVALUATING,
            NodeType.DECIDE: RunStatus.DECIDING,
        }
        state.status = status_map.get(node.node_type, RunStatus.PENDING)

    def _persist_run(self, state):
        cur = self._store.conn.execute(
            "SELECT id FROM agent_state_runs WHERE run_id = ?", (state.run_id,)
        )
        if cur.fetchone():
            self._store.conn.execute(
                "UPDATE agent_state_runs SET status=?, current_node_id=?, context_json=?, "
                "node_results_json=?, history_json=?, error_message=?, updated_at=?, "
                "completed_at=? WHERE run_id=?",
                (state.status.value, state.current_node_id,
                 json.dumps(state.context, default=str),
                 json.dumps(state.node_results, default=str),
                 json.dumps(state.history, default=str),
                 state.error_message, state.updated_at,
                 state.completed_at, state.run_id))
        else:
            graph = self._graphs.get(state.graph_id)
            graph_name = graph.name if graph else ""
            self._store.conn.execute(
                "INSERT INTO agent_state_runs (run_id, graph_id, graph_name, goal, status, "
                "current_node_id, context_json, node_results_json, history_json, "
                "error_message, started_at, updated_at, completed_at) "
                "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                (state.run_id, state.graph_id, graph_name,
                 state.context.get("goal", ""), state.status.value,
                 state.current_node_id,
                 json.dumps(state.context, default=str),
                 json.dumps(state.node_results, default=str),
                 json.dumps(state.history, default=str),
                 state.error_message, state.started_at,
                 state.updated_at, state.completed_at))
        self._store.conn.commit()

    def _log_event(self, run_id, event_type, node_id="", payload=None):
        ts = datetime.now(timezone.utc).isoformat()
        self._store.conn.execute(
            "INSERT INTO agent_state_events (run_id, event_type, node_id, payload_json, created_at) "
            "VALUES (?, ?, ?, ?, ?)",
            (run_id, event_type, node_id, json.dumps(payload or {}), ts))
        self._store.conn.commit()

    def _state_to_dict(self, state):
        return {
            "run_id": state.run_id,
            "graph_id": state.graph_id,
            "status": state.status.value,
            "current_node_id": state.current_node_id,
            "context": state.context,
            "node_results": state.node_results,
            "history": state.history,
            "error_message": state.error_message,
            "started_at": state.started_at,
            "updated_at": state.updated_at,
            "completed_at": state.completed_at,
        }

    def _row_to_state(self, row):
        d = dict(row)
        return RunState(
            run_id=d["run_id"],
            graph_id=d["graph_id"],
            status=RunStatus(d["status"]),
            current_node_id=d.get("current_node_id", ""),
            context=json.loads(d.get("context_json", "{}")),
            node_results=json.loads(d.get("node_results_json", "{}")),
            history=json.loads(d.get("history_json", "[]")),
            error_message=d.get("error_message", ""),
            started_at=d.get("started_at", ""),
            updated_at=d.get("updated_at", ""),
            completed_at=d.get("completed_at", ""),
        )
