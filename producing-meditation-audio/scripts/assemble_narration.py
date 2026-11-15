"""Join narration clips with scripted silences. Run: python assemble_narration.py SCRIPT.json OUT.wav
SCRIPT.json: {"lead_in": 4, "tail": 3, "items": [{"file": "01.wav"}, {"pause": 8}, {"file": "02.wav"}, ...]}
Paths are relative to the JSON file. Each clip is cleaned (high-pass 80 Hz, edges trimmed of TTS
silence at -50 dB, 15 ms fades so no click), resampled to 48 kHz mono, then laid end to end with the
pauses. A pause is real digital silence; the bed fills it later. Prints a cue sheet (start/end per clip)."""
import json, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import duration, run

spec_path, out = sys.argv[1], sys.argv[2]
spec = json.load(open(spec_path)); base = os.path.dirname(os.path.abspath(spec_path))
tmp = out + ".parts"; os.makedirs(tmp, exist_ok=True)
parts, t, cues = [], 0.0, []

def silence(sec):
    f = os.path.join(tmp, f"sil_{len(parts):03d}.wav")
    run(["ffmpeg", "-loglevel", "error", "-y", "-f", "lavfi", "-i", "anullsrc=r=48000:cl=mono",
         "-t", f"{sec:.3f}", "-c:a", "pcm_s24le", f]); parts.append(f); return sec

trim = ("silenceremove=start_periods=1:start_threshold=-50dB:start_silence=0.05,areverse,"
        "silenceremove=start_periods=1:start_threshold=-50dB:start_silence=0.15,areverse")
t += silence(spec.get("lead_in", 4))
for it in spec["items"]:
    if "pause" in it: t += silence(float(it["pause"])); continue
    f = os.path.join(tmp, f"clip_{len(parts):03d}.wav")
    run(["ffmpeg", "-loglevel", "error", "-y", "-i", os.path.join(base, it["file"]), "-af",
         f"aresample=48000,aformat=channel_layouts=mono,highpass=f=80,{trim}", "-c:a", "pcm_s24le", f + ".raw.wav"])
    d = duration(f + ".raw.wav")
    run(["ffmpeg", "-loglevel", "error", "-y", "-i", f + ".raw.wav", "-af",
         f"afade=t=in:d=0.015,afade=t=out:st={max(d - 0.015, 0):.3f}:d=0.015", "-c:a", "pcm_s24le", f])
    parts.append(f); cues.append((it["file"], t, t + d)); t += d
t += silence(spec.get("tail", 3))
lst = os.path.join(tmp, "list.txt")
open(lst, "w").write("".join(f"file '{os.path.abspath(p)}'\n" for p in parts))
run(["ffmpeg", "-loglevel", "error", "-y", "-f", "concat", "-safe", "0", "-i", lst, "-c:a", "pcm_s24le", out])
for name, a, b in cues: print(f"{a:8.2f} {b:8.2f}  {name}")
print(f"{out}: {duration(out):.1f} s, {len(cues)} clips")
