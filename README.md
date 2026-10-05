# Galileo ESP32-S3 Audio

ESPHome configuration and hardware notes for the Galileo/Jarvis ESP32-S3 voice satellite.

The active firmware entrypoint is `esphome/galileo-va.yaml`. It pins the tested upstream Waveshare ESP32-S3 audio voice-assistant package and keeps local Wi-Fi/API credentials in an ignored `esphome/secrets.yaml`.

## Important Files

- `esphome/galileo-va.yaml` - thin ESPHome configuration for the voice satellite.
- `esphome/secrets.example.yaml` - template for local credentials.
- `docs/initial_board_audit.md` - non-destructive board audit and factory backup notes.
- `docs/compatibility_audit.md` - ESPHome/Home Assistant compatibility notes and tested status.
- `docs/first_flash_checklist.md` - first flash checklist and runtime validation order.
- `docs/references.md` - hardware and software references used during the audit.

## Local-Only Data

Factory flash backups, build outputs, virtual environments, and real secrets are intentionally ignored by Git.
