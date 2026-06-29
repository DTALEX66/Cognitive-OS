# Lumina AI 工程顶层门禁

## P0 原则

```text
先校验，再切换。
先修复，再交接。
先冻结，再重生成。
```

## 每次切换工具前必须检查

- UTF-8，无 BOM。
- LF 换行，不混用 CRLF。
- i18n key 中英文完全一致。
- route-package 数据结构完整。
- 静态资源路径存在。
- 冻结路线不得自动覆盖。

## 推荐命令

```bash
npm run prehandoff
npm run lint
npm run typecheck
npm run test
npm run build
```
