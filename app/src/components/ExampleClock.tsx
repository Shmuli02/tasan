import { useEffect, useRef, useState } from "react";
import {
  ALERT_DAYS,
  DAY28,
  EXAMPLE_PATIENTS,
  WEEK6,
  WITH_ON_TIME,
  WITHOUT_ON_TIME,
  alertsFiredBy,
  dayOf,
  treated,
} from "../lib/exampleCohort";

const MS_PER_DAY = 140;
const PAUSE_MS = 1500;
const END_T = 22;

export function ExampleClock({
  lang,
  countyName,
  startAtAlert = false,
  day,
  variant = "light",
  hideControls = false,
  compact = false,
}: {
  lang: "en" | "fi";
  countyName?: string;
  startAtAlert?: boolean;
  day?: number;
  variant?: "light" | "dark";
  hideControls?: boolean;
  compact?: boolean;
}) {
  const fi = lang === "fi";
  const reduced = useReducedMotion();
  const controlled = day !== undefined;
  const [tInternal, setT] = useState(startAtAlert ? (ALERT_DAYS[0] ?? 0) : 0);
  const t = controlled ? day : tInternal;
  const [playing, setPlaying] = useState(!reduced);
  const [playedOnce, setPlayedOnce] = useState(false);
  const raf = useRef<number | null>(null);
  const acc = useRef(0);
  const last = useRef(0);
  const pauseUntil = useRef(0);
  const fired = useRef<Set<number>>(new Set());

  useEffect(() => {
    if (controlled) return;
    fired.current = new Set();
    setT(0);
    setPlayedOnce(false);
    setPlaying(!reduced);
  }, [countyName, reduced, controlled]);

  useEffect(() => {
    if (controlled || !playing || reduced) {
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
      const dt = now - last.current;
      last.current = now;
      acc.current += dt;
      const steps = Math.floor(acc.current / MS_PER_DAY);
      if (steps > 0) {
        acc.current -= steps * MS_PER_DAY;
        setT((prev) => {
          let next = Math.min(END_T, prev + steps);
          for (const ad of ALERT_DAYS) {
            if (prev < ad && next >= ad && !fired.current.has(ad)) {
              next = ad;
              fired.current.add(ad);
              pauseUntil.current = now + PAUSE_MS;
              break;
            }
          }
          if (next >= END_T) {
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
  }, [playing, reduced]);

  const alerts = alertsFiredBy(t);
  const latest = [...alerts].reverse()[0];
  const latestOpen = latest && !treated(latest, t, true) && dayOf(latest, t, true) >= DAY28;

  function onPlay() {
    if (t >= END_T || playedOnce) {
      fired.current = new Set();
      setT(0);
      setPlayedOnce(false);
      if (reduced) {
        setT(END_T);
        setPlayedOnce(true);
        return;
      }
      setPlaying(true);
      return;
    }
    setPlaying((p) => !p);
  }

  const place = countyName ? ` · ${countyName}` : "";

  const dark = variant === "dark";
  return (
    <section id="tasan-clock" className={`example-clock${dark ? " is-dark" : ""}${compact ? " is-compact" : ""}`}>
      {compact ? (
        <div className="mb-1 flex items-center gap-2">
          <span className="badge b-ex">{fi ? "ESIMERKKI" : "EXAMPLE"}</span>
          <h3 className="m-0 text-[13px] font-semibold">{fi ? "Päivän 28 kello" : "Day-28 clock"}</h3>
        </div>
      ) : (
      <div className="mb-2 flex flex-wrap items-center justify-between gap-2">
        <div className="flex flex-wrap items-center gap-2">
          <span className="badge b-ex">{fi ? "ESIMERKKI" : "EXAMPLE"}</span>
          <h3 className="m-0 text-[15px] font-semibold text-navy">{fi ? "Päivän 28 kello" : "Day-28 clock"}</h3>
        </div>
        {hideControls ? null : (
        <button type="button" className="ask-btn" style={{ padding: "8px 12px" }} onClick={onPlay}>
          {playing ? (fi ? "Tauko" : "Pause") : t >= END_T ? (fi ? "Uudelleen" : "Replay") : fi ? "Käynnistä" : "Play"}
        </button>
        )}
      </div>
      )}
      {compact ? null : (
        <>
      <p className="m-0 text-[12.5px] text-[var(--tz-ink-3)]">
        {fi
          ? `Keksitty jono, ei oikeita potilaita${place}. Havainnollistava, ei ennuste.`
          : `A made-up list, not real patients${place}. Illustrative, not a forecast.`}
      </p>
      <p className="vs-inline num">
        <span>{fi ? "Ilman Tasania" : "Without Tasan"}</span>{" "}
        <b>
          {WITHOUT_ON_TIME}/14
        </b>{" "}
        → <span>{fi ? "Tasanin kanssa" : "With Tasan"}</span>{" "}
        <b>
          {WITH_ON_TIME}/14
        </b>
        <span className="vs-note"> {fi ? "havainnollistava, ei ennuste" : "illustrative, not a forecast"}</span>
      </p>
      {alerts.length ? (
        <p className="text-[13px] font-semibold text-[var(--tz-alert)]">
          {alerts.length} {fi ? "hälytystä" : "alerts"} → {alerts.length} {fi ? "navigatoria nimetty" : "navigators assigned"}
        </p>
      ) : null}
      {latestOpen ? (
        <aside className="clock-alert mt-2 rounded-[12px] border border-[var(--tz-alert)] bg-[var(--tz-alert-bg,#F8E6D0)] p-3" role="status">
          <p className="m-0 text-[13px] font-bold uppercase tracking-wide text-[var(--tz-alert)]">{fi ? "Päivän 28 hälytys" : "Day-28 alert"}</p>
          <p className="mt-1 mb-0 text-[15px] font-semibold text-ink">
            {fi
              ? "Päivä 28, ei hoitopäätöstä. Sairaanhoitaja-navigator varaa puuttuvan CT-ajan."
              : "Day 28, no treatment decision. Nurse navigator books the missing CT."}
          </p>
        </aside>
      ) : null}
        </>
      )}
      <ul className="clock-rows mt-2">
        {EXAMPLE_PATIENTS.map((p) => {
          const d = dayOf(p, t, true);
          const done = treated(p, t, true);
          const width = Math.min(100, (d / WEEK6) * 100);
          const tone = done ? "bg-teal" : d >= DAY28 ? "bg-[var(--tz-alert)]" : d >= 21 ? "bg-[var(--tz-risk,#E6C25A)]" : "bg-[var(--tz-ok)]";
          return (
            <li key={`${countyName}-${p.id}`} className="flex items-center gap-2" style={{ minHeight: 14 }}>
              <span className="w-16 shrink-0 text-right text-[12px] tabular-nums text-[var(--tz-ink-3)]">{p.id.replace("P-", "")}</span>
              <div className="relative h-3.5 flex-1 overflow-hidden rounded-full bg-[var(--tz-line)]">
                <span className={`absolute inset-y-0 left-0 rounded-full ${tone}`} style={{ width: `${width}%` }} />
                <span className="absolute inset-y-0 w-px bg-ink/40" style={{ left: `${(DAY28 / WEEK6) * 100}%` }} />
              </div>
            </li>
          );
        })}
      </ul>
    </section>
  );
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
