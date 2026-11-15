#!/usr/bin/env python3
"""Synthesise the music bed + sound effects and mix them with the narration.

Reads timeline.json and audio/v*.wav (macOS `say` takes). Writes audio/mix.wav.
Everything here is generated from sine waves and noise: no third-party samples.
"""
import json, os, wave
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
AUD = os.path.join(HERE, "audio")
SR = 44100
TL = json.load(open(os.path.join(HERE, "timeline.json")))
DUR = TL["duration"]
N = int(DUR * SR)
rng = np.random.default_rng(7)

def read_wav(p):
    with wave.open(p) as w:
        a = np.frombuffer(w.readframes(w.getnframes()), dtype=np.int16).astype(np.float32) / 32768
        if w.getnchannels() == 2:
            a = a.reshape(-1, 2).mean(1)
        return a

def add(buf, sig, t, gain=1.0):
    i = int(t * SR)
    if i >= len(buf): return
    sig = sig[: len(buf) - i]
    buf[i:i + len(sig)] += sig * gain

def tt(d):
    return np.arange(int(d * SR)) / SR

def midi(n):
    return 440.0 * 2 ** ((n - 69) / 12)

# ---------------- music ----------------
BPM = 110
BEAT = 60 / BPM
BAR = 4 * BEAT
music = np.zeros(N, np.float32)

def marimba(f, d=0.9, vel=1.0):
    t = tt(d)
    s = np.sin(2 * np.pi * f * t) * np.exp(-t * 7)
    s += 0.35 * np.sin(2 * np.pi * f * 4 * t) * np.exp(-t * 26)
    s += 0.12 * np.sin(2 * np.pi * f * 9.9 * t) * np.exp(-t * 45)
    att = np.minimum(1, t / 0.004)
    return (s * att * vel).astype(np.float32)

def bass(f, d):
    t = tt(d)
    s = np.sin(2 * np.pi * f * t) + 0.25 * np.sin(2 * np.pi * 2 * f * t)
    env = np.minimum(1, t / 0.02) * np.exp(-t * 2.2)
    return (s * env).astype(np.float32)

def shaker(d=0.07):
    t = tt(d)
    n = rng.standard_normal(len(t))
    n = n - np.convolve(n, np.ones(4) / 4, mode="same")  # crude high-pass
    return (n * np.exp(-t * 60)).astype(np.float32)

# chords as MIDI notes (root position triads + octave), bass root
BRIGHT = [([60, 64, 67], 36), ([55, 59, 62], 43), ([57, 60, 64], 45), ([53, 57, 60], 41)]   # C G Am F
MINOR = [([57, 60, 64], 45), ([53, 57, 60], 41), ([50, 53, 57], 38), ([52, 56, 59], 40)]    # Am F Dm E
ARP = [0, 1, 2, 3, 2, 1, 2, 3]  # index into chord + octave note

def section_for(t):
    for s in TL["scenes"]:
        if s["start"] <= t < s["end"]:
            return s["id"]
    return "level"

bar_i = 0
t0 = 0.0
while t0 < DUR - 1.2:
    sec = section_for(t0 + 0.01)
    prog = MINOR if sec == "clock" else BRIGHT
    notes, root = prog[bar_i % 4]
    tones = notes + [notes[0] + 12]
    sparse = sec in ("clock",)
    for k, idx in enumerate(ARP):
        if sparse and k % 2: continue
        tn = t0 + k * BEAT / 2
        vel = 0.55 if k % 2 == 0 else 0.38
        add(music, marimba(midi(tones[idx] + 12), vel=vel), tn, 0.30)
    if sec != "meet":
        add(music, bass(midi(root), BEAT * 1.8), t0, 0.32)
        add(music, bass(midi(root), BEAT * 1.8), t0 + 2 * BEAT, 0.26)
    if sec not in ("meet", "clock"):
        for k in range(8):
            add(music, shaker(), t0 + k * BEAT / 2 + BEAT / 4, 0.05 if k % 2 else 0.035)
    t0 += BAR
    bar_i += 1
# final ringing C chord
for n in [48, 60, 64, 67, 72]:
    add(music, marimba(midi(n + 12), d=2.5, vel=0.6), DUR - 3.2, 0.25)
add(music, bass(midi(36), 3.0), DUR - 3.2, 0.3)
# fades
fade_in = np.minimum(1, np.arange(N) / (SR * 1.0))
fade_out = np.clip((DUR - np.arange(N) / SR) / 1.5, 0, 1)
music *= fade_in * fade_out

# ---------------- sound effects ----------------
sfx = np.zeros(N, np.float32)

def sweep(f0, f1, d, vib=0.0, decay=6.0):
    t = tt(d)
    f = f0 * (f1 / f0) ** (t / d)
    if vib:
        f = f * (1 + 0.06 * np.sin(2 * np.pi * vib * t))
    ph = 2 * np.pi * np.cumsum(f) / SR
    return (np.sin(ph) * np.exp(-t * decay) * np.minimum(1, t / 0.005)).astype(np.float32)

def noise_band(d, lo_cut=6, decay=None, shape=None):
    t = tt(d)
    n = rng.standard_normal(len(t)).astype(np.float32)
    k = np.ones(lo_cut) / lo_cut
    n = np.convolve(n, k, mode="same")
    env = shape(t) if shape is not None else np.exp(-t * (decay or 10))
    return n * env

def bell(f, d=1.6):
    t = tt(d)
    s = sum(a * np.sin(2 * np.pi * f * r * t) * np.exp(-t * dk) for r, a, dk in
            [(1, 1, 2.5), (2.76, 0.5, 4), (5.4, 0.25, 7), (8.9, 0.12, 10)])
    return (s * np.minimum(1, t / 0.002)).astype(np.float32)

for e in TL["sfx"]:
    t, k = e["t"], e["kind"]
    if k == "thump":
        add(sfx, sweep(160, 60, 0.25, decay=14), t, 0.55)
    elif k == "boing":
        add(sfx, sweep(380, 760, 0.12, decay=4), t, 0.25)
        add(sfx, sweep(760, 300, 0.45, vib=18, decay=5), t + 0.12, 0.28)
    elif k == "whoosh":
        add(sfx, noise_band(0.7, lo_cut=10, shape=lambda x: np.sin(np.pi * x / 0.7) ** 2), t, 0.16)
    elif k == "uhoh":
        add(sfx, sweep(520, 500, 0.18, decay=5), t, 0.18)
        add(sfx, sweep(400, 330, 0.3, decay=4), t + 0.22, 0.18)
    elif k == "ticks":
        for i in range(e["count"]):
            add(sfx, sweep(1400 + 30 * i, 1200 + 30 * i, 0.05, decay=60), t + e["span"] * i / e["count"], 0.10)
    elif k == "hop":
        for i in range(4):
            add(sfx, sweep(500 + 120 * i, 900 + 120 * i, 0.12, decay=18), t + 0.11 * i, 0.16)
    elif k == "whirr":
        for i in range(30):
            add(sfx, noise_band(0.02, lo_cut=2, decay=200), t + i * 0.055, 0.25)
    elif k == "pop":
        add(sfx, sweep(300, 900, 0.09, decay=25), t, 0.3)
    elif k == "ding":
        add(sfx, bell(1318.5), t, 0.28)
    elif k == "flips":
        for i in range(e["count"]):
            add(sfx, noise_band(0.08, lo_cut=3, decay=50), t + e["span"] * i / e["count"], 0.18)
    elif k == "blip":
        add(sfx, sweep(880, 1320, 0.1, decay=20), t, 0.2)
    elif k == "chime":
        for i, n in enumerate([72, 76, 79, 84]):
            add(sfx, bell(midi(n), 2.0), t + 0.09 * i, 0.12)

# ---------------- narration + ducking ----------------
voice = np.zeros(N, np.float32)
for v in TL["voice"]:
    a = read_wav(os.path.join(AUD, v["file"]))
    add(voice, a / max(1e-6, np.abs(a).max()) * 0.85, v["at"], 1.0)

# duck music under the voice (smoothed envelope)
env = np.abs(voice)
win = int(0.25 * SR)
env = np.convolve(env, np.ones(win) / win, mode="same")
duck = 1 - 0.55 * np.clip(env / 0.05, 0, 1)
mix = voice + music * duck + sfx
mix /= max(1.0, np.abs(mix).max() / 0.95)

out = os.path.join(AUD, "mix.wav")
with wave.open(out, "w") as w:
    w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR)
    w.writeframes((mix * 32767).astype(np.int16).tobytes())
print("wrote", out, f"{DUR:.1f}s")
