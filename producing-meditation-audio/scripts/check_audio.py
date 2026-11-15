"""Verify a finished track. Run: python check_audio.py FILE [--lufs -16] [--tp -1.5] [--loop]
Reports and FAILS (exit 1) on: integrated loudness off target by > 0.5 LU, true peak over --tp, clipping (flat-topped peaks),
DC offset, unexpected dead air (digital silence > 10 s, which reads as a broken file in an app),
and with --loop a seam jump (last vs first 20 ms level differ by > 3 dB). Listening is still the final check:
numbers cannot tell you the bed is the wrong mood."""
import argparse, os, re, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import duration, loudness, run

p = argparse.ArgumentParser(); p.add_argument("file")
p.add_argument("--lufs", type=float, default=-16); p.add_argument("--tp", type=float, default=-1.5)
p.add_argument("--loop", action="store_true"); p.add_argument("--max-silence", type=float, default=10)
a = p.parse_args(); bad = []
i, tp, lra = loudness(a.file); d = duration(a.file)
print(f"{a.file}: {d:.1f} s, {i:.2f} LUFS, {tp:.2f} dBTP, LRA {lra:.1f} LU")
if abs(i - a.lufs) > 0.5: bad.append(f"loudness {i:.1f} vs target {a.lufs}")
if tp > a.tp: bad.append(f"true peak {tp:.1f} > {a.tp}")
st = run(["ffmpeg", "-hide_banner", "-i", a.file, "-af", "astats", "-f", "null", "-"]).stderr
dc = [abs(float(x)) for x in re.findall(r"DC offset:\s*(-?[\d.e-]+)", st)]
flat = [float(x) for x in re.findall(r"Flat factor:\s*([\d.]+)", st)]
if dc and max(dc) > 0.005: bad.append(f"DC offset {max(dc):.4f}")
if flat and max(flat) > 0: bad.append("flat-topped (clipped) peaks")
sil = run(["ffmpeg", "-hide_banner", "-i", a.file, "-af", "silencedetect=noise=-70dB:d=1", "-f", "null", "-"]).stderr
for m in re.findall(r"silence_duration: ([\d.]+)", sil):
    if float(m) > a.max_silence: bad.append(f"digital silence {float(m):.1f} s (bed missing?)")
if a.loop:
    def rms(ss, t):
        s = run(["ffmpeg", "-hide_banner", "-ss", f"{ss:.3f}", "-t", f"{t:.3f}", "-i", a.file, "-af",
                 "astats=measure_overall=RMS_level", "-f", "null", "-"]).stderr
        return float(re.findall(r"RMS level dB:\s*(-?[\d.inf]+)", s)[-1])
    head, tail = rms(0, 0.02), rms(d - 0.02, 0.02)
    print(f"  loop seam: tail {tail:.1f} dB -> head {head:.1f} dB")
    if abs(head - tail) > 3: bad.append(f"loop seam jump {abs(head - tail):.1f} dB")
print("PASS" if not bad else "FAIL: " + "; ".join(bad)); sys.exit(1 if bad else 0)
