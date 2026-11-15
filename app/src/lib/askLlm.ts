import { allFacts, factById, usageRules, validateAnswerNumbers } from "./facts";
import { BANNED, extractJsonObject, type PilotBriefDraft, validateBriefDraft } from "./briefDraft";

export const VERDA_TAG = "EU-hosted inference · Verda";
export const FIRST_TOKEN_MS = 6000;
export const COMPLETE_MS = 45000;

const KNOWN_IDS = new Set(allFacts.map((f) => f.id));

export function proxyBaseUrl(): string | null {
  const env = (import.meta as { env?: { VITE_TASAN_PROXY_URL?: string } }).env;
  const raw = env?.VITE_TASAN_PROXY_URL?.trim();
  if (!raw) return null;
  return raw.replace(/\/$/, "");
}

export function isForcedOffline(): boolean {
  if (typeof window === "undefined") return false;
  const q = new URLSearchParams(window.location.search);
  return q.get("ask") === "offline" || q.get("llm") === "0";
}

export function extractCitedIds(text: string): string[] {
  const found = new Set<string>();
  const re = /\[([a-z][a-z0-9_]{3,})\]|\(([a-z][a-z0-9_]{3,})\)/g;
  let m: RegExpExecArray | null;
  while ((m = re.exec(text))) {
    const id = m[1] || m[2];
    if (id && KNOWN_IDS.has(id)) found.add(id);
  }
  // bare ids as a last resort
  for (const id of KNOWN_IDS) {
    const bare = new RegExp(`(^|[^a-z0-9_])${id}([^a-z0-9_]|$)`);
    if (bare.test(text)) found.add(id);
  }
  return [...found];
}

function splitSentences(text: string): string[] {
  return text
    .replace(/\s+/g, " ")
    .split(/(?<=[.!?…])\s+/)
    .map((s) => s.trim())
    .filter((s) => s.length > 0 && !/^```/.test(s));
}

export function validateLlmAnswer(text: string): { ok: boolean; reason?: string; cites: string[]; kind: "ai" | "refuse" } {
  const cites = extractCitedIds(text);
  if (BANNED.test(text)) return { ok: false, reason: "personal name", cites, kind: "ai" };
  const sentences = splitSentences(text).filter((s) => !/^REFUSE\b/i.test(s) && s !== "{" && !s.startsWith("{"));
  if (!sentences.length && !/^REFUSE/i.test(text.trim())) return { ok: false, reason: "empty", cites, kind: "ai" };
  for (const s of sentences) {
    if (extractCitedIds(s).length === 0 && /[A-Za-zÅÄÖåäö]/.test(s) && s.length > 20) {
      return { ok: false, reason: `sentence without fact id: ${s.slice(0, 80)}`, cites, kind: "ai" };
    }
  }
  if (!cites.length && !/^REFUSE/i.test(text.trim())) return { ok: false, reason: "no fact ids", cites, kind: "ai" };
  const nums = validateAnswerNumbers(text, cites);
  if (!nums.ok) return { ok: false, reason: `unverified numbers ${nums.extras.join(", ")}`, cites, kind: "ai" };
  // cited ids must exist (extract already filters)
  const kind: "ai" | "refuse" = /^REFUSE\b/i.test(text.trim()) || /no_public_data|Ei julkista|Ingen offentlig|outside the sourced/i.test(text)
    ? "refuse"
    : "ai";
  // if a cite is unknown — already filtered
  for (const id of cites) {
    if (!factById(id)) return { ok: false, reason: `unknown fact ${id}`, cites, kind };
  }
  return { ok: true, cites, kind };
}

export type LlmResult =
  | { ok: true; kind: "ai" | "refuse"; text: string; cites: string[]; brief?: PilotBriefDraft }
  | { ok: false; reason: string };

export type StreamHandlers = {
  onDelta?: (text: string) => void;
  signal?: AbortSignal;
};

function firstTokenController(parent?: AbortSignal): { signal: AbortSignal; sawByte: () => void; close: () => void } {
  const ac = new AbortController();
  const onParent = () => ac.abort();
  parent?.addEventListener("abort", onParent);
  let got = false;
  const t6 = setTimeout(() => {
    if (!got) ac.abort();
  }, FIRST_TOKEN_MS);
  const t45 = setTimeout(() => ac.abort(), COMPLETE_MS);
  return {
    signal: ac.signal,
    sawByte() {
      got = true;
      clearTimeout(t6);
    },
    close() {
      clearTimeout(t6);
      clearTimeout(t45);
      parent?.removeEventListener("abort", onParent);
    },
  };
}

async function readSse(res: Response, onDelta: (chunk: string) => void, ctl: { sawByte: () => void; signal: AbortSignal }): Promise<string> {
  if (!res.body) {
    const j = await res.json().catch(() => ({}));
    const text = typeof j.text === "string" ? j.text : typeof j.content === "string" ? j.content : "";
    if (text) {
      ctl.sawByte();
      onDelta(text);
    }
    return text;
  }
  const reader = res.body.getReader();
  const dec = new TextDecoder();
  let buf = "";
  let out = "";
  while (true) {
    if (ctl.signal.aborted) throw new DOMException("Aborted", "AbortError");
    const { done, value } = await reader.read();
    if (done) break;
    ctl.sawByte();
    buf += dec.decode(value, { stream: true });
    const parts = buf.split("\n");
    buf = parts.pop() ?? "";
    for (const line of parts) {
      const trimmed = line.trim();
      if (!trimmed || trimmed.startsWith(":")) continue;
      if (trimmed === "data: [DONE]") continue;
      if (trimmed.startsWith("data:")) {
        const payload = trimmed.slice(5).trim();
        if (!payload || payload === "[DONE]") continue;
        try {
          const json = JSON.parse(payload);
          const delta =
            json.choices?.[0]?.delta?.content ??
            json.choices?.[0]?.message?.content ??
            json.text ??
            "";
          if (typeof delta === "string" && delta) {
            out += delta;
            onDelta(out);
          }
        } catch {
          out += payload;
          onDelta(out);
        }
      } else if (!trimmed.startsWith("event:")) {
        // raw chunked text
        out += line;
        onDelta(out);
      }
    }
  }
  return out;
}

export async function streamAsk(
  question: string,
  opts: { county?: string | null; countyLabel?: string; mode?: "answer" | "brief"; lang?: "fi" | "sv" | "en" } & StreamHandlers,
): Promise<LlmResult> {
  const base = proxyBaseUrl();
  if (!base) return { ok: false, reason: "no proxy url" };
  const ctl = firstTokenController(opts.signal);
  try {
    const res = await fetch(`${base}/ask`, {
      method: "POST",
      headers: { "Content-Type": "application/json", Accept: "text/event-stream" },
      body: JSON.stringify({
        question,
        county: opts.county ?? undefined,
        county_label: opts.countyLabel ?? undefined,
        lang: opts.lang ?? undefined,
        mode: opts.mode ?? "answer",
        stream: true,
      }),
      signal: ctl.signal,
    });
    if (!res.ok) {
      ctl.sawByte();
      return { ok: false, reason: `http ${res.status}` };
    }
    const text = (await readSse(res, (t) => opts.onDelta?.(t), ctl)).trim();
    if (!text) return { ok: false, reason: "empty response" };
    if ((opts.mode ?? "answer") === "brief") {
      const parsed = extractJsonObject(text);
      const v = validateBriefDraft(parsed);
      if (!v.ok) return { ok: false, reason: v.reason };
      return { ok: true, kind: "ai", text, cites: extractCitedIds(text), brief: v.draft };
    }
    const v = validateLlmAnswer(text);
    if (!v.ok) return { ok: false, reason: v.reason ?? "invalid" };
    return { ok: true, kind: v.kind, text, cites: v.cites };
  } catch (e) {
    const name = e instanceof Error ? e.name : "";
    const msg = e instanceof Error ? e.message : String(e);
    return { ok: false, reason: name === "AbortError" ? "timeout" : msg };
  } finally {
    ctl.close();
  }
}

export { usageRules };
