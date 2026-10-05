# GALILEO ESP32-S3 AUDIO BOARD - INITIAL AUDIT

Data: 2026-10-03

Board collegata via USB e verificata senza flash, erase o modifiche alla memoria. Le prove eseguite sono state di identificazione USB, interrogazione read-only con esptool, boot log seriale, lettura della partition table e tentativo di backup completo della flash.

## BOARD

- Board attesa: Waveshare ESP32-S3-AUDIO-Board / diymore ESP32-S3 AI Audio Board
- Board rilevata dal firmware: `waveshare-s3-audio-board`
- Board UUID: `05e6feea-9313-41ed-9d1b-ba7362c19070`

## USB

- Porta seriale: `/dev/ttyACM0`
- USB: `303a:1001 Espressif USB JTAG/serial debug unit`
- VID: `303a`
- PID: `1001`
- Manufacturer: `Espressif`
- Product: `USB JTAG/serial debug unit`
- Serial USB: `28:84:85:B2:B8:18`
- Driver seriale: `cdc_acm`
- Interfacce USB:
  - interface 0: Communications, driver `cdc_acm`
  - interface 1: CDC Data, driver `cdc_acm`
  - interface 2: Vendor Specific Class, nessun driver kernel associato

## SERIAL PORT

- `/dev/ttyACM0`
- Non e' stata assunta `/dev/ttyUSB0`: la porta e' stata identificata dai log USB e da `udevadm`.

## CHIP

- Chip: ESP32-S3, package QFN56, revision v0.2
- Feature: Wi-Fi, BT 5 LE, dual core + LP core, 240 MHz
- USB mode: USB-Serial/JTAG

## CHIP REVISION

- v0.2

## FLASH

- Size rilevata: 16 MB
- Manufacturer: `0x20`
- Device: `0x4018`
- Flash type da eFuse: quad, 4 data lines
- Flash voltage da eFuse: 3.3 V

## PSRAM

- 8 MB embedded PSRAM
- Boot log: `Found 8MB PSRAM device`

## CRYSTAL

- 40 MHz

## MAC

- MAC: `28:84:85:b2:b8:18`

## ESP-IDF

- `v5.4.1`

## FACTORY FIRMWARE

Il firmware avviato non sembra un firmware minimale di fabbrica, ma un firmware applicativo gia' completo:

- Project name: `xiaozhi`
- App version: `1.8.9`
- Compile time: `Aug 30 2025 11:02:12`
- ESP-IDF: `v5.4.1`
- Board UUID: `05e6feea-9313-41ed-9d1b-ba7362c19070`
- Board SKU: `waveshare-s3-audio-board`

All'avvio crea un access point:

- SSID: `Xiaozhi-B819`
- IP captive/config: `192.168.4.1`

Messaggio boot log:

```text
手机连接热点 Xiaozhi-B819，浏览器访问 http://192.168.4.1
```

Interpretazione: il firmware e' probabilmente una demo/assistant firmware Xiaozhi per la Waveshare S3 Audio Board. Non e' ancora firmware Galileo.

## SECURE BOOT

- Disabled

## FLASH ENCRYPTION

- Disabled

## PARTITIONS

La partition table letta da flash:

```csv
name,type,subtype,offset,size,flags
nvs,data,nvs,0x009000,0x004000,0x00000000
otadata,data,ota,0x00d000,0x002000,0x00000000
phy_init,data,phy,0x00f000,0x001000,0x00000000
model,data,spiffs,0x010000,0x0f0000,0x00000000
ota_0,app,ota_0,0x100000,0x600000,0x00000000
ota_1,app,ota_1,0x700000,0x600000,0x00000000
```

Note:

- Non c'e' una partizione `factory`.
- Sono presenti due slot OTA da 6 MB.
- La partizione `model` e' SPIFFS da 960 KB: potrebbe contenere asset o modelli del firmware attuale.

## FACTORY BOOT

All'avvio il firmware:

- inizializza display/LVGL
- tenta inizializzazione camera, che fallisce
- inizializza codec audio ES7210/ES8311
- abilita input audio e output audio
- avvia Wi-Fi STA + softAP
- avvia DNS e web server per configurazione

Boot log salvato in `diagnostics/esp32_factory_boot.log`.

## AUDIO

Il boot log conferma l'inizializzazione della catena audio:

- `BoxAudioCodec: Duplex channels created`
- `ES8311: Work in Slave mode`
- `ES7210: Work in Slave mode`
- `ES7210_INPUT_MIC1` abilitato
- `ES7210_INPUT_MIC2` abilitato
- `ES7210_INPUT_MIC3` abilitato
- `ES7210_INPUT_MIC4` abilitato
- `ES7210: Enable TDM mode`
- `ES7210: Unmuted`
- `Adev_Codec: Open codec device OK`
- `AudioCodec: Set input enable to true`
- `AudioCodec: Set output enable to true`
- `Audio codec started`

Questo dice che codec e bus audio partono. Non dimostra ancora che i microfoni acquisiscano correttamente o che la cassa riproduca correttamente: serve un test audio dedicato.

## ES7210

- Stato: DETECTED BUT UNTESTED
- Evidenza: inizializzato in slave mode, TDM mode abilitato, MIC1-MIC4 abilitati, codec unmuted.

## ES8311

- Stato: DETECTED BUT UNTESTED
- Evidenza: inizializzato in slave mode, output enable true, audio codec started.

## MIC LEFT

- Stato: UNTESTED
- Il firmware abilita piu' ingressi microfonici, ma non abbiamo ancora una prova che mappi fisicamente left/right.

## MIC RIGHT

- Stato: UNTESTED
- Il firmware abilita piu' ingressi microfonici, ma non abbiamo ancora una prova che mappi fisicamente left/right.

## SPEAKER

- Stato: UNTESTED
- L'output audio risulta inizializzato, ma non e' stato eseguito un test speaker dal firmware factory.

## OTHER

- RGB: UNKNOWN
- microSD: UNKNOWN
- Wi-Fi: DETECTED BUT UNTESTED, softAP `Xiaozhi-B819`
- Bluetooth: DETECTED BUT UNTESTED come feature del chip, non osservato nel boot log applicativo

## FACTORY FLASH BACKUP

- Path previsto: `hardware/esp32-s3-audio/backups/esp32_s3_audio_factory_FULL.bin`
- Size attesa: 16 MB
- Size ottenuta: 16,777,216 bytes
- SHA256: `d0b72eddaf4486a1bd25f4852f42d78dcd763c82e0bc0ffc3653991b317b75e8`
- Stato: PASS

Dettaglio: la lettura con stub si e' fermata intorno a `0x205000` con errore di trasferimento pacchetto. La lettura completa e' poi riuscita con `--no-stub` in 16 chunk da 1 MB, concatenati nel dump full.

## PROBLEMS

1. Backup full flash richiede `--no-stub` a chunk.

   La lettura con stub si e' fermata intorno a `0x205000` con errore di trasferimento pacchetto. Il backup completo e' riuscito con lettura `--no-stub` a chunk, quindi il problema sembra legato al metodo/trasferimento lungo, non necessariamente a flash danneggiata.

2. Camera non supportata o non presente.

   Il firmware tenta di inizializzare una camera e fallisce:

   ```text
   camera: Detected camera not supported.
   camera: Camera probe failed with error 0x106(ESP_ERR_NOT_SUPPORTED)
   Esp32Camera: Camera init failed with error 0x106
   ```

   Se la board non monta una camera, questo e' probabilmente atteso e non blocca il progetto Galileo.

3. Warning I2C pull-up.

   ```text
   i2c.master: Please check pull-up resistances whether be connected properly.
   ```

   Va tenuto d'occhio se in futuro compaiono problemi su codec, display, touch, sensori o periferiche I2C.

## IMPLICAZIONI PER GALILEO

La board e' adatta a diventare un satellite vocale: ESP32-S3, PSRAM 8 MB, codec ES7210/ES8311 e Wi-Fi sono presenti e inizializzati dal firmware attuale.

Per Galileo, la direzione piu' concreta non e' partire dal firmware presente come sorgente, perche' abbiamo solo il binario e non il progetto. Conviene:

1. Conservare il piu' possibile lo stato originale prima di flashare.
2. Conservare il backup flash originale e il relativo SHA256 fuori da git.
3. Preparare un firmware nostro minimo che validi in ordine:
   - LED RGB
   - speaker
   - microfoni ES7210
   - streaming audio locale
   - wake word o inoltro audio al Raspberry
4. Usare il firmware Xiaozhi solo come riferimento diagnostico: dimostra che pin, codec e periferiche principali sono plausibilmente corretti.

## FILE PRODOTTI

- Boot log: `diagnostics/esp32_factory_boot.log`
- Partition table CSV: `hardware/esp32-s3-audio/diagnostics/partition_table.csv`
- Partition table raw: `hardware/esp32-s3-audio/diagnostics/partition_table.bin` ignorato da git
- Directory backup: `hardware/esp32-s3-audio/backups/` ignorata da git

## BOARD STATUS

| Check | Stato |
| --- | --- |
| USB communication | PASS |
| ESP32-S3 detected | PASS |
| Flash readable | PASS |
| Factory backup | PASS |
| Factory firmware | IDENTIFIED |
| PSRAM | PASS |
| ES7210 | DETECTED BUT UNTESTED |
| ES8311 | DETECTED BUT UNTESTED |
| Microphones | UNTESTED |
| Speaker | UNTESTED |

## RECOMMENDED NEXT STEP

Preparare un thin config ESPHome Galileo dal progetto compatibile selezionato, senza ancora flashare finche' non viene confermato il piano di primo avvio/test.
