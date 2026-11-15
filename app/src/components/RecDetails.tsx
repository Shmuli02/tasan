import { TargetCaveat } from "./Cite";
import { tasanClockNote } from "../lib/data";
import type { CostRange, OwnerRole, Recommendation, StopGo } from "../types";

function present(v: unknown): boolean {
  if (v == null) return false;
  if (typeof v === "string") return v.trim().length > 0;
  if (Array.isArray(v)) return v.some(present);
  if (typeof v === "object") return Object.values(v as object).some(present);
  return true;
}

function asLines(v: unknown): string[] {
  if (!present(v)) return [];
  if (typeof v === "string") return [v];
  if (Array.isArray(v)) return v.flatMap(asLines);
  if (typeof v === "object") return Object.values(v as object).flatMap(asLines);
  return [String(v)];
}

function euros(n: number, currency = "EUR"): string {
  try {
    return new Intl.NumberFormat("fi-FI", { style: "currency", currency, maximumFractionDigits: 0 }).format(n);
  } catch {
    return `${n} ${currency}`;
  }
}

export function RecDetails({ rec }: { rec: Recommendation }) {
  const cost = rec.cost_range ?? undefined;
  const owner = rec.owner_role ?? undefined;
  const stop = rec.stop_go ?? undefined;
  const exists = rec.already_exists;
  const framing = rec.kpi_framing;
  const design = rec.design;
  const itemCaveat = typeof rec.target_times_caveat === "string" ? rec.target_times_caveat.trim() : "";
  const showClock = Boolean(itemCaveat) || mentionsClock(rec);
  if (
    !present(cost) &&
    !present(owner) &&
    !present(stop) &&
    !present(exists) &&
    !present(framing) &&
    !present(design) &&
    !showClock
  ) {
    return null;
  }
  return (
    <div className="mt-3 space-y-2 text-xs leading-relaxed text-ink">
      {showClock ? (
        <div>
          <TargetCaveat compact />
          {itemCaveat && itemCaveat !== tasanClockNote() ? <p className="mt-1 text-muted">{itemCaveat}</p> : null}
        </div>
      ) : null}
      {present(cost) && isCostRange(cost) ? <CostBlock cost={cost} /> : null}
      {present(owner) ? <OwnerBlock owner={owner} /> : null}
      {present(exists) ? (
        <p>
          <span className="font-semibold">Already exists. </span>
          {String(exists)}
        </p>
      ) : null}
      {present(stop) && isStopGo(stop) ? <StopBlock stop={stop} /> : present(stop) && typeof stop === "string" ? (
        <p>
          <span className="font-semibold">Stop / go. </span>
          {stop}
        </p>
      ) : null}
      {present(framing) ? (
        <p className="text-muted">
          <span className="font-semibold text-ink">Peer benchmark. </span>
          {String(framing)}
        </p>
      ) : null}
      {present(design) ? <DesignNotes design={design} /> : null}
    </div>
  );
}

function mentionsClock(rec: Recommendation): boolean {
  const blob = `${rec.id} ${rec.title ?? ""} ${rec.what ?? ""} ${rec.action ?? ""} ${rec.kpi_framing ?? ""}`;
  return /6[ -]?week|42[ -]?d|day-28|day 28/i.test(blob);
}

function isCostRange(v: unknown): v is CostRange {
  return Boolean(v) && typeof v === "object" && !Array.isArray(v);
}

function isStopGo(v: unknown): v is StopGo {
  return Boolean(v) && typeof v === "object" && !Array.isArray(v);
}

function CostBlock({ cost }: { cost: CostRange }) {
  const hasRange = typeof cost.low === "number" && typeof cost.high === "number";
  const unsourced = (cost.unsourced_effort ?? []).filter(Boolean);
  const condition =
    (typeof cost.condition === "string" && cost.condition) ||
    (typeof (cost as { period?: string }).period === "string" && /conditional/i.test(cost.period || "")
      ? String(cost.period)
      : "");
  const conditional = Boolean(cost.conditional) || Boolean(condition);
  return (
    <div>
      <p>
        <span className="font-semibold">{conditional ? "Conditional cost — not a firm figure. staff cost only, estimate. " : "staff cost only, estimate. "}</span>
        {hasRange ? (
          <>
            {euros(cost.low as number, cost.currency || "EUR")}–{euros(cost.high as number, cost.currency || "EUR")}
            {conditional ? <span className="text-muted"> if the condition holds; otherwise €0</span> : null}
          </>
        ) : (
          <span>No sourced euro figure</span>
        )}
        {!conditional && cost.period ? <span className="text-muted"> · {cost.period}</span> : null}
      </p>
      {condition ? <p className="mt-1 text-muted">{condition}</p> : null}
      {unsourced.length ? (
        <p className="mt-1 rounded bg-gold-soft/80 px-2 py-1 text-gold">
          <span className="font-semibold">Unsourced effort (no euro figure): </span>
          {unsourced.join("; ")}
        </p>
      ) : null}
    </div>
  );
}

function OwnerBlock({ owner }: { owner: string | OwnerRole | unknown }) {
  if (typeof owner === "string") {
    return (
      <p>
        <span className="font-semibold">Owner role. </span>
        {owner}
      </p>
    );
  }
  if (!owner || typeof owner !== "object" || Array.isArray(owner)) return null;
  const rec = owner as OwnerRole & { by_county?: Record<string, unknown> };
  const shared = roleRows(rec);
  const partners = Array.isArray(rec.partners) ? rec.partners.filter(Boolean).map(String) : [];
  const byCounty = rec.by_county && typeof rec.by_county === "object" && !Array.isArray(rec.by_county) ? rec.by_county : null;
  if (!shared.length && !partners.length && !byCounty) return null;
  return (
    <div>
      <p className="font-semibold">Owner role</p>
      {shared.length || partners.length ? (
        <ul className="mt-0.5 space-y-0.5 text-muted">
          {shared.map((r) => (
            <li key={r.label}>
              <span className="text-ink">{r.label}:</span> {r.value}
            </li>
          ))}
          {partners.length ? (
            <li>
              <span className="text-ink">Partners:</span> {partners.join("; ")}
            </li>
          ) : null}
        </ul>
      ) : null}
      {byCounty
        ? Object.entries(byCounty).map(([county, block]) => (
            <div key={county} className="mt-2 rounded-lg bg-paper px-2 py-1.5">
              <p className="font-semibold text-ink">{county}</p>
              {typeof block === "string" ? (
                <p className="text-muted">{block}</p>
              ) : (
                <ul className="mt-0.5 space-y-0.5 text-muted">
                  {roleRows(block).map((r) => (
                    <li key={r.label}>
                      <span className="text-ink">{r.label}:</span> {r.value}
                    </li>
                  ))}
                </ul>
              )}
            </div>
          ))
        : null}
    </div>
  );
}

function roleRows(owner: unknown): { label: string; value: string }[] {
  if (!owner || typeof owner !== "object" || Array.isArray(owner)) return [];
  const labels: Record<string, string> = {
    signer: "Signer",
    owner_of_delayed_patients: "Owner of delayed patients",
    data_owner: "Data owner",
    operational_sponsor: "Operational sponsor",
    clinical_lead: "Clinical lead",
  };
  const rows: { label: string; value: string }[] = [];
  for (const [k, label] of Object.entries(labels)) {
    const v = (owner as Record<string, unknown>)[k];
    if (typeof v === "string" && v.trim()) rows.push({ label, value: v });
  }
  return rows;
}

function StopBlock({ stop }: { stop: StopGo }) {
  const go = asLines(stop.go_if_all);
  const halt = asLines(stop.stop_or_redesign_if_any);
  const gate = formatGate(stop.week1_gate);
  return (
    <div>
      {gate ? (
        <p className="rounded-lg border border-gold/40 bg-gold-soft px-2 py-1.5">
          <span className="font-semibold">Week-1 gate. </span>
          {gate}
        </p>
      ) : null}
      <p className="mt-1">
        <span className="font-semibold">Stop / go</span>
        {stop.review_day != null ? <span className="text-muted"> · review day {String(stop.review_day)}</span> : null}
        {stop.decision_owner ? <span className="text-muted"> · {stop.decision_owner}</span> : null}
      </p>
      {go.length ? <p className="text-muted">Go if: {go.join("; ")}</p> : null}
      {halt.length ? <p className="text-muted">Stop or redesign if: {halt.join("; ")}</p> : null}
    </div>
  );
}

function formatGate(v: unknown): string {
  if (!present(v)) return "";
  if (typeof v === "string") return v;
  return asLines(v).join(" ");
}

function DesignNotes({ design }: { design: unknown }) {
  const lines = asLines(design);
  if (!lines.length) return null;
  return (
    <aside className="rounded-lg border border-dashed border-navy/30 bg-navy/5 px-3 py-2">
      <p className="text-[10px] font-semibold uppercase tracking-wider text-navy">Design notes · not a cost or a KPI</p>
      <ul className="mt-1 list-disc space-y-1 pl-4">
        {lines.map((line) => (
          <li key={line.slice(0, 80)}>{line}</li>
        ))}
      </ul>
    </aside>
  );
}
