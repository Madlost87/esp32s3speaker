# ESP32-S3 Audio Docs Manifest

This folder is a clean documentation bundle for the Galileo ESP32-S3 Audio / ESPHome track.

Production: three satellites (Taverna, Sala, Garage) on the shared base
`esphome/galileo-va-direct-audio-cutover-base.yaml`, ESPHome 2026.9.1, full AFE
audio path, direct audio to Galileo Core and VoIP endpoints `101`-`103`.
See `docs/satellites.md` and, for releases and rollout, `docs/fleet.md` (`fleet/`, `tools/fleet.py`, `esphome/sites/`). Lab profiles and the recovery golden are in `esphome/archivio/`.

## Included

- `README.md`: public ESP32-S3 Audio project summary.
- `AUDIT_HARDWARE.md`: current hardware/firmware audit and intervention plan.
- `docs/`: operational guides, historical bring-up notes, runtime validation, recovery, wake-word notes, feature specs, and references. Include
  `docs/spec-011-firmware-modularity-and-transport-hardening.md` for the
  staged firmware refactor and its deployment safeguards; use
  `docs/specs-index.md` as the resumption point and work order.
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
