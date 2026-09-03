import { chromium } from "playwright";
import { mkdir } from "node:fs/promises";
import { fileURLToPath } from "node:url";
import path from "node:path";

const here = path.dirname(fileURLToPath(import.meta.url));
const output = path.resolve(here, "../../docs/media");
const baseUrl = process.env.WEALTHGUARD_QA_URL || "http://127.0.0.1:8000";
await mkdir(output, { recursive: true });

const browser = await chromium.launch({ channel: "chrome", headless: true });
try {
  const mobile = await browser.newPage({ viewport: { width: 390, height: 844 }, deviceScaleFactor: 1 });
  await mobile.goto(baseUrl, { waitUntil: "networkidle" });
  const geometry = await mobile.evaluate(() => ({
    innerWidth: window.innerWidth,
    scrollWidth: document.documentElement.scrollWidth,
    navVisible: Boolean(document.querySelector(".sidebar")?.getBoundingClientRect().height)
  }));
  if (geometry.scrollWidth > geometry.innerWidth || !geometry.navVisible) {
    throw new Error(`Mobile layout failed: ${JSON.stringify(geometry)}`);
  }
  await mobile.getByRole("button", { name: "Run research trace" }).click();
  await mobile.locator(".response-stack").waitFor();
  await mobile.locator("textarea").fill("What does SPY invest in and what are its stated risks?");
  await mobile.getByRole("button", { name: "Run research trace" }).click();
  await mobile.getByRole("link", { name: /Open cited passage/ }).first().waitFor();
  const [passage] = await Promise.all([
    mobile.waitForEvent("popup"),
    mobile.getByRole("link", { name: /Open cited passage/ }).first().click()
  ]);
  await passage.waitForLoadState();
  await passage.close();
  await mobile.getByRole("button", { name: "Useful" }).click();
  const persisted = await mobile.evaluate(() => JSON.parse(localStorage.getItem("wg-dogfood-v1") || "{}"));
  if (persisted.sessions?.length !== 2 || persisted.sessions[0]?.evidenceOpened !== 1 || persisted.sessions[0]?.feedback !== "useful") {
    throw new Error(`Dogfood trace was not persisted correctly: ${JSON.stringify(persisted.sessions?.[0])}`);
  }
  await mobile.screenshot({ path: path.join(output, "mobile-dogfood-home.png"), fullPage: true });

  const desktop = await browser.newPage({ viewport: { width: 1440, height: 1000 }, deviceScaleFactor: 1 });
  await desktop.goto(baseUrl, { waitUntil: "networkidle" });
  await desktop.screenshot({ path: path.join(output, "desktop-dogfood-home.png"), fullPage: true });
  console.log(JSON.stringify({ status: "passed", mobile: geometry, persistedSessions: persisted.sessions.length, evidenceOpenRecorded: true, feedbackRecorded: true }));
} finally {
  await browser.close();
}
