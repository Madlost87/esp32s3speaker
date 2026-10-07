# ESP32-S3 Audio Docs Manifest

This folder is a clean documentation bundle for the Galileo ESP32-S3 Audio / ESPHome track.

## Included

- `README.md`: ESP32-S3 Audio project summary.
- `docs/`: project overview, board audit, compatibility notes, first flash checklist, factory audio adaptation notes, and references.
- `diagnostics/`: sanitized hardware, USB, security, factory string, and partition diagnostics.
- `esphome/`: thin ESPHome config, experimental AFE config, and secrets template.
- `handoff/micro_wake_word_request/`: documentation and JSON templates for a future ESPHome microWakeWord custom model.

## Excluded

- Raspberry / ReSpeaker documentation and scripts.
- Local openWakeWord datasets, captures, ONNX models, and benchmark artifacts.
- Home Assistant migration, MQTT, Zigbee, and Wyoming stack files.
- ESPHome build caches, virtual environments, logs, generated binaries, and flash backups.
- Real secrets such as `secrets.yaml`.
- Binary example model files such as `.tflite`; only JSON/Markdown reference material is copied here.
