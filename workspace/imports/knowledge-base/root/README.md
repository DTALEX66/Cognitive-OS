# Knowledge-Base

本地优先的个人知识库管理工具，集成 FSRS 间隔重复、全文搜索、网页抓取等功能。

[![Backend](https://img.shields.io/badge/Python-3.10%2B-blue)](https://python.org)
[![Frontend](https://img.shields.io/badge/Next.js-16-black)](https://nextjs.org)
[![License](https://img.shields.io/badge/license-MIT-green)](LICENSE)

---

## 开发专线说明

本仓库与 [Inspiration-Research](https://github.com/DTALEX66/Inspiration-Research) 为两条并行开发专线：

| 专线 | 仓库 | 定位 |
|------|------|------|
| **当前专线** | Knowledge-Base | 实用工具层 — 可运行的个人知识库，专注功能完整性和用户体验 |
| **未来核心** | [Inspiration-Research](https://github.com/DTALEX66/Inspiration-Research) | 未来核心系统研究 — 双系统架构设计、学习科学、多 Agent 协同原型 |

两条专线独立迭代，Inspiration-Research 的研究成果成熟后会逐步集成进 Knowledge-Base。

---

## 快速开始

```bash
# 克隆
git clone https://github.com/DTALEX66/Knowledge-Base.git
cd Knowledge-Base/KnowledgeBase

# 后端
cd backend
pip install -r requirements.txt
set PYTHONPATH=.
uvicorn pk_radar.api:app --host 127.0.0.1 --port 8787 --reload

# 前端（新终端）
cd frontend
npm install
npm run dev      # http://localhost:3000
```

### 一键启动
双击 `start.bat` 或运行 `powershell -File KnowledgeBase/start_all.ps1`

### Docker
```bash
docker compose up -d
```

---

## 功能

| 路由 | 页面 |
|------|------|
| `/` | 仪表盘 |
| `/upload` | 上传文档 |
| `/knowledge` | 知识浏览 |
| `/search` | 全文搜索 |
| `/review` | 间隔复习 |
| `/routes` | 学习路线 |
| `/agent` | 智能体 |
| `/sync` | 同步/导出 |
| `/skills` | 技能练习 |
| `/teach` | 费曼教学 |
| `/palace` | 记忆宫殿 |
| `/settings` | 设置 |
| `/training` | 训练 |
| `/diagnostics` | 诊断 |
| `/profile` | 个人资料 |
| `/consolidation` | 合并整理 |
| `/report` | 报告 |
| `/community` | 社区 |

---

## 项目结构

```
KnowledgeBase/
├── backend/pk_radar/     # Python 后端 (FastAPI)
│   ├── core/             # 存储、FSRS、搜索
│   ├── b_line/           # 智能体系统
│   ├── mcp/              # MCP 工具
│   ├── auth/             # 认证
│   ├── adapters/         # 外部适配器
│   └── learning_final/   # 学习引擎
├── frontend/             # Next.js 前端
│   ├── app/              # 18 个页面
│   └── components/       # UI 组件
├── data/                 # 数据存储
└── docs/                 # 文档
```

## 技术栈

- **后端**: Python 3.10+, FastAPI, SQLite FTS5
- **前端**: Next.js 16, React 19, TypeScript, Tailwind CSS 4
- **复习算法**: FSRS 间隔重复
- **抓取**: Playwright, httpx, 支持 80+ 平台
- **桌面**: Electron
- **浏览器**: Chrome 扩展 (Manifest V3)

## 关联仓库

| 仓库 | 说明 |
|------|------|
| [Inspiration-Research](https://github.com/DTALEX66/Inspiration-Research) | 未来核心系统研发专线 |
| [Skill-Integration](https://github.com/DTALEX66/Skill-Integration) | Codex 技能集成 |
| [AI-Enhancement-Package](https://github.com/DTALEX66/AI-Enhancement-Package) | Codex 增强包 |

## 许可证

MIT
