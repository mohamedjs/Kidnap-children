// Shared helpers for the browser scripts (e2e + screenshots).
import { existsSync, readFileSync } from "node:fs";
import { homedir } from "node:os";
import path from "node:path";
import { chromium } from "playwright";

export const WEB = process.env.WEB_URL ?? "http://localhost:3100";
export const ROOT = path.resolve(import.meta.dirname, "../..");

// Use the Chromium already in the local Playwright cache (no browser download).
function executable() {
  if (process.env.PW_CHROMIUM) return process.env.PW_CHROMIUM;
  const base = path.join(homedir(), ".cache/ms-playwright");
  const candidates = ["chromium_headless_shell-1248/chrome-headless-shell-linux64/chrome-headless-shell",
    "chromium-1248/chrome-linux64/chrome"].map((p) => path.join(base, p));
  return candidates.find(existsSync);
}

export function launch() {
  return chromium.launch({ executablePath: executable() });
}

// Demo accounts share ADMIN_SEED_PASSWORD from the gitignored .env (never printed).
export function demoPassword() {
  const env = readFileSync(path.join(ROOT, ".env"), "utf8");
  const m = env.match(/^ADMIN_SEED_PASSWORD=(.+)$/m);
  if (!m) throw new Error("ADMIN_SEED_PASSWORD missing in .env");
  return m[1].trim();
}

export async function login(page, email) {
  await page.goto(`${WEB}/login`);
  await page.fill('input[type="email"]', email);
  await page.fill('input[type="password"]', demoPassword());
  await page.click('button.btn.primary');
  await page.waitForURL(`${WEB}/`);
}
