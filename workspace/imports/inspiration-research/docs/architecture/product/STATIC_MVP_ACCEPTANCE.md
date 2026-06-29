# 静态商用 MVP 验收清单

## UI 验收

- 顶部导航清晰：Home / Routes / Community / Report / Settings。
- 右上角存在双语切换：中 / EN。
- 诗意标题用于页面主标题，功能名用于 plainTitle。
- 首页、上传、复习编码、记忆宫殿、训练、报告、社区、设置、路线资产工作台均可访问。
- 页面风格统一：浅色、蓝紫渐变、圆角卡片、可信学习平台气质。

## 数据验收

- Demo RoutePackage 有 8 个节点。
- 每个节点有事实层与记忆层。
- 每个节点有 sourceText。
- 每个节点有 visualElementMap。
- 事实层改动为 0。
- 图像资产均标记 frozen。

## 本地资产验收

- 可以载入 Demo 路线。
- 可以保存到 localStorage。
- 可以导出 JSON。
- 可以导入 JSON。
- 导入时会校验 RoutePackage 结构。

## 跨工具交接验收

交接前必须执行：

```bash
npm run prehandoff
```

依赖安装后还必须执行：

```bash
npm run lint
npm run typecheck
npm run test
npm run build
```

## 不允许上线的情况

- i18n key 不一致。
- route package 校验失败。
- sourceText 缺失且仍标记 AI 已校验。
- confirmed/frozen 路线被自动重生成。
- 图片资产路径丢失。
- 导出导入后节点数量变化。
