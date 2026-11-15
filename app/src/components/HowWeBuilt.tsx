import { useEffect, useMemo, useRef, useState } from "react";
import samples from "../content/extract/howwebuilt_notes.json";
import numbersPack from "../content/extract/HOW_WE_BUILT_NUMBERS.json";

type Lang = "en" | "fi";
type Ev = {
  type: string;
  date?: string;
  evidence_span?: string;
  start?: number;
  end?: number;
  confidence?: number;
};
type Note = {
  note_id: string;
  patient_id: string;
  lang: string;
  doc_type: string;
  note_date: string;
  title?: string;
  text: string;
  corpus_id?: string;
  split?: string | null;
  gold_events?: Ev[];
  model_events?: Ev[];
  events?: Ev[];
  day_count?: number;
  alert?: boolean;
  source?: string;
  model_name?: string;
};

const PACK = samples as {
  banner?: string;
  notes: Note[];
  source_now?: string;
  source_after_gpu?: string;
  n?: number;
};
const NOTES: Note[] = PACK.notes;
const OPEN_DEFAULT = "SYN2-P0054-oncology_note-04";

const EVENT_ORDER = [
  "referral_received",
  "ct_done",
  "biopsy_done",
  "pathology_result",
  "mdt_decision",
  "treatment_decision",
  "treatment_start",
] as const;

const HL: Record<string, { bg: string; fg: string }> = {
  referral_received: { bg: "#C5E0DC", fg: "#1A4A48" },
  ct_done: { bg: "#C4D6F0", fg: "#1C3A66" },
  biopsy_done: { bg: "#DDD0F0", fg: "#4A2C78" },
  pathology_result: { bg: "#F0DB9A", fg: "#5A4208" },
  mdt_decision: { bg: "#C9D2E2", fg: "#16233F" },
  treatment_decision: { bg: "#EEC8B0", fg: "#5A2E12" },
  treatment_start: { bg: "#E8C5D8", fg: "#6A2450" },
};

const EV_LABEL: Record<string, { en: string; fi: string }> = {
  referral_received: { en: "Referral received", fi: "Lähete saapui" },
  ct_done: { en: "CT / imaging", fi: "TT / kuvantaminen" },
  biopsy_done: { en: "Biopsy", fi: "Biopsia" },
  pathology_result: { en: "Pathology result", fi: "Patologian tulos" },
  mdt_decision: { en: "MDT decision", fi: "MDT-päätös" },
  treatment_decision: { en: "Treatment decision", fi: "Hoitopäätös" },
  treatment_start: { en: "Treatment start", fi: "Hoito alkoi" },
};

function extractedEvents(note: Note): Ev[] {
  if (note.model_events && note.model_events.length) return note.model_events;
  return note.gold_events ?? note.events ?? [];
}

function bodyPos(text: string): number {
  let eq = 0;
  let pos = 0;
  for (const line of text.split(/(?<=\n)/)) {
    if ([...line.trim()].every((c) => c === "=") && line.trim().length > 20) {
      eq += 1;
      if (eq === 2) return pos + line.length;
    }
    pos += line.length;
  }
  return 0;
}

function parseHeader(text: string): Record<string, string> {
  const meta: Record<string, string> = {};
  for (const line of text.split("\n")) {
    if (!line.includes(":") || line.startsWith("=")) continue;
    const i = line.indexOf(":");
    const key = line.slice(0, i).trim();
    if (["corpus_id", "patient_id", "document_id", "document_type", "language", "note_date", "display_name"].includes(key)) {
      meta[key] = line.slice(i + 1).trim();
    }
  }
  return meta;
}

function isV2(note: Note) {
  return /v2/.test(note.corpus_id ?? "") || note.note_id.startsWith("SYN2-");
}

function extractLabel(sourceNow?: string, modelName?: string) {
  const raw = `${modelName ?? ""} ${sourceNow ?? ""}`.toLowerCase();
  if (raw.includes("qwen3-32") || raw.includes("qwen/qwen3-32")) return "Qwen3-32B";
  if (raw.includes("regex")) return "regex_baseline";
  const s = (sourceNow || modelName || "").trim();
  return s || "regex_baseline";
}

const SHEET_W = 248;
const FEATURE_W = 280;
const FEATURE_H = 372;

type Pose = { x: number; y: number; rot: number; z: number };

/** Fan layout sized to the stage: the featured note sits centred, upright and on top,
 *  the rest fan out symmetrically behind it. Coordinates are in design px; `scale`
 *  maps them onto the real stage so the featured sheet is always fully visible. */
function fanLayout(nOthers: number, w: number, h: number): { scale: number; cx: number; featured: Pose; others: Pose[] } {
  const scale = Math.max(0.5, Math.min(1, (h - 32) / (FEATURE_H + 28), (w - 24) / (FEATURE_W + 20)));
  const wd = w / scale;
  const hd = h / scale;
  const cx = wd / 2;
  const fy = Math.max(12, (hd - FEATURE_H) / 2 - 4);
  const featured: Pose = { x: Math.round(cx - FEATURE_W / 2), y: Math.round(fy), rot: 0, z: 50 };
  const half = Math.max(60, Math.min(wd / 2 - SHEET_W / 2 - 12, 440));
  const left = Math.ceil(nOthers / 2);
  const right = nOthers - left;
  const ts: number[] = [];
  for (let j = left - 1; j >= 0; j--) ts.push(-(0.22 + (0.78 * j) / Math.max(left - 1, 1)));
  for (let j = 0; j < right; j++) ts.push(0.22 + (0.78 * j) / Math.max(right - 1, 1));
  const others = ts.map((t) => ({
    x: Math.round(cx + t * half - SHEET_W / 2),
    y: Math.round(fy + 26 + t * t * 34),
    rot: Math.round(t * 24 * 10) / 10,
    z: 40 - Math.round(Math.abs(t) * 30),
  }));
  return { scale, cx, featured, others };
}

function fanPositions(n: number, mode: "fan" | "open"): { x: number; y: number; rot: number }[] {
  const pos: { x: number; y: number; rot: number }[] = [];
  if (mode === "fan") {
    for (let i = 0; i < n; i++) {
      const t = n <= 1 ? 0 : i / (n - 1);
      pos.push({ x: Math.round(260 + t * 640), y: Math.round(168 + (t - 0.5) ** 2 * 150), rot: Math.round((-32 + t * 62) * 10) / 10 });
    }
    return pos;
  }
  const closed = n - 1;
  for (let i = 0; i < closed; i++) {
    const t = closed <= 1 ? 0 : i / Math.max(closed - 1, 1);
    pos.push({ x: Math.round(28 + t * 360), y: Math.round(150 + (t - 0.4) ** 2 * 130), rot: Math.round((-28 + t * 44) * 10) / 10 });
  }
  return pos;
}

function goldDate(note: Note, typ: string): string | undefined {
  return (note.gold_events ?? []).find((e) => e.type === typ)?.date;
}

function HighlightedBody({ text, events, from }: { text: string; events: Ev[]; from: number }) {
  const marks = events
    .filter((e) => (e.start ?? -1) >= 0 && (e.end ?? -1) >= 0 && (e.end as number) > from && (e.start as number) < text.length)
    .sort((a, b) => (a.start as number) - (b.start as number));
  const nodes: { key: number; t: string; ev?: Ev }[] = [];
  let i = from;
  let k = 0;
  for (const e of marks) {
    const s = Math.max(e.start as number, from);
    const en = Math.min(e.end as number, text.length);
    if (s < i) continue;
    if (s > i) nodes.push({ key: k++, t: text.slice(i, s) });
    nodes.push({ key: k++, t: text.slice(s, en), ev: e });
    i = en;
  }
  if (i < text.length) nodes.push({ key: k++, t: text.slice(i) });
  return (
    <div className="body">
      {nodes.map((p) =>
        p.ev ? (
          <mark
            key={p.key}
            className={`hl hl-${p.ev.type}`}
            data-type={p.ev.type}
            data-date={p.ev.date}
            data-start={p.ev.start}
            data-end={p.ev.end}
          >
            {p.t}
          </mark>
        ) : (
          <span key={p.key}>{p.t}</span>
        ),
      )}
    </div>
  );
}

function Stamp() {
  return <div className="stamp">SYNTHETIC · NOT A REAL PATIENT</div>;
}

function ClockSvg({ day, of = 42, size = 88, stroke = 9 }: { day: number; of?: number; size?: number; stroke?: number }) {
  const r = (size - stroke) / 2;
  const c = 2 * Math.PI * r;
  const f = Math.min(day / of, 1);
  const col = day < 21 ? "#2A7F62" : day < 28 ? "#B38A00" : day < 42 ? "#D9822B" : "#C2412D";
  const ticks = [21, 28].map((d) => {
    const a = (2 * Math.PI * d) / of - Math.PI / 2;
    const x1 = size / 2 + (r - 5) * Math.cos(a);
    const y1 = size / 2 + (r - 5) * Math.sin(a);
    const x2 = size / 2 + (r + 5) * Math.cos(a);
    const y2 = size / 2 + (r + 5) * Math.sin(a);
    return <line key={d} x1={x1} y1={y1} x2={x2} y2={y2} stroke="#9AA1AF" strokeWidth="2" />;
  });
  return (
    <svg width={size} height={size} viewBox={`0 0 ${size} ${size}`}>
      <circle cx={size / 2} cy={size / 2} r={r} fill="none" stroke="#E4DFD4" strokeWidth={stroke} />
      <circle
        cx={size / 2}
        cy={size / 2}
        r={r}
        fill="none"
        stroke={col}
        strokeWidth={stroke}
        strokeLinecap="round"
        strokeDasharray={`${(c * f).toFixed(1)} ${c.toFixed(1)}`}
        transform={`rotate(-90 ${size / 2} ${size / 2})`}
      />
      {ticks}
      <text x="50%" y="48%" textAnchor="middle" fontFamily="Nunito, Inter, sans-serif" fontWeight={800} fontSize={22} fill="#16233F">
        D{day}
      </text>
      <text x="50%" y="66%" textAnchor="middle" fontFamily="Inter, sans-serif" fontSize={10} fill="#6B7385">
        of {of} · 6 wk
      </text>
    </svg>
  );
}


type NumbersPack = typeof numbersPack;

function Src({ path }: { path: string }) {
  return <span className="src built-src">{path}</span>;
}

function ResultTiles({ fi, pack }: { fi: boolean; pack: NumbersPack }) {
  const f1 = pack.extract.exact_f1.qwen3_32b_v2_test;
  const regex = pack.extract.exact_f1.regex_untuned_v2_test;
  const alert = pack.extract.alert_accuracy.qwen3_32b_v2_test;
  const v1c = pack.extract.throughput.v1.usd_per_1000_notes;
  const v2c = pack.extract.throughput.v2.usd_per_1000_notes;
  const sketch = pack.extract.nationwide_yearly_sketch;
  const loc = pack.extract.location.value;
  const locCountry = pack.extract.location.country === "FI" ? "Finland" : pack.extract.location.country;
  const twin = pack.pathway_twin.full_run_a;
  const twinTotal = pack.pathway_twin.spend_usd_total_approx.value;
  const spend = pack.spend_totals_usd;
  const live = pack.extract.live_gpu_endpoint;
  return (
    <section className="hwb-tiles" aria-label={fi ? "Tulokset" : "Results"}>
      <article className="btile feature">
        <h3>{fi ? "Extract-tarkkuus" : "Extract accuracy"}</h3>
        <p className="btile-num">{f1.rounded.toFixed(3)}</p>
        <p className="btile-sub">
          {fi ? "Tarkka F1, pidätetty v2-testi" : "Held-out exact F1, v2 test"} ({f1.n_documents})
          {" · "}
          {fi ? "vs regex" : "vs regex"} {regex.rounded.toFixed(3)}
          {" · "}
          {fi ? "hälytys" : "day-28 alert"} {alert.rounded.toFixed(3)}
        </p>
        <p className="btile-line">
          {pack.extract.model.value} · {locCountry} ({loc})
        </p>
        <div className="chiprow"><Src path={f1.source} /></div>
      </article>
      <article className="btile">
        <h3>{fi ? "Kustannusluonnos" : "Throughput / cost"}</h3>
        <p className="btile-num">${v2c.toFixed(2)}</p>
        <p className="btile-sub">
          {fi ? "/ 1 000 muistiota (v2); v1" : "per 1k notes (v2); v1"} ${v1c.toFixed(2)}
        </p>
        <p className="btile-line">
          {sketch.notes_per_year.toLocaleString("en-US")} {fi ? "muistiota/v" : "notes/yr"} ≈ ${sketch.usd_per_year_v2_like}/yr
          {fi ? " (v2)" : " (v2)"} · ${sketch.usd_per_year_v1_like}/yr {fi ? "(v1)" : "(v1)"}
        </p>
        <div className="chiprow">
          <span className="badge b-ex">{fi ? "Luonnos" : "sketch"}</span>
          <Src path={sketch.source} />
        </div>
      </article>
      <article className="btile">
        <h3>Pathway Twin</h3>
        <p className="btile-num">
          {twin.scenario_jobs}+{twin.calibration_jobs}
        </p>
        <p className="btile-sub">
          {fi ? "ajoa A · tavu-identtinen paikallisen kanssa" : "jobs, run A · byte-identical to local"}
        </p>
        <p className="btile-line">
          ≈ ${twin.cost_usd_range[0].toFixed(2)}–{twin.cost_usd_range[1].toFixed(2)} {fi ? "(ajo A)" : "(run A)"} · {fi ? "yhteensä" : "total"} ≈ ${twinTotal.toFixed(2)}
        </p>
        <div className="chiprow">
          <Src path={twin.source} />
          <Src path={twin.also} />
        </div>
      </article>
      <article className="btile">
        <h3>{fi ? "Verda yhteensä" : "Total Verda cost"}</h3>
        <p className="btile-num">
          ≈ ${spend.team_preferred_range[0].toFixed(2)}–${spend.team_preferred_range[1].toFixed(2)}
        </p>
        <p className="btile-sub">
          Extract ≈ ${spend.extract_preferred_approx.toFixed(2)} · Twin ≈ ${spend.twin_preferred_approx.toFixed(2)} · Ask ≈ ${spend.ask_inference_range[0]}–${spend.ask_inference_range[1]}
        </p>
        <div className="chiprow">
          {spend.sources.slice(0, 3).map((src) => (
            <Src key={src} path={src} />
          ))}
        </div>
      </article>
      <article className="btile next">
        <h3>{fi ? "Seuraavaksi" : "Next"}</h3>
        <ul>
          <li>{fi ? "LoRA / hienosäätö — ei ajettu" : "LoRA / fine-tune — not run"}</li>
          <li>{fi ? "Rinnakkaisuussweep — ei ajettu" : "Concurrency sweep — not run"}</li>
          <li>{fi ? "Live Extract-pääte — ei käynnissä" : "Live Extract endpoint — not running"}</li>
        </ul>
        <div className="chiprow"><Src path={live.source} /></div>
      </article>
    </section>
  );
}

function WorkedStrip({ fi }: { fi: boolean }) {
  return (
    <section className="worked-strip">
      <h2>{fi ? "Miten teimme työtä" : "How we worked"}</h2>
      <ul>
        <li>
          <b>81</b> {fi ? "lähteistettyä faktaa" : "sourced facts"}
        </li>
        <li>
          <b>14</b> {fi ? "kieltäytymistä" : "refusals"}
        </li>
        <li>
          <b>133</b> / <b>3374</b> {fi ? "tarkistusta, 0 virhettä" : "checks / 0 failures"}
        </li>
        <li>{fi ? "Vain roolit, ei nimiä" : "Roles only"}</li>
        <li>{fi ? "Vain synteettiset muistiot" : "Synthetic notes only"}</li>
      </ul>
      <Src path="data/scripts/check_facts.py" />
      <Src path="data/scripts/check_app_data.py" />
    </section>
  );
}

export function HowWeBuilt({ lang }: { lang: Lang }) {
  const fi = lang === "fi";
  const [mode, setMode] = useState<"fan" | "open">("fan");
  const [openId, setOpenId] = useState(OPEN_DEFAULT);
  const [anim, setAnim] = useState(true);
  const stageRef = useRef<HTMLDivElement | null>(null);
  const [stage, setStage] = useState({ w: 1100, h: 560 });
  useEffect(() => {
    const el = stageRef.current;
    if (!el) return;
    const ro = new ResizeObserver(([e]) => {
      const { width, height } = e.contentRect;
      if (width > 0 && height > 0) setStage({ w: width, h: height });
    });
    ro.observe(el);
    return () => ro.disconnect();
  }, []);
  const open = NOTES.find((n) => n.note_id === openId) ?? NOTES[0];
  const events = useMemo(() => extractedEvents(open), [open]);
  const present = useMemo(() => new Set(events.map((e) => e.type)), [events]);
  const srcNow = PACK.source_now ?? "";
  const modelShort = extractLabel(srcNow, open.model_name);

  function runAnim() {
    setAnim(false);
    requestAnimationFrame(() => setAnim(true));
  }

  function openNote(id: string) {
    setOpenId(id);
    setMode("open");
    runAnim();
  }

  function showFan() {
    setMode("fan");
    runAnim();
  }

  const others = NOTES.filter((n) => n.note_id !== open.note_id);
  const fanOrder = mode === "fan" ? [...others, open] : others;
  const fan = fanLayout(others.length, stage.w, stage.h);
  const positions: Pose[] =
    mode === "fan"
      ? [...fan.others, fan.featured]
      : fanPositions(NOTES.length, mode).map((p, i) => ({ ...p, z: i + 1 }));

  const header = parseHeader(open.text);
  const bp = bodyPos(open.text);
  const started = events.some((e) => e.type === "treatment_start");

  return (
    <div className={`hwb-page state-${mode}`}>
      <header className="hwb-hdr">
        <div>
          <div className="kicker">{fi ? "Verda extract · EU-hosted inference" : "Verda extract · EU-hosted inference"}</div>
          <h1>{fi ? "Näin teimme tämän" : "How we built it"}</h1>
        </div>
        <div className="chips">
          <span className="badge b-ex">{fi ? "SYNTEETTISET muistiot" : "SYNTHETIC notes"}</span>
          <span className="badge b-comp">{modelShort}</span>
          <span className="badge b-verda" style={{ height: 22, fontSize: 11, padding: "0 10px" }}>EU-hosted</span>
        </div>
      </header>

      <div className="hero">
        <div className="stage" ref={stageRef}>
          <div className="stage-floor" />
          <div
            className={`sheets${anim ? " anim" : ""}`}
            style={mode === "fan" ? { transform: `scale(${fan.scale})`, transformOrigin: "0 0" } : undefined}
          >
            {fanOrder.map((note, i) => {
              const pos = positions[i] ?? { x: 0, y: 0, rot: 0, z: i + 1 };
              const isOpenish = mode === "fan" && note.note_id === open.note_id;
              const text = note.text;
              const from = bodyPos(text);
              const body = text.slice(from);
              return (
                <article
                  key={note.note_id}
                  className={`sheet${isOpenish ? " open" : ""}`}
                  style={{
                    ["--x" as string]: `${pos.x}px`,
                    ["--y" as string]: `${pos.y}px`,
                    ["--rot" as string]: `${pos.rot}deg`,
                    ["--from-x" as string]: mode === "fan" ? `${Math.round(fan.cx - SHEET_W / 2)}px` : "210px",
                    ["--from-y" as string]: mode === "fan" ? `${fan.featured.y + 40}px` : "90px",
                    ["--from-rot" as string]: "-2deg",
                    ["--stagger" as string]: `${(i + 1) * 45}ms`,
                    zIndex: pos.z,
                    left: 0,
                    top: 0,
                    transform: `translate(${pos.x}px, ${pos.y}px) rotate(${pos.rot}deg)`,
                  }}
                  data-note-id={note.note_id}
                  onClick={() => (mode === "fan" && isOpenish ? openNote(note.note_id) : openNote(note.note_id))}
                  role="button"
                  tabIndex={0}
                  onKeyDown={(e) => {
                    if (e.key === "Enter" || e.key === " ") {
                      e.preventDefault();
                      openNote(note.note_id);
                    }
                  }}
                >
                  <div className="tab-lab">{note.doc_type}</div>
                  <div className="meta-row">
                    <span className="lang">
                      {note.lang.toUpperCase()} · {note.note_date}
                    </span>
                    {isV2(note) ? <span className="v2">v2</span> : null}
                  </div>
                  {isOpenish ? <HighlightedBody text={text} events={events} from={from} /> : <div className="body">{body}</div>}
                  <Stamp />
                  <div className="nid">{note.note_id}</div>
                </article>
              );
            })}

            {mode === "open" ? (
              <article
                className="sheet open"
                style={{
                  ["--x" as string]: "455px",
                  ["--y" as string]: "36px",
                  ["--rot" as string]: "-1.2deg",
                  ["--from-x" as string]: "240px",
                  ["--from-y" as string]: "70px",
                  ["--from-rot" as string]: "-8deg",
                  ["--stagger" as string]: "0ms",
                  zIndex: 20,
                  left: 0,
                  top: 0,
                  transform: "translate(455px, 36px) rotate(-1.2deg)",
                }}
                data-note-id={open.note_id}
                onClick={showFan}
              >
                <div className="tab-lab">{open.doc_type}</div>
                <div className="file-head">
                  <div className="banner">SYNTHETIC DOCUMENT — NOT A REAL PATIENT</div>
                  <dl>
                    {(["corpus_id", "patient_id", "document_id", "note_date", "language", "display_name"] as const).map((k) => (
                      <span key={k} style={{ display: "contents" }}>
                        <dt>{k}</dt>
                        <dd>{header[k] ?? (k === "document_id" ? open.note_id : k === "patient_id" ? open.patient_id : k === "language" ? open.lang : k === "note_date" ? open.note_date : "")}</dd>
                      </span>
                    ))}
                  </dl>
                </div>
                <HighlightedBody text={open.text} events={events} from={bp} />
                <Stamp />
                <div className="nid">
                  {open.note_id}
                  {isV2(open) ? " · v2 held-out" : ""} · model_events · {open.source ?? srcNow} · offsets into text
                </div>
              </article>
            ) : null}
          </div>
        </div>

        {mode === "fan" && events.length ? (
          <div className="xstrip" aria-label={fi ? "Poimitut tapahtumat" : "Extracted events"}>
            <div className="xstrip-hd">
              <b>{fi ? "Mallin poimimat tapahtumat" : "What the model pulled out"}</b>
              <span>
                {modelShort} · {open.note_id} · {fi ? "klikkaa muistiota nähdäksesi kaikki" : "click the note for offsets"}
              </span>
            </div>
            <ol className="xchips">
              {[...events].sort((a, b) => String(a.date ?? "").localeCompare(String(b.date ?? ""))).map((e) => (
                <li key={`${e.type}-${e.date}-${e.start}`} style={{ ["--c" as string]: HL[e.type]?.bg, ["--f" as string]: HL[e.type]?.fg }}>
                  <span className="k">{EV_LABEL[e.type]?.[fi ? "fi" : "en"] ?? e.type}</span>
                  <span className="d">{e.date}</span>
                </li>
              ))}
            </ol>
          </div>
        ) : null}

        {mode === "open" ? (
          <aside className="rail">
            <div className="card" style={{ flex: "none" }}>
              <div className="card-head">
                <div>
                  <h2>{fi ? "Tapahtumatyypit" : "Event types"}</h2>
                  <div className="sub">{fi ? "Korosteväri avatussa muistiossa" : "Marker colour on the open note"}</div>
                </div>
              </div>
              <div className="legend">
                {EVENT_ORDER.map((typ) => (
                  <div key={typ} className={`leg${present.has(typ) ? "" : " unused"}`}>
                    <i style={{ background: HL[typ].bg, color: HL[typ].fg }} />
                    {typ}
                  </div>
                ))}
              </div>
            </div>
            <div className="card" style={{ flex: 1 }}>
              <div className="card-head">
                <div>
                  <h2>{fi ? "Poimitut tapahtumat" : "Extracted events"}</h2>
                  <div className="sub">{open.note_id}</div>
                </div>
                <span className="src">{open.source ?? srcNow}</span>
              </div>
              <div className="evlist">
                {events.map((e) => {
                  const off = (e.start ?? -1) >= 0 ? `${e.start}–${e.end}` : "no offset";
                  const g = goldDate(open, e.type);
                  const differs = Boolean(g && e.date && g !== e.date);
                  return (
                    <div className="ev" key={`${e.type}-${e.date}-${e.start}`}>
                      <i style={{ background: HL[e.type]?.bg }} />
                      <span className="t">
                        {e.type}
                        <small>{off}</small>
                      </span>
                      <span className="d">
                        {e.date}
                        {differs ? <span className="diff">{fi ? "eroaa kullasta" : "differs from gold"}</span> : null}
                      </span>
                    </div>
                  );
                })}
              </div>
              <div className="note-sm">
                From model_events · {open.model_name ?? modelShort}. Spans are start/end into text (skip if −1).
              </div>
            </div>
            <div className="card" style={{ flex: "none" }}>
              <div className="card-head">
                <div>
                  <h2>{fi ? "Päivän 28 kello" : "Day-28 clock"}</h2>
                  <div className="sub">{fi ? "Kultatapahtumat vs. note_date" : "Gold events vs note_date"}</div>
                </div>
              </div>
              <div className="clockbox">
                <ClockSvg day={open.day_count ?? 0} />
                <div className="who">
                  <b>{open.patient_id}</b>
                  day_count {open.day_count ?? 0} ·{" "}
                  {open.alert ? (
                    <span className="dchip" style={{ background: "#FCE9D6", color: "#A75A12" }}>
                      {fi ? "Hälytys" : "Alert"}
                    </span>
                  ) : (
                    <span className="dchip" style={{ background: "#E2F1EA", color: "#2A7F62" }}>
                      {fi ? "Ei hälytystä" : "No alert"}
                    </span>
                  )}
                  <br />
                  {started
                    ? fi
                      ? "Hoito merkitty tällä muistiolla."
                      : "Treatment recorded on this note."
                    : fi
                      ? "Hoitoa ei ole aloitettu tällä muistiolla."
                      : "Treatment not started on this note."}
                </div>
              </div>
            </div>
          </aside>
        ) : null}
      </div>

      <ResultTiles fi={fi} pack={numbersPack} />

      <section className="card pipe">
        <div className="step">
          <span className="ico">
            <svg className="i" viewBox="0 0 24 24">
              <path d="M15 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V7Z" />
              <path d="M14 2v4a2 2 0 0 0 2 2h4" />
              <path d="M10 9H8M16 13H8M16 17H8" />
            </svg>
          </span>
          <div className="lab">
            <h3>{fi ? "Synteettiset muistiot" : "Synthetic notes"}</h3>
            <div className="sub">{fi ? "10 näytemuistiota · ei oikeita potilaita" : "10 showcase notes · not real patients"}</div>
          </div>
        </div>
        <div className="arrow" />
        <div className="step next">
          <span className="ico next">
            <svg className="i" viewBox="0 0 24 24">
              <rect width="16" height="16" x="4" y="4" rx="2" />
              <rect width="6" height="6" x="9" y="9" rx="1" />
              <path d="M15 2v2M15 20v2M2 15h2M2 9h2M20 15h2M20 9h2M9 2v2M9 20v2" />
            </svg>
          </span>
          <div className="lab">
            <h3>{fi ? "Poiminta Verdalla" : "Extract on Verda"}</h3>
            <div className="sub">
              <b>{modelShort}</b> · Finland (FIN-01)
              <br />
              regex_baseline {fi ? "on lattia" : "as the floor"}
            </div>
          </div>
        </div>
        <div className="arrow" />
        <div className="step">
          <span className="ico">
            <svg className="i" viewBox="0 0 24 24">
              <path d="M8 3H7a2 2 0 0 0-2 2v5a2 2 0 0 1-2 2 2 2 0 0 1 2 2v5c0 1.1.9 2 2 2h1" />
              <path d="M16 21h1a2 2 0 0 0 2-2v-5c0-1.1.9-2 2-2a2 2 0 0 1-2-2V5a2 2 0 0 0-2-2h-1" />
            </svg>
          </span>
          <div className="lab">
            <h3>{fi ? "Rakenteiset tapahtumat" : "Structured events"}</h3>
            <div className="sub">{fi ? "7 tyyppiä, päivämäärät + evidenssi" : "7 types, dates + evidence spans"}</div>
          </div>
        </div>
        <div className="arrow" />
        <div className="step">
          <span className="ico">
            <svg className="i" viewBox="0 0 24 24">
              <circle cx="12" cy="12" r="10" />
              <path d="M12 6v6l4 2" />
            </svg>
          </span>
          <div className="lab">
            <h3>{fi ? "Päivän 28 kello" : "Day-28 clock"}</h3>
            <div className="sub">{fi ? "Hälytys kun day_count ≥ 28" : "Alert when day_count ≥ 28"}</div>
          </div>
        </div>
      </section>

      <WorkedStrip fi={fi} />
    </div>
  );
}
