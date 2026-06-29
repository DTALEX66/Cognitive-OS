# Knowledge-Base

本地优先的个人知识库管理工具。

## 快速开始

```bash
cd backend
pip install -r requirements.txt
set PYTHONPATH=.
uvicorn pk_radar.api:app --host 127.0.0.1 --port 8787 --reload

# 新终端
cd frontend
npm install
npm run dev
```

或一键启动：`start.bat`

## 项目结构

```
backend/pk_radar/core/        # 存储、FSRS、搜索
backend/pk_radar/learning_final/  # A 线学习模块 (29)
backend/pk_radar/b_line/      # B 线智能体模块 (22)
backend/pk_radar/mcp/         # MCP 工具
backend/pk_radar/adapters/    # 适配器 (6类)
frontend/app/                 # 18 个页面
frontend/components/          # 31 个组件
agents/                       # 智能体定义
frozen/                       # 归档参考
```

## API

- Health: `http://127.0.0.1:8787/health`
- Swagger: `http://127.0.0.1:8787/docs`
- Routes: 121

## 外部依赖

- [Skill-Integration](https://github.com/DTALEX66/Skill-Integration)
- [AI-Enhancement-Package](https://github.com/DTALEX66/AI-Enhancement-Package)
- [Inspiration-Research](https://github.com/DTALEX66/Inspiration-Research)
