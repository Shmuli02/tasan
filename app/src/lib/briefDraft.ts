import type { Fact } from "../types";
import { allFacts, numbersInText, validateAnswerNumbers } from "./facts";

// Packed so the public bundle does not contain role-holder surnames in plaintext.
const BANNED = new RegExp("\\b(" + atob("VGFza2lsYXxLYXVyYW5lbnxSYWphbmllbWl8S3V1c2lzdG98Um9ua2FpbmVufE1ha3NpbW93") + ")\\b", "i");

export type BriefOwner = { role?: string; name?: string; source?: string | null; verified?: string };
export type BriefSigner = { role?: string; name?: string; source?: string; verified?: string };

export type PilotBriefDraft = {
  template_version?: string;
  status: string;
  status_label?: string;
  project?: string;
  title: string;
  date_prepared?: string;
  county: string;
  signer?: BriefSigner;
  problem: { line: string; metric?: string; source?: string; caveat?: string; people_estimate?: string };
  action: { summary: string; components: string[] };
  owners: BriefOwner[];
  cost_range?: { low_eur?: number; high_eur?: number; period?: string; basis?: string; excludes?: string };
  kpis?: { name: string; target: string }[];
  kpi_caveat?: string;
  timeline?: unknown;
  stop_go?: { go?: string; stop?: string; decider?: string };
  az_role?: unknown;
  precedents?: unknown;
  caveats?: unknown;
  appendix?: unknown;
  rules?: unknown;
};

export function extractJsonObject(text: string): unknown | null {
  const trimmed = text.trim();
  const fence = trimmed.match(/```(?:json)?\s*([\s\S]*?)```/i);
  const raw = fence ? fence[1].trim() : trimmed;
  const start = raw.indexOf("{");
  const end = raw.lastIndexOf("}");
  if (start < 0 || end <= start) return null;
  try {
    return JSON.parse(raw.slice(start, end + 1));
  } catch {
    return null;
  }
}

export function validateBriefDraft(
  value: unknown,
  pack: Fact[] = allFacts,
): { ok: true; draft: PilotBriefDraft } | { ok: false; reason: string } {
  if (!value || typeof value !== "object") return { ok: false, reason: "not an object" };
  const d = value as Record<string, unknown>;
  const status = String(d.status ?? "");
  if (!/^draft$/i.test(status)) return { ok: false, reason: "status must be DRAFT" };
  if (typeof d.title !== "string" || !d.title.trim()) return { ok: false, reason: "missing title" };
  if (typeof d.county !== "string" || !d.county.trim()) return { ok: false, reason: "missing county" };
  const problem = d.problem as Record<string, unknown> | undefined;
  const action = d.action as Record<string, unknown> | undefined;
  if (!problem || typeof problem.line !== "string") return { ok: false, reason: "missing problem.line" };
  if (!action || typeof action.summary !== "string") return { ok: false, reason: "missing action.summary" };
  const components = action.components;
  if (!Array.isArray(components) || !components.every((c) => typeof c === "string")) {
    return { ok: false, reason: "action.components must be strings" };
  }
  const owners = d.owners;
  if (!Array.isArray(owners) || owners.length < 1) return { ok: false, reason: "owners required" };
  for (const o of owners) {
    if (!o || typeof o !== "object" || typeof (o as BriefOwner).role !== "string") {
      return { ok: false, reason: "each owner needs a role" };
    }
    const name = (o as BriefOwner).name;
    if (name && String(name).trim()) return { ok: false, reason: "owners must be roles only" };
  }
  const signer = d.signer as BriefSigner | undefined;
  if (signer?.name && String(signer.name).trim()) return { ok: false, reason: "signer must be a role only" };
  const blob = JSON.stringify(value);
  if (BANNED.test(blob)) return { ok: false, reason: "personal name in brief" };
  const cited = Array.from(blob.matchAll(/\[([a-z][a-z0-9_]{3,})\]/g)).map((m) => m[1]);
  const nums = validateAnswerNumbers(blob, cited.length ? cited : pack.map((f) => f.id), pack);
  // For briefs, allow cost-range numbers that already appear in the pre-generated shape only if cited or typical role text has no wild extras.
  // Reject only clearly invented numbers that are not in any fact and not in a small allowlist of template constants.
  const allowExtra = new Set([90, 60, 30, 14, 28, 42, 6, 3, 22, 100]); // days / counts used in the pilot frame
  const leftover = nums.extras.filter((n) => !allowExtra.has(n) && !allowExtra.has(Math.round(n)));
  // cost range may use euro amounts not in facts — allow if in cost_range only and >= 1000
  const cost = d.cost_range as { low_eur?: number; high_eur?: number } | undefined;
  const costNums = [cost?.low_eur, cost?.high_eur].filter((n): n is number => typeof n === "number");
  const leftover2 = leftover.filter((n) => !costNums.some((c) => Math.abs(c - n) < 0.01) || n < 1000);
  if (leftover2.length) return { ok: false, reason: `unverified numbers ${leftover2.join(", ")}` };
  const draft: PilotBriefDraft = {
    template_version: typeof d.template_version === "string" ? d.template_version : "tasan-pilot-brief-v1",
    status: "DRAFT",
    status_label: typeof d.status_label === "string" ? d.status_label : "DRAFT — not signed",
    project: typeof d.project === "string" ? d.project : "Tasan",
    title: d.title as string,
    date_prepared: typeof d.date_prepared === "string" ? d.date_prepared : undefined,
    county: d.county as string,
    signer: signer ?? { role: "Johtajaylilääkäri / Chief Medical Officer" },
    problem: {
      line: String(problem.line),
      metric: problem.metric != null ? String(problem.metric) : undefined,
      source: problem.source != null ? String(problem.source) : undefined,
      caveat: problem.caveat != null ? String(problem.caveat) : undefined,
      people_estimate: problem.people_estimate != null ? String(problem.people_estimate) : undefined,
    },
    action: { summary: String(action.summary), components: components as string[] },
    owners: owners as BriefOwner[],
    cost_range: (d.cost_range as PilotBriefDraft["cost_range"]) ?? undefined,
    kpis: Array.isArray(d.kpis) ? (d.kpis as PilotBriefDraft["kpis"]) : undefined,
    kpi_caveat: typeof d.kpi_caveat === "string" ? d.kpi_caveat : undefined,
    stop_go: (d.stop_go as PilotBriefDraft["stop_go"]) ?? undefined,
  };
  return { ok: true, draft };
}

export { numbersInText, BANNED };
