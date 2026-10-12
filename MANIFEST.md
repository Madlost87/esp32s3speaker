# ESP32-S3 Audio Docs Manifest

This folder is a clean documentation bundle for the Galileo ESP32-S3 Audio / ESPHome track.

Current operational baseline: `esphome/galileo-va-afe.yaml`, friendly name
`Satellite Taverna`, ESPHome 2026.9.1, full AFE audio path, Home Assistant
Assist and local VoIP endpoint `101`.

## Included

- `README.md`: public ESP32-S3 Audio project summary.
- `AUDIT_HARDWARE.md`: current hardware/firmware audit and intervention plan.
- `docs/`: operational guides, historical bring-up notes, runtime validation, recovery, wake-word notes, feature specs, and references.
- `diagnostics/`: sanitized hardware, USB, security, factory string, and partition diagnostics.
- `esphome/`: current full AFE ESPHome config, historical stock config, overlays, and secrets template.
- `handoff/micro_wake_word_request/`: documentation, template files, one example `.tflite`, and a tarball package for a future ESPHome microWakeWord custom model.

## Excluded

- Raspberry / ReSpeaker documentation and scripts.
- Local openWakeWord datasets, captures, ONNX models, and benchmark artifacts.
- Home Assistant migration, MQTT, Zigbee, and Wyoming stack files.
- ESPHome build caches, virtual environments, logs, generated binaries, and binary flash backups.
- Real secrets such as `secrets.yaml`.
- Real Wi-Fi, API, OTA, Home Assistant or SIP provider secrets.
