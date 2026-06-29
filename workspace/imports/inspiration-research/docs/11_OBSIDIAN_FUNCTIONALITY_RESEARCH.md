# 11 Obsidian 功能性调研

> 日期：2026-06-29  
> 调研对象：Obsidian 桌面/移动端、核心插件、Web Clipper、Sync、Publish、插件生态  
> 资料来源：Obsidian 官方帮助文档与官方 GitHub 帮助仓库  
> 目的：判断 Obsidian 作为 `Inspiration-Research` 与 `Knowledge-Base` 前置项目的能力边界。

---

## 1. 总结判断

Obsidian 的核心价值不是数据库、不是自动化执行器，也不是严格的产品后端。它的核心价值是：

```text
本地 Markdown 文件
  + 双向链接
  + 属性 / frontmatter
  + 可视化关系
  + 人工整理工作流
  + 插件扩展
  + 多设备同步与发布能力
```

对于当前三层体系，Obsidian 最适合的位置是：

```text
Obsidian = 上游捕获与人工整理层
Inspiration-Research = 研究验证与框架层
Knowledge-Base = 工程运行与学习/Agent 流程层
```

也就是说，Obsidian 可以当“前置项目”，但不能直接替代 IR 或 KB。

---

## 2. 基础数据模型

官方文档说明，Obsidian 将笔记保存为 vault 中的 Markdown 纯文本文件；vault 本质上是本地文件夹，可以包含子文件夹。Obsidian 会维护本地元数据缓存，用于 Graph、Outline 等功能。

### 对我们的意义

| 能力 | 价值 |
|---|---|
| Markdown 纯文本 | 非锁定格式，适合导入 KB，也适合进入 IR 做框架整理 |
| 本地文件夹 vault | 能用文件系统、Git、同步盘、脚本做受控迁移 |
| `.obsidian/` 配置目录 | 插件、工作区、主题等配置必须单独处理，不能默认导入 |
| 元数据缓存 | Obsidian 内部体验用，不应作为 KB 数据来源 |

### 风险

```text
Markdown 文件可以导出
.obsidian 配置不能默认导出
IndexedDB / metadata cache 不应依赖
附件需要单独白名单
vault 内可能混有私人资料
```

---

## 3. 核心功能分类

### 3.1 捕获层

Obsidian 支持快速创建笔记、每日笔记、模板、Web Clipper、附件拖入等方式。

适合捕获：

```text
灵感
阅读摘录
网页剪藏
项目日志
学习笔记
AI 对话摘要
错误复盘
论文线索
功能想法
```

对我们最有价值的是：

| 功能 | 用法 |
|---|---|
| Daily notes | 记录当天工作、学习、AI 对话和反思 |
| Templates | 固化笔记格式，例如 Intake Candidate、Lesson、Source Note |
| Web Clipper | 把网页内容、高亮和结构化字段保存到 vault |
| Audio recorder | 临时语音记录，后续再整理成文字 |

### 3.2 连接层

Obsidian 的双向链接、Backlinks、Outgoing links、Graph view、Tags view 可以帮助形成知识网络。

适合做：

```text
主题索引
MOC / Map of Content
概念之间的弱连接
项目资料导航
长期思想沉淀
```

但要注意：

```text
双链表示“关联”，不表示“证据充分”
Graph 表示“连接密度”，不表示“重要性”
标签表示“人工分类”，不表示“稳定 schema”
```

### 3.3 结构化层

Obsidian 的 Properties 与 Bases 是最值得接入我们体系的功能。

Properties 可以给每个 Markdown 文件加结构化字段。  
Bases 可以基于 properties 创建类似数据库的视图，支持编辑、排序、筛选，并可用表格、列表、卡片、地图等视图展示。

这非常适合做 Obsidian -> IR / KB 的候选出口。

推荐用法：

```text
每条候选笔记都有 frontmatter
用 Bases 建一个 “KB Export Candidates” 视图
只筛选 candidate_for = kb / ir / both
只导出 privacy != private / sensitive
只导出 verification != raw 或明确标记 needs_check
```

### 3.4 可视化层

Canvas 是官方核心插件，用于二维空间中摆放和连接笔记、图片、附件、网页等内容；Canvas 文件保存为 `.canvas`，使用开放 JSON Canvas 格式。

适合做：

```text
框架草图
系统关系图
学习路线草案
项目概念地图
IR 设计前的头脑风暴
```

不适合直接做：

```text
KB 数据库 schema
可执行任务图
证据图谱
Agent 路由图
```

原因：Canvas 更接近人的可视化思考工具，机器可读性需要额外转换。

### 3.5 检索层

Obsidian 自带 Search、Quick switcher、Bookmarks、Outline、Properties view 等核心功能。

适合做：

```text
找旧笔记
找来源
找某个标签或属性
快速打开项目文件
人工检查候选导出集
```

但 KB 仍然需要自己的检索系统，因为 KB 要处理：

```text
FTS5 / API 搜索
学习卡片关联
复习调度
任务上下文打包
Agent 可审计引用
```

### 3.6 同步与发布层

Obsidian Sync 是官方付费同步服务，支持多设备同步、选择性同步、版本历史、共享 vault 等能力。官方也提醒，如果与 Dropbox、Google Drive、OneDrive 等云服务并用，要备份并注意同步冲突。

Obsidian Publish 是官方托管服务，可将选定笔记发布为网站、wiki、知识库、文档或 digital garden。

对我们的建议：

```text
Sync 用来同步 Obsidian 自身，不作为 KB 自动导入通道
Publish 只用于公开内容，不用于私有 KB 数据
跨电脑流转优先用“导出候选集”，不要全库同步
```

### 3.7 插件生态

Obsidian 有官方核心插件，也有社区插件。核心插件由 Obsidian 团队官方构建并支持，社区插件可以扩展功能。

适合后续考虑的插件类型：

```text
Git 插件
Dataview 类查询插件
Templater 类模板插件
Tasks 类任务插件
Importer
地图 / Canvas / Bases 扩展
```

风险：

```text
插件可能写入额外配置和缓存
社区插件质量不一
插件字段不一定是稳定 schema
不能把插件输出直接当作可信数据
```

---

## 4. 对 IR / KB 的功能映射

### 4.1 Obsidian -> IR

| Obsidian 功能 | IR 接收方式 |
|---|---|
| Markdown 笔记 | 转为 Research Note |
| Properties | 转为 Intake Card 字段 |
| Tags | 转为候选分类，不直接当证据 |
| Backlinks | 转为参考关系 |
| Canvas | 转为框架草图或系统图说明 |
| Web Clipper | 转为 Source Note，保留 URL 和摘录边界 |
| Daily notes | 转为 Lessons Learned 或项目日志 |

### 4.2 Obsidian -> KB

| Obsidian 功能 | KB 接收方式 |
|---|---|
| 普通 Markdown | 导入 documents |
| frontmatter | 映射 source、tags、privacy、verification、candidate_for |
| Web Clipper 内容 | 进入 sources / documents，保留来源 URL |
| Bases 候选视图 | 作为导出清单，不直接当数据库 |
| Canvas | 可作为附件或参考文档，不直接进任务图 |
| Daily notes | 可抽取复盘、错题、下一步行动 |

### 4.3 不建议直接接入的内容

```text
.obsidian/
插件配置
workspace.json
workspaces.json
IndexedDB
缓存文件
未筛选附件
私人日记
密钥、账号、合同、客户资料
未授权 PDF / 书籍全文
```

---

## 5. Obsidian 在完整流程中的角色

推荐闭环：

```text
1. Obsidian 捕获
2. 用 Properties 标注候选状态
3. 用 Bases 筛出导出候选
4. 人工确认隐私和来源
5. 导出 Markdown 候选集
6. IR 生成 Intake Card
7. KB 导入文档或建立 experimental 能力
8. KB 生成卡片 / 搜索索引 / taskpack
9. 使用结果回流为 Lesson / Project Log
10. 重要经验回到 Obsidian 或 IR
```

最小可跑通流程：

```text
Obsidian Markdown
  -> IR Intake Card
  -> KB Document
  -> KB Search
  -> KB Card
  -> KB Review
  -> Daily Report
```

增强流程：

```text
Obsidian Source Note
  -> IR Framework
  -> KB Context Pack
  -> TaskPack
  -> Execution Trace
  -> Machine Lesson
```

---

## 6. 推荐 Obsidian 功能组合

### 6.1 最小组合

```text
Markdown notes
Internal links
Tags
Properties
Templates
Search
Backlinks
```

用途：建立稳定、低风险的个人知识前置层。

### 6.2 结构化组合

```text
Properties
Bases
Templates
Properties view
Search property syntax
```

用途：做 IR / KB 候选导出管理。

### 6.3 研究组合

```text
Web Clipper
Highlighter
Reader
Templates
Source Notes
Canvas
MOC
```

用途：把网页、论文线索、灵感转成可验证研究材料。

### 6.4 项目管理组合

```text
Daily notes
Templates
Bases
Tags
Bookmarks
Workspaces
```

用途：跟踪项目状态、任务、待验证资料和经验教训。

---

## 7. 推荐 frontmatter 字段

```yaml
---
title: ""
created: "YYYY-MM-DD"
updated: "YYYY-MM-DD"
source_type: note | web | paper | book | conversation | project_log | lesson
source_url: ""
author: ""
candidate_for: ir | kb | both | none
privacy: public | internal | private | sensitive
verification: verified | needs_check | opinion | raw
status: inbox |整理中 | candidate | exported | archived
project: Knowledge-Base | Inspiration-Research | Obsidian-Upstream | other
topic: ""
tags:
  - kb-candidate
  - ir-candidate
---
```

字段原则：

```text
少而稳定
明确隐私
明确候选去向
明确验证状态
保留来源
```

---

## 8. 导出前检查清单

Obsidian 内容进入 IR / KB 前，先人工确认：

```text
是否有 privacy: private / sensitive
是否有 source_url 或来源说明
是否含账号、密钥、合同、个人聊天
是否含未授权全文材料
是否只是观点而不是事实
是否已经标注 candidate_for
是否需要进入 IR 验证
是否可以直接作为 KB 普通文档
```

不满足条件时，留在 Obsidian。

---

## 9. 结论

Obsidian 是非常适合作为前置项目的工具，原因是它天然满足四个条件：

```text
本地优先
Markdown 可迁移
人工整理体验强
可用 Properties / Bases 做半结构化出口
```

但它不应该承担以下职责：

```text
替代 KB 的数据库
替代 IR 的证据验证
替代 Agent 的执行审计
直接全库同步到工程系统
```

最佳定位：

```text
Obsidian = 个人知识生产与筛选台
IR = 研究框架与验证台
KB = 运行系统与任务执行台
```

---

## 10. 下一步建议

下一份文档建议改为：

```text
docs/12_OBSIDIAN_EXPORT_CONTRACT.md
```

它应定义：

```text
哪些标签可以导出
哪些 frontmatter 字段必须存在
哪些目录必须排除
附件如何白名单
Canvas 是否导出
Bases 视图如何作为导出清单
导出后如何映射到 IR Intake Card
导出后如何映射到 KB documents
```

只有导出契约稳定以后，再考虑写同步脚本或自动导入工具。

---

## 参考来源

- Obsidian Help: How Obsidian stores data  
  https://github.com/obsidianmd/obsidian-help/blob/master/en/Files%20and%20folders/How%20Obsidian%20stores%20data.md
- Obsidian Help: Core plugins  
  https://github.com/obsidianmd/obsidian-help/blob/master/en/Plugins/Core%20plugins.md
- Obsidian Help: Introduction to Bases  
  https://github.com/obsidianmd/obsidian-help/blob/master/en/Bases/Introduction%20to%20Bases.md
- Obsidian Help: Canvas  
  https://github.com/obsidianmd/obsidian-help/blob/master/en/Plugins/Canvas.md
- Obsidian Help: Properties view  
  https://github.com/obsidianmd/obsidian-help/blob/master/en/Plugins/Properties%20view.md
- Obsidian Help: Web Clipper  
  https://github.com/obsidianmd/obsidian-help/blob/master/en/Obsidian%20Web%20Clipper/Introduction%20to%20Obsidian%20Web%20Clipper.md
- Obsidian Help: Obsidian Sync  
  https://github.com/obsidianmd/obsidian-help/blob/master/en/Obsidian%20Sync/Introduction%20to%20Obsidian%20Sync.md
- Obsidian Help: Obsidian Publish  
  https://github.com/obsidianmd/obsidian-help/blob/master/en/Obsidian%20Publish/Introduction%20to%20Obsidian%20Publish.md