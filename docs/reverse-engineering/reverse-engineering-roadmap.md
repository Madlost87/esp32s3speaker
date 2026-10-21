# Reverse Engineering Roadmap

## Priorita' 1: Consolidare Senza Rischio

### Estrarre Partizioni In Area Temporanea

Richiede autorizzazione per scrivere file, preferibilmente sotto `/tmp`.

Output previsto:

```text
/tmp/esp32-s3-original-fw/
  bootloader.bin
  partition_table.bin
  nvs.bin
  otadata.bin
  phy_init.bin
  model.bin
  ota_0.bin
  ota_1.bin
```

Scopi:

- calcolare SHA256 per ogni partizione;
- identificare formato della partizione `model`;
- preparare input per Ghidra solo su `ota_0.bin`.

### Catalogare Model Partition

Obiettivi:

- riconoscere struttura filesystem/container;
- elencare modelli WakeNet/VAD/NS;
- salvare offset, dimensioni, stringhe e metadati.

Dipendenze:

- eventualmente `binwalk`, `unblob` o tool ESP-SR, ma non installare senza
  autorizzazione.

## Priorita' 2: Abilitare Ghidra + REA

### Stato Attuale

REA MCP e' disponibile, ma Ghidra non e' operativo:

```text
GHIDRA_INSTALL_DIR not set
analyzeHeadless unavailable
Java 17 installed
JDK 21+ required by REA/Ghidra integration
```

### Procedura Proposta

Da eseguire solo previa autorizzazione:

1. Installare o indicare un Ghidra 12.1.x gia' estratto.
2. Installare/configurare JDK 21+.
3. Esportare `GHIDRA_INSTALL_DIR`.
4. Verificare `analyzeHeadless`.
5. Aprire `ota_0.bin` con REA/Ghidra.

### Obiettivi Ghidra

- Funzioni di init board.
- Costruttore/configurazione `BoxAudioCodec`.
- Inizializzazione I2C e TCA9555.
- Parametri I2S/TDM.
- Config AFE, WakeNet, VAD, NS, AGC, BSS.
- Gestione MQTT/WebSocket/OTA.
- Eventuali funzioni display/camera.

## Priorita' 3: Miglioramenti ESPHome Guidati Da Evidenze

### AGC

Domanda:

- il firmware ESPHome deve riattivare AGC leggero?

Piano:

- usare `galileo-va-afe-agc-lite.yaml`;
- misurare wake distante, falsi positivi, stutter TTS, barge-in;
- promuovere a baseline solo con evidenze runtime.

### Wake Word

Domanda:

- vale la pena recuperare WakeNet originale?

Piano:

- documentare modelli `model`;
- verificare fattibilita' ESP-SR in ESPHome custom;
- mantenere microWakeWord come baseline finche' e' piu' stabile/manutenibile.

### AFE Runtime

Domanda:

- i parametri AEC/NS/SE attuali sono vicini al firmware factory?

Piano:

- decompilare config AFE originale;
- confrontare con `esp_afe` attuale;
- variare un parametro alla volta.

## Priorita' 4: Funzioni A Bassa Priorita'

- Display/LVGL: solo se hardware presente e utile.
- Camera: bassa priorita' per satellite vocale.
- Captive portal: non necessario in architettura Home Assistant.
- MQTT/WebSocket Xiaozhi: utile come riferimento, non come target.
- microSD: da verificare con ispezione hardware e documentazione.

## Regole Per Le Fasi Successive

- Ogni estrazione o installazione richiede autorizzazione esplicita.
- Ogni modifica ESPHome deve nascere da una voce di confronto documentata.
- Ogni test runtime deve avere metrica osservabile e rollback chiaro.
- Non flashare firmware senza checklist e backup verificato.
