#!/usr/bin/env python3
"""Recovered original score and synthesis, including the final 59.4-second edit."""

import argparse
import json
import wave
from pathlib import Path

import numpy as np


def compose(output_dir):
    """Synthesise the instrumental score in the requested directory."""
    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)
    sample_rate = 44100
    duration = 59.4
    beat = 60 / 90
    mix = np.zeros((int(sample_rate * duration), 2), np.float64)

    def note(midi, start, length, vol=0.1, pan=0, kind="piano"):
        n = int((length + 1.3) * sample_rate)
        t = np.arange(n) / sample_rate
        f = 440 * 2 ** ((midi - 69) / 12)
        if kind == "piano":
            env = (1 - np.exp(-t / 0.008)) * np.exp(-t / (0.65 + length * 0.45))
            sig = sum(
                a * np.sin(2 * np.pi * f * h * t) * np.exp(-t * h * 0.12)
                for h, a in [(1, 1), (2, 0.30), (3, 0.12), (4, 0.045)]
            )
        elif kind == "pad":
            env = np.minimum(t / 0.28, 1) * np.minimum(
                np.maximum(length + 0.8 - t, 0) / 0.8, 1
            )
            sig = (
                np.sin(2 * np.pi * f * t)
                + 0.22 * np.sin(2 * np.pi * (f * 1.002) * t)
                + 0.15 * np.sin(4 * np.pi * f * t)
            ) * 0.65
        else:
            env = (1 - np.exp(-t / 0.02)) * np.exp(-t / 1.3)
            sig = np.sin(2 * np.pi * f * t) + 0.12 * np.sin(4 * np.pi * f * t)
        env *= np.minimum(np.maximum(length + 1.3 - t, 0) / 0.15, 1)
        sig *= env * vol
        start = int(start * sample_rate)
        end = min(start + n, len(mix))
        sig = sig[: end - start]
        if end <= start:
            return
        mix[start:end, 0] += sig * np.sqrt((1 - pan) / 2)
        mix[start:end, 1] += sig * np.sqrt((1 + pan) / 2)

    # Original C-major score, 22 bars. All tones synthesized here; no recordings/samples.
    chords = [
        ([60, 64, 67, 71], 36),
        ([57, 60, 64, 67], 33),
        ([62, 65, 69, 72], 38),
        ([55, 59, 62, 64], 31),
        ([59, 62, 64, 67], 40),
        ([57, 60, 64, 71], 33),
        ([57, 60, 65, 69], 29),
        ([55, 60, 62, 67], 31),
    ]
    melodies = [
        [(0, 76, 1), (1.5, 74, 0.5), (2, 71, 1), (3.25, 67, 0.5)],
        [(0.5, 72, 1), (2, 76, 0.75), (3, 71, 0.5)],
        [(0, 74, 1.5), (2, 77, 0.5), (3, 76, 0.75)],
        [(0.5, 74, 0.75), (1.5, 71, 0.5), (2.5, 69, 1)],
        [(0, 71, 1), (1.5, 76, 0.75), (3, 74, 0.5)],
        [(0.5, 72, 1), (2, 71, 0.5), (3, 69, 0.75)],
        [(0, 69, 0.75), (1, 72, 0.75), (2.5, 77, 1)],
        [(0, 74, 1), (1.5, 71, 0.75), (3, 67, 0.75)],
    ]
    for bar in range(22):
        start = 0.25 + bar * 4 * beat
        idx = bar % 8
        ch, bass = chords[idx]
        if bar >= 20:
            ch, bass = ([60, 64, 67, 71], 36)
        for k, m in enumerate(ch):
            note(m, start, 2.6, 0.024, (k - 1.5) * 0.32, "pad")
        note(bass, start, 1.8, 0.13, 0, "bass")
        if bar < 21:
            note(bass + 12, start + 2 * beat, 1, 0.065, 0.05, "bass")
        pattern = [0, 2, 1, 3, 2, 1, 3, 2]
        for j, k in enumerate(pattern):
            if bar == 21 and j > 3:
                break
            note(
                ch[k] + 12,
                start + j * 0.5 * beat,
                0.45,
                0.038,
                (-0.4 if j % 2 else 0.4),
            )
        melody = melodies[idx]
        if bar == 20:
            melody = [(0, 76, 1), (1.5, 74, 0.5), (2.5, 71, 0.5)]
        if bar == 21:
            melody = [(0, 72, 2.6)]
        for offset, m, length in melody:
            note(m, start + offset * beat, length * beat, 0.105, -0.08)
    # Subtle stereo room echoes, then smooth fade-in/out.
    dry = mix.copy()
    for delay, gain in [(0.083, 0.14), (0.157, 0.09), (0.293, 0.05)]:
        n = int(delay * sample_rate)
        mix[n:] += dry[:-n, ::-1] * gain
    fade = np.ones(len(mix))
    n = int(1.0 * sample_rate)
    fade[:n] = np.linspace(0, 1, n)
    n = int(2.3 * sample_rate)
    fade[-n:] = np.linspace(1, 0, n)
    mix *= fade[:, None]
    rms = np.sqrt(np.mean(mix**2))
    mix *= min(0.105 / rms, 0.67 / np.max(np.abs(mix)))
    peak = float(np.max(np.abs(mix)))
    rms = float(np.sqrt(np.mean(mix**2)))
    with wave.open(str(out / "知恩相伴-original.wav"), "wb") as w:
        w.setnchannels(2)
        w.setsampwidth(2)
        w.setframerate(sample_rate)
        w.writeframes((mix * 32767).astype("<i2").tobytes())
    (out / "music-provenance.json").write_text(
        json.dumps(
            {
                "title": "知恩相伴",
                "creation": "Original instrumental composition and procedural synthesis for this video",
                "tempo_bpm": 90,
                "samples": "None. Oscillator-synthesized piano-like notes, bass and pad.",
                "melody": "New score; no IU recording or melody used",
                "sample_rate": sample_rate,
                "duration": duration,
                "peak_dbfs": 20 * np.log10(peak),
                "rms_dbfs": 20 * np.log10(rms),
            },
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )
    print("Audio peak dBFS:", 20 * np.log10(peak), "RMS dBFS:", 20 * np.log10(rms))


def main():
    """Generate the instrumental score used by the demonstration video."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("output_dir", type=Path)
    args = parser.parse_args()
    compose(args.output_dir)


if __name__ == "__main__":
    main()
