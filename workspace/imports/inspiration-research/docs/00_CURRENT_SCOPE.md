# 00 CURRENT SCOPE — v0.2 MVP

## 当前项目范围

```
Knowledge-Base = Local-first Personal Knowledge Base
              + Lightweight Learning Loop
              + Lightweight Machine Task Assistant
```

## 层级划分

### Layer 1: core_mvp (当前主线)

```
documents   → 导入、清洗、存储
search      → SQLite FTS5 全文搜索
cards       → 创建、管理学习卡片
reviews     → FSRS 间隔复习
mistakes    → 错题记录与追踪
daily       → 学习日报与导出
context     → 生成 Codex/DEEP 上下文包
taskpack    → 生成任务拆解包
trace       → 证据链追踪
```

### Layer 2: experimental (实验层)

保留代码，不在 README 承诺稳定：

```
cognitive_load, memory_encoding, skill_tasks
feynman_output, learning_profile, long_term_consolidation
knowledge_palace, agent_executor, a_to_b_translator
multi_agent, sandbox_execution
```

### Layer 3: roadmap (未来路线)

见 [06_ROADMAP.md](06_ROADMAP.md)

### Layer 4: archive (历史归档)

见 `frozen/` 和 `reference/archive/`

## API 边界 (MVP)

```
POST   /documents
GET    /documents
GET    /documents/{id}
GET    /search
POST   /cards
GET    /cards
GET    /cards/due
POST   /reviews
POST   /mistakes
GET    /reports/daily
POST   /machine/context-pack
POST   /machine/taskpack
GET    /traces
```

## MCP 工具 (MVP — 8核心)

```
health.check
documents.search
documents.get
cards.create
cards.due
reviews.submit
context_pack.build
taskpack.generate
```

## 前端页面 (MVP — 6核心)

```
/               dashboard
/upload         文档上传
/knowledge      知识浏览
/search         全文搜索
/review         间隔复习
/settings       设置
```
