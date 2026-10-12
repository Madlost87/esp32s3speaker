# Software And Model Versions

Queste versioni descrivono il firmware target su cui dovra' girare la wake word custom.

## Build Target

| Item | Versione / valore |
| --- | --- |
| Firmware framework | ESPHome |
| ESPHome build version | 2026.9.1 |
| Build timestamp osservato | 2026-10-12 |
| ESP-IDF | 5.5.5 |
| Target ESP-IDF | esp32s3 |
| ESPHome config | `esphome/galileo-va-afe.yaml` |
| Runtime packages | `n-IA-hane` ESPHome intercom/audio/VoIP/runtime-controller packages |
| Upstream package min ESPHome | 2026.9.0 |

## Runtime Wake Word

| Item | Versione / valore |
| --- | --- |
| ESPHome component | `micro_wake_word` |
| Model manifest schema | microWakeWord JSON `version: 2` |
| Model file format | TensorFlow Lite Micro `.tflite` |
| VAD model | ESPHome microWakeWord `vad.json` v2 |
| Wake models loaded | `alexa`, `okay_nabu`, `hey_jarvis` |
| Wake models enabled at boot | `alexa`, `okay_nabu` |
| Wake model loaded but disabled | `hey_jarvis` |
| Inference location | On-device on ESP32-S3 |
| Server model compatibility | Not openWakeWord/Wyoming server format |

## Relevant Managed Components

Resolved ESP-IDF managed components observed in the ESPHome build:

| Component | Version | Role |
| --- | --- | --- |
| `espressif/esp-tflite-micro` | `1.3.3~1` | TensorFlow Lite Micro runtime |
| `espressif/esp-nn` | `1.1.2` | Espressif NN acceleration |
| `esphome/esp-micro-speech-features` | `1.2.3` | Micro speech feature extraction / spectrogram features |
| `esphome/esp-audio-libs` | `3.2.1` | Audio/resampling support |
| `esphome/micro-flac` | `0.2.0` | FLAC decode path for media/TTS |
| `esphome/micro-mp3` | `0.4.0` | MP3 decode path for sounds/media |

## Audio Parameters Relevant To Training

| Item | Value |
| --- | --- |
| Microphone ADC | ES7210 |
| Audio input path | ES7210 TDM through full AFE profile |
| PDM | false |
| Sample rate for wake/mic | 16000 Hz |
| Bits per sample | 16 bit |
| Default ES7210 gain | 24 dB |
| Runtime gain step | 3 dB |
| Channel expectation | AFE processed mono stream consumed by ESPHome wake pipeline |

## Model Delivery Contract

Please deliver:

```text
hey_galileo.json
hey_galileo.tflite
```

The JSON should include the real recommended values for:

- `probability_cutoff`
- `sliding_window_size`
- `feature_step_size`
- `tensor_arena_size`
- `minimum_esphome_version`

If a different ESPHome minimum version is required, include it explicitly in the manifest and note it in the handoff.
