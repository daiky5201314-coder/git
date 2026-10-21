# 高中数学高考真题 HTML 可视化教学 Skill V3.0

**重点升级：确保其他 Agent 做出来的页面，在教学画面、知识点展开顺序和用户操作上接近「2025 第17题流畅自动演示完整版」，而非仅满足技术合规。**

## 不可跳过的学习顺序

1. 阅读 `SKILL.md`。
2. 阅读 `references/V3_视觉与交互设计硬契约.md`、`V3_教学分镜模板与具体对照.md`、`V3_视觉验收与反例报告.md`。
3. **亲自打开并交互操作** `examples/首选视觉交互参考_2025第17题.html`，结合 `assets/首选视觉基准_第17题_证明步骤.png`、`反面案例_第16题_图文脱节.png` 体会对比。
4. 观看 `examples/V3_联合视觉与工程示范_函数入门非真题.html`，理解如何用严格时间轴做出与认可成品相近的课堂交互体验；此示例非高考试题。再阅读 `references/标准HTML架构与动画硬约束.md` 并打开 `examples/标准HTML5_时间线和状态同步技术示例.html` 学习工程代码，不要照搬它的简陋 UI。
5. 对用户上传的每道新题重新核题、独立求解、制作知识点动画、完整教学分镜、标准解题步骤，生成一个离线 HTML。
6. 运行 `validate_delivery.py`、`browser_contract_test.py`、`visual_teaching_contract_test.py`；人工审片与数学核对仍是必选。

## 三项测试

```bash
python scripts/validate_delivery.py "新题.html"
python scripts/browser_contract_test.py "新题.html" --shots ./工程截图
python scripts/visual_teaching_contract_test.py "新题.html" --shots ./教学验收截图
```

所需环境：Python + Playwright + Chromium（若使用脚本）。终端缺少依赖时应明确未测试，不可假装通过。

## 原则

- **视觉交互成品**决定最终页面长什么样、学生怎么学。
- **V2 工程底座**决定动画如何可靠地运行。
- **每道题的真实数学内容**决定要演示什么、如何推理。

三者缺一不可。每道题都是独立 HTML，不要求额外的历史聊天和文件。

## 给其他 Agent 的启动指令

> 使用 Skill V3 从零制作我上传的数学题。必须先实际打开 `examples/首选视觉交互参考_2025第17题.html`，以它的**导航、左侧数学舞台、右侧完整教学微步骤卡、真实连续动画与同步公式、思考互动、播放器**作为用户体验基准，不得做成“3D 图+一句提示+底部折叠答案”。同时按 V2 工程标准实现同一时间轴、离线 HTML 和浏览器测试。知识点要从零解释并配独立动画。运行 3 项测试、人工核对 5 种教学状态和最终证明，只交付独立 `.html` 成品。