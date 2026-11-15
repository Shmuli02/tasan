import brief from "../content/briefs/pilot_brief_lapland.json";
import { displayRole } from "../lib/roles";
import type { PilotBriefDraft } from "../lib/briefDraft";

type Owner = { role?: string; name?: string; source?: string | null; verified?: string };
type Signer = { role?: string; name?: string; source?: string; verified?: string };
type Brief = typeof brief & { owners: Owner[]; signer: Signer };

export function PilotBriefBody({
  lang,
  draft,
  showToolbar = false,
}: {
  lang: "en" | "fi";
  draft?: PilotBriefDraft | null;
  showToolbar?: boolean;
}) {
  const fi = lang === "fi";
  const d = (draft ?? brief) as Brief;
  const isStock = !draft;
  const owners = (d.owners ?? []).map((o) => displayRole("role" in o ? o.role : "")).filter(Boolean);
  const signer = displayRole(d.signer?.role);
  return (
    <div className="pilot-brief">
      <div className="mb-3 flex flex-wrap items-start justify-between gap-2">
        <span className="tz-badge tz-badge--alert">{d.status_label}</span>
      </div>
      <h2 className="display text-[22px] font-bold text-navy">{d.title}</h2>
      <p className="mt-1 text-[13px] text-[var(--tz-ink-3)]">{d.county} · {d.date_prepared}</p>
      {showToolbar ? (
        <div className="pilot-toolbar">
          <button type="button" onClick={() => window.print()}>{fi ? "Tulosta" : "Print"}</button>
          {isStock ? (
            <a href="./briefs/pilot_brief_lapland.pdf" target="_blank" rel="noreferrer">
              {fi ? "Lataa PDF" : "Download PDF"}
            </a>
          ) : null}
        </div>
      ) : null}
      <Section label={fi ? "Ongelma" : "Problem"} body={`${d.problem.line} ${d.problem.metric ?? ""}`.trim()} foot={[d.problem.source, d.problem.caveat].filter(Boolean).join(". ")} />
      {d.problem.people_estimate ? <p className="mt-2 text-[13px] leading-snug text-ink">{d.problem.people_estimate}</p> : null}
      <Section label={fi ? "Toimenpide" : "Action"} body={d.action.summary} />
      <ul className="mt-1 list-disc space-y-1 pl-5 text-[13px] text-ink">
        {(d.action.components ?? []).map((c) => (
          <li key={c}>{c}</li>
        ))}
      </ul>
      <Section
        label={fi ? "Omistajat" : "Owners"}
        body={owners.join(" · ")}
        foot={signer ? `${signer}${d.signer.verified ? `. ${d.signer.verified}` : ""}` : undefined}
      />
      <Section
        label={fi ? "Kustannus" : "Cost"}
        body={d.cost_range ? `€${Number(d.cost_range.low_eur ?? 0).toLocaleString("en-GB")}–${Number(d.cost_range.high_eur ?? 0).toLocaleString("en-GB")} / ${d.cost_range.period ?? ""}. ${d.cost_range.basis ?? ""}` : "—"}
        foot={d.cost_range?.excludes}
      />
      <Section label="KPIs" body={(d.kpis ?? []).map((k) => `${k.name}: ${k.target}`).join(" · ") || "—"} foot={d.kpi_caveat} />
      <Section
        label={fi ? "Päivän 90 stop/go" : "Day-90 stop/go"}
        body={`${d.stop_go?.go ?? ""} ${d.stop_go?.stop ?? ""}`.trim() || "—"}
        foot={d.stop_go?.decider}
        wrap
      />
    </div>
  );
}

export function PilotBriefModal({ lang, onClose, draft, drafting = false }: { lang: "en" | "fi"; onClose: () => void; draft?: PilotBriefDraft | null; drafting?: boolean }) {
  const fi = lang === "fi";
  const isStock = !draft && !drafting;
  return (
    <div className="fixed inset-0 z-50 flex items-start justify-center overflow-auto bg-[rgba(22,35,63,.45)] p-4" onClick={onClose}>
      <div className="tz-card relative my-8 w-full max-w-3xl shadow-[var(--tz-sh-3)]" onClick={(e) => e.stopPropagation()}>
        <div className="mb-3 flex flex-wrap items-start justify-between gap-2">
          <button type="button" className="ml-auto rounded-[10px] px-3 py-1 text-[13px] font-semibold text-ink hover:bg-[var(--tz-sunk)]" onClick={onClose}>
            {fi ? "Sulje" : "Close"}
          </button>
        </div>
        {drafting ? (
          <div className="brief-drafting" role="status" aria-live="polite">
            <p className="brief-drafting-label">{fi ? "Luonnosta kirjoitetaan…" : "Drafting brief…"}</p>
            <div className="brief-skel" />
            <div className="brief-skel short" />
            <div className="brief-skel" />
            <div className="brief-skel mid" />
            <div className="brief-skel short" />
          </div>
        ) : (
          <PilotBriefBody lang={lang} draft={draft} />
        )}
        {isStock ? (
          <div className="mt-4 flex flex-wrap gap-2">
            <button type="button" className="rounded-[10px] bg-navy px-4 py-2 text-[13px] font-semibold text-white hover:bg-[var(--tz-navy-700)]" onClick={() => window.print()}>
              {fi ? "Tulosta" : "Print"}
            </button>
            <a className="rounded-[10px] bg-navy px-4 py-2 text-[13px] font-semibold text-white hover:bg-[var(--tz-navy-700)]" href="./briefs/pilot_brief_lapland.pdf" target="_blank" rel="noreferrer">
              {fi ? "Lataa PDF" : "Download PDF"}
            </a>
          </div>
        ) : null}
      </div>
    </div>
  );
}

function Section({ label, body, foot, wrap }: { label: string; body: string; foot?: string; wrap?: boolean }) {
  return (
    <div className="mt-3">
      <p className="text-[11.5px] font-bold uppercase tracking-wide text-[var(--tz-ink-3)]">{label}</p>
      <p className={`mt-0.5 text-[13px] leading-snug text-ink${wrap ? " stopgo" : ""}`}>{body}</p>
      {foot ? <p className="mt-0.5 text-[12px] text-[var(--tz-ink-3)]">{foot}</p> : null}
    </div>
  );
}
