# 02 API MVP — v0.2

## MVP 端点 (15个)

### 知识库核心
| 方法 | 路径 | 说明 |
|------|------|------|
| POST | /documents | 导入文档 |
| GET | /documents | 列出文档 |
| GET | /documents/{doc_id} | 获取文档 |
| DELETE | /documents/{doc_id} | 删除文档 |
| GET | /search | 全文搜索 |
| GET | /sources | 列出来源 |
| GET | /tags | 列出标签 |

### 学习闭环
| 方法 | 路径 | 说明 |
|------|------|------|
| POST | /cards | 创建卡片 |
| GET | /cards | 列出卡片 |
| GET | /cards/due | 待复习卡片 |
| POST | /cards/{card_id}/review | 提交复习 |
| GET | /cards/mistakes | 错题列表 |
| GET | /reports/daily | 日报 |

### 机器辅助
| 方法 | 路径 | 说明 |
|------|------|------|
| POST | /machine/context-pack | 生成上下文包 |
| POST | /machine/taskpack | 生成任务包 |
| GET | /traces | 证据链 |

## 实验层端点 (70+)
见 backend/pk_radar/api.py 完整路由表
