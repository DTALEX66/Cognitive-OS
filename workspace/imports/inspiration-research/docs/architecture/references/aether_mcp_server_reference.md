# Aether Radar MCP Prototype

这是 Aether Radar v0.9 的本地 MCP 原型，用于让支持 MCP 的 Agent 查询 AI 工具库、风险维度和场景方案。

## 运行

```bash
node mcp-server/aether-radar-mcp.mjs
```

## 暴露工具

- `search_entities`：搜索 AI 工具、平台、模型、Agent、开源项目。
- `get_entity`：按 id 或名称查询单个实体。
- `list_categories`：列出分类。
- `list_risks`：列出风险维度。
- `list_scenarios`：列出场景方案。
- `data_status`：返回数据状态和风险提醒。

## 安全边界

当前版本是本地只读查询原型，不写文件、不调用外网、不执行第三方工具。企业化前必须增加：

- 权限与认证
- 调用审计日志
- 数据版本签名
- 速率限制
- 敏感字段最小化
- MCP 工具描述安全复核
