# Lumina AI 新对话交接包｜START HERE

你正在接手 Lumina AI 项目。请先读本文件，再解压 `01_latest_engineering_package/lumina_ai_commercial_frontend_mvp_v0_7_browser_smoke_package.zip`。

## 当前项目状态

项目名：Lumina AI  
中文品牌意象：琉明知途  
定位：AI 学习路线平台。

一句话：把知识变成路线，把路线变成资产，把资产变成社区。

当前最新交付：

```text
v0.7：浏览器冒烟测试与 IndexedDB 迁移准备版
```

当前状态：

```text
可安装、可构建、可页面冒烟、可交接的商用前端 MVP 基线。
```

## 最新工程包

```text
01_latest_engineering_package/lumina_ai_commercial_frontend_mvp_v0_7_browser_smoke_package.zip
```

解压后先运行：

```bash
npm ci --ignore-scripts
npm run quality
npm run smoke:pages
npm run prehandoff
npm run audit:high
git diff --check
```

## v0.7 已覆盖页面

```text
/
/upload
/review
/palace
/training
/report
/routes
/community
/settings
```

## v0.7 已具备能力

```text
Next.js App Router 工程骨架
React + TypeScript
商用品质前端 UI 基线
右上角双语切换：中 / EN
诗意化标题与主题文案
RoutePackage 类型结构
中国近代史 Demo 路线包
localStorage 本地路线保存
路线导入 / 导出
训练记录写入本地
学习报告读取真实训练记录
社区路线信任面板
路线时间—图片—释义预览
UI 参考图目录
品牌命名规范
工程质量门禁
浏览器 HTTP 冒烟测试
IndexedDB 迁移准备
```

## 下一步建议：v0.8

```text
1. Playwright 截图基线
2. IndexedDB 正式替换 localStorage 路线资产存储
3. ZIP 路线资产包导入导出
4. 移动端真实视口验收
5. 空状态 / 错误状态继续细化
6. UI 继续贴近高保真参考图
7. 真实 AI Provider 暂缓
8. 真实社区后端 / 登录 / 支付暂缓
```

## 顶层原则

```text
AI 可以抽象，但不能失真。
图片帮助记忆，但不能乱变。
知识必须可追溯，不能凭空生成。
学习必须可验证，不能只看起来学会。
社区可以分享，但来源和改动必须透明。
先校验，再切换。
先修复，再交接。
先冻结，再重生成。
```
