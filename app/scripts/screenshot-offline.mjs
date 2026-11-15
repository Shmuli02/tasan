#!/usr/bin/env node
import { spawnSync } from "node:child_process";
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath, pathToFileURL } from "node:url";

const APP = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");
const html = path.join(APP, "dist-offline", "index.html");
const out = path.join(APP, "dist-offline", "screenshot.png");

if (!fs.existsSync(html)) {
  console.error("screenshot-offline: missing dist-offline/index.html — run npm run build:offline first");
  process.exit(1);
}

const chrome =
  process.env.CHROME_PATH ||
  ["/usr/bin/google-chrome-stable", "/usr/bin/google-chrome", "/usr/bin/chromium"].find((p) => fs.existsSync(p));
if (!chrome) {
  console.error("screenshot-offline: chrome not found");
  process.exit(1);
}

const fileUrl = pathToFileURL(html).href;
const args = [
  "--headless=new",
  "--disable-gpu",
  "--no-sandbox",
  "--hide-scrollbars",
  "--force-device-scale-factor=1",
  "--window-size=1600,2200",
  "--allow-file-access-from-files",
  // Block network: file:// page must still render if everything is inlined.
  "--host-resolver-rules=MAP * 0.0.0.0",
  "--proxy-server=http://127.0.0.1:1",
  `--screenshot=${out}`,
  fileUrl,
];
const shot = spawnSync(chrome, args, { stdio: "inherit" });
if (shot.status !== 0 || !fs.existsSync(out)) {
  console.error("screenshot-offline: chrome failed");
  process.exit(shot.status ?? 1);
}
console.log(`screenshot-offline: wrote ${out} (${fs.statSync(out).size} bytes) from ${fileUrl} with network blocked`);
