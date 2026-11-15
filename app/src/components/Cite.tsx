import { dataset, sourceById, tasanClockNote } from "../lib/data";

export function Cite({
  ids,
  onOpen,
}: {
  ids?: (string | undefined | null)[];
  onOpen: (id: string) => void;
}) {
  const clean = [...new Set((ids ?? []).filter((x): x is string => Boolean(x)))];
  if (!clean.length) return null;
  return (
    <span className="ml-0.5 inline-flex flex-wrap items-baseline gap-0.5 align-super">
      {clean.map((id) => {
        const s = sourceById(id);
        return (
          <button
            key={id}
            type="button"
            title={s ? `${s.title} — ${s.publisher}` : id}
            onClick={(e) => {
              e.stopPropagation();
              onOpen(id);
            }}
            className="rounded bg-gold-soft px-1 py-px font-sans text-[10px] font-semibold tracking-wide text-gold no-underline hover:bg-gold hover:text-white"
          >
            {shortLabel(id)}
          </button>
        );
      })}
    </span>
  );
}

function shortLabel(id: string): string {
  const labels: Record<string, string> = {
    "src-thl-2016": "THL 21/2016",
    "src-thl-2017": "THL 2017",
    "src-strategy-2026": "Cancer strategy 2026",
    "src-roadmap-2026": "Strategy roadmap",
    "src-lung-2024-yta": "Lung report 2024, Table 4.1",
    "src-lung-2026-t11": "Lung report 2026, Table 11",
    "src-lung-2026-t4": "Lung report 2026, Table 4",
    "src-lung-2026-kuva16": "Lung report 2026, Figure 16",
    "src-sotkanet-6103": "Sotkanet 6103",
    "src-sotkanet-13": "Sotkanet 13",
    "src-geo-statfin-2026": "Statistics Finland",
  };
  if (labels[id]) return labels[id];
  const s = sourceById(id);
  if (s?.title) {
    const t = s.title.replace(/https?:\/\/\S+/g, "").trim();
    return t.length > 42 ? t.slice(0, 40) + "…" : t;
  }
  return id.replace(/^src-(rec-)?/, "");
}

export function ExampleMark({ show }: { show: boolean }) {
  if (!show) return null;
  return (
    <span
      className="ml-1 align-middle text-[10px] font-semibold uppercase tracking-wider text-gold"
      title="This figure is labelled example data, not an official statistic."
    >
      example
    </span>
  );
}

export function Goal3Badge({ show, title }: { show: boolean; title?: string }) {
  if (!show) return null;
  return (
    <span
      title={title ?? "Maps to Goal 3 of the National Cancer Strategy 2026–2035: equal and effective cancer care."}
      className="inline-flex items-center rounded-full border border-teal/30 bg-teal-soft px-2 py-0.5 text-[10px] font-semibold uppercase tracking-wider text-teal-deep"
    >
      Goal 3
    </span>
  );
}

/** Always show the exact Tasan clock sentence wherever 6 weeks / 42 d / day-28 is mentioned. */
export function TargetCaveat({ compact }: { compact?: boolean }) {
  const text = tasanClockNote();
  const longer = dataset.recs.target_times_caveat;
  return (
    <div className={compact ? "mt-1 text-[11px] leading-snug text-gold" : "mt-2 rounded-lg bg-gold-soft px-3 py-2 text-xs leading-relaxed text-ink"}>
      <p>{text}</p>
      {!compact && longer && longer !== text ? <p className="mt-1 text-[11px] text-muted">{longer}</p> : null}
    </div>
  );
}

export function KpiLines({
  kpis,
  fallback,
}: {
  kpis?: { name?: string; baseline?: string; target?: string }[] | null;
  fallback?: { name?: string; baseline?: string; target?: string } | null;
}) {
  const rows = (kpis && kpis.length ? kpis : fallback ? [fallback] : []).filter((k) => k?.name);
  if (!rows.length) return null;
  return (
    <ul className="mt-2 space-y-1 text-xs text-muted">
      {rows.map((k, i) => (
        <li key={`${k.name}-${i}`}>
          <span className="text-ink">{k.name}</span>
          {k.baseline ? <> · baseline {k.baseline}</> : null}
          {k.target ? (
            <>
              {" "}
              ·{" "}
              {/proposed peer benchmark/i.test(k.target) ? (
                <span className="text-ink">{k.target}</span>
              ) : (
                <>
                  <span className="font-semibold text-ink">proposed peer benchmark</span>: {k.target}
                </>
              )}
            </>
          ) : null}
        </li>
      ))}
    </ul>
  );
}
