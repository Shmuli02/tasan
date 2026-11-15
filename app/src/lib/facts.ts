import type { Fact, FactsFile } from "../types";
import { dataset } from "./data";

export const factsPack: FactsFile = dataset.facts;
export const allFacts: Fact[] = dataset.facts.facts ?? [];
export const usageRules: string[] = dataset.facts.usage_rules ?? [];

export function factById(id: string): Fact | undefined {
  return allFacts.find((f) => f.id === id);
}

export function statement(fact: Fact, lang: "fi" | "sv" | "en"): string {
  if (lang === "fi") return fact.statement_fi;
  return fact.statement_en;
}

export function shouldSayAbout(fact: Fact): boolean {
  return fact.measure_type === "computed_by_tasan" || fact.measure_type === "chart_estimate";
}

export function factCite(fact: Fact): string {
  return `${fact.id}: ${fact.source_table}${fact.source_url ? ` (${fact.source_url})` : ""}`;
}

export function factParagraph(fact: Fact, lang: "fi" | "sv" | "en"): string {
  const body = statement(fact, lang);
  const about =
    shouldSayAbout(fact) && lang === "fi"
      ? "Luku on Tasanin laskelma tai kaavioarvio, ei julkaistu luku; käytä muotoa «noin»."
      : shouldSayAbout(fact)
        ? "This is a Tasan computed or chart-estimate figure (say “about”), not a published number."
        : "";
  const caveat = fact.caveat ? (lang === "fi" ? `Huomio: ${fact.caveat}` : `Caveat: ${fact.caveat}`) : "";
  return [body, about, caveat, `Source: ${factCite(fact)}`].filter(Boolean).join(" ");
}

/** Numbers (integers and decimals) in a text, ignoring years 19xx/20xx. */
export function numbersInText(text: string): number[] {
  const cleaned = text
    .replace(/https?:\/\/\S+/gi, " ")
    .replace(/\[[a-z][a-z0-9_]+\]/gi, " ")
    .replace(/\b(?:taulukko|table|tab\.?|työpaperi|tyopaperi|kuvio|figure|fig\.?|liite|appendix|luku)\s*\d+(?:\s*\/\s*\d{4})?/gi, " ")
    .replace(/\b\d+[ -]?year\b/gi, " ")
    .replace(/\b(19|20)\d{2}\s*[–-]\s*(19|20)\d{2}\b/g, " ");
  const out: number[] = [];
  const re = /(?<![A-Za-z])-?\d+(?:[.,]\d+)?/g;
  let m: RegExpExecArray | null;
  while ((m = re.exec(cleaned))) {
    const raw = m[0].replace(",", ".");
    const n = Number(raw);
    if (!Number.isFinite(n)) continue;
    // skip 4-digit years
    if (/^(19|20)\d{2}$/.test(raw.replace("-", ""))) continue;
    out.push(n);
  }
  return out;
}

function factNumberBag(fact: Fact): number[] {
  const bag = numbersInText(`${fact.statement_en} ${fact.statement_fi} ${fact.caveat ?? ""} ${fact.unit ?? ""}`);
  if (typeof fact.value === "number") bag.push(fact.value);
  return bag;
}

function closeTo(n: number, allowed: number[]): boolean {
  return allowed.some((a) => Math.abs(a - n) < 1e-6 || (Math.abs(a) >= 1 && Math.abs(a - n) / Math.abs(a) < 0.0001));
}

/** Every number in the answer must appear in a cited fact's value or statements. */
export function validateAnswerNumbers(
  text: string,
  citedIds: string[],
  pack: Fact[] = allFacts,
): { ok: boolean; extras: number[] } {
  const cited = citedIds.map((id) => pack.find((f) => f.id === id)).filter((f): f is Fact => Boolean(f));
  const allowed: number[] = [];
  for (const f of cited) allowed.push(...factNumberBag(f));
  const extras = numbersInText(text).filter((n) => !closeTo(n, allowed));
  return { ok: extras.length === 0, extras };
}

const REFUSAL_PATTERNS: { id: string; re: RegExp }[] = [
  { id: "nodata_lives_saved", re: /\b(lives saved|save lives|deaths prevented|pelastaa henki|hur många liv|liv .{0,40}rädd|räddar liv|kuolema.*ehkäis|how many lives|kuinka monta henke)\b/i },
  { id: "nodata_regional_target_compliance", re: /\b(6[ -]?week|six week|kuuden viikon|kuusi viikkoa|42[ -]?day|target-?time compliance|on-time rate|hoitoonpääsy.*tavoite)\b/i },
  { id: "nodata_referral_to_diagnosis", re: /\b(referral\s*(to|→|->|–|-)\s*diagnos|lähetteestä diagnoos|remiss.*diagnos)\b/i },
  { id: "nodata_dx_to_treatment_by_county", re: /\b(diagnosis.to.treatment.*county|hyvinvointialue.*hoitoon.*aika|dx to treatment by county)\b/i },
  { id: "nodata_pancreas_liver_pathway", re: /\b(pancrea|liver cancer|haimasyöp|maksasyöp|bukspotts|levercancer)\b/i },
  { id: "nodata_lung_after_2023", re: /\b(2024|2025|2026).{0,40}(lung|keuhko)|diagnos(ed|ed after) 202[4-9]/i },
];

export function matchingRefusalFact(q: string): Fact | undefined {
  for (const { id, re } of REFUSAL_PATTERNS) {
    if (re.test(q)) return factById(id);
  }
  return undefined;
}

export function isTreatmentChoiceQuestion(q: string): boolean {
  return /\b(which (drug|medicine|chemo|immunotherap|tyrosine)|what (drug|treatment|regimen) should|lääke(valinta|hoito)|hoitovalinta|tuleeko leikata|should (we|i) (operate|prescribe|give)|vilket läkemedel|vilken behandling ska|immunos?terapi(a|e)? vs|prescribe (osimertinib|pembrolizumab))\b/i.test(
    q,
  );
}

export function countyCode(fact: Fact): string | null {
  const r = fact.region;
  if (r && typeof r === "object" && !Array.isArray(r) && typeof (r as { code?: unknown }).code === "string") {
    return (r as { code: string }).code;
  }
  return null;
}

export function countyFactSummary(id: string): {
  agestdMen?: number;
  crude?: number;
  perYear?: number;
  noPublicAgestd: boolean;
} {
  const forCounty = allFacts.filter((f) => countyCode(f) === id);
  const agestdMen = forCounty.find((f) => f.id.includes("agestd") && f.id.includes("men") && f.id.includes("curative") && typeof f.value === "number");
  const crude = forCounty.find((f) => f.measure_type === "published" && f.id.startsWith("lung_curative_") && !f.id.includes("agestd") && !f.id.includes("yta") && typeof f.value === "number");
  const perYear = forCounty.find((f) => f.id.startsWith("people_number_") && typeof f.value === "number");
  return {
    agestdMen: agestdMen && typeof agestdMen.value === "number" ? agestdMen.value : undefined,
    crude: crude && typeof crude.value === "number" ? crude.value : undefined,
    perYear: perYear && typeof perYear.value === "number" ? perYear.value : undefined,
    noPublicAgestd: id === "20" || id === "91",
  };
}

export function hoverLabel(id: string, name: string, lang: "fi" | "en"): string {
  const s = countyFactSummary(id);
  if (s.noPublicAgestd) return `${name}: ${lang === "fi" ? "Ei julkista tietoa" : "No public data"}`;
  const nums: string[] = [];
  if (s.agestdMen != null) nums.push(`${s.agestdMen}%`);
  if (s.perYear != null) nums.push(lang === "fi" ? `noin ${s.perYear}/v` : `~${s.perYear}/yr`);
  return nums.length ? `${name}: ${nums.join(" · ")}` : name;
}

export const sourcedFactCount: number = factsPack.n_facts ?? allFacts.length;

/** Short human source chip, never the snake_case fact id. */
export function sourceLabel(fact: Fact, lang: "en" | "fi"): string {
  const fi = lang === "fi";
  if (fact.measure_type === "computed_by_tasan") return fi ? "Tasanin laskelma" : "Tasan calc";
  if (fact.measure_type === "no_public_data") return fi ? "Ei julkista tietoa" : "No public data";
  const table = fact.source_table ?? "";
  const sot = table.match(/Sotkanet\s+(\d+)/i);
  if (sot) return `Sotkanet ${sot[1]}`;
  const stat = table.match(/StatFin\s+(\w+)/i);
  if (stat) return fi ? `Tilastokeskus · ${stat[1]}` : `Statistics Finland · ${stat[1]}`;
  if (/THL Ohjaus/i.test(table)) return "THL Ohjaus 21/2016";
  const paper = table.match(/Työpaperi\s+([\d/]+)/i);
  if (paper) return `THL Työpaperi ${paper[1]}`;
  if (/^Roadmap/i.test(table)) {
    const pg = table.match(/p\.?\s*(\d+)/i);
    return pg ? (fi ? `Tiekartta · s.${pg[1]}` : `Roadmap · p.${pg[1]}`) : fi ? "Tiekartta" : "Roadmap";
  }
  if (/Strategy|Strategia/i.test(table)) {
    const pg = table.match(/p\.?\s*(\d+)/i);
    return pg ? (fi ? `Strategia · s.${pg[1]}` : `Strategy · p.${pg[1]}`) : fi ? "Strategia" : "Strategy";
  }
  const tab = table.match(/Taulukko\s+(\d+(?:\.\d+)?)/i);
  const kuva = table.match(/Kuva\s+(\d+)/i);
  if (/Keuhkosyöpä|syöpärekisteri/i.test(table) || /syoparekisteri/i.test(fact.source_url || "")) {
    const tag = tab ? `T${tab[1]}` : kuva ? `K${kuva[1]}` : null;
    const base = fi ? "Syöpärekisteri" : "Cancer Registry";
    return tag ? `${base} · ${tag}` : base;
  }
  const short = table.split(/[;,:]/)[0].trim();
  return short || (fi ? "Lähde" : "Source");
}

