import { useMemo, useState } from "react";
import { Cite, Goal3Badge, KpiLines, TargetCaveat } from "./Cite";
import { RecDetails } from "./RecDetails";
import { dataset, featuredRecIds, formatCi, formatValue, leadRecId, recById } from "../lib/data";
import { ASSUMPTION_NOTE, SURGERY_MEDIAN_FLOOR_DAYS, applyDaysCut, applyShareLift } from "../lib/simulator";

export function Simulator({
  selectedId,
  onOpenSource,
}: {
  selectedId: string | null;
  stage?: string;
  onOpenSource: (id: string) => void;
}) {
  const recs = dataset.recs.recommendations ?? [];
  const featuredIds = featuredRecIds();
  const leadId = leadRecId();
  const featured = featuredIds.map((id) => recs.find((r) => r.id === id) ?? recById(id)).filter(Boolean);
  const lead = featured.find((r) => r && r.id === leadId) ?? featured[0];
  const triggered = featured.filter((r) => r && r.id !== lead?.id);
  const others = recs.filter((r) => !featuredIds.includes(r.id) && !r.nonpriority);
  const deprioritised = recs.filter((r) => !featuredIds.includes(r.id) && r.nonpriority);

  const [cutSurgery, setCutSurgery] = useState(0);
  const [cutDrug, setCutDrug] = useState(0);
  const [liftCurative, setLiftCurative] = useState(0);
  const [showOthers, setShowOthers] = useState(false);

  const ytas = dataset.hero.yta_waits ?? [];
  const surgeryRows = useMemo(
    () =>
      ytas
        .map((y) => {
          const m = y.modalities.surgery;
          if (!m) return null;
          return { id: y.id, name: y.name_fi, current: m.median, q1: m.q1, q3: m.q3, projected: applyDaysCut(m.median, cutSurgery, SURGERY_MEDIAN_FLOOR_DAYS) };
        })
        .filter(Boolean) as { id: string; name: string; current: number; q1: number | null; q3: number | null; projected: number | null }[],
    [ytas, cutSurgery],
  );
  const drugRows = useMemo(
    () =>
      ytas
        .map((y) => {
          const m = y.modalities.drug;
          if (!m) return null;
          return { id: y.id, name: y.name_fi, current: m.median, projected: applyDaysCut(m.median, cutDrug) };
        })
        .filter(Boolean) as { id: string; name: string; current: number; projected: number | null }[],
    [ytas, cutDrug],
  );

  const county = dataset.regions.regions.find((r) => r.id === selectedId);

  return (
    <section id="simulator" className="rounded-2xl border border-line bg-card p-5">
      <p className="text-xs font-semibold uppercase tracking-[0.16em] text-teal">What-if on published baselines</p>
      <h3 className="serif mt-1 text-xl text-ink">Assume a change — the baselines stay real</h3>
      <p className="mt-1 text-sm text-muted">
        Only published medians and shares are used as starting points. Any day-cut or percentage-point lift is
        <strong className="text-ink"> a user-set assumption</strong>, not an evaluated effect and not a 6-week
        compliance rate. No county publishes that rate.
      </p>
      <TargetCaveat />

      {lead ? (
        <article className="mt-4 rounded-2xl border-2 border-teal bg-teal-soft/40 p-4">
          <div className="flex flex-wrap items-center gap-2">
            <span className="rounded-full bg-navy px-2 py-0.5 text-[11px] font-semibold text-white">Lead · {lead.id}</span>
            <Goal3Badge show={Boolean(lead.goal3_indicator || lead.goal3_mapping)} />
          </div>
          <h4 className="mt-2 font-semibold text-ink">{lead.title}</h4>
          {lead.pilot_county ? <p className="text-xs text-teal">Pilot: {lead.pilot_county}</p> : null}
          <p className="mt-2 text-sm leading-relaxed">{lead.what || lead.action}</p>
          <KpiLines kpis={lead.kpis} fallback={lead.kpi} />
          <RecDetails rec={lead} />
          <Cite ids={lead.evidence_source_ids} onOpen={onOpenSource} />
        </article>
      ) : null}
      {triggered.length ? (
        <div className="mt-3">
          <p className="text-sm font-semibold text-ink">Actions the day-28 alert triggers</p>
          <TargetCaveat compact />
          <div className="mt-2 grid gap-3 lg:grid-cols-2">
            {triggered.map((r) =>
              r ? (
                <article key={r.id} className="rounded-xl bg-paper p-4">
                  <div className="flex flex-wrap items-center gap-2">
                    <span className="rounded-full border border-navy px-2 py-0.5 text-[11px] font-semibold text-navy">
                      Alert triggers {r.id}
                    </span>
                    <Goal3Badge show={Boolean(r.goal3_indicator || r.goal3_mapping)} />
                  </div>
                  <h4 className="mt-2 font-semibold text-ink">{r.title}</h4>
                  {r.pilot_county ? <p className="text-xs text-teal">Pilot: {r.pilot_county}</p> : null}
                  <p className="mt-2 text-sm leading-relaxed">{r.what || r.action}</p>
                  <KpiLines kpis={r.kpis} fallback={r.kpi} />
                  <RecDetails rec={r} />
                  <Cite ids={r.evidence_source_ids} onOpen={onOpenSource} />
                </article>
              ) : null,
            )}
          </div>
        </div>
      ) : null}

      <div className="mt-5 grid gap-4 lg:grid-cols-2">
        <div className="rounded-xl border border-line p-4">
          <p className="text-xs font-semibold uppercase tracking-wider text-gold">Assumption A · Taulukko 4.1 surgery medians</p>
          <p className="mt-1 text-xs text-muted">
            Diagnosis to surgery, 2018 to mid-2022, by home region, surgical patients only (~11%). Assumed cut is
            subtracted from the published median; IQR is left unchanged because no distribution shift was published.
            In the North at least a quarter of these patients have surgery on the diagnosis date (lower quartile 0 days),
            so the low median partly reflects how diagnosis is dated. Projected medians are floored at {SURGERY_MEDIAN_FLOOR_DAYS} day;
            a 0-day median is not shown.
          </p>
          <label className="mt-3 flex items-center justify-between text-sm">
            <span>Assumed days cut from the surgery median</span>
            <span className="font-semibold tabular-nums text-teal">{cutSurgery} d</span>
          </label>
          <input
            type="range"
            min={0}
            max={20}
            step={1}
            value={cutSurgery}
            onChange={(e) => setCutSurgery(Number(e.target.value))}
            className="mt-1 w-full"
            aria-label="Assumed days cut from published surgery median"
          />
          <ul className="mt-3 space-y-1 text-sm">
            {surgeryRows
              .slice()
              .sort((a, b) => a.current - b.current)
              .map((row) => (
                <li key={row.id} className="flex items-baseline justify-between gap-2">
                  <span>{row.name}</span>
                  <span className="tabular-nums">
                    {row.current} d
                    {cutSurgery > 0 ? (
                      <>
                        {" "}
                        → <strong>{row.projected} d</strong>
                      </>
                    ) : (
                      <span className="text-muted"> (IQR {row.q1}–{row.q3})</span>
                    )}
                  </span>
                </li>
              ))}
          </ul>
          <Cite ids={["src-lung-2024-yta"]} onOpen={onOpenSource} />
        </div>

        <div className="rounded-xl border border-line p-4">
          <p className="text-xs font-semibold uppercase tracking-wider text-gold">Assumption A · same table, drug-therapy medians</p>
          <p className="mt-1 text-xs text-muted">
            Same years and geography, different treatment subset. Pohjois-Suomi is slower here than Etelä-Suomi — the
            surgery pattern does not generalise.
          </p>
          <label className="mt-3 flex items-center justify-between text-sm">
            <span>Assumed days cut from the drug-therapy median</span>
            <span className="font-semibold tabular-nums text-teal">{cutDrug} d</span>
          </label>
          <input
            type="range"
            min={0}
            max={20}
            step={1}
            value={cutDrug}
            onChange={(e) => setCutDrug(Number(e.target.value))}
            className="mt-1 w-full"
            aria-label="Assumed days cut from published drug-therapy median"
          />
          <ul className="mt-3 space-y-1 text-sm">
            {drugRows
              .slice()
              .sort((a, b) => a.current - b.current)
              .map((row) => (
                <li key={row.id} className="flex items-baseline justify-between gap-2">
                  <span>{row.name}</span>
                  <span className="tabular-nums">
                    {row.current} d
                    {cutDrug > 0 ? (
                      <>
                        {" "}
                        → <strong>{row.projected} d</strong>
                      </>
                    ) : null}
                  </span>
                </li>
              ))}
          </ul>
          <Cite ids={["src-lung-2024-yta"]} onOpen={onOpenSource} />
        </div>
      </div>

      <div className="mt-4 rounded-xl border border-line p-4">
        <p className="text-xs font-semibold uppercase tracking-wider text-gold">Assumption B · age-adjusted curative share (chart estimate)</p>
        <p className="mt-1 text-xs text-muted">
          Age-adjusted 12-month curative-treatment share, 2019–2023, from Kuva 16 (chart estimate, not stage-adjusted, not survival).
          A different cohort from Signal A. The assumed lift is added in percentage points to the published chart estimate;
          confidence intervals stay with the observed figure. There is no published national age-adjusted figure in the same chart.
        </p>
        <label className="mt-3 flex items-center justify-between text-sm">
          <span>Assumed lift in curative-record share (percentage points)</span>
          <span className="font-semibold tabular-nums text-teal">+{liftCurative} pp</span>
        </label>
        <input
          type="range"
          min={0}
          max={10}
          step={0.5}
          value={liftCurative}
          onChange={(e) => setLiftCurative(Number(e.target.value))}
          className="mt-1 w-full"
          aria-label="Assumed percentage-point lift in curative-record share"
        />
        <AgestdLift county={county ?? null} lift={liftCurative} />
        <Cite ids={["src-lung-2026-kuva16"]} onOpen={onOpenSource} />
      </div>

      {others.length || deprioritised.length ? (
        <details className="mt-4" open={showOthers} onToggle={(e) => setShowOthers((e.target as HTMLDetailsElement).open)}>
          <summary className="cursor-pointer text-sm font-semibold text-muted">Other recommendations (not in the top 3)</summary>
          <ul className="mt-2 space-y-2 text-sm">
            {others.concat(deprioritised).map((r) => (
              <li key={r.id} className="rounded-lg bg-paper px-3 py-2">
                <span className="font-semibold">{r.id}. {r.title}</span>
                {r.optional_goal2 ? <span className="ml-2 text-[11px] uppercase text-muted">optional Goal 2</span> : null}
                {r.nonpriority ? <span className="ml-2 text-[11px] uppercase text-muted">non-priority</span> : null}
                <p className="text-muted">{r.what || r.action}</p>
              </li>
            ))}
          </ul>
        </details>
      ) : null}

      <aside className="mt-4 rounded-xl bg-gold-soft/60 p-3 text-xs leading-relaxed text-ink">
        <p className="font-semibold text-gold">Assumptions and limitations</p>
        <p className="mt-1">{ASSUMPTION_NOTE}</p>
        {cutSurgery === 0 && cutDrug === 0 && liftCurative === 0 ? (
          <p className="mt-1 text-muted">All assumed changes are at 0, so the figures equal the published baselines.</p>
        ) : (
          <p className="mt-1 font-semibold">Assumed changes are on: label them as assumptions if you quote them.</p>
        )}
      </aside>
    </section>
  );
}

function AgestdLift({
  county,
  lift,
}: {
  county: { id: string; name: string; indicators: { id: string; missing?: boolean; men?: { value: number; ci95?: number[] } | null; women?: { value: number; ci95?: number[] } | null }[] } | null;
  lift: number;
}) {
  const heroIds = [
    { id: "21", name: "Lapland" },
    { id: "04", name: "Vantaa-Kerava" },
  ];
  const ids = county ? [county] : heroIds.map((h) => dataset.regions.regions.find((r) => r.id === h.id)).filter(Boolean);
  return (
    <ul className="mt-3 space-y-2 text-sm">
      {ids.map((c) => {
        if (!c) return null;
        const ind = c.indicators.find((i) => i.id === "lung_curative_share" && !i.missing && i.men && i.women);
        if (!ind?.men || !ind.women) {
          return (
            <li key={c.id} className="text-muted">
              {c.name}: No public age-adjusted figure in Kuva 16.
            </li>
          );
        }
        return (
          <li key={c.id}>
            <span className="font-semibold">{c.name}</span>
            <span className="block text-muted">
              Men about {formatValue(ind.men.value, "%", 1)} (95% CI {formatCi(ind.men.ci95?.[0], ind.men.ci95?.[1])})
              {lift > 0 ? <> → assumed {formatValue(applyShareLift(ind.men.value, lift), "%", 1)}</> : null}
            </span>
            <span className="block text-muted">
              Women about {formatValue(ind.women.value, "%", 1)} (95% CI {formatCi(ind.women.ci95?.[0], ind.women.ci95?.[1])})
              {lift > 0 ? <> → assumed {formatValue(applyShareLift(ind.women.value, lift), "%", 1)}</> : null}
            </span>
          </li>
        );
      })}
    </ul>
  );
}
