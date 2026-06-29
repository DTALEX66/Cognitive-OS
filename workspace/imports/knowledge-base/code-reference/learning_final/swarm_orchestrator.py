"""Swarm Orchestrator ? Multi-agent team coordination

Sources:
  - inProcessRunner.ts (53KB): In-process agent runner with permission bridges
  - spawnInProcess.ts (10KB): Subprocess agent spawning with IPC
  - permissionSync.ts (26KB): Cross-agent permission synchronization
  - teamHelpers.ts (21KB): Team management, layout, prompts
"""
from __future__ import annotations
from datetime import datetime, timezone
from typing import Any, Optional
from enum import Enum
import json


class SwarmMode(str, Enum):
    SEQUENTIAL = "sequential"     # Agents run one after another
    PARALLEL = "parallel"         # Agents run simultaneously
    CONSENSUS = "consensus"       # Multiple agents vote on result
    DEBATE = "debate"             # Agents debate and refine


class SwarmRole(str, Enum):
    LEADER = "leader"           # Coordinates the swarm
    WORKER = "worker"           # Executes tasks
    REVIEWER = "reviewer"       # Reviews outputs
    MERGER = "merger"           # Merges results


class SwarmOrchestrator:
    """Swarm patterns ? multi-agent team coordination"""
    
    def __init__(self, store=None):
        self._store = store
        self._teams: dict[str, dict] = {}
        self._sessions: dict[str, dict] = {}
        
    def create_team(self, name: str, mode: SwarmMode = SwarmMode.SEQUENTIAL) -> str:
        team_id = f"swarm_{int(datetime.now(timezone.utc).timestamp())}"
        self._teams[team_id] = {
            "id": team_id,
            "name": name,
            "mode": mode.value,
            "agents": [],
            "created_at": datetime.now(timezone.utc).isoformat(),
        }
        return team_id
    
    def add_agent(self, team_id: str, role: SwarmRole, config: dict) -> Optional[str]:
        team = self._teams.get(team_id)
        if not team:
            return None
        agent_id = f"agent_{len(team['agents'])}_{int(datetime.now(timezone.utc).timestamp())}"
        team["agents"].append({"id": agent_id, "role": role.value, "config": config})
        return agent_id
    
    def run_team(self, team_id: str, objective: str) -> Optional[dict]:
        """ ? run team with mode-specific execution"""
        team = self._teams.get(team_id)
        if not team:
            return None
        
        session_id = f"session_{int(datetime.now(timezone.utc).timestamp())}"
        agents = team["agents"]
        mode = team["mode"]
        
        results = []
        
        if mode == SwarmMode.SEQUENTIAL.value:
            # Agents run one by one, passing context
            context = {"objective": objective}
            for agent in agents:
                result = self._run_agent(agent, context)
                results.append(result)
                context["previous_result"] = result
        
        elif mode == SwarmMode.PARALLEL.value:
            # All agents run independently
            for agent in agents:
                result = self._run_agent(agent, {"objective": objective})
                results.append(result)
        
        elif mode == SwarmMode.CONSENSUS.value:
            # Multiple agents vote, pick best
            votes = []
            for agent in agents:
                result = self._run_agent(agent, {"objective": objective})
                votes.append(result)
            # Simple consensus: pick with most common key points
            from collections import Counter
            all_points = []
            for v in votes:
                all_points.extend(v.get("findings", []))
            top = Counter([str(p) for p in all_points]).most_common(3)
            results = [{"method": "consensus", "top_points": [p for p, c in top], "total_votes": len(votes)}]
        
        elif mode == SwarmMode.DEBATE.value:
            # Agents debate, refine
            context = {"objective": objective}
            for i in range(2):  # 2 rounds of debate
                for agent in agents:
                    result = self._run_agent(agent, context)
                    context["debate_round"] = i + 1
                    context["previous_arguments"] = result.get("summary", "")
                results.extend([{"round": i+1, "agent": a["id"], "result": r} for a, r in zip(agents, [self._run_agent(a, context) for a in agents])])
        
        session = {
            "id": session_id,
            "team_id": team_id,
            "mode": mode,
            "objective": objective,
            "results": results,
            "agent_count": len(agents),
            "completed_at": datetime.now(timezone.utc).isoformat(),
        }
        self._sessions[session_id] = session
        
        return {"session_id": session_id, "mode": mode, "results": results}
    
    def _run_agent(self, agent: dict, context: dict) -> dict:
        return {
            "agent_id": agent["id"],
            "role": agent["role"],
            "summary": f"Agent {agent['role']} processed: {str(context)[:100]}",
            "findings": [],
        }
    
    def get_session(self, session_id: str) -> Optional[dict]:
        return self._sessions.get(session_id)
    
    def get_team(self, team_id: str) -> Optional[dict]:
        return self._teams.get(team_id)
    
    def list_sessions(self, limit: int = 10) -> list[dict]:
        sessions = sorted(self._sessions.values(), key=lambda x: x["completed_at"], reverse=True)
        return [{"id": s["id"], "team_id": s["team_id"], "mode": s["mode"], "objective": s["objective"][:80], "completed": s["completed_at"]} for s in sessions[:limit]]
