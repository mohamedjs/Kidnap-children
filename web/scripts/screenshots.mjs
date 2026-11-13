// Sharp screenshots of the running app with the demo seed, for the landing site.
//   node scripts/screenshots.mjs [outDir]   (default ../site/assets/screens)
import { mkdirSync } from "node:fs";
import path from "node:path";
import { ROOT, WEB, launch, login } from "./browser.mjs";

const out = path.resolve(process.argv[2] ?? path.join(ROOT, "site/assets/screens"));
mkdirSync(out, { recursive: true });

const browser = await launch();

async function shoot({ name, url, user, theme = "dark", lang = "ar", width = 1360, height = 860, prep, full = false }) {
  const ctx = await browser.newContext({ viewport: { width, height }, deviceScaleFactor: 2, colorScheme: theme });
  await ctx.addInitScript(([t, l]) => {
    localStorage.setItem("app-theme", t);
    localStorage.setItem("app-locale", l);
  }, [theme, lang]);
  const page = await ctx.newPage();
  if (user) await login(page, user);
  await page.goto(`${WEB}${url}`);
  await page.waitForLoadState("networkidle");
  if (prep) await prep(page);
  await page.waitForFunction(() => [...document.images].filter((i) => i.getBoundingClientRect().top < innerHeight).every((i) => i.complete && i.naturalWidth > 0));
  await page.evaluate(() => document.fonts.ready);
  await page.screenshot({ path: path.join(out, `${name}.png`), fullPage: full });
  await ctx.close();
  console.log("shot", name);
}

const firstId = async (page, sel) => (await page.locator(sel).first().getAttribute("href"));

await shoot({ name: "home-ar-dark", url: "/" });
await shoot({ name: "home-ar-light", url: "/", theme: "light" });
await shoot({ name: "home-en-dark", url: "/", lang: "en" });
await shoot({ name: "home-en-light", url: "/", lang: "en", theme: "light" });
await shoot({ name: "mobile-home-en", url: "/", lang: "en", width: 390, height: 844 });
await shoot({ name: "search", url: "/?kind=missing&gender=female" });

// report page of the first missing report owned by mona
const ctx = await browser.newContext();
const p = await ctx.newPage();
await p.goto(`${WEB}/?q=${encodeURIComponent("يوسف")}`);
await p.locator(".report-card").first().waitFor();
const reportPath = await firstId(p, ".report-card");
await ctx.close();

await shoot({ name: "report", url: reportPath, user: "mona.salem@example.com", height: 1000 });
await shoot({ name: "report-light", url: reportPath, user: "mona.salem@example.com", theme: "light", height: 1000 });
await shoot({ name: "matches", url: "/matches", user: "mona.salem@example.com", height: 980 });
await shoot({ name: "new-report", url: "/reports/new", user: "heba.farouk@example.com", height: 980 });
await shoot({
  name: "messages", url: "/messages", user: "mona.salem@example.com",
  prep: async (page) => { await page.locator(".conv").first().click(); await page.locator(".msg").first().waitFor(); },
});
await shoot({ name: "profile", url: "/me", user: "karim.adel@example.com" });
await shoot({ name: "notifications", url: "/notifications", user: "mona.salem@example.com" });
await shoot({ name: "admin", url: "/admin", user: "admin@demo.local" });
await shoot({ name: "mobile-home", url: "/", width: 390, height: 844 });
await shoot({ name: "mobile-report", url: reportPath, width: 390, height: 844 });

await browser.close();
