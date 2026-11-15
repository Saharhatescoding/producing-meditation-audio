---
name: producing-meditation-audio
description: Produces guided-meditation audio for an app - AI-generated lo-fi or ambient music beds, AI voice (TTS) narration with scripted pauses, the bed mixed and ducked under the voice, seamless loops, fades, loudness mastering (-16 LUFS / -14 LUFS, true peak) and app-ready exports (AAC/M4A, MP3, Opus, WAV, FLAC) - with ffmpeg scripts that build and verify each track. Use it whenever someone is making meditation, sleep, breathing, relaxation or focus audio; generating a music bed or lo-fi loop with an AI music tool; generating narration with TTS (ElevenLabs, OpenAI, local voices); timing silences or breath pauses; mixing music under voice, ducking, crossfades or loop seams; normalising loudness; or choosing export formats and checking a track before it ships in the app.
---

# Producing meditation audio

A meditation track = narration clips + scripted silences, laid over a looping music bed, mastered once.
Scripts in `scripts/` are run, not read (Python 3.9+, ffmpeg with ebur128/sidechaincompress; no other deps).
Generation tools and prompts: `references/generation.md`. Export specs per platform: `references/export-formats.md`.

## Pipeline
1. **Script** the session as text + pauses (see Pacing). Store it as `session.json` beside the clips.
2. **Voice:** generate one TTS clip per sentence or short paragraph, never the whole script in one call (see Voice).
3. **Assemble:** `python scripts/assemble_narration.py session.json voice.wav` trims TTS edge silence, high-passes at 80 Hz, puts 15 ms fades on every clip, inserts the pauses, prints a cue sheet.
4. **Bed:** generate or pick the music (see Music bed), then `python scripts/make_loop.py bed.wav bed_loop.wav --bpm 70 --bars 32` for a seamless loop.
5. **Mix + master:** `python scripts/mix_bed.py voice.wav bed_loop.wav out.m4a` (bed 14 LU under the voice, ducked, intro/outro, faded, mastered to -16 LUFS / -1.5 dBTP).
6. **Verify:** `python scripts/check_audio.py out.m4a` must print PASS; then listen to the whole thing once, start to end, on phone speakers and on earbuds.

Done = every track PASSes `check_audio.py`, was listened to end to end, and its settings are logged (see Project log).

## Session JSON
```json
{"lead_in": 4, "tail": 3,
 "items": [{"file": "clips/01-welcome.wav"}, {"pause": 3},
           {"file": "clips/02-breathe-in.wav"}, {"pause": 6},
           {"file": "clips/03-body-scan.wav"}, {"pause": 20}]}
```
`lead_in` is bed alone before narration inside the voice file; `mix_bed.py --intro` adds more on top. Keep clips and pauses as separate items so one sentence can be regenerated without re-timing the rest.

## Pacing (silence is the content)
- Speech rate 100-130 wpm for guided meditation, slower than any TTS default. Slow the voice with the provider's speed setting, or `atempo=0.9` (keeps pitch; below about 0.85 artefacts show).
- Pauses are explicit items, never punctuation tricks ("..." in TTS text is read unpredictably).
- Defaults: 1.5-3 s between sentences in one instruction; 4-8 s after "breathe in"/"breathe out" (match the breath count you ask for: "in for 4" = 4 s pause); 15-60 s after an open instruction ("notice your thoughts"); 2-5 min of bed alone is fine in sleep tracks.
- Breathing exercises: time pauses from the count, not from feel. A 4-7-8 cycle = 4 + 7 + 8 s of pause items around the cue words.
- Open with 6-10 s of bed before the first word; end with 20-60 s of bed after the last word, then a 10-20 s fade. A word in the first second startles; a hard stop after the last word breaks the state the track built.
- Long silences are music-only, never digital silence: apps and listeners read 10+ s of true silence as broken. `check_audio.py` flags it.

## Voice (TTS)
- One clip per sentence or short paragraph. Long single generations drift in pace, pitch and loudness, and one bad word forces regenerating everything.
- Pin the voice: same voice id, model, stability/style settings and speed for every clip of a series. Log them.
- Generate 2-3 takes of key lines and pick by ear; TTS mispronounces names and stresses the wrong word. Fix with phonetic spelling or the provider's pronunciation/SSML features, not by editing audio.
- Clean only what is there: TTS output is already clean, so just high-pass 80 Hz (in `assemble_narration.py`). For recorded human voice add light denoise: `highpass=f=90:poles=2,lowshelf=f=180:g=-3,afftdn=nr=12:nf=-35:tn=1`, and note afftdn delays audio about 25 ms.
- Level each clip before joining only if takes differ by more than 2 LU (measure with `common.loudness`); the master handles overall level.
- Never put a quiet voice straight into a hard limiter: level it first, or true peak overshoots.

## Music bed
- Character: lo-fi / ambient, 55-75 BPM (near a resting heart rate), soft attack, no vocals, no lyrics, no drops, no sudden hits, little energy above 8 kHz. Steady key; a drone or pad tonic (e.g. a major or Dorian key, or tuned to the narration's pitch area) keeps it calm.
- Avoid content in 1-4 kHz where the voice lives: sparse melody, low-passed keys, warm pads. `mix_bed.py` also dips 2.5 kHz by 3 dB.
- Generate 2-3 contrasting beds and let the person choose by listening. Generators default to busy and "hype"; ask for sparse explicitly. Numbers cannot say a bed is the wrong mood.
- Loops: AI tracks rarely loop cleanly. Snap the loop to whole bars (`--bpm --bars`; read BPM from the prompt or a beat tracker) and crossfade 3-6 s. Check `check_audio.py loop.wav --loop` and listen across the seam twice.
- Licensing: check the generator's terms for commercial use in an app on the plan used, and keep the prompt, date and plan per bed (see Project log). Free tiers often exclude commercial use.

## Mixing levels and ducking
- Bed 12-16 LU under the voice (momentary medians; `--bed-lu`). 14 is the default; under about 18 the bed disappears on phone speakers, over about 10 it fights the words.
- Ducking: slow and shallow, 3-5 dB under words (`--duck`), 80 ms attack, ~1.2 s release, so the bed breathes back up in pauses without audible pumping. Fast release = pumping.
- Every edit boundary gets a fade: 15-30 ms on voice clips, seconds on the bed. Hard cuts click.
- Mix to 24-bit PCM, master once at the end. Re-mastering an already-mastered file stacks limiting.

## Loudness targets
| Use | Integrated | True peak |
|---|---|---|
| Guided meditation / spoken (default) | -16 LUFS | -1.5 dBTP |
| Music-forward focus tracks, to match streaming | -14 LUFS | -1.0 dBTP |
| Sleep tracks (played at night, quiet rooms) | -18 to -20 LUFS | -2 dBTP |

Keep one target across the whole catalogue so tracks do not jump in level when the app moves between them. `master.py` measures the ENCODED file and corrects in a loop until it is within 0.3 LU and under the peak ceiling: lossy encoders (AAC, MP3) add peak overshoot after limiting, so a pre-encode measurement is not proof. It avoids ffmpeg `loudnorm`, which switches to dynamic mode on peaky input and pumps ambient material.

## Exports
Default delivery: AAC in M4A, 48 kHz stereo, 256 kbps (spoken-only tracks can go mono 96-128 kbps). Keep a 24-bit WAV or FLAC master of every track. Loops for in-app playback: WAV/CAF or a gapless-aware format, never MP3 (encoder priming adds a gap at every repeat). Details: `references/export-formats.md`.

## Verification habits
- `check_audio.py` on every exported file, not just the master: loudness, true peak, flat-topped peaks, DC offset, dead air, and `--loop` seam level.
- Listen to the whole track once at the end, at normal volume, on phone speakers and earbuds. Listen to every join and every loop seam. Measurement catches levels; only listening catches a mispronounced word, a breath cut in half, or the wrong mood.
- Spot-check timing: the cue sheet from `assemble_narration.py` vs the script; each "breathe in for 4" has its 4 s.
- A file that measures near -50 LUFS or flat with no movement has no voice in it (wrong input, muted clip): stop and check inputs.
- When a note is repeated ("the music is too loud again"), it is a defaults bug: change the default in the script or this file, then re-render and recheck every track that used the old default.

## Project log
Keep `project.md` beside the tracks. Per track: script version, TTS provider + voice id + model + settings, bed source (tool, prompt, seed, date, plan/licence), BPM/key, `--bed-lu`/`--duck`/target, output files, check results, listener notes. Regenerating a track months later depends on this.

## Pitfalls
- Whisper or TTS timestamps are approximate (0.2-0.5 s early ends): never cut voice at a word time without checking the waveform; `assemble_narration.py` trims with a silence threshold instead.
- `-stream_loop` on an unlooped bed clicks at every repeat: run `make_loop.py` first.
- `amix` defaults to dividing by input count; scripts use `normalize=0`.
- Backgrounded CLI generators that read stdin can hang forever: run them with `< /dev/null`.
- macOS filenames ignore case: `track_final.m4a` and `track_FINAL.m4a` are one file.
- Some ffmpeg builds lack `drawtext`/libass; irrelevant to audio, but check `ffmpeg -filters` for `ebur128`, `sidechaincompress`, `alimiter` and `libopus`/`libmp3lame` encoders before starting.
