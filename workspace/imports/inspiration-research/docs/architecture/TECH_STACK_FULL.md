# Knowledge-Base 技术清单总表

> Generated 2026-06-23 | Agent-5 (Lorentz)
> 覆盖 A线16大系统 + B线Machine Knowledge OS + 前后端环境依赖

---

## 1. A线16大系统技术清单

| # | 系统 | 核心技术/库 | 算法 | 依赖 | 难度 |
|---|------|-----------|------|------|------|
| 1 | 捕获系统 | httpx, markdownify, Scrapling | source_trust评分 | scrapling[ai] | 中 |
| 2 | 知识结构系统 | NetworkX, graphlib | atomization, DAG | networkx | 中 |
| 3 | 学习诊断系统 | numpy, scipy | prerequisite_scoring | numpy | 中 |
| 4 | 学习路线系统 | graphlib, toposort | DAG拓扑排序 | stdlib | 低 |
| 5 | 认知负荷系统 | 自定义评分引擎 | load_score(加权和) | 无 | 低 |
| 6 | 记忆编码系统 | Pillow, pydub, openai-whisper | modality_fit | Pillow, openai | 高 |
| 7 | 间隔复习系统 | FSRS-5, math, datetime | FSRS遗忘曲线 | stdlib | 已完成 |
| 8 | 知识宫殿系统 | 3D可选: three.js(前端) | spatial_placement | 可选 | 高 |
| 9 | 主动训练系统 | 自定义quiz引擎 | weakness_priority | 无 | 中 |
| 10 | 技能实战系统 | 自定义rubric引擎 | rubric_scoring(加权) | 无 | 中 |
| 11 | 元认知系统 | 自定义统计 | confidence_gap | 无 | 低 |
| 12 | 反馈错误系统 | 自定义分类器 | error_taxonomy | 无 | 中 |
| 13 | 输出教学系统 | OpenAI/本地LLM | explanation_score | openai/ollama | 中 |
| 14 | 学习画像系统 | 自定义策略引擎 | adaptive_policy | 无 | 中 |
| 15 | 长期巩固系统 | 自定义diff/merge | knowledge_evolution | 无 | 中 |
| 16 | A转B翻译系统 | 自定义蒸馏器 | mastery→evidence→publish | 无 | 已完成 |

---

## 2. B线Machine Knowledge OS技术清单

| 层 | 核心技术/库 | 对标开源项目 | 许可 | 难度 |
|----|-----------|-------------|------|------|
| 机器知识 | SQLite + 自定义索引 | Mem0, Zep | MIT/Apache-2.0 | 中 |
| 上下文包 | 自定义评分器 | LlamaIndex, Haystack | MIT | 中 |
| 机器路线 | 轻量状态机 | LangGraph, Conductor | MIT | 高 |
| MCP工具 | JSON Schema + 权限矩阵 | FastMCP, MCP Python SDK | MIT | 中 |
| Agent角色 | 自定义分配引擎 | AutoGen, CrewAI | MIT | 高 |
| 任务包生成 | 模板引擎 | OpenHands, SWE-agent | MIT | 中 |
| 执行沙箱 | subprocess + dry_run | E2B, Docker | MIT/Apache-2.0 | 高 |
| 评估审计 | 自定义eval框架 | Langfuse, promptfoo, Ragas | MIT/Apache-2.0 | 中 |
| 模型网关 | LiteLLM, httpx | LiteLLM, vLLM, Ollama | MIT | 中 |
| 机器记忆 | SQLite + embedding | Mem0, Zep, projectmem | Apache-2.0 | 中 |
| 经验回流 | 事件驱动 | DSPy, projectmem | MIT | 中 |

---

## 3. 前后端环境依赖版本

### 后端 (Python >=3.10)

| 依赖 | 版本 | 用途 |
|------|------|------|
| fastapi | >=0.115 | Web框架 |
| uvicorn | >=0.30 | ASGI服务器 |
| pydantic | >=2.7 | 数据验证 |
| typer | >=0.12 | CLI框架 |
| rich | >=13.7 | 终端美化 |
| markdownify | >=0.13 | HTML→Markdown |
| orjson | >=3.10 | 快速JSON |
| httpx | >=0.27 | HTTP客户端 |
| python-dotenv | >=1.0 | 环境变量 |
| pytest | >=8 | 测试框架 |
| ruff | >=0.5 | Linter |
| mypy | >=1.10 | 类型检查 |
| scrapling[ai] | 可选 | Web抓取 |
| streamlit | >=1.38 (可选) | 数据分析UI |
| ollama | >=0.3 (可选) | 本地AI |

### 前端 (计划)

| 依赖 | 用途 |
|------|------|
| React/Vue/Svelte | SPA框架 |
| D3.js / Chart.js | 雷达图/时间线/图表 |
| Mermaid.js | 流程图/状态图 |
| Monaco/CodeMirror | 代码编辑器 |
| Tailwind CSS | 样式框架 |

### 开发工具

| 工具 | 用途 |
|------|------|
| uv | Python包管理 |
| ruff | 代码格式化/Lint |
| mypy | 类型检查 |
| pytest | 测试框架 |
| git | 版本控制 |
| GitHub Actions | CI/CD |

---

## 4. A线 + B线 数据库表规划

### 已实现 (knowledge.db)

| 表 | 用途 |
|----|------|
| documents | 文档存储 |
| documents_fts | 全文搜索 |
| sources | 知识来源 |
| entities | 知识实体 |
| relations | 实体关系 |
| observations | 学习观察 |
| sessions | 学习会话 |
| cards | 间隔重复卡片 |
| reviews | 复习记录 |

### A线待实现

| 表 | 用途 |
|----|------|
| knowledge_blocks | 知识块原子化 |
| encoding_anchors | 记忆编码锚点 |
| skill_tasks | 技能实战任务 |
| teach_back_records | 费曼输出记录 |
| experiment_runs | A/B学习实验 |
| learner_profile | 学习画像 |
| consolidation_events | 知识巩固事件 |
| cognitive_load_log | 认知负荷日志 |

### B线待实现

| 表 | 用途 |
|----|------|
| machine_knowledge_units | 机器知识单元 |
| machine_routes | 机器执行路线 |
| agent_roles | Agent角色定义 |
| task_packs | 任务包 |
| execution_traces | 执行追踪 |
| context_packs | 上下文包 |
| machine_memory_events | 机器记忆事件 |
| machine_lessons | 机器经验 |
| anti_patterns | 反模式库 |

---

## 5. 每个模块需要的技能/知识/工具

### A线系统5: 认知负荷
- 技能: Python数值计算
- 知识: 认知心理学基础（Miller's Law 7±2）
- 库: math, dataclasses
- 测试: pytest参数化测试

### A线系统6: 记忆编码
- 技能: 多模态数据处理
- 知识: 双编码理论(Dual Coding Theory)
- 库: Pillow(图片), pydub(音频)
- 可选: openai-whisper(语音转文字)

### A线系统10: Rubric评分
- 技能: 加权评分系统设计
- 知识: 教育评估理论
- 库: pydantic(评分模型), dataclasses
- 前端: 雷达图组件

### A线系统14: 学习画像
- 技能: 策略模式, 自适应系统
- 知识: 学习风格理论(VARK), Dunning-Kruger
- 库: numpy(统计分析)
- 前端: 雷达图, 时间线

### B线路由规划
- 技能: 状态机设计, DAG算法
- 知识: LangGraph状态图概念
- 参考: LangGraph, Haystack Pipelines
- 库: graphlib (stdlib)

### B线Agent协作
- 技能: 多Agent系统设计
- 知识: AutoGen对话模式, CrewAI角色模型
- 参考: AutoGen, CrewAI, MetaGPT
- 库: asyncio(并发)

### B线执行沙箱
- 技能: subprocess管理, Docker
- 知识: 容器隔离, 权限控制
- 参考: OpenHands, E2B, SWE-agent
- 库: subprocess, tempfile

### B线评估审计
- 技能: 测试自动化, 回归测试
- 知识: LLM评估指标(faithfulness, relevancy)
- 参考: promptfoo, Ragas, Langfuse
- 库: pytest, custom eval

### B线模型网关
- 技能: API适配, 负载均衡
- 知识: LiteLLM路由策略
- 参考: LiteLLM, vLLM
- 库: httpx, asyncio

### B线机器记忆
- 技能: embedding, 向量检索
- 知识: Mem0记忆抽取, Zep时序知识图谱
- 参考: Mem0, Zep, ChromaDB
- 库: 可选 chromadb, sentence-transformers

---

## 6. 完整技能矩阵

| 角色 | 技能要求 | A线模块 | B线模块 |
|------|---------|---------|---------|
| Python后端 | FastAPI, Pydantic, SQLite | 全部 | 全部 |
| 算法 | 数学/统计, 机器学习基础 | SRS, Rubric, 画像 | 路由, 评分 |
| 前端 | React/Vue, Chart.js, Tailwind | 面板组件 | 面板组件 |
| DevOps | Docker, GitHub Actions, uv | CI/CD | 沙箱 |
| AI/ML | LLM调用, Prompt工程, RAG | 编码, 教学 | 评估, 记忆 |
| 安全 | 权限模型, 沙箱隔离 | 用户隔离 | 执行门控 |
| 产品 | 学习科学, UX设计 | 闭环设计 | 闭环设计 |
