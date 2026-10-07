# ESP32-S3 Audio / ESPHome Project

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

- `hardware/esp32-s3-audio/esphome/galileo-va.yaml`: thin local ESPHome config.
- `hardware/esp32-s3-audio/esphome/secrets.example.yaml`: local secrets template.
- `hardware/esp32-s3-audio/docs/initial_board_audit.md`: factory firmware and hardware audit.
- `hardware/esp32-s3-audio/docs/compatibility_audit.md`: ESPHome/Home Assistant compatibility notes.
- `hardware/esp32-s3-audio/docs/first_flash_checklist.md`: first flash result and runtime checklist.
- `hardware/esp32-s3-audio/docs/references.md`: external reference links.
- `hardware/esp32-s3-audio/diagnostics/`: sanitized chip, flash, USB, and factory diagnostic outputs.

## Firmware Shape

The local ESPHome file is intentionally thin. Board-specific implementation is pulled from:

- `MichalZaniewicz/esphome-waveshare-esp32-s3-audio-va`
- pinned ref: `v1.1.1`

Local substitutions define:

- device name: `galileo-va`
- friendly name: `Galileo Voice`
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

Prepared but still needs runtime validation:

- Home Assistant discovery/adoption.
- Assist device controls.
- LED ring behavior.
- Speaker and TTS playback.
- Microphone audio into Assist.
- Local wake word behavior.
- Full Assist round trip.

## Home Assistant Assist Path

Repo-side integration is prepared through ESPHome components:

- `api`
- `voice_assistant`
- `external_media_player`
- `micro_wake_word`

Initial wake word:

- `hey_jarvis`
- local ESPHome microWakeWord model

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

1. Open/adopt `Galileo Voice` in Home Assistant through ESPHome.
2. Confirm `hey_jarvis` is selected and enabled from device controls.
3. Run the first-boot runtime checklist:
   - LED ring
   - speaker at conservative volume
   - microphone into Assist
   - wake word
   - full Assist round trip
4. Capture ESPHome logs for any codec, audio, wake, or API failures.
5. Only raise volume limits after a clean speaker/TTS test.

## Privacy And Git Notes

Do not commit:

- `hardware/esp32-s3-audio/esphome/secrets.yaml`
- factory flash backups
- generated firmware binaries
- local Home Assistant credentials or tokens
- runtime logs containing private network details

