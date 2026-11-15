/** Display-layer role labels. Recs must already be roles-only; this strips verification clauses and never surfaces a personal name. */
const VERIFY_RE = /\s*\(role holder[^)]*\)/gi;

export function displayRole(raw?: string | null): string {
  if (!raw) return "";
  return raw
    .replace(VERIFY_RE, "")
    .replace(/\s*line-managed by the\s+vs\.?\s*/gi, " ")
    .replace(/\bvs\.\s*hoitotyön johtaja\s*\/\s*/gi, "")
    .replace(/\s{2,}/g, " ")
    .trim();
}

export function signerRole(lang: "en" | "fi", countyName: string, raw?: string | null): string {
  const cleaned = displayRole(raw);
  if (cleaned) return cleaned;
  return lang === "fi"
    ? `Johtajaylilääkäri, ${countyName}`
    : `Johtajaylilääkäri / Chief Medical Officer, ${countyName} wellbeing services county`;
}

export function ownerRole(lang: "en" | "fi", countyName: string, raw?: string | null): string {
  const cleaned = displayRole(raw);
  if (cleaned) return cleaned;
  return lang === "fi"
    ? `Hoitaja-navigator (1 FTE), esihenkilönä hoitotyön johtaja, ${countyName}`
    : `Nurse navigator (1 FTE), Acting Director of Nursing, ${countyName} wellbeing services county`;
}

/** Counties that currently have a pre-generated in-app brief. */
export const BRIEF_COUNTY_IDS = new Set(["21"]);

export function hasPreGeneratedBrief(countyId: string | null | undefined): boolean {
  return typeof countyId === "string" && BRIEF_COUNTY_IDS.has(countyId);
}
