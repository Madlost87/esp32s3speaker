# ESP32-S3 Audio Board References

| COMPONENT | DOCUMENT | MANUFACTURER / PROJECT | REVISION | SOURCE | USED FOR |
| --- | --- | --- | --- | --- | --- |
| BOARD | ESP32-S3-AUDIO-Board Wiki | Waveshare | wiki oldid 110779 | https://www.waveshare.com/wiki/ESP32-S3-AUDIO-Board | Board features, components, demos, resources |
| BOARD | ESP32-S3-AUDIO-Board Documentation | Waveshare | current docs | https://docs.waveshare.com/ESP32-S3-AUDIO-Board | Board identity, SKU, components |
| BOARD | ESP32-S3-AUDIO-Board Schematic | Waveshare | 1.1 PDF | https://files.waveshare.com/wiki/ESP32-S3-AUDIO-Board/ESP32-S3-AUDIO-Board_1.1.pdf | Pinout, codec, ADC, LEDs, SD, power, buttons |
| ESP32-S3 | ESP32-S3 Series Datasheet | Espressif | official | https://www.espressif.com/sites/default/files/documentation/esp32-s3_datasheet_en.pdf | CPU, Wi-Fi/BLE, memory, USB, PSRAM capability |
| ESP32-S3 | ESP32-S3 Technical Reference Manual | Espressif | official | https://www.espressif.com/sites/default/files/documentation/esp32-s3_technical_reference_manual_en.pdf | I2S, USB Serial/JTAG, peripherals |
| ES7210 | ES7210 component documentation | ESPHome | 2026 docs | https://esphome.io/components/audio_adc/es7210/ | ESPHome support, I2C address default, sample/gain options |
| ES8311 | ES8311 component documentation | ESPHome | 2026 docs | https://esphome.io/components/audio_dac/es8311 | ESPHome support for ES8311 DAC |
| I2S | I2S Audio Component | ESPHome | 2026 docs | https://esphome.io/components/i2s_audio/ | I2S BCLK/LRCLK/MCLK/DIN/DOUT semantics |
| I2S MIC | I2S Audio Microphone | ESPHome | 2026 docs | https://esphome.io/components/microphone/i2s_audio/ | External ADC microphone configuration |
| MEDIA | Speaker Audio Media Player | ESPHome | 2026 docs | https://esphome.io/components/media_player/speaker/ | TTS/media playback, PSRAM warning, pipelines |
| WAKE | Micro Wake Word | ESPHome | 2026 docs | https://esphome.io/components/micro_wake_word/ | Local wake word, VAD, model JSON/TFLite support |
| VOICE | Voice Assistant | ESPHome | 2026 docs | https://esphome.io/components/voice_assistant/ | Assist streaming integration |
| HA ASSIST | Assist pipelines | Home Assistant Developer Docs | 2026 docs | https://developers.home-assistant.io/docs/voice/pipelines/ | Wake/STT/intent/TTS architecture |
| HA ASSIST | Assist overview | Home Assistant | 2026 docs | https://www.home-assistant.io/voice_control/ | ESPHome voice devices and Assist role |
| WAKE CENTRAL | openWakeWord add-on docs | Home Assistant add-ons | 2026 docs | https://github.com/home-assistant/addons/blob/master/openwakeword/DOCS.md | Central wake word option, custom model handling |
| PROJECT | ESPHome Waveshare ESP32-S3 Audio VA | Michal Zaniewicz | v1.1.1 tested | https://github.com/MichalZaniewicz/esphome-waveshare-esp32-s3-audio-va | Candidate firmware, pinout, build test |
| PROJECT | Waveshare ESP32-S3 Home Assistant Voice | hannes813 | current GitHub | https://github.com/hannes813/waveshare-esp32-s3-ai-home-assistant-voice | Alternative project comparison |
| LOCAL | ESP32 factory boot log | Galileo repo | 2026-10-03 capture | `diagnostics/esp32_factory_boot.log` | Factory firmware identity and init evidence |
| LOCAL | Selected factory firmware strings | Galileo repo | 2026-10-03 extraction | `hardware/esp32-s3-audio/diagnostics/factory_strings_selected.txt` | Xiaozhi/WakeNet/audio/OTA evidence |
| LOCAL | ESPHome build log | Local ignored build dir | 2026-10-03 build | `hardware/esp32-s3-audio/build-test/build.log` | Compile result and resource usage |
