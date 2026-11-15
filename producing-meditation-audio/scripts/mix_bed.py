"""Lay a music bed under narration and master it. Run:
  python mix_bed.py VOICE.wav BED.wav OUT.(m4a|mp3|wav|...) [--bed-lu 14] [--duck 4] [--fade-in 6] [--fade-out 10]
  [--intro 8] [--outro 20] [--lufs -16] [--tp -1.5]
- The bed is looped (-stream_loop) to cover intro + voice + outro; loop the bed with make_loop.py first or the seam clicks.
- Level: bed's momentary median is set `bed-lu` LU under the voice's (12-16 suits meditation; under ~18 it vanishes on phones).
- Speech-band dip: -3 dB at 2.5 kHz in the bed so words stay clear without turning the bed down.
- Ducking: gentle sidechain (ratio 2, attack 80 ms, release 1.2 s) so the bed eases down `duck` dB under words and
  breathes back up in the pauses; slow release avoids audible pumping between phrases.
- Voice starts after `intro` s of bed alone; bed carries `outro` s after the last word, then fades over `fade-out`.
Then master.py's closed loop on the encoded file."""
import argparse, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import duration, momentary_median, run
from master import master

p = argparse.ArgumentParser()
for n in ("voice", "bed", "out"): p.add_argument(n)
for n, d in (("bed-lu", 14), ("duck", 4), ("fade-in", 6), ("fade-out", 10), ("intro", 8), ("outro", 20),
             ("lufs", -16), ("tp", -1.5)):
    p.add_argument("--" + n, type=float, default=d)
a = p.parse_args()
work = a.out + ".work"; os.makedirs(work, exist_ok=True)
total = a.intro + duration(a.voice) + a.outro
bed = os.path.join(work, "bed.wav"); voice = os.path.join(work, "voice.wav")
run(["ffmpeg", "-loglevel", "error", "-y", "-stream_loop", "-1", "-i", a.bed, "-t", f"{total:.3f}", "-af",
     "aresample=48000,aformat=channel_layouts=stereo,equalizer=f=2500:t=q:w=1:g=-3", "-c:a", "pcm_s24le", bed])
run(["ffmpeg", "-loglevel", "error", "-y", "-i", a.voice, "-af",
     f"aresample=48000,aformat=channel_layouts=stereo,adelay={int(a.intro * 1000)}:all=1,apad=whole_dur={total:.3f}",
     "-c:a", "pcm_s24le", voice])
vmed, bmed = momentary_median(voice), momentary_median(bed)
gain = (vmed - a.bed_lu) - bmed
# threshold ~ -30 dBFS keys on speech, not breaths; ratio picked so a word pulls the bed down about `duck` dB.
ratio = max(1.2, 1 + a.duck / 6)
fc = (f"[1:a]asplit=2[v][key];"
      f"[0:a]volume={gain:.2f}dB,afade=t=in:d={a.fade_in},afade=t=out:st={total - a.fade_out:.3f}:d={a.fade_out}[b0];"
      f"[b0][key]sidechaincompress=threshold=0.03:ratio={ratio:.2f}:attack=80:release=1200:knee=6[b];"
      f"[v][b]amix=inputs=2:normalize=0:duration=longest[a]")
mix = os.path.join(work, "mix.wav")
run(["ffmpeg", "-loglevel", "error", "-y", "-i", bed, "-i", voice, "-filter_complex", fc, "-map", "[a]",
     "-c:a", "pcm_s24le", mix])
i, tp = master(mix, a.out, a.lufs, a.tp)
print(f"{a.out}: {total:.1f} s; bed {gain:+.1f} dB (voice median {vmed:.1f}, bed median {bmed:.1f} -> {a.bed_lu:g} LU under); "
      f"{i:.1f} LUFS, {tp:.1f} dBTP. Work files in {work}/ (delete when done).")
