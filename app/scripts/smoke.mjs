#!/usr/bin/env node
import { spawnSync } from "node:child_process";
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

const APP = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");

function run(cmd, args) {
  const res = spawnSync(cmd, args, { cwd: APP, stdio: "inherit", shell: false });
  if (res.status !== 0) {
    console.error(`smoke: command failed (${cmd} ${args.join(" ")}) exit ${res.status}`);
    process.exit(res.status ?? 1);
  }
}

console.log("smoke: sync + validate");
run("node", ["scripts/sync-data.mjs"]);

const content = path.join(APP, "src", "content");
for (const f of ["regions.json", "sources.json", "key_message.json", "recommendations.json", "counties.json", "_load_report.json"]) {
  const p = path.join(content, f);
  if (!fs.existsSync(p)) {
    console.error(`smoke: missing ${p}`);
    process.exit(1);
  }
  // touch-parse
  JSON.parse(fs.readFileSync(p, "utf8"));
}

const regions = JSON.parse(fs.readFileSync(path.join(content, "regions.json"), "utf8"));
const recs = JSON.parse(fs.readFileSync(path.join(content, "recommendations.json"), "utf8"));
if (!regions.regions || regions.regions.length < 22) {
  console.error("smoke: expected at least 22 regions");
  process.exit(1);
}
if (!recs.recommendations || recs.recommendations.length < 1) {
  console.error("smoke: expected at least one recommendation");
  process.exit(1);
}


for (const f of ["regions.json", "sources.json", "key_message.json", "recommendations.json", "hero.json"]) {
  const p = path.join(content, f);
  if (!fs.existsSync(p) && f === "hero.json") continue;
  if (!fs.existsSync(p)) { console.error("smoke: missing " + p); process.exit(1); }
  const raw = fs.readFileSync(p, "utf8");
  if (/"is_example"\s*:\s*true/i.test(raw) || /51\s*[–-]\s*76/.test(raw)) {
    console.error("smoke: example flag or synthetic 51–76% found in " + f);
    process.exit(1);
  }
}


const hero = JSON.parse(fs.readFileSync(path.join(content, "hero.json"), "utf8"));
const headlines = hero.headlines || [];
const lead = headlines.find((h) => h.id === "lung_curative_share") || headlines[0];
if (!lead) { console.error("smoke: hero.json missing headlines"); process.exit(1); }
const v = lead.value;
const valueOk = Array.isArray(v) || (v && typeof v === "object" && Array.isArray(v.men) && Array.isArray(v.women));
if (!valueOk) { console.error("smoke: lung_curative_share.value must be an array or {men, women}"); process.exit(1); }
if (typeof lead.measure_label !== "string" || !lead.measure_label) {
  console.error("smoke: missing measure_label on lead headline"); process.exit(1);
}
if (v && !Array.isArray(v) && v.men && v.women) {
  if (!lead.crude_secondary) { console.error("smoke: crude_secondary missing on object-valued lead headline"); process.exit(1); }
  const r0 = (lead.regions || [])[0] || {};
  if (!r0.men || typeof r0.men.value !== "number" || !r0.men.ci95) {
    console.error("smoke: lead regions must carry men/women {value, ci95}"); process.exit(1);
  }
}
if (/"src-sotkanet-6411"/.test(fs.readFileSync(path.join(content, "hero.json"), "utf8"))) {
  console.error("smoke: src-sotkanet-6411 leaked into hero.json"); process.exit(1);
}
const recList = recs.recommendations || [];
const top = recs.top3_ids || recList.filter((r) => r.top3).map((r) => r.id);
if (top[0] !== "T3") { console.error("smoke: top3 must start with T3, got " + JSON.stringify(top)); process.exit(1); }
for (const id of ["T3", "T1", "T2"]) {
  const r = recList.find((x) => x.id === id);
  if (!r) { console.error("smoke: missing rec " + id); process.exit(1); }
  for (const k of ["cost_range", "owner_role", "stop_go", "already_exists"]) {
    if (r[k] == null) { console.error(`smoke: ${id} missing ${k}`); process.exit(1); }
  }
}
console.log("smoke: hero + recs shapes OK (object-or-array value, measure_label, crude_secondary, T3 lead)");


console.log("smoke: production build");
run("npm", ["run", "build"]);

const dist = path.join(APP, "dist", "index.html");
if (!fs.existsSync(dist)) {
  console.error("smoke: dist/index.html not produced");
  process.exit(1);
}
const html = fs.readFileSync(dist, "utf8");
if (!html.includes("root") || !html.includes("script")) {
  console.error("smoke: dist/index.html looks incomplete");
  process.exit(1);
}
const assets = fs.readdirSync(path.join(APP, "dist", "assets"));
if (!assets.some((n) => n.endsWith(".js")) || !assets.some((n) => n.endsWith(".css"))) {
  console.error("smoke: expected JS and CSS in dist/assets");
  process.exit(1);
}

console.log("smoke: OK (JSON valid, build succeeded, dist has index + js + css)");
