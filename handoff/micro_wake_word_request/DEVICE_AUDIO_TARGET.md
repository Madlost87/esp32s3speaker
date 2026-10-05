# Device Audio Target

## Board

- Commerciale: diymore ESP32-S3 AI Audio Board.
- Compatibilita' rilevata: Waveshare ESP32-S3-AUDIO-Board / `waveshare-s3-audio-board`.
- MCU: ESP32-S3, dual core, 240 MHz.
- PSRAM: 8 MB octal.
- Flash: 16 MB.
- Framework firmware: ESPHome su ESP-IDF.

## Wake Runtime

- Componente: ESPHome `micro_wake_word`.
- Inferenza: on-device su ESP32-S3.
- Engine: TensorFlow Lite Micro tramite ESPHome.
- Formato modello: manifest JSON microWakeWord v2 + modello `.tflite`.
- Non usare formato openWakeWord server/Wyoming come consegna finale.

## Microphone Chain

- ADC microfonico: ES7210.
- Microfono in ESPHome: `platform: i2s_audio`.
- ADC type: external.
- PDM: false.
- Bits per sample: 16 bit.
- Sample rate osservato/configurato per ES7210: 16000 Hz.
- Gain default ES7210: 24 dB.
- Gain runtime: regolabile dal firmware a step di 3 dB.

## I2S / I2C Pins

- I2S MCLK: GPIO12.
- I2S BCLK/SCLK: GPIO13.
- I2S LRCLK/WS: GPIO14.
- I2S DIN, ES7210 verso ESP32: GPIO15.
- I2S DOUT, ESP32 verso ES8311: GPIO16.
- I2C SDA: GPIO11.
- I2C SCL: GPIO10.

## Audio Topology

Il firmware usa due bus I2S logici sugli stessi clock:

- `i2s_input`: bus microfono, master, sempre in capture per la wake word.
- `i2s_output`: bus speaker, slave, usa il clock del bus microfono.

ES7210 ed ES8311 sono slave rispetto al clock generato dal lato microfono.

## Current ESPHome Model Configuration

Il firmware attuale carica modelli ESPHome microWakeWord v2 simili a:

- `alexa`
- `okay_nabu`
- `hey_jarvis`
- `hey_mycroft`
- `vad`

Il nuovo modello deve essere equivalente come formato al manifest di esempio incluso in `example_model/`.

