"""Closed-loop master. Run: python master.py IN OUT [--lufs -16] [--tp -1.5]
Gain -> 4x-oversampled limiter (approximates true-peak limiting) -> encode by OUT's extension
(.wav 24-bit, .flac, .m4a AAC 256k, .mp3 320k, .ogg/.opus 160k), then MEASURES THE ENCODED FILE and
corrects until it reads target +-0.3 LU and true peak <= --tp. Lossy encoders add peak overshoot,
so measuring the input is not enough. loudnorm is avoided on purpose: on a peaky input it silently
switches to dynamic mode and pumps quiet ambient material."""
import argparse, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import loudness, run

CODEC = {".wav": ["-c:a", "pcm_s24le"], ".flac": ["-c:a", "flac"],
         ".m4a": ["-c:a", "aac", "-b:a", "256k", "-movflags", "+faststart"],
         ".mp3": ["-c:a", "libmp3lame", "-b:a", "320k"],
         ".ogg": ["-c:a", "libopus", "-b:a", "160k"], ".opus": ["-c:a", "libopus", "-b:a", "160k"]}

def master(src, out, target=-16.0, tp_max=-1.5, rate=48000):
    ext = os.path.splitext(out)[1].lower()
    if ext not in CODEC: raise SystemExit(f"unsupported extension {ext}; use {', '.join(CODEC)}")
    gain, ceil = target - loudness(src)[0], tp_max - 0.5
    for _ in range(8):
        af = (f"volume={gain:.2f}dB,aresample=192000,"
              f"alimiter=limit={10 ** (ceil / 20):.5f}:level=0:latency=1:attack=5:release=100,aresample={rate}")
        run(["ffmpeg", "-loglevel", "error", "-y", "-i", src, "-af", af, *CODEC[ext], out])
        i, tp, lra = loudness(out)
        print(f"  pass: gain {gain:+.2f} dB, ceiling {ceil:.2f} -> {i:.2f} LUFS, {tp:.2f} dBTP, LRA {lra:.1f}")
        if abs(i - target) <= 0.3 and tp <= tp_max: return i, tp
        gain += target - i
        if tp > tp_max: ceil = max(tp_max - 3.0, ceil - (tp - tp_max + 0.1))
    raise SystemExit(f"could not reach {target} LUFS / {tp_max} dBTP (last {i:.1f} / {tp:.1f})")

if __name__ == "__main__":
    p = argparse.ArgumentParser(); p.add_argument("src"); p.add_argument("out")
    p.add_argument("--lufs", type=float, default=-16.0); p.add_argument("--tp", type=float, default=-1.5)
    a = p.parse_args(); print("master: %.1f LUFS, %.1f dBTP" % master(a.src, a.out, a.lufs, a.tp))
