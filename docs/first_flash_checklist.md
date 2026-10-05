# Galileo ESP32-S3 First Flash Checklist

Use only after confirming the factory backup exists and `galileo-va.yaml` compiles.

## Before Flash

- Confirm backup SHA256: `d0b72eddaf4486a1bd25f4852f42d78dcd763c82e0bc0ffc3653991b317b75e8`
- Create local `hardware/esp32-s3-audio/esphome/secrets.yaml`
- Compile `hardware/esp32-s3-audio/esphome/galileo-va.yaml`
- Keep the board connected by USB for first serial logs

Last compile result:

- Date: 2026-10-04
- Result: PASS
- Firmware: `galileo-va.bin`
- Binary size: `0x1b8190`
- App partition free: 78%
- RAM used: 43.5%
- Flash used: 22.2%

## First Flash Result

- Date: 2026-10-04
- Result: PASS
- Device: `/dev/ttyACM0`
- Firmware: freshly rebuilt after writing local Wi-Fi secrets
- Upload: `INFO Successfully uploaded program.`
- Network: connected to SSID `casazenari`
- IP: `192.168.1.171`
- Hostname: `galileo-va.local`
- ESPHome API: `galileo-va.local:6053`
- OTA: `galileo-va.local:3232`
- Signal: `-40 dB`

Important note: the first upload reused an older cached build and tried to connect to the dummy SSID `GalileoBuildOnly`. The fix was to clean/rebuild the ESPHome project after creating `secrets.yaml`, then upload again. The rebuilt firmware contains `casazenari` and no longer contains `GalileoBuildOnly`.

## First Boot Test Order

1. Boot logs: PASS, no reboot loop observed.
2. Wi-Fi: PASS, connected to `casazenari`.
3. ESPHome API: PASS, reachable at `galileo-va.local:6053`.
4. Home Assistant discovery/API connection.
5. Select wake word `hey_jarvis` from the Home Assistant device controls.
6. LED ring: verify status changes.
7. Speaker: verify boot chime or test announcement at conservative volume.
8. Microphone: verify Assist receives speech.
9. Wake word: test near, normal voice, then low voice.
10. Full round trip: wake, STT italiano, HA/LLM response, TTS playback.

## Stop Conditions

- Reboot loop
- Codec init failure
- No Home Assistant API connection
- Speaker produces loud distortion
- Wake word triggers continuously without speech
