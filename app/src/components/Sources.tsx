import type { Source } from "../types";
import { dataset } from "../lib/data";

export function Sources({ highlightId }: { highlightId: string | null }) {
  return (
    <section id="sources" className="rounded-2xl border border-line bg-card p-5">
      <p className="text-xs font-semibold uppercase tracking-[0.16em] text-teal">Sources</p>
      <h3 className="serif mt-1 text-xl text-ink">Every number and claim points here</h3>
      <p className="text-sm text-muted">
        {dataset.regions.meta.disclaimer}
      </p>
      <ol className="mt-4 space-y-3">
        {dataset.sources.sources.map((s, i) => (
          <li
            key={s.id}
            id={`source-${s.id}`}
            className={`rounded-xl px-3 py-3 ${highlightId === s.id ? "bg-gold-soft ring-2 ring-gold" : "bg-paper"}`}
          >
            <p className="text-sm font-semibold text-ink">
              <span className="mr-2 text-xs font-medium text-gold">{i + 1} · {s.id.replace(/^src-/, "")}</span>
              {s.title}
            </p>
            <p className="text-xs text-muted">
              {s.publisher}
              {s.year ? ` · ${s.year}` : ""}
              {s.accessed ? ` · accessed ${s.accessed}` : ""}
            </p>
            {s.url ? (
              <a href={s.url} className="break-all text-xs text-teal underline" target="_blank" rel="noreferrer">
                {s.url}
              </a>
            ) : (
              <p className="text-xs text-muted">No public URL (placeholder or internal note).</p>
            )}
            {s.note ? <p className="mt-1 text-xs leading-relaxed text-ink">{s.note}</p> : null}
          </li>
        ))}
      </ol>
      {dataset.recs.meta.disclaimer ? (
        <p className="mt-4 text-xs text-muted">{dataset.recs.meta.disclaimer}</p>
      ) : null}
      {dataset.counties.attribution ? (
        <p className="mt-2 text-xs text-muted">{dataset.counties.attribution}</p>
      ) : null}
    </section>
  );
}

export function openSource(id: string, setHighlight: (id: string) => void) {
  setHighlight(id);
  const el = document.getElementById(`source-${id}`);
  if (el) el.scrollIntoView({ behavior: "smooth", block: "center" });
}

export type { Source };
