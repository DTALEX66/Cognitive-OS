# 005 File Ingestion v1

## 目标

把 Cognitive-OS 从只接收一段文本，推进到可以摄取项目内 Markdown 和文本文件。这个环节对应 `信息 -> 注意力` 里的真实输入入口，也是未来接 Obsidian vault、Knowledge-Base 文档和 Inspiration-Research 调研材料的前置层。

## 本轮新增能力

| 能力 | 接口 | 当前边界 |
| --- | --- | --- |
| 单文件摄取 | `POST /ingest/file` | 只读当前仓库内 `.md`、`.markdown`、`.txt` 文件 |
| 目录批量摄取 | `POST /ingest/directory` | 默认 `*.md`，最多 100 个文件 |
| 路由联动 | 文件摄取后自动调用 attention router | 返回 `document` 与 `route` |
| 安全边界 | 路径必须留在 Cognitive-OS 项目根目录内 | 阻断跨目录读取和任意磁盘访问 |

## 为什么这样设计

- Obsidian 只是 KB 的一个上游入口，所以文件摄取先做成通用 Markdown 输入层。
- KB 和 IR 的导入资料都已经在 `workspace/imports` 下，可以先作为本地样本跑通。
- 路由仍然是第一道判断：同样是 Markdown，学习材料进 `KB`，调研/论文/GitHub 材料进 `IR`，明确行动请求进 `TASK`。
- 当前不自动扫描外部目录，不碰系统目录，也不读取仓库外文件。

## 后续扩展

1. 增加 Obsidian frontmatter、tag、folder 到 metadata 的解析。
2. 增加目录级去重和增量摄取，避免重复写入 memory。
3. 增加 chunking，把长文档切成可检索片段。
4. 给 KB/IR 分别增加专用 ingestion profile。
