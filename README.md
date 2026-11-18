# Galileo ESP32-S3 Audio Satellite

Repository firmware (ESPHome) e gestione flotta delle casse Galileo.

Il progetto parte da una board commerciale **diymore ESP32-S3 AI Audio Board**, rilevata dal firmware factory come compatibile con **Waveshare ESP32-S3-AUDIO-Board**. La board fa da cassa vocale: wake word locale, microfoni, speaker, LED di stato, tasti e interno VoIP.

## Stato attuale

Tre casse in produzione, tutte sulla release `2026.11.8` dal 18/11/2026
(tag da `fw-2026.11.1` a `fw-2026.11.8`):

| Cassa | IP | Interno | Configurazione |
| --- | --- | --- | --- |
| Satellite Taverna | `192.168.1.171` | `101` | `esphome/galileo-va-direct-audio-cutover.yaml` |
| Satellite Sala | `192.168.1.172` | `102` | `esphome/galileo-sala.yaml` |
| Satellite Garage | `192.168.1.133` | `103` | `esphome/galileo-garage.yaml` |

- Wake word: solo `Okay Nabu` (dalla 2026.11.7). `Alexa` e `Hey Jarvis` restano nel firmware ma spente.
- Wake word riconosciuta: bip fisso di 120 ms, sempre attivo (non c'e' uno switch).
- LED: pacchetto upstream `status_ws2812_ring.yaml`. Il tema custom KITT/Talk Glow esiste solo nei file archiviati.
- Voce: audio diretto verso Galileo Core (`192.168.1.186`). L'Assist di Home Assistant non si collega in questo profilo.
- VoIP: ogni cassa e' un peer SIP diretto, senza registrazione, del VoIP Stack dentro Home Assistant (`192.168.1.186`).
- Mute: il mute della card media player e' lo switch `Speaker Mute` (dalla 2026.11.8). `Mic Mute` e' separato.

Dettagli per cassa e build installate: [docs/satellites.md](docs/satellites.md).
Release, rollout e rollback: [docs/fleet.md](docs/fleet.md).

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

La board usa ES7210 ed ES8311 su bus audio condiviso. Il firmware usa il
profilo full AFE con TDM a 48 kHz:

```text
ES7210 TDM slot 0/2 -> ESP32-S3 -> AFE/AEC/NS/SE -> micro_wake_word, voce diretta, VoIP TX
ES7210 TDM slot 1   -> playback reference -------> AEC

TTS da Galileo Core (HTTP), media e VoIP da Home Assistant -> ESP32-S3 -> ES8311 -> NS4150 -> speaker
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
flusso usato da `micro_wake_word`, dalla voce diretta verso Galileo Core e dal
VoIP TX.

## Firmware

Le tre casse usano la stessa base `esphome/galileo-va-direct-audio-cutover-base.yaml`,
divisa per funzione in `esphome/packages/satellite/`.

La configurazione ha tre livelli: firmware (la base comune), sito
(`esphome/sites/casa.yaml`: rete, Galileo Core, Wi-Fi, gruppi VoIP) e
dispositivo (solo identita'). Un fix si fa una volta nella base e si distribuisce
a tutte le casse con `tools/fleet` (release numerata, canarino, controllo dopo
ogni OTA, rollback). Una cassa nuova si aggiunge con `tools/fleet new`. Guida:
[docs/fleet.md](docs/fleet.md).

La base usa componenti esterni AFE/audio/VoIP per sfruttare la board come il firmware factory: TDM 48 kHz, due microfoni fisici, reference hardware per AEC, speaker ES8311, LED ring e tasti fisici.

I profili di laboratorio, il vecchio profilo stock e il golden di recovery sono in `esphome/archivio/` (vedi il suo README e [docs/golden-firmware-recovery.md](docs/golden-firmware-recovery.md)): non sono profili in produzione.

Le credenziali Wi-Fi/API non sono versionate. Il template e' `esphome/secrets.example.yaml`.

## Contenuto del repository

Cosa contiene ogni cartella, dove finisce, fonti di verita', cosa resta fuori
da Git e come si collega al repository `homeassistant`: [MANIFEST.md](MANIFEST.md).

## Wake Word Custom

Il firmware usa modelli **ESPHome microWakeWord**, non modelli openWakeWord generici per server. Il formato richiesto e':

```text
nome_wake_word.json
nome_wake_word.tflite
```

La gestione dei modelli caricati nel firmware e' in
[docs/wake-word-models.md](docs/wake-word-models.md).

Il pacchetto preparato il 12/10/2026 per chiedere una wake word custom (richiesta,
target audio, esempio `hey_jarvis`, guida di training, flash di una board uguale)
e' archiviato in `docs/history/handoff-micro-wake-word-2026-10-12/`. E' uno
snapshot di quella data: va rivisto prima di riusarlo.

## Documentazione

Indice dei documenti attuali e storici: [docs/README.md](docs/README.md).
Lavoro aperto e ordine dei lavori: [docs/specs-index.md](docs/specs-index.md).

## Dati Locali Non Versionati

Segreti, binari compilati, backup della flash di fabbrica e cache di
compilazione restano fuori da Git: l'elenco e dove stanno e' in
[MANIFEST.md](MANIFEST.md#cosa-non-ce-e-dove-sta).
