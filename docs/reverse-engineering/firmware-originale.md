# Firmware Originale

## Identita'

### Confermato

Dump analizzato:

```text
hardware/esp32-s3-audio/backups/esp32_s3_audio_factory_FULL.bin
```

Caratteristiche:

```text
size    16,777,216 bytes
sha256  d0b72eddaf4486a1bd25f4852f42d78dcd763c82e0bc0ffc3653991b317b75e8
```

Metadata app trovati nell'immagine `ota_0`:

```text
app_desc offset 0x100020
project        xiaozhi
version        1.8.9
compile date   Aug 30 2025
compile time   11:02:12
ESP-IDF        v5.4.1
```

Evidenze:

- Header app a `0x100000` con magic `0xe9`.
- `esp_app_desc` a `0x100020`, magic `0xabcd5432`.
- Documenti: `docs/initial_board_audit.md` e
  `hardware/esp32-s3-audio/docs/initial_board_audit.md`.

## Layout Flash

### Confermato

```text
0x000000  bootloader ESP image
0x008000  partition table
0x009000  nvs       data/nvs    size 0x004000
0x00d000  otadata   data/ota    size 0x002000
0x00f000  phy_init  data/phy    size 0x001000
0x010000  model     data/spiffs size 0x0f0000
0x100000  ota_0     app/ota_0   size 0x600000
0x700000  ota_1     app/ota_1   size 0x600000
```

Partition table raw:

```text
hardware/esp32-s3-audio/diagnostics/partition_table.bin
```

Partition table CSV:

```text
hardware/esp32-s3-audio/diagnostics/partition_table.csv
```

## Bootloader

### Confermato

Il bootloader e' una immagine ESP valida all'offset `0x000000`:

```text
magic          0xe9
segments       4
spi_mode       0x02
spi_size_freq  0x4f
entry          0x403c890c
hash_appended  1
approx end     0x402c
```

Segmenti osservati:

```text
load_addr 0x3fce2820 size 0x056c
load_addr 0x403c8700 size 0x0004
load_addr 0x403c8704 size 0x0c2c
load_addr 0x403cb700 size 0x2e58
```

### Sconosciuto

- Configurazione dettagliata del bootloader senza decompilazione.
- Eventuali opzioni di secure boot oltre ai dati di audit.

## OTA E App Attiva

### Confermato

`otadata` contiene una entry valida:

```text
0x00d000 ota_seq=1 ota_state=2 crc=0x4743989a
0x00d020 erased
```

Lo slot attivo e' quindi verosimilmente `ota_0`.

`ota_0` e' una immagine ESP valida:

```text
offset         0x100000
magic          0xe9
segments       6
entry          0x403796ac
hash_appended  1
approx end     0x398b10
```

Segmenti principali:

```text
file data off 0x100020 load 0x3c1a0020 size 0x0dec3c
file data off 0x1dec64 load 0x3fc9d600 size 0x0013b4
file data off 0x1e0020 load 0x42000020 size 0x19ad64
file data off 0x37ad8c load 0x3fc9e9b4 size 0x00877c
file data off 0x383510 load 0x40378000 size 0x0155dc
file data off 0x398af4 load 0x600fe100 size 0x00001c
```

`ota_1` a `0x700000` inizia con `0xff` e non e' stata riconosciuta come
immagine ESP.

## Partizione Model

### Confermato

La partizione `model` parte da `0x010000` e misura `0x0f0000`.

Stringhe osservate nella regione:

```text
0x010004  wn9_nihaoxiaozhi_tts
0x010028  wn9_data
0x010050  wn9_index
0x010078  _MODEL_INFO_
0x0570b6  wakenet9l_tts1h8_
```

### Probabile

- La partizione contiene modelli WakeNet e metadati per ESP-SR.
- Il nome `nihaoxiaozhi` indica una wake word cinese/Xiaozhi.

### Sconosciuto

- Struttura completa del filesystem o container.
- Dimensioni e checksum dei singoli modelli.
- Possibilita' pratica di riutilizzarli in ESPHome.

## Comunicazioni E Servizi

### Confermato

Stringhe osservate nell'app `ota_0`:

```text
https://api.tenclass.net/xiaozhi/ota/
MQTT
WebSocket
http://192.168.4.1
XIAOZHI_STATE_EVENTS
```

Il firmware originale integra:

- captive portal Wi-Fi;
- configurazione OTA;
- MQTT;
- WebSocket;
- HTTP server locale.

### Sconosciuto

- Endpoint MQTT/WebSocket effettivi dopo provisioning.
- Protocollo completo dei messaggi.
- Gestione crittografica dell'audio e dei comandi.
