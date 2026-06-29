# 14 A/B 系统终局效果蓝图

> 日期：2026-06-29  
> 主目标：服务 `Knowledge-Base` 与 `Inspiration-Research` 两个主项目。  
> 本文回答的问题：每个环节最终要达到什么效果，而不只是列出技术或模块。  
> 边界：Obsidian 只是部分输入源，不是主系统；最终效果必须落到 KB / IR 两个主项目。

---

## 1. 总体终局设想

最终系统不是一个普通知识库，而是一套“人类学习 + 机器协作”的闭环系统。

```text
用户看到资料、产生想法、遇到问题
  -> 系统捕获并结构化
  -> 人获得学习路线、卡片、复习、反馈、复盘
  -> 机器获得可信上下文、任务包、权限边界、执行证据
  -> 结果回流成人的学习经验和机器的任务经验
```

最终效果分三层：

| 层级 | 最终效果 |
|---|---|
| 对用户 | 任何资料都能变成可搜索、可复习、可行动的知识资产 |
| 对系统 | 每条知识都有来源、结构、状态、复习记录、任务使用记录 |
| 对 Agent | 每次任务都有可信上下文、明确权限、执行 trace、失败复盘和下次约束 |

---

## 2. A/B 环节终局效果总表

| A 系统环节 | B 系统环节 | 最终效果 | 系统产物 | 技术 / 技能 / 插件 | 验收标准 |
|---|---|---|---|---|---|
| A1 捕获系统：资料、笔记、网页、PDF、AI 对话、错题、项目日志进入系统 | B1 机器知识摄取：资料转成机器可用知识单元 | 用户不再担心资料散落；任何候选资料都能被安全收入、标注来源、判断隐私，并决定进入 KB 还是 IR | `Document`、`Source`、`CaptureRecord`、`MachineKnowledgeUnit` | Obsidian Markdown、Web Clipper、KB upload、FastAPI、SQLite、frontmatter、PyMuPDF、python-docx | 导入一份 Markdown/PDF/网页摘录后，可在 KB 搜索到；来源、标签、隐私状态存在；敏感内容不会自动进入任务流 |
| A2 知识结构系统：主题、标签、来源、概念关系、MOC | B2 Context Pack：按任务生成可信上下文 | 用户的资料不只是堆文件，而是能按主题、来源、证据强度组织；Agent 拿到的是最小必要上下文，而不是整库乱塞 | `Tag`、`Source`、`KnowledgeRelation`、`ContextPack`、`context_pack_score` | Obsidian Links/Backlinks/Graph、SQLite FTS5、Pydantic schema、ContextEngine、token estimator | 给定一个任务，系统能生成上下文包，包含来源、相关性、token 预算和裁剪理由 |
| A3 学习诊断系统：识别薄弱点、误解、认知负荷 | B3 任务理解系统：识别任务意图、约束、风险、验收 | 用户知道自己“卡在哪里”；机器知道任务“难在哪里、风险在哪里、验收是什么” | `DiagnosticReport`、`CognitiveLoadSignal`、`TaskIntent`、`RiskProfile` | diagnostics.py、cognitive_load.py、rubrics、TaskPack schema、prompt templates | 用户完成一次学习或任务后，系统能给出具体薄弱点和下一步，不输出空泛鼓励 |
| A4 路径规划系统：学习路线、阶段目标、下一步行动 | B4 机器路线系统：任务步骤、依赖、验证方式、回滚 | 用户每天知道下一步学什么；Agent 每次知道下一步做什么、如何验证、失败如何回滚 | `LearningRoute`、`NextAction`、`MachineRoute`、`RouteStep` | routes API、route_engine.py、状态机、Mermaid、Canvas 草图、Planning patterns | 任意目标都能生成 3-7 个可执行步骤，每步有输入、输出、验证和风险等级 |
| A5 记忆编码系统：双编码、联想、图像化、概念压缩 | B2/B3 上下文压缩与任务表达：把知识压缩成机器提示和例子 | 用户能把复杂知识变成容易记住的表达；机器能把复杂资料变成短、准、可执行的上下文 | `EncodingSuggestion`、`MnemonicCard`、`CompressedContext`、`FewShotExample` | encoding.py、Prompt engineering、few-shot、schema、Markdown callouts、Context scoring | 同一段复杂资料能生成：摘要、卡片、记忆提示、任务上下文四种不同产物 |
| A6 间隔复习系统：卡片、FSRS、复习历史、遗忘风险 | B11 机器经验记忆：任务经验、失败模式、成功模式长期保存 | 人的知识不会学完就忘；机器的任务经验不会每次重新踩坑 | `Card`、`ReviewLog`、`DueQueue`、`MachineLesson`、`AntiPattern` | FSRS5、cards/reviews、SQLite、machine_lesson.py、feedback_loop.py、Mem0/Zep 可选 | 到期卡片能准确出现；任务失败原因能在下一次相似任务中被提示 |
| A7 知识宫殿系统：空间、房间、地点、视觉锚点、路线记忆 | B1/B2 机器知识地图：知识单元可定位、可引用、可组合 | 用户能用空间路线记忆复杂知识；机器能知道知识在体系中的位置 | `PalaceSpace`、`Room`、`Locus`、`KnowledgeMapNode`、`EvidenceLink` | palace 模块、Obsidian Canvas、JSON Canvas、knowledge graph API、entity/relation extraction | 一个主题能同时显示为：文档列表、概念关系、记忆路线、上下文候选 |
| A8 主动训练系统：练习、挑战、阶段训练、反馈 | B10 评估运行系统：eval run、回归测试、质量评估 | 用户通过练习提升能力；机器通过评估防止输出退化 | `TrainingTask`、`Attempt`、`EvalRun`、`RegressionResult` | skill_tasks、pytest、frontend validators、eval_engine.py、rag_evaluator.py、promptfoo/Ragas/Phoenix 可选 | 每个训练任务有评分；每个机器能力有最小评估集和回归记录 |
| A9 技能实战系统：把知识用于真实项目、真实操作 | B8 沙箱执行系统：dry-run、受限执行、审批门、回放 | 用户能从“知道”走到“会做”；Agent 能执行但不越权、不乱改、不失控 | `PracticeProject`、`ExecutionPlan`、`DryRunReport`、`SandboxResult` | sandbox_executor.py、MCP permissions、Docker/E2B/OpenHands 模式、PowerShell safety、approval gate | 高风险任务必须先 dry-run；写入、删除、联网、跨盘必须有权限门和 trace |
| A10 元认知系统：预测、反思、偏差校准 | B10/B11 机器反思系统：任务质量评估、失败模式、下次约束 | 用户知道自己判断哪里偏了；机器知道上次哪里做错，下次如何避免 | `Prediction`、`Reflection`、`CalibrationReport`、`EvalSummary`、`ConstraintUpdate` | metacognition.py、reports、trace_audit.py、eval_engine.py、Langfuse/Phoenix 可选 | 用户预测与实际结果能对比；Agent 失败后能生成可执行的下次约束 |
| A11 反馈错题系统：错题记录、错误归因、补救行动 | B11 反馈学习系统：anti-pattern、failure trace、success pattern | 错题不再只是记录，而是变成复习计划和任务规则；机器错误也变成规则 | `Mistake`、`ErrorType`、`RemediationAction`、`FailureTrace`、`MachineLesson` | mistakes API、daily report、feedback_loop.py、execution_trace.py、Lessons Learned、code-guardian | 一个错误能追溯到资料、卡片、原因、下一步行动；机器错误能进入 anti-pattern |
| A12 输出教学系统：费曼讲解、复述、教学输出 | B3/B5 任务包与 Agent 角色表达：把解释转成任务规格和角色职责 | 用户通过“讲出来”检验理解；Agent 通过清晰角色和任务规格减少误解 | `TeachBackSession`、`FeynmanScore`、`RoleBrief`、`TaskSpec` | teach_back.py、Templates、Skill/Plugin docs、Agent role prompt、Codex skill conventions | 用户能生成一份可读讲解；系统能指出遗漏、复杂词、逻辑断点 |
| A13 学习画像系统：偏好、节奏、能力、历史表现 | B12 模型路由系统：模型能力、成本、速度、fallback | 系统越来越懂用户怎么学；机器越来越会选择合适模型和工具 | `LearnerProfile`、`Preference`、`CapabilityScore`、`ModelRoute`、`CostRecord` | profile.py、model_router.py、TokenBucket、LiteLLM 可选、user preferences | 建议能根据用户历史变化；模型选择能解释原因、成本和 fallback |
| A14 长期巩固系统：日报、周报、跨主题复盘、长期记忆维护 | B1/B11 知识更新与经验巩固：任务结果变成机器知识和经验 | 用户形成长期学习资产；机器形成长期项目资产 | `DailyReport`、`WeeklyReview`、`ConsolidationPlan`、`KnowledgeUpdate`、`MachineLesson` | consolidation.py、daily/weekly report、Obsidian project log、machine_knowledge.py、machine_lesson.py | 每周能看到知识增长、薄弱点、复习负债、任务经验和下一步计划 |
| A15 知识迁移系统：跨领域迁移、从资料到行动 | B14 A-B 翻译系统：学习信号转机器任务，机器结果回流学习 | 用户能把知识迁移到项目；机器能把任务结果转回可学习材料 | `TransferCase`、`AtoBCandidate`、`TaskPack`、`LearningBackflow` | transfer.py、a_to_b.py、IR-to-KB Bridge、Intake Card、Engineering Contract、Codex/DEEP handoff | 一条学习笔记能变成任务包；一次任务结果能变成卡片、错题或 lesson |
| A16 治理系统：隐私、证据、权限、学习数据边界 | B7/B13 工具权限与 MCP 扩展：工具注册、权限矩阵、风险等级、审计 | 系统可放心长期使用；Agent 能力变强但仍受控、可审计、可回滚 | `Policy`、`PermissionMatrix`、`ToolSpec`、`AuditLog`、`RiskGate` | AGENTS.md、安全规则、MCP permissions/audit、mcp_guard.py、Git gate、security-best-practices、Obsidian privacy 字段 | 任意高风险动作能被拦截、解释、审批、记录；stable/experimental 边界清楚 |

---

## 3. 按用户体验理解的最终效果

### 3.1 用户导入资料后的最终效果

```text
资料进来
  -> 自动识别来源和类型
  -> 生成摘要和标签
  -> 可搜索
  -> 可转卡片
  -> 可进入复习
  -> 可进入日报
  -> 可被任务包引用
```

用户感受到的是：资料不会再丢，且每份资料都有下一步。

### 3.2 用户学习后的最终效果

```text
学习一次
  -> 产生卡片
  -> 进入 FSRS
  -> 错题被归因
  -> 薄弱点被记录
  -> 下一步动作被生成
  -> 周期复盘时被重新连接
```

用户感受到的是：不是“看过”，而是真的被系统推着学会。

### 3.3 用户做项目后的最终效果

```text
项目目标
  -> context pack
  -> taskpack
  -> route
  -> permissions
  -> execution trace
  -> eval
  -> machine lesson
  -> learning backflow
```

用户感受到的是：Agent 不只是回答问题，而是能带着上下文、权限和证据做事。

---

## 4. 按系统产物理解的最终效果

最终 KB 里不应该只有文档，还应该有一组长期资产。

| 资产 | 来源 | 用途 |
|---|---|---|
| Documents | 导入资料 | 阅读、搜索、引用 |
| Sources | 网页、书籍、论文、Obsidian note | 来源追踪 |
| Cards | 文档、错题、教学输出 | 复习 |
| Reviews | FSRS | 间隔调度 |
| Mistakes | 学习错误、项目错误 | 归因和补救 |
| Routes | 学习目标、项目目标 | 路径规划 |
| Context Packs | 文档、来源、trace | Agent 上下文 |
| TaskPacks | 任务目标和验收 | Codex/Agent 执行 |
| Execution Traces | 工具调用、命令、文件变化 | 审计和复盘 |
| Eval Runs | 测试、评分、回归 | 质量控制 |
| Machine Lessons | 成功/失败经验 | 下次约束 |
| Intake Cards | IR 研究成果 | IR 到 KB 的桥 |

---

## 5. 分阶段最终效果

### Phase 1: KB 核心闭环

```text
导入 -> 搜索 -> 卡片 -> 复习 -> 错题 -> 日报
```

完成标志：用户能把资料变成长期学习资产。

### Phase 2: IR 到 KB 桥接闭环

```text
Research Note -> Intake Card -> Engineering Contract -> KB experimental
```

完成标志：IR 的研究不再停在文档，而能稳定变成 KB 工程任务。

### Phase 3: B 线机器任务闭环

```text
Context Pack -> TaskPack -> Permission -> Execution Trace -> Eval -> Machine Lesson
```

完成标志：Agent 能在受控范围内协助真实项目，并留下证据。

### Phase 4: A/B 互相回流

```text
人的学习信号 -> 机器任务约束
机器任务结果 -> 人的学习材料
```

完成标志：A 系统和 B 系统不是两套孤立功能，而是互相增强。

### Phase 5: 合并判断

```text
stable 能力进入 KB
research 能力留在 IR
experimental 继续验证
archive 只读保存
```

完成标志：知道什么该合并、什么不该合并、怎么合并。

---

## 6. 最关键的三条终局验收

### 验收 1：知识资产化

任意一份资料进入系统后，最终至少能形成：

```text
Document + Source + Search Index + Card 或 Context Pack
```

### 验收 2：任务证据化

任意一次 Agent / Codex 辅助任务，最终至少能形成：

```text
TaskPack + Permission Decision + Execution Trace + Result Summary
```

### 验收 3：经验回流化

任意一次学习或任务失败，最终至少能形成：

```text
Mistake 或 MachineLesson + NextAction + Future Constraint
```

---

## 7. 当前表格相对上一版补充了什么

上一版只回答：

```text
A 环节对应 B 环节，用什么技术
```

这一版补充回答：

```text
这个环节最终要让用户获得什么
系统最终要沉淀什么资产
Agent 最终要依据什么行动
怎样才算跑通
```

因此后续每个 Intake Card 都必须包含“最终效果”和“验收标准”，不能只写功能名。