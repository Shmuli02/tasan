import type { Region, StageId } from "../types";
import {
  dataset,
  featuredRecIds,
  formatCi,
  formatValue,
  indicatorForStage,
  leadRecId,
  recById,
  regionById,
  sourceById,
  STAGE_ORDER,
  tasanClockNote,
} from "./data";
import { furthestFromTarget, widestStage } from "./stats";

export interface AnalystAnswer {
  title: string;
  paragraphs: string[];
  bullets?: string[];
  source_ids: string[];
  rec_ids?: string[];
  region_ids?: string[];
}

export interface SuggestedQ {
  id: string;
  label: string;
  query: string;
}

export function suggestedQuestions(selectedId: string | null): SuggestedQ[] {
  const region = regionById(selectedId);
  const wide = widestStage();
  const stageLabel = dataset.regions.stages.find((s) => s.id === wide.stage)?.label ?? wide.stage;
  const rec = recById(leadRecId()) ?? recById(dataset.keyMessage.primary_rec_id) ?? dataset.recs.recommendations[0];
  const qs: SuggestedQ[] = [
    { id: "widest", label: "Where is the widest gap?", query: "Where is the widest gap in the pathway?" },
    {
      id: "furthest",
      label: `Which counties lag on ${stageLabel.toLowerCase()}?`,
      query: `Which counties are furthest from the target for ${stageLabel}?`,
    },
    { id: "action", label: "What should a county do first?", query: "What should a wellbeing services county do first?" },
    { id: "goal3", label: "How does this map to Goal 3?", query: "How does this map to Goal 3 of the national cancer strategy?" },
    { id: "compliance", label: "Is 6-week compliance published?", query: "Does any county publish 6-week treatment-time compliance?" },
    { id: "surgery", label: "What does Taulukko 4.1 actually measure?", query: "What is the diagnosis-to-surgery time in Taulukko 4.1?" },
  ];
  if (rec) {
    qs.push({
      id: "sim",
      label: `Impact of “${rec.title}”`,
      query: `What would happen if we fully implemented ${rec.title}?`,
    });
  }
  if (region) {
    qs.unshift({
      id: "region",
      label: `How does ${region.name} compare?`,
      query: `How does ${region.name} (${region.name_fi ?? region.id}) compare with the national figure?`,
    });
  }
  return qs;
}

const STOP = new Set(
  "a an the of in on for to and or is are was were be by at as from with without what which who whom how where when why does do did can should would a the this that these those it its their our ja ja tai vai mikä missä miten miksi kuin että ei ole on se tämän tuon".split(/\s+/),
);

const SYNONYMS: Record<string, string[]> = {
  gap: ["gap", "difference", "disparity", "inequality", "variation", "spread", "ero", "eriarvo", "yhdenvertaisuus", "unequal", "equal"],
  treatment: ["treatment", "treat", "initiation", "hoito", "hoitoonpääsy", "hoitoon", "clock", "start", "aloitus"],
  referral: ["referral", "lähete", "lahete", "primary", "specialist", "perusterveydenhuolto", "erikoissairaanhoito", "transition"],
  detection: ["detection", "detect", "seulonta", "screening", "early", "stage", "toteaminen", "varhainen"],
  diagnosis: ["diagnosis", "diagnoosi", "diagnostiikka", "diagnostic"],
  goal3: ["goal3", "goal", "tavoite", "tavoite3", "strategy", "strategia", "yhdenvertainen", "vaikuttava"],
  action: ["action", "do", "recommend", "recommendation", "intervention", "should", "toimenpide", "ehdotus", "first"],
  simulate: ["simulate", "impact", "effect", "if", "coverage", "slider", "vaikutus", "proj"],
  worst: ["worst", "furthest", "lowest", "behind", "lag", "weakest", "huonoin"],
  cost: ["cost", "kustannus", "euro", "budget", "owner", "kpi"],
  source: ["source", "citation", "lähde", "lahde", "evidence", "limitation", "assumption"],
};

function tokens(q: string): string[] {
  return q
    .toLowerCase()
    .normalize("NFD")
    .replace(/[\u0300-\u036f]/g, "")
    .replace(/[^\p{L}\p{N}]+/gu, " ")
    .split(/\s+/)
    .filter((t) => t && t.length > 1 && !STOP.has(t));
}

function expand(ts: string[]): Set<string> {
  const out = new Set(ts);
  for (const t of ts) {
    for (const [canon, list] of Object.entries(SYNONYMS)) {
      const norm = list.map((x) => x.normalize("NFD").replace(/[\u0300-\u036f]/g, "").toLowerCase());
      if (t === canon || norm.includes(t)) {
        out.add(canon);
        for (const x of norm) out.add(x);
      }
    }
  }
  return out;
}

function citeForIndicator(stage: StageId): string[] {
  const ids = new Set<string>();
  const nat = indicatorForStage(dataset.regions.national, stage);
  if (nat?.source_id) ids.add(nat.source_id);
  if (nat?.target_source_id) ids.add(nat.target_source_id);
  return [...ids];
}

function collectRecSources(id?: string): string[] {
  const recs = id ? [recById(id)].filter(Boolean) : dataset.recs.recommendations;
  const ids: string[] = [];
  for (const r of recs) {
    if (!r) continue;
    ids.push(...(r.evidence_source_ids ?? []));
    if (r.expected_effect?.source_id) ids.push(r.expected_effect.source_id);
    if (r.cost?.source_id) ids.push(r.cost.source_id);
  }
  return [...new Set(ids)];
}

function unique(ids: string[]): string[] {
  return [...new Set(ids.filter(Boolean))];
}


function regionMatch(expanded: Set<string>, original: string): Region | undefined {
  const q = original.toLowerCase();
  let best: Region | undefined;
  let bestScore = 0;
  for (const r of dataset.regions.regions) {
    const hay = [r.id, r.slug, r.name, r.name_fi, r.name_official_en, r.name_official_fi]
      .filter(Boolean)
      .join(" ")
      .toLowerCase();
    const hayNorm = hay.normalize("NFD").replace(/[\u0300-\u036f]/g, "");
    let score = 0;
    if (q.includes(r.name.toLowerCase()) || (r.name_fi && q.includes(r.name_fi.toLowerCase()))) score += 5;
    if (expanded.has(r.id) || (r.slug && expanded.has(r.slug))) score += 4;
    for (const t of expanded) {
      if (t.length > 3 && hayNorm.includes(t)) score += 1;
    }
    if (score > bestScore) {
      bestScore = score;
      best = r;
    }
  }
  return bestScore >= 3 ? best : undefined;
}

function stageMatch(expanded: Set<string>): StageId | undefined {
  for (const s of STAGE_ORDER) {
    if (expanded.has(s)) return s;
    const synonyms = SYNONYMS[s] ?? [];
    if (synonyms.some((x) => expanded.has(x.normalize("NFD").replace(/[\u0300-\u036f]/g, "").toLowerCase()))) {
      return s;
    }
  }
  return undefined;
}

function surgerySameDayNote(): string {
  const caveat = dataset.hero.headlines?.find((h) => h.id === "lung_dx_to_surgery_days")?.caveat;
  if (typeof caveat === "string" && /same-day|diagnosis date|lower quartile 0/i.test(caveat)) return caveat;
  return "In the North at least a quarter of these surgical patients have surgery on the diagnosis date (lower quartile 0 days), so the low median partly reflects how diagnosis is dated.";
}

function answerWidest(): AnalystAnswer {
  return {
    title: "The widest lung-cancer gap we can show is the age-adjusted curative-treatment share",
    paragraphs: [
      "Men in Lapland: about 16.2% reach curative lung-cancer treatment within 12 months (95% CI 12.7–20.4). Vantaa-Kerava: about 29.8% (95% CI 24.2–36.1). Women: about 23.1% (95% CI 17.9–29.0) vs about 39.7% (95% CI 33.1–47.0). These are chart estimates, age-adjusted, not stage-adjusted, not survival (Kuva 16, ±1 pp). The confidence intervals do not overlap for either sex.",
      "No county publishes 6-week referral-to-treatment compliance, so a widest-gap ranking cannot be computed on the official Goal 3 clock. " + tasanClockNote(),
      "All-specialty primary-to-specialist referral times (Sotkanet 13) are context only. They are not a lung-cancer indicator and are not the widest gap this demo leads with.",
      "Separately, Taulukko 4.1 (diagnosis to surgery, 2018 to mid-2022, by home region, surgical patients only, ~11%) gives YTA medians of 13.5 days in North Finland and 46 days in South Finland. " + surgerySameDayNote(),
    ],
    source_ids: unique(["src-lung-2026-kuva16", "src-thl-2016", "src-strategy-2026", "src-lung-2024-yta", "src-sotkanet-13", ...(dataset.keyMessage.source_ids ?? [])]),
    region_ids: ["21", "04"],
  };
}

function answerCompliance(): AnalystAnswer {
  return {
    title: "No county publishes 6-week compliance",
    paragraphs: [
      "That is why Tasan exists. Goal 3 requires that patients start treatment within target timeframes. The official generic limit is six weeks (42 days) from referral arrival to first treatment. No public statistic reports that rate for any wellbeing services county.",
      tasanClockNote(),
      "Taulukko 4.1 is not that clock: it is diagnosis to first treatment, 2018 to mid-2022, by home region, and the surgery row covers surgical patients only (~11%).",
      "The centrepiece action is T3: the Tasan waiting-time tracker with a day-28 alert and a named nurse navigator. When the alert fires, the navigator triggers T1 (lung fast-track) and T2 (regional video tumour board).",
    ],
    source_ids: unique(["src-thl-2016", "src-thl-2017", "src-strategy-2026", "src-roadmap-2026", "src-lung-2024-yta"]),
  };
}

function answerSurgeryTimes(): AnalystAnswer {
  const ytas = dataset.hero.yta_waits ?? [];
  const bullets = ytas.map((y) => {
    const s = y.modalities.surgery;
    const d = y.modalities.drug;
    return `${y.name_fi}: surgery median ${s?.median} d (IQR ${s?.q1}–${s?.q3}); drug-therapy median ${d?.median} d (IQR ${d?.q1}–${d?.q3}).`;
  });
  return {
    title: "Diagnosis to surgery, 2018 to mid-2022, by home region, surgical patients only (~11%)",
    paragraphs: [
      "These are the published Taulukko 4.1 medians. The interval starts at the Cancer Registry diagnosis date, not at referral. Only patients whose first treatment within six months was that modality are included; the surgery subset is about 11% of patients. Other counties have no public figure.",
      "Drug-therapy waits from the same table are shown so the surgery row is not cherry-picked. Pohjois-Suomi is fastest to surgery but slower to systemic drug therapy than Etelä-Suomi. Do not read these YTA times as a North-versus-South story, and do not chain them with the 2019–2023 county curative-treatment shares into one patient journey.",
      surgerySameDayNote(),
    ],
    bullets,
    source_ids: unique(["src-lung-2024-yta"]),
  };
}

function answerFurthest(stage: StageId): AnalystAnswer {
  const rows = furthestFromTarget(stage, 6);
  const lab = dataset.regions.stages.find((s) => s.id === stage)?.label ?? stage;
  const ind = indicatorForStage(dataset.regions.national, stage);
  return {
    title: `Counties furthest from the ${lab.toLowerCase()} mark`,
    paragraphs: [
      `Indicator: ${ind?.label ?? lab}. National: ${formatValue(ind?.value ?? null, ind?.unit ?? "", ind?.decimals ?? 0)}. Target: ${formatValue(ind?.target ?? null, ind?.unit ?? "", ind?.decimals ?? 0)}${ind?.target_note ? " — " + ind.target_note : ""}.`,
    ],
    bullets: rows.map((r) => {
      const gap = r.gap;
      return `${r.region.name}: ${formatValue(r.value, ind?.unit ?? "", ind?.decimals ?? 0)} (${gap > 0 ? `${gap.toFixed(ind?.decimals ?? 0)} points behind the target` : "at or above the target"}).`;
    }),
    source_ids: unique(citeForIndicator(stage)),
    region_ids: rows.map((r) => r.region.id),
  };
}

function answerAction(): AnalystAnswer {
  const recs = dataset.recs.recommendations ?? [];
  const topIds = featuredRecIds();
  const top = topIds.map((id) => recs.find((r) => r.id === id) ?? recById(id)).filter(Boolean);
  const primary = recById(leadRecId()) ?? top[0] ?? recs[0];
  const paragraphs: string[] = [];
  if (dataset.keyMessage.what_to_do) paragraphs.push(dataset.keyMessage.what_to_do);
  paragraphs.push(
    "T3 is the lead recommendation and the app's centrepiece: the Tasan waiting-time clock with a day-28 alert and nurse navigator. T1 (lung fast-track) and T2 (Oulu video tumour board) are the actions the T3 alert triggers. Simulator day-cuts and share lifts are user-set assumptions, not forecast effects. KPI targets are proposed peer benchmarks.",
  );
  paragraphs.push(tasanClockNote());
  if (primary) {
    paragraphs.push(`${primary.id}. ${primary.title}. ${primary.what || primary.action || ""}`);
    if (primary.owner) paragraphs.push(`Owner: ${primary.owner}`);
    if (primary.who_implements) paragraphs.push(`Who implements: ${primary.who_implements}`);
    const kpi = primary.kpis?.[0] ?? primary.kpi;
    if (kpi?.name) {
      paragraphs.push(
        `KPI: ${kpi.name}${kpi.baseline ? " — baseline " + kpi.baseline : ""}${kpi.target ? " — proposed peer benchmark: " + kpi.target : ""}.`,
      );
    }
  }
  return {
    title: primary ? `Lead action: ${primary.id} ${primary.title}` : "Recommended actions",
    paragraphs,
    bullets: top.map((r) => (r ? `${r.id}${r.id === leadRecId() ? " (lead)" : " (triggered by the T3 alert)"}. ${r.title}: ${r.what || r.action || ""}` : "")).filter(Boolean),
    source_ids: unique([...(dataset.keyMessage.source_ids ?? []), ...collectRecSources(primary?.id)]),
    rec_ids: top.map((r) => r!.id),
  };
}

function answerGoal3(): AnalystAnswer {
  const g3 = dataset.recs.goal3_indicators ?? [];
  const topIds = featuredRecIds();
  const recs = topIds.map((id) => recById(id)).filter(Boolean);
  return {
    title: "Goal 3 of the National Cancer Strategy 2026–2035",
    paragraphs: [
      "Goal 3 is “Varmistetaan yhdenvertainen ja vaikuttava syövänhoito” — ensure equal and effective cancer care. Official follow-up metrics include: 5-year survival of poor-prognosis cancers reaching the Nordic level; a 10% reduction in cancer mortality; and patients starting treatment within target timeframes (THL Ohjaus 21/2016).",
      "No county publishes the official 6-week (42-day) referral-to-first-treatment compliance rate. That is why Tasan exists. " + tasanClockNote(),
      "The county treatment signal in this demo is the age-adjusted 12-month curative-treatment share (Kuva 16 chart estimate, not survival and not 6-week compliance). Men in Lapland about 16.2% (95% CI 12.7–20.4) vs Vantaa-Kerava about 29.8% (95% CI 24.2–36.1); women about 23.1% (95% CI 17.9–29.0) vs about 39.7% (95% CI 33.1–47.0).",
    ],
    bullets: [
      ...g3.map((g) => `${g.label}${g.strategy_ref ? " — " + g.strategy_ref : ""}`),
      ...recs.map((r) => (r ? `${r.id} (recommended action). ${r.title}` : "")).filter(Boolean),
    ],
    source_ids: unique(["src-strategy-2026", "src-thl-2016", "src-roadmap-2026", "src-lung-2026-kuva16", ...recs.flatMap((r) => collectRecSources(r?.id))]),
    rec_ids: recs.map((r) => r!.id),
  };
}

function answerRec(recId?: string): AnalystAnswer {
  const rec = recById(recId) ?? recById(dataset.keyMessage.primary_rec_id) ?? dataset.recs.recommendations[0];
  if (!rec) {
    return { title: "No recommendations loaded", paragraphs: ["Add recs/recommendations.json."], source_ids: [] };
  }
  return {
    title: `${rec.id}. ${rec.title}`,
    paragraphs: [
      rec.what || rec.action || "",
      rec.why ? `Why: ${rec.why}` : "",
      rec.how ? `How: ${rec.how}` : "",
      rec.pilot_county ? `Pilot: ${rec.pilot_county}` : "",
      rec.cost?.label && !rec.cost.is_example ? `Cost: ${rec.cost.label}. ${rec.cost.basis ?? ""}` : "",
      "The simulator applies only user-set assumed day-cuts or percentage-point lifts to published baselines. It does not invent a 6-week on-time rate or a forecast effect size. KPI targets are proposed peer benchmarks.",
      tasanClockNote(),
    ].filter(Boolean),
    bullets: evidenceLines(rec.evidence),
    source_ids: unique(collectRecSources(rec.id)),
    rec_ids: [rec.id],
  };
}

function evidenceLines(evidence: unknown): string[] {
  if (!evidence) return [];
  if (typeof evidence === "string") return evidence.trim() ? [evidence.trim()] : [];
  const rows = Array.isArray(evidence) ? evidence : [evidence];
  const out: string[] = [];
  for (const row of rows) {
    if (typeof row === "string" && row.trim()) out.push(row.trim());
    else if (row && typeof row === "object") {
      const r = row as { claim?: string; source_title?: string; title?: string; source?: string };
      const claim = (r.claim || "").trim();
      const src = (r.source_title || r.title || r.source || "").trim();
      if (claim && src) out.push(`${claim} — ${src}`);
      else if (claim) out.push(claim);
      else if (src) out.push(src);
    }
  }
  return out;
}

function answerRegion(region: Region): AnalystAnswer {
  const yid = dataset.hero.county_yta?.[region.id];
  const yta = dataset.hero.yta_waits?.find((y) => y.id === yid);
  const surg = yta?.modalities.surgery;
  const drug = yta?.modalities.drug;
  const cur = region.indicators.find((i) => i.id === "lung_curative_share");
  const paragraphs: string[] = [
    `${region.name_official_en ?? region.name}${region.name_fi ? ` / ${region.name_official_fi ?? region.name_fi}` : ""}. The figures below are separate public signals, not a single patient journey, and this county has no published 6-week referral-to-treatment compliance rate.`,
    tasanClockNote(),
  ];
  if (surg && yta) {
    paragraphs.push(
      `Signal A (YTA, not a county measurement): ${region.name} sits in ${yta.name_fi}. Diagnosis to surgery, 2018 to mid-2022, by home region, surgical patients only (~11%): median ${surg.median} days (IQR ${surg.q1}–${surg.q3}). Drug-therapy median in the same table: ${drug?.median} days. ` + (/pohjois|north/i.test(yta.name + (yta.name_fi ?? "")) ? surgerySameDayNote() : ""),
    );
  } else {
    paragraphs.push("Signal A: no public collaborative-area diagnosis-to-treatment time is linked to this county.");
  }
  if (cur && !cur.missing && cur.men && cur.women) {
    paragraphs.push(
      `Signal B (county, 2019–2023): age-adjusted curative-treatment share, chart estimate, not stage-adjusted, not survival — men about ${cur.men.value.toFixed(1)}% (95% CI ${formatCi(cur.men.ci95?.[0], cur.men.ci95?.[1])}) / women about ${cur.women.value.toFixed(1)}% (95% CI ${formatCi(cur.women.ci95?.[0], cur.women.ci95?.[1])}).`,
    );
  } else if (cur && !cur.missing && cur.value != null) {
    paragraphs.push(
      `Signal B (county, 2019–2023): age-adjusted curative-treatment share, chart estimate — about ${Number(cur.value).toFixed(1)}%` + (cur.ci95_low != null ? ` (95% CI ${formatCi(cur.ci95_low, cur.ci95_high)})` : "") + ".",
    );
  } else {
    paragraphs.push(`Signal B: No public age-adjusted curative-treatment figure in Kuva 16 for this county. ${cur?.missing_reason ?? cur?.note ?? ""}`.trim());
  }
  const bullets: string[] = [];
  const ids: string[] = ["src-lung-2024-yta", "src-lung-2026-t11", "src-thl-2016"];
  for (const stage of STAGE_ORDER) {
    const r = indicatorForStage(region, stage);
    const n = indicatorForStage(dataset.regions.national, stage);
    const lab = dataset.regions.stages.find((s) => s.id === stage)?.label ?? stage;
    if (!r || r.missing || r.value == null) {
      bullets.push(`${lab}: No public data. ${r?.missing_reason ?? r?.note ?? ""}`.trim());
      continue;
    }
    if (r.men && r.women) {
      bullets.push(
        `${lab}: men about ${r.men.value.toFixed(1)}% (95% CI ${formatCi(r.men.ci95?.[0], r.men.ci95?.[1])}) / women about ${r.women.value.toFixed(1)}% (95% CI ${formatCi(r.women.ci95?.[0], r.women.ci95?.[1])}). Chart estimate, age-adjusted, not survival. No published national age-adjusted figure in the same chart.`,
      );
    } else {
      const ci = r.ci95_low != null ? ` (95% CI ${formatCi(r.ci95_low, r.ci95_high)})` : "";
      const natText = n && !n.missing && n.value != null ? ` vs national ${formatValue(n.value, n.unit, n.decimals)}` : "";
      bullets.push(
        `${lab}: ${formatValue(r.value, r.unit, r.decimals)}${ci}${natText}. Separate cohort/year from the YTA wait times.`,
      );
    }
    if (r.source_id) ids.push(r.source_id);
    if (n?.source_id) ids.push(n.source_id);
  }
  return {
    title: `${region.name}: separate public signals`,
    paragraphs,
    bullets,
    source_ids: unique(ids),
    region_ids: [region.id],
  };
}

function answerSources(): AnalystAnswer {
  return {
    title: "Sources and limitations",
    paragraphs: [
      dataset.regions.meta.disclaimer ?? "Every number in the app is linked to a source entry.",
      dataset.recs.meta.disclaimer ?? "",
      "Click any citation chip to open the matching source in the Sources panel.",
    ].filter(Boolean),
    bullets: dataset.sources.sources.map((s) => `${s.id}: ${s.title} — ${s.publisher}${s.year ? " (" + s.year + ")" : ""}`),
    source_ids: dataset.sources.sources.map((s) => s.id),
  };
}

function detectLang(q: string): "fi" | "sv" | "en" {
  if (/[äöåÄÖÅ]/.test(q) || /\b(mikä|mitä|miksi|miten|kuinka|onko|keuhko|syöpä|hoito|maakunta|hyvinvointialue)\b/i.test(q)) return "fi";
  if (/\b(vad|varför|vilken|hur|cancer|lungcancer|vård|landskap|välfärdsområde)\b/i.test(q) && !/\b(the|what|where|how)\b/i.test(q)) return "sv";
  return "en";
}

function outOfScopeAnswer(q: string): AnalystAnswer | null {
  const other = /\b(breast|prostate|colorectal|bowel|cervical|ovarian|melanoma|skin cancer|rinta|rintasyöpä|eturauhas|suolistosyöpä|kohdunkaula|bröst|prostata|tjocktarm)\b/i;
  const lung = /\b(lung|keuhko|lungcancer|keuhkosyöp)\b/i;
  if (other.test(q) && !lung.test(q)) {
    const lang = detectLang(q);
    const paragraphs =
      lang === "fi"
        ? ["Tasan kattaa tässä demossa vain keuhkosyövän julkiset indikaattorit. Tätä kysymystä ei voi vastata tämän aineiston perusteella."]
        : lang === "sv"
          ? ["Tasan täcker i denna demo endast offentliga indikatorer för lungcancer. Den här frågan kan inte besvaras utifrån det här materialet."]
          : ["Tasan covers lung cancer only in this demo. That question is outside the bundled data, so this tool cannot answer it."];
    return { title: lang === "fi" ? "Kysymys on aineiston ulkopuolella" : lang === "sv" ? "Frågan ligger utanför materialet" : "This question is outside the data", paragraphs, source_ids: [] };
  }
  return null;
}

export function answerQuery(query: string, selectedRegionId: string | null): AnalystAnswer {
  const q = query.trim();
  const scoped = outOfScopeAnswer(q);
  if (scoped) return scoped;
  if (!q) {
    return {
      title: "Ask about the loaded dataset",
      paragraphs: [
        "The offline analyst retrieves from the JSON bundled in this app (regions, recommendations, sources). It does not call a network model. Try a suggested question, or name a county, a pathway stage, Goal 3, or an action.",
      ],
      source_ids: [],
    };
  }
  const ts = tokens(q);
  const expanded = expand(ts);
  const region = regionMatch(expanded, q) ?? (/\b(this|selected|tämä|tama) (county|region|alue)/i.test(q) ? regionById(selectedRegionId) : undefined);
  const stage = stageMatch(expanded);

  const recHit = dataset.recs.recommendations.find((r) => {
    const bag = `${r.id} ${r.title} ${r.what ?? ""} ${r.action ?? ""}`.toLowerCase();
    return ts.some((t) => t.length > 3 && bag.includes(t)) && (expanded.has("simulate") || expanded.has("action") || expanded.has("impact") || bag.includes(q.toLowerCase().slice(0, 24)));
  });

  if (/6411|6410|2676|primary-care wait|primary care wait|avohilmo/i.test(q)) {
    return {
      title: "Sotkanet 6411 is not shown",
      paragraphs: [
        dataset.hero.excluded?.sotkanet_6411
          || "Sotkanet 6411 (and its predecessor 2676, and 6410) measure all-cause primary-care physician waits, not cancer, and are unreliable for Vantaa-Kerava and Helsinki because of Avohilmo data gaps. They are excluded from this app.",
      ],
      source_ids: [],
    };
  }
  if (/6[ -]?week|six week|42[ -]?day|compliance|on-time rate|within (the )?target time/i.test(q)) return answerCompliance();
  if (/taulukko\s*4|diagnosis to surgery|surgery median|4\.1/i.test(q)) return answerSurgeryTimes();
  if (/curative|survival|taulukko\s*11|kuva\s*16/i.test(q) && !region) {
    return {
      title: "Age-adjusted curative-treatment share (chart estimate) — not survival",
      paragraphs: [
        "The figure this demo leads with is the age-adjusted share of lung-cancer patients with a curative-treatment record within 12 months, read from Kuva 16 (±1 pp): men in Lapland about 16.2% (95% CI 12.7–20.4) vs Vantaa-Kerava about 29.8% (95% CI 24.2–36.1); women about 23.1% (95% CI 17.9–29.0) vs about 39.7% (95% CI 33.1–47.0). Not stage-adjusted, not survival. Confidence intervals do not overlap for either sex.",
        "Taulukko 11 is a different, crude measure. It is shown only as a secondary line on the hero card, not as the county or map figure.",
        "Do not chain this 2019–2023 county series with the 2018–mid-2022 YTA diagnosis-to-treatment times into one patient journey.",
      ],
      source_ids: unique(["src-lung-2026-kuva16", "src-lung-2026-t11"]),
    };
  }
  if (expanded.has("goal3") || /goal\s*3|tavoite\s*3/i.test(q)) return answerGoal3();
  if (expanded.has("source") && !expanded.has("action")) return answerSources();
  if (expanded.has("widest") || ((expanded.has("gap") || expanded.has("where")) && !region && !stage)) {
    if (/widest|largest|where.*gap|gap.*emerge|bottleneck/i.test(q) || expanded.has("gap")) return answerWidest();
  }
  if (expanded.has("worst") || /furthest|lag|behind|lowest/i.test(q)) return answerFurthest(stage ?? widestStage().stage);
  if (expanded.has("simulate") || /fully implemented|what would happen|impact of/i.test(q)) return answerRec(recHit?.id);
  if (expanded.has("action") || /should .* do|what to do|first action|recommend/i.test(q)) return answerAction();
  if (region) return answerRegion(region);
  if (stage) return answerFurthest(stage);
  if (recHit) return answerRec(recHit.id);
  if (expanded.has("gap") || expanded.has("where")) return answerWidest();

  // fallback: keyword score over recs + stages + regions
  const scored: { score: number; fn: () => AnalystAnswer }[] = [];
  scored.push({ score: overlapScore(expanded, "gap pathway stage spread national"), fn: answerWidest });
  scored.push({ score: overlapScore(expanded, "goal strategy equal effective hoito"), fn: answerGoal3 });
  scored.push({ score: overlapScore(expanded, "cost owner kpi implement action"), fn: answerAction });
  const top = scored.sort((a, b) => b.score - a.score)[0];
  if (top && top.score > 0) return top.fn();

  return {
    title: "No direct match",
    paragraphs: [
      "The offline analyst did not find a strong match in the loaded JSON. Try a suggested question, or use words such as a county name, detection, referral, diagnosis, treatment, Goal 3, or the title of an action.",
    ],
    source_ids: [],
  };
}

function overlapScore(expanded: Set<string>, bag: string): number {
  return bag.split(/\s+/).filter((t) => expanded.has(t)).length;
}

export function sourceLine(id: string): string {
  const s = sourceById(id);
  if (!s) return id;
  const year = s.year ? ` (${s.year})` : "";
  return `${s.title} — ${s.publisher}${year}`;
}
