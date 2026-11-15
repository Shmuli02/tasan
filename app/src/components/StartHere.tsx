import { useEffect, useState } from "react";

const STEPS = [
  { id: "gap", n: 1, label: "The gap", hint: "Hero number, men and women", target: "step-gap" },
  { id: "where", n: 2, label: "Where", hint: "Map, signals, no public data", target: "step-where" },
  { id: "actions", n: 3, label: "What to do", hint: "T3, then T1 and T2", target: "step-actions" },
  { id: "sim", n: 4, label: "Simulator", hint: "What-if on real baselines", target: "simulator" },
] as const;

function scrollToStep(index: number) {
  const el = document.getElementById(STEPS[index].target);
  if (el) el.scrollIntoView({ behavior: "smooth", block: "start" });
}

export function StartHere() {
  const [step, setStep] = useState<number | null>(null);
  const active = step != null;

  function go(index: number) {
    const next = Math.max(0, Math.min(STEPS.length - 1, index));
    setStep(next);
    scrollToStep(next);
  }

  function start() {
    go(0);
  }

  function stop() {
    setStep(null);
  }

  useEffect(() => {
    function onKey(e: KeyboardEvent) {
      const tag = (e.target as HTMLElement | null)?.tagName;
      if (tag === "INPUT" || tag === "TEXTAREA" || tag === "SELECT") return;
      if ((e.target as HTMLElement | null)?.getAttribute("type") === "range") return;
      if (!active) {
        if (e.key === "Enter" && (e.target as HTMLElement)?.id === "start-here-btn") return;
        return;
      }
      if (e.key === "ArrowRight" || e.key === "PageDown") {
        e.preventDefault();
        if (step != null) go(step + 1);
      } else if (e.key === "ArrowLeft" || e.key === "PageUp") {
        e.preventDefault();
        if (step != null) go(step - 1);
      } else if (e.key === "Home") {
        e.preventDefault();
        go(0);
      } else if (e.key === "End") {
        e.preventDefault();
        go(STEPS.length - 1);
      } else if (e.key === "Escape") {
        e.preventDefault();
        stop();
      } else if (e.key >= "1" && e.key <= "4") {
        e.preventDefault();
        go(Number(e.key) - 1);
      }
    }
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, [active, step]);

  return (
    <>
      <button
        id="start-here-btn"
        type="button"
        onClick={start}
        className="rounded-full bg-gold px-4 py-1.5 text-sm font-semibold text-white shadow-sm hover:bg-gold/90"
      >
        Start here
      </button>
      {active ? (
        <div className="fixed inset-x-0 top-0 z-40 border-b-2 border-navy bg-navy text-white shadow-lg">
          <div className="mx-auto flex max-w-[1600px] flex-wrap items-center gap-2 px-4 py-2">
            <p className="mr-2 hidden text-xs font-semibold uppercase tracking-[0.14em] text-gold-soft sm:block">
              2-minute path
            </p>
            <ol className="flex flex-1 flex-wrap items-center gap-1">
              {STEPS.map((s, i) => (
                <li key={s.id}>
                  <button
                    type="button"
                    onClick={() => go(i)}
                    className={`rounded-full px-3 py-1 text-sm font-semibold ${
                      i === step ? "bg-gold text-white" : "bg-white/10 text-white hover:bg-white/20"
                    }`}
                  >
                    <span className="mr-1 tabular-nums">{s.n}</span>
                    {s.label}
                    <span className="ml-1 hidden font-normal opacity-80 lg:inline">· {s.hint}</span>
                  </button>
                </li>
              ))}
            </ol>
            <div className="flex items-center gap-2">
              <button
                type="button"
                className="rounded-full border border-white/40 px-3 py-1 text-sm font-semibold disabled:opacity-40"
                onClick={() => step != null && go(step - 1)}
                disabled={step === 0}
              >
                Back
              </button>
              <button
                type="button"
                className="rounded-full bg-white px-3 py-1 text-sm font-semibold text-navy disabled:opacity-40"
                onClick={() => (step === STEPS.length - 1 ? stop() : step != null && go(step + 1))}
              >
                {step === STEPS.length - 1 ? "Done" : "Next"}
              </button>
              <button type="button" className="text-xs text-white/70 hover:text-white" onClick={stop} title="Esc">
                Close
              </button>
            </div>
            <p className="w-full text-[11px] text-white/70 sm:w-auto sm:pl-2">
              Arrow keys move between steps · 1–4 jump · Esc closes
            </p>
          </div>
        </div>
      ) : null}
      {active ? <div className="h-[4.5rem]" aria-hidden="true" /> : null}
    </>
  );
}
