# AlphaQuantPro 中文视频演示录制脚本

用 Playwright 自动打开 AlphaQuantPro，按章节逐步演示完整工作流，并录制为可直接下载的视频文件（`.webm`）。画面中会叠加中文章节卡片与字幕，无需人工配音。

## 演示内容（六个章节）

| 章节 | 内容 |
| --- | --- |
| 1. 项目简介 | 工作台定位：策略代码 → 确定性回测 → 模拟运行 → 运行分析 → AI 评审 |
| 2. 使用场景说明 | 量化开发者 / 策略研究员 / AI 策略构建者 / 投资交易爱好者 |
| 3. 核心功能演示 | 策略编辑、一键回测（指标/曲线/交易/日志）、模拟运行实时跟踪与手动停止 |
| 4. AI 能力展示 | DeepSeek 运行后分析、AI 策略评审、AI 助手多轮中文对话（缺密钥时为标注 MOCK 的演示输出） |
| 5. 输入、处理过程和输出结果 | 行情数据获取与标准化 → 沙箱执行与确定性引擎 → 指标/图表/成交/日志证据链 |
| 6. 项目亮点说明 | 确定性优先、全程可审计、仅限模拟、统一数据网关与单一 LLM 运行时、双语界面 |

## 前置条件

1. 后端已启动：`cd backend && pip install -r requirements.txt && uvicorn app.main:app --port 8000`
2. 前端已启动：`cd frontend && npm install && npm run dev`（http://localhost:3000）
3. 本机已安装 Chrome（脚本优先使用系统 Chrome，否则可执行 `npx playwright install chromium`）

## 运行方式

```bash
cd demo
npm install
npm run record
```

## 输出

录制完成后，视频保存到：

```text
demo/output/alphaquantpro_demo_zh.webm
```

`.webm` 可直接在浏览器播放、下载或分享；如需 `.mp4`，可用 ffmpeg 转换：
`ffmpeg -i output/alphaquantpro_demo_zh.webm demo.mp4`。

## 可选配置

| 环境变量 | 默认值 | 说明 |
| --- | --- | --- |
| `DEMO_BASE_URL` | `http://localhost:3000` | 前端地址 |

## 常见问题

- **页面元素找不到 / 超时**：确认前后端均已启动，且首页能正常打开；脚本会先把界面切换为简体中文，按钮定位依赖中文文案。
- **AI 输出显示 MOCK**：属预期行为——未配置 `DEEPSEEK_API_KEY` 时，AI 功能自动降级为明确标注的演示输出，确定性功能不受影响。

> 免责声明：演示内容仅用于产品功能展示，非投资建议；本 MVP 仅限模拟，不支持实盘交易。
