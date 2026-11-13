// Films the REAL running app (dev stack: web :3100, api :4100, worker) for the product video.
// A fake cursor glides to every target; frames come from a CDP screencast resampled to FPS.
//   node video/film.mjs [clipId …]      → video/clips/<id>/0000.jpg …, video/stills/<id>.png
// Demo data only (seed users, generated silhouettes). Passwords come from the gitignored .env.
import fs from "node:fs";
import path from "node:path";
import { launch, login, demoPassword, WEB } from "../web/scripts/browser.mjs";

const HERE = import.meta.dirname;
const FPS = 30;
const [W, H] = [1440, 810];
const only = process.argv.slice(2);
const photo = path.join(HERE, "demo/found.jpg");
const yesterday = new Date(Date.now() - 864e5).toISOString().slice(0, 10);

const CURSOR = `(() => { if (document.getElementById('__cur')) return;
  const c = document.createElement('div'); c.id = '__cur';
  c.style.cssText = 'position:fixed;left:0;top:0;width:26px;height:26px;margin:-13px 0 0 -13px;border-radius:50%;background:rgba(255,197,77,.92);box-shadow:0 0 0 6px rgba(255,197,77,.33),0 6px 14px rgba(0,0,0,.35);z-index:2147483647;pointer-events:none;transition:transform .12s';
  document.documentElement.appendChild(c); window.__curXY = window.__curXY || [innerWidth * .5, innerHeight * .55];
  c.style.left = window.__curXY[0] + 'px'; c.style.top = window.__curXY[1] + 'px'; })()`;

async function glide(p, target) {
  const loc = typeof target === "string" ? p.locator(target).first() : target;
  await loc.scrollIntoViewIfNeeded().catch(() => {});
  const box = await loc.boundingBox();
  if (!box) throw new Error(`not found: ${target}`);
  await p.evaluate(CURSOR);
  await p.evaluate(async ([x, y]) => {
    const c = document.getElementById("__cur"), [x0, y0] = window.__curXY, t0 = performance.now(), D = 600;
    await new Promise((res) => { const f = (now) => { const k = Math.min(1, (now - t0) / D), e = 1 - Math.pow(1 - k, 3);
      c.style.left = x0 + (x - x0) * e + "px"; c.style.top = y0 + (y - y0) * e + "px"; k < 1 ? requestAnimationFrame(f) : res(); }; requestAnimationFrame(f); });
    window.__curXY = [x, y];
  }, [box.x + box.width / 2, box.y + box.height / 2]);
  return loc;
}
const tap = (p) => p.evaluate(() => { const c = document.getElementById("__cur"); c.style.transform = "scale(.7)"; setTimeout(() => (c.style.transform = ""), 160); });
async function click(p, target) { const loc = await glide(p, target); await tap(p); await loc.click(); await p.waitForTimeout(350); }
async function type(p, target, text, delay = 55) { const loc = await glide(p, target); await tap(p); await loc.click(); await loc.fill(""); await p.keyboard.type(text, { delay }); }
async function scroll(p, y, ms = 1200) {
  await p.evaluate(([dy, d]) => new Promise((res) => { const y0 = scrollY, t0 = performance.now();
    const f = (now) => { const k = Math.min(1, (now - t0) / d), e = k < .5 ? 2 * k * k : 1 - Math.pow(-2 * k + 2, 2) / 2;
      scrollTo(0, y0 + dy * e); k < 1 ? requestAnimationFrame(f) : res(); }; requestAnimationFrame(f); }), [y, ms]);
}
const settle = async (p) => {
  await p.waitForLoadState("networkidle", { timeout: 6000 }).catch(() => {});
  await p.waitForFunction(() => [...document.images].filter((i) => i.getBoundingClientRect().top < innerHeight).every((i) => i.complete)).catch(() => {});
  await p.evaluate(() => document.fonts.ready);
};

// ---------- clips ----------
const clips = {
  // the public feed, logged out
  async home(p) {
    await p.goto(WEB); await settle(p);
    return async () => {
      await p.waitForTimeout(800);
      await glide(p, ".report-card >> nth=1"); await p.waitForTimeout(500);
      await scroll(p, 520, 2200); await p.waitForTimeout(700);
      await glide(p, ".report-card >> nth=4"); await p.waitForTimeout(600);
      await scroll(p, -520, 1600); await p.waitForTimeout(600);
    };
  },

  // log in as a volunteer
  async login(p) {
    await p.goto(`${WEB}/login`); await settle(p);
    return async () => {
      await p.waitForTimeout(500);
      await type(p, 'input[type="email"]', "heba@demo.local", 45);
      await p.waitForTimeout(250);
      await glide(p, 'input[type="password"]'); await tap(p);
      await p.locator('input[type="password"]').fill(demoPassword());
      await p.waitForTimeout(400);
      await click(p, "button.btn.primary");
      await p.waitForURL(`${WEB}/`); await settle(p); await p.waitForTimeout(1200);
    };
  },

  // post a "found" report with a photo (presigned PUT straight to the bucket)
  async post(p) {
    await login(p, "heba@demo.local");
    const prev = path.join(HERE, "clips/posted-report.txt");
    if (fs.existsSync(prev)) { // remove the previous take through the app (also deletes its photos from the bucket)
      await p.goto(fs.readFileSync(prev, "utf8").trim()); await settle(p);
      const del = p.locator("button.danger:has-text('حذف البلاغ')");
      if (await del.count()) { p.once("dialog", (d) => d.accept()); await del.click(); await p.waitForURL(`${WEB}/`); console.log("  removed previous take"); }
      fs.rmSync(prev);
    }
    await p.goto(`${WEB}/reports/new`); await settle(p);
    const puts = [];
    p.on("request", (r) => { if (r.method() === "PUT" && r.url().includes("X-Amz-Signature")) puts.push(new URL(r.url()).host); });
    return async () => {
      await p.waitForTimeout(500);
      await click(p, ".segmented button >> nth=1");
      await p.waitForTimeout(300);
      const gender = p.locator("form select.input").first();
      await glide(p, gender); await tap(p); await gender.selectOption("male"); await p.waitForTimeout(250);
      await type(p, 'form input[type="number"]', "6", 80);
      const date = p.locator('form input[type="date"]');
      await glide(p, date); await tap(p); await date.fill(yesterday); await p.waitForTimeout(250);
      const inputs = p.locator("form .fields input.input:not([type])");
      await type(p, inputs.nth(1), "القاهرة", 60);
      await type(p, inputs.nth(2), "شبرا", 60);
      await click(p, "text=📍");
      await p.waitForTimeout(500);
      await type(p, "form textarea", "لقيت ولد تايه جنب محطة المترو، حوالي ٦ سنين، لابس سويتر أزرق. هو معانا دلوقتي وفي أمان.", 28);
      await glide(p, ".field:has(input[type=file])").catch(() => {});
      await tap(p);
      await p.setInputFiles('input[type="file"]', photo);
      await p.waitForFunction(() => !document.querySelector(".progress") && document.querySelectorAll(".tile img").length === 1);
      await p.waitForTimeout(900);
      await click(p, "form button.btn.primary");
      await p.waitForURL(/\/reports\/[0-9a-f-]{36}$/); await settle(p);
      await p.waitForFunction(() => document.querySelector("img.main")?.naturalWidth > 0);
      await p.waitForTimeout(1400);
      // the worker matches in the background; reload once it has suggested something
      for (let i = 0; i < 20 && (await p.locator("text=لا توجد تطابقات بعد").count()); i++) { await p.waitForTimeout(800); await p.reload(); await settle(p); }
      await p.evaluate(CURSOR);
      await glide(p, "text=تطابقات محتملة لهذا البلاغ"); await p.waitForTimeout(400);
      await scroll(p, 420, 1600); await p.waitForTimeout(1800);
      console.log("  report:", p.url(), "· presigned PUT host:", puts.join(","));
      fs.writeFileSync(path.join(HERE, "clips/posted-report.txt"), p.url() + "\n");
    };
  },

  // search the feed
  async search(p) {
    await p.goto(WEB); await settle(p);
    return async () => {
      await p.waitForTimeout(500);
      await type(p, "input.q", "سويتر أزرق", 70);
      await p.waitForTimeout(300);
      await click(p, ".filter-grid button.btn.primary");
      await p.waitForURL(/q=/); await settle(p); await p.waitForTimeout(1000);
      await glide(p, ".report-card >> nth=0"); await p.waitForTimeout(1500);
    };
  },

  // the parent of the missing child: notification, then the suggested match
  async match(p) {
    await login(p, "mona@demo.local");
    await p.goto(`${WEB}/notifications`); await settle(p);
    return async () => {
      await p.waitForTimeout(800);
      await glide(p, ".notif, li, .card >> nth=0").catch(() => {});
      await p.waitForTimeout(900);
      await click(p, 'a[href="/matches"]');
      await settle(p); await p.waitForTimeout(900);
      await glide(p, "text=درجة التطابق >> nth=0"); await p.waitForTimeout(900);
      await scroll(p, 260, 1500); await p.waitForTimeout(500);
      await glide(p, "button:has-text('هذا هو الطفل') >> nth=0"); await p.waitForTimeout(1500);
    };
  },

  // private message to the reporter
  async messages(p) {
    await login(p, "mona@demo.local");
    await p.goto(`${WEB}/messages`); await settle(p);
    return async () => {
      await p.waitForTimeout(500);
      await click(p, ".conv >> nth=0");
      await p.locator(".msg").first().waitFor(); await p.waitForTimeout(1200);
      const box = p.locator("form textarea, form input.input").last();
      await type(p, box, "شكرًا جدًا، أنا جاية حالًا على القسم 🙏", 55);
      await p.waitForTimeout(1200);
    };
  },
};

// ---------- runner ----------
const browser = await launch();
fs.mkdirSync(path.join(HERE, "clips"), { recursive: true });
fs.mkdirSync(path.join(HERE, "stills"), { recursive: true });
for (const [id, prepare] of Object.entries(clips)) {
  if (only.length && !only.includes(id)) continue;
  const ctx = await browser.newContext({
    viewport: { width: W, height: H }, deviceScaleFactor: 4 / 3, colorScheme: "dark", locale: "ar-EG",
    geolocation: { latitude: 30.0802, longitude: 31.2448 }, permissions: ["geolocation"],
  });
  await ctx.addInitScript(() => { localStorage.setItem("app-theme", "dark"); localStorage.setItem("app-locale", "ar"); });
  const p = await ctx.newPage();
  const act = await prepare(p);
  await p.evaluate(CURSOR);
  const cdp = await ctx.newCDPSession(p);
  const shots = [];
  cdp.on("Page.screencastFrame", (f) => { shots.push([Date.now(), Buffer.from(f.data, "base64")]); cdp.send("Page.screencastFrameAck", { sessionId: f.sessionId }).catch(() => {}); });
  await cdp.send("Page.startScreencast", { format: "jpeg", quality: 92, maxWidth: 1920, maxHeight: 1080, everyNthFrame: 1 });
  const t0 = Date.now();
  await act();
  const t1 = Date.now();
  await cdp.send("Page.stopScreencast").catch(() => {});
  await p.evaluate(() => document.getElementById("__cur")?.remove());
  await p.screenshot({ path: path.join(HERE, `stills/${id}.png`) });
  await ctx.close();
  const dir = path.join(HERE, `clips/${id}`);
  fs.rmSync(dir, { recursive: true, force: true }); fs.mkdirSync(dir, { recursive: true });
  const n = Math.round(((t1 - t0) / 1000) * FPS); let j = 0;
  for (let i = 0; i < n; i++) {
    const t = t0 + (i * 1000) / FPS; while (j + 1 < shots.length && shots[j + 1][0] <= t) j++;
    fs.writeFileSync(`${dir}/${String(i).padStart(4, "0")}.jpg`, shots[j][1]);
  }
  console.log(id, `${((t1 - t0) / 1000).toFixed(1)} s`, n, "frames", `(${shots.length} screencast frames)`);
}
await browser.close();
