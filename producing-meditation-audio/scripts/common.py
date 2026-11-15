"""Shared ffmpeg helpers. Imported by the other scripts; not run directly."""
import re, statistics, subprocess

def run(args):
    r = subprocess.run(args, capture_output=True, text=True)
    if r.returncode:
        raise SystemExit(f"ffmpeg failed: {' '.join(args[:6])}...\n{r.stderr[-1500:]}")
    return r

def duration(f):
    return float(subprocess.check_output(["ffprobe", "-v", "error", "-show_entries",
        "format=duration", "-of", "csv=p=0", f]).strip())

def loudness(f):
    """Integrated LUFS, true peak dBTP, loudness range LU (ebur128 on the file as stored)."""
    s = run(["ffmpeg", "-hide_banner", "-i", f, "-af", "ebur128=peak=true", "-f", "null", "-"]).stderr
    s = s[s.rindex("Summary:"):]
    g = lambda p: float(re.search(p, s).group(1))
    return g(r"I:\s*(-?[\d.]+) LUFS"), g(r"Peak:\s*(-?[\d.inf]+) dBFS"), g(r"LRA:\s*(-?[\d.]+) LU")

def momentary_median(f, floor=-45.0):
    """Median momentary loudness of the sounding parts (silence below `floor` ignored)."""
    s = run(["ffmpeg", "-v", "verbose", "-i", f, "-af", "ebur128=framelog=verbose", "-f", "null", "-"]).stderr
    v = [float(m) for m in re.findall(r"M:\s*(-?[\d.]+)", s) if float(m) > floor]
    return statistics.median(v) if v else floor
