import ranked from "../content/charts/curative_agestd_ranked.json";
import profiles from "../content/charts/county_profiles.json";
import { dataset } from "./data";

type Sid = { id: string; source_url: string | null; source_table: string | null };
type RankedRec = {
  sex: "men" | "women";
  region: string;
  region_code: string;
  level: string;
  value_pct: number | null;
  ci95_low: number | null;
  ci95_high: number | null;
  rank: number | null;
  rank_of: number | null;
  measure_type: string;
  fact_ids?: string[];
  null_reason?: string;
  note?: string;
  sid?: string;
};
type Profile = {
  region: string;
  region_name_fi: string;
  region_code: string;
  curative_crude_pct: number | null;
  curative_n: number | null;
  curative_N: number | null;
  curative_ci95_low?: number | null;
  curative_ci95_high?: number | null;
  people_gap_per_year?: number | null;
  curative_agestd_men_pct?: number | null;
  curative_agestd_men_ci95_low?: number | null;
  curative_agestd_men_ci95_high?: number | null;
  curative_agestd_women_pct?: number | null;
  curative_agestd_women_ci95_low?: number | null;
  curative_agestd_women_ci95_high?: number | null;
  src?: Record<string, { measure_type?: string; fact_ids?: string[]; null_reason?: string }>;
};

export type CountyProfile = Profile;
export type MeasureMode = "crude" | "agestd-men";

export const MAP_RAMP = ["#16233F", "#2D6B7D", "#4F9C9C", "#86BFB9", "#BCDCD6", "#E6F2EF"] as const;

export function rampColor(value: number | null, min: number, max: number): string {
  if (value == null || !Number.isFinite(min) || !Number.isFinite(max) || max === min) return "#D9D4C9";
  const t = (value - min) / (max - min);
  const i = Math.max(0, Math.min(MAP_RAMP.length - 1, Math.round(t * (MAP_RAMP.length - 1))));
  return MAP_RAMP[i];
}

export function allCountyProfiles(): Profile[] {
  return profileDoc.counties;
}

export function nationalCrude(): { pct: number; factId?: string } | undefined {
  const n = (profiles as { national?: { curative_crude_pct?: number; src?: Record<string, { fact_ids?: string[] }> } }).national;
  if (n?.curative_crude_pct == null) return undefined;
  return { pct: n.curative_crude_pct, factId: n.src?.curative_crude?.fact_ids?.[0] };
}

export function crudeFactIds(id: string): string[] {
  return countyProfile(id)?.src?.curative_crude?.fact_ids ?? [];
}

export const SHORT_NAME: Record<string, { en: string; fi: string }> = {
  "21": { en: "Lapland", fi: "Lappi" },
  "11": { en: "South Karelia", fi: "Etelä-Karjala" },
  "10": { en: "Kymenlaakso", fi: "Kymenlaakso" },
  "20": { en: "Kainuu", fi: "Kainuu" },
  "14": { en: "North Karelia", fi: "Pohjois-Karjala" },
  "18": { en: "Central Ostrob.", fi: "Keski-Pohjanmaa" },
  "07": { en: "Kanta-Häme", fi: "Kanta-Häme" },
  "12": { en: "South Savo", fi: "Etelä-Savo" },
  "19": { en: "North Ostrobothnia", fi: "Pohjois-Pohjanmaa" },
  "05": { en: "Southwest Finland", fi: "Varsinais-Suomi" },
  "13": { en: "North Savo", fi: "Pohjois-Savo" },
  "06": { en: "Satakunta", fi: "Satakunta" },
  "15": { en: "Central Finland", fi: "Keski-Suomi" },
  "17": { en: "Ostrobothnia", fi: "Pohjanmaa" },
  "01": { en: "East Uusimaa", fi: "Itä-Uusimaa" },
  "09": { en: "Päijät-Häme", fi: "Päijät-Häme" },
  "16": { en: "South Ostrobothnia", fi: "Etelä-Pohjanmaa" },
  "08": { en: "Pirkanmaa", fi: "Pirkanmaa" },
  "03": { en: "West Uusimaa", fi: "Länsi-Uusimaa" },
  "90": { en: "Helsinki", fi: "Helsinki" },
  "02": { en: "Central Uusimaa", fi: "Keski-Uusimaa" },
  "04": { en: "Vantaa-Kerava", fi: "Vantaa-Kerava" },
};

export function shortName(id: string, lang: "en" | "fi"): string {
  const s = SHORT_NAME[id];
  if (s) return lang === "fi" ? s.fi : s.en;
  const r = dataset.regions.regions.find((x) => x.id === id);
  return lang === "fi" ? r?.name_fi || r?.name || id : r?.name || id;
}

export function measureValue(id: string, mode: MeasureMode): { value: number | null; missing: boolean; reason?: string; factIds: string[] } {
  if (mode === "crude") {
    const p = countyProfile(id);
    if (p?.curative_crude_pct != null) return { value: p.curative_crude_pct, missing: false, factIds: crudeFactIds(id) };
    return { value: null, missing: true, reason: "No public data", factIds: [] };
  }
  const rec = agestdFor(id, "men");
  if (rec?.value_pct != null) return { value: rec.value_pct, missing: false, factIds: rec.fact_ids ?? [] };
  return { value: null, missing: true, reason: rec?.null_reason || "No public data", factIds: rec?.fact_ids ?? [] };
}


const rankedDoc = ranked as { records: RankedRec[]; sid_catalog: Sid[]; method?: string; caveat?: string };
const profileDoc = profiles as { counties: Profile[]; sid_catalog: Sid[] };

export const agestdCaveat = rankedDoc.caveat ?? "Age-standardised, NOT stage-adjusted; chart estimates, not published numbers; say “about”.";

export function lookupSid(catalog: Sid[] | undefined, sid?: string): Sid | undefined {
  if (!sid || !catalog) return undefined;
  return catalog.find((s) => s.id === sid);
}

export function agestdRecords(sex: "men" | "women", level = "county"): RankedRec[] {
  return rankedDoc.records.filter((r) => r.sex === sex && r.level === level);
}

export function agestdFor(id: string, sex: "men" | "women" = "men"): RankedRec | undefined {
  return rankedDoc.records.find((r) => r.sex === sex && r.level === "county" && r.region_code === id);
}

export function agestdNational(sex: "men" | "women"): RankedRec | undefined {
  return rankedDoc.records.find((r) => r.sex === sex && r.level === "national_reference_sex_specific");
}

export function countyProfile(id: string): Profile | undefined {
  return profileDoc.counties.find((c) => c.region_code === id);
}

export function countyHoverText(id: string, lang: "fi" | "en", mode: MeasureMode = "agestd-men"): string {
  const region = dataset.regions.regions.find((r) => r.id === id);
  const name = lang === "fi" ? region?.name_fi || region?.name || id : region?.name || id;
  if (mode === "crude") {
    const p = countyProfile(id);
    if (p?.curative_crude_pct != null) {
      return lang === "fi"
        ? `${name}: karkea ${p.curative_crude_pct} % (Taulukko 11, kaikki iät)`
        : `${name}: crude ${p.curative_crude_pct}% (Table 11, all ages)`;
    }
    return `${name}: ${lang === "fi" ? "Ei julkista tietoa" : "No public data"}`;
  }
  const men = agestdFor(id, "men");
  const women = agestdFor(id, "women");
  const prof = countyProfile(id);
  const parts: string[] = [];
  if (men?.value_pct != null) {
    parts.push(lang === "fi" ? `noin ${men.value_pct} % · miehet, ikävakioitu, kaavioarvio` : `about ${men.value_pct}% · men, age-adjusted, chart estimate`);
  }
  if (women?.value_pct != null) {
    parts.push(lang === "fi" ? `naiset noin ${women.value_pct} %` : `women about ${women.value_pct}%`);
  }
  if (prof?.curative_crude_pct != null) {
    parts.push(lang === "fi" ? `karkea ${prof.curative_crude_pct} % (Taulukko 11, kaikki iät)` : `crude ${prof.curative_crude_pct}% (Table 11, all ages)`);
  }
  if (!parts.length) {
    const reason = men?.null_reason || women?.null_reason;
    return `${name}: ${lang === "fi" ? "Ei julkista tietoa" : "No public data"}${reason ? ` · ${reason}` : ""}`;
  }
  if (men?.value_pct == null && men?.null_reason) {
    parts.unshift(lang === "fi" ? "Ei julkista ikävakioitua lukua" : "No public age-adjusted figure");
  }
  return `${name}: ${parts.join(" · ")}`;
}

export function agestdNullReason(id: string, sex: "men" | "women" = "men"): string | undefined {
  return agestdFor(id, sex)?.null_reason;
}
