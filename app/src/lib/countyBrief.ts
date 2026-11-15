import type { PilotBriefDraft } from "./briefDraft";
import { SHORT_NAME, countyProfile, shortName } from "./chartData";
import { displayRole } from "./roles";

const ALIASES: Record<string, string[]> = {
  "01": ["East Uusimaa", "Itä-Uusimaa", "Itä-Uudenmaan", "Östra Nyland"],
  "02": ["Central Uusimaa", "Keski-Uusimaa", "Keski-Uudenmaan", "Mellersta Nyland"],
  "03": ["West Uusimaa", "Länsi-Uusimaa", "Länsi-Uudenmaan", "Västra Nyland"],
  "04": ["Vantaa-Kerava", "Vantaa and Kerava", "Vantaan ja Keravan", "Vanda-Kervo"],
  "05": ["Southwest Finland", "Varsinais-Suomi", "Varsinais-Suomen", "Egentliga Finland"],
  "06": ["Satakunta", "Satakunnan"],
  "07": ["Kanta-Häme", "Kanta-Hämeen", "Egentliga Tavastland"],
  "08": ["Pirkanmaa", "Pirkanmaan", "Birkaland"],
  "09": ["Päijät-Häme", "Päijät-Hämeen", "Päijänne-Tavastland"],
  "10": ["Kymenlaakso", "Kymenlaakson", "Kymmenedalen"],
  "11": ["South Karelia", "Etelä-Karjala", "Etelä-Karjalan", "Södra Karelen"],
  "12": ["South Savo", "Etelä-Savo", "Etelä-Savon", "Södra Savolax"],
  "13": ["North Savo", "Pohjois-Savo", "Pohjois-Savon", "Norra Savolax"],
  "14": ["North Karelia", "Pohjois-Karjala", "Pohjois-Karjalan", "Norra Karelen"],
  "15": ["Central Finland", "Keski-Suomi", "Keski-Suomen", "Mellersta Finland"],
  "16": ["South Ostrobothnia", "Etelä-Pohjanmaa", "Etelä-Pohjanmaan", "Södra Österbotten"],
  "17": ["Ostrobothnia", "Pohjanmaa", "Pohjanmaan", "Österbotten"],
  "18": ["Central Ostrobothnia", "Central Ostrob.", "Keski-Pohjanmaa", "Keski-Pohjanmaan", "Mellersta Österbotten"],
  "19": ["North Ostrobothnia", "Pohjois-Pohjanmaa", "Pohjois-Pohjanmaan", "Norra Österbotten"],
  "20": ["Kainuu", "Kainuun", "Kajanaland"],
  "21": ["Lapland", "Lappi", "Lapin", "Lappland"],
  "90": ["Helsinki", "Helsingin", "Helsingfors"],
};

function escapeRe(s: string): string {
  return s.replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
}

export type NamedCounty = { id?: string; label: string; isLapland: boolean; unknown?: boolean };

/** Places Tasan does not cover (Åland is not one of the 21 mainland counties or Helsinki). */
const UNLISTED = [
  "Åland", "Ålands", "Aland", "Ahvenanmaa", "Ahvenanmaan", "Ahvenanmaalle",
  "Ahvenanmaan maakunta", "Landskapet Åland", "Mariehamn", "Maarianhamina",
];

const BRIEF_NOISE = /\b(please|kindly|can you|could you|would you|voi(tko|sitko)?|luo|kirjoita|tee|laadi|draft|a|an|the|en|ett|pilot|brief|muistio|promemoria|pilottimuistio|pilotti|90-?day|90\s*päivän|päivän|day|luonnos|utkast|for|för|om|alueelle|alueella|alueen|tälle|tämän|this|that|county|counties|alue|område|wellbeing services county|hyvinvointialue(elle|en)?|maakunta(an)?|from|about)\b/gi;
const GENERIC_PLACE = /^(the\s+)?((this|that)\s+)?(county|alue|område|maakunta)?\.?$/i;

function mentionsUnlisted(q: string): string | null {
  for (const name of [...UNLISTED].sort((a, b) => b.length - a.length)) {
    const re = new RegExp(`(?:^|[^A-Za-zÄÖÅäöå])${escapeRe(name)}(?:[^A-Za-zÄÖÅäöå]|$)`, "i");
    if (re.test(q)) return name;
  }
  return null;
}

function leftoverPlace(q: string): string {
  return q.replace(BRIEF_NOISE, " ").replace(/[^A-Za-zÄÖÅäöå\- ]+/g, " ").replace(/\s+/g, " ").trim();
}

/** Longest-name win, so "North Ostrobothnia" is not "Ostrobothnia". */
export function countyFromText(q: string): NamedCounty {
  const hits: { id: string; len: number }[] = [];
  for (const [id, names] of Object.entries(SHORT_NAME)) {
    const bag = new Set([names.en, names.fi, ...(ALIASES[id] ?? [])].filter(Boolean));
    for (const name of bag) {
      const re = new RegExp(`(?:^|[^A-Za-zÄÖÅäöå])${escapeRe(name)}(?:[^A-Za-zÄÖÅäöå]|$)`, "i");
      if (re.test(q)) hits.push({ id, len: name.length });
    }
  }
  if (!hits.length) return { label: "", isLapland: false };
  hits.sort((a, b) => b.len - a.len);
  const id = hits[0].id;
  return { id, label: SHORT_NAME[id]?.en ?? id, isLapland: id === "21" };
}

export function briefTarget(q: string, uiCountyId?: string | null): NamedCounty {
  const named = countyFromText(q);
  if (named.id) return named;
  const unlisted = mentionsUnlisted(q);
  const leftover = leftoverPlace(q);
  // A named place that is not one of the 21 mainland counties or Helsinki:
  // never fall back to the on-screen county (Åland, typo, etc.).
  if (unlisted || (leftover && !GENERIC_PLACE.test(leftover))) {
    return { label: unlisted || leftover, isLapland: false, unknown: true };
  }
  if (uiCountyId && SHORT_NAME[uiCountyId]) {
    return { id: uiCountyId, label: SHORT_NAME[uiCountyId].en, isLapland: uiCountyId === "21" };
  }
  return { label: "", isLapland: false };
}

function fmtPct(n: number | null | undefined, digits = 1): string | null {
  if (n == null || !Number.isFinite(n)) return null;
  return n.toFixed(digits);
}

/** Schema-valid DRAFT, roles only, numbers from the county profile. */
export function buildCountyBrief(countyId: string, lang: "fi" | "sv" | "en" = "en"): PilotBriefDraft | null {
  const p = countyProfile(countyId);
  if (!p) return null;
  const en = shortName(countyId, "en");
  const fi = shortName(countyId, "fi");
  const county = lang === "fi" ? `${p.region_name_fi} (${en})` : `${p.region} (${fi})`;
  const crude = fmtPct(p.curative_crude_pct);
  const n = p.curative_n;
  const N = p.curative_N;
  const ci = p.curative_ci95_low != null && p.curative_ci95_high != null
    ? ` (95% CI ${fmtPct(p.curative_ci95_low)}–${fmtPct(p.curative_ci95_high)})`
    : "";
  const nat = "27.0";
  const men = fmtPct(p.curative_agestd_men_pct);
  const women = fmtPct(p.curative_agestd_women_pct);
  const counts = n != null && N != null ? ` (${n} of ${N})` : "";
  const line = crude
    ? `In ${en}, ${crude}% of lung cancer patients diagnosed 2019–2023 had a curative-treatment record within 12 months${counts}${ci}, against ${nat}% nationally. Not stage-adjusted.`
    : `Public crude curative-treatment share for ${en} is used where published; comparisons are not stage-adjusted.`;
  const metricBits = [
    crude ? `Crude share, 2019–2023: ${en} ${crude}%${counts}${ci} vs national ${nat}% (4009 of 14873).` : null,
    men && women ? `Age-standardised chart estimate, men ${men}% and women ${women}% in ${en}.` : null,
  ].filter(Boolean);
  const cmo = displayRole(`Johtajaylilääkäri / Chief Medical Officer, ${en} wellbeing services county`);
  const nurse = displayRole(`Acting Director of Nursing, ${en} wellbeing services county`);
  return {
    template_version: "tasan-pilot-brief-v1",
    status: "DRAFT",
    status_label: "DRAFT — not signed. Not discussed with the county.",
    project: "Tasan",
    title: `Tasan 90-day pilot – ${county}`,
    date_prepared: "2026-11-14",
    county,
    signer: { role: cmo },
    problem: {
      line,
      metric: metricBits.join(" ") || undefined,
      source: "Finnish Cancer Registry/THL/FICAN, Keuhkosyöpä Suomessa 2019–2023, Taulukot 10–11 and Kuva 16 — https://syoparekisteri.fi/assets/themes/ssy3/factsheets/keuhkosyoparaportti.html",
      caveat: "Crude registry shares, not age- or stage-adjusted (stage is missing for 47.7% nationally). Patients are counted by home county, not treating hospital. Illustrative draft, not a forecast or a lives-saved claim.",
    },
    action: {
      summary: "T3 pathway clock: measure each suspected lung cancer from referral to first treatment, raise an alert on day 28 with no treatment decision, and give every patient a named nurse navigator.",
      components: [
        "Clock: the 4 THL time points (referral, specialist visit, diagnosis, first treatment) per patient, weekly feed from county data.",
        "Day-28 alert: open pathways without a treatment decision go to the navigator and the responsible physician.",
        "Named nurse navigator (1.0 FTE): contacts every new suspected case and unblocks waits.",
        "Data-quality task: registry-completeness check first; recording practices differ by county.",
      ],
    },
    owners: [
      { role: `Signer / sponsor: ${cmo}` },
      { role: `Navigator line manager: ${nurse}` },
      { role: "Data / clock: county analytics unit / tietojohtaminen (to be assigned by the county)" },
    ],
    cost_range: {
      low_eur: 20339,
      high_eur: 23988,
      period: "90 days",
      basis: "1.0 FTE sairaanhoitaja (€3,174–4,048/month) + 0.5 FTE analyytikko (€4,663–4,891/month) × 3 months × 1.2314 employer contributions. Low = task-based pay, high = total earnings.",
      excludes: "No IT, physician time or treatment capacity costed (no sourced figure). No euro saving claimed.",
    },
    kpis: [
      { name: "Data completeness", target: "≥85% complete" },
      { name: "Treated within 42 days of referral", target: "80% within 42 days" },
      { name: "Day-28 alerts actioned", target: "≥90% within 2 working days" },
      { name: "Navigator contact", target: "≥90% of new suspected cases within 3 working days" },
    ],
    kpi_caveat: "Day-28 alert and the 80% target are Tasan design choices, not official targets. Completeness and contact rates are measured from county operational data, not the Cancer Registry publication.",
    stop_go: {
      go: "Go (extend) if ≥85% of pathways have all 4 time points, the own baseline is presented to the board, ≥90% of day-28 alerts are actioned within 2 working days and ≥90% of new cases are contacted within 3 working days.",
      stop: "Completeness <70% after one fix cycle: pause the clock and fix recording first. Otherwise extend 90 days with one named fix.",
      decider: `Johtajaylilääkäri / Chief Medical Officer, ${en} wellbeing services county, on the day-90 board report.`,
    },
  };
}

export function briefLooksLikeLapland(draft: { county?: string; title?: string } | null | undefined): boolean {
  if (!draft) return false;
  return /lapland|lapin|lappi|lappland/i.test(`${draft.county ?? ""} ${draft.title ?? ""}`);
}
