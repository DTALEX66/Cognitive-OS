# 01 ARCHITECTURE MVP — v0.2

## 系统架构

### 三层结构

| 层 | 说明 |
|---|------|
| backend/ | Python FastAPI + SQLite |
| frontend/ | Next.js 16 + React 19 |
| data/ | 本地 SQLite 数据库 |

### 后端模块

- pk_radar/api.py — 主 API 路由
- pk_radar/core/ — 核心存储、搜索、配置
- pk_radar/mcp/ — MCP 工具服务器
- pk_radar/learning_final/ — A线学习模块(experimental)
- pk_radar/b_line/ — B线机器模块(experimental)

### 前端页面

MVP 核心(6页): dashboard, upload, knowledge, search, review, settings
实验层(9页): community, consolidation, diagnostics, palace, profile, report, routes, skills, teach, training

### 数据流

导入 -> 清洗 -> SQLite存储 -> FTS5索引 -> 搜索/卡片/复习 -> 日报导出
