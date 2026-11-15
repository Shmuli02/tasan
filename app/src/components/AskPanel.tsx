import { useEffect, useMemo, useRef, useState, type FormEvent } from "react";
import { factById, sourcedFactCount, sourceLabel } from "../lib/facts";
import { answerQuestion, detectQuestionLang, isActionQuestion, isBriefQuestion, isSurvivalQuestion, isWhyQuestion } from "../lib/askLocal";
import { briefLooksLikeLapland, briefTarget } from "../lib/countyBrief";
import { isTreatmentChoiceQuestion, matchingRefusalFact } from "../lib/facts";
import { isForcedOffline, proxyBaseUrl, streamAsk } from "../lib/askLlm";
import type { PilotBriefDraft } from "../lib/briefDraft";

type Msg =
  | { kind: "me"; text: string }
  | { kind: "ai"; text: string; cites: string[]; meta?: string }
  | { kind: "refuse"; text: string; cites: string[]; meta?: string };

export function AskPanel({
  lang,
  context,
  onOpenBrief,
  open,
  onClose,
  dark = false,
  tab = "overview",
  countyId = null,
  countyLabel,
}: {
  lang: "en" | "fi";
  context: string;
  onOpenBrief?: (draft?: PilotBriefDraft, opts?: { drafting?: boolean; cancel?: boolean }) => void;
  open: boolean;
  onClose: () => void;
  dark?: boolean;
  tab?: string;
  countyId?: string | null;
  countyLabel?: string;
}) {
  const fi = lang === "fi";
  const [msgs, setMsgs] = useState<Msg[]>([]);
  const [query, setQuery] = useState("");
  const [busy, setBusy] = useState(false);
  const endRef = useRef<HTMLDivElement | null>(null);
  const offline = isForcedOffline();
  const proxy = proxyBaseUrl();

  useEffect(() => {
    endRef.current?.scrollIntoView({ behavior: "smooth", block: "end" });
  }, [msgs]);

  const chips = useMemo(() => {
    if (tab === "built") {
      return [
        { id: "extract", label: fi ? "Mikä poimi nämä tapahtumat?" : "What extracted these events?" },
        { id: "synth", label: fi ? "Miksi synteettisiä muistioita?" : "Why synthetic notes?" },
        { id: "clock", label: fi ? "Mikä käynnistää kellon?" : "What starts the clock?" },
      ];
    }
    if (tab === "live") {

      return [
        { id: "alerts", label: fi ? "Tiivistä tämän päivän hälytykset" : "Summarise today's alerts" },
        { id: "nav", label: fi ? "Kuka tarvitsee navigatorin?" : "Who needs a navigator?" },
        { id: "cmo", label: fi ? "Luonnos: viikoittainen CMO-muistio" : "Draft weekly CMO note" },
      ];
    }
    return [
      { id: "brief", label: fi ? "Luonnos: Lapin pilottimuistio" : "Draft Lapland pilot brief" },
      { id: "dark", label: fi ? "Missä tieto pimenee?" : "Where does data go dark?" },
      { id: "kym", label: fi ? "Vertaa Kymenlaaksoa" : "Compare Kymenlaakso" },
    ];
  }, [fi, tab]);

  async function push(q: string) {
    const qLang = detectQuestionLang(q);
    const mustRefuse = isSurvivalQuestion(q) || isTreatmentChoiceQuestion(q) || Boolean(matchingRefusalFact(q));
    const briefQ = isBriefQuestion(q) && !mustRefuse;
    const target = briefQ ? briefTarget(q, countyId) : null;
    const unknownBrief = Boolean(briefQ && target?.unknown);
    const routed = isActionQuestion(q) || isWhyQuestion(q) || mustRefuse || unknownBrief;
    const wantLlm = Boolean(proxy) && !offline && !busy && !routed;
    const draftingLabel = qLang === "fi" ? "Luonnosta kirjoitetaan…" : qLang === "sv" ? "Utkast skrivs…" : "Drafting brief…";
    const BUNDLED = "Bundled sourced answer";
    const LIVE_TAG = "EU-hosted inference";
    setMsgs((m) => [
      ...m,
      { kind: "me", text: q },
      {
        kind: "ai" as const,
        text: briefQ && wantLlm ? draftingLabel : fi ? "Haetaan…" : "Asking…",
        cites: [],
        meta: wantLlm ? (fi ? "Yhdistetään…" : "Connecting…") : undefined,
      },
    ]);
    const replaceLast = (msg: Msg) => setMsgs((m) => [...m.slice(0, -1), msg]);

    if (wantLlm) {
      setBusy(true);
      let streamed = "";
      if (briefQ && onOpenBrief) onOpenBrief(undefined, { drafting: true });
      const result = await streamAsk(q, {
        county: briefQ ? (target?.id ?? undefined) : (countyId ?? undefined),
        countyLabel: (briefQ && target?.label) || countyLabel,
        mode: briefQ ? "brief" : "answer",
        lang: qLang,
        onDelta: (text) => {
          streamed = text;
          // Never paint raw JSON while a brief is streaming.
          replaceLast({
            kind: "ai",
            text: briefQ ? draftingLabel : (streamed || (fi ? "Haetaan…" : "Asking…")),
            cites: [],
            meta: fi ? "Suoratoisto…" : "Streaming…",
          });
        },
      });
      setBusy(false);
      if (result.ok) {
        const leakedLapland = Boolean(briefQ && target?.id && target.id !== "21" && result.brief && briefLooksLikeLapland(result.brief));
        if (!leakedLapland) {
          if (result.brief && onOpenBrief) onOpenBrief(result.brief);
          replaceLast({
            kind: result.kind,
            text: result.brief
              ? fi
                ? `Luonnos alueelle ${result.brief.county} on valmis. Luonnos, ei allekirjoitettu. Omistajat rooleina, ei niminä.`
                : `Draft brief for ${result.brief.county} is ready. Draft, not signed. Owners are listed by role, not by personal name.`
              : result.text.replace(/^REFUSE\s*/i, ""),
            cites: result.cites,
            meta: LIVE_TAG,
          });
          return;
        }
        // LLM drafted the Lapland brief for another county — fall through.
      }
      // fall through to deterministic
    }

    const local = answerQuestion(q, qLang, target?.unknown ? undefined : (target?.id ?? countyId));
    if (local.openBrief === "pregenerated" && onOpenBrief) onOpenBrief();
    else if (local.brief && onOpenBrief) onOpenBrief(local.brief);
    else if (briefQ && onOpenBrief) onOpenBrief(undefined, { cancel: true });
    replaceLast({ kind: local.kind, text: local.text, cites: local.cites, meta: local.meta ?? BUNDLED });
  }

  function onSubmit(e: FormEvent) {
    e.preventDefault();
    const q = query.trim();
    if (!q) return;
    setQuery("");
    push(q);
  }

  if (!open) return null;

  return (
    <aside className={`panel${dark ? " dark" : ""}`} id="ask-tasan">
      <div className="panel-head">
        <div className="panel-title">
          <span className="spark">
            <svg className="i" viewBox="0 0 24 24">
              <path d="M9.94 15.5A2 2 0 0 0 8.5 14.06l-6.13-1.58a.5.5 0 0 1 0-.96L8.5 9.94A2 2 0 0 0 9.94 8.5l1.58-6.13a.5.5 0 0 1 .96 0L14.06 8.5A2 2 0 0 0 15.5 9.94l6.13 1.58a.5.5 0 0 1 0 .96L15.5 14.06a2 2 0 0 0-1.44 1.44l-1.58 6.13a.5.5 0 0 1-.96 0z" />
              <path d="M20 3v4M22 5h-4" />
            </svg>
          </span>
          Ask Tasan
          <span className="badge b-comp" style={{ marginLeft: "auto" }}>
            {fi
              ? `Perustuu ${sourcedFactCount} lähteistettyyn faktaan`
              : `Grounded in ${sourcedFactCount} sourced facts`}
          </span>
          <button type="button" className="panel-hide" onClick={onClose}>
            {fi ? "Piilota" : "Hide"}
          </button>
        </div>
        <div className="ctx">
          Context <b>{context}</b>
        </div>
      </div>
      <div className="msgs">
        {msgs.map((m, i) => (
          <Bubble key={i} msg={m} lang={lang} />
        ))}
        <div ref={endRef} />
      </div>
      <div className="sugg">
        {chips.map((c) => (
          <button key={c.id} type="button" onClick={() => push(c.label)}>
            {c.label}
          </button>
        ))}
      </div>
      <form className="input" onSubmit={onSubmit}>
        <input
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder={fi ? "Kysy hyvinvointialueesta…" : "Ask about any county…"}
          aria-label={fi ? "Kysymys" : "Question"}
          disabled={busy}
        />
        <button type="submit" className="send" aria-label={fi ? "Lähetä" : "Send"} disabled={busy}>
          <svg className="i" viewBox="0 0 24 24">
            <path d="M14.5 21.7a.5.5 0 0 0 .9 0L22 2.4a.5.5 0 0 0-.6-.6L2.3 8.5a.5.5 0 0 0 0 .9l8 3.2a2 2 0 0 1 1.1 1.1z" />
            <path d="m21.9 2.1-11 11" />
          </svg>
        </button>
      </form>
      <div className="panel-foot">
        <span>
          {offline
            ? fi
              ? "Pakotettu offline · lähteistetyt faktat"
              : "Forced offline · sourced facts only"
            : fi
              ? "Kieltäytyy ilman lähdettä"
              : "Refuses without a source"}
        </span>
      </div>
    </aside>
  );
}

function Bubble({ msg, lang }: { msg: Msg; lang: "en" | "fi" }) {
  if (msg.kind === "me") return <div className="bubble me">{msg.text}</div>;
  if (msg.kind === "refuse") {
    return (
      <div className="bubble refuse">
        <div className="rl">
          <svg className="i" viewBox="0 0 24 24">
            <path d="M10.7 5.1A10.7 10.7 0 0 1 22 12a10.8 10.8 0 0 1-1.4 2.2M14.1 14.2a3 3 0 0 1-4.2-4.2M17.5 17.5A10.7 10.7 0 0 1 2 12a10.7 10.7 0 0 1 4.4-5.5M2 2l20 20" />
          </svg>
          {lang === "fi" ? "Ei lähteellistä vastausta" : "No sourced answer"}
        </div>
        {msg.text} <Cites ids={msg.cites} lang={lang} />
        {msg.meta ? <div className="meta">{msg.meta}</div> : null}
      </div>
    );
  }
  return (
    <div className="bubble ai">
      {msg.text} <Cites ids={msg.cites} lang={lang} />
      {msg.meta ? (
        <div className="meta">
          <svg className="i" viewBox="0 0 24 24">
            <path d="M20 13c0 5-3.5 7.5-7.66 8.95a1 1 0 0 1-.67-.01C7.5 20.5 4 18 4 13V6a1 1 0 0 1 1-1c2 0 4.5-1.2 6.24-2.72a1.17 1.17 0 0 1 1.52 0C14.51 3.81 17 5 19 5a1 1 0 0 1 1 1z" />
          </svg>
          {msg.meta}
        </div>
      ) : null}
    </div>
  );
}

function Cites({ ids, lang }: { ids: string[]; lang: "en" | "fi" }) {
  if (!ids.length) return null;
  return (
    <span className="cites-wrap">
      {ids.map((id) => {
        const fact = factById(id);
        const label = fact ? sourceLabel(fact, lang) : id;
        return (
          <span key={id} className="cite" title={id}>
            {label}
          </span>
        );
      })}
    </span>
  );
}
