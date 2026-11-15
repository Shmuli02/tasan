import { useEffect, useMemo, useRef, useState } from "react";
import sim from "../content/charts/sim_lapland.json";
import {
  ALERT_DAYS,
  DAY28,
  EXAMPLE_PATIENTS,
  PILOT_DAYS,
  STEPS,
  WEEK6,
  WITH_ON_TIME,
  WITHOUT_ON_TIME,
  alertsFiredBy,
  dayOf,
  onTimeCount,
  stepIndex,
  treated,
  exampleFeedEvents,
  feedEventsUpTo,
  type ExPatient,
} from "../lib/exampleCohort";
import { ExampleClock } from "./ExampleClock";
import { PolkuLink } from "./PolkuLink";

const MS_1X = 480;
const ALERT_COPY = {
  en: {
    ct: "Day 28, no treatment decision. Nurse navigator books the missing CT.",
    biopsy: "Day 28, no treatment decision. Nurse navigator chases the biopsy result.",
    mdt: "Day 28, no treatment decision. Nurse navigator books the MDT slot.",
  },
  fi: {
    ct: "Päivä 28, ei hoitopäätöstä. Sairaanhoitaja-navigator varaa puuttuvan CT-ajan.",
    biopsy: "Päivä 28, ei hoitopäätöstä. Sairaanhoitaja-navigator kiirehtii biopsian vastausta.",
    mdt: "Päivä 28, ei hoitopäätöstä. Sairaanhoitaja-navigator varaa MDT-ajan.",
  },
};

function ringColor(day: number, done: boolean): string {
  if (done) return "#4CC2A4";
  if (day >= 42) return "#FF6B5A";
  if (day >= 28) return "#F2A65A";
  if (day >= 21) return "#E6C25A";
  return "#4CC2A4";
}

function DayRing({ day, done, size = 28, stroke = 4 }: { day: number; done: boolean; size?: number; stroke?: number }) {
  const r = (size - stroke) / 2;
  const c = 2 * Math.PI * r;
  const pct = Math.min(1, day / WEEK6);
  return (
    <svg className="ring" width={size} height={size} viewBox={`0 0 ${size} ${size}`} aria-hidden>
      <circle cx={size / 2} cy={size / 2} r={r} fill="none" stroke="#2A3B60" strokeWidth={stroke} />
      <circle
        cx={size / 2}
        cy={size / 2}
        r={r}
        fill="none"
        stroke={ringColor(day, done)}
        strokeWidth={stroke}
        strokeLinecap="round"
        strokeDasharray={`${(pct * c).toFixed(1)} ${c.toFixed(1)}`}
        transform={`rotate(-90 ${size / 2} ${size / 2})`}
      />
    </svg>
  );
}

function liveStartFromUrl() {
  if (typeof window === "undefined") return null;
  const q = new URLSearchParams(window.location.search);
  const clock = q.get("clock");
  if (clock === "end") {
    return { who: EXAMPLE_PATIENTS[0], at: 22, end: true as const };
  }
  if (clock !== "alert") return null;
  const who = EXAMPLE_PATIENTS.find((p) => p.alertKind === "ct") ?? EXAMPLE_PATIENTS[0];
  const at = DAY28 - who.day0;
  return { who, at, end: false as const };
}

export function TasanLive({ lang }: { lang: "en" | "fi" }) {
  const fi = lang === "fi";
  const reduced = useReducedMotion();
  const start = liveStartFromUrl();
  const [t, setT] = useState(start ? start.at : 0);
  const [playing, setPlaying] = useState(start ? false : !reduced);
  const [speed, setSpeed] = useState<1 | 8 | 32>(1);
  const [playedOnce, setPlayedOnce] = useState(Boolean(start?.end));
  const [pausedForAlert, setPausedForAlert] = useState(false);
  const [selectedId, setSelectedId] = useState(start ? start.who.id : "P-0207");
  const [feed, setFeed] = useState<{ t: number; clock: string; text: string; alert?: boolean; id: string }[]>(() => {
    const at = start ? start.at : 0;
    return feedEventsUpTo(at, fi, clockLabel);
  });
  const firedEvents = useRef<Set<string>>(new Set(feedEventsUpTo(start ? start.at : 0, fi, clockLabel).map((e) => e.id)));
  const raf = useRef<number | null>(null);
  const acc = useRef(0);
  const last = useRef(0);
  const pauseUntil = useRef(0);
  const firedAlerts = useRef<Set<number>>(new Set(start ? [start.at] : []));
  const [toast, setToast] = useState<string | null>(null);
  const [holdForContinue, setHoldForContinue] = useState(false);
  const holdRef = useRef(false);
  function continuePlayback() {
    holdRef.current = false;
    pauseUntil.current = 0;
    setHoldForContinue(false);
    setPausedForAlert(false);
  }
  const endT = 22;
  useEffect(() => {
    if (!toast) return;
    const id = window.setTimeout(() => setToast(null), 2000);
    return () => window.clearTimeout(id);
  }, [toast]);
  useEffect(() => {
    const q = new URLSearchParams(window.location.search);
    if (q.get("clock") === "alert") {
      const who = EXAMPLE_PATIENTS.find((p) => p.alertKind === "ct") ?? EXAMPLE_PATIENTS[0];
      const at = DAY28 - who.day0;
      firedAlerts.current = new Set([at]);
      setT(at);
      setPlaying(false);
      holdRef.current = true;
      setHoldForContinue(true);
      setPausedForAlert(true);
      setSelectedId(who.id);
      firedEvents.current = new Set(feedEventsUpTo(at, fi, clockLabel).map((e) => e.id));
      setFeed(feedEventsUpTo(at, fi, clockLabel));
    }
  }, []);

  const withOn = onTimeCount(t, true);
  const alerts = alertsFiredBy(t);
  const openAlerts = alerts.filter((p) => !treated(p, t, true));
  const selected = EXAMPLE_PATIENTS.find((p) => p.id === selectedId) ?? EXAMPLE_PATIENTS[0];

  useEffect(() => {
    if (openAlerts[0] && !playing) {
      /* keep selection */
    } else if (openAlerts[0]) {
      setSelectedId(openAlerts[openAlerts.length - 1].id);
    }
  }, [openAlerts.length]); // eslint-style: length only

  useEffect(() => {
    if (!playing || reduced) {
      if (raf.current) cancelAnimationFrame(raf.current);
      return;
    }
    last.current = performance.now();
    acc.current = 0;
    const tick = (now: number) => {
      if (now < pauseUntil.current) {
        raf.current = requestAnimationFrame(tick);
        return;
      }
      if (pauseUntil.current) {
        pauseUntil.current = 0;
        setPausedForAlert(false);
      }
      const dt = now - last.current;
      last.current = now;
      const ms = MS_1X / speed;
      acc.current += dt;
      const steps = Math.floor(acc.current / ms);
      if (steps > 0) {
        acc.current -= steps * ms;
        setT((prev) => {
          let next = Math.min(endT, prev + steps);
          for (const ad of ALERT_DAYS) {
            if (prev < ad && next >= ad && !firedAlerts.current.has(ad)) {
              next = ad;
              firedAlerts.current.add(ad);
              holdRef.current = true;
              pauseUntil.current = Number.POSITIVE_INFINITY;
              setHoldForContinue(true);
              setPausedForAlert(true);
              const who = EXAMPLE_PATIENTS.find((p) => p.alertKind && DAY28 - p.day0 === ad);
              if (who) {
                setSelectedId(who.id);
                const slot = who.blocker ?? (fi ? "ei hoitopäätöstä" : "no treatment decision");
                setToast(
                  fi
                    ? `Päivä 28 · ${who.id} · ${slot} → navigator nimetty`
                    : `Day 28 · ${who.id} · ${slot} → navigator assigned`,
                );
              }
              break;
            }
          }
          const arrived = exampleFeedEvents().filter((e) => e.t > prev && e.t <= next && !firedEvents.current.has(e.id));
          if (arrived.length) {
            for (const e of arrived) firedEvents.current.add(e.id);
            setFeed((f) =>
              [
                ...[...arrived].reverse().map((e) => ({
                  t: e.t,
                  clock: clockLabel(e.t),
                  text: fi ? e.fi : e.en,
                  alert: e.alert,
                  id: e.id,
                })),
                ...f,
              ].slice(0, 24),
            );
          }
          if (next >= endT) {
            setPlaying(false);
            setPlayedOnce(true);
          }
          return next;
        });
      }
      raf.current = requestAnimationFrame(tick);
    };
    raf.current = requestAnimationFrame(tick);
    return () => {
      if (raf.current) cancelAnimationFrame(raf.current);
    };
  }, [playing, speed, reduced, fi, endT]);

  useEffect(() => {
    const onKey = (e: KeyboardEvent) => {
      if (!holdRef.current) return;
      const tag = (e.target as HTMLElement | null)?.tagName;
      if (tag === "INPUT" || tag === "TEXTAREA") return;
      if (e.key === " " || e.key === "ArrowRight") {
        e.preventDefault();
        continuePlayback();
        setPlaying(true);
      }
    };
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, []);

  function resetAndPlay() {
    holdRef.current = false;
    pauseUntil.current = 0;
    setHoldForContinue(false);
    setPausedForAlert(false);
    firedAlerts.current = new Set();
    const initial = feedEventsUpTo(0, fi, clockLabel);
    firedEvents.current = new Set(initial.map((e) => e.id));
    setFeed(initial);
    setT(0);
    setPlayedOnce(false);
    setPausedForAlert(false);
    setSelectedId("P-0207");
    if (reduced) {
      setT(endT);
      setPlayedOnce(true);
      setPlaying(false);
      firedAlerts.current = new Set(ALERT_DAYS);
      const all = feedEventsUpTo(endT, fi, clockLabel);
      firedEvents.current = new Set(all.map((e) => e.id));
      setFeed(all);
      return;
    }
    setPlaying(true);
  }

  function togglePlay() {
    if (t >= endT || playedOnce && t >= endT) {
      resetAndPlay();
      return;
    }
    setPlaying((p) => !p);
  }

  const selDay = dayOf(selected, t, true);
  const selDone = treated(selected, t, true);
  const mid = sim.scenarios.mid.pct_le42_from_referral;
  const base = sim.baseline_pct_le42_from_referral;
  const low = sim.scenarios.low.delta_pct_le42_from_referral;
  const high = sim.scenarios.high.delta_pct_le42_from_referral;

  const blockers = useMemo(() => countBlockers(t), [t]);

  return (
    <div className="live-root">
      <div className="lhdr">
        <h1>Tasan Live</h1>
        <div className="ctxl">
          {fi ? "Lappi · keuhkopolku · navigator-konsoli" : "Lapland · lung pathway navigator console"}
        </div>
        <span className="live">
          <span className="pulse" />
          LIVE
        </span>
        <span className="badge exd">{fi ? "ESIMERKKI · simuloidut potilaat" : "EXAMPLE · simulated patients"}</span>
        <div className="vs-banner" aria-label={fi ? "Esimerkin lopputulos, havainnollistava, ei ennuste" : "Example outcome, illustrative, not a forecast"}>
          <span className="vs-k">{fi ? "Ilman" : "Without"}</span>
          <b className="num">{WITHOUT_ON_TIME}/{EXAMPLE_PATIENTS.length}</b>
          <span className="vs-arrow">→</span>
          <span className="vs-k">{fi ? "Tasanin kanssa" : "With Tasan"}</span>
          <b className="num">{WITH_ON_TIME}/{EXAMPLE_PATIENTS.length}</b>
        </div>
        <div className="play">
          <button type="button" className="pb" onClick={togglePlay} aria-label={playing ? (fi ? "Tauko" : "Pause") : t >= endT ? (fi ? "Uudelleen" : "Replay") : fi ? "Käynnistä" : "Play"}>
            {playing && !pausedForAlert ? (
              <svg className="i" viewBox="0 0 24 24">
                <rect x="14" y="4" width="4" height="16" rx="1" />
                <rect x="6" y="4" width="4" height="16" rx="1" />
              </svg>
            ) : t >= endT ? (
              <svg className="i" viewBox="0 0 24 24">
                <path d="M3 12a9 9 0 1 0 9-9 9.75 9.75 0 0 0-6.74 2.74L3 8" />
                <path d="M3 3v5h5" />
              </svg>
            ) : (
              <svg className="i" viewBox="0 0 24 24">
                <path d="m7 4 12 8-12 8z" fill="currentColor" stroke="none" />
              </svg>
            )}
          </button>
          <div className="spd" role="group">
            {([1, 8, 32] as const).map((s) => (
              <button key={s} type="button" className={speed === s ? "on" : ""} onClick={() => setSpeed(s)}>
                {s}×
              </button>
            ))}
          </div>
          <div className="scrub">
            <div className="bar">
              <i style={{ width: `${(t / PILOT_DAYS) * 100}%` }} />
              <u style={{ left: `${(28 / PILOT_DAYS) * 100}%` }} />
              <b style={{ left: `${(t / PILOT_DAYS) * 100}%` }} />
            </div>
            <div className="lab">
              <span>
                {fi ? "Pilottipäivä" : "Pilot day"} <b>{t}</b>
              </span>
              <span>stop/go D90</span>
            </div>
          </div>
        </div>
      </div>

      {toast ? <div className="live-toast" role="status">{toast}</div> : null}
      {holdForContinue ? (
        <div className="live-continue">
          <button type="button" onClick={() => { continuePlayback(); setPlaying(true); }}>
            {fi ? "Jatka" : "Continue"}
          </button>
          <span>{fi ? "Välilyönti tai →" : "Space or →"}</span>
        </div>
      ) : null}

      {playedOnce && t >= endT ? (
        <div className="end-banner">
          <div>
            <b>{WITHOUT_ON_TIME}/14</b>
            <span className="vs-arrow">→</span>
            <b>{WITH_ON_TIME}/14</b>
            <span> {fi ? "aloitti hoidon 6 viikossa (havainnollistava)" : "started within 6 weeks (illustrative)"}</span>
          </div>
          <PolkuLink page="demo" className="polku-end">
            {fi ? "Simuloidut kellot. Polku ajaa ne oikeasti" : "Simulated clocks. Polku runs them for real"}
          </PolkuLink>
          <button type="button" onClick={resetAndPlay}>{fi ? "Toista" : "Replay"}</button>
        </div>
      ) : null}

      <div className="lgrid">
        <div className="kpirow">
          <div className="dk">
            <div className="l">{fi ? "Aktiiviset potilaat" : "Active patients"}</div>
            <div className="v">14</div>
            <Spark pts={[4, 6, 10, 8, 12, 14]} color="#5CC4C4" />
            <div className="s">
              <span className="up">▲ 3</span> {fi ? "tällä viikolla" : "this week"}
            </div>
          </div>
          <div className="dk">
            <div className="l">{fi ? "Aikataulussa tähän päivään (Tasanin kanssa)" : "On track so far (with Tasan)"}</div>
            <div className="v">
              {withOn}
              <small>/14</small>
            </div>
            <Spark pts={[2, 3, 4, 6, 7, withOn]} color="#4CC2A4" />
            <div className="s">
              {fi
                ? `Tässä ajossa tähän asti · esimerkin lopputulos ${WITH_ON_TIME}/14`
                : `So far this run · example outcome ${WITH_ON_TIME}/14`}
            </div>
          </div>
          <div className="dk">
            <div className="l">{fi ? "Päivän 28 hälytykset auki" : "Day-28 alerts open"}</div>
            <div className="v" style={{ color: "#F2A65A" }}>
              {openAlerts.length}
            </div>
            <Spark pts={[0, 0, 1, 2, 3, openAlerts.length]} color="#F2A65A" />
            <div className="s">
              <span className="am">
                {alerts.length} {fi ? "hälytystä" : "alerts"} → {alerts.length} {fi ? "navigatoria nimetty" : "navigators assigned"}
              </span>
            </div>
          </div>
          <div className="dk">
            <div className="l">{fi ? "Mallin tulos, lähete → hoito ≤6 vk" : "Model output, referral → treatment ≤6 wk"}</div>
            <div className="v" style={{ fontSize: 22, alignSelf: "center" }}>
              ~{base.median.toFixed(0)}
              <small>%</small>
            </div>
            <div className="s" style={{ gridColumn: "1 / 3" }}>
              <span className="badge exd" style={{ marginRight: 6 }}>
                MODEL OUTPUT
              </span>
              {fi
                ? `Lappi noin ${base.median.toFixed(0)} % (${base.p2_5.toFixed(0)}–${base.p97_5.toFixed(0)}); mid what-if noin ${mid.median.toFixed(0)} % (${mid.p2_5.toFixed(0)}–${mid.p97_5.toFixed(0)}). Ei ennuste.`
                : `Lapland about ${base.median.toFixed(0)}% (${base.p2_5.toFixed(0)}–${base.p97_5.toFixed(0)}); mid what-if about ${mid.median.toFixed(0)}% (${mid.p2_5.toFixed(0)}–${mid.p97_5.toFixed(0)}). Not a forecast.`}
            </div>
          </div>
        </div>

        <div className="dcard ptab">
          <div className="hd">
            <h3>
              <svg className="i" viewBox="0 0 24 24">
                <path d="M16 21v-2a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v2" />
                <circle cx="9" cy="7" r="4" />
                <path d="M22 21v-2a4 4 0 0 0-3-3.87M16 3.13a4 4 0 0 1 0 7.75" />
              </svg>
              {fi ? "Potilaat kellossa" : "Patients on the clock"}
            </h3>
            <span className="mut">
              {fi ? "riskin mukaan" : "sorted by risk"} · {EXAMPLE_PATIENTS.length} {fi ? "potilasta" : "patients"}
            </span>
          </div>
          <div className="ptab-scroll">
            <table>
              <thead>
                <tr>
                  <th />
                  <th>{fi ? "Potilas" : "Patient"}</th>
                  <th>{fi ? "Päivä" : "Day"}</th>
                  <th>{fi ? "Vaihe" : "Pathway step"}</th>
                  <th>{fi ? "Este" : "Blocker"}</th>
                  <th>Navigator</th>
                  <th>{fi ? "Tila" : "Status"}</th>
                </tr>
              </thead>
              <tbody>
                {sortPatients(t).map((p) => {
                  const d = dayOf(p, t, true);
                  const done = treated(p, t, true);
                  const si = stepIndex(p, t, true);
                  const alerted = p.alertKind && d >= DAY28 && !done;
                  const status = done
                    ? { cls: "ok", en: "Treated", fi: "Hoidettu" }
                    : alerted
                      ? { cls: "al", en: "Alert", fi: "Hälytys" }
                      : d >= 35
                        ? { cls: "cr", en: "At risk", fi: "Riski" }
                        : d >= 21
                          ? { cls: "risk", en: "Watch", fi: "Seuranta" }
                          : { cls: "ok", en: "On track", fi: "Aikataulussa" };
                  return (
                    <tr
                      key={p.id}
                      className={selectedId === p.id ? "sel" : ""}
                      onClick={() => setSelectedId(p.id)}
                    >
                      <td>
                        <DayRing day={d} done={done} />
                      </td>
                      <td className="id">{p.id}</td>
                      <td>D{d}</td>
                      <td>
                        <span className="steps">
                          {STEPS.map((_, i) => (
                            <i key={i} className={i < si ? "d" : i === si ? "c" : ""} />
                          ))}
                        </span>
                        <span className="stx">{fi ? stepFi(STEPS[si]) : STEPS[si]}</span>
                      </td>
                      <td>
                        {p.blocker && !done ? (
                          <span className="blk" style={{ color: alerted ? "#F2A65A" : "#E6C25A" }}>
                            {p.blocker}
                          </span>
                        ) : (
                          "—"
                        )}
                      </td>
                      <td>
                        <span className="nav">
                          <i>{p.nav ?? "+"}</i>
                          {p.nav ? "Navigator" : fi ? "Ei nimetty" : "Unassigned"}
                        </span>
                      </td>
                      <td>
                        <span className={`st ${status.cls}`}>{fi ? status.fi : status.en}</span>
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        </div>

        <div className="acol">
          <div className="dcard">
            <div className="hd">
              <h3>
                {fi ? "Päivän 28 hälytys" : "Day 28 alert"}
              </h3>
              <span className="mut">{clockLabel(t)}</span>
            </div>
            <div className="focus">
              <BigRing day={selDay} done={selDone} />
              <div>
                <div className="who">{selected.id}</div>
                <div className="why">
                  {selected.alertKind && selDay >= DAY28 && !selDone
                    ? ALERT_COPY[fi ? "fi" : "en"][selected.alertKind]
                    : selDone
                      ? ""
                      : fi
                        ? "Kaikki potilaat ovat vielä ennen päivää 28, tai navigator on jo toiminut."
                        : "All patients still before day 28, or the navigator has already acted."}
                </div>
                {selected.alertKind && selDay >= DAY28 ? (
                  <div className="acts">
                    <span className="btn pri">{fi ? "Nimeä navigator" : "Assign navigator"}</span>
                    <span className="btn gh">{fi ? "Varaa CT-aika" : "Request CT slot"}</span>
                  </div>
                ) : null}
              </div>
            </div>
          </div>
          <div className="dcard" style={{ flex: 1, minHeight: 0 }}>
            <div className="hd">
              <h3>{fi ? "Hälytysjono" : "Alert queue"}</h3>
              <span className="mut">
                {openAlerts.length} {fi ? "auki" : "open"}
              </span>
            </div>
            {openAlerts.length === 0 ? (
              <div className="mut">{t === 0 ? (fi ? "Ei hälytyksiä ennen päivää 28." : "No alerts before day 28.") : fi ? "Ei avoimia hälytyksiä." : "No open alerts."}</div>
            ) : (
              openAlerts.map((p) => (
                <div className="arow" key={p.id} onClick={() => setSelectedId(p.id)}>
                  <div className="bar" style={{ background: "#F2A65A" }} />
                  <div>
                    <div className="t1">
                      {p.id}{" "}
                      <span className="dchip" style={{ color: "#F2A65A", background: "rgba(242,166,90,.16)" }}>
                        {fi ? "PÄIVÄ" : "DAY"} {dayOf(p, t, true)}
                      </span>
                    </div>
                    <div className="t2">{p.blocker ?? (fi ? "Ei hoitopäätöstä" : "No treatment decision")}</div>
                  </div>
                  <span className="btn gh">{fi ? "Nimeä" : "Assign"}</span>
                </div>
              ))
            )}
          </div>
        </div>

        <div className="dcard blocks">
          <div className="dcard">
            <div className="hd">
              <h3>{fi ? "Esteet nyt" : "Blockers now"}</h3>
              <span className="mut">{fi ? "ESIMERKKI" : "EXAMPLE"} · {fi ? "potilaat" : "patients"}</span>
            </div>
            {blockers.map((b) => (
              <div className="hb" key={b.label}>
                <span>{b.label}</span>
                <div className="bt">
                  <i style={{ width: `${(b.n / 5) * 100}%`, background: b.color }} />
                </div>
                <b>{b.n}</b>
              </div>
            ))}
          </div>
          <div className="dcard">
            <div className="hd">
              <h3>{fi ? "Hoidettu 6 viikossa" : "Treated within 6 weeks"}</h3>
              <span className="mut">{fi ? "ESIMERKKI" : "EXAMPLE"} · {fi ? "viikoittain %" : "weekly %"}</span>
            </div>
            <ExampleClock lang={lang} day={t} variant="dark" hideControls compact />
          </div>
        </div>

        <div className="dcard trend">
          <div className="hd">
            <h3>{fi ? "Missä aika kuluu" : "Where time is lost"}</h3>
            <span className="mut">{fi ? "ESIMERKKI" : "EXAMPLE"} · {fi ? "mediaanipäivät" : "median days"}</span>
          </div>
          {[
            ["Referral → CT", 6],
            ["CT → biopsy", 9],
            ["Biopsy → MDT", 11],
            ["MDT → treatment", 7],
          ].map(([lab, n]) => (
            <div className="hb" key={String(lab)}>
              <span>{lab}</span>
              <div className="bt">
                <i style={{ width: `${(Number(n) / 12) * 100}%`, background: "#5CC4C4" }} />
              </div>
              <b>{n}</b>
            </div>
          ))}
          <p className="mut model-note" style={{ marginTop: 6 }}>
            {fi
              ? `Mallin tulos, Lappi (low–high): +${low.median.toFixed(0)}–${high.median.toFixed(0)} yksikköä.`
              : `Model output, Lapland (low–high): +${low.median.toFixed(0)}–${high.median.toFixed(0)} pp.`}
          </p>
        </div>

        <div className="dcard feed">
          <div className="hd">
            <h3>{fi ? "Tapahtumavirta" : "Event feed"}</h3>
            <span className="mut">{fi ? "ESIMERKKI" : "EXAMPLE"}</span>
          </div>
          <div className="feed-body">
            {feed.length === 0 ? (
              <div className="ev">
                <span className="tm">00:00:00</span>
                <span className="dt" style={{ background: "#5CC4C4" }} />
                <span>{fi ? "Konsoli valmis · kaikki potilaat ennen päivää 28" : "Console ready · all patients start before day 28"}</span>
              </div>
            ) : null}
            {feed.map((e, i) => (
              <div key={e.id} className={`ev${e.alert ? " al new" : ""} ${i === 0 ? "new" : ""}`}>
                <span className="tm">{e.clock}</span>
                <span className="dt" style={{ background: e.alert ? "#F2A65A" : "#5CC4C4" }} />
                <span>
                  {e.alert ? <b className="a">{e.text}</b> : e.text}
                </span>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}

function BigRing({ day, done }: { day: number; done: boolean }) {
  const size = 128;
  const stroke = 11;
  const r = (size - stroke) / 2;
  const c = 2 * Math.PI * r;
  const pct = Math.min(1, day / WEEK6);
  const col = ringColor(day, done);
  return (
    <svg className="day-ring" width={size} height={size} viewBox={`0 0 ${size} ${size}`} aria-hidden>
      <circle cx={size / 2} cy={size / 2} r={r} fill="none" stroke="#2A3B60" strokeWidth={stroke} />
      <circle
        cx={size / 2}
        cy={size / 2}
        r={r}
        fill="none"
        stroke={col}
        strokeWidth={stroke}
        strokeLinecap="round"
        strokeDasharray={`${pct * c} ${c}`}
        transform={`rotate(-90 ${size / 2} ${size / 2})`}
        style={{ filter: `drop-shadow(0 0 8px ${col})`, transition: "stroke-dasharray 160ms linear, stroke 160ms linear" }}
      />
      <text x="50%" y="48%" textAnchor="middle" fill="#fff" fontFamily="JetBrains Mono" fontSize="28" fontWeight="700">
        D{day}
      </text>
      <text x="50%" y="64%" textAnchor="middle" fill="#A9B4C8" fontFamily="Inter" fontSize="11">
        of 42 · 6 wk
      </text>
    </svg>
  );
}

function Spark({ pts, color }: { pts: number[]; color: string }) {
  const max = Math.max(...pts, 1);
  const min = 0;
  const w = 92;
  const h = 34;
  const xs = pts.map((_, i) => 2 + (i * (w - 4)) / (pts.length - 1));
  const ys = pts.map((v) => h - 5 - ((v - min) / (max - min || 1)) * (h - 10));
  const d = xs.map((x, i) => `${i ? "L" : "M"}${x.toFixed(1)},${ys[i].toFixed(1)}`).join(" ");
  return (
    <svg className="spk" width={w} height={h}>
      <path d={d} fill="none" stroke={color} strokeWidth="2" strokeLinejoin="round" />
      <circle cx={xs[xs.length - 1]} cy={ys[ys.length - 1]} r="3" fill={color} />
    </svg>
  );
}

function sortPatients(t: number): ExPatient[] {
  return EXAMPLE_PATIENTS.slice().sort((a, b) => {
    const da = treated(a, t, true) ? 0 : dayOf(a, t, true);
    const db = treated(b, t, true) ? 0 : dayOf(b, t, true);
    return db - da;
  });
}

function countBlockers(t: number) {
  const rows = [
    { label: "CT slot", color: "#F2A65A", n: 0 },
    { label: "Biopsy", color: "#E6C25A", n: 0 },
    { label: "MDT slot", color: "#FF6B5A", n: 0 },
    { label: "PET-CT", color: "#5CC4C4", n: 0 },
  ];
  for (const p of EXAMPLE_PATIENTS) {
    if (treated(p, t, true) || !p.blocker) continue;
    const row = rows.find((r) => p.blocker && p.blocker.startsWith(r.label.split(" ")[0]));
    if (row) row.n += 1;
  }
  return rows;
}

function stepFi(s: string): string {
  return ({ Referral: "Lähete", Imaging: "Kuvantaminen", Biopsy: "Biopsia", MDT: "MDT", Treatment: "Hoito" } as Record<string, string>)[s] ?? s;
}

function clockLabel(day: number): string {
  const h = 8 + (day % 10);
  const m = (day * 7) % 60;
  const s = (day * 13) % 60;
  return `${String(h).padStart(2, "0")}:${String(m).padStart(2, "0")}:${String(s).padStart(2, "0")}`;
}

function useReducedMotion(): boolean {
  const [reduced, setReduced] = useState(false);
  useEffect(() => {
    const mq = window.matchMedia("(prefers-reduced-motion: reduce)");
    const apply = () => setReduced(mq.matches);
    apply();
    mq.addEventListener("change", apply);
    return () => mq.removeEventListener("change", apply);
  }, []);
  return reduced;
}
