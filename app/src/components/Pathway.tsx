import type { StageId } from "../types";
import { Cite, ExampleMark, Goal3Badge } from "./Cite";
import { dataset, formatCi, formatValue, goal3Label, indicatorForStage } from "../lib/data";
import { STAGE_ORDER } from "../lib/data";

export function Pathway({
  selectedId,
  stage,
  onStage,
  onOpenSource,
}: {
  selectedId: string | null;
  stage: StageId;
  onStage: (s: StageId) => void;
  onOpenSource: (id: string) => void;
}) {
  const region = dataset.regions.regions.find((r) => r.id === selectedId);
  const title = region ? region.name : "Finland (national)";
  const subtitle = region
    ? `${region.name_official_fi ?? region.name_fi ?? ""} · vs national`
    : dataset.regions.national.name_fi ?? "Koko maa";

  return (
    <section className="rounded-2xl border border-line bg-card p-5">
      <div className="flex flex-wrap items-start justify-between gap-2">
        <div>
          <p className="text-xs font-semibold uppercase tracking-[0.16em] text-teal">Pathway breakdown</p>
          <h3 className="serif mt-1 text-xl text-ink">{title}</h3>
          <p className="text-sm text-muted">{subtitle || "Click a county to compare it with the national figure."}</p>
        </div>
        {region ? (
          <button type="button" className="text-xs font-medium text-teal underline" onClick={() => onStage(stage)}>
            Showing {dataset.regions.stages.find((s) => s.id === stage)?.label}
          </button>
        ) : null}
      </div>
      <ul className="mt-4 space-y-4">
        {STAGE_ORDER.map((s) => {
          const def = dataset.regions.stages.find((x) => x.id === s);
          const rInd = region ? indicatorForStage(region, s) : undefined;
          const nInd = indicatorForStage(dataset.regions.national, s);
          const focus = s === stage;
          const value = region ? rInd : nInd;
          const compare = region ? nInd : undefined;
          return (
            <li key={s}>
              <button type="button" onClick={() => onStage(s)} className={`w-full rounded-xl p-3 text-left ${focus ? "bg-teal-soft/60" : "hover:bg-paper"}`}>
                <div className="flex flex-wrap items-center gap-2">
                  <span className="text-xs font-semibold uppercase tracking-wider text-muted">{def?.label}</span>
                  <Goal3Badge
                    show={Boolean(value?.goal === "3" && value?.goal3_indicator)}
                    title={goal3Label(value?.goal3_indicator) ?? value?.label}
                  />
                  <ExampleMark show={Boolean(value?.is_example)} />
                </div>
                <p className="mt-1 text-sm text-ink">{value?.label}</p>
                {value?.missing || value?.value == null ? (
                  <div className="mt-2 rounded-lg border border-dashed border-line bg-paper px-3 py-2 text-sm text-muted">
                    <span className="font-semibold text-ink">No public data</span>
                    {value?.missing_reason ? <span> — {value.missing_reason}</span> : null}
                    {region?.yta_id && s === "diagnosis" ? (
                      <YtaHint ytaId={region.yta_id} />
                    ) : null}
                  </div>
                ) : value?.men && value?.women ? (
                  <div className="mt-2 rounded-lg bg-paper px-3 py-2 text-sm text-ink">
                    <p>
                      Men about {formatValue(value.men.value, "%", 1)}
                      {value.men.ci95 ? <span className="text-muted"> (95% CI {formatCi(value.men.ci95[0], value.men.ci95[1])})</span> : null}
                    </p>
                    <p>
                      Women about {formatValue(value.women.value, "%", 1)}
                      {value.women.ci95 ? <span className="text-muted"> (95% CI {formatCi(value.women.ci95[0], value.women.ci95[1])})</span> : null}
                    </p>
                    <p className="mt-1 text-[11px] text-muted">
                      {value.measure_label || "chart estimate, age-adjusted, not stage-adjusted, not survival"}
                    </p>
                  </div>
                ) : (
                <Bar
                  a={value?.value ?? null}
                  aLabel={region ? region.name : "National"}
                  b={compare?.value ?? (region ? null : value?.target ?? null)}
                  bLabel={region ? "National" : value?.target != null ? "Target" : ""}
                  target={value?.target ?? null}
                  unit={value?.unit ?? ""}
                  decimals={value?.decimals ?? 0}
                  higher={value?.higher_is_better ?? true}
                />
                )}
                <p className="mt-1 text-[11px] text-muted">
                  {value?.year ? `Year ${value.year}. ` : null}
                  {value?.target != null && s !== "treatment"
                    ? `Target ${formatValue(value.target, value.unit, value.decimals)}.`
                    : null}{" "}
                  {value?.note && s === "diagnosis" && !region ? value.note + " " : null}
                  {value?.target_note}
                  {value?.iqr && value.iqr.length >= 2 ? ` IQR ${value.iqr[0]}–${value.iqr[1]}.` : ""}
                  {value?.ci95_low != null && !(value?.men && value?.women) ? ` 95% CI ${formatCi(value.ci95_low, value.ci95_high)}.` : ""}
                  {value?.numerator != null ? ` n=${value.numerator}/${value.denominator}.` : ""}
                  <Cite ids={[value?.source_id, value?.target_source_id]} onOpen={onOpenSource} />
                </p>
              </button>
            </li>
          );
        })}
      </ul>
    </section>
  );
}

function Bar({
  a,
  aLabel,
  b,
  bLabel,
  target,
  unit,
  decimals,
  higher,
}: {
  a: number | null;
  aLabel: string;
  b: number | null;
  bLabel: string;
  target: number | null;
  unit: string;
  decimals: number;
  higher: boolean;
}) {
  const max = Math.max(100, a ?? 0, b ?? 0, target ?? 0);
  const pct = (v: number | null) => (v == null ? 0 : Math.max(0, Math.min(100, (v / max) * 100)));
  const worse = a != null && b != null && (higher ? a < b : a > b);
  return (
    <div className="mt-2 space-y-1.5">
      <Row color={worse ? "#9a2f2a" : "#0e6a67"} width={pct(a)} label={aLabel} value={formatValue(a, unit, decimals)} />
      {b != null && bLabel ? (
        <Row color="#1a2744" width={pct(b)} label={bLabel} value={formatValue(b, unit, decimals)} muted />
      ) : null}
      {target != null && bLabel !== "Target" ? (
        <div className="relative h-0">
          <div
            className="absolute -top-7 h-8 border-l border-dashed border-gold"
            style={{ left: `${pct(target)}%` }}
            title={`Target ${formatValue(target, unit, decimals)}`}
          />
        </div>
      ) : null}
    </div>
  );
}

function Row({
  color,
  width,
  label,
  value,
  muted,
}: {
  color: string;
  width: number;
  label: string;
  value: string;
  muted?: boolean;
}) {
  return (
    <div className="flex items-center gap-2">
      <span className={`w-20 shrink-0 text-[11px] ${muted ? "text-muted" : "text-ink"}`}>{label}</span>
      <div className="h-3 flex-1 overflow-hidden rounded-full bg-paper">
        <div className="h-full rounded-full" style={{ width: `${width}%`, background: color }} />
      </div>
      <span className="w-14 text-right text-sm font-semibold tabular-nums">{value}</span>
    </div>
  );
}


function YtaHint({ ytaId }: { ytaId: string }) {
  const yta = dataset.hero.yta_waits?.find((y) => y.id === ytaId);
  const w = yta?.modalities?.surgery;
  if (!w || !yta) return null;
  return (
    <p className="mt-1 text-xs text-ink">
      Collaborative area context ({yta.name_fi}): median diagnosis → surgery {w.median} days (IQR {w.q1}–{w.q3}). This is the YTA figure, not a county measurement.
    </p>
  );
}
