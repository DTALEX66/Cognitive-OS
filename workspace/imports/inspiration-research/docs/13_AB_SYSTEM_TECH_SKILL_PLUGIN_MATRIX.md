# 13 A/B 系统环节与技术/技能/插件矩阵

> 日期：2026-06-29  
> 主目标：服务 `Knowledge-Base` 与 `Inspiration-Research` 两个主项目。  
> 边界：Obsidian 只属于输入/捕获环节的一部分，不是主系统。  
> 用途：把 A 系统、B 系统和涉及技术/技能/插件横向对应起来，作为后续 Intake Card 与 KB 工程任务拆分依据。

---

## 总表

| A 系统：Human Learning OS 各环节 | B 系统：Machine Knowledge / Agent OS 各环节 | 涉及技术 / 技能 / 插件 |
|---|---|---|
| A1 捕获系统：收集笔记、网页、PDF、Markdown、本地文档、AI 对话、错题、项目日志 | B1 机器知识摄取：把资料转成 machine knowledge unit，保留来源、可信度、更新时间 | Obsidian Markdown、Properties、Bases、Web Clipper、KB upload/documents、FastAPI、SQLite、PyMuPDF、python-docx、markdown/frontmatter 解析 |
| A2 知识结构系统：标签、来源、主题、概念关系、MOC、人工知识结构 | B2 上下文包系统：按任务组装 context pack，控制 token、来源、证据强度 | Obsidian 双链/Backlinks/Graph、YAML frontmatter、SQLite FTS5、KB tags/sources、ContextEngine、token estimator、Pydantic/JSON Schema |
| A3 学习诊断系统：判断薄弱点、理解缺口、认知负荷、学习状态 | B3 任务理解系统：识别任务类型、约束、风险、验收标准，生成 taskpack 输入 | learning_final/diagnostics.py、cognitive_load.py、rubrics、TaskPack schema、prompt templates、Intake Card、Codex task decomposition |
| A4 路径规划系统：生成学习路线、下一步行动、阶段目标 | B4 机器路线系统：规划任务步骤、依赖、验证方式、风险等级 | route APIs、route_engine.py、任务图、依赖图、状态机、Mermaid/Canvas 草图、Planning skill、IR Roadmap |
| A5 记忆编码系统：双编码、联想、图像化、PAO、概念压缩 | B2/B3 上下文压缩与任务表达：把知识压缩成机器可用提示、约束和示例 | encoding.py、schema 设计、Prompt engineering、few-shot examples、Obsidian Canvas、Markdown callouts、Context Pack scoring |
| A6 间隔复习系统：卡片、FSRS 调度、复习记录、遗忘风险 | B11 机器经验记忆：把任务结果沉淀为 machine lesson、anti-pattern、可复用经验 | FSRS5、cards/reviews、SQLite、daily report、machine_lesson.py、feedback_loop.py、未来可选 Mem0/Zep |
| A7 知识宫殿系统：空间、房间、地点、视觉锚点、路线记忆 | B1/B2 机器知识地图：把知识单元组织成可检索、可引用、可打包的结构 | palace 模块、Obsidian Canvas、Graph view、JSON Canvas、knowledge graph API、实体/关系抽取、可视化组件 |
| A8 主动训练系统：练习、挑战、阶段训练、训练反馈 | B10 评估运行系统：eval run、回归测试、任务质量评估、RAG 评估 | training 页面、skill_tasks、pytest、frontend validators、eval_engine.py、rag_evaluator.py、promptfoo/Ragas/Phoenix 作为未来可选参考 |
| A9 技能实战系统：把知识用于真实任务、项目练习、工具操作 | B8 沙箱执行系统：dry-run、受限执行、审批门、执行回放 | sandbox_executor.py、MCP permissions、Docker/E2B/OpenHands 模式参考、LocalSandbox、PowerShell safety、dry-run/WhatIf、approval gate |
| A10 元认知系统：预测、反思、偏差校准、学习策略调整 | B10/B11 机器反思系统：评估任务结果，识别失败模式，产生下次约束 | metacognition.py、reports、eval_engine.py、trace_audit.py、Langfuse/Phoenix 可观测性参考、machine lessons、review checklist |
| A11 反馈错题系统：错题记录、错误归因、下一步补救 | B11 反馈学习系统：anti-pattern、failure trace、success pattern、约束回写 | mistakes API、daily report、feedback_loop.py、execution_trace.py、machine_lesson.py、Lessons Learned、code-guardian 复盘流程 |
| A12 输出教学系统：费曼讲解、复述、教学输出、理解验证 | B3/B5 任务包与 Agent 角色表达：把人类解释转成任务规格、角色职责和验收 | teach_back.py、Feynman score、Templates、Skill/Plugin 文档格式、Agent role prompt、Codex skill conventions |
| A13 学习画像系统：偏好、节奏、能力、历史表现、个性化建议 | B12 模型路由系统：模型选择、成本、限流、能力匹配、fallback | profile.py、LearnerProfile、model_router.py、TokenBucket、LiteLLM 可选、成本追踪、user preferences |
| A14 长期巩固系统：日报、周报、跨主题复盘、长期记忆维护 | B1/B11 知识更新与经验巩固：把长期任务结果沉淀为可检索机器知识 | consolidation.py、daily/weekly reports、Obsidian project logs、Context Pack archive、machine_knowledge.py、machine_lesson.py |
| A15 知识迁移系统：跨领域迁移、从学习到任务、从资料到行动 | B14 A-B 翻译系统：把人的学习信号翻译成机器任务信号，把机器结果回流为学习材料 | transfer.py、a_to_b.py、IR-to-KB Bridge、Intake Card、Engineering Contract、TaskPack、Codex/DEEP handoff |
| A16 治理系统：隐私、权限、证据、学习数据边界、操作规则 | B7/B13 工具权限与 MCP 扩展：工具注册、权限矩阵、风险等级、审计 | AGENTS.md、安全规则、MCP tool_registry/permissions/audit、mcp_guard.py、Git status/diff gate、Obsidian privacy 字段、code-guardian/security-best-practices |

---

## 分层说明

| 层级 | A 系统关注 | B 系统关注 | 代表技术 / 插件 |
|---|---|---|---|
| 输入层 | 捕获资料、笔记、错题、灵感 | 摄取资料、生成机器知识单元 | Obsidian、Web Clipper、Markdown、frontmatter、KB documents |
| 结构层 | 标签、主题、来源、知识关系 | context pack、知识检索、任务上下文 | SQLite FTS5、Graph、Backlinks、ContextEngine、Pydantic |
| 学习层 | 诊断、规划、编码、复习、反馈 | 任务理解、任务路线、角色分配 | FSRS、rubrics、route_engine、TaskPack、AgentRole |
| 执行层 | 技能实战、训练、输出教学 | 沙箱执行、工具调用、MCP 权限 | MCP、sandbox_executor、dry-run、Docker/E2B 参考、Codex skills |
| 反馈层 | 错题、日报、元认知、长期巩固 | trace、eval、machine lesson、anti-pattern | reports、trace_audit、eval_engine、feedback_loop、Langfuse/Phoenix 参考 |
| 治理层 | 隐私、证据、学习边界 | 权限、审计、风险、回滚 | AGENTS.md、Git gate、MCP audit、security-best-practices |

---

## Obsidian 的准确位置

Obsidian 只出现在以下位置：

```text
A1 捕获系统
A2 知识结构系统的人工预整理
A14 长期巩固中的项目日志 / 复盘
IR Research Note 的候选来源
```

它不承担：

```text
KB 主数据库
IR 证据验证系统
B 系统 Agent 执行系统
MCP 权限系统
最终合并主体
```

---

## 后续拆分建议

下一步应该把每一行拆成 Intake Card，例如：

| 优先级 | Intake Card |
|---|---|
| P1 | A1/B1：资料捕获到机器知识单元 |
| P1 | A2/B2：知识结构到 Context Pack |
| P1 | A11/B11：错题反馈到 Machine Lesson |
| P2 | A4/B4：学习路线到机器路线 |
| P2 | A16/B7：治理规则到权限矩阵 |