#!/usr/bin/env node
/**
 * Copy + validate team JSON from /workspace/junction-new/{data,recs}
 * into app/src/content. Always re-runs extract_team_data.py so a regenerated
 * recs/recommendations.json is picked up. Example-data is a last-resort fallback
 * and the build FAILS if any is_example flag or synthetic 51–76% rate would ship.
 */
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";
import { spawnSync } from "node:child_process";
import { sanitizeTree, assertNoPersonalNames } from "./strip-personal-names.mjs";

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const APP = path.resolve(__dirname, "..");
const ROOT = path.resolve(APP, "..");
const TEAM_DATA = path.join(ROOT, "data");
const TEAM_RECS = path.join(ROOT, "recs");
const EXAMPLE = path.join(APP, "example-data");
const OUT = path.join(APP, "src", "content");

const FILES = [
  { key: "regions", rel: "data/regions.json", team: path.join(TEAM_DATA, "regions.json") },
  { key: "sources", rel: "data/sources.json", team: path.join(TEAM_DATA, "sources.json") },
  { key: "key_message", rel: "data/key_message.json", team: path.join(TEAM_DATA, "key_message.json") },
  { key: "recommendations", rel: "recs/recommendations.json", team: path.join(TEAM_RECS, "recommendations.json") },
  { key: "counties", rel: "data/counties.geojson", team: path.join(TEAM_DATA, "counties.geojson"), optional: true },
];

const STAGES = new Set(["detection", "referral", "diagnosis", "treatment"]);
const REGION_TYPES = new Set(["wellbeing_services_county", "city", "autonomous_region"]);

function readJson(file) {
  const raw = fs.readFileSync(file, "utf8");
  return JSON.parse(raw);
}

function fail(errors, msg) {
  errors.push(msg);
}

function asObj(v) {
  return v && typeof v === "object" && !Array.isArray(v);
}

function validateSources(doc, errors) {
  if (!asObj(doc) || !Array.isArray(doc.sources)) {
    return fail(errors, "sources.json: missing sources[]");
  }
  const ids = new Set();
  for (const s of doc.sources) {
    if (!s || typeof s.id !== "string" || !s.id) fail(errors, "sources.json: a source is missing id");
    else if (ids.has(s.id)) fail(errors, `sources.json: duplicate id ${s.id}`);
    else ids.add(s.id);
    if (!s.title) fail(errors, `sources.json: ${s.id} missing title`);
    if (!s.publisher) fail(errors, `sources.json: ${s.id} missing publisher`);
  }
  return ids;
}

function validateRegions(doc, sourceIds, errors) {
  if (!asObj(doc)) return fail(errors, "regions.json: not an object");
  if (!asObj(doc.meta)) fail(errors, "regions.json: missing meta");
  if (!Array.isArray(doc.stages) || doc.stages.length < 1) fail(errors, "regions.json: missing stages[]");
  if (!Array.isArray(doc.indicator_catalog) || doc.indicator_catalog.length < 1) {
    fail(errors, "regions.json: missing indicator_catalog[]");
  }
  if (!asObj(doc.national)) fail(errors, "regions.json: missing national");
  if (!Array.isArray(doc.regions)) fail(errors, "regions.json: missing regions[]");

  const catalogIds = new Set();
  for (const c of doc.indicator_catalog || []) {
    if (!c?.id) fail(errors, "regions.json: catalog entry missing id");
    else catalogIds.add(c.id);
    if (c.stage && !STAGES.has(c.stage)) fail(errors, `regions.json: catalog ${c.id} has invalid stage ${c.stage}`);
    if (c.target_source_id && sourceIds.size && !sourceIds.has(c.target_source_id)) {
      fail(errors, `regions.json: catalog ${c.id} target_source_id ${c.target_source_id} not in sources.json`);
    }
  }

  const checkIndicators = (owner, list) => {
    if (!Array.isArray(list)) return fail(errors, `regions.json: ${owner} missing indicators[]`);
    for (const ind of list) {
      if (!ind?.id) fail(errors, `regions.json: ${owner} has an indicator without id`);
      if (!catalogIds.has(ind.id)) fail(errors, `regions.json: ${owner} indicator ${ind.id} not in catalog`);
      if (ind.value != null && typeof ind.value !== "number") {
        fail(errors, `regions.json: ${owner} indicator ${ind.id} value must be a number or null`);
      }
      if (ind.source_id && sourceIds.size && !sourceIds.has(ind.source_id)) {
        fail(errors, `regions.json: ${owner} indicator ${ind.id} source_id ${ind.source_id} not in sources.json`);
      }
    }
  };

  if (doc.national) checkIndicators("national", doc.national.indicators);

  const seen = new Set();
  for (const r of doc.regions || []) {
    if (!r?.id) fail(errors, "regions.json: a region is missing id");
    else if (seen.has(r.id)) fail(errors, `regions.json: duplicate region id ${r.id}`);
    else seen.add(r.id);
    if (!r.name) fail(errors, `regions.json: region ${r.id} missing name`);
    if (r.type && !REGION_TYPES.has(r.type)) fail(errors, `regions.json: region ${r.id} invalid type ${r.type}`);
    checkIndicators(`region ${r.id}`, r.indicators);
  }

  const required = ["01","02","03","04","05","06","07","08","09","10","11","12","13","14","15","16","17","18","19","20","21","90"];
  const missing = required.filter((id) => !seen.has(id));
  if (missing.length) fail(errors, `regions.json: missing required region ids: ${missing.join(", ")}`);
}

function validateKeyMessage(doc, errors) {
  if (!asObj(doc)) return fail(errors, "key_message.json: not an object");
  if (!asObj(doc.meta)) fail(errors, "key_message.json: missing meta");
}

function validateRecs(doc, sourceIds, errors) {
  if (!asObj(doc)) return fail(errors, "recommendations.json: not an object");
  if (!asObj(doc.meta)) fail(errors, "recommendations.json: missing meta");
  if (!Array.isArray(doc.recommendations) || doc.recommendations.length < 1) {
    return fail(errors, "recommendations.json: missing recommendations[]");
  }
  const seen = new Set();
  for (const r of doc.recommendations) {
    if (!r?.id) fail(errors, "recommendations.json: a recommendation is missing id");
    else if (seen.has(r.id)) fail(errors, `recommendations.json: duplicate id ${r.id}`);
    else seen.add(r.id);
    if (!r.title) fail(errors, `recommendations.json: ${r.id} missing title`);
    if (!r.what && !r.action) fail(errors, `recommendations.json: ${r.id} missing what/action`);
    if (r.stage && !STAGES.has(r.stage)) fail(errors, `recommendations.json: ${r.id} invalid stage ${r.stage}`);
    const srcs = [...(r.evidence_source_ids || []), r.expected_effect?.source_id, r.cost?.source_id].filter(Boolean);
    for (const sid of srcs) {
      if (sourceIds.size && !sourceIds.has(sid)) {
        fail(errors, `recommendations.json: ${r.id} source_id ${sid} not in sources.json`);
      }
    }
    if (r.effect_params) {
      const p = r.effect_params;
      if (typeof p.effect_at_full_coverage !== "number") {
        fail(errors, `recommendations.json: ${r.id} effect_params.effect_at_full_coverage must be a number`);
      }
      if (!p.applies_to_indicator) {
        fail(errors, `recommendations.json: ${r.id} effect_params.applies_to_indicator missing`);
      }
    }
  }
}

function validateCounties(doc, errors) {
  if (!asObj(doc) || doc.type !== "FeatureCollection" || !Array.isArray(doc.features)) {
    return fail(errors, "counties.geojson: must be a FeatureCollection");
  }
  if (doc.features.length < 22) fail(errors, `counties.geojson: expected at least 22 features, got ${doc.features.length}`);
  for (const f of doc.features) {
    const id = f?.properties?.id;
    if (!id) fail(errors, "counties.geojson: a feature is missing properties.id");
    if (!f.geometry) fail(errors, `counties.geojson: feature ${id} missing geometry`);
  }
}

function tryLoad(file) {
  if (!fs.existsSync(file)) return { ok: false, error: `file not found: ${file}` };
  try {
    return { ok: true, doc: readJson(file) };
  } catch (e) {
    return { ok: false, error: `invalid JSON in ${file}: ${e.message}` };
  }
}


function collectExampleViolations(doc, path, out) {
  if (doc == null) return;
  if (typeof doc === "string") {
    if (/51\s*[–-]\s*76/.test(doc) || /ranges from 51% to 76%/i.test(doc)) {
      out.push(`${path}: synthetic 51–76% on-time range`);
    }
    return;
  }
  if (Array.isArray(doc)) {
    doc.forEach((v, i) => collectExampleViolations(v, `${path}[${i}]`, out));
    return;
  }
  if (typeof doc === "object") {
    if (doc.is_example === true) out.push(`${path}.is_example is true`);
    for (const [k, v] of Object.entries(doc)) collectExampleViolations(v, `${path}.${k}`, out);
  }
}


function internSources(doc) {
  const catalog = [];
  const map = new Map();
  function sid(url, table) {
    const k = `${url ?? ""}\0${table ?? ""}`;
    if (map.has(k)) return map.get(k);
    const id = `s${catalog.length + 1}`;
    catalog.push({ id, source_url: url ?? null, source_table: table ?? null });
    map.set(k, id);
    return id;
  }
  function walk(node) {
    if (Array.isArray(node)) return node.map(walk);
    if (!node || typeof node !== "object") return node;
    const hasUrl = Object.prototype.hasOwnProperty.call(node, "source_url");
    const hasTable = Object.prototype.hasOwnProperty.call(node, "source_table");
    const out = {};
    for (const [k, v] of Object.entries(node)) {
      if (k === "source_url" || k === "source_table") continue;
      out[k] = walk(v);
    }
    if (hasUrl || hasTable) out.sid = sid(node.source_url, node.source_table);
    return out;
  }
  const body = walk(doc);
  body.sid_catalog = catalog;
  return body;
}

function syncChartData() {
  const srcDir = path.join(TEAM_DATA, "app");
  const destDir = path.join(OUT, "charts");
  fs.mkdirSync(destDir, { recursive: true });
  const files = [
    ["curative_agestd_ranked.json", "curative_agestd_ranked.json"],
    ["timeseries.json", "timeseries.json"],
    ["pathway_by_county.json", "pathway_by_county.json"],
    ["pathway.json", "pathway.json"],
    ["yta.json", "yta.json"],
    ["counties.json", "county_profiles.json"],
  ];
  const written = [];
  for (const [srcName, destName] of files) {
    const src = path.join(srcDir, srcName);
    if (!fs.existsSync(src)) {
      console.error(`FATAL: required chart data missing: data/app/${srcName}`);
      process.exit(1);
    }
    const compact = internSources(readJson(src));
    const dest = path.join(destDir, destName);
    fs.writeFileSync(dest, JSON.stringify(compact));
    written.push({ name: destName, bytes: fs.statSync(dest).size, sources: compact.sid_catalog.length });
  }
  console.log("sync-data: chart packs -> src/content/charts/");
  for (const w of written) console.log(`  ${w.name}: ${w.bytes} bytes, ${w.sources} unique sources`);
  return written.map((w) => w.name);
}

function tryExtractTeamData() {
  const extract = path.join(APP, "scripts", "extract_team_data.py");
  const csvDir = path.join(TEAM_DATA, "csv");
  if (!fs.existsSync(extract) || !fs.existsSync(csvDir)) return { ok: false, error: "no extractor or csv/" };
  const staging = path.join(APP, ".staging-team");
  fs.mkdirSync(staging, { recursive: true });
  const res = spawnSync("python3", [extract, staging], { encoding: "utf8" });
  if (res.status !== 0) {
    return { ok: false, error: (res.stderr || res.stdout || "extract failed").slice(0, 2000) };
  }
  return { ok: true, staging, log: res.stdout };
}

function main() {
  fs.mkdirSync(OUT, { recursive: true });
  const extracted = tryExtractTeamData();

  const report = {
    used_example: false,
    is_example: false,
    errors: [],
    warnings: [],
    loaded_from: {},
    files: {},
    synced_at: new Date().toISOString(),
  };

  const loaded = {};
  const teamErrors = [];
  if (extracted.ok) {
    console.log(extracted.log.trim());
  } else if (extracted.error) {
    console.log("sync-data: extract skipped/failed —", extracted.error.split("\n")[0]);
  }

  for (const f of FILES) {
    const teamPath = extracted.ok
      ? path.join(extracted.staging, path.basename(f.rel === "recs/recommendations.json" ? "recommendations.json" : f.rel === "data/counties.geojson" ? "" : path.basename(f.rel)))
      : f.team;
    // counties still come from example/team geo, not the extractor
    const team = f.key === "counties"
      ? tryLoad(f.team)
      : tryLoad(extracted.ok && f.key !== "counties" ? path.join(extracted.staging, ({regions:"regions.json",sources:"sources.json",key_message:"key_message.json",recommendations:"recommendations.json"}[f.key])) : f.team);
    if (team.ok) {
      loaded[f.key] = { doc: team.doc, from: "team", path: f.team };
    } else {
      if (!f.optional || fs.existsSync(f.team)) teamErrors.push(team.error);
      const exPath = path.join(EXAMPLE, f.rel);
      const ex = tryLoad(exPath);
      if (!ex.ok) {
        console.error(`FATAL: example fallback also failed for ${f.key}: ${ex.error}`);
        process.exit(1);
      }
      loaded[f.key] = { doc: ex.doc, from: "example", path: exPath, teamError: team.error };
    }
  }

  // Prefer an all-team or all-example consistent set. If ANY required team file
  // is missing/invalid, fall back entirely so we never mix real and example numbers.
  const requiredKeys = FILES.filter((f) => !f.optional).map((f) => f.key);
  const anyTeamMissing = requiredKeys.some((k) => loaded[k].from !== "team");
  const allTeam = requiredKeys.every((k) => loaded[k].from === "team");

  if (anyTeamMissing && !allTeam) {
    report.used_example = true;
    for (const f of FILES) {
      if (loaded[f.key].from === "team") {
        report.warnings.push(`Ignoring team ${f.key} because other required files are missing/invalid (refusing to mix example and team data).`);
      }
      const exPath = path.join(EXAMPLE, f.rel);
      const ex = tryLoad(exPath);
      if (!ex.ok) {
        console.error(`FATAL: example fallback failed for ${f.key}: ${ex.error}`);
        process.exit(1);
      }
      loaded[f.key] = { doc: ex.doc, from: "example", path: exPath, teamError: loaded[f.key].teamError };
    }
  }

  const errors = [];
  const sourceIds = validateSources(loaded.sources.doc, errors) || new Set();
  validateRegions(loaded.regions.doc, sourceIds, errors);
  validateKeyMessage(loaded.key_message.doc, errors);
  validateRecs(loaded.recommendations.doc, sourceIds, errors);
  validateCounties(loaded.counties.doc, errors);

  if (errors.length) {
    if (allTeam) {
      report.warnings.push("Team dataset failed validation; falling back to example data.");
      for (const e of errors) report.warnings.push(e);
      for (const f of FILES) {
        const exPath = path.join(EXAMPLE, f.rel);
        const ex = tryLoad(exPath);
        if (!ex.ok) {
          console.error(`FATAL: example fallback failed for ${f.key}: ${ex.error}`);
          process.exit(1);
        }
        loaded[f.key] = { doc: ex.doc, from: "example-fallback", path: exPath };
      }
      report.used_example = true;
      // Example data should validate; if it doesn't, abort.
      const errors2 = [];
      const sourceIds2 = validateSources(loaded.sources.doc, errors2) || new Set();
      validateRegions(loaded.regions.doc, sourceIds2, errors2);
      validateKeyMessage(loaded.key_message.doc, errors2);
      validateRecs(loaded.recommendations.doc, sourceIds2, errors2);
      validateCounties(loaded.counties.doc, errors2);
      if (errors2.length) {
        console.error("FATAL: example data itself is invalid:\n" + errors2.map((e) => "  - " + e).join("\n"));
        process.exit(1);
      }
    } else {
      console.error("FATAL: example data failed validation:\n" + errors.map((e) => "  - " + e).join("\n"));
      process.exit(1);
    }
  }

  // County geometry may come from the bundled Statistics Finland file; that is not "example indicators".
  const contentKeys = ["regions", "sources", "key_message", "recommendations"];
  report.used_example = contentKeys.some((k) => String(loaded[k].from).startsWith("example"));
  report.is_example = Boolean(loaded.regions.doc.meta?.is_example);
  report.recs_are_example = Boolean(loaded.recommendations.doc.meta?.is_example);
  report.key_message_is_example = Boolean(loaded.key_message.doc.meta?.is_example);

  if (teamErrors.length && report.used_example) {
    for (const e of teamErrors) report.warnings.push(e);
  }

  for (const f of FILES) {
    const basename = f.key === "counties" ? "counties.json" : path.basename(f.rel);
    const dest = path.join(OUT, basename);
    fs.writeFileSync(dest, JSON.stringify(loaded[f.key].doc, null, 2) + "\n");
    report.loaded_from[f.key] = loaded[f.key].from;
    report.files[f.key] = dest;
  }

  const factsSrc = path.join(TEAM_DATA, "facts.json");
  const factsDst = path.join(OUT, "facts.json");
  if (fs.existsSync(factsSrc)) {
    fs.copyFileSync(factsSrc, factsDst);
  } else if (!fs.existsSync(factsDst)) {
    console.error("FATAL: data/facts.json is required grounding and was not found.");
    process.exit(1);
  }

  if (extracted.ok) {
    const heroSrc = path.join(extracted.staging, "hero.json");
    if (fs.existsSync(heroSrc)) fs.copyFileSync(heroSrc, path.join(OUT, "hero.json"));
  } else if (!fs.existsSync(path.join(OUT, "hero.json"))) {
    // keep a minimal hero so the app import never breaks
    const fallback = path.join(EXAMPLE, "data", "hero.json");
    if (fs.existsSync(fallback)) fs.copyFileSync(fallback, path.join(OUT, "hero.json"));
  }

  const briefSrc = path.join(TEAM_RECS, "pilot_brief.md");
  const briefDst = path.join(OUT, "pilot_brief.md");
  if (fs.existsSync(briefSrc)) fs.copyFileSync(briefSrc, briefDst);
  else if (!fs.existsSync(briefDst)) fs.writeFileSync(briefDst, "");

  const briefDir = path.join(OUT, "briefs");
  fs.mkdirSync(briefDir, { recursive: true });
  const lapJson = path.join(TEAM_RECS, "pilot_brief_lapland.json");
  if (fs.existsSync(lapJson)) fs.copyFileSync(lapJson, path.join(briefDir, "pilot_brief_lapland.json"));
  const lapMd = path.join(TEAM_RECS, "pilot_brief_lapland.md");
  if (fs.existsSync(lapMd)) fs.copyFileSync(lapMd, path.join(OUT, "pilot_brief_lapland.md"));

  const pubBriefs = path.join(APP, "public", "briefs");
  fs.mkdirSync(pubBriefs, { recursive: true });
  const lapPdf = path.join(TEAM_RECS, "pilot_brief_lapland.pdf");
  const pubPdf = path.join(pubBriefs, "pilot_brief_lapland.pdf");
  if (fs.existsSync(lapPdf)) fs.copyFileSync(lapPdf, pubPdf);

  const chartFiles = syncChartData();

  const reportPath = path.join(OUT, "_load_report.json");
  fs.writeFileSync(reportPath, JSON.stringify(report, null, 2) + "\n");

  const violations = [];
  const scanNames = ["regions.json","sources.json","key_message.json","recommendations.json","hero.json","facts.json","_load_report.json", ...chartFiles.map((n) => path.join("charts", n))];
  for (const name of scanNames) {
    const fp = path.join(OUT, name);
    if (!fs.existsSync(fp)) continue;
    collectExampleViolations(JSON.parse(fs.readFileSync(fp, "utf8")), name, violations);
  }
  const bannedIds = ["src-sotkanet-6411", "src-sotkanet-2676", "src-sotkanet-6410"];
  for (const name of scanNames) {
    const fp = path.join(OUT, name);
    if (!fs.existsSync(fp)) continue;
    const raw = fs.readFileSync(fp, "utf8");
    for (const id of bannedIds) {
      if (raw.includes(id)) violations.push(`${name}: banned source ${id} (all-cause PHC waits, not cancer; excluded)`);
    }
  }
  if (violations.length) {
    console.error("FATAL: example, synthetic, or banned Sotkanet figures reached the app bundle:\n  - " + violations.join("\n  - "));
    process.exit(1);
  }
  if (report.is_example || report.used_example) {
    console.error("FATAL: refusing to bundle example/placeholder indicator data for the live demo.");
    process.exit(1);
  }

  const nameRoots = [OUT, path.join(APP, "public", "briefs")];
  let stripped = 0;
  for (const root of nameRoots) stripped += sanitizeTree(root);
  if (stripped) console.log(`sync-data: stripped personal names from ${stripped} bundled file(s)`);
  for (const root of nameRoots) assertNoPersonalNames(root, path.relative(APP, root) || root);

  const serverFactsSrc = path.join(OUT, "facts.json");
  const serverFactsDst = path.join(APP, "server", "facts.json");
  if (fs.existsSync(serverFactsSrc)) {
    fs.mkdirSync(path.dirname(serverFactsDst), { recursive: true });
    fs.copyFileSync(serverFactsSrc, serverFactsDst);
    console.log("sync-data: copied facts.json to server/ for the Ask proxy");
  }

  const banner = report.is_example
    ? "EXAMPLE DATA will be shown in the UI."
    : (report.recs_are_example
        ? "Team indicator data loaded; recommendations are still the example set."
        : "Team dataset loaded (real indicator values; recs included).");
  const extractSrc = path.join(APP, "..", "verda", "extract");
  const extractDst = path.join(APP, "src", "content", "extract");
  fs.mkdirSync(extractDst, { recursive: true });
  for (const name of ["samples.json", "app_export.json"]) {
    const src = path.join(extractSrc, name);
    if (fs.existsSync(src)) {
      fs.copyFileSync(src, path.join(extractDst, name));
    }
  }
  const numbersSrc = path.join(APP, "..", "verda", "HOW_WE_BUILT_NUMBERS.json");
  if (fs.existsSync(numbersSrc)) {
    fs.copyFileSync(numbersSrc, path.join(extractDst, "HOW_WE_BUILT_NUMBERS.json"));
  }

  console.log(`sync-data: ${banner}`);
  console.log(`  regions:           ${report.loaded_from.regions}`);
  console.log(`  sources:           ${report.loaded_from.sources}`);
  console.log(`  key_message:       ${report.loaded_from.key_message}`);
  console.log(`  recommendations:   ${report.loaded_from.recommendations}`);
  console.log(`  counties:          ${report.loaded_from.counties}`);
  if (report.warnings.length) {
    console.log("  warnings:");
    for (const w of report.warnings) console.log("   - " + w);
  }
  console.log(`  report: ${reportPath}`);
}

main();
