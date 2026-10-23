# Raspberry / ReSpeaker Project

## Scope

This track is the original Galileo voice satellite prototype.

Hardware:

- Raspberry Pi Zero 2 W
- KEYESTUDIO ReSpeaker 2-Mic Pi HAT v1.0 / WM8960
- Amplified speaker connected to the HAT jack

Goal:

- Run a local satellite process on Raspberry Pi.
- Capture microphone audio through ALSA.
- Detect speech and eventually the custom wake word `Galileo`.
- Stream the following utterance to a server or Home Assistant-facing pipeline.
- Play TTS audio back through the local speaker.

## Repository Areas

- `satellite/`: Raspberry-side Python package for capture, preprocessing, VAD, state diagnostics, dataset recording, and future wake-word integration.
- `config/galileo.toml`: current Raspberry audio, VAD, state, wake-word, and dataset settings.
- `scripts/`: Raspberry setup, diagnostics, ReSpeaker LED, playback, openWakeWord, and capture helpers.
- `diagnostics/`: sanitized validation reports and benchmark notes.
- `docs/wakeword_audit.md`: detailed wake-word assessment and recommended reliability path.

## Current Status

Validated:

- Raspberry Pi OS Lite boots.
- Wi-Fi and SSH work.
- WM8960/ReSpeaker audio is available through ALSA as `hw:0,0`.
- Real microphone capture works after enabling the input mixer boost path.
- Playback through the HAT jack works.
- Initial full-duplex capture/playback test passed.
- Python capture and preprocessing path works.
- Energy-based VAD diagnostic works.
- Diagnostic state loop works: `IDLE -> LISTENING -> PROCESSING -> IDLE`.
- Dataset recorder works and stores personal WAV data outside git.
- openWakeWord pilot training/scoring has been tested.
- ReSpeaker APA102 LEDs work and are used by wake-word diagnostics.
- A continuous Raspberry-side openWakeWord LED diagnostic exists.

Not final yet:

- The wake-word detector is not integrated into `satellite/wakeword/` as the main runtime.
- `PROCESSING` is still a stub in the state machine.
- Streaming, STT, TTS playback, watchdog service, and final 24/7 behavior are not complete.
- Microphone left/right separation and DC offset still need tuning.
- Speaker leakage must be retested at realistic TTS volume.

## Wake Word Direction

Selected primary path:

- openWakeWord custom model for `Galileo`

Fallback:

- Porcupine custom model, only if openWakeWord stalls or reliability becomes more important than avoiding vendor dependency.

Important distinction:

- Raspberry uses openWakeWord/ONNX-style models.
- ESP32-S3 ESPHome uses microWakeWord/TFLite-style models.
- These model formats and runtimes should not be treated as interchangeable.

## Next Actions

1. Collect more LED-guided real samples:
   - positive: `Galileo`
   - negative: normal speech without `Galileo`
   - noise: room silence, TV/music/domestic noise
   - speaker echo: future TTS/playback leakage
2. Build an explicit train/validation/holdout manifest.
3. Retrain and evaluate a new openWakeWord pilot.
4. Promote a model only after fresh holdout tests pass.
5. Add the real detector behind `satellite/wakeword/`.
6. Gate the state machine on wake-word detection instead of VAD-only speech.
7. Add streaming and playback paths.
8. Create a final systemd service only after wake and audio behavior are stable.

## Privacy And Git Notes

Personal recordings, generated models, local datasets, local captures, logs, backups, and credentials should stay outside git.

Relevant ignored locations include:

- `local_data/`
- `recordings/`
- `logs/`
- `*.wav`
- `hardware/esp32-s3-audio/backups/`

