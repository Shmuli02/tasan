# Tasan UX review (JN UX Critic, Sat 14 Nov 20:10 EET)
Live https://petaled-trowel-90.beacon.host/ and offline dist-offline/index.html were reviewed hands-on, as a county director with 2 minutes. Both builds are identical. Screenshots are in this folder (01-16).

## Verdict
The owner's instinct is right. The data is honest and well sourced, but the page reads like a research appendix: about 66k characters of text and two different Lapland number pairs on screen 1. A director gets the message ("nobody measures the 6-week clock"), but nothing *moves* and nothing feels like a product. There is no wow moment yet.
AI: it does not feel AI-powered. The "AI ANALYST" says "Deterministic retrieval over the bundled JSON" (keyword and synonym matching in lib/analyst.ts), next to a greyed "Online LLM (not configured)" checkbox. In testing:
- "Why is Lapland behind?" returned a generic referral list that never mentions Lapland.
- The Finnish question was answered in English with no action.
- "Breast cancer waiting times in Helsinki" silently returned lung data.
A judge who types one question will see through it, so this is a real stage risk.

## Ranked top 10
1. **Rebuild screen 1 around one message and one picture** (02:00 test). Effort M, 2-3 h. Screenshot 01.
   - Wrong: a 4-line serif sentence with jargon (Goal 3 clock, day-28 alert, nurse navigator), raw source IDs, a hero "number" written as a sentence, and a caveat paragraph.
   - Fix: on the left, a Finland map coloured by curative-treatment share. On the right, one huge line: "Lung cancer in Lapland: 16% get curative treatment. Vantaa-Kerava: 30%." Under it, one sentence: "And no county measures whether patients start treatment within 6 weeks." Then one button: "See what your county can do". Show the source as a single small line ("Cancer Registry 2026, age-adjusted, men"). Women, CIs and the caveats go behind an (i).
2. **Make the Tasan clock something you can see working. This is the wow.** Effort M-L, 3-4 h. Screenshot 04.
   - Wrong: the product (tracker + day-28 alert + navigator) exists only as a paragraph.
   - Fix: a mock county dashboard with 12-20 EXAMPLE patients as horizontal bars (referral to today, coloured green, amber at day 21, red at day 28). Press "Play": the days tick, one bar crosses day 28, an alert card pops up ("Patient #7, day 28, no treatment decision. Blocker: CT slot. Navigator: assigned."), and a counter reads "% started within 6 weeks: 64%". Label it EXAMPLE DATA in big letters. This is the 15-second moment judges remember, and it answers "early-warning system", one of the brief's own suggested solutions.
3. **"Pick your county" gives a one-screen brief.** Effort M, 2 h. Screenshots 07-09.
   - Wrong: the county panel lists four indicators and leaves the director to interpret mixed signals (Lapland is above national on detection and referral, far below on curative share).
   - Fix: a county dropdown on screen 1. The result is one card: "Your biggest gap: curative treatment (18.5% vs 27.0% national). What you can't see: 6-week compliance. Start with: Tasan clock pilot, about €20-29k for 90 days, owner X, KPI Y." Add a printable/PDF button ("take this to your board").
4. **Make the AI real, or stop calling it AI.** Effort M with an LLM, S for the guards only. Screenshots 10-12.
   - Wrong: canned answers, the off-topic question is answered wrongly, there's no Finnish, and the disabled LLM checkbox looks broken.
   - Fix: wire an LLM that answers only from the bundled JSON, must cite source IDs, answers in the question's language and refuses out-of-scope questions ("Tasan covers lung cancer only"). Keep the deterministic engine as the offline fallback.
   - Best demo use: the LLM writes the county brief from fix 3 ("AI drafts your board memo").
   - Minimum if there's no time: delete the checkbox, add an out-of-scope refusal, route "why" plus a county name to that county's breakdown, and rename the section "Ask the data".
5. **Cut about 70% of visible text.** Effort S-M, 1-2 h. Screenshots 01, 03, 05.
   - Wrong: walls of tiny grey caveats; labels like SIGNAL · LUNG_TREATED_WITHIN_2_MONTHS and LUNG_STAGE_MISSING; "IQR 0–44"; tags like "lung-2024-yta, thl-2016…".
   - Fix: one caveat line per number at most, with the rest behind "Method & caveats" disclosures. Use human labels ("Treated within 2 months"). Remove raw IDs from the face.
   - The rule: if a director wouldn't read it aloud, it's collapsed by default. The sources stay one click away, so the transparency points are kept.
6. **One Lapland number pair, not two.** Effort S. Screenshot 01.
   - Wrong: 16.2 vs 29.8 (age-adjusted) and 18.5 vs 35.6 (crude) both appear on screen 1, which looks like inconsistency.
   - Fix: show the age-adjusted pair only. Crude goes in the details. The map and county card should label which one they show.
7. **Map honesty and legibility.** Effort M, 1-2 h. Screenshots 04, 07-08.
   - Wrong: counties are coloured by collaborative-area YTA medians, so four South counties all show 46.0 d, which reads as county data despite the disclaimer. Labels are truncated ("Vantaa-Kerav…", "South Ostrob…") or overlap in the south. The legend gradient has no units. The page jumps on click.
   - Fix: colour by the county-level curative share (crude Taulukko 11 is county level). Show the 13.5/46 d figure as a separate 5-area note. Fix label collisions (use leader lines, or labels only on hover plus the list). Put units in the legend. Don't scroll on click.
8. **Kill or rebuild "Start here".** Effort S. Screenshots 02-05.
   - Wrong: the panel is mostly off-screen, the page lands mid-scroll, and step 4 lands on the rec cards, not the Simulator.
   - Fix: if fix 1 happens, delete the feature, because the page itself is the 2-minute path. Otherwise make each step a full-viewport snap section.
9. **Recommendation cards: 4 lines on the face.** Effort S. Screenshot 05.
   - Fix: show action, owner, cost, the KPI, and Goal 3 chip on the face. Put the design notes, owner-role lists, "holder not verified" and "assumed to exist; not priced" behind "Details". Internal-sounding caveats on the face make the plan look unfinished.
10. **Housekeeping before freeze.** Effort S.
    - Fix the console 404 on load.
    - Remove the off-topic sources from the lung source list (NHS stats PDF, colorectal screening page), or group them under "context".
    - The Analyst pill says "OFFLINE MODE" even live. Hide it online.
    - Mobile (390px) is untested because my browser can't emulate it. The builder should check it with devtools.
    - At 150% the hero numbers drop below the fold. At 67% (projector) the headline and numbers are fine but the caveats are unreadable, which fix 5 solves.

## Stage risks
- Live typing into the Analyst is the biggest one (fix 4).
- Scrolling a 66k-character page on stage.
- Two pairs of Lapland numbers invite a "which is it?" question.

## If only 3 things get done
Fixes 1, 2 and 4-minimum. Screen 1 becomes one message plus the map, the clock demo gives the wow, and nobody can expose the Analyst.
