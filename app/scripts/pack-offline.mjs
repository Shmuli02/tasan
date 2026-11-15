#!/usr/bin/env node
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";
import { spawnSync } from "node:child_process";

const APP = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");
const DIR = path.join(APP, "dist-offline");
const htmlPath = path.join(DIR, "index.html");

if (!fs.existsSync(htmlPath)) {
  console.error("pack-offline: missing dist-offline/index.html");
  process.exit(1);
}

let html = fs.readFileSync(htmlPath, "utf8");

function resolveAsset(src) {
  const rel = src.replace(/^\.\//, "").replace(/^\//, "");
  const fp = path.join(DIR, rel);
  return fs.existsSync(fp) ? fp : null;
}

html = html.replace(/<script([^>]*?)\ssrc="([^"]+)"([^>]*)><\/script>/g, (m, pre, src, post) => {
  const fp = resolveAsset(src);
  if (!fp) return m;
  return `<script${pre}${post}>${fs.readFileSync(fp, "utf8")}</script>`;
});

html = html.replace(/<link([^>]*?)href="([^"]+\.css)"([^>]*)\/?>/g, (m, pre, href, post) => {
  const fp = resolveAsset(href);
  if (!fp) return m;
  return `<style${pre}${post}>${fs.readFileSync(fp, "utf8")}</style>`;
});

fs.writeFileSync(htmlPath, html);

const leftover = [...html.matchAll(/(?:src|href)=["']([^"']*assets\/[^"']+)["']/g)].map((x) => x[1]);
if (leftover.length) {
  console.error("pack-offline: still has external asset refs:", leftover);
  process.exit(1);
}

const py = `
import zipfile, pathlib
root = pathlib.Path(${JSON.stringify(DIR)})
html = root / "index.html"
zip_path = root / "tasan-offline.zip"
# Keep only the self-contained page in the zip (and a short readme).
readme = root / "README-offline.txt"
readme.write_text(
    "Tasan offline demo\\n"
    "Double-click index.html. It needs no network and no local server.\\n"
    "Open from file:// — all JS, CSS, fonts, map and data are inlined.\\n"
)
with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as z:
    z.write(html, "index.html")
    z.write(readme, "README-offline.txt")
print("pack-offline: index.html", html.stat().st_size, "bytes; zip", zip_path.stat().st_size)
`;
const res = spawnSync("python3", ["-c", py], { encoding: "utf8" });
if (res.status !== 0) {
  console.error(res.stderr || res.stdout);
  process.exit(res.status ?? 1);
}
process.stdout.write(res.stdout || "");
