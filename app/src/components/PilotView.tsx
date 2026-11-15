import { PilotBriefBody } from "./PilotBriefModal";

export function PilotView({ lang }: { lang: "en" | "fi"; onOpenBrief?: () => void }) {
  const fi = lang === "fi";
  return (
    <div className="pilot-view">
      <div className="hdr">
        <div>
          <div className="kicker">T3 · 90 {fi ? "päivää" : "days"}</div>
          <h1>{fi ? "Lapin 90 päivän pilotti" : "Lapland 90-day pilot"}</h1>
        </div>
      </div>
      <PilotBriefBody lang={lang} showToolbar />
    </div>
  );
}
