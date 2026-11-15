import { useEffect, useRef, useState } from "react";
import type { StageId } from "../types";
import { dataset } from "../lib/data";
import { factById } from "../lib/facts";
import { FinlandMap, type MapLayer } from "./FinlandMap";
import { CountyPanel } from "./CountyPanel";

export type Lang = "en" | "fi";

const REGISTRY = "https://syoparekisteri.fi/assets/themes/ssy3/factsheets/keuhkosyoparaportti.html";

type Props = {
  lang: Lang;
  selectedId: string | null;
  onSelect: (id: string | null) => void;
  stage: StageId;
  onStage: (s: StageId) => void;
  layer: MapLayer;
  onLayer: (l: MapLayer) => void;
  view: "hero" | "county";
  onBack: () => void;
  clockAlert?: boolean;
};

export function Screen1({
  lang,
  selectedId,
  onSelect,
  stage,
  onStage,
  layer,
  onLayer,
  view,
  onBack,
  clockAlert,
}: Props) {
  const [info, setInfo] = useState(false);
  const rootRef = useRef<HTMLElement | null>(null);
  const national = factById("people_number_national");
  const show65 = national?.value === 65;
  const fi = lang === "fi";
  useEffect(() => {
    function onKey(e: KeyboardEvent) {
      if (e.key === "Escape") {
        setInfo(false);
        onBack();
      }
    }
    function onPtr(e: PointerEvent) {
      const el = rootRef.current;
      if (!el) return;
      if (!el.contains(e.target as Node)) {
        setInfo(false);
        onBack();
      }
    }
    window.addEventListener("keydown", onKey);
    window.addEventListener("pointerdown", onPtr);
    return () => {
      window.removeEventListener("keydown", onKey);
      window.removeEventListener("pointerdown", onPtr);
    };
  }, [onBack]);

  return (
    <section
      ref={rootRef}
      id="screen-1"
      className="mx-auto grid w-full max-w-[1280px] items-start gap-6 lg:grid-cols-[minmax(620px,1.25fr)_minmax(360px,0.85fr)]"
    >
      <div>
        <FinlandMap
          heroMode
          lang={lang}
          stage={stage}
          onStage={onStage}
          selectedId={selectedId}
          onSelect={onSelect}
          layer={layer}
          onLayer={onLayer}
        />
        <p className="mt-2 text-[13px] leading-snug text-ink">
          {fi
            ? "Osuus keuhkosyöpäpotilaista, jotka saavat parantavaa hoitoa (ikävakioitu)"
            : "Share of lung-cancer patients getting curative treatment (age-adjusted)"}
        </p>
      </div>

      <div className="relative min-w-0">
        {view === "county" && selectedId ? (
          <CountyPanel lang={lang} countyId={selectedId} onBack={onBack} clockAlert={clockAlert} />
        ) : (
          <HeroCopy fi={fi} show65={show65} />
        )}

        <div className="relative mt-5">
          <button
            type="button"
            className="inline-flex items-center gap-2 rounded-full border border-line px-3 py-1.5 text-[13px] font-semibold text-ink hover:bg-card"
            onClick={() => setInfo((v) => !v)}
            aria-expanded={info}
            aria-controls="hero-sources"
          >
            <span className="inline-flex h-5 w-5 items-center justify-center rounded-full bg-navy text-[12px] font-bold text-white" aria-hidden>
              i
            </span>
            {fi ? "Lähteet" : "Sources"}
          </button>
          {info ? (
            <div
              id="hero-sources"
              className="absolute left-0 right-0 z-20 mt-2 rounded-2xl border border-line bg-card p-4 text-[13px] leading-relaxed text-ink shadow-lg"
            >
              {show65 ? (
                <p className="font-medium">
                  {fi
                    ? "Noin 65 keuhkosyöpäpotilasta enemmän vuodessa voisi saada parantavan hoidon, jos alle keskiarvon jäävät alueet yltäisivät valtakunnalliseen osuuteen (Syöpärekisteri 2019–2023, havainnollistava, ei vaihevakioitu)."
                    : "About 65 more lung cancer patients a year could get curative treatment if every below-average county reached the national rate (Cancer Registry 2019–2023, illustrative, not stage-adjusted)."}
                </p>
              ) : null}
              <ul className="mt-3 space-y-1">
                <li>
                  <a className="font-semibold text-teal underline decoration-teal/40 hover:decoration-teal" href={REGISTRY} target="_blank" rel="noreferrer">
                    {fi ? "Syöpärekisteri 2026, Taulukko 11" : "Finnish Cancer Registry 2026, Table 11"}
                  </a>
                </li>
                <li>
                  <a className="font-semibold text-teal underline decoration-teal/40 hover:decoration-teal" href={REGISTRY} target="_blank" rel="noreferrer">
                    {fi ? "Syöpärekisteri 2026, Kuva 16" : "Finnish Cancer Registry 2026, Figure 16"}
                  </a>
                </li>
              </ul>
              <p className="mt-2 text-[13px] text-muted">
                {fi
                  ? "Havainnollistava laskelma, ei vaihevakioitu, ei elossaololuku."
                  : "Illustrative calculation, not stage-adjusted, not survival."}
              </p>
              <details className="mt-3 text-[13px] text-muted">
                <summary className="cursor-pointer font-semibold text-ink">{fi ? "Tekniset tiedot" : "Technical"}</summary>
                <p className="mt-2 break-all">
                  people_number_national, people_number_lapland, lung_curative_agestd_lapland_men, lung_curative_national.
                  {national ? ` ${national.source_table}` : ""}
                </p>
              </details>
            </div>
          ) : null}
        </div>
      </div>
    </section>
  );
}

function HeroCopy({ fi, show65 }: { fi: boolean; show65: boolean }) {
  const lapland = factById("people_number_lapland");
  if (!show65) return <HeroPairFallback fi={fi} />;
  return (
    <>
      <p className="text-[13px] font-semibold uppercase tracking-[0.14em] text-teal">
        {fi ? "Keuhkosyöpä · Suomi" : "Lung cancer · Finland"}
      </p>
      <p className="serif hero-number mt-2 font-medium tracking-tight text-navy">{fi ? "Noin 65" : "~65"}</p>
      <p className="serif mt-2 text-xl leading-snug text-ink sm:text-2xl">
        {fi
          ? "keuhkosyöpäpotilasta enemmän vuodessa voisi saada parantavan hoidon"
          : "more lung cancer patients a year could get curative treatment"}
      </p>
      <p className="mt-3 max-w-md text-[17px] leading-snug text-muted">
        {fi
          ? "jos alle keskiarvon jäävät alueet yltäisivät valtakunnalliseen osuuteen"
          : "if every below-average county reached the national rate"}
      </p>
      {lapland?.value === 12 ? (
        <p className="mt-4 text-[15px] text-ink">{fi ? "Lappi: noin 12 vuodessa" : "Lapland: ~12/yr"}</p>
      ) : null}
    </>
  );
}

function HeroPairFallback({ fi }: { fi: boolean }) {
  const h = (dataset.hero.headlines ?? []).find((x) => x.id === "lung_curative_share");
  const regions = (h?.regions ?? []) as Array<Record<string, unknown>>;
  const men = regions.map((r) => {
    const s = r.men as { value?: number } | undefined;
    return { name: String(r.name ?? ""), value: s?.value };
  });
  const a = men[0];
  const b = men[1];
  if (!a?.value || !b?.value) {
    return <p className="serif text-3xl text-ink">{fi ? "Hoitoonpääsy ei ole tasaista" : "Curative treatment is not equal"}</p>;
  }
  return (
    <>
      <p className="serif text-4xl leading-tight text-navy">
        {fi
          ? `Lappi noin ${Math.round(a.value)} % vs. Vantaa-Kerava noin ${Math.round(b.value)} %`
          : `Lapland ~${Math.round(a.value)}% vs Vantaa-Kerava ~${Math.round(b.value)}%`}
      </p>
      <p className="mt-4 text-lg text-muted">
        {fi ? "ikävakioitu parantavan hoidon osuus, miehet" : "of men get curative treatment (age-adjusted)"}
      </p>
    </>
  );
}

