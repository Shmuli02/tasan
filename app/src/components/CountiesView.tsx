import { allCountyProfiles, measureValue, shortName, type MeasureMode } from "../lib/chartData";
import { TheAskCard } from "./TheAskCard";
import { FactChip } from "./FactChip";
import { ExampleClock } from "./ExampleClock";

export function CountiesView({
  lang,
  selectedId,
  onSelect,
  onOpenBrief,
}: {
  lang: "en" | "fi";
  selectedId: string | null;
  onSelect: (id: string) => void;
  onOpenBrief: () => void;
}) {
  const fi = lang === "fi";
  const id = selectedId ?? "21";
  const profiles = allCountyProfiles();
  const crude = measureValue(id, "crude");
  const agestd: MeasureMode = "agestd-men";
  const men = measureValue(id, agestd);

  return (
    <div className="counties-view">
      <div className="hdr">
        <div>
          <div className="kicker">{fi ? "Hyvinvointialueet" : "Wellbeing services counties"}</div>
          <h1>{shortName(id, lang)}</h1>
        </div>
      </div>
      <div className="counties-grid">
        <div className="card" style={{ overflow: "auto", minHeight: 0 }}>
          <div className="card-head">
            <h2>{fi ? "Alueet" : "Counties"}</h2>
          </div>
          <ul className="county-list">
            {profiles
              .slice()
              .sort((a, b) => (a.curative_crude_pct ?? 99) - (b.curative_crude_pct ?? 99))
              .map((p) => (
                <li key={p.region_code}>
                  <button type="button" className={p.region_code === id ? "on" : ""} onClick={() => onSelect(p.region_code)}>
                    <span>{shortName(p.region_code, lang)}</span>
                    <span className="num">{p.curative_crude_pct != null ? `${p.curative_crude_pct}%` : "—"}</span>
                  </button>
                </li>
              ))}
          </ul>
        </div>
        <div className="card">
          <div className="card-head">
            <div>
              <h2>{shortName(id, lang)}</h2>
              <div className="sub">{fi ? "Karkea osuus (Taulukko 11) ja ikävakioitu kaavioarvio, miehet" : "Crude share (Table 11) and age-adjusted chart estimate, men"}</div>
            </div>
            <FactChip id="lung_curative_national" lang={lang} label="Taulukko 11" />
          </div>
          <div className="val num" style={{ font: "800 44px/1 var(--tz-font-display)", color: "var(--tz-navy)" }}>
            {crude.value != null ? `${crude.value.toFixed(1)}%` : fi ? "Ei julkista tietoa" : "No public data"}
          </div>
          <p className="cmp" style={{ margin: "6px 0 12px" }}>
            {fi ? "Koko maa" : "National"} <b>27.0%</b>
            {men.value != null ? (fi ? ` · ikävakioitu, miehet noin ${men.value}%` : ` · age-adjusted, men about ${men.value}%`) : men.missing ? (fi ? " · ei julkista ikävakioitua lukua" : " · no public age-adjusted figure") : ""}
          </p>
          {men.reason ? <p className="note">{men.reason}</p> : null}
          <ExampleClock lang={lang} countyName={shortName(id, lang)} />
        </div>
        <TheAskCard lang={lang} countyId={id} onOpenBrief={onOpenBrief} />
      </div>
    </div>
  );
}
