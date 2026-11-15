#!/usr/bin/env node
import { spawn, spawnSync } from "node:child_process";
import fs from "node:fs";
import path from "node:path";
import http from "node:http";
import { fileURLToPath } from "node:url";

const APP = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");
const OUT = path.join(APP, "screenshot.png");
const PORT = 4173;
const URL = `http://127.0.0.1:${PORT}/`;

function waitFor(url, tries = 80) {
  return new Promise((resolve, reject) => {
    const tick = (n) => {
      const req = http.get(url, (res) => {
        res.resume();
        resolve(res.statusCode);
      });
      req.on("error", () => {
        if (n <= 0) reject(new Error("preview did not start"));
        else setTimeout(() => tick(n - 1), 250);
      });
    };
    tick(tries);
  });
}

if (!fs.existsSync(path.join(APP, "dist", "index.html"))) {
  const b = spawnSync("npm", ["run", "build"], { cwd: APP, stdio: "inherit" });
  if (b.status !== 0) process.exit(b.status ?? 1);
}

const preview = spawn("npx", ["vite", "preview", "--host", "127.0.0.1", "--port", String(PORT)], {
  cwd: APP,
  stdio: "inherit",
});

const chrome =
  process.env.CHROME_PATH ||
  ["/usr/bin/google-chrome-stable", "/usr/bin/google-chrome", "/usr/bin/chromium"].find((p) =>
    fs.existsSync(p),
  );

let code = 0;
try {
  await waitFor(URL);
  await new Promise((r) => setTimeout(r, 1500));
  if (!chrome) throw new Error("chrome not found");
  const args = [
    "--headless=new",
    "--disable-gpu",
    "--no-sandbox",
    "--hide-scrollbars",
    "--force-device-scale-factor=1",
    "--window-size=1600,2200",
    `--screenshot=${OUT}`,
    URL,
  ];
  const shot = spawnSync(chrome, args, { stdio: "inherit" });
  if (shot.status !== 0 || !fs.existsSync(OUT)) {
    console.error("screenshot: chrome failed");
    code = shot.status ?? 1;
  } else {
    console.log(`screenshot: wrote ${OUT} (${fs.statSync(OUT).size} bytes)`);
  }
} catch (e) {
  console.error("screenshot:", e);
  code = 1;
} finally {
  preview.kill("SIGTERM");
  setTimeout(() => {
    try {
      preview.kill("SIGKILL");
    } catch {}
    process.exit(code);
  }, 400);
}
