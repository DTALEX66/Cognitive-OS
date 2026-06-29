"""A-line learning module routes"""
from __future__ import annotations
from fastapi import APIRouter, HTTPException
from pk_radar.learning_final.cognitive_load import CognitiveLoadEngine
from pk_radar.learning_final.encoding import EncodingEngine
from pk_radar.learning_final.skills import SkillEngine
from pk_radar.learning_final.rubrics import RubricEngine
from pk_radar.learning_final.teach_back import TeachBackEngine
from pk_radar.learning_final.understanding import UnderstandingEngine
from pk_radar.learning_final.transfer import TransferEngine
from pk_radar.learning_final.b_line_coordinator import BLineCoordinatorV2
from pk_radar.learning_final.agent_coordinator import AgentRole
from pk_radar.learning_final.swarm_orchestrator import SwarmOrchestrator, SwarmMode, SwarmRole
from pk_radar.learning_final.palace import PalaceEngine
from pk_radar.learning_final.scraper_engine import ScraperEngine, Platform
from pk_radar.learning_final.governance import GovernanceEngine, StudyMode

def create_learning_router(store) -> APIRouter:
    router = APIRouter(prefix="/learning", tags=["learning"])
    
    cognitive_load = CognitiveLoadEngine(store)
    encoding = EncodingEngine(store)
    skills = SkillEngine(store)
    rubrics = RubricEngine(store)
    teach_back = TeachBackEngine(store)
    understanding = UnderstandingEngine(store)
    transfer = TransferEngine(store)
    coordinator = BLineCoordinatorV2(store)
    swarm = SwarmOrchestrator(store)
    palace = PalaceEngine(store)
    scraper = ScraperEngine(store)
    governance = GovernanceEngine(store)

    # --- Cognitive Load ---
    @router.post("/cognitive-load/evaluate")
    def evaluate_load(body: dict):
        return cognitive_load.evaluate({"tasks": body.get("tasks", []), "new_concepts": body.get("new_concepts", 0.5), "session_time": body.get("session_time", 30)})

    @router.get("/cognitive-load/status")
    def load_status():
        return {"load": 0.5, "status": "normal"}

    # --- Encode ---
    @router.post("/encode")
    def encode(body: dict):
        text = body.get("text", "")
        tags = body.get("tags", "")
        return encoding.encode(text, tags)

    @router.post("/encode/validate")
    def validate_encoding(body: dict):
        return encoding.validate(body)

    # --- Skills ---
    @router.get("/skills")
    def list_skills(domain: str = "", status: str = ""):
        return {"skills": skills.list(domain, status)}

    @router.post("/skills")
    def create_skill(body: dict):
        name = body.get("name", "")
        domain = body.get("domain", "general")
        difficulty = body.get("difficulty", 3)
        desc = body.get("description", "")
        if not name: raise HTTPException(400, "name required")
        return {"task_id": skills.create_task(name, domain, difficulty, desc)}

    @router.post("/skills/{task_id}/complete")
    def complete_skill(task_id: int, body: dict):
        return skills.complete_task(task_id, body.get("evidence", ""), body.get("score", 1.0))

    # --- Rubrics ---
    @router.get("/rubrics")
    def list_rubrics():
        return {"rubrics": rubrics.list_rubrics()}

    @router.post("/rubrics/score")
    def score_rubric(body: dict):
        return rubrics.score_submission(body.get("rubric_id", 0), body.get("submission", ""))

    # --- Teach-back ---
    @router.post("/teach-back")
    def submit_teach(body: dict):
        return teach_back.submit_explanation(body.get("concept", ""), body.get("explanation", ""))

    @router.get("/teach-back")
    def list_teach(concept: str = "", limit: int = 20):
        return {"explanations": teach_back.list_explanations(concept, limit)}

    @router.post("/teach-back/evaluate")
    def evaluate_teach(body: dict):
        return teach_back.evaluate_clarity(body.get("explanation_id", 0))

    # --- Understanding (Knowledge Structure) ---
    @router.get("/understanding/context")
    def system_context():
        return understanding.build_system_context()

    @router.get("/understanding/user-context")
    def user_context():
        return understanding.build_user_context()

    @router.post("/understanding/classify")
    def classify(body: dict):
        return {"node_type": understanding.classify_content(
            body.get("title", ""), body.get("content", ""), body.get("tags", "")).value}

    @router.post("/understanding/atomize")
    def atomize(body: dict):
        return {"blocks": understanding.atomize(body.get("text", ""))}

    @router.post("/understanding/graph")
    def knowledge_graph(body: dict):
        return understanding.build_knowledge_graph(body.get("card_ids"))

    @router.post("/understanding/nodes")
    def save_node(body: dict):
        if not body.get("title") or not body.get("content"):
            raise HTTPException(400, "title and content required")
        return {"id": understanding.save_knowledge_node(
            body["title"], body["content"], body.get("node_type", "fact"), body.get("tags", ""))}

    # --- Transfer ---
    @router.post("/transfer/bridge")
    def bridge_knowledge(body: dict):
        return transfer.bridge_knowledge(
            body.get("source_domain", ""), body.get("target_domain", ""),
            body.get("content", ""), body.get("context"))

    @router.get("/transfer/sessions")
    def list_transfers(limit: int = 20):
        return {"transfers": transfer.list_transfers(limit)}

    # --- B-line Coordinator ---
    @router.post("/b-line/dispatch")
    def dispatch_agent(body: dict):
        role_str = body.get("role", "research")
        try:
            role = AgentRole(role_str)
        except ValueError:
            raise HTTPException(400, f"invalid role: {role_str}")
        return coordinator.dispatch(role, body.get("prompt", ""), body.get("context"))

    @router.get("/b-line/tasks")
    def list_b_tasks():
        return {"tasks": coordinator.list_active()}

    # --- Palace ---
    @router.get("/palace/structure")
    def palace_structure():
        try:
            return {"rooms": palace.build_from_database().__dict__}
        except Exception:
            return {"rooms": [], "error": "palace not initialized"}

    @router.get("/palace/scan")
    def palace_scan():
        try:
            return {"items": palace.build_from_database().get("rooms", [])}
        except Exception:
            return {"items": []}

    # --- Governance ---
    @router.post("/governance/check")
    def governance_check(body: dict):
        return governance.check(body.get("action", ""), body.get("context", {}))

    @router.post("/governance/mode")
    def set_mode(body: dict):
        mode = body.get("mode", "standard")
        try:
            governance.set_mode(StudyMode(mode))
            return {"mode": mode, "status": "set"}
        except ValueError:
            raise HTTPException(400, f"invalid mode: {mode}")


    # --- Swarm ---
    @router.post("/swarm/create")
    def create_swarm(body: dict):
        return coordinator.swarm_create(body.get("name", "unnamed"), body.get("mode", "sequential"))

    @router.post("/swarm/{team_id}/add-agent")
    def add_swarm_agent(team_id: str, body: dict):
        return coordinator.swarm_add_agent(team_id, body.get("role", "worker"))

    @router.post("/swarm/{team_id}/run")
    def run_swarm(team_id: str, body: dict):
        return coordinator.swarm_run(team_id, body.get("objective", ""))

    @router.get("/swarm/sessions")
    def list_swarm_sessions():
        return {"sessions": swarm.list_sessions()}

    # --- Agent ---
    @router.post("/agent/fork")
    def fork_agent(body: dict):
        return coordinator.agent_fork(body.get("task_id", ""), body.get("prompt", ""))

    @router.post("/agent/memory")
    def save_agent_memory(body: dict):
        if hasattr(coordinator, "_agent_coord"):
            return coordinator._agent_coord.save_memory(body.get("task_id", ""), body.get("key", ""), body.get("value"))
        return {"error": "not available"}

    @router.get("/agent/memory/{task_id}/{key}")
    def recall_agent_memory(task_id: str, key: str):
        if hasattr(coordinator, "_agent_coord"):
            return coordinator._agent_coord.recall_memory(task_id, key) or {"error": "not found"}
        return {"error": "not available"}


    @router.get("/palace/architecture")
    def pa(): return palace.get_architecture()
    @router.post("/palace/store")
    def ps(b): return palace.store_knowledge(b.get("card_id",0),b.get("title",""),b.get("content",""),b.get("tags",""))
    @router.post("/palace/recall")
    def pr(b): return {"results": palace.recall(b.get("query",""),b.get("top_k",5))}
    @router.get("/palace/walk/{wn}")
    def pw(wn): return palace.take_walk(wn)
    @router.post("/palace/build")
    def pb(): return palace.build_from_database()
    @router.post("/scraper/scrape")
    def ss(b):
        p = b.get("platform")
        return scraper.scrape(b.get("url",""), Platform(p) if p else None)
    @router.post("/scraper/search")
    def sr(b): return {"results": scraper.search(b.get("query",""),Platform(b.get("platform","web")),b.get("limit",10))}
    @router.post("/scraper/batch")
    def sb(b): return {"results": scraper.batch_scrape(b.get("urls",[]))}

    return router
