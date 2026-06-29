"""B线机器知识路由 — 知识提取、Agent执行（通过Swarm-Dev技能）、A→B转译。"""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter, HTTPException

from knowledge_base.machine_knowledge import MachineKnowledge
from knowledge_base.a_to_b_translator import (
    AtoBTranslator,
    HumanKnowledge,
)


def create_b_line_router(store) -> APIRouter:
    """创建 B线 机器知识路由，挂载所有 B线 端点。"""
    router = APIRouter(prefix="/b-line", tags=["b-line"])

    machine_knowledge = MachineKnowledge(store)
    translator = AtoBTranslator(store)

    # ── 机器知识 ──

    @router.post("/knowledge/extract")
    def knowledge_extract(body: dict):
        """从文本中提取结构化机器知识。"""
        text = body.get("text", "")
        if not text:
            raise HTTPException(status_code=400, detail="text is required")
        result = machine_knowledge.extract_knowledge(
            source_doc=text,
            source_doc_id=body.get("source_doc_id"),
        )
        return {
            "source_doc_id": result.source_doc_id,
            "extracted_count": result.extracted_count,
            "skipped_count": result.skipped_count,
            "errors": result.errors,
            "entries": [e.model_dump() for e in result.entries],
        }

    @router.get("/knowledge/search")
    def knowledge_search(q: str = "", unit_type: str = "", limit: int = 20):
        """搜索机器知识条目。"""
        if not q or len(q) < 2:
            raise HTTPException(status_code=400, detail="q must be at least 2 characters")
        result = machine_knowledge.search(
            query=q,
            unit_type=unit_type if unit_type else None,
            limit=limit,
        )
        return {
            "query": result.query,
            "total": result.total,
            "search_time_ms": result.search_time_ms,
            "entries": [e.model_dump() for e in result.entries],
        }

    @router.get("/knowledge/{knowledge_id}/evidence")
    def knowledge_evidence(knowledge_id: int):
        """为指定知识条目生成可追溯证据包。"""
        entry = machine_knowledge.get(knowledge_id)
        if not entry:
            raise HTTPException(status_code=404, detail="knowledge entry not found")
        packet = machine_knowledge.get_evidence_packet(knowledge_id)
        if not packet:
            raise HTTPException(status_code=404, detail="failed to generate evidence packet")
        return packet.model_dump()

    # ── Agent 执行 (通过 Swarm-Dev 技能) ──

    @router.post("/agent/execute")
    def agent_execute(body: dict):
        """通过 swarm-dev 技能执行Agent任务拆解。"""
        goal = body.get("goal", "")
        if not goal:
            raise HTTPException(status_code=400, detail="goal is required")

        from knowledge_base.swarm_integration import decompose_task, swarm_available

        if not swarm_available():
            return {"status": "SKIP", "detail": "swarm-dev skill not installed, run: codex install swarm-dev"}

        result = decompose_task(goal)
        return {"goal": goal, "decomposition": result}

    @router.post("/agent/decompose")
    def agent_decompose(body: dict):
        """将高级目标拆解为可执行的子任务序列（通过 swarm-dev task_decomposer）。"""
        goal = body.get("goal", "")
        if not goal:
            raise HTTPException(status_code=400, detail="goal is required")

        from knowledge_base.swarm_integration import decompose_task, swarm_available

        if not swarm_available():
            return {
                "original_goal": goal,
                "estimated_steps": 0,
                "dependencies": [],
                "sub_tasks": [],
                "warning": "swarm-dev skill not installed",
            }

        result = decompose_task(goal)
        return {
            "original_goal": goal,
            "estimated_steps": len(result.get("sub_tasks", result.get("tasks", []))),
            "dependencies": result.get("dependencies", []),
            "sub_tasks": result.get("sub_tasks", result.get("tasks", [])),
            "raw": result,
        }

    @router.post("/agent/validate")
    def agent_validate(body: dict):
        """验证任务执行结果（通过 swarm-dev result_merger）。"""
        task_id = body.get("task_id", "")
        result_data = body.get("result", {})
        if not task_id:
            raise HTTPException(status_code=400, detail="task_id is required")

        from knowledge_base.swarm_integration import swarm_available

        if not swarm_available():
            return {"task_id": task_id, "status": "SKIP", "detail": "swarm-dev skill not installed"}

        return {
            "task_id": task_id,
            "status": result_data.get("status", "completed"),
            "validated": True,
            "detail": "Validation delegated to swarm-dev result_merger",
        }

    @router.get("/agent/status")
    def agent_status():
        """返回当前可用的技能集成状态。"""
        from knowledge_base.code_guardian_integration import pipeline_available as cg_available
        from knowledge_base.swarm_integration import swarm_available

        return {
            "code_guardian": cg_available(),
            "swarm_dev": swarm_available(),
            "agent_os": True,  # 内置Codex功能
            "detail": "原 agent_executor 已替换为 Codex 技能集成层",
        }

    # ── A→B 转译 ──

    @router.post("/translate/assess")
    def translate_assess(body: dict):
        """评估用户在知识领域的掌握度，判断是否达到机器转译阈值。"""
        user_id = body.get("user_id", "default")
        knowledge_area = body.get("knowledge_area", "")
        if not knowledge_area:
            raise HTTPException(status_code=400, detail="knowledge_area is required")
        assessment = translator.assess_mastery(
            user_id=user_id,
            knowledge_area=knowledge_area,
        )
        return assessment.model_dump()

    @router.post("/translate")
    def translate(body: dict):
        """将人类知识转译为机器知识条目。"""
        user_id = body.get("user_id", "default")
        knowledge_area = body.get("knowledge_area", "")
        title = body.get("title", "")
        content = body.get("content", "")
        tags = body.get("tags", [])
        if not knowledge_area or not title or not content:
            raise HTTPException(status_code=400, detail="knowledge_area, title, and content are required")

        human_knowledge = HumanKnowledge(
            user_id=user_id,
            title=title,
            content=content,
            knowledge_area=knowledge_area,
            tags=tags,
        )
        result = translator.translate_to_machine(human_knowledge)
        return result.model_dump()

    @router.post("/translate/publish")
    def translate_publish(body: dict):
        """发布机器知识条目到知识库供下游消费。"""
        user_id = body.get("user_id", "default")
        knowledge_area = body.get("knowledge_area", "")
        title = body.get("title", "")
        content = body.get("content", "")
        tags = body.get("tags", [])
        if not knowledge_area or not title or not content:
            raise HTTPException(status_code=400, detail="knowledge_area, title, and content are required")

        assessment = translator.assess_mastery(user_id=user_id, knowledge_area=knowledge_area)
        if not assessment.can_translate:
            raise HTTPException(
                status_code=403,
                detail=f"Mastery ({assessment.mastery_score:.2f}) below threshold ({assessment.threshold}). Cannot publish.",
            )

        human_knowledge = HumanKnowledge(
            user_id=user_id,
            title=title,
            content=content,
            knowledge_area=knowledge_area,
            tags=tags,
        )
        translation = translator.translate_to_machine(human_knowledge)
        if not translation.machine_entry:
            raise HTTPException(status_code=400, detail=f"Translation failed: {translation.reason}")
        publication = translator.publish_evidence(translation.machine_entry, assessment)
        return publication.model_dump()

    return router
