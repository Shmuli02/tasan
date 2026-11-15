import { useMemo, useState } from "react";
import type { StageId } from "../types";
import { dataset, formatCi, formatValue, isExampleApp } from "../lib/data";
import { agestdFor, agestdNullReason, countyHoverText, countyProfile, rampColor, MAP_RAMP, type MeasureMode } from "../lib/chartData";
import { UUSIMAA_IDS, featureCentroid, featurePath, featuresBBox, makeProjector } from "../lib/geo";
import { ExampleMark, TargetCaveat } from "./Cite";


const INSET_LABELS: Record<string, { en: string; fi: string }> = {
  "90": { en: "Helsinki", fi: "Helsinki" },
  "04": { en: "Vantaa-Kerava", fi: "Vantaa-Kerava" },
  "01": { en: "East Uusimaa", fi: "Itä-Uusimaa" },
  "03": { en: "West Uusimaa", fi: "Länsi-Uusimaa" },
  "02": { en: "Central Uusimaa", fi: "Keski-Uusimaa" },
};

const COLORS = [...MAP_RAMP];

export type MapLayer = "yta-surgery" | "yta-radiotherapy" | "yta-drug" | "curative" | "screening" | "referral";

export const LAYER_FOR_STAGE: Record<StageId, MapLayer> = {
  detection: "screening",
  referral: "referral",
  diagnosis: "yta-surgery",
  treatment: "curative",
};

function colorFor(value: number | null, min: number, max: number, higherIsBetter: boolean): string {
  if (value == null || !Number.isFinite(min) || !Number.isFinite(max) || max === min) return "#D9D4C9";
  let t = (value - min) / (max - min);
  if (!higherIsBetter) t = 1 - t;
  const i = Math.max(0, Math.min(COLORS.length - 1, Math.round(t * (COLORS.length - 1))));
  return COLORS[i];
}

function ytaOf(regionId: string): string | undefined {
  return dataset.hero.county_yta?.[regionId] ?? dataset.regions.regions.find((r) => r.id === regionId)?.yta_id;
}

function ytaWait(ytaId: string | undefined, modality: "surgery" | "radiotherapy" | "drug") {
  if (!ytaId) return undefined;
  return dataset.hero.yta_waits?.find((y) => y.id === ytaId)?.modalities?.[modality];
}

export function FinlandMap({
  stage,
  onStage,
  selectedId,
  onSelect,
  layer,
  onLayer,
  heroMode = false,
  compact = false,
  lang = "en",
  onHover,
  metric,
  dashboard = false,
}: {
  stage: StageId;
  onStage: (s: StageId) => void;
  selectedId: string | null;
  onSelect: (id: string | null) => void;
  layer: MapLayer;
  onLayer: (l: MapLayer) => void;
  heroMode?: boolean;
  compact?: boolean;
  lang?: "en" | "fi";
  onHover?: (id: string | null) => void;
  metric?: MeasureMode;
  dashboard?: boolean;
}) {
  const [hover, setHover] = useState<string | null>(null);
  function setHoverId(id: string | null) {
    setHover(id);
    onHover?.(id);
  }
  const isYta = layer.startsWith("yta-");
  const modality = layer === "yta-radiotherapy" ? "radiotherapy" : layer === "yta-drug" ? "drug" : "surgery";

  const features = dataset.counties.features;
  const main = useMemo(() => {
    const bbox = featuresBBox(features);
    const w = 420;
    const h = 620;
    const project = makeProjector(bbox, w, h, 12);
    return { w, h, project, paths: features.map((f) => ({ f, d: featurePath(f, project), c: featureCentroid(f) })) };
  }, [features]);

  const inset = useMemo(() => {
    const feats = features.filter((f) => UUSIMAA_IDS.has(f.properties.id));
    const bbox = featuresBBox(feats);
    const w = 200;
    const h = 200;
    const project = makeProjector(bbox, w, h, 10);
    return { w, h, project, paths: feats.map((f) => ({ f, d: featurePath(f, project), c: featureCentroid(f) })) };
  }, [features]);

  const countyIndicatorId =
    layer === "curative"
      ? "lung_curative_share"
      : layer === "screening"
        ? "colorectal_screening_share"
        : layer === "referral"
          ? "referral_within_3d_share"
          : "lung_dx_to_surgery_days";

  function countyValue(id: string): { value: number | null; missing: boolean; reason?: string } {
    if (isYta) {
      const w = ytaWait(ytaOf(id), modality);
      if (!w || w.median == null) return { value: null, missing: true, reason: "No public figure at collaborative-area or county level." };
      return { value: w.median, missing: false };
    }
    if (metric === "crude") {
      const p = countyProfile(id);
      if (p?.curative_crude_pct != null) return { value: p.curative_crude_pct, missing: false };
      return { value: null, missing: true, reason: "No public data" };
    }
    if (layer === "curative" || heroMode || metric === "agestd-men") {
      const rec = agestdFor(id, "men");
      if (rec?.value_pct != null) return { value: rec.value_pct, missing: false };
      return { value: null, missing: true, reason: rec?.null_reason || agestdNullReason(id) || "No public data" };
    }
    const r = dataset.regions.regions.find((x) => x.id === id);
    const ind = r?.indicators.find((i) => i.id === countyIndicatorId);
    if (!ind || ind.missing || ind.value == null || ind.exclude_from_ranking) {
      return { value: null, missing: true, reason: ind?.missing_reason || ind?.note || "No public data" };
    }
    return { value: ind.value, missing: false };
  }

  const scaleVals = isYta
    ? (dataset.hero.yta_waits || [])
        .map((y) => y.modalities[modality]?.median)
        .filter((v): v is number => v != null)
    : dataset.regions.regions
        .map((r) => countyValue(r.id))
        .filter((x) => !x.missing && x.value != null)
        .map((x) => x.value as number);
  const min = scaleVals.length ? Math.min(...scaleVals) : 0;
  const max = scaleVals.length ? Math.max(...scaleVals) : 1;
  const higherIsBetter = !isYta && layer !== "referral" ? layer === "curative" || layer === "screening" : isYta ? false : true;
  // referral: higher is better (processed within 3d). yta waits: lower is better.

  function paint(id: string): string {
    const v = countyValue(id);
    if (v.missing) return "url(#no-data-hatch)";
    return colorFor(v.value, min, max, higherIsBetter);
  }

  const stageDefs = dataset.regions.stages.slice().sort((a, b) => a.order - b.order);
  const activeId = hover ?? selectedId;
  const active = dataset.regions.regions.find((r) => r.id === activeId);

  function onClick(id: string) {
    onSelect(id);
  }

  const ranked = dataset.regions.regions
    .map((r) => ({ r, v: countyValue(r.id) }))
    .sort((a, b) => {
      if (a.v.missing && b.v.missing) return a.r.name.localeCompare(b.r.name);
      if (a.v.missing) return 1;
      if (b.v.missing) return -1;
      return higherIsBetter ? (a.v.value as number) - (b.v.value as number) : (b.v.value as number) - (a.v.value as number);
    });

  const unit = isYta ? "days" : layer === "curative" || layer === "screening" || layer === "referral" ? "%" : "";
  const decimals = isYta || layer !== "screening" ? 1 : 1;
  const title =
    layer === "yta-surgery"
      ? "Diagnosis to surgery, 2018 to mid-2022, by home region, surgical patients only (~11%) — YTA median days"
      : layer === "yta-radiotherapy"
        ? "Diagnosis to radiotherapy, 2018 to mid-2022, by home region — YTA median days (same table as surgery)"
        : layer === "yta-drug"
          ? "Diagnosis to systemic drug therapy, 2018 to mid-2022, by home region — YTA median days (same table as surgery)"
          : layer === "curative"
            ? "Age-adjusted 12-month curative-treatment share, 2019–2023 (chart estimate, not survival) — men’s figure colours the map"
            : layer === "screening"
              ? "Colorectal screening participation 2024 (county) — a separate, later cohort"
              : "Specialist referrals processed within 3 days, 2025 (county) — a separate indicator";

  if (dashboard) {
    const chipId = hover && hover !== selectedId ? hover : null;
    const chipText = chipId ? countyHoverText(chipId, lang, metric === "crude" ? "crude" : "agestd-men") : null;
    return (
      <div className="dash-map relative flex h-full min-h-0 w-full items-center justify-center">
        <svg viewBox={`0 0 ${main.w} ${main.h}`} preserveAspectRatio="xMidYMid meet" className="h-full w-full max-h-full max-w-full" role="img" aria-label={lang === "fi" ? "Kartta hyvinvointialueista" : "Map of Finnish wellbeing services counties"}>
          <defs>
            <pattern id="no-data-hatch" width="8" height="8" patternUnits="userSpaceOnUse" patternTransform="rotate(45)">
              <rect width="8" height="8" fill="#d9d4cc" />
              <line x1="0" y1="0" x2="0" y2="8" stroke="#8a8580" strokeWidth="2" />
            </pattern>
          </defs>
          {main.paths.map(({ f, d }) => {
            const id = f.properties.id;
            const isSel = selectedId === id;
            const isHov = hover === id;
            return (
              <path
                key={id}
                d={d}
                fill={paint(id)}
                stroke={isSel ? "#D9822B" : isHov ? "#16233F" : "#fff"}
                strokeWidth={isSel ? 2.5 : 0.9}
                strokeLinejoin="round"
                className="cursor-pointer"
                onMouseEnter={() => setHoverId(id)}
                onMouseLeave={() => setHoverId(null)}
                onMouseDown={(e) => e.preventDefault()}
                onClick={() => onClick(id)}
              />
            );
          })}
        </svg>
        {chipText ? (
          <div className="pointer-events-none absolute right-2 top-2 max-w-[16rem] rounded-[10px] border border-[var(--tz-line)] bg-white px-2.5 py-1.5 text-[12px] font-semibold leading-snug text-[var(--tz-ink-2)] shadow-[var(--tz-sh-2)]">
            {chipText}
          </div>
        ) : null}
      </div>
    );
  }

  return (
    <div className={heroMode ? "relative" : "grid gap-4 lg:grid-cols-[minmax(0,1fr)_260px]"}>
      <div className="relative">
        {heroMode ? null : (
        <div className="mb-3 flex flex-wrap items-center gap-2">
          {stageDefs.map((s) => (
            <button
              key={s.id}
              type="button"
              onClick={() => {
                onStage(s.id);
                onLayer(LAYER_FOR_STAGE[s.id]);
              }}
              className={`rounded-full px-3 py-1 text-xs font-semibold ${
                LAYER_FOR_STAGE[s.id] === layer || (s.id === stage && !isYta)
                  ? "bg-navy text-white"
                  : s.id === "diagnosis" && isYta
                    ? "bg-navy text-white"
                    : "bg-paper text-muted hover:bg-line"
              }`}
            >
              {s.short ?? s.label}
            </button>
          ))}
        </div>
        )}
        {heroMode ? null : isYta ? (
          <div className="mb-3 flex flex-wrap gap-1.5">
            {(["yta-surgery", "yta-radiotherapy", "yta-drug"] as MapLayer[]).map((l) => (
              <button
                key={l}
                type="button"
                onClick={() => onLayer(l)}
                className={`rounded-full px-2.5 py-0.5 text-[11px] ${layer === l ? "bg-teal text-white" : "bg-paper text-muted"}`}
              >
                {l === "yta-surgery" ? "Surgery" : l === "yta-radiotherapy" ? "Radiotherapy" : "Drug therapy"}
              </button>
            ))}
          </div>
        ) : null}
        {heroMode ? null : <p className="mb-2 text-xs text-muted">{title}</p>}
        {heroMode ? null : isYta ? (
          <>
            <p className="mb-2 rounded-lg bg-gold-soft/70 px-2 py-1 text-[11px] leading-snug text-ink">
              Published only for the five collaborative areas (YTA), not for the 22 counties. Counties are coloured with
              their YTA figure — this is not a county measurement. Clock starts at Cancer Registry diagnosis, not at
              referral, so these days are not 6-week compliance. Hatched areas have no public figure.
            </p>
            <TargetCaveat compact />
            {layer === "yta-surgery" && surgeryHeadlineCaveat() ? (
              <p className="mb-2 text-[11px] leading-snug text-ink">{surgeryHeadlineCaveat()}</p>
            ) : null}
          </>
        ) : null}
        <div className={"relative overflow-hidden rounded-2xl border border-line " + ((compact || heroMode) ? (compact ? "max-h-[460px]" : "map-frame-hero") : "")} style={{background:"#E6F2EF"}}>
          <svg viewBox={`0 0 ${main.w} ${main.h}`} className={"w-full " + ((compact || heroMode) ? (compact ? "h-full max-h-[460px]" : "h-full map-frame-hero") : "h-auto")} role="img" aria-label={lang === "fi" ? "Kartta hyvinvointialueista" : "Map of Finnish wellbeing services counties"}>
            <defs>
              <pattern id="no-data-hatch" width="8" height="8" patternUnits="userSpaceOnUse" patternTransform="rotate(45)">
                <rect width="8" height="8" fill="#d9d4cc" />
                <line x1="0" y1="0" x2="0" y2="8" stroke="#8a8580" strokeWidth="2" />
              </pattern>
            </defs>
            {isExampleApp() ? (
              <text x={main.w / 2} y={36} textAnchor="middle" fill="#9a6410" fontSize="13" fontWeight="700" opacity="0.7">
                EXAMPLE DATA
              </text>
            ) : null}
            {main.paths.map(({ f, d, c }) => {
              const id = f.properties.id;
              const isSel = selectedId === id;
              const isHov = hover === id;
              const p = heroMode ? null : main.project(c.lon, c.lat);
              return (
                <g key={id}>
                  <path
                    d={d}
                    fill={paint(id)}
                    stroke={isSel ? "#D9822B" : isHov ? "#16233F" : "#fff"}
                    strokeWidth={isSel ? 2.5 : isHov ? 1.6 : 1}
                    className="cursor-pointer"
                    onMouseEnter={() => setHoverId(id)}
                    onMouseLeave={() => setHoverId(null)}
                    onMouseDown={(e) => e.preventDefault()}
                    onClick={() => onClick(id)}
                  >
                    <title>{countyHoverText(id, lang, metric === "crude" ? "crude" : "agestd-men")}</title>
                  </path>
                  {!heroMode && p && (isSel || isHov) ? (
                    <text x={Math.min(Math.max(p.x, 36), main.w - 36)} y={Math.min(Math.max(p.y, 16), main.h - 12)} textAnchor="middle" className="pointer-events-none" fill="#fff" fontSize="10" fontWeight="700" style={{ textShadow: "0 0 4px #151c24" }}>
                      {shortName(id)}
                    </text>
                  ) : null}
                </g>
              );
            })}
          </svg>
          {heroMode ? (() => {
            const chipId = hover ?? selectedId;
            if (!chipId) return null;
            return (
              <div className="pointer-events-none absolute left-3 top-3 z-10 max-w-[min(100%,22rem)] rounded-lg border border-line bg-white/95 px-3 py-1.5 text-[13px] font-medium leading-snug text-ink shadow-sm">
                {countyHoverText(chipId, lang)}
              </div>
            );
          })() : null}
        </div>
        <div className={heroMode ? "mt-2 flex flex-wrap items-start justify-between gap-3" : "mt-3 flex flex-wrap items-start justify-between gap-4"}>
          {heroMode ? null : (
          <div className="rounded-xl border border-line bg-white/95 p-2 shadow-sm">
            <p className="mb-1 text-[10px] font-semibold uppercase tracking-wider text-muted">Uusimaa inset · Helsinki is easier to click here</p>
            <svg viewBox={`0 0 ${inset.w} ${inset.h}`} width={200} height={200} role="img" aria-label="Uusimaa inset">
              <defs>
                <pattern id="no-data-hatch-inset" width="8" height="8" patternUnits="userSpaceOnUse" patternTransform="rotate(45)">
                  <rect width="8" height="8" fill="#d9d4cc" />
                  <line x1="0" y1="0" x2="0" y2="8" stroke="#8a8580" strokeWidth="2" />
                </pattern>
              </defs>
              {inset.paths.map(({ f, d, c }) => {
                const id = f.properties.id;
                const isSel = selectedId === id;
                const isHov = hover === id;
                const p = inset.project(c.lon, c.lat);
                const fill = countyValue(id).missing ? "url(#no-data-hatch-inset)" : paint(id);
                return (
                  <g key={id}>
                    <path
                      d={d}
                      fill={fill}
                      stroke={isSel ? "#D9822B" : isHov ? "#16233F" : "#fff"}
                      strokeWidth={isSel ? 2.5 : 1}
                      className="cursor-pointer"
                      onMouseEnter={() => setHoverId(id)}
                      onMouseLeave={() => setHoverId(null)}
                      onMouseDown={(e) => e.preventDefault()}
                      onClick={() => onClick(id)}
                    />
                    <text x={p.x} y={p.y} textAnchor="middle" fontSize="8" fontWeight="600" fill="#151c24" className="pointer-events-none">
                      {shortName(id)}
                    </text>
                  </g>
                );
              })}
            </svg>
          </div>
          )}
          <div className={`mt-2 flex flex-1 flex-col justify-end ${heroMode ? "text-[13px] leading-snug text-ink" : "text-xs text-muted"}`}>
            {heroMode ? (
            <div className="flex w-full flex-wrap items-start justify-between gap-4">
              <div className="min-w-[14rem] flex-1">
                <div className="flex flex-wrap items-center gap-2">
                  <span className="tz-num text-[13px] font-semibold">{lang === "fi" ? "noin 16 %" : "about 16%"}</span>
                  <span className="inline-flex overflow-hidden rounded" aria-hidden>
                    {COLORS.map((c) => (
                      <span key={c} className="inline-block h-3 w-7" style={{ background: c }} />
                    ))}
                  </span>
                  <span className="tz-num text-[13px] font-semibold">{lang === "fi" ? "noin 32 %" : "about 32%"}</span>
                </div>
                <p className="mt-1 text-[12px] text-[var(--tz-ink-3)]">{lang === "fi" ? "Matalampi osuus ↔ korkeampi osuus" : "Lower curative share ↔ higher"}</p>
                <span className="mt-2 inline-flex items-center gap-2 text-[13px]">
                  <span className="inline-block h-3.5 w-6 border border-line" style={{ background: "repeating-linear-gradient(45deg,#d9d4cc,#d9d4cc 3px,#8a8580 3px,#8a8580 5px)" }} />
                  {lang === "fi" ? "Ei julkista tietoa" : "No public data"}
                </span>
              </div>
              <div className="pointer-events-auto shrink-0 rounded-[16px] border border-line bg-card p-2 shadow-[var(--tz-sh-1)]">
                <p className="mb-1 text-[13px] font-semibold text-ink">{lang === "fi" ? "Helsingin seutu" : "Helsinki region"}</p>
                <svg viewBox={`0 0 ${inset.w} ${inset.h}`} width={264} height={264} role="img" aria-label={lang === "fi" ? "Helsingin seutu" : "Helsinki region"}>
                  <defs>
                    <pattern id="no-data-hatch-inset-hero" width="8" height="8" patternUnits="userSpaceOnUse" patternTransform="rotate(45)">
                      <rect width="8" height="8" fill="#d9d4cc" />
                      <line x1="0" y1="0" x2="0" y2="8" stroke="#8a8580" strokeWidth="2" />
                    </pattern>
                  </defs>
                  {inset.paths.map(({ f, d, c }) => {
                    const id = f.properties.id;
                    const isSel = selectedId === id;
                    const isHov = hover === id;
                    const fill = countyValue(id).missing ? "url(#no-data-hatch-inset-hero)" : paint(id);
                    const p = inset.project(c.lon, c.lat);
                    const label = INSET_LABELS[id];
                    return (
                      <g key={`hero-${id}`}>
                        <path
                          d={d}
                          fill={fill}
                          stroke={isSel ? "#D9822B" : isHov ? "#16233F" : "#fff"}
                          strokeWidth={isSel ? 2.5 : 1}
                          className="cursor-pointer"
                          onMouseEnter={() => setHoverId(id)}
                          onMouseLeave={() => setHoverId(null)}
                          onMouseDown={(e) => e.preventDefault()}
                          onClick={() => onClick(id)}
                        />
                        {label ? (
                          <text x={p.x} y={p.y} textAnchor="middle" fontSize="11" fontWeight="700" fill="#16233F" className="pointer-events-none" style={{ paintOrder: "stroke", stroke: "#fff", strokeWidth: 3 }}>
                            {lang === "fi" ? label.fi : label.en}
                          </text>
                        ) : null}
                      </g>
                    );
                  })}
                </svg>
              </div>
            </div>
            ) : (
            <div className="flex flex-wrap items-center justify-between gap-3">
              <span>
                {higherIsBetter ? "Lower (worse)" : "Higher (worse)"}
                <span className="mx-2 inline-flex overflow-hidden rounded">
                  {COLORS.map((c) => (
                    <span key={c} className="inline-block h-2 w-6" style={{ background: c }} />
                  ))}
                </span>
                {higherIsBetter ? "Higher (better)" : "Lower (better)"}
                <span className="ml-2 tabular-nums">
                  {formatValue(min, unit, decimals)} – {formatValue(max, unit, decimals)}
                </span>
              </span>
              <span className="inline-flex items-center gap-1">
                <span className="inline-block h-3 w-5 border border-line" style={{ background: "repeating-linear-gradient(45deg,#d9d4cc,#d9d4cc 3px,#8a8580 3px,#8a8580 5px)" }} />
                No public data
                <ExampleMark show={isExampleApp()} />
              </span>
            </div>
            )}
            {heroMode ? null : (
            <p className="mt-1 text-[11px] text-muted">
              Boundaries: Statistics Finland, wellbeing services counties 2026 (1:4 500 000), CC BY 4.0.
            </p>
            )}
          </div>
        </div>
      </div>
      {heroMode ? null : (
      <div>
        <p className="mb-2 text-xs font-semibold uppercase tracking-[0.16em] text-muted">Ranked · {isYta ? "by YTA value" : "by county"}</p>
        <ul className="max-h-[640px] overflow-auto rounded-2xl border border-line bg-card">
          {ranked.map(({ r, v }, i) => {
            const sel = r.id === selectedId;
            const hov = r.id === hover;
            return (
              <li key={r.id}>
                <button
                  type="button"
                  onMouseDown={(e) => e.preventDefault()}
                  onClick={() => onClick(r.id)}
                  onMouseEnter={() => setHoverId(r.id)}
                  onMouseLeave={() => setHoverId(null)}
                  className={`flex w-full items-center gap-2 px-3 py-1.5 text-left text-sm ${sel ? "bg-teal-soft" : hov ? "bg-paper" : ""}`}
                >
                  <span className="w-5 text-[11px] text-muted">{v.missing ? "—" : i + 1}</span>
                  <span
                    className="h-2.5 w-2.5 shrink-0 rounded-full border border-line"
                    style={{
                      background: v.missing
                        ? "repeating-linear-gradient(45deg,#d9d4cc,#d9d4cc 2px,#8a8580 2px,#8a8580 3px)"
                        : colorFor(v.value, min, max, higherIsBetter),
                    }}
                  />
                  <span className="flex-1">
                    {r.name}
                    {isYta && ytaOf(r.id) ? (
                      <span className="ml-1 text-[10px] uppercase text-muted">
                        {dataset.hero.yta_waits.find((y) => y.id === ytaOf(r.id))?.name_fi}
                      </span>
                    ) : null}
                  </span>
                  <span className={`text-right text-xs font-semibold tabular-nums ${v.missing ? "text-muted" : ""}`}>
                    {v.missing ? "No public data" : formatValue(v.value, unit, decimals)}
                  </span>
                </button>
              </li>
            );
          })}
        </ul>
        {active ? (
          <ActiveCaption regionId={active.id} layer={layer} modality={modality} isYta={isYta} />
        ) : (
          <p className="mt-2 text-xs text-muted">Click a county. Hatched areas have no public figure for this indicator.</p>
        )}
      </div>
      )}
    </div>
  );
}

function ActiveCaption({
  regionId,
  layer,
  modality,
  isYta,
}: {
  regionId: string;
  layer: MapLayer;
  modality: "surgery" | "radiotherapy" | "drug";
  isYta: boolean;
}) {
  const r = dataset.regions.regions.find((x) => x.id === regionId);
  if (!r) return null;
  const yid = ytaOf(regionId);
  const yta = dataset.hero.yta_waits.find((y) => y.id === yid);
  const w = ytaWait(yid, modality);
  if (isYta) {
    return (
      <div className="mt-2 text-xs leading-relaxed text-muted">
        <p>
          <strong className="text-ink">{r.name}</strong> has no county-level diagnosis-to-treatment time.
          {w && yta ? (
            <>
              {" "}
              It sits in {yta.name} ({yta.name_fi}), where the published median is {w.median} days (IQR {w.q1}–{w.q3}). Clock starts at Cancer Registry diagnosis, not at referral.
            </>
          ) : (
            <> No public collaborative-area figure either.</>
          )}
        </p>
        {w && yta ? <TargetCaveat compact /> : null}
        {modality === "surgery" && surgeryHeadlineCaveat() ? (
          <p className="mt-1 text-[11px] leading-snug text-ink">{surgeryHeadlineCaveat()}</p>
        ) : null}
      </div>
    );
  }
  const ind = r.indicators.find((i) =>
    layer === "curative" ? i.id === "lung_curative_share" : layer === "screening" ? i.id === "colorectal_screening_share" : i.id === "referral_within_3d_share",
  );
  if (!ind || ind.missing || ind.value == null) {
    return (
      <p className="mt-2 text-xs leading-relaxed text-muted">
        <strong className="text-ink">{r.name}</strong>: No public data. {ind?.missing_reason ?? ind?.note ?? ""}
      </p>
    );
  }
  const men = ind.men;
  const women = ind.women;
  if (layer === "curative" && men && women) {
    return (
      <p className="mt-2 text-xs leading-relaxed text-muted">
        <strong className="text-ink">{r.name}</strong>: age-adjusted curative share (chart estimate, not stage-adjusted, not survival) — men about {formatValue(men.value, "%", 1)}
        {men.ci95 ? ` (95% CI ${formatCi(men.ci95[0], men.ci95[1])})` : ""}
        {" / "}women about {formatValue(women.value, "%", 1)}
        {women.ci95 ? ` (95% CI ${formatCi(women.ci95[0], women.ci95[1])})` : ""}. The map is coloured by the men’s figure.
      </p>
    );
  }
  const ci = ind.ci95_low != null ? ` (95% CI ${formatCi(ind.ci95_low, ind.ci95_high)})` : "";
  return (
    <p className="mt-2 text-xs leading-relaxed text-muted">
      <strong className="text-ink">{r.name}</strong>: {formatValue(ind.value, ind.unit === "Percent" ? "%" : ind.unit || "%", 1)}
      {ci}. {ind.note ?? ""} {ind.exclude_from_ranking ? "Excluded from ranking." : ""}
    </p>
  );
}

function shortName(id: string): string {
  const r = dataset.regions.regions.find((x) => x.id === id);
  if (!r) return id;
  if (r.id === "90") return "HKI";
  if (r.id === "04") return "V-K";
  if (r.id === "91") return "Åland";
  return r.name_fi ?? r.name;
}

function surgeryHeadlineCaveat(): string | undefined {
  return dataset.hero.headlines?.find((h) => h.id === "lung_dx_to_surgery_days")?.caveat;
}


export function HelsinkiInset({
  selectedId,
  onSelect,
  lang = "en",
  metric = "crude",
  hover,
  onHover,
  scaleMin,
  scaleMax,
}: {
  selectedId: string | null;
  onSelect: (id: string | null) => void;
  lang?: "en" | "fi";
  metric?: MeasureMode;
  hover?: string | null;
  onHover?: (id: string | null) => void;
  scaleMin?: number;
  scaleMax?: number;
}) {
  const features = dataset.counties.features.filter((f) => UUSIMAA_IDS.has(f.properties.id));
  const inset = useMemo(() => {
    const bbox = featuresBBox(features);
    const w = 140;
    const h = 92;
    const project = makeProjector(bbox, w, h, 8);
    return { w, h, project, paths: features.map((f) => ({ f, d: featurePath(f, project) })) };
  }, [features]);

  const vals = features
    .map((f) => {
      if (metric === "crude") return countyProfile(f.properties.id)?.curative_crude_pct ?? null;
      return agestdFor(f.properties.id, "men")?.value_pct ?? null;
    })
    .filter((v): v is number => v != null);
  const min = scaleMin ?? (vals.length ? Math.min(...vals) : 0);
  const max = scaleMax ?? (vals.length ? Math.max(...vals) : 1);

  function fillFor(id: string): string {
    const v = metric === "crude" ? countyProfile(id)?.curative_crude_pct ?? null : agestdFor(id, "men")?.value_pct ?? null;
    if (v == null) return "url(#no-data-hatch-inset-dash)";
    return rampColor(v, min, max);
  }

  return (
    <div className="inset">
      <div className="t">{lang === "fi" ? "Helsingin seutu" : "Helsinki region"}</div>
      <svg className="inset-map" viewBox={`0 0 ${inset.w} ${inset.h}`} preserveAspectRatio="xMidYMid meet" width={110} height={72} role="img" aria-label={lang === "fi" ? "Helsingin seutu" : "Helsinki region"}>
        <defs>
          <pattern id="no-data-hatch-inset-dash" width="6" height="6" patternUnits="userSpaceOnUse" patternTransform="rotate(45)">
            <rect width="6" height="6" fill="#D9D4C9" />
            <line x1="0" y1="0" x2="0" y2="6" stroke="#B9B2A4" strokeWidth="1.5" />
          </pattern>
        </defs>
        {inset.paths.map(({ f, d }) => {
          const id = f.properties.id;
          const isSel = selectedId === id;
          const isHov = hover === id;
          return (
            <path
              key={id}
              d={d}
              fill={fillFor(id)}
              stroke={isSel ? "#D9822B" : isHov ? "#16233F" : "#fff"}
              strokeWidth={isSel ? 2 : 0.9}
              strokeLinejoin="round"
              className="cursor-pointer"
              onMouseEnter={() => onHover?.(id)}
              onMouseLeave={() => onHover?.(null)}
              onMouseDown={(e) => e.preventDefault()}
              onClick={() => onSelect(id)}
            >
              <title>{lang === "fi" ? (INSET_LABELS[id]?.fi ?? id) : (INSET_LABELS[id]?.en ?? id)}</title>
            </path>
          );
        })}
      </svg>
    </div>
  );
}
