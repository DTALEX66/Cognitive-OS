# 03 DATABASE MVP — v0.2

## 数据库

SQLite 本地文件数据库，存放在 data/ 目录。

### 核心表

| 表 | 说明 |
|----|------|
| documents | 导入的文档 |
| cards | 学习卡片 |
| reviews | 复习记录 |
| mistakes | 错题记录 |
| sources | 来源信息 |
| tags | 标签 |

### 索引

- FTS5 全文搜索索引
- cards.due 日期索引
- documents.created_at 时间索引

### 迁移

数据库迁移文件在 backend/pk_radar/migrations/
