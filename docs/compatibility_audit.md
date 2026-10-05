# GALILEO / JARVIS ESP32-S3 AUDIO BOARD - COMPATIBILITY AUDIT

Data: 2026-10-03

Scope: audit non distruttivo della board collegata via USB, verifica compatibilita' ESPHome + Home Assistant Assist, confronto con progetti esistenti, backup factory e build test senza flash.

## BOARD IDENTIFICATION

Commercial name: diymore ESP32-S3 AI Audio Board

Probable manufacturer: Waveshare-compatible / rebrand

Board model: `waveshare-s3-audio-board`, dal boot log factory

Original/Rebrand/Clone/Unknown: **Rebrand or clone compatible, not proven original**

Evidence:

- USB: `303a:1001 Espressif USB JTAG/serial debug unit`, `/dev/ttyACM0`, driver `cdc_acm`
- Chip: ESP32-S3 QFN56 rev v0.2, MAC `28:84:85:b2:b8:18`
- Flash: 16 MB
- PSRAM: 8 MB
- Factory firmware: `xiaozhi` v1.8.9, ESP-IDF v5.4.1
- Factory firmware board SKU: `waveshare-s3-audio-board`
- Waveshare docs list ESP32-S3R8, 16 MB Flash, 8 MB PSRAM, ES7210, ES8311, dual microphones, speaker, 7 RGB LEDs, TCA9555, TF slot and Bluetooth/Wi-Fi.

Conclusion: the connected board is electrically very likely compatible with Waveshare ESP32-S3-AUDIO-Board. It cannot be called a confirmed original Waveshare unit because no physical manufacturer/revision marking was read from the PCB.

## ESP32

- Status: CONFIRMED
- Chip: ESP32-S3
- Revision: v0.2
- CPU: dual-core LX7 class, 240 MHz capability
- USB mode: USB-Serial/JTAG
- Secure Boot: disabled
- Flash Encryption: disabled
- Confidence: HIGH

## FLASH

- Status: CONFIRMED
- Size: 16 MB
- Backup: PASS
- Backup path: `hardware/esp32-s3-audio/backups/esp32_s3_audio_factory_FULL.bin`
- Backup size: 16,777,216 bytes
- Backup SHA256: `d0b72eddaf4486a1bd25f4852f42d78dcd763c82e0bc0ffc3653991b317b75e8`
- Note: backup files are ignored by git.

## PSRAM

- Status: CONFIRMED
- Size: 8 MB
- Evidence: esptool chip info and factory boot log `Found 8MB PSRAM device`
- Confidence: HIGH

## AUDIO HARDWARE

### ES7210

- Status: DETECTED BUT UNTESTED
- Evidence: factory boot log initializes `ES7210`, enables MIC1-MIC4, TDM mode, unmuted.
- ESPHome support: official `audio_adc: platform: es7210`
- Default ESPHome I2C address: `0x40` unless overridden
- Interface: I2C control + I2S/TDM audio input
- Confidence: HIGH for presence/init, MEDIUM for exact microphone mapping

### ES8311

- Status: DETECTED BUT UNTESTED
- Evidence: factory boot log initializes `ES8311`, output enable true, audio codec started.
- ESPHome support: official `audio_dac: platform: es8311`
- Interface: I2C control + I2S audio output
- Confidence: HIGH for presence/init

### MIC LEFT

- Status: DETECTED BUT UNTESTED
- Evidence: Waveshare docs say dual microphone array; factory log enables multiple ES7210 inputs.
- Limitation: left/right physical mapping not validated by acoustic test.
- Confidence: MEDIUM

### MIC RIGHT

- Status: DETECTED BUT UNTESTED
- Evidence: same as MIC LEFT.
- Confidence: MEDIUM

### Speaker

- Status: DETECTED BUT UNTESTED
- Evidence: Waveshare docs list speaker header/amplifier; factory log enables output; ESPHome candidate uses ES8311 + amplifier enable.
- Functional playback not yet tested after ESPHome flash.
- Confidence: MEDIUM

### Amplifier

- Status: PROBABLE
- Evidence: Waveshare docs mention amplifier chip; candidate ESPHome config uses TCA9555 channel `8` as active-high `PA_EN / amplifier enable`.
- Exact IC not verified on this physical board.
- Confidence: MEDIUM

### I2S

- Status: CONFIRMED FOR DESIGN / DETECTED IN FACTORY LOG
- Factory log shows I2S TDM/std modes at 24 kHz.
- Candidate ESPHome config compiles two I2S bus definitions over shared clock pins.
- Confidence: HIGH

### I2C

- Status: CONFIRMED FOR DESIGN / DETECTED WITH WARNING
- Factory boot log shows I2C activity and a pull-up warning.
- Candidate ESPHome config uses I2C GPIO11/GPIO10 at 100 kHz.
- Risk: verify bus scan after flash.
- Confidence: HIGH

## OTHER HARDWARE

| Component | Status | Evidence | Confidence |
| --- | --- | --- | --- |
| Wi-Fi | CONFIRMED | Factory firmware starts STA + AP `Xiaozhi-B819` | HIGH |
| Bluetooth | DETECTED BUT UNTESTED | ESP32-S3 chip feature; not exercised | MEDIUM |
| RGB | PROBABLE | Waveshare docs list 7 RGB LEDs; ESPHome candidate uses WS2812 on GPIO38 | MEDIUM |
| microSD | PROBABLE | Waveshare docs and schematic list TF/SD; not in factory boot log | MEDIUM |
| Buttons | PROBABLE | Waveshare docs list keys; candidate config uses TCA9555 keys 9/10/11 plus GPIO0 BOOT | MEDIUM |
| Display/camera headers | DETECTED BUT UNTESTED | Factory firmware initializes display and attempts camera; camera probe fails without supported sensor | MEDIUM |

## PINOUT

Pins below are **not invented**. They come from the candidate ESPHome project v1.1.1 and are consistent with the Waveshare board family and factory boot evidence. The physical diymore PCB is not independently probed with a multimeter yet.

| GPIO / expander | Function | Source | Confidence |
| --- | --- | --- | --- |
| GPIO10 | I2C SCL | Candidate ESPHome `base/core.yaml`; Waveshare design family | HIGH |
| GPIO11 | I2C SDA | Candidate ESPHome `base/core.yaml`; Waveshare design family | HIGH |
| GPIO12 | I2S MCLK | Candidate ESPHome `base/core.yaml` | HIGH |
| GPIO13 | I2S BCLK / SCLK | Candidate ESPHome `base/core.yaml` | HIGH |
| GPIO14 | I2S LRCLK / WS | Candidate ESPHome `base/core.yaml` | HIGH |
| GPIO15 | I2S DIN, ES7210 to ESP32 | Candidate ESPHome `base/core.yaml` | HIGH |
| GPIO16 | I2S DOUT, ESP32 to ES8311 | Candidate ESPHome `base/core.yaml` | HIGH |
| GPIO38 | WS2812 RGB ring data | Candidate ESPHome `base/core.yaml` | MEDIUM |
| TCA9555 `0x20`, channel 8 | PA_EN / amplifier enable, active high | Candidate ESPHome `base/core.yaml` | MEDIUM |
| TCA9555 `0x20`, channel 9 | Key1 / volume down | Candidate ESPHome `base/core.yaml` | MEDIUM |
| TCA9555 `0x20`, channel 10 | Key2 / play-pause | Candidate ESPHome `base/core.yaml` | MEDIUM |
| TCA9555 `0x20`, channel 11 | Key3 / volume up | Candidate ESPHome `base/core.yaml` | MEDIUM |
| GPIO0 | BOOT button, strapping pin | Candidate ESPHome and ESP32-S3 behavior | HIGH with caution |
| microSD pins | UNKNOWN in selected ESPHome project | Not used by candidate config | UNKNOWN |

## SOFTWARE COMPATIBILITY

### ESPHome

- Status: CONFIRMED BUILD PASS
- Tested version: ESPHome 2026.9.1
- Framework: ESP-IDF 5.5.5 downloaded by ESPHome
- Candidate config: `MichalZaniewicz/esphome-waveshare-esp32-s3-audio-va` pinned `v1.1.1`
- Build result: PASS
- First flash/runtime result: PASS on 2026-10-04; device reachable as `galileo-va.local` at `192.168.1.171`

Build metrics:

- `waveshare-va.bin`: `0x1b8190` bytes
- App partition: `0x7c0000` bytes
- Free app partition: 78%
- RAM: 43.5% used, 148,611 / 341,760 bytes
- Flash: 22.2% used, 1,802,519 / 8,126,464 app bytes
- Warning: GPIO0 strapping pin warning for BOOT button; not fatal.

### Home Assistant Assist

- Status: COMPATIBLE
- ESPHome `voice_assistant` streams microphone audio to Home Assistant Assist.
- Assist pipelines support wake/STT/intent/TTS stages.
- The planned Galileo architecture, including later orchestrator split between domotica and LLM, is not blocked by this satellite firmware.

### voice_assistant

- Status: CONFIRMED BUILD PASS
- Candidate config wires `voice_assistant` to `i2s_mics`, `external_media_player`, and `micro_wake_word`.

### micro_wake_word

- Status: CONFIRMED BUILD PASS
- Candidate config downloads official ESPHome model manifests/TFLite files, including:
  - `hey_jarvis.json`
  - `hey_jarvis.tflite`
  - `vad.json`
- Important: ESPHome microWakeWord models are not generic openWakeWord server models. Use microWakeWord-format models for on-device ESP32 detection.

### Speaker / TTS Playback

- Status: CONFIRMED BUILD PASS, HARDWARE UNTESTED
- Candidate uses speaker media player with ES8311 DAC, I2S speaker output, mixer/resampler, and Home Assistant media/announcement pipelines.

## PROJECT COMPARISON

### 1. MichalZaniewicz/esphome-waveshare-esp32-s3-audio-va

- Compatibility: HIGH
- Dependencies: ESPHome standard, external package from GitHub, ESP-IDF framework, official ESPHome audio/wake components.
- External components: no forked ESPHome detected in tested build; package uses upstream ESPHome components.
- Known limitations:
  - GPIO0 strapping warning for BOOT button.
  - Full-duplex is handled by two I2S buses sharing clock pins; this is a configuration workaround, not hardware AEC.
  - Runtime hardware audio still must be tested after first flash.
- Build result: BUILD PASS
- Best fit: YES

### 2. hannes813/waveshare-esp32-s3-ai-home-assistant-voice

- Compatibility: PROBABLE
- Dependencies: GitHub project for same board class.
- External components: not build-tested in this pass.
- Known limitations: not selected because the first project already compiles with current ESPHome and has explicit pin/full-duplex commentary.
- Build result: NOT RUN
- Best fit: backup/reference, not first flash candidate.

### 3. Generic ESP32-S3 AI smart speaker projects

- Compatibility: UNKNOWN to PROBABLE
- Usefulness: reference only.
- Reason: many boards share ESP32-S3 + ES7210/ES8311 shape but differ in GPIO, expander, LED and amplifier wiring. They must not override the Waveshare-specific pinout without direct evidence.

## HEY JARVIS

Local wake feasibility: HIGH

Evidence: candidate ESPHome build downloads and compiles official ESPHome microWakeWord `hey_jarvis` model.

Central wake feasibility: HIGH

Evidence: Home Assistant supports wake-word stage and openWakeWord/Wyoming style wake detection, but that approach streams audio to HA for wake detection.

Recommended approach for initial testing: **local micro_wake_word on ESP32 using `hey_jarvis`**

Reason:

- It compiled successfully.
- It avoids constant raw audio streaming to Home Assistant until wake.
- It matches the satellite model and keeps the Raspberry/HA side simpler.
- If false positives are bad, central openWakeWord can be evaluated later with better logs and easier model swapping.

Difference:

- `micro_wake_word`: ESPHome/on-device, model format expected by ESPHome/microWakeWord.
- `openWakeWord`: usually server-side or Wyoming/Home Assistant path, model handling and runtime are different. Do not assume a `.tflite` from one path is directly usable in the other without matching metadata/runtime.

## AUDIO LIMITATIONS

### AEC

- Hardware AEC: UNKNOWN / NOT CONFIRMED
- Waveshare marketing mentions echo cancellation/noise reduction/far-field behavior, but this audit did not find proof that ES7210 or ES8311 themselves provide standalone hardware AEC.
- ESPHome candidate sets `noise_suppression_level: 0` and `auto_gain: 0 dbfs` in `voice_assistant`, so AEC/NS is not currently being claimed there.

### Noise suppression

- ESPHome/HA software path: available in Assist pipeline settings and voice assistant options.
- Factory firmware: appears to use WakeNet/Xiaozhi stack; exact AFE configuration unknown.
- Recommendation: start with conservative settings, measure false positives and missed wakes, then tune.

### Full duplex

- Hardware: probable, because ES7210 input and ES8311 output are separate chips sharing I2S clocking.
- ESPHome candidate: explicitly supports simultaneous capture/playback by using two I2S buses with shared BCLK/LRCLK: mic bus primary/master, speaker bus secondary/slave.
- Build: PASS.
- Runtime: still needs speaker + mic test after flash.

### Self wake

- Candidate handles wake word during announcements/media by stopping announcements or starting/stopping Assist depending on state.
- No proven acoustic echo cancellation yet, so self-wake prevention remains a runtime tuning item.

## RISKS

1. Board identity is not 100% original Waveshare.
   - Mitigation: factory firmware reports `waveshare-s3-audio-board`, matching candidate project expectations.

2. RGB/buttons/amplifier pinout depends on TCA9555 mapping.
   - Mitigation: project cites Waveshare driver behavior; verify immediately after flash with LED/button/speaker tests.

3. GPIO0 strapping pin warning.
   - Mitigation: leave BOOT as diagnostic/deep sleep only; do not add external pullups/pulldowns.

4. No runtime ESPHome audio test yet.
   - Mitigation: after first flash, test in this order: boot logs, I2C scan, LEDs, speaker chime, microphone level, `hey_jarvis`, Assist round trip.

5. AEC claims are not proven.
   - Mitigation: do not rely on hardware AEC; tune VAD/wake thresholds and physical placement.

6. Factory firmware will be overwritten by first flash.
   - Mitigation: full 16 MB backup with SHA256 exists before proceeding.

## VERDETTO TECNICO

**GO WITH CHANGES**

Meaning: hardware and software are compatible enough to proceed to the first controlled ESPHome flash, but we should treat the board as a Waveshare-compatible/rebrand rather than an original-proven unit, and runtime validation is mandatory immediately after flash.

RECOMMENDED BASE PROJECT:

`MichalZaniewicz/esphome-waveshare-esp32-s3-audio-va` pinned release `v1.1.1`

REQUIRED CHANGES BEFORE FLASH:

1. Create our own thin Galileo YAML from `waveshare-va.yaml`.
2. Set device name/friendly name for Galileo.
3. Set real Wi-Fi/API secrets outside git.
4. Set timezone to Europe/Rome.
5. Keep `hey_jarvis` enabled.
6. Do not enable deep sleep initially.
7. Keep volume conservative.
8. Prepare first-boot checklist for LED, speaker, mic, wake and Assist.

SAFE TO FLASH NEXT:

YES, with backup already completed and with the above thin-config changes.

CONFIDENCE:

MEDIUM-HIGH
