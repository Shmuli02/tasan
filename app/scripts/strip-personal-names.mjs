#!/usr/bin/env node
/**
 * Roles-only guard. Recs may be regenerated with names by mistake;
 * the public app must never ship a known personal name from recs/.
 *
 *   node scripts/strip-personal-names.mjs --check <dir>
 *   node scripts/strip-personal-names.mjs --sanitize <dir>
 */
import fs from "node:fs";
import path from "node:path";
import { spawnSync } from "node:child_process";
import { fileURLToPath } from "node:url";

/** Surnames (and full names) that have appeared as role-holders in recs/. */
export const PERSONAL_NAME_PATTERNS = [
  { id: "Taskila", re: /\b(?:Jyri\s+J\.?\s+)?Taskila\b/gi },
  { id: "Kauranen", re: /\b(?:Henna\s+)?Kauranen\b/gi },
  { id: "Rajaniemi", re: /\b(?:Tuula\s+)?Rajaniemi\b/gi },
  { id: "Kuusisto", re: /\b(?:Mari\s+)?Kuusisto\b/gi },
  { id: "Ronkainen", re: /\b(?:Ari\s+)?Ronkainen\b/gi },
  { id: "Maksimow", re: /\b(?:Anu\s+)?Maksimow\b/gi },
];

const TEXT_EXT = new Set([
  ".js",
  ".mjs",
  ".cjs",
  ".css",
  ".html",
  ".json",
  ".md",
  ".svg",
  ".txt",
  ".map",
  ".xml",
  ".ts",
  ".tsx",
]);
const SKIP_DIR = new Set(["node_modules", ".git"]);
const SKIP_EXT = new Set([
  ".woff",
  ".woff2",
  ".ttf",
  ".otf",
  ".png",
  ".jpg",
  ".jpeg",
  ".ico",
  ".webp",
  ".gz",
  ".br",
]);

export function findPersonalNames(text) {
  const hits = [];
  for (const { id, re } of PERSONAL_NAME_PATTERNS) {
    re.lastIndex = 0;
    if (re.test(text)) hits.push(id);
  }
  return hits;
}

export function stripPersonalNames(text) {
  let t = String(text);
  t = t.replace(/\s*\((?:holder verified|verified on)[^)]*\)/gi, "");
  t = t.replace(
    /\s*Currently\s+(?:Jyri J\.?\s+Taskila|Henna Kauranen|Tuula Rajaniemi|Mari Kuusisto|Ari Ronkainen|Anu Maksimow)/gi,
    "",
  );
  for (const { re } of PERSONAL_NAME_PATTERNS) {
    re.lastIndex = 0;
    t = t.replace(re, "");
  }
  return t.replace(/\s{2,}/g, " ").replace(/\s+:/g, ":").replace(/:\s+,/g, ",").trim();
}

function stripValue(v) {
  if (typeof v === "string") return stripPersonalNames(v);
  if (Array.isArray(v)) return v.map(stripValue);
  if (v && typeof v === "object") {
    const o = {};
    for (const [k, val] of Object.entries(v)) o[k] = stripValue(val);
    return o;
  }
  return v;
}

function extractPdfText(file) {
  const r = spawnSync("pdftotext", ["-q", file, "-"], { encoding: "utf8" });
  if (r.status === 0) return r.stdout || "";
  return fs.readFileSync(file).toString("latin1");
}

export function checkPath(root) {
  const leaks = [];
  if (!fs.existsSync(root)) return leaks;
  const walk = (dir) => {
    for (const name of fs.readdirSync(dir)) {
      if (SKIP_DIR.has(name)) continue;
      const p = path.join(dir, name);
      const st = fs.statSync(p);
      if (st.isDirectory()) {
        walk(p);
        continue;
      }
      const ext = path.extname(name).toLowerCase();
      if (SKIP_EXT.has(ext)) continue;
      let text = "";
      if (ext === ".pdf") text = extractPdfText(p);
      else if (TEXT_EXT.has(ext) || ext === "") {
        try {
          text = fs.readFileSync(p, "utf8");
        } catch {
          continue;
        }
      } else continue;
      const hits = findPersonalNames(text);
      if (hits.length) leaks.push({ file: path.relative(root, p) || p, names: hits });
    }
  };
  const st = fs.statSync(root);
  if (st.isFile()) {
    const ext = path.extname(root).toLowerCase();
    const text = ext === ".pdf" ? extractPdfText(root) : fs.readFileSync(root, "utf8");
    const hits = findPersonalNames(text);
    if (hits.length) leaks.push({ file: root, names: hits });
  } else walk(root);
  return leaks;
}

export function sanitizeTree(root) {
  if (!fs.existsSync(root)) return 0;
  let changed = 0;
  const walk = (dir) => {
    for (const name of fs.readdirSync(dir)) {
      if (SKIP_DIR.has(name)) continue;
      const p = path.join(dir, name);
      const st = fs.statSync(p);
      if (st.isDirectory()) {
        walk(p);
        continue;
      }
      const ext = path.extname(name).toLowerCase();
      if (ext === ".json") {
        const raw = fs.readFileSync(p, "utf8");
        const next = JSON.stringify(stripValue(JSON.parse(raw)), null, 2) + "\n";
        if (next !== raw && findPersonalNames(raw).length) {
          fs.writeFileSync(p, next);
          changed += 1;
        }
      } else if (ext === ".md") {
        const raw = fs.readFileSync(p, "utf8");
        const hits = findPersonalNames(raw);
        if (hits.length) {
          fs.writeFileSync(p, stripPersonalNames(raw) + (raw.endsWith("\n") ? "\n" : ""));
          changed += 1;
        }
      }
    }
  };
  const st = fs.statSync(root);
  if (st.isDirectory()) walk(root);
  return changed;
}

export function assertNoPersonalNames(root, label = root) {
  const leaks = checkPath(root);
  if (leaks.length) {
    const lines = leaks.map((l) => `  - ${l.file}: ${l.names.join(", ")}`);
    console.error(`FATAL: personal names from recs/ appeared in ${label}:\n` + lines.join("\n"));
    process.exit(1);
  }
}

function main() {
  const args = process.argv.slice(2);
  const mode = args[0];
  const target = args[1] || path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..", "dist");
  if (mode === "--sanitize") {
    const n = sanitizeTree(target);
    console.log(`strip-personal-names: sanitized ${n} file(s) under ${target}`);
    assertNoPersonalNames(target, target);
    console.log("strip-personal-names: clean after sanitize");
    return;
  }
  if (mode === "--check" || !mode) {
    assertNoPersonalNames(target, target);
    console.log(`strip-personal-names: no personal names in ${target}`);
    return;
  }
  console.error("usage: strip-personal-names.mjs --check <dir> | --sanitize <dir>");
  process.exit(2);
}

if (process.argv[1] && path.resolve(process.argv[1]) === fileURLToPath(import.meta.url)) {
  main();
}
