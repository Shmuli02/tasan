import { factById, isTreatmentChoiceQuestion, matchingRefusalFact, statement } from "./facts";
import { displayRole, hasPreGeneratedBrief } from "./roles";
import { recById } from "./data";
import { briefTarget, buildCountyBrief, countyFromText } from "./countyBrief";
import type { PilotBriefDraft } from "./briefDraft";

export type AskKind = "ai" | "refuse";

export type LocalAnswer = {
  kind: AskKind;
  text: string;
  cites: string[];
  meta?: string;
  openBrief?: "pregenerated" | "generated" | "none";
  brief?: PilotBriefDraft;
};

export function detectQuestionLang(q: string): "fi" | "sv" | "en" {
  const s = q.toLowerCase();
  const fiHit = /\b(mikä|miksi|kuinka|onko|missä|miten|luonnos|alueelle|hyvinvointialue|keuhkosyöp|lappi|lapin|vertail|pimene|tämän|kuka|tarvitsee|hälyt)\b/i.test(s);
  const svHit = /\b(vilka|vilket|vilken|varför|hur många|utkasten|utkast|välfärdsområde|landskap|lappland|jämför|överlevnad|läkemedel|promemoria)\b/i.test(s);
  if (svHit && !fiHit) return "sv";
  if (fiHit) return "fi";
  if (/[äöå]/i.test(q) && svHit) return "sv";
  if (/[äö]/i.test(q)) return "fi";
  return "en";
}


export function isActionQuestion(q: string): boolean {
  return /\b(what should|do first|mitä .{0,40}(ensin|ensiksi)|teh[däaä]+ ensin|ska .{0,40}göra( först)?|först)\b/i.test(q);
}

export function isWhyQuestion(q: string): boolean {
  return /\b(why|miksi|varför|behind|jäljessä|efter|gap|ero)\b/i.test(q);
}

export function leadRecIdForCounty(countyId?: string | null, q = ""): "T1" | "T3" {
  const blob = `${countyId ?? ""} ${q}`.toLowerCase();
  if (countyId === "10" || /kymen/i.test(blob)) return "T1";
  return "T3";
}

function recAnswer(q: string, lang: "fi" | "sv" | "en", countyId?: string | null): LocalAnswer | null {
  if (!isActionQuestion(q)) return null;
  const id = leadRecIdForCounty(countyId, q);
  const rec = recById(id);
  if (!rec) return null;
  const countyName = /kymen/i.test(`${countyId} ${q}`) || id === "T1" ? "Kymenlaakso" : "Lapland";
  const roleBlock = rec.owner_role && typeof rec.owner_role === "object" ? rec.owner_role as Record<string, unknown> : null;
  const byCounty = roleBlock && typeof roleBlock.by_county === "object" ? (roleBlock.by_county as Record<string, Record<string, string>>) : null;
  const site = byCounty?.[countyName] ?? byCounty?.[id === "T1" ? "Kymenlaakso" : "Lapland"];
  const ownerRaw =
    site?.owner_of_delayed_patients ||
    site?.signer ||
    (typeof roleBlock?.owner_of_delayed_patients === "string" ? roleBlock.owner_of_delayed_patients : "") ||
    (typeof roleBlock?.signer === "string" ? roleBlock.signer : "") ||
    (Array.isArray((rec as unknown as { owners?: string[] }).owners) ? String((rec as unknown as { owners: string[] }).owners[0] ?? "") : "");
  const owner = displayRole(ownerRaw) || (id === "T3"
    ? `Nurse navigator (1 FTE), Acting Director of Nursing, ${countyName} wellbeing services county`
    : `Johtajaylilääkäri / Chief Medical Officer, ${countyName} wellbeing services county`);
  const cost = rec.cost_range;
  const costText =
    cost && cost.low != null && cost.high != null
      ? `€${Number(cost.low).toLocaleString("en-GB")}–€${Number(cost.high).toLocaleString("en-GB")} / ${cost.period ?? "90-day pilot"}`
      : "";
  const cites = id === "T1" ? ["lung_curative_kymenlaakso", "lung_curative_national"] : ["lung_curative_lapland", "lung_curative_national"];
  const text =
    lang === "fi"
      ? `Ensimmäinen toimenpide alueella ${countyName} on ${id}: ${rec.title}. Omistaja (rooli): ${owner}. Kustannus, henkilöstö vain, arvio: ${costText}.`
      : lang === "sv"
        ? `Första åtgärden i ${countyName} är ${id}: ${rec.title}. Ägare (roll): ${owner}. Kostnad, endast personal, uppskattning: ${costText}.`
        : `The first thing ${countyName} should do is ${id}: ${rec.title}. Owner (role only): ${owner}. Staff cost only, estimate: ${costText}.`;
  return { kind: "ai", text, cites };
}

export function isBriefQuestion(q: string): boolean {
  if (isSurvivalQuestion(q) || isTreatmentChoiceQuestion(q) || matchingRefusalFact(q)) return false;
  return /\b((draft|luonnos|utkast)\b.{0,80}(brief|muistio|promemoria|pilot)|pilot brief|pilottimuistio|draft a pilot)/i.test(q)
    && !/\b(cmo|viikoittainen|weekly cmo)\b/i.test(q);
}

export function isSurvivalQuestion(q: string): boolean {
  return /\b((1|5|one|five)[ -]?year survival|survival (rate|benefit|gain|improv)|improve[s]? survival|eloonjäämis|ylihenkis|överlevnad(stal|en)?|kuolleisuutta vähent)\b/i.test(
    q,
  );
}

export function namedCountyFromQuestion(q: string): { id?: string; label: string; isLapland: boolean } {
  return countyFromText(q);
}

function t(lang: "fi" | "sv" | "en", fi: string, sv: string, en: string): string {
  if (lang === "fi") return fi;
  if (lang === "sv") return sv;
  return en;
}

function refuseIfNeeded(q: string, lang: "fi" | "sv" | "en"): LocalAnswer | null {
  if (isTreatmentChoiceQuestion(q)) {
    return {
      kind: "refuse",
      text: t(
        lang,
        "Tasan ei anna lääke- tai hoitovalintoja. Kysymys on aineiston ulkopuolella.",
        "Tasan ger inte råd om läkemedel eller behandlingsval. Frågan ligger utanför de källbelagda fakta.",
        "Tasan does not advise on drugs or treatment choice. That is outside the sourced facts.",
      ),
      cites: [],
    };
  }
  if (isSurvivalQuestion(q)) {
    const f = factById("nodata_lives_saved");
    return {
      kind: "refuse",
      text: f
        ? lang === "fi"
          ? statement(f, "fi")
          : lang === "sv"
            ? "Ingen offentlig källa uppskattar räddade liv eller överlevnadsvinst, så Tasan gör det inte heller."
            : statement(f, "en")
        : t(
            lang,
            "Tasan ei arvioi eloonjäämistä tai pelastettuja henkiä ilman julkista lähdettä.",
            "Tasan uppskattar inte överlevnad eller räddade liv utan en offentlig källa.",
            "Tasan does not estimate survival or lives saved without a public source.",
          ),
      cites: f ? [f.id] : [],
    };
  }
  const refusal = matchingRefusalFact(q);
  if (refusal) {
    const text =
      lang === "sv"
        ? `${statement(refusal, "en")} (ingen offentlig källa; Tasan vägrar att gissa.)`
        : statement(refusal, lang === "fi" ? "fi" : "en");
    return { kind: "refuse", text, cites: [refusal.id] };
  }
  return null;
}

export function answerQuestion(q: string, lang: "fi" | "sv" | "en" = detectQuestionLang(q), countyId?: string | null): LocalAnswer {
  const early = refuseIfNeeded(q, lang);
  if (early) return early;
  if (isBriefQuestion(q)) {
    const named = briefTarget(q, countyId);
    if (named.unknown) {
      return {
        kind: "ai",
        text: t(
          lang,
          "Ei muistiota sille alueelle: Tasan kattaa 21 manner-Suomen hyvinvointialuetta ja Helsingin",
          "Ingen promemoria för det området: Tasan täcker de 21 välfärdsområdena på fastlandet och Helsingfors",
          "No brief for that county: Tasan covers the 21 mainland wellbeing services counties and Helsinki",
        ),
        cites: [],
        openBrief: "none",
      };
    }
    // Only the hand-authored Lapland brief may open under openBrief=pregenerated.
    if (named.isLapland && hasPreGeneratedBrief(named.id)) {
      return {
        kind: "ai",
        text: t(
          lang,
          "Avaan Lapin 90 päivän pilottimuistion. Luonnos, ei allekirjoitettu. Omistajat on merkitty rooleina, ei niminä.",
          "Öppnar Lapplands 90-dagars pilot-PM. Utkast, inte undertecknat. Ägare anges med roll, inte personnamn.",
          "Opening the Lapland 90-day pilot brief. Draft, not signed. Owners are listed by role, not by personal name.",
        ),
        cites: ["people_number_lapland", "lung_curative_lapland"],
        openBrief: "pregenerated",
      };
    }
    const generated = named.id ? buildCountyBrief(named.id, lang === "fi" ? "fi" : "en") : null;
    if (generated) {
      return {
        kind: "ai",
        text: t(
          lang,
          `Luonnos alueelle ${named.label} on valmis. Luonnos, ei allekirjoitettu. Omistajat rooleina, ei niminä.`,
          `Utkast för ${named.label} är klart. Utkast, inte undertecknat. Ägare anges med roll, inte personnamn.`,
          `Draft brief for ${named.label} is ready. Draft, not signed. Owners are listed by role, not by personal name.`,
        ),
        cites: ["lung_curative_national", "nodata_stage_adjusted_comparison"],
        openBrief: "generated",
        brief: generated,
      };
    }
    const place = named.label || t(lang, "tälle alueelle", "detta område", "this county");
    return {
      kind: "ai",
      text: t(
        lang,
        `Alueelle ${place} ei ole vielä valmista luonnosta.`,
        `Ingen färdig promemoria för ${place} ännu.`,
        `No pre-generated brief for ${place} yet`,
      ),
      cites: [],
      openBrief: "none",
    };
  }

  const rec = recAnswer(q, lang, countyId);
  if (rec) return rec;

  if (isWhyQuestion(q) || /gap|ero|lapland|lappi|lappland|curative|parantav/i.test(q)) {
    const kym = /kymen/i.test(q) || countyId === "10";
    const gap = factById(kym ? "lung_curative_kymenlaakso" : "lung_curative_lapland");
    const nat = factById("lung_curative_national");
    const stage = factById("nodata_stage_adjusted_comparison");
    const dark = factById("nodata_referral_to_diagnosis");
    if (gap) {
      const bit = (f: ReturnType<typeof factById>, fallback: string) =>
        f ? statement(f, lang === "fi" ? "fi" : "en") : fallback;
      const stageBit =
        lang === "fi"
          ? "Ei vaihevakioitu: ei julkista tietoa."
          : lang === "sv"
            ? "Inte stadiejusterat: inga offentliga uppgifter."
            : "Not stage-adjusted: no public data.";
      const darkBit =
        lang === "fi"
          ? "Julkista tietoa hoitopolun vaiheista lähetteestä diagnoosiin tai diagnoosista hoitoon hyvinvointialueittain ei ole."
          : lang === "sv"
            ? "Det finns ingen offentlig information per välfärdsområde om stegen från remiss till diagnos eller från diagnos till behandling."
            : "There is no public county-level data on referral-to-diagnosis or diagnosis-to-treatment steps.";
      return {
        kind: "ai",
        text: `${bit(gap, "")} ${nat ? statement(nat, lang === "fi" ? "fi" : "en") : ""} ${stageBit} ${darkBit}`.replace(/\s+/g, " ").trim(),
        cites: [gap.id, nat?.id, stage?.id, dark?.id].filter((id): id is string => Boolean(id)),
      };
    }
  }

  if (/summarise|tiivist|alert|hälyt/i.test(q) && /today|tämän päiv|navigator/i.test(q) || /who needs a navigator|kuka tarvitsee/i.test(q)) {
    return {
      kind: "ai",
      text: t(
        lang,
        "Esimerkkikonsolissa kolme potilasta ylittää päivän 28 ilman hoitopäätöstä. Navigator varaa puuttuvan CT-ajan. Havainnollistava, ei ennuste.",
        "I exempelkonsolen passerar tre patienter dag 28 utan behandlingsbeslut. Navigatorn bokar den saknade CT-tiden. Illustrativt, inte en prognos.",
        "In the example console, three patients cross day 28 with no treatment decision. The navigator books the missing CT. Illustrative, not a forecast.",
      ),
      cites: ["nodata_regional_target_compliance"],
    };
  }
  if (/cmo|viikoittainen/i.test(q)) {
    return {
      kind: "ai",
      text: t(
        lang,
        "Ei julkista alueittaista 6 viikon hoitoonpääsyn tilastoa. Tämä on aukko, jonka Tasan Live täyttää esimerkillä.",
        "Det finns ingen offentlig regional statistik för 6 veckors väntetid till behandling. Det är luckan Tasan Live fyller med ett exempel.",
        "No public regional 6-week compliance statistic. That is the gap Tasan Live fills with an example.",
      ),
      cites: ["nodata_regional_target_compliance"],
    };
  }

  if (/dark|pimene|nodata|ei julkist|går mörk/i.test(q)) {
    return {
      kind: "ai",
      text: t(
        lang,
        "Julkista tietoa hoitopolun vaiheista lähetteestä diagnoosiin tai diagnoosista hoitoon hyvinvointialueittain ei ole. THL:n tavoite on 6 viikkoa lähetteestä hoitoon.",
        "Det finns ingen offentlig information per välfärdsområde om stegen från remiss till diagnos eller från diagnos till behandling. THL:s mål är 6 veckor från remiss till behandling.",
        "There is no public county-level data on referral-to-diagnosis or diagnosis-to-treatment steps. The THL target is 6 weeks from referral to treatment.",
      ),
      cites: ["nodata_referral_to_diagnosis", "thl_6wk_referral_to_treatment"],
    };
  }
  if (/kymen/i.test(q)) {
    const f = factById("lung_curative_kymenlaakso");
    const st = f ? statement(f, lang === "fi" ? "fi" : "en") : t(lang, "Ei osumaa.", "Ingen träff.", "No match.");
    return { kind: "ai", text: lang === "sv" && f ? `${st}` : st, cites: ["lung_curative_kymenlaakso", "lung_curative_national"] };
  }
  const gap = factById("lung_curative_lapland");
  if (gap && /gap|ero|lapland|lappi|lappland|curative|parantav/i.test(q)) {
    return {
      kind: "ai",
      text: statement(gap, lang === "fi" ? "fi" : "en"),
      cites: ["lung_curative_lapland", "lung_curative_national"],
    };
  }
  const ppl = factById("people_number_national");
  if (ppl && /65|12|people|potilas|personer/i.test(q)) {
    return { kind: "ai", text: statement(ppl, lang === "fi" ? "fi" : "en"), cites: ["people_number_national"] };
  }
  return {
    kind: "refuse",
    text: t(
      lang,
      "Ei suoraa osumaa bundletuissa faktoissa. Kokeile ehdotettua kysymystä.",
      "Ingen direkt träff i de medföljande fakta. Prova en föreslagen fråga.",
      "No direct match in the bundled facts. Try a suggested question.",
    ),
    cites: [],
  };
}
