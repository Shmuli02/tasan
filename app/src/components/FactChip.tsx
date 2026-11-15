import { useEffect, useRef, useState } from "react";
import { factById, sourceLabel, statement } from "../lib/facts";

export function FactChip({
  id,
  lang,
  label,
  sourcesOn = true,
  className = "",
}: {
  id: string;
  lang: "en" | "fi";
  label?: string;
  sourcesOn?: boolean;
  className?: string;
}) {
  const [open, setOpen] = useState(false);
  const ref = useRef<HTMLSpanElement | null>(null);
  const fact = factById(id);
  useEffect(() => {
    if (!open) return;
    function onPtr(e: PointerEvent) {
      if (ref.current && !ref.current.contains(e.target as Node)) setOpen(false);
    }
    window.addEventListener("pointerdown", onPtr);
    return () => window.removeEventListener("pointerdown", onPtr);
  }, [open]);
  if (!fact) return null;
  const fi = lang === "fi";
  const chip = label ?? sourceLabel(fact, lang);
  return (
    <span ref={ref} className={`relative inline-flex ${className}`}>
      <button
        type="button"
        className={`src${sourcesOn ? "" : " src-dot"}`}
        onClick={() => setOpen((v) => !v)}
        aria-expanded={open}
        aria-label={chip}
        title={chip}
      >
        {sourcesOn ? chip : ""}
      </button>
      {open ? (
        <div className="absolute left-0 top-[calc(100%+6px)] z-40 w-[min(22rem,calc(100vw-2rem))] rounded-[12px] border border-[var(--tz-line)] bg-white p-3 text-left shadow-[var(--tz-sh-3)]">
          <p className="m-0 text-[13px] leading-snug text-[var(--tz-ink)]">{statement(fact, fi ? "fi" : "en")}</p>
          {fact.source_table ? (
            <p className="mt-2 text-[11.5px] font-semibold uppercase tracking-wide text-[var(--tz-ink-3)]">{fact.source_table}</p>
          ) : null}
          {fact.source_url ? (
            <a className="mt-1 inline-block text-[13px] font-semibold text-[var(--tz-teal-700)] underline" href={fact.source_url} target="_blank" rel="noreferrer">
              {fi ? "Avaa lähde" : "Open source"}
            </a>
          ) : null}
          {fact.caveat ? <p className="mt-2 text-[12px] leading-snug text-[var(--tz-ink-2)]">{fact.caveat}</p> : null}
          <p className="mt-2 font-[var(--tz-font-mono)] text-[11px] text-[var(--tz-ink-3)]">{fact.id}</p>
        </div>
      ) : null}
    </span>
  );
}
