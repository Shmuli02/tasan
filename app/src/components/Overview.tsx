import { useEffect, useMemo, useRef, useState } from "react";
import heroDoc from "../content/hero.json";
import { FinlandMap, HelsinkiInset } from "./FinlandMap";
import { FactChip } from "./FactChip";
import { TheAskCard } from "./TheAskCard";
import {
  allCountyProfiles,
  agestdFor,
  agestdNational,
  measureValue,
  nationalCrude,
  rampColor,
  shortName,
  type MeasureMode,
} from "../lib/chartData";

type Lang = "en" | "fi";

export function Overview({
  lang,
  selectedId,
  onSelect,
  sourcesOn,
  onToggleSources,
  onOpenBrief,
}: {
  lang: Lang;
  selectedId: string | null;
  onSelect: (id: string | null) => void;
  sourcesOn: boolean;
  onToggleSources: () => void;
  onOpenBrief: () => void;
}) {
  const fi = lang === "fi";
  const [caveatOn, setCaveatOn] = useState(false);
  const caveatRef = useRef<HTMLDivElement | null>(null);
  const peopleCaveat = String((heroDoc as { people_number?: { caveat?: string } }).people_number?.caveat ?? "");

  useEffect(() => {
    if (!caveatOn) return;
    const onKey = (e: KeyboardEvent) => { if (e.key === "Escape") setCaveatOn(false); };
    const onPtr = (e: MouseEvent) => {
      if (caveatRef.current && !caveatRef.current.contains(e.target as Node)) setCaveatOn(false);
    };
    document.addEventListener("keydown", onKey);
    document.addEventListener("mousedown", onPtr);
    return () => {
      document.removeEventListener("keydown", onKey);
      document.removeEventListener("mousedown", onPtr);
    };
  }, [caveatOn]);

  const [mode, setMode] = useState<MeasureMode>("crude");
  const [hover, setHover] = useState<string | null>(null);
  const nat = nationalCrude();
  const natPct = nat?.pct ?? 27;
  const menNat = agestdNational("men");

  const rows = useMemo(() => {
    const list = allCountyProfiles().map((p) => {
      const m = measureValue(p.region_code, mode);
      return { id: p.region_code, ...m };
    });
    return list.sort((a, b) => {
      if (a.missing && b.missing) return a.id.localeCompare(b.id);
      if (a.missing) return 1;
      if (b.missing) return -1;
      return (a.value as number) - (b.value as number);
    });
  }, [mode]);

  const scaleMax = 40;
  const vals = rows.filter((r) => r.value != null).map((r) => r.value as number);
  const vmin = vals.length ? Math.min(...vals) : 16;
  const vmax = vals.length ? Math.max(...vals) : 36;
  const natLine = mode === "crude" ? natPct : menNat?.value_pct ?? null;
  const pinId = selectedId ?? "21";
  const pin = measureValue(pinId, mode);

  const ci = [
    { id: "21", sex: "men" as const, color: "#16233F" },
    { id: "04", sex: "men" as const, color: "#3A9A9A" },
    { id: "21", sex: "women" as const, color: "#16233F" },
    { id: "04", sex: "women" as const, color: "#3A9A9A" },
  ].map((r) => {
    const rec = agestdFor(r.id, r.sex);
    return { ...r, rec };
  });

  return (
    <>
      <div className="hdr">
        <div>
          <div className="kicker">{fi ? "Keuhkosyöpä · Suomi · todettu 2019–2023" : "Lung cancer · Finland · diagnosed 2019–2023"}</div>
          <h1>{fi ? "Parantava hoito ei ole tasainen Suomessa" : "Curative care is not even across Finland"}</h1>
        </div>
        <div className="chips" style={{ gap: 10 }}>
          <div className="seg" role="group" aria-label={fi ? "Mittari" : "Measure"}>
            <button type="button" className={mode === "crude" ? "on" : ""} onClick={() => setMode("crude")}>
              {fi ? "Karkea" : "Raw"}
            </button>
            <button type="button" className={mode === "agestd-men" ? "on" : ""} onClick={() => setMode("agestd-men")}>
              {fi ? "Ikävakioitu" : "Adjusted for age"}
            </button>
          </div>
          <span className="g3chip" title={fi ? "Kansallinen syöpästrategia 2026–2035, tavoite 3, mittari 3" : "National Cancer Strategy 2026–2035, Goal 3, indicator 3"}>
            Goal 3 · “Potilaat pääsevät hoitoon tavoiteaikojen puitteissa”
            <FactChip id="g3_indicator_target_times" lang={lang} sourcesOn={sourcesOn} />
          </span>
          <button type="button" className={`btn-ghost${sourcesOn ? " on" : ""}`} onClick={onToggleSources} aria-pressed={sourcesOn}>
            <svg className="i" viewBox="0 0 24 24">
              <circle cx="12" cy="12" r="10" />
              <path d="M12 16v-4M12 8h.01" />
            </svg>
            {fi ? "Lähteet" : "Sources"}
          </button>
        </div>
      </div>

      <section className="kpis">
        <div className="card kpi hero">
          <div className="val num">
            ~65<small>{fi ? "/v" : "/yr"}</small>
          </div>
          <div style={{ display: "flex", flexDirection: "column", gap: 8, minWidth: 0 }}>
            <div className="lbl">
              {fi
                ? "keuhkosyöpäpotilasta enemmän vuodessa voisi saada parantavan hoidon, jos jokainen alle keskiarvon jäävä alue yltäisi valtakunnalliseen osuuteen"
                : "more lung cancer patients a year could get curative treatment if every below-average county reached the national rate"}
            </div>
            <div className="lbl" style={{ fontSize: 12, color: "#9FB0CF", fontWeight: 500 }}>
              {fi
                ? "mitattuna parantavan hoidon merkintänä Syöpärekisterissä, 2019–2023 · havainnollistava, ei vaihevakioitu"
                : "measured as a curative-treatment record in the Cancer Registry, 2019–2023 · illustrative, not stage-adjusted"}
            </div>
            <div className="foot caveat-anchor" ref={caveatRef}>
              <span className="badge b-comp">{fi ? "Tasanin laskelma · karkea" : "Computed by Tasan · crude"}</span>
              <FactChip id="people_number_national" lang={lang} sourcesOn={sourcesOn} />
              {peopleCaveat ? (
                <button type="button" className="caveat-link" onClick={() => setCaveatOn((v) => !v)} aria-expanded={caveatOn} aria-controls="hero-caveat-pop">
                  Caveat
                </button>
              ) : null}
              {caveatOn && peopleCaveat ? (
                <div className="hero-caveat" id="hero-caveat-pop" role="dialog" aria-label="Caveat">
                  {peopleCaveat}
                </div>
              ) : null}
            </div>
          </div>
        </div>
        <div className="card kpi">
          <div className="top">
            <div className="lbl">{fi ? "Lappi · parantavan hoidon merkintä" : "Lapland · curative-treatment record"}</div>
            <span className="ico">
              <svg className="i" viewBox="0 0 24 24">
                <path d="M14.1 6 9.9 3.9a2 2 0 0 0-1.8 0L3.6 6.2A1 1 0 0 0 3 7.1v12.3a1 1 0 0 0 1.4.9l3.7-1.9a2 2 0 0 1 1.8 0l4.2 2.1a2 2 0 0 0 1.8 0l4.5-2.3a1 1 0 0 0 .6-.9V5.1a1 1 0 0 0-1.4-.9l-3.7 1.9a2 2 0 0 1-1.8 0z" />
                <path d="M15 6v15M9 3v15" />
              </svg>
            </span>
          </div>
          <div className="val num">
            18.5<small>%</small>
          </div>
          <div className="cmp">
            {fi ? "Karkea · koko maa" : "Crude · national"} <b className="num">27.0%</b>
          </div>
          <div className="foot">
            <FactChip id="lung_curative_lapland" lang={lang} sourcesOn={sourcesOn} />
            <FactChip id="lung_curative_national" lang={lang} sourcesOn={sourcesOn} />
          </div>
        </div>
        <div className="card kpi">
          <div className="top">
            <div className="lbl">{fi ? "Enemmän potilaita vuodessa Lapissa, koko maan osuudella" : "More patients a year in Lapland, at the national share"}</div>
            <span className="ico">
              <svg className="i" viewBox="0 0 24 24">
                <path d="M16 21v-2a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v2" />
                <circle cx="9" cy="7" r="4" />
                <path d="M22 21v-2a4 4 0 0 0-3-3.87M16 3.13a4 4 0 0 1 0 7.75" />
              </svg>
            </span>
          </div>
          <div className="val num">
            ~12<small>{fi ? "/v" : "/yr"}</small>
          </div>
          <div className="cmp">{fi ? "Tasanin laskelma · karkea" : "Computed by Tasan · crude"}</div>
          <div className="foot">
            <FactChip id="people_number_lapland" lang={lang} sourcesOn={sourcesOn} />
          </div>
        </div>
        <div className="card kpi gap">
          <div className="top">
            <div className="lbl">{fi ? "6 viikon hoitoonpääsy alueittain" : "6-week treatment access by region"}</div>
            <span className="ico" aria-hidden="true">
              <svg className="i" viewBox="0 0 24 24">
                <path d="M10.7 5.1A10.7 10.7 0 0 1 22 12a10.8 10.8 0 0 1-1.4 2.2M14.1 14.2a3 3 0 0 1-4.2-4.2M17.5 17.5A10.7 10.7 0 0 1 2 12a10.7 10.7 0 0 1 4.4-5.5M2 2l20 20" />
              </svg>
            </span>
          </div>
          <div className="val gap-glyph">{fi ? "Ei mitattu" : "Not measured"}</div>
          <div className="cmp">{fi ? "Mikään alue ei julkaise 6 viikon toteumaa" : "No region publishes 6-week compliance"}</div>
          <div className="foot">
            <span className="badge b-nodata">{fi ? "Tietokatko" : "Data gap"}</span>
            <FactChip id="nodata_regional_target_compliance" lang={lang} sourcesOn={sourcesOn} />
          </div>
        </div>
      </section>

      <section className="grid3">
        <div className="card mapcard">
          <div className="card-head">
            <div>
              <h2>{fi ? "Parantavan hoidon osuus alueittain" : "Curative-treatment share by county"}</h2>
              <div className="sub">
                {mode === "agestd-men"
                  ? fi
                    ? "Tummempi = matalampi osuus · miehet, ikävakioitu, kaavioarvio · klikkaa aluetta"
                    : "Darker = lower share · men, age-adjusted, chart estimate · click a county"
                  : fi
                    ? "Tummempi = matalampi osuus · klikkaa aluetta"
                    : "Darker = lower share · click a county"}
              </div>
            </div>
            {mode === "agestd-men" ? (
              <span className="badge b-est">{fi ? "Kaavioarvio" : "Chart estimate"}</span>
            ) : (
              <FactChip id="lung_curative_national" lang={lang} sourcesOn={sourcesOn} />
            )}
          </div>
          <div className="mapwrap">
            <FinlandMap
              dashboard
              metric={mode}
              heroMode
              lang={lang}
              stage="treatment"
              onStage={() => undefined}
              layer="curative"
              onLayer={() => undefined}
              selectedId={pinId}
              onSelect={onSelect}
              onHover={setHover}
            />
            <HelsinkiInset selectedId={pinId} onSelect={onSelect} lang={lang} metric={mode} hover={hover} onHover={setHover} scaleMin={vmin} scaleMax={vmax} />
            {pin.value != null ? (
              <div className="pin" style={{ right: 8, top: 16, left: "auto" }}>
                {shortName(pinId, lang)}
                <b>
                  {mode === "agestd-men" ? (fi ? "noin " : "about ") : ""}
                  {pin.value.toFixed(1)}%
                </b>
              </div>
            ) : pin.missing ? (
              <div className="pin" style={{ right: 8, top: 16, left: "auto" }}>
                {shortName(pinId, lang)}
                <b>{fi ? "Ei julkista tietoa" : "No public data"}</b>
              </div>
            ) : null}
          </div>
          <div className="legend">
            <span>{fi ? "matalampi" : "lower"}</span>
            <span className="ramp">
              <i style={{ background: "#16233F" }} />
              <i style={{ background: "#2D6B7D" }} />
              <i style={{ background: "#4F9C9C" }} />
              <i style={{ background: "#86BFB9" }} />
              <i style={{ background: "#BCDCD6" }} />
              <i style={{ background: "#E6F2EF" }} />
            </span>
            <span>{fi ? "korkeampi" : "higher"}</span>
            <span style={{ marginLeft: "auto" }}>
              <span className="nd" />
              {fi ? "Ei julkista tietoa" : "No public data"}
            </span>
          </div>
        </div>

        <div className="card barscard" style={{ display: "flex", flexDirection: "column", minHeight: 0 }}>
          <div className="card-head">
            <div>
              <h2>{fi ? "Kaikki alueet, järjestettynä" : "All counties, ranked"}</h2>
              <div className="sub">
                {mode === "agestd-men"
                  ? fi
                    ? "Ikävakioitu osuus, miehet, kaavioarvio"
                    : "Age-adjusted share, men, chart estimate"
                  : fi
                    ? "Osuus, jolla parantavan hoidon merkintä 12 kuukauden sisällä (karkea)"
                    : "Share with a curative-treatment record within 12 months (crude)"}
              </div>
            </div>
            {mode === "agestd-men" ? (
              <span className="badge b-est">{fi ? "Kaavioarvio" : "Chart estimate"}</span>
            ) : (
              <FactChip id="lung_curative_national" lang={lang} sourcesOn={sourcesOn} />
            )}
          </div>
          <div className="bars" style={{ marginTop: 10 }}>
            <div className="axis">
              {[0, 10, 20, 30, 40].map((n) => (
                <div key={n} className="g" style={{ left: `${(n / scaleMax) * 100}%` }}>
                  <span>{n}%</span>
                </div>
              ))}
              {natLine != null ? (
                <div className="nat" style={{ left: `${(natLine / scaleMax) * 100}%` }}>
                  <span>
                    {mode === "agestd-men"
                      ? fi
                        ? `Koko maa, miehet noin ${natLine}%`
                        : `National, men about ${natLine}%`
                      : fi
                        ? `Koko maa ${natLine.toFixed(1)}%`
                        : `National ${natLine.toFixed(1)}%`}
                  </span>
                </div>
              ) : null}
            </div>
            {rows.map((r) => (
              <button
                type="button"
                key={r.id}
                className={`brow${r.id === pinId ? " sel" : ""}`}
                onClick={() => onSelect(r.id)}
              >
                <span className="nm">{shortName(r.id, lang)}</span>
                <div className="track">
                  {r.value != null ? (
                    <div className="bar" style={{ width: `${(r.value / scaleMax) * 100}%`, background: rampColor(r.value, vmin, vmax) }} />
                  ) : (
                    <div className="bar" style={{ width: "40%", background: "repeating-linear-gradient(45deg,#D9D4C9 0 3px,#B9B2A4 3px 4.5px)" }} />
                  )}
                </div>
                <span className="v">
                  {r.value != null && r.factIds.length
                    ? `${mode === "agestd-men" ? (fi ? "noin " : "about ") : ""}${r.value.toFixed(1)}%`
                    : r.missing
                      ? ""
                      : ""}
                </span>
              </button>
            ))}
          </div>
        </div>

                  <div className="card ci-card">
            <div className="card-head">
              <div>
                <h2>{fi ? "Ikävakioitu, sama ero" : "Age-adjusted, same gap"}</h2>
                <div className="sub">{fi ? "Parantavan hoidon osuus / 100 potilasta" : "Curative share per 100 patients"}</div>
              </div>
              <span className="badge b-est">{fi ? "Kaavioarvio" : "Chart estimate"}</span>
            </div>
            {(["men", "women"] as const).map((sex) => (
              <div key={sex}>
                <div className="sexlbl">{sex === "men" ? (fi ? "Miehet" : "Men") : fi ? "Naiset" : "Women"}</div>
                {ci
                  .filter((r) => r.sex === sex)
                  .map((r) => {
                    const rec = r.rec;
                    if (!rec || rec.value_pct == null || rec.ci95_low == null || rec.ci95_high == null) return null;
                    const left = ((rec.ci95_low - 10) / 40) * 100;
                    const width = ((rec.ci95_high - rec.ci95_low) / 40) * 100;
                    const mid = ((rec.value_pct - 10) / 40) * 100;
                    return (
                      <div className="ci-row" key={`${r.id}-${sex}`}>
                        <span className="nm">{shortName(r.id, lang)}</span>
                        <div className="ci-track">
                          <div className="w" style={{ left: `${left}%`, width: `${width}%` }} />
                          <div className="d" style={{ left: `${mid}%`, background: r.color }} />
                          <div className="l" style={{ left: `${mid}%` }}>
                            ~{rec.value_pct}
                          </div>
                        </div>
                      </div>
                    );
                  })}
              </div>
            ))}
            <div className="ci-axis">
              <span />
              <div>
                <span>10%</span>
                <span>20%</span>
                <span>30%</span>
                <span>40%</span>
                <span>50%</span>
              </div>
            </div>
            <div className="note">
              {fi
                ? "Luettu raportin kaaviosta (±1 %-yksikkö) · 95 %:n välit eivät mene päällekkäin"
                : "Read from report chart (±1 pp) · 95% intervals don't overlap"}
            </div>
            <div className="chips" style={{ marginTop: 8 }}>
              <FactChip id="lung_curative_agestd_lapland_men" lang={lang} sourcesOn={sourcesOn} />
              <FactChip id="lung_curative_agestd_vk_men" lang={lang} sourcesOn={sourcesOn} />
              <FactChip id="lung_curative_agestd_lapland_women" lang={lang} sourcesOn={sourcesOn} />
            </div>
          </div>

          <TheAskCard lang={lang} countyId={pinId} onOpenBrief={onOpenBrief} compact />
      </section>
    </>
  );
}
