# Knowledge-Base UI Themes Package

这是一个可继续开发/二次设计的 **Knowledge-Base 个人学习 OS 仪表盘 UI 套装**。

## 包含内容

- 6 套不同主题：Apple Light、Graphite Dark、Aurora Glass、Forest Focus、Cream Paper、Pro Blue
- 每套均包含：
  - `*_layered.svg`：可导入 Figma / Illustrator / Affinity Designer 的分层 SVG
  - `*_preview.png`：1536×1024 PNG 预览图
  - `*_mockup.html`：HTML/CSS 可运行界面稿，适合交给 CODEX 继续实现
  - `theme_tokens.json`：主题颜色变量
- `00_Preview_Board/`：AI 生成的整体预览/参考图
- `layer_manifest.json`：图层结构说明
- `CODEX_HANDOFF.md`：给 CODEX 的开发交接说明

## 分层结构

SVG 中的主要图层组：

1. `00_background`：背景与主题装饰
2. `layer_sidebar`：左侧 macOS 半透明导航栏
3. `layer_main_window`：主窗口容器
4. `layer_top_bar`：顶部标题栏/搜索/头像
5. `layer_main_content`：主体内容
6. `layer_onboarding_panel`：欢迎引导 4 步
7. `layer_stat_cards`：4 个统计卡片
8. `layer_quick_actions`：4 个快捷操作卡片
9. `layer_recent_activity`：最近活动列表
10. `layer_bottom_dock`：底部 Dock

## 注意

- 本包没有包含任何字体文件，字体采用系统字体栈：`-apple-system, SF Pro, Inter, Arial`。
- `.svg` 是真实可编辑分层矢量文件；如需 `.fig` 或 `.psd`，可将 SVG 导入 Figma/Photoshop 后另存。

