# producing-meditation-audio

A Claude Code skill for making guided-meditation audio: AI lo-fi / ambient music beds, TTS narration with timed pauses, music ducked under the voice, seamless loops, loudness mastering (-16 / -14 LUFS) and app-ready exports, with ffmpeg scripts that build and check each track.

## Install
```bash
cp -R producing-meditation-audio ~/.claude/skills/
```
Claude Code loads it automatically when you ask for meditation audio, a music bed, TTS narration, ducking, loops or loudness work.

Requirements: Python 3.9+ and ffmpeg (`brew install ffmpeg` / `apt install ffmpeg`). No Python packages.

## Quick start
```bash
cd producing-meditation-audio/scripts
python assemble_narration.py session.json voice.wav          # clips + pauses -> one narration file
python make_loop.py bed.wav bed_loop.wav --bpm 65 --bars 32  # seamless loop
python mix_bed.py voice.wav bed_loop.wav track.m4a           # mix, duck, fade, master to -16 LUFS
python check_audio.py track.m4a                              # PASS/FAIL
```

## Contents
- `SKILL.md`: pipeline, pacing, voice, music, mixing, loudness, verification
- `references/generation.md`: TTS and AI music tools, prompts, cost and licensing
- `references/export-formats.md`: formats per platform, loop playback
- `scripts/`: `assemble_narration.py`, `make_loop.py`, `mix_bed.py`, `master.py`, `check_audio.py`, `common.py`

## Licence
MIT. Check the terms of any TTS or music generator you use; this licence covers the skill, not generated audio.
