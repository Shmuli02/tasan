import regions from "../content/regions.json";
import sources from "../content/sources.json";
import keyMessage from "../content/key_message.json";
import recs from "../content/recommendations.json";
import counties from "../content/counties.json";
import report from "../content/_load_report.json";
import hero from "../content/hero.json";
import facts from "../content/facts.json";
import type {
  Dataset,
  FactsFile,
  HeroFile,
  IndicatorCatalogEntry,
  IndicatorValue,
  Recommendation,
  Region,
  RegionsFile,
  ResolvedIndicator,
  Source,
  StageId,
} from "../types";

export const dataset: Dataset = {
  regions: regions as RegionsFile,
  sources: sources as Dataset["sources"],
  keyMessage: keyMessage as Dataset["keyMessage"],
  recs: recs as unknown as Dataset["recs"],
  counties: counties as Dataset["counties"],
  report: report as Dataset["report"],
  hero: hero as unknown as HeroFile,
  facts: facts as FactsFile,
};

export function sourceById(id: string | undefined | null): Source | undefined {
  if (!id) return undefined;
  return dataset.sources.sources.find((s) => s.id === id);
}

export function catalogById(id: string): IndicatorCatalogEntry | undefined {
  return dataset.regions.indicator_catalog.find((c) => c.id === id);
}

export function resolveIndicator(
  value: IndicatorValue,
  catalog = dataset.regions.indicator_catalog,
): ResolvedIndicator {
  const cat = catalog.find((c) => c.id === value.id);
  return {
    id: value.id,
    stage: value.stage ?? cat?.stage ?? "detection",
    label: value.label ?? cat?.label ?? value.id,
    unit: value.unit ?? cat?.unit ?? "",
    higher_is_better: value.higher_is_better ?? cat?.higher_is_better ?? true,
    decimals: cat?.decimals ?? 0,
    target: value.target ?? cat?.target ?? null,
    target_source_id: cat?.target_source_id,
    target_note: cat?.target_note,
    goal: cat?.goal,
    goal3_indicator: cat?.goal3_indicator,
    value: typeof value.value === "number" ? value.value : value.value == null ? null : Number(value.value),
    year: value.year ?? null,
    source_id: value.source_id,
    is_example: Boolean(value.is_example),
    note: value.note,
    missing: Boolean(value.missing) || value.value == null,
    missing_reason: value.missing_reason,
    yta_id: value.yta_id,
    data_quality: value.data_quality,
    exclude_from_ranking: value.exclude_from_ranking,
    numerator: value.numerator,
    denominator: value.denominator,
    ci95_low: value.ci95_low,
    ci95_high: value.ci95_high,
    iqr: value.iqr,
    men: value.men ?? undefined,
    women: value.women ?? undefined,
    measure_label: value.measure_label ?? undefined,
  };
}

export function indicatorsOf(place: { indicators: IndicatorValue[] }): ResolvedIndicator[] {
  return place.indicators.map((v) => resolveIndicator(v));
}

export function indicatorForStage(
  place: { indicators: IndicatorValue[] },
  stage: StageId,
): ResolvedIndicator | undefined {
  const resolved = indicatorsOf(place);
  const primary = dataset.regions.indicator_catalog.find((c) => c.stage === stage);
  if (primary) {
    const match = resolved.find((i) => i.id === primary.id);
    if (match) return match;
  }
  return resolved.find((i) => i.stage === stage);
}

export function regionById(id: string | null | undefined): Region | undefined {
  if (!id) return undefined;
  return dataset.regions.regions.find((r) => r.id === id);
}

export function recById(id: string | null | undefined): Recommendation | undefined {
  if (!id) return undefined;
  return dataset.recs.recommendations.find((r) => r.id === id);
}

export function goal3Label(id: string | null | undefined): string | undefined {
  if (!id) return undefined;
  return dataset.recs.goal3_indicators?.find((g) => g.id === id)?.label;
}

export function isExampleApp(): boolean {
  return Boolean(
    dataset.report.is_example ||
      dataset.regions.meta.is_example ||
      dataset.keyMessage.meta.is_example ||
      dataset.recs.meta.is_example,
  );
}

export function formatCi(low?: number | null, high?: number | null): string {
  if (low == null || high == null || Number.isNaN(Number(low)) || Number.isNaN(Number(high))) return "";
  return `${Number(low).toFixed(1)}–${Number(high).toFixed(1)}`;
}

export function formatValue(
  value: number | null | undefined,
  unit = "",
  decimals = 0,
): string {
  if (value == null || Number.isNaN(value)) return "n/a";
  const n = value.toFixed(decimals);
  return unit === "%" ? `${n}%` : unit ? `${n} ${unit}` : n;
}

export function formatDelta(delta: number, unit: string, decimals = 0): string {
  const sign = delta > 0 ? "+" : "";
  const u = unit === "percentage points" || unit === "%" ? " pp" : unit ? ` ${unit}` : "";
  return `${sign}${delta.toFixed(decimals)}${u}`;
}

export const STAGE_ORDER: StageId[] = ["detection", "referral", "diagnosis", "treatment"];

export function isMissing(ind: { missing?: boolean; value: number | null } | undefined): boolean {
  return !ind || ind.missing === true || ind.value == null;
}

export function formatIndicatorValue(ind: ResolvedIndicator | undefined): string {
  if (!ind || ind.missing || ind.value == null) return "No public data";
  return formatValue(ind.value, ind.unit, ind.decimals);
}

/** Fallback if recommendations.json has not yet supplied a clock note. */
export const DEFAULT_TASAN_CLOCK_NOTE =
  "Target per THL Ohjaus 21/2016 (marked outdated; no lung-specific limit; new cancer-specific targets due 2026-28, roadmap 3.1.2). Day-28 alert and 80% goal are Tasan design choices.";

export function tasanClockNote(): string {
  const recs = dataset.recs as { tasan_clock_note?: string; clock_note?: string; target_times_caveat?: string };
  return (
    recs.tasan_clock_note ||
    recs.clock_note ||
    dataset.hero?.tasan_clock_note ||
    dataset.keyMessage?.tasan_clock_note ||
    DEFAULT_TASAN_CLOCK_NOTE
  );
}

export function leadRecId(): string {
  const recs = dataset.recs as { lead_id?: string; centrepiece_id?: string; primary_rec_id?: string };
  return recs.lead_id || recs.centrepiece_id || recs.primary_rec_id || dataset.keyMessage.primary_rec_id || "T3";
}

export function featuredRecIds(): string[] {
  const recs = dataset.recs;
  const lead = leadRecId();
  const fromFile = recs.display_ids?.filter(Boolean) ?? [];
  const top = recs.top3_ids?.filter(Boolean) ?? recs.recommendations.filter((r) => r.top3).map((r) => r.id);
  const rest = (fromFile.length ? fromFile : top).filter((id) => id !== lead);
  const ordered = [lead, ...rest];
  return ordered.filter((id, i) => ordered.indexOf(id) === i && recs.recommendations.some((r) => r.id === id));
}

export const KPI_TARGET_LABEL = "proposed peer benchmark";

export function crudeForCounty(id: string | null) {
  const pack = dataset.hero.crude_curative;
  if (!pack || !id) return null;
  const row = pack.counties.find((c) => c.code === id);
  if (!row) return null;
  return { ...row, national_pct: pack.national_pct, national_n: pack.national_n, national_N: pack.national_N, period: pack.period, source_table: pack.source_table, source_url: pack.source_url, measure_label: pack.measure_label };
}
