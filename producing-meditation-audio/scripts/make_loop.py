"""Make a seamless loop from a music bed. Run: python make_loop.py IN OUT.wav [--xfade 4] [--bpm 70 --bars 16 --beats 4]
Takes the tail `xfade` seconds and crossfades them (equal-power) into the head, so the file's last sample
flows into its first. With --bpm/--bars the loop length snaps to whole bars, so the groove does not hiccup
at the seam. Check the result with check_audio.py --loop."""
import argparse, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import duration, run

p = argparse.ArgumentParser(); p.add_argument("src"); p.add_argument("out")
p.add_argument("--xfade", type=float, default=4.0); p.add_argument("--bpm", type=float)
p.add_argument("--bars", type=int); p.add_argument("--beats", type=int, default=4)
a = p.parse_args()
d, x = duration(a.src), a.xfade
L = d - x  # loop length without bar snapping
if a.bpm and a.bars:
    L = a.bars * a.beats * 60.0 / a.bpm
    if L + x > d: raise SystemExit(f"source {d:.1f}s too short for {a.bars} bars ({L:.1f}s) + {x}s crossfade")
# Output = src[x, L) + (src[L, L+x) fading out, mixed with src[0, x) fading in): it ends where it starts (src at x).
fc = (f"[0:a]aresample=48000,asplit=3[s1][s2][s3];"
      f"[s1]atrim=start={x}:end={L},asetpts=PTS-STARTPTS[pre];"
      f"[s2]atrim=start={L}:end={L + x},asetpts=PTS-STARTPTS,afade=t=out:d={x}:curve=qsin[tail];"
      f"[s3]atrim=start=0:end={x},asetpts=PTS-STARTPTS,afade=t=in:d={x}:curve=qsin[head];"
      f"[tail][head]amix=inputs=2:normalize=0[seam];[pre][seam]concat=n=2:v=0:a=1[a]")
run(["ffmpeg", "-loglevel", "error", "-y", "-i", a.src, "-filter_complex", fc, "-map", "[a]", "-c:a", "pcm_s24le", a.out])
print(f"{a.out}: loop {duration(a.out):.2f} s (crossfade {x} s)")
