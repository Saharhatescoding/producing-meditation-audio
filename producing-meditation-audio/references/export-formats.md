# Export formats for apps

| Use | Format | Settings | Why |
|---|---|---|---|
| Master / archive | WAV or FLAC | 48 kHz, 24-bit, stereo | lossless source for every future re-export |
| Streamed or downloaded track (iOS + Android) | AAC in .m4a | 48 kHz, 256 kbps stereo (128 kbps mono for voice-only) | plays natively everywhere, small, good at low bitrates |
| Web / broad compatibility | MP3 | 44.1 or 48 kHz, 192-320 kbps CBR | universal; not for loops (priming gap) |
| Small files, web/Android | Opus in .ogg/.webm | 96-160 kbps | best quality per byte; older iOS support is weaker |
| In-app seamless loops | WAV / CAF (iOS), OGG Vorbis with a gapless player, or PCM loaded into memory | 48 kHz | AAC and MP3 add encoder priming samples, so a naive repeat gaps or clicks |
| Streaming via HLS | AAC segments | 128-256 kbps | if the app streams long sleep tracks |

- Pick one sample rate (48 kHz) for the whole pipeline; resample once.
- `master.py OUT.ext` picks the codec from the extension: .wav, .flac, .m4a, .mp3, .ogg/.opus.
- Re-encode from the WAV master, never from another lossy file, and run `check_audio.py` on each export (true peak changes per codec).
- Metadata: set title/artist/album with `-metadata title="..."` on export if the app reads tags; artwork goes in the app, not the file.
- File names: lowercase, hyphens, stable ids (`body-scan-10min-v2.m4a`); the app references them.
- Loop playback in code: AVAudioPlayer `numberOfLoops = -1` or AVAudioEngine with a scheduled buffer (iOS); ExoPlayer `REPEAT_MODE_ONE` with a gapless source or SoundPool for short loops (Android); Web Audio `AudioBufferSourceNode.loop = true` (web). Test the seam on device.
