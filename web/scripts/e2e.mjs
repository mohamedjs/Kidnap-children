// Browser end-to-end: create a report with a photo through the real UI (presigned PUT from
// the browser), see it listed and searched, view the photo through a presigned GET.
//   node scripts/e2e.mjs path/to/photo.jpg
import { randomUUID } from "node:crypto";
import { WEB, launch, login } from "./browser.mjs";

const photo = process.argv[2];
if (!photo) throw new Error("usage: node scripts/e2e.mjs <photo.jpg>");
const tag = randomUUID().slice(0, 6);
const results = [];
const check = async (name, fn) => {
  try { results.push([(await fn()) !== false, name]); } catch (e) { results.push([false, `${name} (${e.message.split("\n")[0]})`]); }
};

const browser = await launch();
const page = await browser.newPage({ viewport: { width: 1280, height: 900 } });
const s3Puts = [];
page.on("request", (r) => { if (r.method() === "PUT" && r.url().includes("X-Amz-Signature")) s3Puts.push(r.url()); });
const apiUploadBodies = [];
page.on("request", (r) => { if (r.url().includes("/api/") && r.method() !== "GET") apiUploadBodies.push(r.postData()?.length ?? 0); });

await check("Arabic RTL and dark theme by default", async () => {
  await page.goto(WEB);
  const [dir, lang, theme] = await page.evaluate(() => [document.dir, document.documentElement.lang, document.documentElement.dataset.theme]);
  return dir === "rtl" && lang === "ar" && theme === "dark";
});

await check("log in as a demo user", () => login(page, "mona@demo.local"));

let reportUrl = "";
await check("create a report with a photo from the form", async () => {
  await page.goto(`${WEB}/reports/new`);
  const inputs = page.locator("form input.input");
  await inputs.nth(0).fill(`تجربة ${tag}`);
  await page.locator("form select.input").first().selectOption("male");
  await page.locator('form input[type="number"]').fill("5");
  await page.locator("form textarea").fill(`بلاغ تجريبي من اختبار المتصفح ${tag}: يرتدي قميصًا أحمر.`);
  await page.setInputFiles('input[type="file"]', photo);
  await page.waitForFunction(() => !document.querySelector(".progress") && document.querySelectorAll(".tile img").length === 1);
  await page.click("form button.btn.primary");
  await page.waitForURL(/\/reports\/[0-9a-f-]{36}$/);
  reportUrl = page.url();
  return true;
});

await check("photo bytes went browser -> bucket (presigned PUT), never through the API", async () =>
  s3Puts.length === 1 && !s3Puts[0].includes("/api/") && Math.max(...apiUploadBodies) < 5000);

await check("photo shown via presigned GET and loads", async () => {
  const img = page.locator("img.main");
  await img.waitFor();
  const src = await img.getAttribute("src");
  await page.waitForFunction(() => document.querySelector("img.main")?.naturalWidth > 0);
  return src.includes("X-Amz-Signature") && src.includes("X-Amz-Expires=300");
});

await check("report is listed on the home feed", async () => {
  await page.goto(WEB);
  await page.locator(".report-card").first().waitFor();
  return (await page.locator(".report-card h3", { hasText: `تجربة ${tag}` }).count()) === 1;
});

await check("report is found by search", async () => {
  await page.fill("input.q", tag);
  await page.click(".filter-grid button.btn.primary");
  await page.waitForURL(new RegExp(`q=${tag}`));
  await page.waitForFunction(() => document.querySelectorAll(".report-card").length === 1);
  return (await page.locator(".report-card").getAttribute("href")) === new URL(reportUrl).pathname;
});

await check("English toggle switches to LTR", async () => {
  await page.click("text=English");
  return (await page.evaluate(() => document.dir)) === "ltr";
});

await check("clean up: delete the test report", async () => {
  await page.click("text=العربية");
  await page.goto(reportUrl);
  page.once("dialog", (d) => d.accept());
  await page.click("button.danger:has-text('حذف البلاغ')");
  await page.waitForURL(`${WEB}/`);
  return true;
});

await browser.close();
for (const [ok, name] of results) console.log(`${ok ? "PASS" : "FAIL"}  ${name}`);
const failed = results.filter(([ok]) => !ok).length;
console.log(`\n${results.length - failed}/${results.length} browser checks passed`);
process.exit(failed ? 1 : 0);
