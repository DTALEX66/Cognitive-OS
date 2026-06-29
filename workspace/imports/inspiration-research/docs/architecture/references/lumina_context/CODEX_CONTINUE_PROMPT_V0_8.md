# 给 Codex 的继续开发指令｜v0.8

请基于 Lumina AI v0.7 开发包继续开发 v0.8。

## 优先目标

1. 接入 Playwright，建立页面截图基线。
2. 将 localStorage 路线存储正式升级为 IndexedDB，保留 localStorage 作为轻量状态层。
3. 增加 ZIP 路线资产包导入导出准备。
4. 增加移动端真实视口测试。
5. 继续修复 UI，使页面更贴近 public/ui-reference 下的高保真参考图。
6. 保持右上角双语切换。
7. 保持诗意标题，但导航必须清晰。
8. 不接真实 AI、不做登录、不做支付、不做完整社区后端。

## 必须通过

```bash
npm run quality
npm run smoke:pages
npm run prehandoff
npm run audit:high
git diff --check
```

## 硬性产品原则

```text
AI 可以抽象，但不能失真。
图片帮助记忆，但不能乱变。
知识必须可追溯。
路线确认后不得自动重新生成。
社区可以分享，但来源和改动必须透明。
先校验，再切换。
```
