import { useMemo, useState } from "react";
import raw from "../content/pilot_brief.md?raw";

export function PilotBrief() {
  const [open, setOpen] = useState(false);
  const text = useMemo(() => cleanPilotMarkdown(raw ?? ""), []);
  const html = useMemo(() => (text.body ? renderLiteMarkdown(text.body) : ""), [text]);
  const draft = text.draft;
  if (!text.body) return null;
  return (
    <section id="pilot-brief" className="rounded-2xl border border-line bg-card p-5">
      <div className="flex flex-wrap items-center justify-between gap-2">
        <div>
          <p className="text-xs font-semibold uppercase tracking-[0.16em] text-teal">Pilot brief</p>
          <h3 className="serif mt-1 text-xl text-ink">One page per pilot county</h3>
        </div>
        <button
          type="button"
          className="rounded-full border border-line px-3 py-1 text-sm font-semibold hover:bg-paper"
          onClick={() => setOpen((v) => !v)}
        >
          {open ? "Hide brief" : "Show brief"}
        </button>
      </div>
      {open ? (
        <div className="mt-4 max-w-none text-sm leading-relaxed text-ink">
          {draft ? (
            <p className="mb-3 inline-flex rounded-full bg-gold-soft px-3 py-1 text-xs font-semibold uppercase tracking-wider text-gold">
              Draft — not signed
            </p>
          ) : null}
          <div dangerouslySetInnerHTML={{ __html: html }} />
        </div>
      ) : (
        <p className="mt-2 text-sm text-muted">Rendered from recs/pilot_brief.md. Draft for discussion; nothing has been sent to the counties.</p>
      )}
    </section>
  );
}

function escapeHtml(s: string): string {
  return s.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;").replace(/"/g, "&quot;");
}

function inline(s: string): string {
  let out = escapeHtml(s);
  out = out.replace(/\[([^\]]+)\]\((https?:[^)]+)\)/g, '<a class="text-teal underline" href="$2" target="_blank" rel="noreferrer">$1</a>');
  out = out.replace(/`([^`]+)`/g, "<code>$1</code>");
  out = out.replace(/\*\*([^*]+)\*\*/g, "<strong>$1</strong>");
  out = out.replace(/\*([^*]+)\*/g, "<em>$1</em>");
  return out;
}

function renderLiteMarkdown(src: string): string {
  const lines = src.replace(/\r\n/g, "\n").split("\n");
  const out: string[] = [];
  let i = 0;
  let list: string[] = [];
  function flushList() {
    if (!list.length) return;
    out.push("<ul class='my-2 list-disc pl-5'>" + list.join("") + "</ul>");
    list = [];
  }
  while (i < lines.length) {
    const line = lines[i];
    if (line.startsWith("|") && lines[i + 1]?.startsWith("|")) {
      flushList();
      const rows: string[] = [];
      while (i < lines.length && lines[i].startsWith("|")) {
        const cells = lines[i].split("|").slice(1, -1).map((c) => c.trim());
        const isSep = cells.every((c) => /^:?-+:?$/.test(c));
        if (!isSep) {
          const tag = rows.length === 0 ? "th" : "td";
          rows.push("<tr>" + cells.map((c) => `<${tag} class='border border-line px-2 py-1'>${inline(c)}</${tag}>`).join("") + "</tr>");
        }
        i++;
      }
      out.push("<div class='overflow-x-auto'><table class='mt-2 w-full border-collapse text-left text-xs'>" + rows.join("") + "</table></div>");
      continue;
    }
    if (/^\s*[-*] /.test(line)) {
      list.push("<li>" + inline(line.replace(/^\s*[-*] /, "")) + "</li>");
      i++;
      continue;
    }
    flushList();
    if (line.startsWith("# ")) out.push(`<h2 class='serif mt-4 text-2xl'>${inline(line.slice(2))}</h2>`);
    else if (line.startsWith("## ")) out.push(`<h3 class='serif mt-4 text-xl'>${inline(line.slice(3))}</h3>`);
    else if (line.startsWith("### ")) out.push(`<h4 class='mt-3 font-semibold'>${inline(line.slice(4))}</h4>`);
    else if (line.startsWith("---")) out.push("<hr class='my-4 border-line' />");
    else if (line.trim() === "") out.push("");
    else out.push(`<p class='mt-2'>${inline(line)}</p>`);
    i++;
  }
  flushList();
  return out.join("\n");
}

function cleanPilotMarkdown(src: string): { draft: boolean; body: string } {
  let draft = false;
  const out: string[] = [];
  for (let line of src.replace(/\r\n/g, "\n").split("\n")) {
    if (/gen_pilot_brief\.py|do not hand-edit/i.test(line)) {
      line = line.replace(/\s*Generated from[^.]*gen_pilot_brief\.py[^.]*(, so do not hand-edit)?\.?/gi, "").trim();
      if (!line || line === "*" || line === "**") continue;
    }
    const unquoted = line.replace(/^>\s?/, "");
    if (/⚠\s*DRAFT|DRAFT\s*[–-]\s*not signed/i.test(unquoted)) {
      draft = true;
      continue;
    }
    out.push(unquoted);
  }
  return { draft, body: out.join("\n").trim() };
}
