import type { Lang } from "./Screen1";
import { dataset } from "../lib/data";
import { countyFactSummary, factById } from "../lib/facts";
import { ExampleClock } from "./ExampleClock";

export function CountyPanel({
  lang,
  countyId,
  onBack,
  clockAlert,
}: {
  lang: Lang;
  countyId: string;
  onBack: () => void;
  clockAlert?: boolean;
}) {
  const fi = lang === "fi";
  const region = dataset.regions.regions.find((r) => r.id === countyId);
  const name = region ? (fi && region.name_fi ? region.name_fi : region.name) : countyId;
  const facts = countyFactSummary(countyId);
  const nationalFact = factById("lung_curative_national");
  const national = nationalFact?.value === 27 || nationalFact?.value === 27.0 ? 27.0 : undefined;
  const crude = facts.crude;
  const perYear = facts.perYear;
  const agestd = facts.agestdMen;
  const showBar = crude != null && national != null;
  const below = crude != null && national != null && crude < national;
  const maxPct = Math.max(national ?? 0, crude ?? 0, 40);

  return (
    <div id="county-view" className="flex flex-col">
      <button type="button" onClick={onBack} className="mb-2 self-start text-[13px] font-semibold text-teal hover:text-teal-deep">
        {fi ? "← Kartta" : "← Map"}
      </button>
      <h2 className="serif text-3xl leading-tight text-ink sm:text-4xl">{name}</h2>

      {perYear != null ? (
        <p className="mt-3 text-[17px] leading-snug text-ink">
          {fi
            ? `Noin ${perYear} potilasta enemmän vuodessa voisi saada parantavan hoidon, jos tämä alue yltäisi valtakunnalliseen osuuteen.`
            : `About ${perYear} more patients a year could get curative treatment if this county reached the national rate.`}
        </p>
      ) : below ? (
        <p className="mt-3 text-[17px] leading-snug text-ink">
          {fi ? "Karkea osuus on valtakunnallisen osuuden alapuolella." : "The crude share is below the national rate."}
        </p>
      ) : crude != null && national != null && crude >= national ? (
        <p className="mt-3 text-[17px] leading-snug text-ink">
          {fi ? "Tämä alue on valtakunnallisessa karkeassa osuudessa tai sen yläpuolella." : "This county is at or above the national crude rate."}
        </p>
      ) : facts.noPublicAgestd ? (
        <p className="mt-3 text-[17px] leading-snug text-ink">{fi ? "Ei julkista tietoa." : "No public data."}</p>
      ) : agestd != null ? (
        <p className="mt-3 text-[17px] leading-snug text-ink">
          {fi ? `Ikävakioitu osuus, miehet: noin ${agestd} %.` : `Age-adjusted share, men: about ${agestd}%.`}
        </p>
      ) : (
        <p className="mt-3 text-[17px] leading-snug text-ink">
          {fi ? "Tälle alueelle ei ole erillistä lukua facts-paketissa." : "No separate figure for this county is in the facts pack."}
        </p>
      )}

      {showBar ? (
        <div className="mt-4 space-y-3">
          <GapBar label={name} pct={crude as number} max={maxPct} color={below ? "bg-rose" : "bg-teal"} />
          <GapBar label={fi ? "Koko maa" : "National rate"} pct={national as number} max={maxPct} color="bg-navy" />
          <p className="text-[13px] text-muted">
            {fi
              ? `Karkea osuus (Taulukko 11), ei ikä- eikä vaihevakioitu.`
              : `Crude share (Table 11), not age- or stage-adjusted.`}
          </p>
        </div>
      ) : null}

      <ExampleClock lang={lang} startAtAlert={clockAlert} countyName={name} />
    </div>
  );
}

function GapBar({ label, pct, max, color }: { label: string; pct: number; max: number; color: string }) {
  const w = Math.max(2, (pct / max) * 100);
  return (
    <div>
      <div className="mb-1 flex items-baseline justify-between gap-2 text-[13px]">
        <span className="text-ink">{label}</span>
        <span className="tabular-nums font-semibold text-ink">{pct.toFixed(1)}%</span>
      </div>
      <div className="h-3 overflow-hidden rounded-full bg-line/70">
        <div className={`h-full rounded-full ${color}`} style={{ width: `${w}%` }} />
      </div>
    </div>
  );
}
