/** EXAMPLE cohort only — illustrative, not a forecast, not official statistics. */
export const WEEK6 = 42;
export const DAY28 = 28;
export const AMBER_FROM = 21;
export const PILOT_DAYS = 90;

export type ExPatient = {
  id: string;
  initials: string;
  nav: string | null;
  day0: number;
  treatWithout: number | null;
  treatWith: number | null;
  step0: "Referral" | "Imaging" | "Biopsy" | "MDT" | "Treatment";
  blocker: string | null;
  alertKind: "ct" | "biopsy" | "mdt" | null;
};

/**
 * All 14 patients start before day 28.
 * Without Tasan, 6/14 start treatment by day 42.
 * With Tasan, the 3 day-28 alerts are acted on and 9/14 start by day 42.
 */
export const EXAMPLE_PATIENTS: ExPatient[] = [
  { id: "P-0207", initials: "AK", nav: "AK", day0: 24, treatWithout: null, treatWith: 35, step0: "Imaging", blocker: "CT slot", alertKind: "ct" },
  { id: "P-0193", initials: "MV", nav: "MV", day0: 22, treatWithout: null, treatWith: 38, step0: "Biopsy", blocker: "Biopsy result", alertKind: "biopsy" },
  { id: "P-0188", initials: "AK", nav: "AK", day0: 20, treatWithout: null, treatWith: 40, step0: "MDT", blocker: "MDT slot", alertKind: "mdt" },
  { id: "P-0211", initials: "", nav: null, day0: 18, treatWithout: 26, treatWith: 26, step0: "Imaging", blocker: "PET-CT", alertKind: null },
  { id: "P-0214", initials: "AK", nav: "AK", day0: 12, treatWithout: 26, treatWith: 26, step0: "Imaging", blocker: null, alertKind: null },
  { id: "P-0201", initials: "MV", nav: "MV", day0: 16, treatWithout: 27, treatWith: 27, step0: "MDT", blocker: null, alertKind: null },
  { id: "P-0215", initials: "AK", nav: "AK", day0: 8, treatWithout: 22, treatWith: 22, step0: "Treatment", blocker: null, alertKind: null },
  { id: "P-0218", initials: "", nav: null, day0: 3, treatWithout: 19, treatWith: 19, step0: "Referral", blocker: null, alertKind: null },
  { id: "P-0229", initials: "MV", nav: "MV", day0: 10, treatWithout: 24, treatWith: 24, step0: "Biopsy", blocker: null, alertKind: null },
  { id: "P-0185", initials: "AK", nav: "AK", day0: 15, treatWithout: null, treatWith: null, step0: "Referral", blocker: null, alertKind: null },
  { id: "P-0199", initials: "MV", nav: "MV", day0: 11, treatWithout: null, treatWith: null, step0: "Imaging", blocker: "CT slot", alertKind: null },
  { id: "P-0219", initials: "", nav: null, day0: 6, treatWithout: null, treatWith: null, step0: "Biopsy", blocker: null, alertKind: null },
  { id: "P-0204", initials: "AK", nav: "AK", day0: 9, treatWithout: null, treatWith: null, step0: "MDT", blocker: "MDT slot", alertKind: null },
  { id: "P-0221", initials: "MV", nav: "MV", day0: 4, treatWithout: null, treatWith: null, step0: "Referral", blocker: null, alertKind: null },
];

export const WITHOUT_ON_TIME = EXAMPLE_PATIENTS.filter((p) => p.treatWithout != null && p.treatWithout <= WEEK6).length;
export const WITH_ON_TIME = EXAMPLE_PATIENTS.filter((p) => p.treatWith != null && p.treatWith <= WEEK6).length;

export function dayOf(p: ExPatient, t: number, withTasan: boolean): number {
  const treatAt = withTasan ? p.treatWith : p.treatWithout;
  const elapsed = p.day0 + t;
  if (treatAt != null && elapsed >= treatAt) return treatAt;
  return elapsed;
}

export function treated(p: ExPatient, t: number, withTasan: boolean): boolean {
  const treatAt = withTasan ? p.treatWith : p.treatWithout;
  return treatAt != null && p.day0 + t >= treatAt;
}

export function crossed28(p: ExPatient, t: number): boolean {
  return p.day0 < DAY28 && p.day0 + t >= DAY28 && (p.treatWithout == null || p.treatWithout >= DAY28) && (p.treatWith == null || p.treatWith >= DAY28);
}

export function alertPatientsAt(t: number): ExPatient[] {
  return EXAMPLE_PATIENTS.filter((p) => p.alertKind && p.day0 + t >= DAY28 && !treated(p, t, true) && dayOf(p, t, true) >= DAY28);
}

export function alertsFiredBy(t: number): ExPatient[] {
  return EXAMPLE_PATIENTS.filter((p) => p.alertKind && p.day0 + t >= DAY28);
}

/** Pilot-day offsets when each alert first fires (patient hits day 28). */
export const ALERT_DAYS = EXAMPLE_PATIENTS.filter((p) => p.alertKind).map((p) => DAY28 - p.day0).sort((a, b) => a - b);

export function onTimeCount(t: number, withTasan: boolean): number {
  return EXAMPLE_PATIENTS.filter((p) => treated(p, t, withTasan) && (withTasan ? p.treatWith! : p.treatWithout!) <= WEEK6).length;
}

export function stepIndex(p: ExPatient, t: number, withTasan: boolean): number {
  if (treated(p, t, withTasan)) return 4;
  const d = dayOf(p, t, withTasan);
  if (d >= 35) return 3;
  if (d >= 28) return 2;
  if (d >= 21) return 1;
  return 0;
}

export const STEPS = ["Referral", "Imaging", "Biopsy", "MDT", "Treatment"] as const;

export type FeedEvent = { t: number; id: string; alert?: boolean; en: string; fi: string };

/** EXAMPLE playback events — illustrative only, not a forecast. */
export function exampleFeedEvents(): FeedEvent[] {
  const ev: FeedEvent[] = [
    {
      t: 0,
      id: "start",
      en: "EXAMPLE playback started · 14 patients on the pathway",
      fi: "ESIMERKKI-toisto alkoi · 14 potilasta polulla",
    },
  ];
  for (const p of EXAMPLE_PATIENTS) {
    if (p.treatWith != null) {
      const at = p.treatWith - p.day0;
      if (at >= 0 && at <= 22) {
        ev.push({
          t: at,
          id: `tx-${p.id}`,
          en: `EXAMPLE ${p.id} started treatment (with Tasan)`,
          fi: `ESIMERKKI ${p.id} aloitti hoidon (Tasanin kanssa)`,
        });
      }
    }
    if (p.alertKind) {
      const at = DAY28 - p.day0;
      ev.push({
        t: at,
        id: `alert-${p.id}`,
        alert: true,
        en: `EXAMPLE ${p.id} DAY-28 ALERT ${p.blocker ?? "no treatment decision"}`,
        fi: `ESIMERKKI ${p.id} PÄIVÄ-28 HÄLYTYS ${p.blocker ?? "ei hoitopäätöstä"}`,
      });
    }
  }
  ev.push(
    { t: 2, id: "img", en: "EXAMPLE navigator reviewing open imaging slots", fi: "ESIMERKKI navigator tarkistaa avoimet kuvantamisajat" },
    { t: 7, id: "mdt", en: "EXAMPLE MDT list refreshed", fi: "ESIMERKKI MDT-lista päivitetty" },
    { t: 11, id: "nav2", en: "EXAMPLE second navigator shift picks up biopsy follow-up", fi: "ESIMERKKI toinen navigator hoitaa koepalan seurannan" },
    { t: 14, id: "wk2", en: "EXAMPLE week-2 pathway review", fi: "ESIMERKKI viikon 2 polun katselmus" },
    { t: 18, id: "slot", en: "EXAMPLE CT slot released and rebooked for an alerted patient", fi: "ESIMERKKI CT-aika vapautui ja varattiin hälytetylle potilaalle" },
    { t: 21, id: "wk3", en: "EXAMPLE week-3 huddle: still-open day-28 cases", fi: "ESIMERKKI viikon 3 tilanne: avoimet päivä-28-tapaukset" },
  );
  ev.sort((a, b) => a.t - b.t || a.id.localeCompare(b.id));
  return ev;
}

export function feedEventsUpTo(
  t: number,
  fi: boolean,
  label: (day: number) => string,
): { t: number; clock: string; text: string; alert?: boolean; id: string }[] {
  return exampleFeedEvents()
    .filter((e) => e.t <= t)
    .sort((a, b) => b.t - a.t || a.id.localeCompare(b.id))
    .map((e) => ({ t: e.t, clock: label(e.t), text: fi ? e.fi : e.en, alert: e.alert, id: e.id }));
}
