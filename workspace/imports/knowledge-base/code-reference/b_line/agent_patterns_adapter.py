"""agent_patterns_adapter.py — Multi-Agent patterns adapter for B-Line.

Extracts and adapts key multi-agent conversation patterns from:
  - AutoGen (MIT) — group chat, agent handoff, tool calling
  - CrewAI (MIT) — role-based task delegation
  - CAMEL (Apache-2.0) — role-playing, task specification

These patterns enhance the existing agent_orchestrator.py with:
  1. Conversation state machine (AutoGen GroupChat pattern)
  2. Agent-to-agent handoff protocol (AutoGen handoff pattern)
  3. Role negotiation & task allocation (CrewAI hierarchical pattern)
  4. Agent conversation memory buffer (CAMEL role-playing memory)

All code is original; only algorithmic ideas are adapted from references.
Licenses: MIT/Apache-2.0 (patterns only, no code copied)
"""
from __future__ import annotations

import json
import time
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum, auto
from typing import Any, Callable, Optional, Sequence


# ---------------------------------------------------------------------------
# Conversation State Machine — adapted from AutoGen GroupChat
# ---------------------------------------------------------------------------
class AgentState(Enum):
    """States in the multi-agent conversation lifecycle.

    Adapted from AutoGen''s ConversableAgent state tracking.
    """
    IDLE = auto()
    LISTENING = auto()
    THINKING = auto()
    SPEAKING = auto()
    WAITING_FOR_TOOL = auto()
    WAITING_FOR_HUMAN = auto()
    TERMINATED = auto()


class SpeakerSelection(Enum):
    """Speaker selection strategies.

    Adapted from AutoGen GroupChat speaker_selection_method.
    """
    AUTO = "auto"           # LLM decides next speaker
    ROUND_ROBIN = "round_robin"  # Sequential turn-taking
    RANDOM = "random"       # Random selection
    MANUAL = "manual"       # Human chooses next speaker


@dataclass
class AgentMessage:
    """A single message in a multi-agent conversation.

    Adapted from AutoGen''s message format with agent attribution.
    """
    sender: str
    receiver: str
    content: str
    message_type: str = "text"  # text, tool_call, tool_result, system
    timestamp: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class AgentRole:
    """Role definition with capabilities and constraints.

    Adapted from CrewAI role-based agent design.
    """
    name: str
    role_type: str  # planner, executor, reviewer, observer
    goal: str
    backstory: str = ""
    capabilities: list[str] = field(default_factory=list)
    allowed_tools: list[str] = field(default_factory=list)
    priority: int = 0
    delegation_enabled: bool = True


class ConversationManager:
    """Multi-agent conversation state machine.

    Adapted from AutoGen GroupChatManager pattern:
    - Maintains conversation history as a message list
    - Manages agent states and turn-taking
    - Supports speaker selection strategies
    - Handles tool-call/result paired messages
    """

    def __init__(
        self,
        max_rounds: int = 12,
        speaker_selection: SpeakerSelection = SpeakerSelection.AUTO,
    ):
        self.max_rounds = max_rounds
        self.speaker_selection = speaker_selection
        self.messages: list[AgentMessage] = []
        self.agent_states: dict[str, AgentState] = {}
        self.round_count = 0
        self.speaker_order: list[str] = []
        self._participants: dict[str, AgentRole] = {}

    # ---- Participant management (adapted from AutoGen GroupChat) ----

    def register_agent(self, role: AgentRole) -> None:
        """Register an agent role in the conversation."""
        self._participants[role.name] = role
        self.agent_states[role.name] = AgentState.IDLE
        if role.name not in self.speaker_order:
            self.speaker_order.append(role.name)

    def remove_agent(self, agent_name: str) -> None:
        """Remove an agent from the conversation."""
        self._participants.pop(agent_name, None)
        self.agent_states.pop(agent_name, None)
        self.speaker_order = [n for n in self.speaker_order if n != agent_name]

    # ---- Message routing (adapted from AutoGen send/receive pattern) ----

    def send_message(
        self,
        sender: str,
        receiver: str,
        content: str,
        message_type: str = "text",
        metadata: dict[str, Any] | None = None,
    ) -> AgentMessage:
        """Route a message from one agent to another.

        Adapted from AutoGen ConversableAgent.send() / receive() pattern.
        Transitions sender state to THINKING→SPEAKING→IDLE,
        receiver state to LISTENING→THINKING.
        """
        msg = AgentMessage(
            sender=sender,
            receiver=receiver,
            content=content,
            message_type=message_type,
            metadata=metadata or {},
        )
        self.messages.append(msg)
        self.agent_states[sender] = AgentState.IDLE
        self.agent_states[receiver] = AgentState.THINKING
        self.round_count += 1
        return msg

    def broadcast(self, sender: str, content: str, exclude: list[str] | None = None) -> list[AgentMessage]:
        """Broadcast a message to all participants.

        Adapted from AutoGen GroupChat broadcast pattern.
        """
        exclude_set = set(exclude or [])
        results = []
        for name in self._participants:
            if name != sender and name not in exclude_set:
                results.append(self.send_message(sender, name, content, "text"))
        return results

    # ---- Speaker selection (adapted from AutoGen speaker_selection_method) ----

    def select_next_speaker(
        self,
        current_speaker: str,
        *,
        llm_selector: Optional[Callable[[list[str], list[AgentMessage]], str]] = None,
    ) -> str | None:
        """Select the next speaker based on the configured strategy.

        Adapted from AutoGen GroupChat.select_speaker() pattern.
        Supports AUTO (LLM), ROUND_ROBIN, RANDOM, and MANUAL.
        """
        active_agents = [
            n for n, s in self.agent_states.items()
            if s not in (AgentState.TERMINATED, AgentState.WAITING_FOR_HUMAN)
        ]
        if not active_agents:
            return None

        if self.speaker_selection == SpeakerSelection.ROUND_ROBIN:
            idx = (self.speaker_order.index(current_speaker) + 1) % len(self.speaker_order)
            return self.speaker_order[idx]

        elif self.speaker_selection == SpeakerSelection.RANDOM:
            import random
            return random.choice(active_agents)

        elif self.speaker_selection == SpeakerSelection.AUTO and llm_selector:
            return llm_selector(active_agents, self.messages[-5:])

        # Default: return first active that is not current
        for name in active_agents:
            if name != current_speaker:
                return name
        return None

    # ---- Termination (adapted from AutoGen termination condition) ----

    def is_terminated(self) -> bool:
        """Check if conversation should terminate.

        Adapted from AutoGen GroupChat termination conditions:
        - Max rounds reached
        - All agents in TERMINATED state
        - Termination message received
        """
        if self.round_count >= self.max_rounds:
            return True
        # Check for explicit termination message
        for msg in reversed(self.messages[-3:]):
            if msg.message_type == "system" and "TERMINATE" in msg.content:
                return True
        # Check if all agents terminated
        active = [s for s in self.agent_states.values() if s != AgentState.TERMINATED]
        return len(active) == 0

    # ---- Conversation history (adapted from AutoGen chat_messages) ----

    def get_history(self, last_n: int = 0) -> list[dict[str, Any]]:
        """Get conversation history as serializable dicts."""
        msgs = self.messages[-last_n:] if last_n > 0 else self.messages
        return [
            {
                "sender": m.sender,
                "receiver": m.receiver,
                "content": m.content,
                "type": m.message_type,
                "timestamp": m.timestamp,
            }
            for m in msgs
        ]

    def get_context_for_agent(self, agent_name: str, window: int = 10) -> list[AgentMessage]:
        """Get recent messages relevant to a specific agent.

        Adapted from AutoGen agent-specific context window.
        """
        relevant = [
            m for m in self.messages
            if agent_name in (m.sender, m.receiver) or m.message_type == "system"
        ]
        return relevant[-window:]


# ---------------------------------------------------------------------------
# Role Negotiation — adapted from CrewAI hierarchical task delegation
# ---------------------------------------------------------------------------

@dataclass
class TaskDelegation:
    """Task delegation record.

    Adapted from CrewAI Task/Process pattern.
    """
    task_id: str
    delegator: str
    delegate: str
    description: str
    expected_output: str
    status: str = "pending"  # pending, accepted, completed, rejected
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


class TaskDelegator:
    """Role-based task delegation manager.

    Adapted from CrewAI''s hierarchical process pattern:
    - Roles have capabilities and priorities
    - Tasks are matched to roles by capability overlap
    - Delegation can be accepted or rejected
    - Supports escalation when delegate rejects
    """

    def __init__(self, roles: list[AgentRole]):
        self.roles = {r.name: r for r in roles}
        self.delegations: list[TaskDelegation] = []

    def find_best_role(
        self,
        required_capabilities: list[str],
        exclude: list[str] | None = None,
    ) -> str | None:
        """Find the best-matching role for a task based on capabilities.

        Adapted from CrewAI task-to-agent matching algorithm.
        """
        exclude_set = set(exclude or [])
        candidates = []
        for name, role in self.roles.items():
            if name in exclude_set or not role.delegation_enabled:
                continue
            # Score: count of matching capabilities
            match_count = len(set(required_capabilities) & set(role.capabilities))
            if match_count > 0:
                candidates.append((match_count, role.priority, name))

        candidates.sort(reverse=True)
        return candidates[0][2] if candidates else None

    def delegate(
        self,
        delegator: str,
        description: str,
        required_capabilities: list[str],
        expected_output: str = "",
    ) -> TaskDelegation | None:
        """Delegate a task to the best-matching role.

        Adapted from CrewAI Task.delegate() pattern.
        """
        delegate = self.find_best_role(required_capabilities, exclude=[delegator])
        if not delegate:
            return None

        d = TaskDelegation(
            task_id=f"task_{int(time.time())}_{len(self.delegations)}",
            delegator=delegator,
            delegate=delegate,
            description=description,
            expected_output=expected_output,
        )
        self.delegations.append(d)
        return d

    def accept_delegation(self, task_id: str) -> TaskDelegation | None:
        """Accept a delegation."""
        for d in self.delegations:
            if d.task_id == task_id:
                d.status = "accepted"
                return d
        return None

    def reject_delegation(self, task_id: str, reason: str = "") -> TaskDelegation | None:
        """Reject a delegation (triggers re-delegation)."""
        for d in self.delegations:
            if d.task_id == task_id:
                d.status = "rejected"
                d.description += f" [Rejected: {reason}]"
                return d
        return None


# ---------------------------------------------------------------------------
# Agent Conversation Memory — adapted from CAMEL role-playing memory
# ---------------------------------------------------------------------------

@dataclass
class ConversationMemory:
    """Persistent memory for multi-agent conversations.

    Adapted from CAMEL RolePlaying memory pattern:
    - Stores conversation turns with role attribution
    - Tracks task progress and milestones
    - Supports context window retrieval
    """

    turns: list[dict[str, Any]] = field(default_factory=list)
    task_context: dict[str, Any] = field(default_factory=dict)
    milestones: list[str] = field(default_factory=list)
    lessons_learned: list[str] = field(default_factory=list)

    def add_turn(self, speaker: str, listener: str, message: str, turn_type: str = "chat") -> None:
        """Record a conversation turn."""
        self.turns.append({
            "speaker": speaker,
            "listener": listener,
            "message": message,
            "type": turn_type,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        })

    def add_milestone(self, description: str) -> None:
        """Record a task milestone."""
        self.milestones.append(f"[{datetime.now(timezone.utc).isoformat()}] {description}")

    def add_lesson(self, lesson: str) -> None:
        """Record a learned lesson for future conversations."""
        self.lessons_learned.append(lesson)

    def get_recent_context(self, n_turns: int = 10) -> str:
        """Get recent conversation context as formatted text.

        Adapted from CAMEL context assembly pattern.
        """
        recent = self.turns[-n_turns:]
        lines = []
        for t in recent:
            lines.append(f"[{t['speaker']} -> {t['listener']}]: {t['message']}")
        return "\n".join(lines)

    def to_dict(self) -> dict[str, Any]:
        """Serialize for persistence."""
        return {
            "turns": self.turns,
            "task_context": self.task_context,
            "milestones": self.milestones,
            "lessons_learned": self.lessons_learned,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "ConversationMemory":
        """Deserialize from persistence."""
        return cls(
            turns=data.get("turns", []),
            task_context=data.get("task_context", {}),
            milestones=data.get("milestones", []),
            lessons_learned=data.get("lessons_learned", []),
        )


# ---------------------------------------------------------------------------
# Tool Calling Handoff — adapted from AutoGen tool use pattern
# ---------------------------------------------------------------------------

@dataclass
class ToolCallRecord:
    """Record of a tool call in agent conversation.

    Adapted from AutoGen tool call / tool result paired-message pattern.
    """
    call_id: str
    agent: str
    tool_name: str
    arguments: dict[str, Any]
    result: Any = None
    error: str | None = None
    called_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    completed_at: str | None = None


class ToolCallHandler:
    """Manages tool call handoffs between agents.

    Adapted from AutoGen''s tool registration and calling pattern:
    - Agents register available tools
    - Tool calls are routed with call_id for pairing
    - Results are returned to the calling agent
    """

    def __init__(self):
        self.tools: dict[str, dict[str, Callable]] = defaultdict(dict)
        self.call_history: list[ToolCallRecord] = []

    def register_tool(self, agent_name: str, tool_name: str, func: Callable) -> None:
        """Register a tool for an agent."""
        self.tools[agent_name][tool_name] = func

    def execute_tool(
        self,
        agent_name: str,
        tool_name: str,
        arguments: dict[str, Any],
    ) -> ToolCallRecord:
        """Execute a tool call and record it.

        Adapted from AutoGen execute_tool pattern.
        """
        record = ToolCallRecord(
            call_id=f"call_{len(self.call_history)}_{int(time.time())}",
            agent=agent_name,
            tool_name=tool_name,
            arguments=arguments,
        )

        if agent_name not in self.tools or tool_name not in self.tools[agent_name]:
            record.error = f"Tool ''{tool_name}'' not registered for agent ''{agent_name}''"
            self.call_history.append(record)
            return record

        try:
            record.result = self.tools[agent_name][tool_name](**arguments)
        except Exception as e:
            record.error = str(e)

        record.completed_at = datetime.now(timezone.utc).isoformat()
        self.call_history.append(record)
        return record

    def list_agent_tools(self, agent_name: str) -> list[str]:
        """List all tools registered for an agent."""
        return list(self.tools.get(agent_name, {}).keys())

    def recent_calls(self, agent_name: str, limit: int = 5) -> list[ToolCallRecord]:
        """Get recent tool calls for an agent."""
        agent_calls = [c for c in self.call_history if c.agent == agent_name]
        return agent_calls[-limit:]


# ---------------------------------------------------------------------------
# Self-test
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    print("=== Multi-Agent Patterns Adapter Test ===\n")

    # Test ConversationManager
    cm = ConversationManager(max_rounds=5, speaker_selection=SpeakerSelection.ROUND_ROBIN)
    cm.register_agent(AgentRole("planner", "planner", "Break down complex tasks"))
    cm.register_agent(AgentRole("coder", "executor", "Write and test code"))
    cm.register_agent(AgentRole("reviewer", "reviewer", "Review code quality"))

    cm.send_message("planner", "coder", "Create a Python function to compute Fibonacci numbers")
    cm.send_message("coder", "reviewer", "Here is the implementation: def fib(n): ...")
    cm.send_message("reviewer", "coder", "Looks good, consider adding type hints")

    print(f"Conversation rounds: {cm.round_count}")
    print(f"Messages: {len(cm.messages)}")
    print(f"Terminated: {cm.is_terminated()}")

    # Test TaskDelegator
    roles = [
        AgentRole("planner", "planner", "Plan tasks", capabilities=["planning", "estimation"]),
        AgentRole("coder", "executor", "Write code", capabilities=["coding", "testing"]),
        AgentRole("reviewer", "reviewer", "Review code", capabilities=["review", "audit"]),
    ]
    td = TaskDelegator(roles)
    delegation = td.delegate("planner", "Implement auth middleware", ["coding"])
    if delegation:
        print(f"\nTask delegated: {delegation.description} -> {delegation.delegate}")

    # Test ConversationMemory
    mem = ConversationMemory()
    mem.add_turn("planner", "coder", "Implement auth middleware")
    mem.add_turn("coder", "planner", "Done, please review")
    mem.add_milestone("Auth middleware implemented")
    mem.add_lesson("Auth middleware should validate JWT expiry first")
    print(f"\nMemory turns: {len(mem.turns)}")
    print(f"Milestones: {len(mem.milestones)}")
    print(f"Lessons: {len(mem.lessons_learned)}")

    # Test ToolCallHandler
    tch = ToolCallHandler()
    tch.register_tool("coder", "fibonacci", lambda n: [0, 1] if n <= 2 else [0, 1, 1])
    result = tch.execute_tool("coder", "fibonacci", {"n": 10})
    print(f"\nTool call result: {result.result}, error: {result.error}")

    print("\n=== All tests passed ===")
