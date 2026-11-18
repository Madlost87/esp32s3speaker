# ESP32-S3 Audio / ESPHome Project

> Stato: documento storico di bring-up.
>
> La guida operativa corrente e' il README principale insieme a
> [satellites.md](satellites.md) e [fleet.md](fleet.md). Il firmware attivo oggi e'
> `esphome/galileo-va-direct-audio-cutover-base.yaml`; i profili storici sono
> in `esphome/archivio/`.

## Scope

This track is the newer Galileo voice satellite path based on an ESP32-S3 audio board and ESPHome.

Hardware:

- diymore ESP32-S3 AI Audio Board
- Treated as Waveshare ESP32-S3-AUDIO-Board compatible
- ESP32-S3 with 16 MB flash and 8 MB PSRAM
- ES7210 microphone ADC
- ES8311 speaker DAC

Goal:

- Run the device as a Home Assistant Assist voice satellite.
- Use ESPHome for firmware, API, OTA, audio, media playback, and wake-word integration.
- Keep the device simpler than the Raspberry path by leaning on Home Assistant Assist for the voice pipeline.

## Repository Areas

- `esphome/galileo-va-direct-audio-cutover-base.yaml`: current firmware base.
- `esphome/archivio/`: historical, lab and recovery ESPHome configs.
- `esphome/secrets.example.yaml`: local secrets template.
- `docs/`: audit, runtime validation, recovery, wake-word and feature notes.
- `diagnostics/`: sanitized chip, flash, USB, and factory diagnostic outputs.

## Firmware Shape

The original local ESPHome file was intentionally thin and used:

- `MichalZaniewicz/esphome-waveshare-esp32-s3-audio-va`
- pinned ref: `v1.1.1`

That profile is no longer the operational baseline. The current firmware uses
the full AFE profile, then in `esphome/galileo-va-afe.yaml` (now archived in `esphome/archivio/`).

Local substitutions define:

- device name: `galileo-va`
- friendly name: `Satellite Taverna`
- conservative volume limits
- Europe/Rome timezone
- no deep sleep for first bring-up

Wi-Fi credentials live in local `secrets.yaml`, which is ignored by git.

## Current Status

Validated:

- Factory firmware was identified as `xiaozhi` v1.8.9.
- Board reports SKU `waveshare-s3-audio-board`.
- Secure Boot and Flash Encryption are disabled.
- Full 16 MB factory flash backup completed and stored outside git.
- ESPHome build passed.
- First ESPHome flash passed on 2026-10-04.
- Device joined Wi-Fi as `galileo-va.local`, IP `192.168.1.171`.
- ESPHome API was reachable on port `6053`.
- OTA was reachable on port `3232`.

Later runtime validation moved the project to the full AFE baseline. Current
validated items are tracked in `runtime-validation-20261008.md` and
`history/voip-centralino-esp32.md`.

## Home Assistant Assist Path

Repo-side integration is prepared through ESPHome components:

- `api`
- `voice_assistant`
- `external_media_player`
- `micro_wake_word`

Current wake-word model set:

- `alexa`
- `okay_nabu`
- `hey_jarvis`

At boot only `Okay Nabu` is enabled (since 2026.11.7). `Alexa` and `Hey Jarvis` are loaded but disabled.
See `wake-word-models.md`.

Important distinction:

- ESP32-S3 uses ESPHome microWakeWord models.
- Raspberry uses openWakeWord/ONNX models.
- Do not reuse a Raspberry ONNX wake-word model directly on this ESPHome path.

## Piper / TTS Note

This repository does not configure Piper directly.

The ESP32-S3 path is prepared to participate in a Home Assistant Assist pipeline that includes wake, STT, intent, and TTS stages. If Piper is used, it should be configured in Home Assistant as the TTS engine for the Assist pipeline, not in this repository.

## Main Risks

- Runtime audio quality is still unknown.
- Speaker distortion/leakage needs testing before raising volume.
- Wake reliability needs near, normal, far, and low-voice tests.
- Hardware AEC is not proven.
- ESPHome noise suppression and Home Assistant pipeline settings may need tuning after real tests.

## Next Actions

1. Keep `esphome/galileo-va-afe.yaml` (now `esphome/archivio/`, archived) as the baseline.
2. Test `Listen Feedback Sound` ON/OFF and with `Speaker Mute` (switch only in the archived profile).
3. Measure wake reliability and false positives for `Okay Nabu` (the only active wake word since 2026.11.7).
4. Prepare the Galileo/Jarvis custom model when the ESPHome microWakeWord v2
   files are available.
5. Keep audio stack, pinout, AFE mode, VoIP packages and buffer strategy stable
   unless a new test proves a concrete failure.

## Privacy And Git Notes

Do not commit:

- `esphome/secrets.yaml`
- factory flash backups
- generated firmware binaries
- local Home Assistant credentials or tokens
- runtime logs containing private network details
