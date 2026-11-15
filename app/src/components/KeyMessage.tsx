import { Cite, Goal3Badge, KpiLines, TargetCaveat } from "./Cite";
import { RecDetails } from "./RecDetails";
import { dataset, featuredRecIds, formatCi, formatValue, leadRecId, recById } from "../lib/data";
import type { HeroHeadline } from "../types";

const CHART_ESTIMATE_LABEL = "chart estimate";
const CHART_ESTIMATE_DETAIL = "estimate read from chart";

export function KeyMessage({ onOpenSource, section = "all" }: { onOpenSource: (id: string) => void; section?: "gap" | "where" | "actions" | "all" }) {
  const km = dataset.keyMessage;
  const recs = dataset.recs.recommendations ?? [];
  const topIds = featuredRecIds();
  const leadId = leadRecId();
  const top = topIds.map((id) => recs.find((r) => r.id === id) ?? recById(id)).filter(Boolean);
  const lead = top.find((r) => r && r.id === leadId) ?? top[0];
  const triggered = top.filter((r) => r && r.id !== lead?.id);
  const headlines: HeroHeadline[] = dataset.hero.headlines ?? [];
  const curative = headlines.find((h) => h.id === "lung_curative_share");
  const surgery = headlines.find((h) => h.id === "lung_dx_to_surgery_days");
  const others = headlines.filter((h) => h.id !== "lung_curative_share");

  const gap = (
    <section id="step-gap" className="space-y-4">
      <div>
        <p className="text-xs font-semibold uppercase tracking-[0.16em] text-teal">The figures in full</p>
        <h2 className="serif mt-1 max-w-5xl text-2xl leading-snug text-ink">Age-adjusted shares, confidence intervals, and the crude comparison</h2>
        <p className="mt-2 max-w-3xl text-sm text-muted">
          The opening line uses the age-adjusted chart estimates. Crude shares (Lapland 18.5% vs Vantaa-Kerava 35.6%)
          are a secondary comparison only and are not the hero number.
        </p>
        <div className="mt-1">
          <Cite ids={km.source_ids} onOpen={onOpenSource} />
        </div>
      </div>
      {curative ? <AgeAdjustedHero headline={curative} /> : null}
    </section>
  );

  const where = (
    <div id="step-where-signals" className="space-y-4">

      <aside className="rounded-2xl border-2 border-gold bg-gold-soft p-5">
        <p className="text-xs font-semibold uppercase tracking-[0.16em] text-gold">Why Tasan exists</p>
        <h3 className="serif mt-1 text-xl text-ink">No county publishes 6-week compliance</h3>
        <p className="mt-2 text-[15px] leading-relaxed text-ink">
          Goal 3 requires that patients start treatment within target timeframes. The official generic limit is six
          weeks (42 days) from <em>referral arrival</em> to first treatment. No public statistic reports that
          rate for any wellbeing services county. Tasan is the tracker that would make it visible — and the
          lead action below is what a county can start next quarter.
        </p>
        <TargetCaveat />
        {dataset.hero.target_reference?.caveat ? (
          <p className="mt-2 text-xs leading-relaxed text-ink">{dataset.hero.target_reference.caveat}</p>
        ) : null}
        <Cite ids={["src-thl-2016", "src-thl-2017", "src-strategy-2026"]} onOpen={onOpenSource} />
      </aside>

      <p className="text-sm text-muted">
        The public signals below are <strong className="text-ink">separate cohorts, years and geographies</strong>.
        Labels and caveats are shown exactly as supplied in the team hero file. They are not stages of one patient journey.
      </p>

      <div className="grid gap-4 lg:grid-cols-2">
        {surgery ? <HeadlineCard headline={surgery} secondary onOpenSource={onOpenSource} /> : null}
        {others
          .filter((h) => h.id !== "lung_dx_to_surgery_days")
          .map((h) => (
            <HeadlineCard key={h.id} headline={h} onOpenSource={onOpenSource} />
          ))}
      </div>

    </div>
  );

  const actions = (
      <section id="step-actions" className="rounded-2xl border border-line bg-card p-5">
        <p className="text-xs font-semibold uppercase tracking-[0.16em] text-teal">3 · What to do · Tasan is the centrepiece</p>
        <h3 className="serif mt-1 text-xl text-ink">Start with the waiting-time clock; let the alert trigger the clinical actions</h3>
        {km.what_to_do ? <p className="mt-2 text-sm leading-relaxed text-ink">{km.what_to_do}</p> : null}
        {lead ? (
          <article className="mt-4 rounded-2xl border-2 border-teal bg-teal-soft/40 p-5">
            <div className="flex flex-wrap items-center gap-2">
              <span className="rounded-full bg-navy px-2 py-0.5 text-[11px] font-semibold text-white">Lead · {lead.id}</span>
              <Goal3Badge show={Boolean(lead.goal3_indicator || lead.goal3_mapping)} />
            </div>
            <h4 className="mt-2 font-serif text-xl text-ink">{lead.title}</h4>
            {lead.pilot_county ? <p className="text-xs text-teal">Pilot: {lead.pilot_county}</p> : null}
            <p className="mt-2 text-sm leading-relaxed text-ink">{lead.what || lead.action}</p>
            <KpiLines kpis={lead.kpis} fallback={lead.kpi} />
            <RecDetails rec={lead} />
          </article>
        ) : null}
        {triggered.length ? (
          <div className="mt-4">
            <p className="text-sm font-semibold text-ink">When the day-28 alert fires, the nurse navigator triggers these actions</p>
            <TargetCaveat compact />
            <ol className="mt-3 grid gap-4 lg:grid-cols-2">
              {triggered.map((r) =>
                r ? (
                  <li key={r.id} className="rounded-xl bg-paper p-4">
                    <div className="flex flex-wrap items-center gap-2">
                      <span className="rounded-full border border-navy px-2 py-0.5 text-[11px] font-semibold text-navy">
                        Alert triggers {r.id}
                      </span>
                      <Goal3Badge show={Boolean(r.goal3_indicator || r.goal3_mapping)} />
                    </div>
                    <h4 className="mt-2 font-semibold text-ink">{r.title}</h4>
                    {r.pilot_county ? <p className="text-xs text-teal">Pilot: {r.pilot_county}</p> : null}
                    <p className="mt-2 text-sm leading-relaxed text-ink">{r.what || r.action}</p>
                    <KpiLines kpis={r.kpis} fallback={r.kpi} />
                    <RecDetails rec={r} />
                  </li>
                ) : null,
              )}
            </ol>
          </div>
        ) : null}
      </section>
  );

  if (section === "gap") return gap;
  if (section === "where") return where;
  if (section === "actions") return actions;
  return (
    <section id="key-message" className="space-y-4">
      {gap}
      {where}
      {actions}
    </section>
  );
}

function AgeAdjustedHero({ headline }: { headline: HeroHeadline }) {
  const measure =
    (typeof headline.measure_label === "string" && headline.measure_label) ||
    "chart estimate, age-adjusted, not stage-adjusted, not survival";
  const columns = sexColumns(headline);
  const crude = headline.crude_secondary as
    | {
        label?: string;
        caveat?: string;
        source_table?: string;
        period?: string;
        regions?: Array<Record<string, unknown>>;
      }
    | undefined;

  return (
    <article className="rounded-2xl border-2 border-navy bg-card p-5 sm:p-6">
      <p className="text-xs font-semibold uppercase tracking-[0.16em] text-teal">Hero number · Goal 3</p>
      <h3 className="serif mt-2 text-2xl leading-snug text-ink sm:text-[1.85rem]">{headline.label}</h3>
      {headline.goal_link ? <p className="mt-1 text-sm text-muted">{headline.goal_link}</p> : null}
      {headline.period ? <p className="text-xs text-muted">{headline.period}</p> : null}

      <div className="mt-3 flex flex-wrap items-end justify-between gap-2">
        <HeroLabels measure={measure} />
      </div>
      <div className="mt-2 grid gap-4 sm:grid-cols-2">
        {columns.map((col) => (
          <div key={col.sex} className="rounded-xl bg-paper p-4">
            <p className="text-xs font-semibold uppercase tracking-[0.16em] text-teal">{col.label}</p>
            <ul className="mt-2 space-y-3">
              {col.rows.map((row) => (
                <li key={row.name}>
                  <p className="text-sm text-ink">{row.name}</p>
                  <p className="font-serif text-3xl leading-tight text-ink">
                    about {row.value.toFixed(1)}%
                  </p>
                  {row.ci ? (
                    <p className="text-sm tabular-nums text-muted">
                      95% CI {formatCi(row.ci[0], row.ci[1])}
                    </p>
                  ) : null}
                </li>
              ))}
            </ul>
          </div>
        ))}
      </div>

      {headline.ci_method ? <p className="mt-3 text-xs leading-relaxed text-muted">{String(headline.ci_method)}</p> : null}
      {headline.caveat ? <p className="mt-3 text-sm leading-relaxed text-ink">{headline.caveat}</p> : null}
      {headline.source_table ? <p className="mt-2 text-[11px] text-muted">{headline.source_table}</p> : null}

      {crude ? (
        <aside className="mt-5 rounded-xl border border-line bg-paper p-4">
          <p className="text-[11px] font-semibold uppercase tracking-wider text-muted">Secondary value · crude (not the hero number)</p>
          {crude.label ? <p className="mt-1 text-sm text-ink">{crude.label}</p> : null}
          {crude.period ? <p className="text-xs text-muted">{crude.period}</p> : null}
          <ul className="mt-2 space-y-1 text-sm">
            {(crude.regions ?? []).map((r, i) => {
              const name = String(r.name ?? r.code ?? i);
              const value = r.value as number | undefined;
              const ci = r.ci95 as number[] | undefined;
              const n = r.n as number | undefined;
              const N = r.N as number | undefined;
              return (
                <li key={name} className="flex flex-wrap items-baseline justify-between gap-2">
                  <span>{name}</span>
                  <span className="tabular-nums">
                    {value != null ? `${Number(value).toFixed(1)}%` : "n/a"}
                    {ci ? <span className="text-muted"> (95% CI {formatCi(ci[0], ci[1])})</span> : null}
                    {n != null && N != null ? <span className="text-muted"> ({n}/{N})</span> : null}
                  </span>
                </li>
              );
            })}
          </ul>
          {crude.caveat ? <p className="mt-2 text-xs leading-relaxed text-muted">{crude.caveat}</p> : null}
          {crude.source_table ? <p className="mt-1 text-[11px] text-muted">{crude.source_table}</p> : null}
        </aside>
      ) : null}
    </article>
  );
}

function HeroLabels({ measure }: { measure: string }) {
  const required = ["about", "chart estimate", "not stage-adjusted", "not survival"];
  const extra = required.filter((p) => !measure.toLowerCase().includes(p));
  return (
    <div className="mt-2 flex flex-wrap items-center gap-1.5">
      <span className="inline-flex items-center rounded-full border border-gold/40 bg-gold-soft px-2 py-0.5 text-[10px] font-semibold uppercase tracking-wider text-gold">
        {measure}
      </span>
      {extra.map((p) => (
        <span
          key={p}
          className="inline-flex items-center rounded-full border border-line bg-paper px-2 py-0.5 text-[10px] font-semibold uppercase tracking-wider text-ink"
        >
          {p}
        </span>
      ))}
    </div>
  );
}

type SexRow = { name: string; value: number; ci?: number[] };
type SexCol = { sex: string; label: string; rows: SexRow[] };

function sexColumns(headline: HeroHeadline): SexCol[] {
  const regions = (headline.regions ?? []) as Array<Record<string, unknown>>;
  const fromRegions = ["men", "women"].map((sex) => {
    const rows: SexRow[] = [];
    for (const r of regions) {
      const s = r[sex];
      if (s && typeof s === "object" && !Array.isArray(s) && typeof (s as { value?: unknown }).value === "number") {
        const obj = s as { value: number; ci95?: number[] };
        rows.push({ name: String(r.name ?? r.code ?? ""), value: obj.value, ci: obj.ci95 });
      }
    }
    return { sex, label: sex === "men" ? "Men" : "Women", rows };
  });
  if (fromRegions.every((c) => c.rows.length)) return fromRegions;

  const check = (headline.age_standardised_check ?? {}) as Record<string, unknown>;
  const places = Object.entries(check).filter(([k, v]) => k !== "note" && v && typeof v === "object") as [
    string,
    Record<string, number[]>,
  ][];
  if (places.length) {
    return ["men", "women"].map((sex) => ({
      sex,
      label: sex === "men" ? "Men" : "Women",
      rows: places.map(([name, sexes]) => {
        const trip = sexes[sex];
        return { name, value: trip?.[0], ci: trip?.slice(1) } as SexRow;
      }).filter((r) => r.value != null),
    }));
  }
  return fromRegions.filter((c) => c.rows.length);
}

function HeadlineCard({
  headline,
  secondary,
  onOpenSource,
}: {
  headline: HeroHeadline;
  secondary?: boolean;
  onOpenSource: (id: string) => void;
}) {
  const chart = isChartEstimate(headline);
  return (
    <article className={`rounded-2xl border bg-card p-5 ${secondary ? "border-gold" : "border-line"}`}>
      <div className="flex flex-wrap items-center gap-2">
        {secondary ? (
          <span className="rounded-full bg-gold-soft px-2 py-0.5 text-[11px] font-semibold uppercase tracking-wider text-gold">
            Secondary signal
          </span>
        ) : (
          <span className="text-xs font-semibold uppercase tracking-[0.14em] text-gold">
            Signal · {humanHeadlineTitle(headline)}
          </span>
        )}
        {chart && headline.id !== "lung_stage_missing" ? <ChartEstimateBadge /> : null}
      </div>
      <h3 className="mt-2 font-semibold leading-snug text-ink">{headline.label}</h3>
      {headline.period ? <p className="mt-1 text-xs text-muted">{headline.period}</p> : null}
      <HeadlineValues headline={headline} />
      {headline.caveat ? <p className="mt-3 text-sm leading-relaxed text-ink">{headline.caveat}</p> : null}
      {headline.source_table ? <p className="mt-2 text-[11px] text-muted">{headline.source_table}</p> : null}
      <Cite ids={sourceIdsFor(headline)} onOpen={onOpenSource} />
    </article>
  );
}

function HeadlineValues({ headline }: { headline: HeroHeadline }) {
  const regions = (headline.regions ?? []) as Array<Record<string, unknown>>;
  if (!regions.length) return null;
  return (
    <ul className="mt-3 space-y-1.5 text-sm">
      {regions.map((r, i) => {
        const name = String(r.name ?? r.code ?? i);
        const unit = headline.unit || "";
        const sexed = sexPair(r);
        if (sexed) {
          return (
            <li key={name} className="space-y-0.5">
              <span>{name}</span>
              <div className="flex flex-wrap gap-3 text-sm font-semibold tabular-nums">
                <span>Men about {formatHeroValue(sexed.men.value, unit)}{ciText(sexed.men.ci)}</span>
                <span>Women about {formatHeroValue(sexed.women.value, unit)}{ciText(sexed.women.ci)}</span>
              </div>
            </li>
          );
        }
        const value = typeof r.value === "number" ? r.value : undefined;
        const ci = (r.ci95 ?? r.ci95_approx) as number[] | undefined;
        const iqr = r.iqr as number[] | undefined;
        const n = r.n as number | undefined;
        const N = r.N as number | undefined;
        return (
          <li key={name} className="flex flex-wrap items-baseline justify-between gap-2">
            <span>{name}</span>
            <span className="font-semibold tabular-nums">
              {formatHeroValue(value, unit)}
              {ci ? <span className="font-normal text-muted"> (95% CI {formatCi(ci[0], ci[1])})</span> : null}
              {iqr ? <span className="font-normal text-muted"> IQR {iqr[0]}–{iqr[1]}</span> : null}
              {n != null && N != null ? <span className="font-normal text-muted"> ({n}/{N})</span> : null}
            </span>
          </li>
        );
      })}
    </ul>
  );
}


function ChartEstimateBadge() {
  return (
    <span
      className="inline-flex items-center rounded-full border border-gold/40 bg-gold-soft px-2 py-0.5 text-[10px] font-semibold uppercase tracking-wider text-gold"
      title={CHART_ESTIMATE_DETAIL}
    >
      {CHART_ESTIMATE_LABEL}
      <span className="ml-1 font-normal normal-case tracking-normal">· {CHART_ESTIMATE_DETAIL}</span>
    </span>
  );
}

function isChartEstimate(h: HeroHeadline): boolean {
  const blob = JSON.stringify(h);
  return /chart[- ]?digit|chart_estimate|estimate read from chart|\+\/- ?1 pp/i.test(blob);
}

function formatHeroValue(value: unknown, unit: string): string {
  if (typeof value !== "number" || Number.isNaN(value)) return "n/a";
  if (unit.startsWith("%")) return formatValue(value, "%", 1);
  if (unit.toLowerCase().includes("day")) return `${value} d`;
  return formatValue(value, unit, 1);
}

function ciText(ci?: number[]) {
  if (!ci || ci.length < 2) return null;
  return <span className="font-normal text-muted"> (95% CI {formatCi(ci[0], ci[1])})</span>;
}

function sexPair(r: Record<string, unknown>): { men: { value: number; ci?: number[] }; women: { value: number; ci?: number[] } } | null {
  const read = (v: unknown) => {
    if (v && typeof v === "object" && !Array.isArray(v) && typeof (v as { value?: unknown }).value === "number") {
      const o = v as { value: number; ci95?: number[] };
      return { value: o.value, ci: o.ci95 };
    }
    return null;
  };
  const men = read(r.men);
  const women = read(r.women);
  return men && women ? { men, women } : null;
}

function humanHeadlineTitle(h: HeroHeadline): string {
  const map: Record<string, string> = {
    lung_curative_share: "Curative treatment",
    lung_dx_to_surgery_days: "Diagnosis to surgery",
    lung_treated_within_2_months: "Treated within 2 months",
    lung_1yr_survival: "1-year survival",
    lung_stage_missing: "Stage at diagnosis missing",
  };
  return map[h.id] || (h.label ? h.label.split(/[.:]/)[0] : "Public signal");
}

function sourceIdsFor(h: HeroHeadline): string[] {

  if (h.id === "lung_curative_share" || h.id === "lung_stage_missing") return ["src-lung-2026-t11", "src-lung-2026-t4"];
  if (h.id === "lung_dx_to_surgery_days" || h.id === "lung_treated_within_2_months" || h.id === "lung_1yr_survival") {
    return ["src-lung-2024-yta"];
  }
  return [];
}
