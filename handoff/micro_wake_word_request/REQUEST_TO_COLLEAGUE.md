# Richiesta Modello Wake Word Custom

Ciao, ti giro i dettagli del device target per trainare/esportare una wake word compatibile.

Mi serve un modello per **ESPHome micro_wake_word** che giri **on-device su ESP32-S3** con TensorFlow Lite Micro. Non mi serve un modello openWakeWord generico per server/Wyoming, perche' il firmware carica modelli microWakeWord in formato manifest JSON + `.tflite`.

## Wake Word

- Frase desiderata: `hey galileo` oppure concordiamo la frase finale prima del training.
- Lingua/pronuncia: italiano.
- Scenario: ambiente domestico, satellite vocale far-field, parlato normale a distanza stanza.

## Formato Di Consegna

Consegnami questi due file:

- `hey_galileo.json`
- `hey_galileo.tflite`

Il JSON deve essere un manifest ESPHome microWakeWord schema v2:

```json
{
  "type": "micro",
  "wake_word": "hey galileo",
  "author": "TUO_NOME",
  "model": "hey_galileo.tflite",
  "trained_languages": ["it"],
  "version": 2,
  "micro": {
    "probability_cutoff": 0.97,
    "sliding_window_size": 5,
    "feature_step_size": 10,
    "tensor_arena_size": 22860,
    "minimum_esphome_version": "2024.7.0"
  }
}
```

Puoi cambiare `probability_cutoff`, `sliding_window_size` e `tensor_arena_size` se il modello richiede valori diversi. Mi serve pero' che i valori reali consigliati siano nel JSON.

## Target Audio

- Device: ESP32-S3 audio board compatibile Waveshare ESP32-S3-AUDIO-Board / diymore ESP32-S3 AI Audio Board.
- Runtime: ESPHome `micro_wake_word`.
- MCU: ESP32-S3, 240 MHz, 8 MB PSRAM, 16 MB flash.
- Microphone ADC: ES7210.
- Input audio: I2S, ADC esterno, non PDM.
- Sample rate microfono/wake: 16 kHz.
- Bit depth: 16 bit.
- Canale usato dal firmware: stream microfono ESPHome `i2s_audio`.
- Gain ES7210 default firmware: 24 dB, regolabile a runtime a step di 3 dB.

## Note Di Compatibilita'

- Il modello deve essere abbastanza piccolo da girare su ESP32-S3 con TensorFlow Lite Micro.
- Deve essere compatibile con ESPHome microWakeWord v2.
- Se possibile, includi anche una soglia iniziale consigliata e note su falsi positivi/falsi negativi.
- Nel pacchetto trovi `example_model/hey_jarvis.json` e `example_model/hey_jarvis.tflite` come esempio di formato gia' accettato dal firmware.

