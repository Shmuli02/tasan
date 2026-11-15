/** User-set assumptions applied to published baselines. No interpolated on-time rates. */

export const ASSUMPTION_NOTE =
  "Every day-cut or percentage-point change below is a user-set assumption, not a published effect size and not a measured 6-week compliance rate. Surgery and drug-therapy baselines are the published Taulukko 4.1 medians (diagnosis to first treatment, 2018 to mid-2022, by home region, modality-specific subsets). The curative-share slider uses the age-adjusted Kuva 16 chart estimates (not the crude Taulukko 11 share). No county publishes the official 6-week referral-to-treatment compliance rate; this tool does not invent one.";

/** Projected surgery medians are floored at 1 day. A 0-day median is not shown: the published North Q1 of 0 days already means at least a quarter of these surgical patients have surgery on the diagnosis date, not that a typical wait can be assumed to be zero. */
export const SURGERY_MEDIAN_FLOOR_DAYS = 1;

export function applyDaysCut(median: number | null | undefined, assumedCutDays: number, floor = 0): number | null {
  if (median == null || Number.isNaN(median)) return null;
  return Math.max(floor, Math.round((median - assumedCutDays) * 10) / 10);
}

export function applyShareLift(share: number | null | undefined, assumedPp: number): number | null {
  if (share == null || Number.isNaN(share)) return null;
  return Math.max(0, Math.min(100, Math.round((share + assumedPp) * 10) / 10));
}
