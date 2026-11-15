export function ComingTab({
  lang,
  title,
  line,
  dark,
}: {
  lang: "en" | "fi";
  title: string;
  line: string;
  dark?: boolean;
}) {
  const fi = lang === "fi";
  return (
    <div className={`flex min-h-[28rem] items-center justify-center rounded-[22px] p-8 ${dark ? "bg-[var(--tz-console-bg)] text-[var(--tz-console-text)]" : "bg-card border border-line"}`}>
      <div className="max-w-md text-center">
        {dark ? <span className="tz-badge tz-badge--example mb-3">EXAMPLE</span> : null}
        <h2 className="display text-[32px] font-bold">{title}</h2>
        <p className={`mt-2 text-[15px] ${dark ? "text-[var(--tz-console-text-2)]" : "text-[var(--tz-ink-2)]"}`}>{line}</p>
        <p className={`mt-4 text-[13px] font-semibold uppercase tracking-wide ${dark ? "text-[var(--tz-console-text-3)]" : "text-[var(--tz-ink-3)]"}`}>{fi ? "Tulossa" : "Coming"}</p>
      </div>
    </div>
  );
}
