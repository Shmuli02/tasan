import type { ReactNode } from "react";
import brief from "../content/briefs/pilot_brief_lapland.json";
import { displayRole } from "../lib/roles";
import type { PilotBriefDraft } from "../lib/briefDraft";

type Owner = { role?: string; name?: string; source?: string | null; verified?: string };
type Signer = { role?: string; name?: string; source?: string; verified?: string };
type Brief = typeof brief & { owners: Owner[]; signer: Signer };

type Cmp = { label: string; values: Record<string, { value: number; ci?: number[] }> };
type Loose = Brief & {
  problem: Brief["problem"] & { comparison?: { focus: string; reference: string; groups: Cmp[] }; people_headline?: { value: string; unit: string; label: string } };
  timeline?: string[];
  kpis?: { name: string; target: string; baseline_method?: string }[];
};

/** "Clock: the 4 THL time points…" → ["Clock", "the 4 THL time points…"] */
function splitLead(s: string): [string, string] {
  const i = s.indexOf(": ");
  return i > 0 && i < 48 ? [s.slice(0, i), s.slice(i + 2)] : ["", s];
}
const eur = (n?: number) => `€${(Number(n ?? 0) / 1000).toLocaleString("en-GB", { maximumFractionDigits: 1 })}k`;

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
  const d = (draft ?? brief) as Loose;
  const isStock = !draft;
  const owners = (d.owners ?? []).map((o) => displayRole("role" in o ? o.role : "")).filter(Boolean);
  const signer = displayRole(d.signer?.role);
  const cmp = d.problem.comparison as { focus: string; reference: string; groups: Cmp[] } | undefined;
  const people = d.problem.people_headline;
  const timeline = Array.isArray(d.timeline) ? (d.timeline as string[]) : [];
  const kpis = d.kpis ?? [];
  const problemNote = [d.problem.metric, d.problem.source, d.problem.caveat].filter(Boolean).join(" ");
  return (
    <div className="pilot-brief pb">
      <span className="tz-badge tz-badge--alert pb-status">{d.status_label}</span>
      <h2 className="pb-title">{d.title}</h2>
      <p className="pb-meta">{d.county} · {d.date_prepared}</p>
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

      <div className="pb-stats">
        {people ? (
          <div className="pb-stat hero">
            <b>{people.value}</b>
            <span>{fi ? "potilasta / vuosi" : people.unit}</span>
            <small>{fi ? "enemmän parantavaa hoitoa koko maan tasolla (havainnollistava)" : "more with curative treatment at the national share (illustrative)"}</small>
          </div>
        ) : null}
        <div className="pb-stat">
          <b>90</b>
          <span>{fi ? "päivää" : "days"}</span>
          <small>{fi ? "kolme 30 päivän vaihetta, päätös päivänä 90" : "three 30-day phases, stop/go on day 90"}</small>
        </div>
        {d.cost_range ? (
          <div className="pb-stat">
            <b>{eur(d.cost_range.low_eur)}–{eur(d.cost_range.high_eur)}</b>
            <span>{fi ? "kustannus" : "cost"} / {d.cost_range.period}</span>
            <small>{fi ? "vain henkilöstökulut" : "staff cost only"}</small>
          </div>
        ) : null}
      </div>

      <PbSection n={1} label={fi ? "Ongelma" : "The problem"}>
        <p className="pb-lead">{d.problem.line}</p>
        {cmp ? (
          <div className="pb-cmp">
            {cmp.groups.map((g) => (
              <div key={g.label} className="pb-cmp-group">
                <div className="pb-cmp-g">{g.label}</div>
                {[cmp.focus, cmp.reference].map((name) => {
                  const v = g.values[name]?.value;
                  if (v == null) return null;
                  return (
                    <div key={name} className={`pb-bar${name === cmp.focus ? " focus" : ""}`}>
                      <span className="nm">{name}</span>
                      <span className="tr"><i style={{ width: `${Math.min(100, (v / 50) * 100)}%` }} /></span>
                      <b>{v.toFixed(1)}%</b>
                    </div>
                  );
                })}
              </div>
            ))}
            <div className="pb-cmp-cap">{fi ? "Ikävakioitu osuus, joka saa parantavaa hoitoa, 2019–2023" : "Age-adjusted share getting curative treatment, 2019–2023"}</div>
          </div>
        ) : null}
        <Note label={fi ? "Lähde ja varaumat" : "Source & caveats"} text={[problemNote, d.problem.people_estimate].filter(Boolean).join(" ")} />
      </PbSection>

      <PbSection n={2} label={fi ? "Toimenpide" : "What we do"}>
        <p className="pb-lead">{d.action.summary}</p>
        <div className="pb-cards">
          {(d.action.components ?? []).map((c) => {
            const [h, t] = splitLead(c);
            return (
              <div key={c} className="pb-card">
                {h ? <b>{h}</b> : null}
                <span>{t}</span>
              </div>
            );
          })}
        </div>
      </PbSection>

      {timeline.length ? (
        <PbSection n={3} label={fi ? "Aikataulu" : "Timeline"}>
          <ol className="pb-steps">
            {timeline.map((t) => {
              const [h, body] = splitLead(t);
              return (
                <li key={t}>
                  <b>{h}</b>
                  <span>{body}</span>
                </li>
              );
            })}
          </ol>
        </PbSection>
      ) : null}

      {kpis.length ? (
        <PbSection n={timeline.length ? 4 : 3} label={fi ? "Mittarit ja tavoitteet" : "KPIs & targets"}>
          <div className="pb-kpis">
            {kpis.map((k) => (
              <div key={k.name} className="pb-kpi">
                <b>{k.target}</b>
                <span>{k.name}</span>
              </div>
            ))}
          </div>
          <Note label={fi ? "Huomio" : "Note"} text={d.kpi_caveat} />
        </PbSection>
      ) : null}

      <PbSection n={timeline.length ? 5 : 4} label={fi ? "Päivän 90 päätös" : "Day-90 decision"}>
        <div className="pb-gostop">
          {d.stop_go?.go ? <div className="go"><b>{fi ? "Jatketaan" : "Go"}</b><span>{d.stop_go.go.replace(/^Go(\s*\(extend\))?\s*/i, "")}</span></div> : null}
          {d.stop_go?.stop ? <div className="stop"><b>{fi ? "Pysäytetään" : "Stop / fix"}</b><span>{d.stop_go.stop}</span></div> : null}
        </div>
        {d.stop_go?.decider ? <p className="pb-small">{fi ? "Päättäjä: " : "Decided by: "}{d.stop_go.decider}</p> : null}
      </PbSection>

      <PbSection n={timeline.length ? 6 : 5} label={fi ? "Omistajat ja kustannus" : "Owners & cost"}>
        <ul className="pb-owners">
          {owners.map((o) => {
            const [h, t] = splitLead(o);
            return (
              <li key={o}>
                {h ? <b>{h}</b> : null}
                <span>{t}</span>
              </li>
            );
          })}
        </ul>
        {signer && d.signer?.verified ? <p className="pb-small">{d.signer.verified}</p> : null}
        {d.cost_range ? (
          <Note
            label={fi ? "Kustannuslaskelma" : "Cost breakdown"}
            text={`€${Number(d.cost_range.low_eur ?? 0).toLocaleString("en-GB")}–${Number(d.cost_range.high_eur ?? 0).toLocaleString("en-GB")} / ${d.cost_range.period ?? ""}. ${d.cost_range.basis ?? ""} ${d.cost_range.excludes ?? ""}`}
          />
        ) : null}
      </PbSection>
    </div>
  );
}

function PbSection({ n, label, children }: { n: number; label: string; children: ReactNode }) {
  return (
    <section className="pb-sec">
      <h3><span>{n}</span>{label}</h3>
      {children}
    </section>
  );
}

function Note({ label, text }: { label: string; text?: string }) {
  if (!text) return null;
  return (
    <details className="pb-note">
      <summary>{label}</summary>
      <p>{text}</p>
    </details>
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
