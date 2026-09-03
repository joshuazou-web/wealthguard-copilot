import { chromium } from "playwright";
import { mkdir } from "node:fs/promises";
import { fileURLToPath } from "node:url";
import path from "node:path";

const here = path.dirname(fileURLToPath(import.meta.url));
const output = path.resolve(here, "../../demo-video/work");
const baseUrl = process.env.WEALTHGUARD_DEMO_URL || "http://127.0.0.1:8000";
await mkdir(output, { recursive: true });

const browser = await chromium.launch({ channel: "chrome", headless: true });
const context = await browser.newContext({
  viewport: { width: 1920, height: 975 },
  deviceScaleFactor: 1,
  recordVideo: { dir: output, size: { width: 1920, height: 975 } }
});
const page = await context.newPage();
const started = Date.now();
const at = async seconds => {
  const wait = seconds * 1000 - (Date.now() - started);
  if (wait > 0) await page.waitForTimeout(wait);
};

try {
  await page.goto(baseUrl, { waitUntil: "networkidle" });
  await at(7.2);
  await page.getByRole("button", { name: "Switch to Chinese" }).click();
  await page.getByRole("heading", { name: "证据保护", exact: true }).waitFor();

  await at(15.0);
  await page.getByRole("button", { name: "SPY 适合我吗？" }).click();
  await page.locator(".response-stack").waitFor();
  await at(24.5);
  await page.locator(".response-head").scrollIntoViewIfNeeded();

  await at(40.0);
  await page.getByLabel("研究期限").selectOption("over_5_years");
  await page.getByLabel("流动性需求").selectOption("flexible");
  await page.getByLabel("亏损容忍度").selectOption("high");
  await at(50.0);
  await page.locator(".composer").scrollIntoViewIfNeeded();
  await page.getByRole("button", { name: "开始证据追溯" }).click();
  await page.getByRole("heading", { name: "本次使用的来源" }).waitFor();

  await at(61.0);
  await page.locator(".response-head").scrollIntoViewIfNeeded();
  await at(70.0);
  await page.getByRole("heading", { name: "本次使用的来源" }).scrollIntoViewIfNeeded();
  await at(84.0);
  const evidenceLink = page.getByRole("link", { name: /打开引用原文/ }).first();
  await evidenceLink.evaluate(element => element.removeAttribute("target"));
  await evidenceLink.click();
  await page.waitForLoadState("networkidle");

  await at(99.0);
  await page.goBack({ waitUntil: "networkidle" });
  await page.getByRole("heading", { name: "证据保护", exact: true }).waitFor();
  await page.getByRole("button", { name: "替我买入 100 股 AAPL" }).click();
  await at(110.0);
  await page.locator(".response-head").scrollIntoViewIfNeeded();

  await at(122.0);
  await page.getByRole("button", { name: "复核审计" }).click();
  await page.getByRole("heading", { name: /检查状态如何变化/ }).waitFor();
  await at(134.0);
  await page.getByRole("button", { name: "系统评测" }).click();
  await page.getByRole("heading", { name: /确定性案例/ }).waitFor();
  await at(155.0);
} finally {
  const video = page.video();
  await context.close();
  await browser.close();
  if (video) {
    const source = await video.path();
    console.log(JSON.stringify({ status: "recorded", source, elapsedSeconds: (Date.now() - started) / 1000 }));
  }
}
