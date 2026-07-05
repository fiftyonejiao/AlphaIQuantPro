# AlphaQuantPro 视频演示脚本 · 简短文档

> 脚本文件：`demo/record_demo_zh.js`（Playwright，Node.js）
> 作用：自动打开 AlphaQuantPro，按六个章节逐步演示完整工作流，并录制为可下载的视频文件。

## 一、快速使用

```bash
# 1. 启动后端
cd backend && pip install -r requirements.txt && uvicorn app.main:app --port 8000

# 2. 启动前端（另开终端）
cd frontend && npm install && npm run dev    # http://localhost:3000

# 3. 录制演示视频（另开终端）
cd demo && npm install && npm run record
```

**输出**：`demo/output/alphaquantpro_demo_zh.webm`（约 2 分钟，可直接下载 / 浏览器播放 / 分享；
如需 mp4：`ffmpeg -i output/alphaquantpro_demo_zh.webm demo.mp4`）

## 二、演示章节（与脚本一一对应）

| 章节 | 内容 | 演示画面 |
| --- | --- | --- |
| 1. 项目简介 | AI 量化策略工作台：策略 → 回测 → 模拟运行 → 分析 → AI 评审 | 中文仪表盘总览 |
| 2. 使用场景说明 | 量化开发者 / 策略研究员 / AI 策略构建者 / 投资交易爱好者 | 策略库（指标型 + 脚本型示例） |
| 3. 核心功能演示 | 编辑策略代码与参数；一键确定性回测；启动并手动停止模拟运行 | 代码编辑器、指标卡片、权益/回撤图、成交表、TSLA 模拟运行 |
| 4. AI 能力展示 | 运行后分析、AI 策略评审、AI 助手中文多轮对话（仅 DeepSeek；缺密钥时为标注 MOCK 的演示输出） | 运行详情页 + 分析页 |
| 5. 输入、处理过程和输出结果 | 输入：策略 + 参数 + 行情数据；处理：校验标准化 + 沙箱 + 确定性引擎；输出：指标 / 图表 / 成交 / 日志 | 市场数据页（NVDA 取数）+ 回测详情页 |
| 6. 项目亮点说明 | 确定性可复现、全程可审计、仅限模拟、统一数据网关 + 单一 LLM、双语界面 | 亮点卡片 + 回到仪表盘收尾 |

## 三、脚本实现要点

- **中文界面**：开场自动点击语言切换按钮，全程以简体中文演示；
- **章节卡片 + 字幕**：通过页面注入全屏章节卡与底部字幕条，无需配音即可讲解每一步；
- **真实操作**：全部为真实点击 / 输入 / 等待（运行回测、启动并停止模拟运行、生成分析、AI 对话、取数）；
- **视频录制**：使用 Playwright `recordVideo` 能力，1440×900 分辨率，结束后自动重命名保存；
- **浏览器**：优先使用系统 Chrome，无则回退 Playwright 自带 Chromium（首次可执行 `npx playwright install chromium ffmpeg`）；
- **可配置**：`DEMO_BASE_URL` 环境变量可指定前端地址（默认 `http://localhost:3000`）。

## 四、常见问题

- **元素定位超时**：确认前后端已启动、首页可打开；按钮定位依赖中文文案，请勿手动切回英文；
- **AI 显示 MOCK**：未配置 `DEEPSEEK_API_KEY` 时的预期降级行为，确定性功能不受影响；
- **录制报缺 ffmpeg**：执行 `npx playwright install ffmpeg` 后重试。

> 免责声明：演示仅用于产品功能展示，非投资建议；本 MVP 仅限模拟，不支持实盘交易。
