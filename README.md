# Galileo ESP32-S3 Audio Satellite

Firmware ESPHome, audit hardware e pacchetto di lavoro per trasformare una board ESP32-S3 audio in un satellite vocale locale per Galileo/Jarvis e Home Assistant Assist.

Il progetto parte da una board commerciale **diymore ESP32-S3 AI Audio Board**, rilevata dal firmware factory come compatibile con **Waveshare ESP32-S3-AUDIO-Board**. L'obiettivo e' usare la board come nodo vocale: wake word locale, microfono I2S, speaker integrato, LED di stato e integrazione con Home Assistant.

## Stato Del Progetto

| Area | Stato | Note |
| --- | --- | --- |
| Audit hardware | Fatto | Identificazione chip, USB, flash, PSRAM, codec e partizioni |
| Backup factory | Fatto | Dump completo flash 16 MB salvato localmente e ignorato da Git |
| Build ESPHome | Pass | ESPHome 2026.9.1, profilo full AFE compilato correttamente |
| Flash/OTA | Pass | Device online come `galileo-va.local` |
| Wi-Fi/API ESPHome | Pass | IP osservato: `192.168.1.171`, API su porta `6053` |
| Home Assistant | Pass | Connessione API e integrazione Assist verificate |
| Wake word locale | Pass | `micro_wake_word` ESPHome v2 con `Alexa + Okay Nabu` attive al boot |
| Audio runtime | Pass | Speaker, microfoni e round trip Assist testati sulla board |
| Profilo audio operativo | Pass | Full AFE con dual mic, TDM, AEC, NS, SE e reference hardware |
| VoIP locale | Pass | Satellite Taverna, interno `101`, SIP `5060/udp`, RTP base `40000` |
| LED ring theme | OTA pass | Palette rosso/viola/blu con `Talk Glow Color` su wake/listening; validazione visiva da fare sul ring |
| Listen feedback sound | Pass | Switch per-device `Listen Feedback Sound`, LED solo oppure LED + bip locale |
| Golden firmware | Fatto | Recovery locale in `backups/golden-esp-voip-20261010/`, documentata in `docs/golden-firmware-recovery.md` |

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

La board usa ES7210 ed ES8311 su bus audio condiviso. Il firmware operativo usa
il profilo full AFE con TDM a 48 kHz:

```text
ES7210 TDM slot 0/2 -> ESP32-S3 -> AFE/AEC/NS/SE -> micro_wake_word
ES7210 TDM slot 1   -> playback reference -------> AEC

Home Assistant TTS/media/VoIP -> ESP32-S3 -> ES8311 -> NS4150 -> speaker
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

I microfoni sono configurati tramite ES7210 esterno, non PDM. L'AFE produce il
flusso voce usato da ESPHome `micro_wake_word`, Assist e VoIP TX.

## Firmware

Entrypoint ESPHome operativo:

```text
esphome/galileo-va-afe.yaml
```

Questo e' il profilo stabile attuale del satellite `Satellite Taverna`. Usa componenti esterni AFE/audio/VoIP per sfruttare la board come il firmware factory: TDM 48 kHz, due microfoni fisici, reference hardware per AEC, speaker ES8311, LED ring e tasti fisici.

Il vecchio profilo stock ESPHome resta nel repository come riferimento storico e fallback di confronto:

```text
esphome/galileo-va.yaml
```

Non e' il profilo operativo corrente.

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
La gestione dei modelli wake word caricati nel firmware operativo e' descritta in:

```text
docs/wake-word-models.md
```
Per un collega developer c'e' anche una guida rapida dedicata:

```text
handoff/micro_wake_word_request/DEVELOPER_QUICK_TRAINING_GUIDE.md
```

Per chi ha una board uguale e vuole provare il modello su hardware reale, il pacchetto include anche:

```text
handoff/micro_wake_word_request/FLASH_IDENTICAL_BOARD.md
handoff/micro_wake_word_request/example_full_flash_yaml/galileo-va-afe-identical-board.yaml
```

## Struttura Repository

```text
.
|-- README.md
|-- MANIFEST.md
|-- AUDIT_HARDWARE.md
|-- esphome/
|   |-- galileo-va-afe.yaml
|   |-- galileo-va.yaml
|   `-- secrets.example.yaml
|-- docs/
|   |-- README.md
|   |-- initial_board_audit.md
|   |-- compatibility_audit.md
|   |-- first_flash_checklist.md
|   |-- golden-firmware-recovery.md
|   |-- led-ring-theme.md
|   |-- listen-feedback-sound.md
|   |-- runtime-validation-20261008.md
|   |-- voip-centralino-esp32.md
|   |-- wake-word-models.md
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

- `docs/README.md` - indice della documentazione e distinzione tra documenti operativi e storici.
- `AUDIT_HARDWARE.md` - audit aggiornato di hardware, firmware attuale, gap e piano interventi.
- `esphome/galileo-va-afe.yaml` - firmware operativo attuale per `Satellite Taverna`.
- `esphome/galileo-va.yaml` - vecchio profilo stock, conservato come riferimento storico/fallback.
- `docs/initial_board_audit.md` - audit non distruttivo iniziale, factory firmware, partizioni e backup.
- `docs/compatibility_audit.md` - compatibilita' ESPHome/Home Assistant, pinout e stato test.
- `docs/first_flash_checklist.md` - checklist storica del primo flash stock.
- `docs/original_firmware_audio_adaptation.md` - confronto storico tra firmware factory Xiaozhi, stock ESPHome e passaggio AFE.
- `docs/runtime-validation-20261008.md` - validazione della baseline full AFE.
- `docs/voip-centralino-esp32.md` - guida operativa ESP32-S3 per VoIP, audio, tasti e deploy.
- `docs/wake-word-models.md` - stato corrente dei modelli wake word.
- `docs/golden-firmware-recovery.md` - procedura per ripristinare la cassa allo stato funzionante attuale.
- `docs/led-ring-theme.md` - tema LED ring, effetti custom e rollback.
- `docs/listen-feedback-sound.md` - spec del bip locale opzionale quando il satellite entra in ascolto.
- `docs/references.md` - fonti hardware/software usate durante l'audit.
- `handoff/micro_wake_word_request/REQUEST_TO_COLLEAGUE.md` - testo pronto per chiedere una wake word custom.
- `handoff/micro_wake_word_request/DEVELOPER_QUICK_TRAINING_GUIDE.md` - guida rapida per trainare una micro wake word compatibile.
- `handoff/micro_wake_word_request/FLASH_IDENTICAL_BOARD.md` - guida per compilare/flashare una board uguale.

## Dati Locali Non Versionati

Sono esclusi da Git:

- backup flash factory in `backups/`
- build ESPHome e log pesanti in `build-test/`
- cache `.esphome/`
- virtualenv Python
- `esphome/secrets.yaml`
- binari generati

Il backup factory resta deliberatamente locale: e' utile per recovery, ma non appartiene al repository pubblico.

## Lavoro Aperto

La board e' gia' stata portata online, il profilo full AFE e' la baseline operativa e il flusso vocale principale e' stato testato. I prossimi lavori vanno fatti a piccoli passi, senza cambiare audio stack, pin, buffer o VoIP insieme ad altre feature:

1. Testare sul campo lo switch `Listen Feedback Sound` con ON, OFF e `Speaker Mute`.
2. Testare sul campo il tema LED ring con `KITT Scan` e `Talk Glow`.
3. Tarare wake word e falsi positivi per la combinazione corrente `Alexa + Okay Nabu`.
4. Preparare il modello custom Galileo/Jarvis quando sara' disponibile in formato ESPHome microWakeWord v2.
5. Misurare barge-in, STT, volume speaker e clipping con test ripetibili.
6. Valutare solo in profilo separato AGC AFE, gain ES7210 e una futura variante no-VoIP.
7. Progettare la feature futura di feedback comando eseguito, distinta dal bip di ascolto.
