#!/usr/bin/env python3
"""Build the Tasan pitch video from slide stills + macOS `say` voice-over.

Usage:  python3 pitch/video/build_video.py
Needs:  macOS `say`, ffmpeg with libass. Output: pitch/video/tasan_pitch.mp4 (+ .srt)
Frames come from pitch/video/frames/ (rendered from the deck at 1920x1080).
"""
import json, os, re, subprocess, wave, contextlib

HERE = os.path.dirname(os.path.abspath(__file__))
FR = os.path.join(HERE, "frames")
WORK = os.path.join(HERE, "build")
os.makedirs(WORK, exist_ok=True)

VOICE_EN = "Daniel"
VOICE_FI = "Satu"
RATE = 175          # words per minute for `say`
FPS = 30
XF = 0.6            # crossfade seconds
LEAD = 0.9          # silence before narration in each scene
TAIL = 1.1          # silence after narration
GAP = 0.3           # pause between sentences

# Slide is shown at 86% inside a dark frame, leaving a caption band underneath.
SW, SH = 1652, 929
SX, SY = (1920 - SW) // 2, 22
FRAME_BG = "0x0E1628"

# (frame file, min seconds, push-in target (cx, cy, zoom) in slide px, [(voice, text), ...])
SCENES = [
    ("01_cover.png", 5.0, (960, 540, 1.04), []),
    ("02_people.png", 0, (960, 540, 1.05), [
        ("en", "Same cancer, different postcode."),
        ("en", "About 65 more lung cancer patients a year would get curative treatment if every below-average county reached the national rate."),
        ("en", "That's Cancer Registry counts for 2019 to 2023. It's illustrative, and it isn't stage-adjusted."),
        ("en", "About 12 of them a year are in Lapland."),
    ]),
    ("03_proof.png", 0, (960, 540, 1.05), [
        ("en", "And it isn't just age."),
        ("en", "Age-adjusted, about 16 in 100 men with lung cancer in Lapland have a curative-treatment record within a year, against about 30 in 100 in Vantaa-Kerava."),
        ("en", "That's a chart estimate from the 2026 Cancer Registry report. The intervals don't overlap."),
        ("en", "Women show the same gap. It's not survival."),
    ]),
    ("04_gap.png", 0, (960, 540, 1.05), [
        ("en", "Goal 3 of Finland's cancer strategy says patients must start treatment within the target times."),
        ("en", "Today no county can see that clock for its own patients."),
        ("en", "Tasan is that clock."),
    ]),
    ("05_clock.png", 0, (960, 540, 1.05), [
        ("en", "Every lung patient's clock starts when the referral arrives."),
        ("en", "On day 28 with no treatment decision, the nurse navigator gets an alert, and owns that patient."),
    ]),
    ("06_overview.png", 0, (1232, 540, 1.68), [
        ("en", "Every number in Tasan shows its source."),
        ("en", "Ask it something nobody in Finland can answer, and it says so."),
        ("en", "That missing number is the pilot."),
    ]),
    ("07_live.png", 0, (688, 540, 1.68), [
        ("en", "This is what the navigator sees: every open pathway, sorted by risk, with the blocker named."),
        ("en", "These patients are simulated."),
    ]),
    ("08_extract.png", 0, (960, 540, 1.05), [
        ("en", "To fill the clock from clinical notes, we ran an open model on a Verda GPU in Finland."),
        ("en", "The notes never leave the country, and the dates go straight into the clock."),
    ]),
    ("09_pilot.png", 0, (960, 540, 1.05), [
        ("en", "Lapland can start on Monday."),
        ("en", "The chief medical officer signs a 90-day pilot: one nurse navigator and half an analyst."),
        ("en", "In the first month we measure Lapland's own baseline, and check the registry against the hospital's records."),
        ("en", "After that, every patient with no treatment decision by day 28 goes to the navigator."),
        ("en", "On day 90, the county decides: go, or stop."),
    ]),
    ("10_honest.png", 8.0, (960, 540, 1.03), []),
    ("11_ask.png", 0, (960, 540, 1.05), [
        ("en", "Your challenge asks for a follow-up with a Finnish wellbeing services county."),
        ("en", "Our ask: help us put this brief in front of Lapland's chief medical officer."),
        ("en", "Ninety days. One clock. One nurse."),
        ("fi", "Tasan, koska hoito ei saa riippua postinumerosta."),
    ]),
]

def run(cmd):
    subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)

def wav_len(p):
    with contextlib.closing(wave.open(p)) as w:
        return w.getnframes() / w.getframerate()

def silence(path, secs):
    run(["ffmpeg", "-y", "-f", "lavfi", "-i", "anullsrc=r=44100:cl=mono", "-t", f"{secs:.3f}", path])

def tts(voice, text, path):
    aiff = path[:-4] + ".aiff"
    v = VOICE_FI if voice == "fi" else VOICE_EN
    run(["say", "-v", v, "-r", str(RATE if voice == "en" else 165), "-o", aiff, text])
    run(["ffmpeg", "-y", "-i", aiff, "-ar", "44100", "-ac", "1", path])
    os.remove(aiff)

def chunks(text, max_words=12):
    """Split a sentence into evenly sized caption pieces, nudged to the nearest comma."""
    words = text.split()
    n = -(-len(words) // max_words)
    if n <= 1:
        return [text]
    out, start = [], 0
    for k in range(1, n):
        cut = round(len(words) * k / n)
        for d in (0, 1, -1, 2, -2):
            c = cut + d
            if start < c < len(words) and re.search(r"[,:;]$", words[c - 1]):
                cut = c; break
        out.append(" ".join(words[start:cut])); start = cut
    out.append(" ".join(words[start:]))
    return out

def ts(t, srt=False):
    h, r = divmod(t, 3600); m, s = divmod(r, 60)
    if srt:
        return f"{int(h):02d}:{int(m):02d}:{int(s):02d},{int(round((s % 1) * 1000)):03d}"
    return f"{int(h)}:{int(m):02d}:{s:05.2f}"

# 1. voice-over per scene, with caption timings relative to the scene start
scene_meta = []
for i, (frame, mind, focus, lines) in enumerate(SCENES):
    parts, caps, t = [], [], LEAD
    lead = os.path.join(WORK, f"s{i:02d}_lead.wav"); silence(lead, LEAD); parts.append(lead)
    for j, (voice, text) in enumerate(lines):
        p = os.path.join(WORK, f"s{i:02d}_l{j:02d}.wav"); tts(voice, text, p)
        d = wav_len(p)
        pcs = chunks(text); total_w = sum(len(c.split()) for c in pcs); ct = t
        for c in pcs:
            cd = d * len(c.split()) / total_w
            caps.append((ct, ct + cd, c)); ct += cd
        parts.append(p); t += d
        g = os.path.join(WORK, f"s{i:02d}_g{j:02d}.wav"); silence(g, GAP); parts.append(g); t += GAP
    dur = max(mind, t + TAIL) if lines else mind
    lst = os.path.join(WORK, f"s{i:02d}.txt")
    open(lst, "w").write("".join(f"file '{p}'\n" for p in parts))
    sa = os.path.join(WORK, f"s{i:02d}_audio.wav")
    run(["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", lst, "-af", f"apad=whole_dur={dur:.3f}", "-t", f"{dur:.3f}", sa])
    scene_meta.append({"frame": frame, "dur": round(dur, 3), "focus": focus, "caps": caps, "audio": sa})

# 2. one clip per scene: framed slide with a slow push-in toward the focus point
for i, m in enumerate(scene_meta):
    cx, cy, z1 = m["focus"]; n = int(round(m["dur"] * FPS))
    # zoompan on a 2x upscaled still to avoid jitter
    zexpr = f"1+({z1}-1)*on/{n}"
    xexpr = f"({cx}*2)-(iw/zoom/2)+((iw/2)-({cx}*2))*(1-(zoom-1)/({z1}-1+0.000001))"
    yexpr = f"({cy}*2)-(ih/zoom/2)+((ih/2)-({cy}*2))*(1-(zoom-1)/({z1}-1+0.000001))"
    vf = (f"scale=3840:2160,zoompan=z='{zexpr}':x='max(0,min(iw-iw/zoom,{xexpr}))':y='max(0,min(ih-ih/zoom,{yexpr}))'"
          f":d={n}:s={SW}x{SH}:fps={FPS},"
          f"pad=1920:1080:{SX}:{SY}:color={FRAME_BG},format=yuv420p")
    m["clip"] = os.path.join(WORK, f"s{i:02d}.mp4")
    run(["ffmpeg", "-y", "-loop", "1", "-i", os.path.join(FR, m["frame"]), "-vf", vf,
         "-frames:v", str(n), "-c:v", "libx264", "-preset", "medium", "-crf", "18", m["clip"]])

# 3. scene start times on the final timeline (each crossfade overlaps XF seconds)
starts, t = [], 0.0
for m in scene_meta:
    starts.append(t); t += m["dur"] - XF
total = t + XF

# 4. captions: SRT + ASS (burned in, in the band under the slide)
srt, ass_ev, k = [], [], 1
for st, m in zip(starts, scene_meta):
    for a, b, text in m["caps"]:
        A, B = st + a, st + b
        srt.append(f"{k}\n{ts(A, True)} --> {ts(B, True)}\n{text}\n"); k += 1
        ass_ev.append(f"Dialogue: 0,{ts(A)},{ts(B)},Cap,,0,0,0,,{text}")
open(os.path.join(HERE, "tasan_pitch.srt"), "w").write("\n".join(srt))
ass = os.path.join(WORK, "captions.ass")
open(ass, "w").write(f"""[Script Info]
ScriptType: v4.00+
PlayResX: 1920
PlayResY: 1080

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Cap,Helvetica Neue,40,&H00EAF1F4,&H00EAF1F4,&H00281610,&H00281610,0,0,0,0,100,100,0,0,1,0,0,2,120,120,40,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
""" + "\n".join(ass_ev) + "\n")

# 5. stitch: video crossfades + delayed scene audio, captions burned in
inputs, fc = [], []
for m in scene_meta:
    inputs += ["-i", m["clip"]]
for m in scene_meta:
    inputs += ["-i", m["audio"]]
prev = "[0:v]"
for i in range(1, len(scene_meta)):
    off = starts[i]
    out = f"[v{i}]"
    fc.append(f"{prev}[{i}:v]xfade=transition=fade:duration={XF}:offset={off:.3f}{out}")
    prev = out
fc.append(f"{prev}fade=t=in:st=0:d=0.8,fade=t=out:st={total-1.0:.3f}:d=1.0,ass={ass}[vout]")
na = len(scene_meta)
for i, st in enumerate(starts):
    ms = int(round(st * 1000))
    fc.append(f"[{na+i}:a]adelay={ms}|{ms}[a{i}]")
fc.append("".join(f"[a{i}]" for i in range(na)) + f"amix=inputs={na}:normalize=0,loudnorm=I=-16:TP=-1.5[aout]")
out = os.path.join(HERE, "tasan_pitch.mp4")
run(["ffmpeg", "-y", *inputs, "-filter_complex", ";".join(fc), "-map", "[vout]", "-map", "[aout]",
     "-c:v", "libx264", "-preset", "medium", "-crf", "20", "-pix_fmt", "yuv420p", "-r", str(FPS),
     "-c:a", "aac", "-b:a", "160k", "-t", f"{total:.3f}", "-movflags", "+faststart", out])

json.dump({"total_seconds": round(total, 2),
           "scenes": [{"frame": m["frame"], "start": round(s, 2), "dur": m["dur"]} for s, m in zip(starts, scene_meta)]},
          open(os.path.join(WORK, "timeline.json"), "w"), indent=2)
print(f"wrote {out} ({total:.1f} s)")
