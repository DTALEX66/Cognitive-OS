# Knowledge-Base 安装指南

## 方式一：本地开发（推荐快速体验）

### 环境要求
- Python 3.10+
- Node.js 20+
- npm 10+

### 安装步骤

```bash
# 1. 克隆
git clone https://github.com/DTALEX66/Knowledge-Base.git
cd Knowledge-Base/KnowledgeBase

# 2. 后端
cd backend
pip install -r requirements.txt
copy .env.example .env
set PYTHONPATH=.
uvicorn pk_radar.api:app --host 127.0.0.1 --port 8787 --reload
# 访问 http://127.0.0.1:8787/docs （Swagger UI）

# 3. 前端（新终端）
cd ../frontend
npm install
npm run dev
# 访问 http://localhost:3000
```

### 一键启动（Windows）
```bat
start.bat
```

## 方式二：Docker 部署（生产推荐）

### 环境要求
- Docker Engine 24+
- Docker Compose v2+

### 安装步骤

```bash
# 1. 克隆
git clone https://github.com/DTALEX66/Knowledge-Base.git
cd Knowledge-Base/KnowledgeBase

# 2. 配置环境变量
copy .env.example .env

# 3. 启动所有服务
docker compose up --build -d

# 4. 访问 http://localhost

# 查看日志
docker compose logs -f

# 停止
docker compose down
```

### 生产部署
```bash
docker compose -f docker-compose.yml -f docker/docker-compose.prod.yml up --build -d
```

## 方式三：Electron 桌面应用

```bash
cd KnowledgeBase/electron
npm install
npm start
```

## 初始化种子数据（可选）

启动后端后，首次访问会自动初始化示例文档。如需手动：

```bash
cd backend
set PYTHONPATH=.
python -c "from pk_radar.seed_data import seed_database; seed_database()"
```

## 验证安装

| 检查项 | 地址 |
|--------|------|
| 后端健康 | http://127.0.0.1:8787/health |
| API文档 | http://127.0.0.1:8787/docs |
| 前端页面 | http://localhost:3000 |
| Docker | http://localhost |
