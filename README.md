# 高考数学 HTML 可视化教学 Skill

> **gaokao-math-html-lesson** · V3.0 教学画面与交互标准版

用于指导 AI Agent 将高中数学题目制作成**可离线运行的单文件 HTML 可视化微课堂**，覆盖原题核对、知识点教学、完整解题逻辑、函数生长 / 空间几何动画、真正连续的自动演示、以及工程与数学验收。

## 开始使用

1. 阅读 [Skill 入口](gaokao-math-html-lesson/SKILL.md)。
2. 根据 Skill 中的顺序学习 [参考资料](gaokao-math-html-lesson/references/) 与 [示例](gaokao-math-html-lesson/examples/)。
3. 向 Agent 提供一道数学题（截图、PDF 或完整题面），让它**从零独立制作**，生成一个不依赖外部资源的 HTML。
4. 在本地执行检查脚本，并通过浏览器人工审片。

## 重点要求

- 不得把「自动演示」简化为切换文字或章节。
- 左侧动态图形、右侧完整推导、教学导航、思考互动与进度条必须同步。
- 严格使用单时间轴，支持任意定位和可恢复的数学状态。
- 所有知识点都从零教学，每题都是独立的完整 HTML。
- 数学与浏览器测试未通过的文件不得称为完成。

## 仓库目录

- `gaokao-math-html-lesson/SKILL.md` — Agent 必读入口
- `gaokao-math-html-lesson/references/` — 教学/视觉/数学/工程标准
- `gaokao-math-html-lesson/examples/` — 真实教学画面和工程示例
- `gaokao-math-html-lesson/scripts/` — 检查与验收脚本

**版本**：V3.0 · 独立教学 Skill；示例不自动证明任何未来生成的题目合格。

## 文件发布状态

GitHub 已发布 **33 份可浏览的文本源文件**，包括完整 Skill、HTML 参考、规范、验收脚本和测试记录。原 ZIP 中还包含 PNG 截图等二进制资料；由于本次 GitHub 连接接口不支持直接上传原有 ZIP / PNG，它们**暂未进入此仓库**。因此本仓库当前是「源文件版」，而非原 ZIP 的逐字节镜像。需要完整图片与原 ZIP 时，使用 ChatGPT 对话中交付的 V3.0 原压缩包。仓库中的图片引用可能暂时无法预览，但 HTML 示范与正文规范均可独立阅读。


> 发布说明：此仓库用于托管可浏览的文本源文件；完整离线 ZIP 原件应在支持二进制上传后补充发布。