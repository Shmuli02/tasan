import type { KeyMessageFile, Region, StageId } from "../types";
import {
  dataset,
  formatValue,
  indicatorForStage,
  recById,
  STAGE_ORDER,
} from "./data";

export interface StageSpread {
  stage: StageId;
  indicatorId: string;
  label: string;
  unit: string;
  higher_is_better: boolean;
  decimals: number;
  target: number | null;
  national: number | null;
  min: number;
  max: number;
  range: number;
  minRegions: Region[];
  maxRegions: Region[];
}

export function includedRegions(): Region[] {
  return dataset.regions.regions.filter((r) => r.include_in_national !== false);
}

export function stageSpreads(): StageSpread[] {
  const regions = includedRegions();
  return STAGE_ORDER.map((stage) => {
    const nat = indicatorForStage(dataset.regions.national, stage);
    const rows = regions
      .map((r) => ({ r, ind: indicatorForStage(r, stage) }))
      .filter((x) => x.ind && x.ind.value != null) as { r: Region; ind: NonNullable<ReturnType<typeof indicatorForStage>> }[];
    const usable = rows.filter((x) => x.ind.value != null && !x.ind.missing && !x.ind.exclude_from_ranking);
    const values = usable.map((x) => x.ind.value as number);
    const min = values.length ? Math.min(...values) : NaN;
    const max = values.length ? Math.max(...values) : NaN;
    return {
      stage,
      indicatorId: nat?.id ?? "",
      label: nat?.label ?? stage,
      unit: nat?.unit ?? "",
      higher_is_better: nat?.higher_is_better ?? true,
      decimals: nat?.decimals ?? 0,
      target: nat?.target ?? null,
      national: nat?.value ?? null,
      min,
      max,
      range: values.length ? max - min : 0,
      minRegions: usable.filter((x) => x.ind.value === min).map((x) => x.r),
      maxRegions: usable.filter((x) => x.ind.value === max).map((x) => x.r),
    };
  });
}

export function widestStage(): StageSpread {
  const spreads = stageSpreads();
  return [...spreads].sort((a, b) => b.range - a.range)[0];
}

export function furthestFromTarget(stage: StageId, limit = 5): { region: Region; value: number; gap: number }[] {
  const nat = indicatorForStage(dataset.regions.national, stage);
  const higher = nat?.higher_is_better ?? true;
  const target = nat?.target ?? nat?.value;
  const rows = includedRegions()
    .map((r) => {
      const ind = indicatorForStage(r, stage);
      if (ind?.value == null || ind.missing || ind.exclude_from_ranking) return null;
      const ref = target ?? 0;
      const gap = higher ? ref - ind.value : ind.value - ref;
      return { region: r, value: ind.value, gap };
    })
    .filter((x): x is { region: Region; value: number; gap: number } => x != null)
    .sort((a, b) => b.gap - a.gap);
  return rows.slice(0, limit);
}

export function autoKeyMessage(): Required<Pick<KeyMessageFile, "headline" | "gap" | "where_in_pathway" | "what_to_do">> & {
  source_ids: string[];
  auto: boolean;
} {
  const km = dataset.keyMessage;
  const hasManual = Boolean(km.headline && km.gap && km.where_in_pathway && km.what_to_do);
  if (hasManual) {
    return {
      headline: km.headline!,
      gap: km.gap!,
      where_in_pathway: km.where_in_pathway!,
      what_to_do: km.what_to_do!,
      source_ids: km.source_ids ?? [],
      auto: false,
    };
  }
  const wide = widestStage();
  const worst = (wide.higher_is_better ? wide.minRegions : wide.maxRegions)
    .map((r) => r.name)
    .join(", ");
  const best = (wide.higher_is_better ? wide.maxRegions : wide.minRegions)
    .map((r) => r.name)
    .join(", ");
  const rec =
    recById(km.primary_rec_id) ??
    dataset.recs.recommendations.find((r) => r.stage === wide.stage) ??
    dataset.recs.recommendations[0];
  const stageLabel = dataset.regions.stages.find((s) => s.id === wide.stage)?.label ?? wide.stage;
  return {
    headline: `The widest regional gap in the loaded dataset appears at ${stageLabel.toLowerCase()}.`,
    gap: `${wide.label} ranges from ${formatValue(wide.min, wide.unit, wide.decimals)} to ${formatValue(wide.max, wide.unit, wide.decimals)} (${wide.range.toFixed(wide.decimals)} point spread). Lowest: ${worst}. Highest: ${best}.`,
    where_in_pathway: `Compared with the other pathway stages, ${stageLabel.toLowerCase()} shows the largest county-to-county spread.`,
    what_to_do: rec
      ? (rec.what || rec.action || rec.title)
      : "Add concrete recommendations in recs/recommendations.json.",
    source_ids: km.source_ids ?? [],
    auto: true,
  };
}
