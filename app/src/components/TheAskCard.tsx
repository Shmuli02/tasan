import { useState } from "react";
import { recById } from "../lib/data";
import { shortName as countyShort } from "../lib/chartData";
import { displayRole, hasPreGeneratedBrief, ownerRole, signerRole } from "../lib/roles";
import { FactChip } from "./FactChip";

const COUNTY_KEYS: Record<string, string> = {
  "21": "Lapland",
  "10": "Kymenlaakso",
};

export function TheAskCard({
  lang,
  countyId,
  onOpenBrief,
  compact = false,
}: {
  lang: "en" | "fi";
  countyId: string | null;
  onOpenBrief: () => void;
  compact?: boolean;
}) {
  const fi = lang === "fi";
  const t3 = recById("T3");
  const cost = t3?.cost_range;
  const owners = t3?.owner_role && typeof t3.owner_role === "object" ? (t3.owner_role as Record<string, unknown>) : {};
  const byCounty = (owners.by_county ?? {}) as Record<string, Record<string, string>>;
  const key = countyId ? COUNTY_KEYS[countyId] : "Lapland";
  const block = (key && byCounty[key]) || null;
  const countyLabel = countyId ? countyShort(countyId, lang) : fi ? "Lappi" : "Lapland";
  const signer = signerRole(lang, countyLabel, block?.signer);
  const owner = ownerRole(lang, countyLabel, block?.owner_of_delayed_patients);
  const stop = t3?.stop_go as { go_if_all?: string[]; stop_or_redesign_if_any?: string[]; note?: string } | undefined;
  const hasDraft = hasPreGeneratedBrief(countyId);
  const [missing, setMissing] = useState(false);
  const costLabel =
    cost && typeof cost.low === "number"
      ? `€${cost.low.toLocaleString("en-GB")}–${Number(cost.high).toLocaleString("en-GB")} per 90 days, staff cost only, estimate`
      : "€20,339–23,988 per 90 days, staff cost only, estimate";

  return (
    <article className={`card ask-card${compact ? " compact" : ""}`}>
      <div className="card-head">
        <div>
          <h2>{fi ? "Askel" : "The ask"}</h2>
          <div className="sub">
            {fi ? "90 päivän päivän-28 pilotti" : "90-day day-28 pilot"}
            {" · "}
            {countyLabel}
          </div>
        </div>
        <span className="badge b-comp">T3</span>
      </div>
      <div className="ask-grid">
        <div>
          <div className="ask-k">{fi ? "Allekirjoittaja" : "Signer"}</div>
          <div className="ask-v">{signer}</div>
        </div>
        <div>
          <div className="ask-k">{fi ? "Omistaja" : "Owner"}</div>
          <div className="ask-v">{owner}</div>
        </div>
        <div>
          <div className="ask-k">{fi ? "Kustannus" : "Cost"}</div>
          <div className="ask-v">{costLabel}</div>
        </div>
        <div>
          <div className="ask-k">{fi ? "Päivän 90 stop/go" : "Day-90 stop/go"}</div>
          <div className="ask-v stopgo">
            {fi
              ? "Jatko jos ≥85 % poluista täydellisiä, perustaso hallitukselle, ≥90 % hälytyksistä 2 arkipäivässä. Alle 70 %: korjaa kirjaaminen ensin."
              : "Go if ≥85% of pathways are complete, the baseline is shown to the board, ≥90% of alerts actioned in 2 working days. Below 70% completeness: fix recording first."}
          </div>
        </div>
      </div>
      <div className="ask-foot">
        <button
          type="button"
          className="ask-btn"
          onClick={() => {
            if (hasDraft) onOpenBrief();
            else setMissing(true);
          }}
        >
          {fi ? "Luo pilottimuistio" : "Generate pilot brief"}
        </button>
        <span className="ask-note">
          {hasDraft
            ? fi
              ? "Valmis luonnos, ei allekirjoitettu."
              : "Pre-generated draft, not signed."
            : missing
              ? fi
                ? `Luonnosta alueelle ${countyLabel} ei ole vielä valmiina.`
                : `Draft brief for ${countyLabel} not pre-generated yet`
              : fi
                ? "Luonnos vain Lapille toistaiseksi."
                : "A pre-generated draft exists for Lapland only."}
        </span>
        {stop?.note ? <span className="ask-note">{displayRole(stop.note)}</span> : null}
        <FactChip id="nodata_regional_target_compliance" lang={lang} label={fi ? "Tavoiteajat" : "Target times"} />
      </div>
    </article>
  );
}
