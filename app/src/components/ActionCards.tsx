import { recById } from "../lib/data";
import { FactChip } from "./FactChip";

export function ActionCards({ lang, onOpenBrief }: { lang: "en" | "fi"; onOpenBrief: () => void }) {
  const fi = lang === "fi";
  const t3 = recById("T3");
  const t1 = recById("T1");
  const t2 = recById("T2");
  const cost = t3?.cost_range;
  const owners = t3?.owner_role && typeof t3.owner_role === "object" ? (t3.owner_role as Record<string, unknown>) : {};
  const byCounty = (owners.by_county ?? {}) as Record<string, Record<string, string>>;
  const lap = byCounty.Lapland ?? {};
  const stop = t3?.stop_go as
    | { go_if_all?: string[]; stop_or_redesign_if_any?: string[]; decision_owner?: string; note?: string }
    | undefined;

  return (
    <div className="grid gap-3 lg:grid-cols-[minmax(0,1.4fr)_minmax(0,1fr)]">
      <article className="tz-card">
        <div className="flex flex-wrap items-center gap-2">
          <span className="rounded-full bg-navy px-2.5 py-0.5 text-[11.5px] font-bold uppercase tracking-wide text-white">T3 · lead</span>
          <span className="tz-badge tz-badge--estimate">{fi ? "Tavoite 3" : "Goal 3"}</span>
        </div>
        <h2 className="mt-2 text-[22px] font-semibold text-navy">{fi ? "90 päivän päivän-28 pilotti" : "90-day day-28 pilot"}</h2>
        <p className="mt-1 text-[13px] text-[var(--tz-ink-2)]">{fi ? "Tasan-kello, hälytys ja nimetty hoitaja. Lappi." : "Tasan clock, alert, and a named nurse navigator. Lapland."}</p>
        <dl className="mt-3 grid gap-2 text-[13px] sm:grid-cols-2">
          <Item k={fi ? "Allekirjoittaja" : "Signer"} v={shortName(lap.signer) || "Johtajaylilääkäri"} />
          <Item k={fi ? "Hoitajaomistaja" : "Nurse owner"} v={shortName(lap.owner_of_delayed_patients) || "Named nurse navigator, 1 FTE"} />
          <Item
            k={fi ? "Kustannus" : "Cost"}
            v={
              cost && typeof cost.low === "number"
                ? `€${cost.low.toLocaleString("en-GB")}–${cost.high!.toLocaleString("en-GB")} per 90 days, staff cost only, estimate`
                : "€20,339–23,988 per 90 days, staff cost only, estimate"
            }
          />
          <Item
            k={fi ? "Ensimmäiset 30 päivää" : "First 30 days"}
            v={fi ? "Aikapisteet 12 kk, täydellisyys, perustaso, nimetty hoitaja." : "Extract 12-month time points, completeness check, publish baseline, name navigator."}
          />
        </dl>
        <div className="mt-3 rounded-[10px] bg-[var(--tz-card-alt)] p-3 text-[13px] leading-snug text-ink">
          <p className="text-[11.5px] font-bold uppercase tracking-wide text-[var(--tz-ink-3)]">{fi ? "Päivän 90 stop/go" : "Day-90 stop/go"}</p>
          <p className="mt-1">
            {fi
              ? "Jatko jos ≥85 % poluista täydellisiä, perustaso hallitukselle, ≥90 % hälytyksistä 2 arkipäivässä ja ≥90 % uusista potilaista tavoitettu 3 arkipäivässä. Alle 70 %: korjaa kirjaaminen ensin."
              : "Go if ≥85% of pathways are complete, the baseline is shown to the board, ≥90% of alerts are actioned in 2 working days, and ≥90% of new cases are contacted in 3 working days. Below 70% completeness: fix recording first."}
          </p>
          {stop?.decision_owner ? <p className="mt-1 text-[12px] text-[var(--tz-ink-3)]">{stop.decision_owner}</p> : null}
        </div>
        <div className="mt-3 flex flex-wrap items-center gap-2">
          <button type="button" onClick={onOpenBrief} className="rounded-[10px] bg-navy px-4 py-2 text-[13px] font-semibold text-white hover:bg-[var(--tz-navy-700)]">
            {fi ? "Avaa pilottimuistio" : "Open pilot brief"}
          </button>
          <FactChip id="nodata_regional_target_compliance" lang={lang} label={fi ? "Tavoiteajat" : "Target times"} />
        </div>
      </article>
      <div className="grid gap-3">
        <Triggered id="T1" title={fi ? "Keuhkopolun pikakaista" : "Lung fast-track"} where="Kymenlaakso" rec={t1} lang={lang} />
        <Triggered id="T2" title={fi ? "OYS-videokokous + sädehoito" : "OYS video MDT + curative RT"} where={fi ? "Lappi" : "Lapland"} rec={t2} lang={lang} />
      </div>
    </div>
  );
}

function Item({ k, v }: { k: string; v: string }) {
  return (
    <div>
      <dt className="text-[11.5px] font-bold uppercase tracking-wide text-[var(--tz-ink-3)]">{k}</dt>
      <dd className="mt-0.5 font-medium text-ink">{v}</dd>
    </div>
  );
}

function Triggered({
  id, title, where, rec, lang,
}: {
  id: string;
  title: string;
  where: string;
  rec: ReturnType<typeof recById>;
  lang: "en" | "fi";
}) {
  const fi = lang === "fi";
  const cost = rec?.cost_range;
  const costLabel =
    cost && typeof cost.low === "number"
      ? `€${cost.low.toLocaleString("en-GB")}–${cost.high!.toLocaleString("en-GB")}`
      : "";
  const cond = typeof cost?.period === "string" && /CONDITIONAL/i.test(cost.period);
  return (
    <article className="tz-card !p-4">
      <div className="flex flex-wrap items-center gap-2">
        <span className="rounded-full border border-line px-2 py-0.5 text-[11.5px] font-bold uppercase tracking-wide text-ink">{id}</span>
        <span className="text-[11.5px] font-semibold uppercase tracking-wide text-[var(--tz-teal-700)]">{fi ? "T3:n käynnistämä" : "Triggered action"}</span>
      </div>
      <h3 className="mt-2 text-[17px] font-semibold text-navy">{title}</h3>
      <p className="mt-1 text-[13px] text-[var(--tz-ink-2)]">{where}{costLabel ? ` · ${costLabel}` : ""}{cond ? (fi ? " · ehdollinen" : " · conditional") : ""}</p>
    </article>
  );
}

function shortName(raw?: string): string {
  if (!raw) return "";
  const m = raw.match(/:\s*([^(/]+?)(?:\s*\(|$)/);
  return (m ? m[1] : raw).replace(/\s+/g, " ").trim();
}
