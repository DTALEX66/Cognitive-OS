# Database Draft

当前 v1.1 仍以 JSON 种子数据为主。`schema.sql` 是 SaaS 化迁移草案。

迁移建议：

1. 先把 `data/seeds/*.json` 导入 Postgres。
2. 保留 JSON 数据作为离线包和回滚基线。
3. 所有在线编辑写入数据库，定期导出 JSON/Excel。
4. 企业版开启 RLS、审计日志和 API Key 访问限制。
