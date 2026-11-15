# Generating voice and music

## Contents
- Voice (TTS) options
- TTS settings that matter for meditation
- Music generation options
- Prompt patterns for beds
- Cost and licensing habits

## Voice (TTS) options
| Option | Notes |
|---|---|
| ElevenLabs | most natural calm voices; voice library + cloning; stability/similarity/style sliders and speed; per-character pricing |
| OpenAI TTS (`gpt-4o-mini-tts` and later) | cheap; accepts an instruction ("speak slowly and softly, like a meditation guide") |
| Google / Azure / Amazon Polly | SSML support (`<break time="3s"/>`, `<prosody rate="slow">`); good for exact pronunciation control |
| Local: Piper, Kokoro, XTTS/Coqui | free, offline, batchable; less expressive; check each model's licence |

Check current model names and prices on the provider's site before building; they change often.

## TTS settings that matter for meditation
- Higher stability (ElevenLabs ~0.6-0.8) = even, calm delivery; low stability adds drama.
- Speed 0.85-0.95 of default, or slow afterwards with `atempo` (pitch kept).
- Write for the ear: short sentences, second person, present tense; spell out numbers ("four").
- Put pauses in the session JSON, not in the text. SSML breaks are fine where supported, but JSON pauses stay editable without regenerating.
- Save every clip as WAV (or the highest-quality format offered), named `NN-slug.wav` in script order.
- Batch with a small script that reads the script file, calls the API per line, and skips clips already on disk, so a rerun regenerates only what changed. Keep API keys in an environment variable or `.env`, never in the script or the repo.

## Music generation options
| Option | Notes |
|---|---|
| Suno, Udio | full tracks from a text prompt, "instrumental" toggle; commercial use usually needs a paid plan |
| Stable Audio | good at ambient textures and loops; length and BPM in the prompt |
| ElevenLabs Music / sound generation | music and ambience from text |
| Local: MusicGen / AudioCraft, Stable Audio Open | free, offline, short clips (~30 s) you loop and layer; check model licences for commercial use |
| Royalty-free libraries (CC0 / licensed) | when generation will not give a usable bed |

## Prompt patterns for beds
- Name tempo, key, instruments, mood and what to leave out: "lo-fi ambient bed, 65 BPM, D major, warm Rhodes and soft pad, vinyl crackle, no drums, no vocals, no melody lead, slow evolving, for guided meditation".
- Ask for "sparse", "minimal", "no build-up", "no drop", "steady"; generators add energy by default.
- Ask for 2-4 minutes even if the track is longer: shorter, steadier material loops better.
- Layer if needed: a drone or pad bed plus a quieter textural layer (rain, ocean, room tone) mixed 6-10 dB under it.
- Record prompt, seed, tool, model version and date in `project.md` for each bed.

## Cost and licensing habits
- Generation costs money per call. Estimate the count (clips x takes) before a batch and confirm the budget with whoever pays.
- Keep generated originals; regenerate only changed lines.
- Confirm commercial-use rights for an app on the exact plan used, and keep a copy of the terms or receipt per bed.
- Never use a voice clone of a real person without their written consent.
