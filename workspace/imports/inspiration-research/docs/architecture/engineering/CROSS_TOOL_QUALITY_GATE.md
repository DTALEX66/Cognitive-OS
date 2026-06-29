# 跨工具质量门禁

## 1. 目的

避免在 ChatGPT 网页版、Codex 桌面版、VS Code、Cursor 或其他 IDE 之间切换时出现乱码、语法断裂、依赖漂移、i18n 不一致、路线包结构漂移等问题。

## 2. 切换前必须完成

```bash
npm run prehandoff
git diff --check
```

如果本地依赖可用，再运行：

```bash
npm run lint
npm run typecheck
npm run test
npm run build
```

## 3. P0 检查项

| 检查项 | 失败后果 |
|---|---|
| UTF-8 / BOM / CRLF | 中文乱码、Codex patch 异常 |
| ESLint | 隐性语法和 React 问题 |
| TypeScript | 类型错误、构建失败 |
| i18n key 对齐 | 双语切换缺文案 |
| RoutePackage 校验 | 导入导出失败 |
| 资产路径校验 | 页面图片丢失 |
| 冻结资产保护 | 记忆路线不稳定 |

## 4. 禁止

```text
检查失败时继续切工具
未说明风险就交给下一个工具
自动覆盖用户已冻结资产
只复制部分文件导致包结构断裂
```
