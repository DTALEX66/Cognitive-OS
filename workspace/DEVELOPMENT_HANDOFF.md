# Cognitive-OS 跨设备开发交接计划

> 更新时间：2026-06-29
> 目标：把后续开发规划、环境要求、数据边界和启动步骤放进仓库，方便在另一台电脑继续开发。

## 1. 当前远端入口

| 项目 | 值 |
| --- | --- |
| GitHub 仓库 | `DTALEX66/Cognitive-OS` |
| 当前开发分支 | `codex/integrate-cognitive-runtime` |
| 推荐远端协议 | SSH：`git@github.com:DTALEX66/Cognitive-OS.git` |
| PR 创建页 | `https://github.com/DTALEX66/Cognitive-OS/pull/new/codex/integrate-cognitive-runtime` |

新电脑优先从该分支继续，不要直接在 `main` 上开发。

## 2. 新电脑启动步骤

```powershell
git clone git@github.com:DTALEX66/Cognitive-OS.git
cd Cognitive-OS
git switch codex/integrate-cognitive-runtime

python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt

.\scripts\setup_env.ps1
.\.venv\Scripts\python.exe scripts\doctor_environment.py --fix --check-files
.\.venv\Scripts\python.exe -m unittest discover -s tests
.\.venv\Scripts\python.exe -m compileall app tests scripts
```

如果新电脑还没有 GitHub SSH key，先完成 SSH key 配置，再运行：

```powershell
ssh -T git@github.com
```

看到 GitHub 识别到 `DTALEX66` 后再推送代码。

## 3. 环境硬规则

| 环节 | 规则 | 检查方式 |
| --- | --- | --- |
| Git remote | 使用 SSH，不走 HTTPS | `git remote -v` |
| Git 换行 | 仓库本地 `core.autocrlf=false`, `core.eol=lf` | `scripts/doctor_environment.py --fix` |
| 文本编码 | UTF-8，无 BOM，不接受乱码标记 | `python -m unittest tests.test_encoding_policy` |
| PowerShell 读文本 | 使用 `Get-Content -Encoding UTF8`，或先跑 `scripts/setup_env.ps1` | 读取 `workspace/NEXT_TASKS.md` 应显示正常中文 |
| 上传前检查 | 测试、编译、编码审计都要通过 | `unittest`, `compileall`, `doctor_environment.py --check-files` |

不要用 PowerShell 默认文本编码读写中文 Markdown；它可能把正常 UTF-8 显示成乱码，进而误改文件。

## 4. 数据边界

| 数据/目录 | 是否上传 | 说明 |
| --- | --- | --- |
| `workspace/imports/` | 已上传 | 精选后的参考资产，可供新电脑继续开发 |
| `workspace/local-imports/` | 不上传 | 本地快照目录，已被 Git 忽略 |
| `data/` | 不上传 | 运行记忆、日志、trace、工具输出都留本机 |
| `.venv/` | 不上传 | 新电脑自行创建 |
| `.env`, `.codex/`, SSH key, token | 禁止上传 | 私密配置只能留在本机 |

如果新电脑需要 `workspace/local-imports/` 的完整本地快照，必须单独走用户确认的安全迁移流程；不要为了方便把整个快照推到 GitHub。

## 5. 已完成能力

| 模块 | 当前状态 | 关键文件 |
| --- | --- | --- |
| API smoke test | 已建立 | `tests/test_api_smoke.py` |
| ContextPack | 已实现确定性评分 | `app/rag/context_engine.py`, `app/rag/retriever.py` |
| 内容质量判断 | 已接入摄入与路由 | `app/ingestion/quality.py`, `app/core/router.py` |
| Trace Audit | 已接入 eval | `app/evaluation/trace_audit.py`, `app/evaluation/evaluator.py` |
| MachineLesson | 已生成带证据 lesson | `app/evaluation/lesson_engine.py` |
| Tool Guard | 已接入工具注册表 | `app/tools/guard.py`, `app/tools/registry.py` |
| FSRS 卡片复习 | 已有 API 与 JSONL 存储 | `app/learning/fsrs.py`, `app/learning/cards.py`, `app/main.py` |
| 编码/上传护栏 | 已落地 | `tests/test_encoding_policy.py`, `scripts/setup_env.ps1`, `scripts/doctor_environment.py` |

## 6. 后续开发顺序

| 顺序 | 任务 | 目标文件 | 验收标准 |
| ---: | --- | --- | --- |
| 1 | Teach-back/Rubric | `app/learning/teach_back.py`, `app/learning/rubrics.py` | 可对学习卡片进行讲回、评分、薄弱点记录 |
| 2 | Obsidian 输入层 | `app/ingestion/obsidian.py` | 支持 frontmatter、wikilink、tag 的本地 Markdown 解析 |
| 3 | Web/URL 摄入策略 | `app/ingestion/web.py`, `app/core/policy.py` | URL 必须显式输入，禁止隐式抓取敏感内容 |
| 4 | OCR sidecar 契约 | `app/ingestion/ocr.py` 或 `sidecars/ocr_service/` | 先提供 mock 接口，模型和大依赖不进 Git |
| 5 | SQLite/FTS 存储 | `app/memory/sqlite_store.py` | JSONL 继续可用，SQLite 只写项目内临时测试库 |
| 6 | 前端/仪表盘评估 | 待定 | 后端 API 稳定后再决定是否启动 UI |

## 7. 每轮提交前检查

```powershell
.\scripts\setup_env.ps1
.\.venv\Scripts\python.exe scripts\doctor_environment.py --fix --check-files
.\.venv\Scripts\python.exe -m unittest discover -s tests
.\.venv\Scripts\python.exe -m compileall app tests scripts
git status --short
git diff --stat
```

暂存必须使用显式路径：

```powershell
git add -- path/to/file1 path/to/file2
```

不要使用：

```powershell
git add .
git push --force
```

## 8. 下一位开发者先读

1. `AGENTS.md`
2. `workspace/NEXT_TASKS.md`
3. `workspace/IMPORT_MANIFEST.md`
4. `workspace/DEVELOPMENT_HANDOFF.md`
5. `workspace/intake/008_external_project_integration_plan.md`

先确认环境绿灯，再继续实现下一项功能。
