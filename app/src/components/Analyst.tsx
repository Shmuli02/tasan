import { useMemo, useState } from "react";
import { Cite, Goal3Badge } from "./Cite";
import { answerQuery, sourceLine, suggestedQuestions, type AnalystAnswer } from "../lib/analyst";
import { featuredRecIds, recById, regionById } from "../lib/data";

export function Analyst({
  selectedId,
  onOpenSource,
  onSelectRegion,
  onlineEnabled,
}: {
  selectedId: string | null;
  onOpenSource: (id: string) => void;
  onSelectRegion: (id: string) => void;
  onlineEnabled: boolean;
}) {
  const suggestions = useMemo(() => suggestedQuestions(selectedId), [selectedId]);
  const [query, setQuery] = useState(suggestions[0]?.query ?? "");
  const [answer, setAnswer] = useState<AnalystAnswer>(() => answerQuery(suggestions[0]?.query ?? "", selectedId));

  function ask(q: string) {
    setQuery(q);
    setAnswer(answerQuery(q, selectedId));
  }

  return (
    <section id="analyst" className="rounded-2xl border border-line bg-card p-5">
      <div className="flex flex-wrap items-start justify-between gap-2">
        <div>
          <p className="text-xs font-semibold uppercase tracking-[0.16em] text-teal">AI analyst · offline</p>
          <h3 className="serif mt-1 text-xl text-ink">Ask about the gap, a county, or an action</h3>
          <p className="text-sm text-muted">
            Deterministic retrieval over the bundled JSON. Every answer carries source citations. Works with no network.
          </p>
        </div>
        {onlineEnabled ? (
          <span className="rounded-full bg-teal-soft px-2.5 py-1 text-[11px] font-semibold uppercase tracking-wider text-teal-deep">
            Online LLM available
          </span>
        ) : isLocalServe() ? (
          <span className="rounded-full bg-teal-soft px-2.5 py-1 text-[11px] font-semibold uppercase tracking-wider text-teal-deep">
            Offline mode
          </span>
        ) : null}
      </div>
      {onlineEnabled ? (
        <p className="mt-2 rounded-lg bg-gold-soft px-3 py-2 text-xs text-gold">
          Online LLM mode is on, but no endpoint is used unless configured at build time. The offline answer is shown so the
          demo cannot fail on stage.
        </p>
      ) : null}
      <div className="mt-3 flex flex-wrap gap-1.5">
        {suggestions.map((s) => (
          <button
            key={s.id}
            type="button"
            onClick={() => ask(s.query)}
            className="rounded-full border border-line bg-paper px-3 py-1 text-xs text-ink hover:border-teal hover:bg-teal-soft"
          >
            {s.label}
          </button>
        ))}
      </div>
      <form
        className="mt-3 flex gap-2"
        onSubmit={(e) => {
          e.preventDefault();
          ask(query);
        }}
      >
        <input
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder="e.g. How does Kainuu compare?  /  Mitä Goal 3 vaatii?"
          className="flex-1 rounded-xl border border-line bg-paper px-3 py-2 text-sm text-ink outline-none focus:border-teal"
        />
        <button type="submit" className="rounded-xl bg-navy px-4 py-2 text-sm font-semibold text-white hover:bg-teal-deep">
          Ask
        </button>
      </form>
      <article className="mt-4">
        <h4 className="font-semibold text-ink">{answer.title}</h4>
        {answer.paragraphs.map((p, i) => (
          <p key={i} className="mt-2 text-sm leading-relaxed text-ink">
            {p}
          </p>
        ))}
        {answer.bullets && answer.bullets.length > 0 ? (
          <ul className="mt-2 list-disc space-y-1 pl-5 text-sm text-ink">
            {answer.bullets.map((b, i) => (
              <li key={i}>{b}</li>
            ))}
          </ul>
        ) : null}
        {answer.rec_ids?.length ? (
          <div className="mt-3 flex flex-wrap gap-2">
            {answer.rec_ids.map((id) => {
              const r = recById(id);
              if (!r) return null;
              return (
                <span key={id} className="inline-flex items-center gap-1 rounded-full bg-paper px-2 py-1 text-[11px]">
                  {r.title}
                  <Goal3Badge show={featuredRecIds().includes(id) && Boolean(r.goal3_indicator) && !r.optional_goal2 && r.goal !== "2"} />
                </span>
              );
            })}
          </div>
        ) : null}
        {answer.region_ids?.length ? (
          <div className="mt-2 flex flex-wrap gap-1">
            {answer.region_ids.map((id) => (
              <button
                key={id}
                type="button"
                className="text-xs text-teal underline"
                onClick={() => onSelectRegion(id)}
              >
                Show {regionById(id)?.name ?? id}
              </button>
            ))}
          </div>
        ) : null}
        <div className="mt-3 border-t border-line pt-2">
          <p className="text-[11px] font-semibold uppercase tracking-wider text-muted">Sources</p>
          {answer.source_ids.length ? (
            <ul className="mt-1 space-y-1 text-xs text-muted">
              {answer.source_ids.map((id) => (
                <li key={id}>
                  <Cite ids={[id]} onOpen={onOpenSource} /> {sourceLine(id)}
                </li>
              ))}
            </ul>
          ) : (
            <p className="mt-1 text-xs text-muted">No source matched this answer — it is a navigation hint only.</p>
          )}
        </div>
      </article>
    </section>
  );
}

function isLocalServe(): boolean {
  if (typeof window === "undefined") return false;
  const h = window.location.hostname;
  return window.location.protocol === "file:" || h === "localhost" || h === "127.0.0.1";
}
