# 08 IR-KB 双线框架续写

> 日期：2026-06-29  
> 范围：`Inspiration-Research` + `Knowledge-Base`  
> 性质：全面分析、桥接框架、后续实施边界  
> 原则：IR 继续做研究与框架，KB 继续做工程实现；成熟成果通过明确门槛进入 KB。

---

## 1. 当前结论

两个仓库不是重复项目，而是同一系统的两条专线。

| 仓库 | 当前定位 | 主要资产 | 当前风险 |
|---|---|---|---|
| `Inspiration-Research` | 未来核心系统研究线 | A 线学习系统、B 线多 Agent、学习科学资料、桥接设计 | 研究资产很厚，但需要成熟度门槛，不能直接等同于可上线功能 |
| `Knowledge-Base` | 当前可运行工程线 | FastAPI 后端、SQLite 本地存储、Next.js 前端、A/B 实验实现、MCP 与 Agent 原型 | 实现面已经超过 MVP 文档口径，需要稳定层、实验层、路线层重新分层 |

当前最重要的工作不是继续堆模块，而是建立一套稳定的吸收框架：

```text
IR 产生研究结论
  -> 形成可审计设计卡
  -> 转换为 KB 工程合同
  -> 在 KB experimental 层实现
  -> 经过质量门后升入 stable 层
```

---

## 2. 双项目结构分析

### 2.1 Inspiration-Research

IR 是文档研究仓库，核心资产分布如下：

| 目录 | 角色 |
|---|---|
| `A-Line-Human-Learning-OS/` | 人类学习操作系统：捕获、诊断、规划、编码、反馈、训练、元认知、教学等设计 |
| `B-Line-Multi-Agent/` | 机器知识与 Agent 执行系统：协调、编排、并行、事件、权限、MCP 扩展 |
| `docs/` | 当前 MVP 口径、API、数据库、前端、测试、路线图、决策记录 |
| `reference/` | KB 分析、开源项目吸收计划、FSRS 与集成方案 |
| `dual-system-integration/` | A/B 线与 CC/CW 来源吸收映射 |
| `maps/MAPPING.md` | 双线优先级、迁移难度与阶段关系 |
| `IR-to-KB-Bridge.md` | IR 与 KB 的桥接声明 |

IR 的强项是体系化：它知道未来系统要长成什么样。IR 的弱项是验证压力：尤其学习科学论文与证据池必须保持真实性边界，未经验证的内容只能进入研究参考，不能进入产品承诺。

### 2.2 Knowledge-Base

KB 是工程仓库，当前已经具备可运行系统雏形：

| 层 | 当前状态 |
|---|---|
| 后端 | Python 3.10+、FastAPI、SQLite、FTS5、MCP、A/B 线实验模块 |
| 前端 | Next.js 16、React 19、TypeScript、Tailwind，页面数已经超过最小 MVP |
| 数据 | 本地优先，SQLite 文件数据库，强调可携带与低配置 |
| A 线实现 | `learning_final/` 中已有诊断、编码、教学、元认知、画像、巩固等模块 |
| B 线实现 | `b_line/` 中已有机器知识、上下文、路线、Agent 编排、沙箱、评估、反馈、追踪等模块 |
| MCP | 已有工具注册、权限、审计、服务器雏形 |

KB 的强项是已有运行面和模块骨架。KB 的弱项是口径不一致：文档中的 MVP 边界较窄，但实际路由与页面已经扩大；需要一个“稳定核心 / 实验吸收 / 未来路线”的治理框架。

---

## 3. 核心矛盾

### 3.1 文档成熟度与工程成熟度不一致

IR 有大量设计，KB 有大量实现，但两者之间缺少统一成熟度标尺。结果是：有些研究资产看起来完整，但还不能工程化；有些 KB 模块已经存在，但缺少明确验收标准。

### 3.2 MVP 口径与实际功能面不一致

当前 MVP 文档强调 6 个核心页面和 15 个核心端点，但 KB 后端和前端已经包含更多实验路由、实验页面和 Agent 能力。必须明确：

```text
stable = README 和用户可依赖能力
experimental = 代码存在但不承诺稳定
research = IR 中的设计、证据、路线和待验证方案
archive = 历史材料，不作为当前承诺
```

### 3.3 A/B 线需要接口，不需要混成一团

A 线关注人的学习闭环：资料、理解、记忆、练习、反馈、迁移。  
B 线关注机器任务闭环：上下文、任务包、工具、权限、执行、审计、反馈。

二者应通过明确接口协作：

```text
A -> B: 学习目标、知识卡、错题、用户偏好、可信材料
B -> A: 上下文包、任务路线、执行证据、失败模式、可复用经验
```

---

## 4. 新框架：IR-KB 四层吸收模型

### Layer 0: Evidence / Research

位置：IR  
目标：保证来源真实、结论可追溯、边界诚实。

准入标准：

- 论文、数据、案例必须标明来源与可信等级。
- 未验证论文不得进入 KB 产品承诺。
- 研究结论必须写明适用场景和不适用场景。

输出：

```text
Evidence Note
Research Summary
Risk Boundary
Reference Map
```

### Layer 1: Design / Spec

位置：IR  
目标：把研究结论变成可执行设计，而不是抽象愿景。

每个设计必须包含：

| 字段 | 说明 |
|---|---|
| Problem | 要解决什么真实问题 |
| User Loop | 用户如何感知这个能力 |
| Data Contract | 需要哪些数据结构 |
| API Contract | 需要哪些接口 |
| UI Contract | 需要哪些页面或组件 |
| Safety Boundary | 哪些操作必须审批或禁止 |
| Acceptance | 怎么判断完成 |

输出：

```text
Spec Card
Acceptance Checklist
Risk Register
```

### Layer 2: Engineering Contract

位置：KB 文档层  
目标：把 IR 设计翻译为 KB 工程任务。

工程合同必须回答：

```text
目标模块在哪里？
是 stable 还是 experimental？
需要新增表、接口、页面、测试吗？
是否破坏现有数据？
如何回滚？
最小验证命令是什么？
```

输出：

```text
Task Pack
Migration Plan
Test Plan
Rollback Plan
```

### Layer 3: Runtime / Product

位置：KB 代码层  
目标：实现、验证、收敛。

升级规则：

| 等级 | 含义 | 可见性 |
|---|---|---|
| R0 | 研究想法 | IR only |
| R1 | 设计完成 | IR docs |
| R2 | 工程合同完成 | KB docs / taskpack |
| R3 | experimental 实现 | KB experimental |
| R4 | stable 实现 | README / 用户可见 |

---

## 5. A 线框架续写

A 线不应一次性全部产品化。建议按学习闭环拆成三段。

### A-Core: 稳定学习闭环

优先收敛以下能力：

| 能力 | KB 对应 | 目标 |
|---|---|---|
| 文档捕获 | documents / upload / search | 用户能导入、检索、回看资料 |
| 学习卡片 | cards / reviews / FSRS | 用户能从资料生成可复习内容 |
| 错题反馈 | mistakes / feedback | 用户能记录错误并形成下一步行动 |
| 日报 | reports/daily | 用户知道今天学了什么、下一步做什么 |

稳定标准：

```text
有 API
有数据表
有前端入口
有测试
有导出或审计记录
```

### A-Enhance: 个性化增强

进入 experimental，不急于承诺稳定：

| 能力 | 价值 | 风险 |
|---|---|---|
| 认知负荷 | 控制学习难度 | 指标容易伪精确 |
| 记忆编码 | 提升记忆效率 | 不同材料差异大 |
| 费曼输出 | 检查理解 | 评分需要人工校准 |
| 学习画像 | 个性化推荐 | 数据不足时容易误判 |
| 元认知反思 | 强化自我调节 | 需要避免空泛建议 |

### A-Future: 高复杂系统

暂不进入 stable：

```text
知识宫殿 3D
主动训练 hooks
技能实战沙箱
跨系统迁移
完整治理系统
```

这些能力应先写成 IR 设计卡，再进入 KB experimental。

---

## 6. B 线框架续写

B 线应围绕“机器可执行任务闭环”收敛。

### B-Core: 机器任务最小闭环

```text
machine_knowledge
  -> context_pack
  -> taskpack
  -> route
  -> permission
  -> execution_trace
  -> eval_run
  -> machine_lesson
```

最小稳定目标：

| 阶段 | 输出 |
|---|---|
| 知识检索 | 可信上下文片段 + 来源 |
| 上下文包 | token 预算内的任务上下文 |
| 任务包 | 可交给 Codex / DEEP 的步骤、验收、回滚 |
| 权限门 | 工具、路径、网络、删除、写入范围 |
| 执行追踪 | 每一步证据链 |
| 评估反馈 | 成功经验与失败模式 |

### B-Enhance: Agent 能力升级

优先补三件事：

1. Agent 角色矩阵：角色、工具、权限、风险等级统一表。
2. Context Pack 评分：相关性、可信度、近期性、证据强度、token 成本。
3. 执行审计闭环：每次任务生成 trace，失败生成 machine_lesson。

### B-Future: 外部框架吸收

AutoGen、CrewAI、DSPy、Ragas、Langfuse、Mem0、E2B 等都不应直接重依赖导入。优先吸收模式，必要时通过 adapter 引入可选依赖。

---

## 7. IR -> KB Intake Card 模板

后续任何 IR 成果进入 KB 前，先写这张卡。

```md
# Intake Card: <能力名称>

## 1. 来源
- IR 文件：
- 参考论文 / 项目：
- 证据等级：S / A / B / C / D / 未验证

## 2. 问题
- 用户现在遇到什么问题：
- 不做会怎样：

## 3. 目标
- stable / experimental：
- 成功标准：

## 4. 工程合同
- 后端模块：
- 前端入口：
- 数据结构：
- API：
- 测试：

## 5. 风险
- 数据风险：
- 安全风险：
- 体验风险：
- 误导风险：

## 6. 验收
- 最小验证命令：
- 手工验证路径：
- 回滚方式：
```

---

## 8. 近期路线图

### Step 1: 统一口径

目标：把 KB 当前功能分成 stable / experimental / research / archive 四类。

输出：

```text
KB_CAPABILITY_MATRIX.md
```

### Step 2: 写第一批 Intake Card

优先选择三个最能形成闭环的能力：

| 能力 | 原因 |
|---|---|
| Context Pack 评分 | 直接提升机器任务质量 |
| Agent 角色矩阵 | 解决 B 线权限与分工混乱 |
| 错题 -> 下一步学习建议 | 连接 A 线反馈与用户行动 |

### Step 3: KB experimental 收敛

只做小步：一个能力一张卡、一个接口、一个测试、一个回滚路径。

### Step 4: stable 升级门

能力进入 stable 前必须满足：

```text
文档已同步
API 已稳定
UI 有入口
数据结构可迁移
测试通过
风险边界明确
回滚路径明确
```

---

## 9. 现在不做的事

为避免重复过去的大而全问题，当前阶段明确不做：

- 不把 IR 全量搬进 KB。
- 不直接把未验证论文变成产品结论。
- 不引入大型外部 Agent 框架作为核心依赖。
- 不把 experimental 页面写进稳定承诺。
- 不重构 KB 存储层，除非先有迁移计划和数据备份策略。
- 不扩大到 E 盘、用户资料盘、系统配置或全盘扫描。

---

## 10. 下一步建议

建议下一个文档是：

```text
docs/09_KB_CAPABILITY_MATRIX.md
```

内容：把 KB 当前所有能力按 stable / experimental / research / archive 归类，并标注：

```text
能力名称
当前入口
后端模块
前端页面
数据依赖
测试状态
IR 来源
下一步动作
```

这会让后续工程实现不再靠感觉推进，而是按能力矩阵逐项收敛。