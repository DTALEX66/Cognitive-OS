# Cognitive-OS 后续任务清单

> 更新时间：2026-06-29
> 当前原则：先稳住最小闭环，再逐步并入 `D:\Project Directory` 中已经保存到本项目本地快照的可用能力。

## 1. 总优先级

| 优先级 | 任务 | 目标文件/目录 | 来源参考 | 验收标准 |
| --- | --- | --- | --- | --- |
| P0 | 固化数据边界规范 | `AGENTS.md`, `config/*.yaml`, `workspace/NEXT_TASKS.md` | 当前用户要求 | 明确数据放置位置、禁止外溢、禁止乱复制 |
| P0 | 保持当前测试绿灯 | `tests/` | 当前新增测试 | `python -m unittest discover -s tests` 通过 |
| P1 | 增加 API smoke test | `tests/test_api_smoke.py` | 当前 FastAPI app | 覆盖 `/health`, `/route`, `/run`, `/tools`, `/memory/search` |
| P1 | 强化 ContextPack 评分 | `app/rag/context_engine.py`, `app/rag/retriever.py` | `knowledge-base/pk_radar/b_line/context_engine.py` | 中英文记忆检索有解释性评分 |
| P1 | 增加内容质量判断 | `app/ingestion/quality.py` | `knowledge-base/pk_radar/core/quality.py`, `cleaner.py` | 空内容、噪声、低质量文本可解释地 DROP/REVIEW |
| P2 | 并入 Trace Audit | `app/evaluation/trace_audit.py` | `knowledge-base/pk_radar/b_line/trace_audit.py` | 能识别成功、失败、blocked、缺证据 trace |
| P2 | 强化 MachineLesson | `app/evaluation/lesson_engine.py`, `app/evaluation/feedback.py` | `knowledge-base/pk_radar/b_line/machine_lesson.py` | lesson 不再只有泛泛文本，有类型、证据、下一步约束 |
| P3 | 强化工具安全门 | `app/tools/guard.py`, `app/tools/registry.py` | `knowledge-base/pk_radar/b_line/mcp_guard.py`, `sandbox_executor.py` | 中高风险工具 dry-run/blocked，路径越界被拒绝 |
| P4 | 加入 FSRS 复习模型 | `app/learning/fsrs.py`, `app/learning/cards.py` | `knowledge-base/pk_radar/core/fsrs5.py` | KB 文档可生成卡片，复习评分可更新 due time |
| P4 | 加入 Teach-back/Rubric | `app/learning/teach_back.py`, `app/learning/rubrics.py` | `knowledge-base/teach_back.py`, `rubrics.py` | 支持讲回、评分、薄弱点记录 |
| P5 | Obsidian 输入层 | `app/ingestion/obsidian.py` | `obsidian-skills` | 支持 frontmatter、wikilink、tag、canvas 参考 |
| P5 | Web/URL 摄入策略 | `app/ingestion/web.py`, `app/core/policy.py` | `knowledge-base/pk_radar/core/policy.py` | 默认本地优先，URL 校验，禁止隐式抓取敏感内容 |
| P6 | OCR sidecar 契约 | `app/ingestion/ocr.py` 或 `sidecars/ocr_service` | `screen-translation-assistant/sidecars/ocr_service` | 先 mock，后可选本地 OCR，模型和依赖不进 Git |
| P7 | SQLite/FTS 存储 | `app/memory/sqlite_store.py` | `knowledge-base/pk_radar/core/store.py` | JSONL 仍可用，SQLite 仅用临时测试库 |
| P8 | 前端/仪表盘再评估 | 待定 | KnowledgeBase frontend | 后端 API 稳定后再决定是否做 UI |

## 2. 数据放置规范

| 数据类型 | 允许位置 | Git 状态 | 说明 |
| --- | --- | --- | --- |
| 运行记忆 | `data/memory/` | 忽略 | 本地运行产生，不提交 |
| 执行日志/trace | `data/logs/` | 忽略 | 本地运行产生，不提交 |
| 工具输出 | `data/output/` | 忽略 | 默认输出目录，避免乱写到别处 |
| 外部项目本地快照 | `workspace/local-imports/` | 忽略 | 只做本地保留，不进 Git |
| 规划/任务/架构记录 | `workspace/intake/`, `workspace/*.md` | 可提交 | 必须是安全、去隐私的文本 |
| 公开配置 | `config/`, `.codex.example/` | 可提交 | 不得包含 token、密钥、私人路径 |
| 测试样例 | `tests/fixtures/` | 可提交 | 只能放脱敏、小体量、可复现数据 |
| 临时文件 | 系统临时目录或用户明确指定路径 | 不提交 | 用完应说明，不默认长期保留 |

## 3. 禁止放置位置

| 禁止/需确认位置 | 规则 |
| --- | --- |
| 其他项目目录 | 不把 Cognitive-OS 生成物写到兄弟项目或旧项目目录 |
| 其他磁盘根目录 | 不写入 `D:\`, `E:\` 等根目录；跨盘操作需确认 |
| 云同步目录 | 不默认写入 OneDrive、Dropbox、网盘等同步目录 |
| 用户配置目录 | 不写入用户 profile、浏览器、SSH、系统配置目录 |
| 源项目原目录 | 不回写 `D:\Project Directory`，除非用户明确要求 |
| 仓库根目录散文件 | 不随手把报告、缓存、导出文件堆在项目根 |

## 4. 外溢控制规则

| 场景 | 必须先做什么 |
| --- | --- |
| 复制/搬运数据 | 说明源路径、目标路径、排除规则、是否 Git 忽略 |
| 生成文件 | 先选择最小合适目录，优先 `data/output/` 或 `workspace/intake/` |
| 导出报告 | 优先生成脱敏、小体量 Markdown，不打包整个项目 |
| 网络请求 | 不携带本地文件内容，除非用户确认目的地和数据范围 |
| 引入外部项目代码 | 先做 source-to-target 映射，不整仓库混入运行时代码 |
| 清理旧目录 | 先确认本地快照完整，再由用户确认具体删除路径 |

## 5. 近期执行顺序

| 顺序 | 本轮可做任务 | 产出 |
| ---:| --- | --- |
| 1 | 补 API smoke test | `tests/test_api_smoke.py` |
| 2 | 抽出 ContextEngine | `app/rag/context_engine.py` |
| 3 | 补内容质量模块 | `app/ingestion/quality.py` |
| 4 | 把 trace audit 做成确定性评估 | `app/evaluation/trace_audit.py` |
| 5 | 让 lesson 带证据和约束 | `app/evaluation/lesson_engine.py` |
| 6 | 给 tools 加 guard 层 | `app/tools/guard.py` |

## 6. 每轮完成标准

| 检查项 | 命令/要求 |
| --- | --- |
| 单元测试 | `python -m unittest discover -s tests` |
| 编译检查 | `python -m compileall app tests` |
| Git 状态 | `git status --short` |
| 差异摘要 | `git diff --stat` |
| 数据边界 | 不出现未忽略的 runtime data、缓存、数据库、密钥、外部快照 |

## 7. 执行记录

| 日期 | 执行内容 | 结果 | 后续 |
| --- | --- | --- | --- |
| 2026-06-29 | Round 1：API smoke test、ContextEngine、内容质量模块 | 15 个测试通过，编译通过，本地快照仍被 Git 忽略 | 下一轮进入 Trace Audit 和 LessonEngine |
| 2026-06-29 | Round 2：Trace Audit、LessonEngine、eval audit evidence | 18 个测试通过，编译通过，`/run` 返回具体 audit 和 lesson | 下一轮进入 Tool Guard |
| 2026-06-29 | Round 3：Tool Guard、dry-run/path/high-risk 统一安全门 | 23 个测试通过，编译通过，工具结果包含 guard reasons | 下一轮进入 FSRS/card review loop |
| 2026-06-29 | Round 4：FSRS/card review loop、学习卡片 API | 28 个测试通过，编译通过，卡片创建/复习/due 查询可用 | 下一轮进入 Teach-back/Rubric 或 Obsidian 输入层 |
