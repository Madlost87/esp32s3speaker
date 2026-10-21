# Reverse Engineering Firmware Originale ESP32-S3 Audio

Stato: fase preliminare documentata, senza decompilazione Ghidra.
Data ultimo aggiornamento: 2026-10-13.

Questa directory raccoglie l'analisi permanente del firmware originale della
cassa ESP32-S3 audio usata come satellite Galileo/Home Assistant.

## Obiettivi

- Conservare una mappa tecnica del firmware originale `xiaozhi`.
- Identificare componenti hardware e software riutilizzabili.
- Confrontare il firmware factory con il firmware ESPHome Galileo.
- Guidare miglioramenti futuri del profilo ESPHome senza perdere evidenze.

## Stato Sintetico

### Confermato

- Il backup originale completo e' presente localmente:
  `hardware/esp32-s3-audio/backups/esp32_s3_audio_factory_FULL.bin`.
- Il dump ha dimensione `16,777,216` byte, pari a 16 MB.
- SHA256 noto: `d0b72eddaf4486a1bd25f4852f42d78dcd763c82e0bc0ffc3653991b317b75e8`.
- Il firmware originale e' `xiaozhi` versione `1.8.9`, compilato il
  `Aug 30 2025 11:02:12`, con ESP-IDF `v5.4.1`.
- L'app attiva si trova nello slot `ota_0` a offset `0x100000`.
- Lo slot `ota_1` a offset `0x700000` appare vuoto nel dump esaminato.
- Secure Boot e Flash Encryption risultano disabilitati nei documenti di audit.

### Probabile

- La board e' compatibile con Waveshare ESP32-S3-AUDIO-Board, ma potrebbe essere
  un rebrand/clone diymore.
- Il firmware originale usa ESP-SR/AFE con WakeNet, VAD, AEC, WebRTC noise
  suppression, AGC digitale e speech enhancement/BSS.
- La partizione `model` contiene modelli WakeNet/Xiaozhi usati dal firmware.

### Sconosciuto

- La configurazione esatta dei GPIO nel codice macchina, senza decompilazione.
- Il mapping completo delle funzioni C/C++ originali.
- Il contenuto strutturato completo della partizione `model`, non ancora estratta.
- La configurazione runtime completa di AFE e WakeNet.

## File In Questa Directory

- `firmware-originale.md`: layout flash, partizioni, immagini ESP-IDF, metadata.
- `hardware-map.md`: GPIO, bus, periferiche, confidenza ed evidenze.
- `audio-analysis.md`: codec, I2S/TDM, AFE, AEC, NS, AGC, BSS.
- `wake-word-analysis.md`: WakeNet, VAD, modelli e limiti.
- `esphome-comparison.md`: confronto con `galileo-va-afe.yaml`.
- `missing-features.md`: funzionalita' originali non sfruttate o parziali.
- `reverse-engineering-roadmap.md`: passi successivi e priorita'.

## Strumenti Verificati

### Disponibili

- REA MCP, ma senza provider Ghidra operativo.
- `strings`, `xxd`, `readelf`, `objdump`.
- Toolchain Xtensa ESP locale:
  `.esphome/idf/tools/xtensa-esp-elf/.../xtensa-esp32s3-elf-objdump`.

### Non Disponibili O Non Configurati

- Ghidra non configurato: `GHIDRA_INSTALL_DIR` assente.
- `analyzeHeadless` non trovato.
- Java disponibile: 17, ma REA richiede JDK 21+ per Ghidra.
- `binwalk` e `unblob` non trovati.
- `esptool.py` di sistema presente ma non funzionante per dipendenza Python
  mancante (`esp_pylib`).

## Regole Di Lavoro

- Non modificare il firmware originale.
- Non flashare la scheda durante l'analisi.
- Estrarre partizioni solo in directory temporanee o dedicate, previa
  autorizzazione.
- Segnare sempre ogni conclusione come confermata, probabile o sconosciuta.
- Conservare offset, path e comandi usati come evidenza.
