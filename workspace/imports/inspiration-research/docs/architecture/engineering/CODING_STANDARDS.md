# 编程程序规范

## 1. 基础编码规范

- 全部文本文件使用 UTF-8，无 BOM。
- 使用 LF 换行。
- 不允许混入不可见字符。
- TypeScript 优先显式类型。
- React 组件文件使用 PascalCase。
- 工具函数使用 kebab-case 文件名。

## 2. Next.js 规范

- App Router 页面放在 `app/<route>/page.tsx`。
- 使用浏览器 API 的组件必须加 `'use client'`。
- 数据结构放在 `lib/`，不要写进页面组件。
- Demo 数据放在 `data/`。
- 静态图放在 `public/`。

## 3. 本地存储规范

- localStorage 只用于 MVP 和轻量状态。
- 所有 key 必须有版本号，例如 `lumina.current.route-package.v1`。
- 读取失败必须 fallback 到 Demo 数据，不让页面崩溃。
- 后续 IndexedDB 接入时，不改变上层 RoutePackage 类型。

## 4. 路线资产规则

- `confirmed` / `frozen` 状态不得自动重生成。
- 重生成只能创建候选版本。
- 用户确认后才替换当前版本。
- 事实层改动必须记录到 `changeStatus.factChangedFromSource`。

## 5. 代码提交前必须检查

```bash
npm run prehandoff
git diff --check
```

完整检查：

```bash
npm run lint
npm run typecheck
npm run test
npm run build
```

## 6. 跨工具切换规则

从 ChatGPT 到 Codex、从 Codex 到 IDE、从 IDE 回 ChatGPT 前，必须写明：
- 当前版本。
- 改了哪些文件。
- 跑过哪些检查。
- 哪些检查没跑。
- 已知风险和下一步。
