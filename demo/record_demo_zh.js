/**
 * AlphaQuantPro 中文视频演示录制脚本（Playwright）
 * =================================================
 *
 * 功能：自动打开 AlphaQuantPro 应用，按章节逐步演示完整工作流，
 * 并录制为可直接下载/分享的视频文件（.webm）。
 *
 * 演示章节：
 *   1. 项目简介
 *   2. 使用场景说明
 *   3. 核心功能演示（策略 → 回测 → 模拟运行）
 *   4. AI 能力展示（DeepSeek 策略评审 / 助手 / 运行后分析）
 *   5. 输入、处理过程和输出结果
 *   6. 项目亮点说明
 *
 * 前置条件：
 *   - 后端已启动：  cd backend  && uvicorn app.main:app --port 8000
 *   - 前端已启动：  cd frontend && npm run dev   （http://localhost:3000）
 *
 * 运行方式：
 *   cd demo && npm install && npm run record
 *
 * 输出：
 *   demo/output/alphaquantpro_demo_zh.webm
 *
 * 可选环境变量：
 *   DEMO_BASE_URL   前端地址（默认 http://localhost:3000）
 */

const { chromium } = require("playwright");
const fs = require("fs");
const path = require("path");

const BASE_URL = process.env.DEMO_BASE_URL || "http://localhost:3000";
const OUTPUT_DIR = path.join(__dirname, "output");
const VIDEO_NAME = "alphaquantpro_demo_zh.webm";
const VIEWPORT = { width: 1440, height: 900 };

/* ---------------- 画面叠加层工具 ---------------- */

/** 全屏章节卡片：显示章节编号、标题与说明文字，停留数秒后淡出 */
async function showChapter(page, num, title, lines, holdMs = 5000) {
  console.log(`\n【第 ${num} 章】${title}`);
  await page.evaluate(
    ({ num, title, lines }) => {
      const old = document.getElementById("demo-chapter");
      if (old) old.remove();
      const el = document.createElement("div");
      el.id = "demo-chapter";
      el.style.cssText =
        "position:fixed;inset:0;z-index:99999;background:rgba(2,6,23,.94);" +
        "display:flex;flex-direction:column;align-items:center;justify-content:center;" +
        "font-family:system-ui,'PingFang SC','Microsoft YaHei',sans-serif;opacity:1;transition:opacity .5s";
      const items = lines
        .map(
          (l) =>
            `<li style="color:#cbd5e1;font-size:19px;line-height:1.9;list-style:none;">${l}</li>`
        )
        .join("");
      el.innerHTML =
        `<div style="color:#38bdf8;font-size:22px;letter-spacing:6px;margin-bottom:10px;">第 ${num} 章</div>` +
        `<h1 style="color:#f1f5f9;font-size:44px;margin:0 0 24px;font-weight:700;">${title}</h1>` +
        `<ul style="margin:0;padding:0;text-align:center;">${items}</ul>` +
        `<div style="position:absolute;bottom:28px;color:#475569;font-size:13px;">AlphaQuantPro · 仅限模拟，非投资建议</div>`;
      document.body.appendChild(el);
    },
    { num, title, lines }
  );
  await page.waitForTimeout(holdMs);
  await page.evaluate(() => {
    const el = document.getElementById("demo-chapter");
    if (el) {
      el.style.opacity = "0";
      setTimeout(() => el.remove(), 550);
    }
  });
  await page.waitForTimeout(650);
}

/** 底部字幕条：解释当前正在演示的操作（页面跳转后需重新调用） */
async function caption(page, text, holdMs = 2600) {
  console.log(`  · ${text}`);
  await page.evaluate((text) => {
    let el = document.getElementById("demo-caption");
    if (!el) {
      el = document.createElement("div");
      el.id = "demo-caption";
      el.style.cssText =
        "position:fixed;left:50%;bottom:26px;transform:translateX(-50%);z-index:99998;" +
        "background:rgba(8,47,73,.96);border:1px solid #0ea5e9;color:#e0f2fe;" +
        "padding:10px 24px;border-radius:12px;font-size:17px;max-width:82%;text-align:center;" +
        "font-family:system-ui,'PingFang SC','Microsoft YaHei',sans-serif;box-shadow:0 6px 24px rgba(0,0,0,.5)";
      document.body.appendChild(el);
    }
    el.textContent = text;
  }, text);
  await page.waitForTimeout(holdMs);
}

/** 平滑滚动页面，便于展示长内容 */
async function scrollTo(page, y, holdMs = 1600) {
  await page.evaluate((y) => window.scrollTo({ top: y, behavior: "smooth" }), y);
  await page.waitForTimeout(holdMs);
}

/* ---------------- 主流程 ---------------- */

async function main() {
  fs.mkdirSync(OUTPUT_DIR, { recursive: true });

  // 优先使用系统 Chrome，失败时回退到 Playwright 自带 Chromium
  let browser;
  try {
    browser = await chromium.launch({ headless: true, channel: "chrome" });
  } catch {
    browser = await chromium.launch({ headless: true });
  }

  const context = await browser.newContext({
    viewport: VIEWPORT,
    recordVideo: { dir: OUTPUT_DIR, size: VIEWPORT },
    locale: "zh-CN",
  });
  context.setDefaultTimeout(30000);
  const page = await context.newPage();

  /* ========== 第 1 章：项目简介 ========== */
  await page.goto(`${BASE_URL}/dashboard`, { waitUntil: "networkidle" });
  // 将界面切换为简体中文（语言选择会持久化到 localStorage）
  await page.getByRole("button", { name: "中文" }).click();
  await page.waitForTimeout(800);

  await showChapter(page, "01", "项目简介", [
    "AlphaQuantPro —— AI 量化策略工作台",
    "策略代码 → 确定性回测 → 模拟运行 → 运行分析 → AI 评审",
    "本地优先 · 全程可审计 · 仅限模拟（MVP 不支持实盘交易）",
  ]);
  await caption(page, "这是工作台首页：策略、回测、模拟运行一览，右下角展示市场数据网关状态");
  await scrollTo(page, 300);
  await scrollTo(page, 0, 900);

  /* ========== 第 2 章：使用场景说明 ========== */
  await showChapter(page, "02", "使用场景说明", [
    "量化开发者：一站式管理策略代码与回测记录",
    "策略研究员：可复现实验，指标与日志全程留痕",
    "AI 策略构建者：用 AI 辅助评审与改进策略",
    "投资交易爱好者：在零风险的模拟环境中验证想法",
  ]);
  await page.getByRole("link", { name: "策略", exact: true }).click();
  await page.waitForTimeout(1200);
  await caption(page, "策略库：内置指标型（DataFrame）与脚本型（事件驱动）两类示例策略");

  /* ========== 第 3 章：核心功能演示 ========== */
  await showChapter(page, "03", "核心功能演示", [
    "① 编辑策略代码与参数",
    "② 一键运行确定性回测，查看指标 / 曲线 / 交易 / 日志",
    "③ 启动模拟运行（Paper Run），实时跟踪信号与盈亏",
  ]);

  // ① 打开策略详情：代码编辑器 + 参数面板
  await page.getByRole("link", { name: "RSI Mean Reversion" }).click();
  await page.waitForTimeout(1400);
  await caption(page, "策略详情页：左侧是 Python 策略代码与 JSON 参数，右侧是回测配置与 AI 助手");
  await scrollTo(page, 250);

  // ② 运行回测
  await caption(page, "现在点击「运行回测」——回测由确定性引擎同步完成，结果可复现", 2200);
  await page.getByRole("button", { name: "运行回测" }).click();
  await page.waitForURL("**/backtests/**", { timeout: 60000 });
  await page.waitForTimeout(1600);
  await caption(page, "回测完成：顶部是核心指标卡片（总收益率、最大回撤、夏普、胜率等）");
  await scrollTo(page, 420);
  await caption(page, "权益曲线与回撤图直观展示策略表现，右侧为风险指标与运行日志");
  await scrollTo(page, 1000);
  await caption(page, "每一笔成交都有时间、方向、数量、价格、手续费与触发原因，全程可审计");
  await scrollTo(page, 0, 1000);

  // ③ 启动模拟运行
  await page.getByRole("link", { name: "模拟运行" }).click();
  await page.waitForTimeout(1200);
  await caption(page, "模拟运行页：仅限模拟，永远不会发送真实订单");
  await page.getByLabel("标的").fill("TSLA");
  await caption(page, "选择策略与标的 TSLA，模式为历史回放，点击「开始模拟运行」", 2000);
  await page.getByRole("button", { name: "开始模拟运行" }).click();
  await page.waitForTimeout(3500);
  await page.locator('a[href^="/paper-runs/"]').first().click();
  await page.waitForURL("**/paper-runs/**");
  await page.waitForTimeout(1200);
  await caption(page, "运行详情实时刷新：当前权益、盈亏、信号、订单、成交与日志", 5000);

  // 若仍在运行则手动停止，演示「随时可停」的人工控制
  const stopBtn = page.getByRole("button", { name: "停止运行" });
  if (await stopBtn.isVisible().catch(() => false)) {
    await caption(page, "用户可随时停止运行——人工控制优先于自动化", 1800);
    await stopBtn.click();
    await page.waitForTimeout(1500);
  }

  /* ========== 第 4 章：AI 能力展示 ========== */
  await showChapter(page, "04", "AI 能力展示", [
    "LLM 运行时仅使用 DeepSeek（deepseek-chat）",
    "AI 只对确定性引擎的输出进行解读，绝不编造行情或指标",
    "未配置密钥时自动降级为明确标注的 MOCK 输出",
  ]);

  // 运行后分析：确定性摘要 + AI 分析
  await scrollTo(page, 2000, 1200);
  const genBtn = page.getByRole("button", { name: "生成分析" });
  if (await genBtn.isVisible().catch(() => false)) {
    await caption(page, "点击「生成分析」：先输出确定性摘要，再由 DeepSeek 生成解读与改进建议", 2200);
    await     genBtn.click();
    await page.waitForTimeout(13000); // real DeepSeek analysis latency
    await scrollTo(page, 2600);
    await caption(page, "运行后分析：上方为引擎计算的确定性摘要，下方为 DeepSeek 生成的 AI 分析（未配置密钥时会明确标注为 MOCK）", 3200);
  }

  // 分析页：AI 策略评审 + AI 助手对话
  await page.getByRole("link", { name: "分析", exact: true }).click();
  await page.waitForTimeout(1200);
  await caption(page, "分析页：选择策略后可请求 AI 策略评审，并可选携带某次回测作为上下文");
  await page.getByRole("button", { name: "请求 AI 评审" }).click();
  await page.waitForTimeout(14000); // real DeepSeek review latency
  await caption(page, "AI 评审结果由 DeepSeek 生成并附带免责声明（未配置密钥时会明确标注为 MOCK 输出）", 3000);
  await page
    .getByPlaceholder("询问策略、风险或改进建议...")
    .fill("如何降低这个策略的最大回撤？");
  await page.getByRole("button", { name: "发送" }).click();
  await page.waitForTimeout(14000); // real DeepSeek chat latency
  await caption(page, "AI 策略助手支持多轮对话，回复语言跟随界面语言（当前为简体中文）", 3000);

  /* ========== 第 5 章：输入、处理过程和输出结果 ========== */
  await showChapter(page, "05", "输入、处理过程和输出结果", [
    "输入：策略代码 + 参数 + QVeris 行情数据（缺密钥时为标注 MOCK 的模拟数据）",
    "处理：数据校验与标准化 → 沙箱执行策略 → 确定性回测/模拟引擎",
    "输出：指标、权益曲线、成交明细、运行日志与 AI 分析报告",
  ]);
  await page.getByRole("link", { name: "市场数据" }).click();
  await page.waitForTimeout(1200);
  await caption(page, "输入端：所有行情数据经统一网关获取，右侧列出可用数据能力");
  await page.getByLabel("标的").fill("NVDA");
  await page.getByRole("button", { name: "获取" }).click();
  await page.waitForTimeout(2000);
  await scrollTo(page, 500);
  await caption(page, "处理过程：OHLCV 经过字段校验与标准化，来源与质量说明清晰标注（含 MOCK 标签）", 3200);
  await page.getByRole("link", { name: "回测", exact: true }).click();
  await page.waitForTimeout(1200);
  await page.getByRole("link", { name: "查看" }).first().click();
  await page.waitForTimeout(1500);
  await caption(page, "输出结果：同一输入必然得到同一输出——指标、图表、交易与日志构成完整证据链", 3200);
  await scrollTo(page, 400);

  /* ========== 第 6 章：项目亮点说明 ========== */
  await showChapter(
    page,
    "06",
    "项目亮点说明",
    [
      "✔ 确定性优先：回测可复现，指标由引擎计算，AI 绝不参与算账",
      "✔ 全程可审计：信号、订单、成交、日志、数据来源全部留痕",
      "✔ 安全边界清晰：仅限模拟，实盘交易在 MVP 中被硬性禁用",
      "✔ 统一数据网关 + 单一 LLM 运行时（DeepSeek），密钥只存在于后端",
      "✔ 中英双语界面一键切换，本地优先、开箱即用",
    ],
    7000
  );
  await page.getByRole("link", { name: "仪表盘" }).click();
  await page.waitForTimeout(1000);
  await caption(page, "演示结束，感谢观看 AlphaQuantPro！", 2600);

  /* ---------------- 保存视频 ---------------- */
  const video = page.video();
  await context.close();
  await browser.close();

  const rawPath = await video.path();
  const finalPath = path.join(OUTPUT_DIR, VIDEO_NAME);
  fs.renameSync(rawPath, finalPath);
  console.log(`\n✅ 演示视频已保存（可直接下载/分享）：${finalPath}`);
}

main().catch((err) => {
  console.error("❌ 录制失败：", err);
  process.exit(1);
});
