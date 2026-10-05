# Galileo ESP32-S3 Audio Satellite

Firmware ESPHome, audit hardware e pacchetto di lavoro per trasformare una board ESP32-S3 audio in un satellite vocale locale per Galileo/Jarvis e Home Assistant Assist.

Il progetto parte da una board commerciale **diymore ESP32-S3 AI Audio Board**, rilevata dal firmware factory come compatibile con **Waveshare ESP32-S3-AUDIO-Board**. L'obiettivo e' usare la board come nodo vocale: wake word locale, microfono I2S, speaker integrato, LED di stato e integrazione con Home Assistant.

## Stato Del Progetto

| Area | Stato | Note |
| --- | --- | --- |
| Audit hardware | Fatto | Identificazione chip, USB, flash, PSRAM, codec e partizioni |
| Backup factory | Fatto | Dump completo flash 16 MB salvato localmente e ignorato da Git |
| Build ESPHome | Pass | ESPHome 2026.9.1, firmware compilato correttamente |
| Primo flash | Pass | Device online come `galileo-va.local` |
| Wi-Fi/API ESPHome | Pass | IP osservato: `192.168.1.171`, API su porta `6053` |
| Home Assistant | Pass iniziale | Connessione API osservata da Home Assistant |
| Wake word locale | Build pass | `micro_wake_word` con modelli ESPHome v2 |
| Audio runtime | Da completare | Speaker, microfoni e round trip Assist da collaudare bene |

## Hardware Rilevato

- MCU: ESP32-S3, dual core, 240 MHz.
- Flash: 16 MB.
- PSRAM: 8 MB.
- USB: Espressif USB Serial/JTAG, `/dev/ttyACM0`.
- Audio ADC: ES7210 per microfoni.
- Audio DAC: ES8311 per speaker.
- LED: ring WS2812 a 7 LED.
- Expander: TCA9555 per amplificatore e tasti.
- Secure Boot: disabilitato.
- Flash Encryption: disabilitata.

Il firmware originale rilevato era `xiaozhi` v1.8.9, con board SKU `waveshare-s3-audio-board`. Prima di flashare ESPHome e' stato eseguito un backup completo della flash factory.

## Architettura Audio

La board usa ES7210 ed ES8311 su bus I2S condiviso. Il firmware ESPHome scelto usa due bus I2S logici sugli stessi clock:

```text
ES7210 microphones -> I2S input bus -> ESP32-S3 -> micro_wake_word
                                      -> Home Assistant Assist

Home Assistant TTS/media -> ESP32-S3 -> I2S output bus -> ES8311 -> speaker
```

Pin principali:

| Segnale | GPIO | Funzione |
| --- | --- | --- |
| I2S MCLK | GPIO12 | Clock master |
| I2S BCLK/SCLK | GPIO13 | Bit clock |
| I2S LRCLK/WS | GPIO14 | Word select |
| I2S DIN | GPIO15 | ES7210 verso ESP32 |
| I2S DOUT | GPIO16 | ESP32 verso ES8311 |
| I2C SDA | GPIO11 | Controllo codec/expander |
| I2C SCL | GPIO10 | Controllo codec/expander |
| LED data | GPIO38 | Ring WS2812 |

Il microfono e' configurato come I2S esterno, non PDM, a 16 bit. La wake word gira sul device con ESPHome `micro_wake_word` e TensorFlow Lite Micro.

## Firmware

Entrypoint ESPHome:

```text
esphome/galileo-va.yaml
```

La configurazione locale resta volutamente sottile: importa il package upstream testato e pinato a `v1.1.1`:

```yaml
packages:
  core:
    url: https://github.com/MichalZaniewicz/esphome-waveshare-esp32-s3-audio-va
    ref: v1.1.1
    files:
      - base/core.yaml
```

Le credenziali Wi-Fi/API non sono versionate. Il template e':

```text
esphome/secrets.example.yaml
```

## Wake Word Custom

Il firmware usa modelli **ESPHome microWakeWord**, non modelli openWakeWord generici per server. Il formato richiesto e':

```text
nome_wake_word.json
nome_wake_word.tflite
```

Nel repository e' incluso un pacchetto da inviare a chi deve trainare una wake word custom:

```text
handoff/micro_wake_word_request/
handoff/micro_wake_word_request.tar.gz
```

Contiene una richiesta tecnica pronta, i dettagli del target audio e un esempio reale `hey_jarvis` in formato JSON + TFLite.

## Struttura Repository

```text
.
|-- esphome/
|   |-- galileo-va.yaml
|   `-- secrets.example.yaml
|-- docs/
|   |-- initial_board_audit.md
|   |-- compatibility_audit.md
|   |-- first_flash_checklist.md
|   `-- references.md
|-- diagnostics/
|   |-- chip_info.txt
|   |-- security_info.txt
|   |-- partition_table.csv
|   `-- usb_identification.txt
`-- handoff/
    `-- micro_wake_word_request/
```

## File Importanti

- `docs/initial_board_audit.md` - audit non distruttivo iniziale, factory firmware, partizioni e backup.
- `docs/compatibility_audit.md` - compatibilita' ESPHome/Home Assistant, pinout e stato test.
- `docs/first_flash_checklist.md` - checklist flash e ordine dei test runtime.
- `docs/references.md` - fonti hardware/software usate durante l'audit.
- `handoff/micro_wake_word_request/REQUEST_TO_COLLEAGUE.md` - testo pronto per chiedere una wake word custom.

## Dati Locali Non Versionati

Sono esclusi da Git:

- backup flash factory in `backups/`
- build ESPHome e log pesanti in `build-test/`
- cache `.esphome/`
- virtualenv Python
- `esphome/secrets.yaml`
- binari generati

Il backup factory resta deliberatamente locale: e' utile per recovery, ma non appartiene al repository pubblico.

## Prossimi Passi

1. Collaudare speaker a volume conservativo.
2. Verificare acquisizione microfoni e mapping fisico left/right.
3. Testare wake word locale con `hey_jarvis`.
4. Integrare una wake word custom microWakeWord per Galileo.
5. Validare round trip completo: wake word, STT italiano, intent/LLM, TTS su speaker.
