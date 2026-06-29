# 10 Obsidian 前置知识库层

> 日期：2026-06-29  
> 范围：另一台电脑上的 Obsidian 知识库、Inspiration-Research、Knowledge-Base  
> 定位：Obsidian 作为个人知识捕获与人工整理前置层，IR 作为研究与框架层，KB 作为工程运行层。  
> 原则：不直接合并资料库，不跳过验证，不把私人笔记直接产品化。

---

## 1. 核心判断

另一台电脑上的 Obsidian 知识库可以成为 IR 与 KB 的前置项目，但它不应直接替代 IR 或 KB。

正确关系是：

```text
Obsidian Vault
  -> Capture / Personal Notes / Raw Knowledge
  -> Inspiration-Research
  -> Research / Framework / Intake Cards
  -> Knowledge-Base
  -> Product / Runtime / Review / Search / Agent Task Flow
```

Obsidian 负责“先收住、先想清楚”。  
IR 负责“验证、抽象、设计”。  
KB 负责“运行、检索、复习、任务化”。

---

## 2. 三层定位

| 层 | 项目 | 核心问题 | 输出 |
|---|---|---|---|
| 前置层 | Obsidian | 我有什么材料、灵感、笔记、长期想法？ | 原始笔记、主题页、链接图谱、人工整理成果 |
| 研究层 | Inspiration-Research | 哪些内容值得变成框架、规范、路线、证据？ | 框架文档、Intake Card、证据分级、设计规格 |
| 运行层 | Knowledge-Base | 哪些内容能进入日常使用和机器任务流程？ | 文档库、搜索、卡片、复习、任务包、执行追踪 |

---

## 3. Obsidian 适合做什么

### 3.1 捕获

Obsidian 适合作为低摩擦入口：

```text
临时想法
阅读摘录
项目日志
会议记录
AI 对话摘录
论文线索
功能想法
错误复盘
个人偏好
```

### 3.2 人工整理

Obsidian 的优势是人脑驱动的连接：

```text
双链
标签
MOC / Index Note
Canvas
主题页
每日笔记
手动归纳
```

### 3.3 早期孵化

任何还没有验证、还没有工程价值、还没有清晰边界的东西，都应先留在 Obsidian。

---

## 4. Obsidian 不适合直接做什么

Obsidian 不应直接承担以下职责：

| 不建议 | 原因 |
|---|---|
| 直接作为 KB 数据库 | 缺少严格 schema、API、测试与审计 |
| 直接成为 IR 证据库 | 私人笔记常混有猜测、摘录、灵感，不能等同证据 |
| 直接喂给 Agent 执行 | 可能包含隐私、错误、过期材料、未验证结论 |
| 直接同步全库 | 附件、插件、隐藏目录、私人内容可能混入 |
| 直接把双链当知识图谱 | 双链表示关联，不等于因果、证据或可靠性 |

---

## 5. 推荐流转流程

### Stage 0: Vault 内整理

在 Obsidian 内先做最小整理：

```text
Inbox
  -> Topic Note
  -> MOC / Index
  -> Evidence / Source
  -> Candidate Export
```

建议标签：

```text
#kb-candidate
#ir-candidate
#needs-verification
#private
#source
#project-log
#lesson-learned
#task-idea
```

### Stage 1: 选择性导出

只导出被标记的候选内容，不导出整个 vault。

导出范围建议：

```text
只导出 #ir-candidate / #kb-candidate
不导出 #private
不导出 .obsidian/
不导出插件目录
不导出未清理附件
不导出账户、密钥、合同、个人隐私材料
```

### Stage 2: 进入 IR

进入 IR 前先做转换：

```text
Obsidian Note
  -> Research Note
  -> Evidence Boundary
  -> Intake Card
```

IR 只接收：

```text
框架想法
研究问题
证据线索
产品需求
架构草案
经验教训
```

IR 不接收未经处理的私人流水账。

### Stage 3: 进入 KB

只有通过 IR Intake Card 的内容，才进入 KB。

```text
Intake Card
  -> KB Engineering Contract
  -> experimental implementation
  -> test / validation
  -> stable promotion
```

---

## 6. Obsidian Note 标准格式

建议未来在 Obsidian 里对候选笔记使用统一 frontmatter。

```yaml
---
title: ""
created: "YYYY-MM-DD"
source_type: note | book | paper | web | conversation | project_log
candidate_for: ir | kb | both | none
privacy: public | internal | private | sensitive
verification: verified | needs_check | opinion | raw
related_project: Knowledge-Base | Inspiration-Research | other
tags:
  - kb-candidate
  - needs-verification
---
```

正文建议：

```md
## 摘要

## 来源

## 我的理解

## 可复用结论

## 风险 / 未验证点

## 适合进入哪里
- IR：
- KB：

## 下一步
```

---

## 7. IR 接收规则

Obsidian 内容进入 IR 时，必须按类型处理。

| Obsidian 内容 | IR 处理方式 |
|---|---|
| 灵感 | 进入框架草案，不直接变成结论 |
| 阅读摘录 | 标来源，写 Evidence Boundary |
| 论文线索 | 按铁律验证，不验证不入证据池 |
| 项目经验 | 进入 Lessons Learned 或 Intake Card |
| 功能想法 | 转成 Problem / User Loop / Acceptance |
| AI 对话 | 只能作为思路，不作为事实来源 |

---

## 8. KB 接收规则

Obsidian 内容不能绕过 IR 直接进入 KB stable。

允许直接进入 KB 的只有低风险资料类内容：

```text
用户明确选择导入的普通 markdown 文档
不含隐私
不含密钥
不含未授权材料
不作为产品结论
```

需要经过 IR 的内容：

```text
学习科学结论
架构设计
Agent 行为规则
权限策略
模型评估方法
产品路线
商业化判断
```

---

## 9. 全流程跑通定义

“全部流程跑通”不是指把 Obsidian 全库复制到 KB，而是跑通以下闭环：

```text
1. Obsidian 捕获一条真实想法或资料
2. 在 Obsidian 标记为候选
3. 导出为干净 Markdown
4. IR 接收并生成 Intake Card
5. KB 根据 Intake Card 建立实验能力或导入资料
6. KB 生成卡片 / 搜索索引 / 任务包
7. 用户复习、检索或让 Agent 使用
8. 执行结果回写为经验教训
9. 经验教训回到 Obsidian 或 IR
```

最小闭环：

```text
Obsidian note
  -> IR Intake Card
  -> KB document
  -> KB card/review
  -> daily report
  -> lesson learned
```

增强闭环：

```text
Obsidian note
  -> IR framework
  -> KB context pack
  -> taskpack
  -> execution trace
  -> machine lesson
  -> Obsidian/IR 复盘
```

---

## 10. 安全边界

另一台电脑上的 Obsidian vault 可能包含私人资料，默认按敏感源处理。

禁止自动处理：

```text
整个 vault 批量同步
.obsidian/ 配置目录
插件目录
附件目录全量上传
含密钥、账户、合同、私人聊天的笔记
未授权 PDF / 图片 / 书籍全文
```

任何跨电脑同步前必须先明确：

```text
同步方式
同步目录
排除规则
隐私标签
回滚方式
冲突处理
```

---

## 11. 建议目录关系

推荐概念结构：

```text
Obsidian Vault
  00_Inbox/
  10_Projects/
  20_Research/
  30_Knowledge/
  40_Lessons/
  90_Export/

Inspiration-Research
  docs/
  A-Line-Human-Learning-OS/
  B-Line-Multi-Agent/
  reference/

Knowledge-Base
  KnowledgeBase/backend/
  KnowledgeBase/frontend/
  KnowledgeBase/data/
```

`90_Export/` 可以作为候选导出区，但不应自动包含全部笔记。

---

## 12. 下一步

建议先写一个 Obsidian 导出契约，而不是马上写同步脚本。

下一份文档建议：

```text
docs/11_OBSIDIAN_EXPORT_CONTRACT.md
```

内容包括：

```text
导出标签
frontmatter 字段
隐私过滤
附件规则
文件命名
IR Intake Card 映射
KB 导入映射
手动验收清单
```

只有这个契约稳定后，再考虑同步工具或导入脚本。