// One LIVE session filmed from both sides at the same time, in two real browser windows:
//   Heba (found a boy)  : logs in → posts a "found" report with his photo → sees the match → replies
//   Mona (his mother)   : sits on the feed → the notification arrives by itself (app polling) →
//                         opens the match → opens Heba's report → messages her → sees the reply
// Both screencasts share one clock: video/clips/live-heba, video/clips/live-mona (30 fps)
// and video/clips/live-events.json (seconds of each moment on that clock).
//   node video/live.mjs
import fs from "node:fs";
import path from "node:path";
import { launch, demoPassword, WEB } from "../web/scripts/browser.mjs";

const HERE = import.meta.dirname;
const FPS = 30;
const PASS = demoPassword();
const HEBA = "heba.farouk@example.com", MONA = "mona.salem@example.com";
const yesterday = new Date(Date.now() - 864e5).toISOString().slice(0, 10);

const CURSOR = `(() => { if (document.getElementById('__cur')) return;
  const c = document.createElement('div'); c.id = '__cur';
  c.style.cssText = 'position:fixed;left:0;top:0;width:26px;height:26px;margin:-13px 0 0 -13px;border-radius:50%;background:rgba(255,197,77,.92);box-shadow:0 0 0 6px rgba(255,197,77,.33),0 6px 14px rgba(0,0,0,.35);z-index:2147483647;pointer-events:none;transition:transform .12s';
  document.documentElement.appendChild(c); window.__curXY = window.__curXY || [innerWidth * .5, innerHeight * .55];
  c.style.left = window.__curXY[0] + 'px'; c.style.top = window.__curXY[1] + 'px'; })()`;
async function glide(p, target) {
  const loc = typeof target === "string" ? p.locator(target).first() : target;
  await loc.scrollIntoViewIfNeeded().catch(() => {});
  const box = await loc.boundingBox(); if (!box) throw new Error(`not found: ${target}`);
  await p.evaluate(CURSOR);
  await p.evaluate(async ([x, y]) => {
    const c = document.getElementById("__cur"), [x0, y0] = window.__curXY, t0 = performance.now(), D = 600;
    await new Promise((res) => { const f = (now) => { const k = Math.min(1, (now - t0) / D), e = 1 - Math.pow(1 - k, 3);
      c.style.left = x0 + (x - x0) * e + "px"; c.style.top = y0 + (y - y0) * e + "px"; k < 1 ? requestAnimationFrame(f) : res(); }; requestAnimationFrame(f); });
    window.__curXY = [x, y];
  }, [box.x + box.width / 2, box.y + box.height / 2]);
  return loc;
}
const tap = (p) => p.evaluate(() => { const c = document.getElementById("__cur"); if (c) { c.style.transform = "scale(.7)"; setTimeout(() => (c.style.transform = ""), 160); } });
async function click(p, t) { const l = await glide(p, t); await tap(p); await l.click(); await p.waitForTimeout(350); await p.evaluate(CURSOR); }
async function type(p, t, text, delay = 50) { const l = await glide(p, t); await tap(p); await l.click(); await l.fill(""); await p.keyboard.type(text, { delay }); }
async function scroll(p, y, ms = 1200) {
  await p.evaluate(([dy, d]) => new Promise((res) => { const y0 = scrollY, t0 = performance.now();
    const f = (now) => { const k = Math.min(1, (now - t0) / d), e = k < .5 ? 2 * k * k : 1 - Math.pow(-2 * k + 2, 2) / 2;
      scrollTo(0, y0 + dy * e); k < 1 ? requestAnimationFrame(f) : res(); }; requestAnimationFrame(f); }), [y, ms]);
}
const settle = async (p) => { await p.waitForLoadState("networkidle", { timeout: 6000 }).catch(() => {}); await p.evaluate(() => document.fonts.ready); await p.evaluate(CURSOR); };
async function login(p, email) {
  await p.goto(`${WEB}/login`); await p.fill('input[type="email"]', email); await p.fill('input[type="password"]', PASS);
  await p.click("button.btn.primary"); await p.waitForURL(`${WEB}/`);
}

const browser = await launch();
const ctxOpts = (geo) => ({ viewport: { width: 1440, height: 810 }, deviceScaleFactor: 4 / 3, colorScheme: "dark", locale: "ar-EG",
  geolocation: geo, permissions: geo ? ["geolocation"] : [] });

// ---- setup (not filmed): remove the previous take, clear Mona's unread notifications
const prevFile = path.join(HERE, "clips/posted-report.txt");
{
  const ctx = await browser.newContext(); const p = await ctx.newPage(); await login(p, HEBA);
  // delete every earlier take of Heba's report through the app (also removes its photos from the bucket)
  const ids = (process.env.OLD_REPORTS || "").split(",").filter(Boolean);
  if (fs.existsSync(prevFile)) ids.push(fs.readFileSync(prevFile, "utf8").trim().split("/").pop());
  for (const id of new Set(ids)) {
    await p.goto(`${WEB}/reports/${id}`); await p.waitForLoadState("networkidle");
    const del = p.locator("button.danger:has-text('حذف البلاغ')");
    if (await del.waitFor({ timeout: 5000 }).then(() => true, () => false)) {
      p.once("dialog", (d) => d.accept()); await del.click(); await p.waitForURL(`${WEB}/`); console.log("removed earlier take", id);
    }
  }
  fs.rmSync(prevFile, { force: true });
  await ctx.close();
}
const heba = await browser.newContext(ctxOpts({ latitude: 30.0802, longitude: 31.2448 }));
const mona = await browser.newContext(ctxOpts());
for (const c of [heba, mona]) await c.addInitScript(() => { localStorage.setItem("app-theme", "dark"); localStorage.setItem("app-locale", "ar"); });
const hp = await heba.newPage(), mp = await mona.newPage();
await login(mp, MONA);
await mp.goto(`${WEB}/notifications`); await settle(mp);
await mp.locator("button:has-text('تعليم الكل')").click().catch(() => {});
await mp.goto(WEB); await settle(mp);
await hp.goto(`${WEB}/login`); await settle(hp);

// ---- film both windows on one clock
const T0 = Date.now(); const ev = {}; const mark = (k) => { ev[k] = +((Date.now() - T0) / 1000).toFixed(2); console.log(k, ev[k]); };
async function film(page) {
  const cdp = await page.context().newCDPSession(page); const shots = [];
  cdp.on("Page.screencastFrame", (f) => { shots.push([Date.now(), Buffer.from(f.data, "base64")]); cdp.send("Page.screencastFrameAck", { sessionId: f.sessionId }).catch(() => {}); });
  await cdp.send("Page.startScreencast", { format: "jpeg", quality: 92, maxWidth: 1920, maxHeight: 1080, everyNthFrame: 1 });
  return { shots, stop: () => cdp.send("Page.stopScreencast").catch(() => {}) };
}
// navigation restarts a screencast in Chromium; restart it on every main-frame navigation
async function filmAll(page) {
  const all = []; let cur = await film(page); all.push(cur);
  page.on("framenavigated", async (f) => { if (f === page.mainFrame()) { cur = await film(page); all.push(cur); } });
  return { shots: () => all.flatMap((a) => a.shots).sort((a, b) => a[0] - b[0]), stop: async () => { for (const a of all) await a.stop(); } };
}
const recH = await filmAll(hp), recM = await filmAll(mp);
let hebaReportUrl = "";
let messageSent = false;

const hebaSide = (async () => {
  await hp.waitForTimeout(800);
  await type(hp, 'input[type="email"]', HEBA, 40);
  await glide(hp, 'input[type="password"]'); await tap(hp); await hp.locator('input[type="password"]').fill(PASS); await hp.waitForTimeout(300);
  await click(hp, "button.btn.primary"); await hp.waitForURL(`${WEB}/`); await settle(hp); mark("heba_logged_in");
  await hp.waitForTimeout(800);
  await click(hp, 'a[href="/reports/new"]'); await settle(hp); mark("heba_form");
  await click(hp, ".segmented button >> nth=1");
  const g = hp.locator("form select.input").first(); await glide(hp, g); await tap(hp); await g.selectOption("male");
  await type(hp, 'form input[type="number"]', "6", 80);
  const d = hp.locator('form input[type="date"]'); await glide(hp, d); await tap(hp); await d.fill(yesterday);
  const inputs = hp.locator("form .fields input.input:not([type])");
  await type(hp, inputs.nth(1), "القاهرة", 55); await type(hp, inputs.nth(2), "شبرا", 55);
  await click(hp, "text=📍");
  await type(hp, "form textarea", "لقيت ولد قاعد لوحده على رصيف محطة مترو روض الفرج، حوالي ٦ سنين، لابس سويتر أزرق تريكو. هو معايا دلوقتي وفي أمان.", 24);
  await glide(hp, ".field:has(input[type=file])").catch(() => {}); await tap(hp);
  await hp.setInputFiles('input[type="file"]', path.join(HERE, "photos/youssef-found.jpg")); mark("heba_photo");
  await hp.waitForFunction(() => !document.querySelector(".progress") && document.querySelectorAll(".tile img").length === 1);
  await hp.waitForTimeout(700);
  await click(hp, "form button.btn.primary"); mark("heba_submit");
  await hp.waitForURL(/\/reports\/[0-9a-f-]{36}$/); hebaReportUrl = hp.url(); fs.writeFileSync(prevFile, hebaReportUrl + "\n");
  await settle(hp); await hp.waitForTimeout(1500);
  for (let i = 0; i < 25 && (await hp.locator("text=لا توجد تطابقات بعد").count()); i++) { await hp.waitForTimeout(800); await hp.reload(); await settle(hp); }
  mark("heba_match_shown");
  await glide(hp, "text=تطابقات محتملة لهذا البلاغ"); await scroll(hp, 420, 1600); await hp.waitForTimeout(700);
  await glide(hp, "text=تشابه الصور"); await hp.waitForTimeout(2500);
  // wait for Mona's message to land (the app's own counters poll), then answer
  while (!messageSent) await hp.waitForTimeout(300);
  await hp.locator('a[href="/messages"] .badge').waitFor({ timeout: 40000 }); mark("heba_message_badge");
  await hp.waitForTimeout(1200);
  await click(hp, 'a[href="/messages"]'); await settle(hp);
  await click(hp, ".conv >> nth=0"); await hp.locator(".msg").first().waitFor(); await hp.waitForTimeout(1200);
  await type(hp, hp.locator("input.input.grow").last(), "أيوه يا حبيبتي، يوسف معايا في أمان 🤍 أنا في محطة روض الفرج، تعالي على طول.", 40);
  await hp.locator("input.input.grow").last().press("Enter"); mark("heba_reply"); await hp.waitForTimeout(2500);
})();

const monaSide = (async () => {
  // the notification arrives by itself — nothing is reloaded on Mona's side
  await mp.locator('a[href="/notifications"] .badge').waitFor({ timeout: 120000 }); mark("mona_badge");
  await mp.waitForTimeout(1500);
  await click(mp, 'a[href="/notifications"]'); await settle(mp); await mp.waitForTimeout(1200);
  await click(mp, "button.item.unread >> nth=0"); await settle(mp); mark("mona_open_match");
  await mp.waitForTimeout(1200);
  if (!mp.url().includes("/matches")) { await click(mp, 'a[href="/matches"]'); await settle(mp); }
  await glide(mp, "text=درجة التطابق >> nth=0"); await mp.waitForTimeout(1200);
  await glide(mp, "text=تشابه الصور >> nth=0"); await mp.waitForTimeout(1800);
  await click(mp, ".side >> nth=0"); await settle(mp); await mp.waitForTimeout(1500);
  if (!mp.url().startsWith(hebaReportUrl)) { await mp.goto(hebaReportUrl); await settle(mp); }
  await glide(mp, "img.main"); await mp.waitForTimeout(1500);
  await click(mp, "a.btn:has-text('✉')"); await settle(mp); await mp.waitForTimeout(700);
  await type(mp, mp.locator("input.input.grow").last(), "السلام عليكم، ده ابني يوسف 😭 أنا مامته، إنتي فين دلوقتي؟", 45);
  await mp.locator("input.input.grow").last().press("Enter"); mark("mona_message"); messageSent = true;
  // Heba's answer shows up in the open thread by itself (the thread polls)
  await mp.locator(".msg", { hasText: "روض الفرج" }).waitFor({ timeout: 60000 }); mark("mona_reply_seen");
  await mp.waitForTimeout(3000);
})();

await Promise.all([hebaSide, monaSide]);
const T1 = Date.now(); mark("end");
await recH.stop(); await recM.stop();
for (const [name, rec] of [["live-heba", recH], ["live-mona", recM]]) {
  const shots = rec.shots(); const dir = path.join(HERE, "clips", name);
  fs.rmSync(dir, { recursive: true, force: true }); fs.mkdirSync(dir, { recursive: true });
  const n = Math.round(((T1 - T0) / 1000) * FPS); let j = 0;
  for (let i = 0; i < n; i++) { const t = T0 + (i * 1000) / FPS; while (j + 1 < shots.length && shots[j + 1][0] <= t) j++; fs.writeFileSync(`${dir}/${String(i).padStart(4, "0")}.jpg`, shots[j][1]); }
  console.log(name, n, "frames from", shots.length, "screencast frames");
}
fs.writeFileSync(path.join(HERE, "clips/live-events.json"), JSON.stringify(ev, null, 1));
await browser.close();
