"""B-Line Coordinator V2 - delegates to AgentCoordinator + SwarmOrchestrator"""
from .agent_coordinator import AgentCoordinator, AgentRole
from .swarm_orchestrator import SwarmOrchestrator, SwarmMode, SwarmRole

class BLineCoordinatorV2:
    def __init__(self, store=None):
        self.agent_coord = AgentCoordinator(store)
        self.swarm = SwarmOrchestrator(store)
    def dispatch(self, role, prompt, context=None):
        return self.agent_coord.dispatch(role, prompt, context)
    def swarm_create(self, name, mode="sequential"):
        try:
            m = SwarmMode(mode) if isinstance(mode, str) else mode
        except ValueError:
            m = SwarmMode.SEQUENTIAL
        return self.swarm.create_team(name, m)
    def swarm_add_agent(self, team_id, role="worker"):
        try:
            r = SwarmRole(role) if isinstance(role, str) else role
        except ValueError:
            r = SwarmRole.WORKER
        return self.swarm.add_agent(team_id, r, {})
    def swarm_run(self, team_id, objective):
        return self.swarm.run_team(team_id, objective)
    def agent_fork(self, task_id, prompt):
        return self.agent_coord.agent_fork(task_id, prompt)
    def list_active(self):
        return self.agent_coord.list_active()
