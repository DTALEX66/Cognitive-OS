# Knowledge-Base 项目文件索引 (FILE_INDEX)

> v3.2 | 2026-06-23 | Agent-5 审计生成
> 列出项目所有重要文件的用途说明

---

## 根目录

| 文件 | 用途 |
|------|------|
| README.md | 项目主自述文件，包含快速开始、架构概览 |
| PROJECT_STATUS.md | 项目进度状态、测试覆盖、后续任务 |
| PROJECT_MANIFEST.json | 项目清单配置 |
| AGENTS.md | AI编码Agent行为规则（部分引用过期） |
| STANDARDS_INDEX.md | 标准文档导航索引（→ docs/STANDARDS_INDEX.md） |
| .gitignore | Git忽略规则 |
| .editorconfig | 编辑器配置 |
| .env.example | 环境变量示例 |
| .dockerignore | Docker构建忽略 |
| docker-compose.yml | Docker编排配置 |
| THIRD_PARTY_NOTICES.md | 第三方依赖声明 |

## backend/ — Python后端

| 路径 | 用途 |
|------|------|
| backend/pk_radar/ai/ | AI学习引擎（元认知/知识图谱） |
| backend/pk_radar/b_line/ | B线：行为评估/回流/路线优化 |
| backend/pk_radar/core/ | 核心：存储/迁移/进化引擎 |
| backend/pk_radar/learning_final/ | A线：认知负荷/编码/技能/费曼/巩固/策略/诊断/元认知/画像 |
| backend/pk_radar/mcp/ | MCP工具服务器（40+工具） |
| backend/pk_radar/search/ | FTS全文搜索 |
| backend/pk_radar/security/ | 安全防护 |
| backend/pk_radar/api.py | FastAPI路由（88条） |
| backend/pk_radar/adapters/ | 外部适配器（爬虫/转换器） |
| backend/tests/ | pytest测试（22文件/204测试） |
| backend/seed_real_data.py | 种子数据脚本 |
| backend/requirements.txt | Python依赖 |

## frontend/ — Next.js前端

| 路径 | 用途 |
|------|------|
| frontend/app/diagnostics/ | A线学习诊断页面 |
| frontend/app/skills/ | A线技能任务页面 |
| frontend/app/teach/ | A线费曼输出页面 |
| frontend/app/profile/ | A线学习者画像页面 |
| frontend/app/consolidation/ | A线长期巩固页面 |
| frontend/app/review/ | 间隔复习页面 |
| frontend/app/knowledge/ | 知识浏览页面 |

## docs/ — 文档

| 路径 | 用途 |
|------|------|
| docs/STANDARDS_INDEX.md | 标准文档总索引 |
| docs/FILE_INDEX.md | 本文件 - 项目文件索引 |
| docs/architecture/00_PROJECT_SPEC_INDEX.md | 项目规格文档导航 |
| docs/architecture/DUAL_LINE_INTEGRATION.md | A线↔B线双线集成方案 |
| docs/architecture/TECH_STACK_FULL.md | 完整技术清单（A线16系统+B线10层） |
| docs/architecture/ai/ | AI/记忆/知识规范 |
| docs/architecture/brand/ | 品牌执行指南 |
| docs/architecture/community/ | 社区路由信任规范 |
| docs/architecture/content/ | 文案/国际化指南 |
| docs/architecture/data/ | 数据库模式/路由包规范 |
| docs/architecture/design/ | UI设计系统/参考/清单 |
| docs/architecture/engineering/ | 工程护栏/编码标准/质量门 |
| docs/architecture/planning/ | (已归档至 frozen/planning-archive/) |
| docs/architecture/product/ | 产品需求/商业化/验收 |
| docs/architecture/qa/ | QA测试策略 |
| docs/architecture/references/ | 架构参考资料 |
| docs/architecture/release/ | 发布门控模板（历史版本说明已归档至 frozen/docs-release/） |
| docs/architecture/security/ | 安全/隐私/合规 |
| docs/architecture/testing/ | 测试计划（历史日志/报告已归档至 frozen/docs-testing/） |
| docs/deep-plan/ | 深度并行开发计划 |
| docs/projects/ | 项目分析/设计文档 |
| docs/research/ | 研究文档（01-18系列） |
| docs/api/ | API文档/OpenAPI规范 |
| docs/api/openapi.json | OpenAPI 3.0规范 |

## reference/ — 参考项目

| 路径 | 用途 |
|------|------|
| reference/GITHUB_REFERENCE_PROJECTS.md | 48个开源项目对标分析 |
| reference/A线分析提取报告.md | A线16系统算法/数据模型提取 |
| reference/B线分析提取报告.md | B线11层架构/评分算法提取 |
| reference/FSRS集成方案.md | PyO3/ORM/DTO集成代码方案 |
| reference/ANALYSIS.md | 分析总报告 |
| reference/EXTRACTION.md | 提取说明 |
| reference/A线极限增强包_vFinal/ | A线参考源包 |
| reference/B线线路最终合集包/ | B线参考源包 |
| reference/extracted/ | 提取的开源项目（autogen/mem0/py-fsrs） |
| reference/fsrs_python_system/ | FSRS Python参考实现 |
| reference/rs-fsrs-python/ | FSRS Rust绑定参考 |

## scripts/ — 脚本

| 路径 | 用途 |
|------|------|
| scripts/deploy.ps1 | 部署脚本 |
| scripts/e2e-test.ps1 | E2E端到端测试 |
| scripts/http-smoke-test.py | HTTP烟雾测试 |
| scripts/install.ps1 | 安装脚本 |
| scripts/install-agents.ps1 | Agent安装（PS） |
| scripts/install-agents.sh | Agent安装（Shell） |
| scripts/run-dev.ps1 | 开发环境启动 |
| scripts/run-ui.ps1 | UI启动 |
| scripts/test-full.ps1 | 全量测试 |
| scripts/validate-data.py | 数据验证 |
| scripts/windows/verify_p0.ps1 | P0优先级验证 |

## data/ — 数据

| 路径 | 用途 |
|------|------|
| data/*.db | SQLite数据库文件 |
| data/automation/ | 自动化运行状态/任务 |

## docker/ — Docker部署

| 路径 | 用途 |
|------|------|
| docker/backend.Dockerfile | 后端镜像 |
| docker/frontend.Dockerfile | 前端镜像 |
| docker/nginx.conf | Nginx配置 |

## .github/ — CI/CD

| 路径 | 用途 |
|------|------|
| .github/workflows/build.yml | 构建工作流 |
| .github/workflows/ci.yml | 持续集成 |
| .github/workflows/preflight.yml | 预检工作流 |
| .github/workflows/python-security.yml | Python安全检查 |
| .github/workflows/security.yml | 综合安全检查 |

## outputs/ — 输出产物

| 路径 | 用途 |
|------|------|
| outputs/CHATGPT_TECH_SUMMARY.md | 提交ChatGPT的技术清单摘要 |

---

> **审计说明 (2026-06-23)**: 已删除 docs/references/ 下96个AI生成的ref_*.md空壳文件（被.gitignore排除）。已删除 docs/agents/ 下2个空壳文件和 agents/ 下5个空目录。
