# 12 主框架与环节系统拆分

> 日期：2026-06-29  
> 主目标：打造 `Knowledge-Base` 与 `Inspiration-Research` 两个项目，并在验证成熟后决定最终合并方式。  
> 边界：Obsidian 只是 KB 工作流中的一个输入/捕获环节，不是主系统，不是最终目标。  
> 输出目的：把总框架、各环节、各系统、流转关系和阶段边界细分清楚。

---

## 1. 总体定位

当前体系只有两个主项目。

```text
Inspiration-Research
  = 研究、论证、框架、证据、设计、路线、Intake Card

Knowledge-Base
  = 工程实现、可运行系统、数据存储、搜索、复习、任务包、Agent 执行流
```

Obsidian 的位置：

```text
Obsidian
  = KB 的部分上游输入源
  = 个人笔记、资料捕获、灵感沉淀、人工整理工具
  != 主系统
  != 合并目标
  != IR 或 KB 的替代品
```

---

## 2. 总框架图

```text
外部输入源
  ├─ Obsidian 笔记库
  ├─ 网页 / 文章 / 论文线索
  ├─ 本地文档 / PDF / Markdown
  ├─ AI 对话 / 项目日志
  └─ 手动录入 / 错题 / 经验教训

        ↓ 筛选、清洗、标注、隐私过滤

Inspiration-Research
  ├─ 研究验证层
  ├─ 框架设计层
  ├─ A 线 Human Learning OS
  ├─ B 线 Machine Knowledge / Agent OS
  ├─ Intake Card
  └─ KB 工程合同

        ↓ 成熟度门槛 / 工程任务拆解

Knowledge-Base
  ├─ 文档知识库
  ├─ 搜索与索引
  ├─ 卡片与 FSRS 复习
  ├─ 错题与反馈
  ├─ A 线学习增强模块
  ├─ B 线机器任务模块
  ├─ MCP / Agent / TaskPack
  ├─ 执行审计与反馈学习
  └─ 前端 / 桌面 / 插件 / 同步

        ↓ 验证稳定、边界清楚、功能成熟

最终合并判断
  ├─ 保持双仓库 + 稳定桥接
  ├─ 文档合并到 KB
  ├─ 部分研究资产迁入 KB docs
  └─ 仓库级合并（最后选项）
```

---

## 3. 项目层级拆分

### 3.1 P0：主目标层

| 项目 | 目标 | 交付物 |
|---|---|---|
| `Knowledge-Base` | 做成真正可运行、可积累、可复习、可搜索、可任务化的个人知识系统 | 前后端、数据库、API、MCP、Agent、复习系统、任务包 |
| `Inspiration-Research` | 给 KB 提供经过验证的研究、框架、路线和设计规格 | 框架文档、证据分级、路线图、Intake Card、工程合同 |

### 3.2 P1：输入源层

输入源不是主系统，只提供材料。

| 输入源 | 角色 | 进入方式 | 风险 |
|---|---|---|---|
| Obsidian | 个人笔记与灵感捕获 | 候选笔记导出 | 隐私、未验证观点、插件噪音 |
| 网页 / 文章 | 外部资料来源 | Web Clipper / 手动导入 | 来源不稳定、版权、断链 |
| 论文线索 | 研究证据候选 | IR 验证后进入证据池 | 伪论文、引用错误 |
| 本地文档 | KB 普通知识材料 | KB documents 导入 | 格式、重复、隐私 |
| AI 对话 | 想法与过程记录 | 作为 project log 或 lesson | 不能作为事实证据 |
| 错题 / 复盘 | 学习反馈 | KB mistakes / daily report | 分类不准、建议空泛 |

### 3.3 P2：研究框架层

由 IR 承担。

| 子系统 | 职责 |
|---|---|
| 证据验证系统 | 判断资料是否真实、可信、可引用 |
| 框架设计系统 | 把零散材料抽象成结构、流程、规格 |
| Intake Card 系统 | 把研究成果变成可进入 KB 的候选卡 |
| 决策记录系统 | 记录为什么做、为什么不做、为什么推迟 |
| 风险边界系统 | 明确隐私、安全、数据、误导、执行风险 |
| 路线图系统 | 决定 stable / experimental / future 的推进顺序 |

### 3.4 P3：工程运行层

由 KB 承担。

| 子系统 | 职责 |
|---|---|
| 文档系统 | 导入、清洗、存储、展示资料 |
| 搜索系统 | FTS5 / 语义 / 混合检索，支持用户和 Agent 查找知识 |
| 卡片系统 | 从资料生成可复习卡片 |
| 复习系统 | FSRS 调度、复习记录、遗忘风险管理 |
| 错题系统 | 记录错误、归因、下一步行动 |
| 报告系统 | 日报、周报、学习路径反馈 |
| A 线学习系统 | 人类学习增强：诊断、编码、教学、画像、元认知 |
| B 线机器系统 | 机器任务增强：上下文包、任务包、Agent、审计、反馈 |
| MCP / 工具系统 | 工具注册、权限、审计、执行边界 |
| 前端系统 | 用户可操作界面 |
| 同步 / 导出系统 | 数据导出、导入、跨端同步、备份 |

---

## 4. 主流程拆分

### 4.1 资料进入流程

```text
输入源
  -> 隐私判断
  -> 来源判断
  -> 格式清洗
  -> 标签 / frontmatter / 元数据
  -> 进入 IR 或 KB
```

分流规则：

| 内容类型 | 进入哪里 |
|---|---|
| 普通知识文档 | KB documents |
| 学习材料 | KB documents + cards |
| 研究线索 | IR evidence / research note |
| 架构想法 | IR framework / Intake Card |
| 功能需求 | IR Intake Card -> KB task |
| 错题经验 | KB mistakes -> reports -> IR lessons 可选 |
| 私人敏感内容 | 留在源系统，不进入 IR / KB |

### 4.2 IR 到 KB 的吸收流程

```text
IR Research Note
  -> Evidence Boundary
  -> Framework Spec
  -> Intake Card
  -> KB Engineering Contract
  -> KB experimental
  -> Test / Review / Audit
  -> KB stable
```

吸收门槛：

| 阶段 | 通过条件 |
|---|---|
| Research Note | 来源明确，边界明确 |
| Framework Spec | 有问题、用户场景、数据合同、API/UI 影响 |
| Intake Card | 有验收、风险、回滚、最小验证 |
| Engineering Contract | 指明 KB 模块、接口、数据、测试 |
| experimental | 能跑，但不承诺稳定 |
| stable | 文档、测试、UI、API、回滚全部明确 |

### 4.3 KB 内部运行流程

```text
Document
  -> Search Index
  -> Knowledge View
  -> Card Generation
  -> FSRS Review
  -> Mistake / Feedback
  -> Daily Report
  -> Next Action
```

机器辅助流程：

```text
Document / Trace / Card / Source
  -> Context Pack
  -> TaskPack
  -> Agent Role / Tool Permission
  -> Execution Trace
  -> Eval Run
  -> Machine Lesson
  -> Next Task Constraint
```

---

## 5. A 线 Human Learning OS 细分

A 线服务“人怎么更好地学”。

| 编号 | 系统 | 当前定位 | KB 对应 |
|---|---|---|---|
| A1 | 捕获系统 | 收集资料、笔记、网页、本地文件 | upload / documents / Obsidian 输入 |
| A2 | 知识结构系统 | 分类、标签、概念关系、来源关系 | knowledge / search / tags / sources |
| A3 | 诊断系统 | 判断学习薄弱点、理解缺口 | diagnostics / cognitive_load |
| A4 | 路径规划系统 | 给用户下一步学习路线 | routes / next-actions |
| A5 | 记忆编码系统 | 图像化、联想、PAO、双编码 | encoding / skills |
| A6 | 间隔复习系统 | FSRS 复习调度 | cards / reviews |
| A7 | 知识宫殿系统 | 空间化记忆结构 | palace |
| A8 | 主动训练系统 | 练习、挑战、阶段训练 | training / skill-tasks |
| A9 | 技能实战系统 | 把知识用于任务 | task / teach / execute |
| A10 | 元认知系统 | 预测、反思、偏差校准 | metacognition / report |
| A11 | 反馈错题系统 | 错误归因、复盘、下一步 | mistakes / feedback |
| A12 | 输出教学系统 | 费曼讲解、教学输出 | teach-back / teach |
| A13 | 学习画像系统 | 用户偏好、能力、节奏 | profile |
| A14 | 长期巩固系统 | 周期复盘、跨主题连接 | consolidation / daily report |
| A15 | 知识迁移系统 | 跨领域迁移、任务迁移 | transfer / bridge |
| A16 | 治理系统 | 学习数据权限、风险、边界 | settings / policy / permissions |

A 线阶段建议：

```text
先稳定 A1 + A2 + A6 + A11 + A14
再增强 A3 + A4 + A5 + A10 + A12 + A13
最后推进 A7 + A8 + A9 + A15 + A16
```

---

## 6. B 线 Machine Knowledge / Agent OS 细分

B 线服务“机器怎么更好地协助任务”。

| 编号 | 系统 | 当前定位 | KB 对应 |
|---|---|---|---|
| B1 | 机器知识系统 | 把知识转成机器可用单元 | machine_knowledge |
| B2 | 上下文包系统 | 为任务打包最小可信上下文 | context_engine / context_pack |
| B3 | 任务包系统 | 生成可交给 Codex / Agent 的任务 | taskpack |
| B4 | 机器路线系统 | 规划任务步骤、依赖、风险 | route_engine |
| B5 | Agent 角色系统 | Planner / Researcher / Coder / Tester 等 | agent_role |
| B6 | Agent 编排系统 | 顺序、并行、条件执行 | agent_orchestrator |
| B7 | 工具权限系统 | 工具、路径、网络、写入、删除边界 | mcp permissions / mcp_guard |
| B8 | 沙箱执行系统 | dry-run、受限执行、审批门 | sandbox_executor |
| B9 | 执行追踪系统 | 记录每一步证据链 | execution_trace / trace_audit |
| B10 | 评估系统 | 成功率、质量、回归、RAG 评估 | eval_engine / rag_evaluator |
| B11 | 反馈学习系统 | anti-pattern、machine lesson、下次约束 | feedback_loop / machine_lesson |
| B12 | 模型路由系统 | 模型选择、限流、成本控制 | model_router |
| B13 | MCP 扩展系统 | 工具注册、schema、审计 | mcp server / registry |
| B14 | A-B 翻译系统 | 把人的学习信号转成机器任务信号 | a_to_b |

B 线阶段建议：

```text
先稳定 B1 + B2 + B3 + B7 + B9
再增强 B4 + B5 + B6 + B10 + B11
最后推进 B8 + B12 + B13 + B14
```

---

## 7. Obsidian 所属环节

Obsidian 只属于输入源层和 A1 捕获系统的一部分。

```text
Obsidian
  -> A1 捕获系统
  -> 部分 A2 知识结构前处理
  -> 可选 IR Research Note 来源
```

它可以参与：

| 环节 | 作用 |
|---|---|
| 资料捕获 | 笔记、网页、灵感、日志 |
| 人工整理 | MOC、标签、双链、Canvas |
| 候选筛选 | Properties / Bases 筛选导出候选 |
| 经验回流 | 保存项目复盘、lesson、想法 |

它不参与：

| 环节 | 原因 |
|---|---|
| KB 主数据库 | 缺少严格 schema、API、测试、审计 |
| IR 证据验证 | 私人笔记不等于可信证据 |
| Agent 执行 | 权限、安全、审计不足 |
| 最终合并判断 | 不是主项目 |

---

## 8. 治理系统拆分

为了最终能合并，必须先有治理层。

| 治理对象 | 规则 |
|---|---|
| 仓库边界 | IR 写研究，KB 写工程；不互相污染 |
| 数据边界 | 私人资料、密钥、合同、未授权材料不进入系统 |
| 证据边界 | 未验证论文不能变成产品结论 |
| 功能边界 | experimental 不写进 stable 承诺 |
| 执行边界 | 写入、删除、联网、跨盘、同步必须审批 |
| 合并边界 | 只有稳定、可追溯、可回滚的内容才考虑合并 |

---

## 9. 最终合并路径

最终合并不是现在的动作，而是成熟后的决策。

### 9.1 不合并，仅桥接

```text
IR 保持研究仓库
KB 保持工程仓库
通过 Intake Card / Engineering Contract / Release Note 桥接
```

适用：研究资产持续增长，工程需要保持干净。

### 9.2 文档部分合并

```text
IR 中成熟框架
  -> KB docs/reference 或 docs/research
```

适用：某些研究结论已变成 KB stable 功能依据。

### 9.3 能力合并

```text
IR Intake Card
  -> KB experimental
  -> KB stable
```

适用：具体功能已经在 KB 中实现并验证。

### 9.4 仓库级合并

最后选项。

只有在以下条件全部满足时考虑：

```text
IR 的研究资产已经稳定
KB 的工程结构已经清晰
文档、代码、测试、数据边界全部清楚
历史归档已处理
隐私和证据风险已清理
```

---

## 10. 当前优先级

### 第一优先级：口径统一

```text
明确 IR / KB / Obsidian 的边界
明确 stable / experimental / research / archive
明确 Obsidian 只是输入源之一
```

### 第二优先级：流程跑通

```text
Obsidian 或普通文档
  -> KB documents
  -> search
  -> cards
  -> reviews
  -> report
```

### 第三优先级：IR 到 KB 工程化

```text
IR Intake Card
  -> KB Engineering Contract
  -> KB experimental
  -> test
  -> stable
```

### 第四优先级：B 线机器任务闭环

```text
context_pack
  -> taskpack
  -> permission
  -> execution_trace
  -> eval
  -> machine_lesson
```

### 第五优先级：合并评估

```text
先桥接
再部分合并
最后才考虑仓库合并
```

---

## 11. 下一步文档建议

建议继续新增三份文档：

| 文档 | 目的 |
|---|---|
| `13_FLOW_OBSIDIAN_TO_KB.md` | 只定义 Obsidian 作为 KB 输入源的一条流程 |
| `14_IR_TO_KB_INTAKE_WORKFLOW.md` | 定义 IR 研究成果如何进入 KB |
| `15_KB_STABLE_EXPERIMENTAL_BOUNDARY.md` | 定义 KB 当前功能的稳定/实验边界 |

建议先写 `14_IR_TO_KB_INTAKE_WORKFLOW.md`，因为这是两个主项目之间最关键的桥。