import type { ReactNode } from "react";
import { polkuUrl, type PolkuPage } from "../lib/polku";

function ExternalIcon() {
  return (
    <svg className="i polku-ext" viewBox="0 0 24 24" aria-hidden>
      <path d="M15 3h6v6M10 14 21 3M18 13v6a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h6" />
    </svg>
  );
}

/** Inline link out to Polku. Always opens in a new tab so the Tasan demo stays put. */
export function PolkuLink({
  page = "demo",
  className = "",
  children,
  title,
}: {
  page?: PolkuPage;
  className?: string;
  children: ReactNode;
  title?: string;
}) {
  return (
    <a className={`polku-link ${className}`.trim()} href={polkuUrl(page)} target="_blank" rel="noopener noreferrer" title={title}>
      {children}
      <ExternalIcon />
    </a>
  );
}

/** Topbar switch: Tasan (this app, county view) | Polku (care-team side). */
export function PolkuSwitch({ lang }: { lang: "en" | "fi" }) {
  const fi = lang === "fi";
  return (
    <div className="polku-switch" role="group" aria-label={fi ? "Projektin näkymät" : "Project sides"}>
      <span className="on" aria-current="page" title={fi ? "Alueet ja johto" : "Counties and leadership"}>
        Tasan
      </span>
      <PolkuLink
        page="home"
        title={fi ? "Hoitotiimeille: ajaa jokaisen hoitopolun vaiheen kellon mukaan" : "For care teams: runs every pathway step on the clock"}
      >
        Polku
      </PolkuLink>
    </div>
  );
}
