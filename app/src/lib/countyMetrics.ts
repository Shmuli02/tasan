import { crudeForCounty, dataset } from "./data";

export type CountyMetrics = {
  id: string;
  name: string;
  nameFi: string;
  agestdMen?: { value: number; ci95?: [number, number] };
  agestdWomen?: { value: number; ci95?: [number, number] };
  crude?: { share_pct: number; n: number; N: number };
};

export function countyMetrics(id: string): CountyMetrics {
  const region = dataset.regions.regions.find((r) => r.id === id);
  const ind = region?.indicators.find((i) => i.id === "lung_curative_share");
  const men = ind && !ind.missing && ind.men && typeof ind.men.value === "number" ? ind.men : undefined;
  const women = ind && !ind.missing && ind.women && typeof ind.women.value === "number" ? ind.women : undefined;
  const crude = crudeForCounty(id);
  return {
    id,
    name: region?.name ?? id,
    nameFi: region?.name_fi || region?.name || id,
    agestdMen: men
      ? { value: men.value, ci95: men.ci95 as [number, number] | undefined }
      : undefined,
    agestdWomen: women
      ? { value: women.value, ci95: women.ci95 as [number, number] | undefined }
      : undefined,
    crude: crude ? { share_pct: crude.share_pct, n: crude.n, N: crude.N } : undefined,
  };
}

export function allCountyMetrics(): CountyMetrics[] {
  return dataset.regions.regions.map((r) => countyMetrics(r.id));
}

export function countyHoverText(id: string, lang: "fi" | "en"): string {
  const m = countyMetrics(id);
  const name = lang === "fi" ? m.nameFi : m.name;
  const parts: string[] = [];
  if (m.agestdMen) {
    parts.push(
      lang === "fi"
        ? `noin ${m.agestdMen.value} % · miehet, ikävakioitu, kaavioarvio`
        : `about ${m.agestdMen.value}% · men, age-adjusted, chart estimate`,
    );
  }
  if (m.crude) {
    parts.push(
      lang === "fi"
        ? `karkea ${m.crude.share_pct} % (Taulukko 11, kaikki iät)`
        : `crude ${m.crude.share_pct}% (Table 11, all ages)`,
    );
  }
  if (!parts.length) return `${name}: ${lang === "fi" ? "Ei julkista tietoa" : "No public data"}`;
  return `${name}: ${parts.join(" · ")}`;
}
