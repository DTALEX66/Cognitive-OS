# 09 KB 能力分层矩阵

> 日期：2026-06-29  
> 来源：对 `Knowledge-Base` 与 `Inspiration-Research` 的当前结构、文档、路由、前端页面、A/B 线模块进行静态分析  
> 目的：把 KB 已有能力按 stable / experimental / research / archive 分层，作为后续工程收敛依据。

---

## 1. 分层规则

| 层级 | 含义 | 用户承诺 | 允许状态 |
|---|---|---|---|
| stable | 当前应稳定可用的核心能力 | 可以写进 README、安装指南、日常使用路径 | 必须有入口、数据、API、最小验证 |
| experimental | 已有实现或页面，但不承诺稳定 | 可以内部试用，不作为默认承诺 | 允许接口变化，必须有风险边界 |
| research | IR 研究或设计资产，尚未进入 KB 工程合同 | 不对用户承诺 | 必须有 Intake Card 后才能进入 KB |
| archive | 历史材料、旧规划、冻结方案 | 不作为当前路线 | 只读参考 |

---

## 2. Stable 候选层

这些能力应作为 KB 当前主线，优先保证稳定。

| 能力 | 用户入口 | KB 后端 / 数据 | IR 对应来源 | 当前判断 | 下一步 |
|---|---|---|---|---|---|
| 健康检查 | `/health` | `pk_radar/api.py` | MVP 文档 | 稳定基础能力 | 保持简单，不扩展成复杂诊断页 |
| 文档导入 | `/upload` | `/documents`, `documents` | A-1 捕获系统 | stable 候选 | 明确支持格式、失败提示、重复导入策略 |
| 文档浏览 | `/knowledge` | `/documents`, `/documents/{id}` | A-2 知识结构 | stable 候选 | 建立来源、标签、时间排序的一致规则 |
| 全文搜索 | `/search` | `/search`, SQLite FTS5 | A-2 知识结构 | stable 候选 | 增加搜索质量基本验收：召回、空结果、中文分词边界 |
| 卡片创建 | `/review` / 相关入口 | `/cards`, `cards` | A-6 间隔复习 | stable 候选 | 明确从文档到卡片的最小闭环 |
| FSRS 复习 | `/review` | `/cards/due`, `/cards/{id}/review`, `reviews` | FSRS 集成方案 | stable 候选 | 增加四评级预览或保留为后续增强 |
| 错题记录 | `/review` 或 `/report` | `/cards/mistakes`, `mistakes` | A-11 反馈系统 | stable 候选 | 将错题转化为下一步学习建议 |
| 每日报告 | `/report` | `/reports/daily` | A-14 长期巩固 | stable 候选 | 报告内容限制在真实数据，不生成无依据建议 |
| 设置 | `/settings` | 本地配置 | 治理系统 | stable 候选 | 把路径、隐私、模型、同步设置分区 |

---

## 3. Experimental 层

这些能力已有页面、API 或模块，但不应马上写入稳定承诺。

| 能力 | 用户入口 / API | KB 模块 | IR 来源 | 风险 | 收敛条件 |
|---|---|---|---|---|---|
| 学习路线 | `/routes`, `/routes/*` | route APIs | A-4 路径规划 | 容易变成空路线图 | 必须绑定文档、卡片、复习表现 |
| 知识宫殿 | `/palace`, `/palace/*` | `learning_final/palace`, palace APIs | A-7 宫殿系统 | 可视化复杂，容易先形式后价值 | 先做 2D/列表化 locus，不急 3D |
| 认知负荷 | `/diagnostics`, `/learning/cognitive-load/*` | `learning_final/cognitive_load.py` | A-3/A-10 | 指标伪精确 | 只输出区间和建议，不输出绝对判断 |
| 记忆编码 | `/skills` 或学习相关入口 | `learning_final/encoding.py` | A-5 编码系统 | 对材料类型依赖强 | 每种编码策略要有适用边界 |
| 费曼教学 | `/teach` | `learning_final/teach_back.py` | A-12 输出教学 | 自动评分不稳定 | 保留人工确认和示例对照 |
| 学习画像 | `/profile` | `learning_final/profile.py` | A-13 学习画像 | 数据不足会误判 | 标注置信度与数据来源 |
| 长期巩固 | `/consolidation` | `learning_final/consolidation.py` | A-14 长期巩固 | 容易与复习重复 | 只处理跨文档、跨主题的巩固 |
| 元认知 | `/report` / `/profile` | `learning_final/metacognition.py` | A-10 元认知 | 建议容易空泛 | 绑定具体预测、结果、偏差 |
| 社区 | `/community` | 前端页面 | 产品化路线 | 本地优先定位冲突 | 暂不进入核心，等同步机制成熟 |
| 同步导出 | `/sync`, `/sync/*` | `sync`, `/sync/export`, `/sync/import`, git sync APIs | 产品化路线 | 数据安全、冲突合并 | 先只做导出，再做导入，再做远端同步 |
| Agent 页面 | `/agent`, `/agent-os/*` | `b_line`, agent-os APIs | B 线 / Agent OS | 权限与执行风险高 | 必须先完成权限矩阵和审计追踪 |
| 认证与 API Key | `/auth/*` | `auth` | 产品化路线 | 本地单机下可能过早复杂化 | 明确单机、本地网络、团队版边界 |

---

## 4. B 线能力矩阵

B 线应先形成机器任务闭环，再扩展多 Agent。

| B 线能力 | KB 模块 / API | 当前层级 | 必须补的合同 |
|---|---|---|---|
| 机器知识单元 | `b_line/machine_knowledge.py`, `/b-line/knowledge` | experimental | 知识可信度、来源、更新时间 |
| 上下文包 | `b_line/context_engine.py`, `/b-line/context-packs`, `/machine/context-pack` | experimental | `context_pack_score` 和 token 预算 |
| 任务包 | `/machine/taskpack`, `/ai/task-packs` | experimental | 验收、回滚、权限、风险等级 |
| 机器路线 | `b_line/route_engine.py`, `/b-line/routes` | experimental | route_score、步骤依赖、失败处理 |
| Agent 角色 | `b_line/agent_role.py`, `/b-line/roles` | experimental | 角色矩阵、工具权限、风险等级 |
| Agent 编排 | `b_line/agent_orchestrator.py`, `/agent-os/orchestrate` | experimental | 顺序/并行/条件模式的可验证输出 |
| 沙箱执行 | `b_line/sandbox_executor.py` | experimental | dry-run、审批门、路径边界 |
| 执行追踪 | `b_line/execution_trace.py`, `/b-line/traces`, `/traces` | stable 候选 | 所有机器辅助任务都必须产出 trace |
| 评估运行 | `b_line/eval_engine.py`, `/b-line/eval/*` | experimental | 指标定义、样本集、回归门 |
| 反馈学习 | `b_line/feedback_loop.py` | experimental | anti-pattern -> machine_lesson -> 下次任务约束 |

B 线的 stable 候选不是“Agent 自动执行”，而是：

```text
可信上下文包 + 可审计任务包 + 执行证据链
```

---

## 5. Research 层

这些内容继续留在 IR，不能直接写进 KB 用户承诺。

| 研究资产 | 来源 | 进入 KB 前置条件 |
|---|---|---|
| 学习科学论文摘要库 | `A-Line-Human-Learning-OS/09-Learning-Science-Knowledge-Base/15_论文摘要库` | 证据验证完成，未验证项保持标记 |
| 主动训练 hooks | A-7 / A-8 / CC hooks | 写出非侵入式训练事件模型 |
| 技能实战沙箱 | A-9 Execute / B 沙箱 | 完成 dry-run 与审批门 |
| 知识迁移系统 | A-15 Transfer | 明确跨系统数据合同和冲突处理 |
| 事件路由系统 | B-04 Event Routing | 先定义事件 schema，再考虑事件总线 |
| MCP 多传输扩展 | B-06 MCP Extension | 先稳定本地 MCP 工具与权限 |
| Agent OS 完整体 | Phase 5 | B-Core 闭环稳定后再进入 |
| 商业化 / 团队版 | Phase 6 | 同步、认证、权限、审计成熟后再进入 |

---

## 6. Archive 层

以下内容只作为历史参考，不作为当前实现依据。

| 位置 | 处理方式 |
|---|---|
| `frozen/` | 保持只读，作为历史规划索引 |
| `reference/archive/` | 只读参考，不直接复制进主线 |
| 旧 Lumina / Aether 规划 | 仅用于理解来源，不进入 README 承诺 |
| 已冻结 B 线材料 | 可引用原则，但具体实现以当前 KB 模块为准 |

---

## 7. 当前最小收敛目标

建议下一阶段只收敛三个交叉点。

### 7.1 A 线：错题 -> 下一步学习建议

目标：把用户错误转成可执行学习动作。

```text
mistake
  -> error_type
  -> related_document
  -> related_card
  -> next_action
  -> review_schedule
```

验收：用户能从日报看到“为什么错、下次做什么”。

### 7.2 B 线：Context Pack 评分

目标：让机器任务上下文可衡量。

```text
context_pack_score = relevance + trust + recency + task_fit + evidence - token_cost
```

验收：每个 taskpack 都显示上下文评分和主要证据来源。

### 7.3 桥接：Intake Card 流程

目标：任何 IR 设计进入 KB 前都先有卡片。

验收：每个新增 KB experimental 能力都能追溯到一个 IR Intake Card。

---

## 8. 后续文件建议

| 文件 | 用途 |
|---|---|
| `docs/10_INTAKE_CARD_CONTEXT_PACK_SCORE.md` | 第一张 Intake Card，聚焦 B 线 Context Pack 评分 |
| `docs/11_INTAKE_CARD_MISTAKE_NEXT_ACTION.md` | 第二张 Intake Card，聚焦 A 线错题到行动 |
| `docs/12_AGENT_ROLE_PERMISSION_MATRIX.md` | Agent 角色、工具、权限、风险矩阵 |

建议顺序：先 `10`，再 `11`，最后 `12`。因为 Context Pack 评分能直接支撑后续 Agent 和任务包质量。