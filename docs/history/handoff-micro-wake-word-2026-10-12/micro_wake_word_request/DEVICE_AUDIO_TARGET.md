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
- Microfono in ESPHome: `mic_main`, uscita processata dal profilo full AFE.
- ADC type: external ES7210 via TDM.
- PDM: false.
- Bits per sample: 16 bit.
- Sample rate codec/TDM: 48000 Hz.
- Sample rate consumato da wake/Assist dopo AFE: 16000 Hz.
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

Il firmware operativo usa il profilo full AFE:

- ES7210/ES8311 su TDM 48 kHz;
- slot `0` e `2`: microfoni fisici;
- slot `1`: playback reference per AEC;
- slot `3`: inutilizzato/quasi silente su questa board;
- AFE con AEC, noise suppression, speech enhancement e VAD;
- output processato a 16 kHz verso `micro_wake_word` e Assist.

Il vecchio profilo stock a due bus I2S resta solo come riferimento storico.

## Current ESPHome Model Configuration

Il firmware attuale carica questi modelli ESPHome microWakeWord v2:

- `alexa`
- `okay_nabu`
- `hey_jarvis`
- `vad`

Al boot sono abilitati `alexa` e `okay_nabu`; `hey_jarvis` e' caricato ma
disabilitato.

Il nuovo modello deve essere equivalente come formato al manifest di esempio incluso in `example_model/`.
