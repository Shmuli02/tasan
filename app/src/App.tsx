import { useEffect, useState, type ReactNode } from "react";
import { Overview } from "./components/Overview";
import { AskPanel } from "./components/AskPanel";
import { TasanLive } from "./components/TasanLive";
import { PilotView } from "./components/PilotView";
import { HowWeBuilt } from "./components/HowWeBuilt";
import { PilotBriefModal } from "./components/PilotBriefModal";
import type { PilotBriefDraft } from "./lib/briefDraft";
import { isExampleApp } from "./lib/data";
import { shortName } from "./lib/chartData";

export type Lang = "en" | "fi";
export type TabId = "overview" | "live" | "pilot" | "built";

const TABS: { id: TabId; en: string; fi: string; sv?: string; example?: boolean; icon: "map" | "pulse" | "clip" | "layers" }[] = [
  { id: "overview", en: "Overview", fi: "Yhteenveto", icon: "map" },
  { id: "live", en: "Tasan Live", fi: "Tasan Live", example: true, icon: "pulse" },
  { id: "pilot", en: "Pilot", fi: "Pilotti", icon: "clip" },
  { id: "built", en: "How we built it", fi: "Näin teimme tämän", sv: "Så här byggde vi det", icon: "layers" },
];

function isNarrowScreen(): boolean {
  return typeof window !== "undefined" && window.matchMedia("(max-width: 1600px)").matches;
}

export function App() {
  const [lang, setLang] = useState<Lang>("en");
  const [tab, setTab] = useState<TabId>("overview");
  const [selectedId, setSelectedId] = useState<string | null>("21");
  const [narrow, setNarrow] = useState(isNarrowScreen);
  const [askOpen, setAskOpen] = useState(() => !isNarrowScreen());
  const [sourcesOn, setSourcesOn] = useState(true);
  const [briefOpen, setBriefOpen] = useState(false);
  const [briefDraft, setBriefDraft] = useState<PilotBriefDraft | null>(null);
  const [briefDrafting, setBriefDrafting] = useState(false);
  function openBrief(draft?: PilotBriefDraft, opts?: { drafting?: boolean; cancel?: boolean }) {
    if (opts?.cancel) {
      setBriefOpen(false);
      setBriefDraft(null);
      setBriefDrafting(false);
      return;
    }
    setBriefDrafting(Boolean(opts?.drafting));
    setBriefDraft(opts?.drafting ? null : (draft ?? null));
    setBriefOpen(true);
  }

  const example = isExampleApp();
  const fi = lang === "fi";

  useEffect(() => {
    document.title = example
      ? "Tasan — EXAMPLE data"
      : fi
        ? "Tasan — Yhdenvertainen syöpähoito"
        : "Tasan — Equal care across Finland";
    document.documentElement.lang = fi ? "fi" : "en";
  }, [example, fi]);

  useEffect(() => {
    const q = new URLSearchParams(window.location.search);
    const county = q.get("county");
    const tabQ = q.get("tab");
    if (county) setSelectedId(county);
    if (tabQ === "live" || tabQ === "overview" || tabQ === "pilot" || tabQ === "built") setTab(tabQ);
  }, []);

  useEffect(() => {
    const mq = window.matchMedia("(max-width: 1600px)");
    const apply = () => {
      setNarrow(mq.matches);
      setAskOpen(!mq.matches);
    };
    mq.addEventListener("change", apply);
    return () => mq.removeEventListener("change", apply);
  }, []);

  const countyLabel = selectedId ? shortName(selectedId, lang) : fi ? "Suomi" : "Finland";
  const tabLabel = TABS.find((t) => t.id === tab);
  const context =
    tab === "built"
      ? (fi ? "Näin teimme tämän" : "How we built it")
      : `${tab === "overview" ? (fi ? "Suomi" : "Finland") : tab === "live" ? (fi ? "Lappi" : "Lapland") : countyLabel} · ${fi ? tabLabel?.fi : tabLabel?.en}`;

  return (
    <div className={`app-root${tab === "live" ? " theme-live" : ""}`}>
      <header className="topbar">
        <img className="logo" src="./logo-horizontal.svg" alt="tasan" height={30} />
        <nav className="tabs" aria-label={fi ? "Näkymät" : "Views"}>
          {TABS.map((t) => (
            <button
              key={t.id}
              type="button"
              className={`tab${tab === t.id ? " on" : ""}`}
              onClick={() => setTab(t.id)}
            >
              <TabIcon name={t.icon} />
              {fi ? t.fi : t.en}
              {t.example ? <span className="ex">{fi ? "ESIMERKKI" : "EXAMPLE"}</span> : null}
            </button>
          ))}
        </nav>
        <div className="right">
          <div className="lang" role="group" aria-label={fi ? "Kieli" : "Language"}>
            <button type="button" className={lang === "fi" ? "on" : ""} onClick={() => setLang("fi")}>
              FI
            </button>
            <button type="button" className={lang === "en" ? "on" : ""} onClick={() => setLang("en")}>
              EN
            </button>
          </div>
          <button
            type="button"
            className={`btn-ask-header${askOpen ? " on" : ""}`}
            onClick={() => setAskOpen((v) => !v)}
            aria-expanded={askOpen}
            aria-controls="ask-tasan"
          >
            Ask Tasan
          </button>
        </div>
      </header>
      <div className={`shell${askOpen && !narrow ? "" : " shell-collapsed"}`}>
        <main className={`main${tab === "live" ? " console" : ""}`}>
          {tab === "overview" ? (
            <Overview
              lang={lang}
              selectedId={selectedId}
              onSelect={setSelectedId}
              sourcesOn={sourcesOn}
              onToggleSources={() => setSourcesOn((v) => !v)}
              onOpenBrief={openBrief}
            />
          ) : tab === "live" ? (
            <TasanLive lang={lang} />
          ) : tab === "built" ? (
            <HowWeBuilt lang={lang} />
          ) : (
            <PilotView lang={lang} onOpenBrief={openBrief} />
          )}
        </main>
        {askOpen ? (
          <AskPanel
            lang={lang}
            context={context}
            open={askOpen}
            onClose={() => setAskOpen(false)}
            onOpenBrief={openBrief}
            dark={tab === "live"}
            tab={tab}
            countyId={selectedId}
            countyLabel={countyLabel}
          />
        ) : null}
      </div>
      {askOpen && narrow ? <div className="ask-backdrop" onClick={() => setAskOpen(false)} /> : null}
      {briefOpen ? <PilotBriefModal lang={lang} draft={briefDraft} drafting={briefDrafting} onClose={() => { setBriefOpen(false); setBriefDraft(null); setBriefDrafting(false); }} /> : null}
    </div>
  );
}

function TabIcon({ name }: { name: (typeof TABS)[number]["icon"] }) {
  const paths: Record<typeof name, ReactNode> = {
    map: (
      <>
        <path d="M14.1 6 9.9 3.9a2 2 0 0 0-1.8 0L3.6 6.2A1 1 0 0 0 3 7.1v12.3a1 1 0 0 0 1.4.9l3.7-1.9a2 2 0 0 1 1.8 0l4.2 2.1a2 2 0 0 0 1.8 0l4.5-2.3a1 1 0 0 0 .6-.9V5.1a1 1 0 0 0-1.4-.9l-3.7 1.9a2 2 0 0 1-1.8 0z" />
        <path d="M15 6v15M9 3v15" />
      </>
    ),
    pulse: <path d="M22 12h-2.48a2 2 0 0 0-1.93 1.46l-2.35 8.36a.25.25 0 0 1-.48 0L9.24 2.18a.25.25 0 0 0-.48 0l-2.35 8.36A2 2 0 0 1 4.49 12H2" />,
    clip: (
      <>
        <rect x="8" y="2" width="8" height="4" rx="1" />
        <path d="M16 4h2a2 2 0 0 1 2 2v14a2 2 0 0 1-2 2H6a2 2 0 0 1-2-2V6a2 2 0 0 1 2-2h2" />
        <path d="m9 14 2 2 4-4" />
      </>
    ),
    layers: (
      <>
        <path d="M12.83 2.18a2 2 0 0 0-1.66 0L2.6 6.08a1 1 0 0 0 0 1.83l8.58 3.91a2 2 0 0 0 1.66 0l8.58-3.9a1 1 0 0 0 0-1.83z" />
        <path d="m22 17.65-9.17 4.16a2 2 0 0 1-1.66 0L2 17.65" />
        <path d="m22 12.65-9.17 4.16a2 2 0 0 1-1.66 0L2 12.65" />
      </>
    ),
  };
  return (
    <svg className="i" viewBox="0 0 24 24">
      {paths[name]}
    </svg>
  );
}
