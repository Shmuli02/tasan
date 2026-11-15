// Polku is the care-team side of the same project: it runs each lung pathway
// step by phone and records the step clocks that Tasan says nobody publishes.
// Tasan links out to it at the points where that missing data shows up.

export const POLKU_ORIGIN = "https://polku.ender.fi";

export type PolkuPage = "home" | "demo" | "nurse" | "handoffs";

const PATHS: Record<PolkuPage, string> = {
  home: "/",
  demo: "/demo",
  nurse: "/nurse",
  handoffs: "/handoffs",
};

export function polkuUrl(page: PolkuPage = "home"): string {
  return `${POLKU_ORIGIN}${PATHS[page]}`;
}

export type PolkuLinkSpec = { href: string; label: string };

const POLKU_Q =
  /\bpolku\b|real (clock|data|time)|where (would|will|does) (the )?(real )?data come from|how (would|do|can) (we|you|it) (collect|measure|record)|who records|patient call|phone line|oikea(a|t)? (data|kello)|mistä (data|tieto)|kuka kirjaa|puhelin/i;

export function isPolkuQuestion(q: string): boolean {
  return POLKU_Q.test(q);
}

export function polkuAnswer(lang: "fi" | "sv" | "en"): { text: string; link: PolkuLinkSpec } {
  if (lang === "fi") {
    return {
      text:
        "Tasan näyttää, missä aukko on. Polku on saman projektin toinen puoli hoitotiimeille: potilas soittaa, sääntömoottori tarkistaa oireet julkaistuja kriteerejä vasten, hoitaja hyväksyy ehdotetun ajan ja jokaisen vaiheen kello käy. Ne kellot ovat juuri sitä lähete → hoito -dataa, jota mikään alue ei nyt julkaise. Polku on synteettisellä datalla, ei potilaskäytössä.",
      link: { href: polkuUrl("demo"), label: "Katso Polku toiminnassa" },
    };
  }
  if (lang === "sv") {
    return {
      text:
        "Tasan visar var gapet finns. Polku är projektets andra sida, för vårdteam: patienten ringer, en regelmotor matchar symtomen mot publicerade kriterier, sjuksköterskan godkänner en föreslagen tid och varje stegs klocka går. De klockorna är just den remiss → behandling-data som ingen region publicerar i dag. Polku körs på syntetiska data.",
      link: { href: polkuUrl("demo"), label: "Se Polku i drift" },
    };
  }
  return {
    text:
      "Tasan shows where the gap is. Polku is the other side of the same project, for care teams: the patient phones in, a rules engine checks symptoms against published criteria, the nurse accepts a proposed time, and every step runs on its own clock. Those clocks are exactly the referral → treatment data no county publishes today. Polku runs on synthetic data, not with patients.",
    link: { href: polkuUrl("demo"), label: "See Polku run" },
  };
}
