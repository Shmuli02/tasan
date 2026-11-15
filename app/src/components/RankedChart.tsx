import { allCountyMetrics, type CountyMetrics } from "../lib/countyMetrics";

export function RankedChart({
  lang,
  selectedId,
  onSelect,
}: {
  lang: "en" | "fi";
  selectedId: string | null;
  onSelect: (id: string) => void;
}) {
  const fi = lang === "fi";
  const rows = allCountyMetrics();
  const withAgestd = rows.filter((r) => r.agestdMen).sort((a, b) => (a.agestdMen!.value - b.agestdMen!.value));
  const crudeOnly = rows.filter((r) => !r.agestdMen && r.crude);
  const none = rows.filter((r) => !r.agestdMen && !r.crude);
  const lo = 12;
  const hi = 42;
  const x = (v: number) => `${((v - lo) / (hi - lo)) * 100}%`;

  return (
    <div className="tz-card flex h-full min-h-0 flex-col !p-4">
      <div className="mb-2 flex flex-wrap items-baseline justify-between gap-2">
        <h2 className="text-[17px] font-semibold text-ink">{fi ? "Alueet, matalin ensin" : "Counties, lowest first"}</h2>
        <span className="tz-badge tz-badge--estimate">{fi ? "Kaavioarvio" : "Chart estimate"}</span>
      </div>
      <p className="mb-3 text-[13px] text-[var(--tz-ink-3)]">
        {fi ? "Miehet, ikävakioitu parantavan hoidon osuus (Kuva 16). Viikset = 95 %:n LV. Piste = naiset." : "Men, age-adjusted curative share (Fig. 16). Whiskers = 95% CI. Dot = women."}
      </p>
      <ul className="min-h-0 flex-1 space-y-1 overflow-auto pr-1">
        {withAgestd.map((r) => (
          <BarRow key={r.id} r={r} lang={lang} selected={selectedId === r.id} onSelect={onSelect} lo={lo} x={x} />
        ))}
        {crudeOnly.length ? (
          <li className="pt-2 text-[11.5px] font-bold uppercase tracking-wide text-[var(--tz-ink-3)]">
            {fi ? "Ei ikävakioitua lukua · karkea, Taulukko 11" : "No age-adjusted figure · crude, Table 11"}
          </li>
        ) : null}
        {crudeOnly.map((r) => (
          <li key={r.id}>
            <button type="button" onClick={() => onSelect(r.id)} className={`flex w-full items-center gap-2 rounded-[10px] px-1 py-0.5 text-left hover:bg-[var(--tz-teal-100)] ${selectedId === r.id ? "bg-[var(--tz-teal-100)]" : ""}`}>
              <span className="w-[7.5rem] shrink-0 truncate text-[12px] font-semibold text-ink">{fi ? r.nameFi : r.name}</span>
              <span className="relative h-2.5 flex-1 rounded-full bg-[var(--tz-sunk)]">
                <span className="absolute inset-y-0 left-0 rounded-full bg-[var(--tz-chart-muted)]" style={{ width: x(r.crude!.share_pct) }} />
              </span>
              <span className="tz-num w-12 text-right text-[12px] font-semibold text-ink">{r.crude!.share_pct}%</span>
            </button>
          </li>
        ))}
        {none.map((r) => (
          <li key={r.id} className="flex items-center gap-2 px-1 py-0.5 text-[12px] text-[var(--tz-ink-3)]">
            <span className="w-[7.5rem] truncate font-semibold">{fi ? r.nameFi : r.name}</span>
            <span className="h-2.5 flex-1 rounded-full bg-[repeating-linear-gradient(45deg,#d9d4c9,#d9d4c9_3px,#b9b2a4_3px,#b9b2a4_6px)]" />
            <span className="w-12 text-right">{fi ? "Ei tietoa" : "No data"}</span>
          </li>
        ))}
      </ul>
    </div>
  );
}

function BarRow({
  r, lang, selected, onSelect, lo: _lo, x,
}: {
  r: CountyMetrics;
  lang: "en" | "fi";
  selected: boolean;
  onSelect: (id: string) => void;
  lo: number;
  x: (v: number) => string;
}) {
  const men = r.agestdMen!;
  const ci = men.ci95;
  const fi = lang === "fi";
  return (
    <li>
      <button
        type="button"
        onClick={() => onSelect(r.id)}
        className={`flex w-full items-center gap-2 rounded-[10px] px-1 py-0.5 text-left hover:bg-[var(--tz-teal-100)] ${selected ? "bg-[var(--tz-teal-100)]" : ""}`}
      >
        <span className="w-[7.5rem] shrink-0 truncate text-[12px] font-semibold text-ink">{fi ? r.nameFi : r.name}</span>
        <span className="relative h-3 flex-1">
          <span className="absolute inset-y-[3px] left-0 right-0 rounded-full bg-[var(--tz-sunk)]" />
          <span
            className="absolute top-[3px] h-1.5 rounded-full bg-[var(--tz-chart-primary)]"
            style={{ left: 0, width: x(men.value) }}
          />
          {ci ? (
            <span
              className="absolute top-1/2 h-[2px] -translate-y-1/2 bg-[var(--tz-chart-ci)]"
              style={{ left: x(ci[0]), width: `calc(${x(ci[1])} - ${x(ci[0])})` }}
            />
          ) : null}
          {r.agestdWomen ? (
            <span
              className="absolute top-1/2 h-2 w-2 -translate-x-1/2 -translate-y-1/2 rounded-full bg-[var(--tz-chart-compare)]"
              style={{ left: x(r.agestdWomen.value) }}
              title={fi ? `Naiset noin ${r.agestdWomen.value} %` : `Women about ${r.agestdWomen.value}%`}
            />
          ) : null}
        </span>
        <span className="tz-num w-12 shrink-0 text-right text-[12px] font-semibold text-ink">{men.value.toFixed(1)}%</span>
      </button>
    </li>
  );
}
