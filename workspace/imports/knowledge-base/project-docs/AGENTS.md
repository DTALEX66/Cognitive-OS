# AGENTS.md — Knowledge-Base 项目规范

## 0. 写入代码前必须做

```powershell
python scripts\health_check.py
```

失败就停，修好了再写代码。

## 1. 代码规范

- **不要 AI 化代码**。变量名用自然语言（`user_count` 不是 `uc`），函数名用动词开头，注释写"为什么"不是"是什么"。
- **不写模板注释**。`# ==== Section ====` 这类格式化分隔线不要出现，代码自己就是文档。
- **文件编码**：所有文件统一 UTF-8，不带 BOM。.py / .json 禁止手工在 PowerShell 里写，用 Python 写。
- **导入安全**：`__init__.py` 禁止链式 import。任何 import 失败不能崩溃整个包，用 try/except 或惰性加载。

## 2. Git 规范

- `git status` 检查有什么文件要提交。`.gitignore` 必须覆盖所有生成文件路径。
- `.gitignore` 用目录阻断 + 文件名模式双保险。新加的生成文件第一时间加 ignore。
- 远程用 SSH，不用 HTTPS。新机器第一件事：`git remote set-url origin git@github.com:DTALEX66/Knowledge-Base.git`

## 3. 前端规范

- `tsconfig.json` 的 `include` 禁止用 `**/*.tsx`，必须精确到子目录。
- 新页面必须确保所有 import 的目标文件存在。缺组件就先建桩。
- 构建命令 `npm run build`，确保通过再推送。

## 4. 错误不重犯

每次遇到问题，写入 `docs/LESSONS_LEARNED.md`。规则总结：

| # | 原则 |
|---|------|
| 1 | .py 文件只用 Python 写，不用 PowerShell |
| 2 | 配置文件写的时候控制 BOM |
| 3 | __init__.py 禁止链式 import |
| 4 | .gitignore 目录 + 文件模式双层阻断 |
| 5 | tsconfig include 精确目录 |
| 6 | 新增组件先建桩，不留断链 |
| 7 | commit 前先 git status |
| 8 | 构建前跑 health_check.py |
| 9 | Git 远程用 SSH |
| 10 | 错误记入 LESSONS_LEARNED.md |




---

## Project Scope (v0.2 MVP)

Current: Local-first knowledge base + lightweight learning loop + lightweight machine task assistant.

- README.md, PROJECT_STATUS.md, docs/00_CURRENT_SCOPE.md define scope
- docs/06_ROADMAP.md defines future
- frozen/ stores historical docs
- Experimental code stays in backend/pk_radar/experimental/

## Codex Skills

Skills live in Codex (~/.codex/skills/), source at [Skill-Integration](https://github.com/DTALEX66/Skill-Integration).

| Skill | Trigger |
|-------|---------|
| code-guardian | quality gate, code review, AI pattern detection |
| swarm-dev | multi-agent, parallel, task decomposition |
| agent-os | auto-loop, TDD, memory, context pack |
| fast-safe-coder | quick fix, small patch |

### Quick Commands
`
python ~/.codex/skills/code-guardian/scripts/pipeline.py --all
python ~/.codex/skills/code-guardian/scripts/project_guard.py --root . --fail-on error
python ~/.codex/skills/agent-os/scripts/context_pack_builder.py --root . --out outputs/context_pack.md
`
