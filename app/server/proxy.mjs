/**
 * Portable analyst proxy: same file runs as a Beacon Worker (default export)
 * or as a Node HTTP server on a Verda CPU instance (`node proxy.mjs`).
 * Default model: kimi-k3-1-pro (EU-hosted inference). Key stays in env only.
 * Never print, log or commit the key.
 */
import { factsPack as bundledFacts } from "./facts-data.mjs";

const DEFAULT_MODEL = "kimi-k3-1-pro";
const DEFAULT_BASE = "https://inference.verda.com/v1";
const ALLOW_ORIGIN = "https://petaled-trowel-90.beacon.host";
const MAX_BODY = 16 * 1024;
const WINDOW_MS = 60_000;
const MAX_REQ = 30;
const UPSTREAM_MS = 45_000;
const hits = new Map();
let factsCache = null;

function envGet(env, key, fallback = "") {
  if (env && env[key] != null) return String(env[key]);
  if (typeof process !== "undefined" && process.env && process.env[key] != null) return process.env[key];
  return fallback;
}

function originAllowed(origin) {
  return origin === ALLOW_ORIGIN || (origin && /^http:\/\/(localhost|127\.0\.0\.1)(:\d+)?$/.test(origin));
}

function corsHeaders(origin, extra = {}) {
  const allow = originAllowed(origin) ? origin : ALLOW_ORIGIN;
  return {
    "Access-Control-Allow-Origin": allow,
    "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
    "Access-Control-Allow-Headers": "Content-Type, Accept",
    "Access-Control-Max-Age": "86400",
    Vary: "Origin",
    ...extra,
  };
}

function json(body, status, origin) {
  return new Response(JSON.stringify(body), {
    status,
    headers: { "Content-Type": "application/json; charset=utf-8", ...corsHeaders(origin) },
  });
}

function rateLimited(ip) {
  const now = Date.now();
  const rec = hits.get(ip) || { n: 0, t: now };
  if (now - rec.t > WINDOW_MS) {
    rec.n = 0;
    rec.t = now;
  }
  rec.n += 1;
  hits.set(ip, rec);
  return rec.n > MAX_REQ;
}

async function loadFacts(env) {
  if (factsCache) return factsCache;
  if (bundledFacts && (bundledFacts.facts || bundledFacts.usage_rules)) {
    factsCache = bundledFacts;
    return factsCache;
  }
  if (env && env.FACTS_JSON) {
    try { factsCache = JSON.parse(String(env.FACTS_JSON)); return factsCache; } catch { /* fall through */ }
  }
  factsCache = { usage_rules: [], facts: [] };
  return factsCache;
}

function compactFacts(pack) {
  const facts = pack.facts || [];
  return facts
    .map((f) => {
      const region = f.region && typeof f.region === "object" ? f.region.name || f.region.code || "" : f.region || "";
      const val = f.value == null ? "" : ` value=${f.value}${f.unit ? " " + f.unit : ""}`;
      const cav = f.caveat ? ` caveat=${String(f.caveat).replace(/\s+/g, " ").slice(0, 220)}` : "";
      return `${f.id} [${f.measure_type}] ${region} ${f.years || ""}${val}\n  EN: ${f.statement_en}\n  FI: ${f.statement_fi}\n  source_table: ${f.source_table} source_url: ${f.source_url}${cav}`;
    })
    .join("\n");
}

function systemPrompt(pack, mode, lang, countyLabel) {
  const rules = pack.usage_rules || [];
  const numbered = rules.map((r, i) => `${i + 1}. ${r}`).join("\n");
  const county = countyLabel ? `The dashboard county context is: ${countyLabel}.` : "";
  const langLine =
    lang === "sv"
      ? "The user is writing in Swedish. Answer in Swedish, copying numbers exactly from the facts (facts are in Finnish and English only)."
      : lang === "fi"
        ? "The user is writing in Finnish. Answer in Finnish using statement_fi wording where you cite a fact."
        : "The user is writing in English. Answer in English using statement_en wording where you cite a fact.";
  const modeBlock =
    mode === "brief"
      ? `MODE: draft a pilot brief. Return ONLY a JSON object, no markdown, no prose. The JSON must be schema-valid with keys:
status (must be "DRAFT"), status_label, title, date_prepared, county, signer (object with role only, no name),
problem {line, metric, source, caveat, people_estimate?}, action {summary, components: string[]},
owners: array of {role, source, verified} with role only (never personal names),
cost_range {low_eur, high_eur, period, basis, excludes}, kpis: [{name, target}], kpi_caveat,
stop_go {go, stop, decider}.
Cite fact ids in square brackets inside problem.metric / problem.source / people_estimate when you use a number.
Use roles such as "Johtajaylilääkäri / Chief Medical Officer, Lapland wellbeing services county". Never invent personal names.
If the county has no sourced facts that support a brief, return JSON {"status":"REFUSE","reason":"..." } instead.`
      : `MODE: answer the question.
Write short sourced prose. Every sentence must end with at least one fact id in square brackets, e.g. [lung_curative_lapland], and mention the fact's source_table in words.
If you must refuse, start the reply with the exact token REFUSE, then one polite sentence, and cite the matching no_public_data fact.
Never claim lives saved, survival benefit, drug or treatment choice, or 6-week compliance rates. Never invent numbers.`;
  return `You are Ask Tasan, a grounded analyst for the Junction 2026 "Equal Care Across Finland" demo.
You must follow these usage_rules verbatim:

${numbered}

${langLine}
${county}
${modeBlock}

Use ONLY the facts below. Do not use other knowledge. Do not say where the model is hosted.

FACTS:
${compactFacts(pack)}`;
}

function isMock(env) {
  const key = envGet(env, "VERDA_API_KEY");
  return !key || key === "mock" || envGet(env, "VERDA_MOCK") === "1";
}

function requestOrigin(req) {
  const origin = req.headers.get("Origin") || "";
  if (origin) return origin;
  const ref = req.headers.get("Referer") || "";
  try {
    if (ref) return new URL(ref).origin;
  } catch {
    /* ignore */
  }
  return "";
}

async function handle(req, env) {
  const url = new URL(req.url);
  const origin = requestOrigin(req);
  const path = url.pathname.replace(/\/$/, "") || "/";

  if (req.method === "OPTIONS") return new Response(null, { status: 204, headers: corsHeaders(origin) });

  if (req.method === "GET" && (path === "/health" || path === "/")) {
    const pack = await loadFacts(env);
    return json(
      {
        ok: true,
        model: envGet(env, "VERDA_MODEL", DEFAULT_MODEL),
        mock: isMock(env),
        facts: (pack.facts || []).length,
        rules: (pack.usage_rules || []).length,
        service: "tasan-ask",
      },
      200,
      origin,
    );
  }

  if (req.method !== "POST") return json({ error: "method_not_allowed" }, 405, origin);
  if (path !== "/" && path !== "/ask") return json({ error: "not_found" }, 404, origin);
  if (!originAllowed(origin)) return json({ error: "origin_not_allowed" }, 403, origin);

  const ip = req.headers.get("CF-Connecting-IP") || req.headers.get("x-forwarded-for") || "local";
  if (rateLimited(ip)) return json({ error: "rate_limited" }, 429, origin);

  const raw = await req.text();
  if (raw.length > MAX_BODY) return json({ error: "payload_too_large" }, 413, origin);
  let payload;
  try {
    payload = raw ? JSON.parse(raw) : {};
  } catch {
    return json({ error: "invalid_json" }, 400, origin);
  }

  const pack = await loadFacts(env);
  const question = typeof payload.question === "string" ? payload.question.trim() : "";
  const mode = payload.mode === "brief" ? "brief" : "answer";
  const lang = payload.lang === "fi" || payload.lang === "sv" ? payload.lang : "en";
  const countyLabel = typeof payload.county_label === "string" ? payload.county_label : "";
  const stream = payload.stream !== false;
  const model = envGet(env, "VERDA_MODEL", DEFAULT_MODEL);
  const maxTokens = Math.min(Number(payload.max_tokens) || (mode === "brief" ? 1400 : 700), mode === "brief" ? 1800 : 900);

  const messages = question
    ? [
        { role: "system", content: systemPrompt(pack, mode, lang, countyLabel) },
        { role: "user", content: question },
      ]
    : payload.messages;

  if (!messages || !Array.isArray(messages)) return json({ error: "missing_question" }, 400, origin);

  if (isMock(env)) {
    const content =
      mode === "brief"
        ? JSON.stringify({
            status: "DRAFT",
            status_label: "DRAFT — not signed",
            title: "Mock brief",
            county: countyLabel || "Lapland",
            signer: { role: "Johtajaylilääkäri / Chief Medical Officer" },
            problem: { line: "Mock problem", metric: "18.5% [lung_curative_lapland]" },
            action: { summary: "Mock action", components: ["Navigator"] },
            owners: [{ role: "Hoitotyön johtaja / Chief Nursing Officer", source: "mock", verified: "role only" }],
          })
        : "Mock proxy reply. [lung_curative_lapland]";
    if (stream) return sseFromText(content, origin);
    return json({ mock: true, model, text: content, choices: [{ message: { role: "assistant", content } }] }, 200, origin);
  }

  const key = envGet(env, "VERDA_API_KEY");
  const base = envGet(env, "VERDA_BASE_URL", DEFAULT_BASE).replace(/\/$/, "");
  const ac = new AbortController();
  const timer = setTimeout(() => ac.abort(), UPSTREAM_MS);
  let upstream;
  try {
    upstream = await fetch(`${base}/chat/completions`, {
      method: "POST",
      headers: { Authorization: `Bearer ${key}`, "Content-Type": "application/json" },
      body: JSON.stringify({
        model,
        messages,
        max_tokens: maxTokens,
        temperature: 0,
        stream,
        thinking: { type: "disabled" },
      }),
      signal: ac.signal,
    });
  } catch {
    clearTimeout(timer);
    return json({ error: "upstream_unreachable" }, 502, origin);
  }
  clearTimeout(timer);

  if (!upstream.ok) {
    // Do not forward upstream body (may contain request echoes). Status only.
    return json({ error: "upstream_error", status: upstream.status }, 502, origin);
  }

  if (stream && upstream.body) {
    return new Response(upstream.body, {
      status: 200,
      headers: corsHeaders(origin, {
        "Content-Type": "text/event-stream; charset=utf-8",
        "Cache-Control": "no-cache, no-transform",
        Connection: "keep-alive",
        "X-Accel-Buffering": "no",
      }),
    });
  }

  const data = await upstream.json();
  const text = data?.choices?.[0]?.message?.content ?? "";
  return json({ model, text, choices: data.choices }, 200, origin);
}

function sseFromText(text, origin) {
  const payload = `data: ${JSON.stringify({ choices: [{ delta: { content: text } }] })}\n\ndata: [DONE]\n\n`;
  return new Response(payload, {
    status: 200,
    headers: corsHeaders(origin, {
      "Content-Type": "text/event-stream; charset=utf-8",
      "Cache-Control": "no-cache, no-transform",
    }),
  });
}

export default {
  async fetch(req, env) {
    return handle(req, env);
  },
};

const isNode = typeof process !== "undefined" && !!process.versions?.node && process.argv[1] && String(process.argv[1]).includes("proxy.mjs");
if (isNode) {
  const { createServer } = await import("node:http");
  const host = process.env.TASAN_BIND || "127.0.0.1";
  const port = Number(process.env.PORT || 8787);
  const server = createServer(async (req, res) => {
    const chunks = [];
    for await (const c of req) chunks.push(c);
    const body = Buffer.concat(chunks);
    const headers = new Headers();
    for (const [k, v] of Object.entries(req.headers)) if (v) headers.set(k, Array.isArray(v) ? v.join(",") : v);
    const url = `http://${req.headers.host || "localhost"}${req.url}`;
    const request = new Request(url, { method: req.method, headers, body: req.method === "GET" || req.method === "HEAD" ? undefined : body });
    const response = await handle(request, process.env);
    res.statusCode = response.status;
    response.headers.forEach((v, k) => res.setHeader(k, v));
    const buf = Buffer.from(await response.arrayBuffer());
    res.end(buf);
  });
  server.listen(port, host, () => {
    console.log(`tasan-ask proxy listening on ${host}:${port} model=${DEFAULT_MODEL}`);
  });
}
