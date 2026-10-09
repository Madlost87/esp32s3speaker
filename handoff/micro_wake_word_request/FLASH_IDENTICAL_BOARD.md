# Flash Su Board Uguale

Questa nota serve al collega che ha una board uguale e vuole provare una wake word custom sullo stesso tipo di cassa.

## File YAML Incluso

Template completo:

```text
example_full_flash_yaml/galileo-va-afe-identical-board.yaml
```

Il file e' una copia del profilo attualmente funzionante sul satellite ESP32-S3, con:

- ESPHome;
- ESP32-S3;
- ES7210 microfoni;
- ES8311 speaker;
- AFE;
- `micro_wake_word`;
- Voice Assistant;
- VoIP stack;
- LED e tasti fisici.

## Prima Di Flashare

Per usare il template con ESPHome, copiarlo nella cartella `esphome/` del progetto di test:

```bash
cp handoff/micro_wake_word_request/example_full_flash_yaml/galileo-va-afe-identical-board.yaml \
  esphome/galileo-va-afe-identical-board.yaml
```

Cambiare almeno questi campi nel blocco `substitutions`:

```yaml
substitutions:
  name: galileo-va-test
  friendly_name: Satellite Test
  voip_extension: "199"
```

Regole:

- `name` deve essere unico nella rete e in Home Assistant;
- `friendly_name` e' il nome visibile in Home Assistant;
- `voip_extension` deve essere libero nel centralino/phonebook;
- non usare lo stesso `name` della cassa gia' in produzione, altrimenti Home Assistant puo' confondere i device.

## Secrets

Creare nella stessa cartella ESPHome un file `secrets.yaml` locale, non versionato:

```yaml
wifi_ssid: "SSID_WIFI"
wifi_password: "PASSWORD_WIFI"
```

Se il template locale richiede anche API key, OTA password o fallback AP, tenerli sempre in `secrets.yaml`, non nel file YAML consegnato.

## Inserire La Wake Word Custom

Quando sono pronti:

```text
aiuto_aiuto.json
aiuto_aiuto.tflite
```

metterli in una cartella accessibile a ESPHome, per esempio:

```text
models/aiuto_aiuto.json
models/aiuto_aiuto.tflite
```

Poi nel blocco `micro_wake_word` aggiungere il modello:

```yaml
micro_wake_word:
  id: mww
  microphone: mic_main
  task_stack_in_psram: true
  models:
    - model: https://github.com/esphome/micro-wake-word-models/raw/main/models/v2/okay_nabu.json
      id: okay_nabu
    - model: https://github.com/esphome/micro-wake-word-models/raw/main/models/v2/hey_jarvis.json
      id: hey_jarvis
    - model: models/aiuto_aiuto.json
      id: aiuto_aiuto
```

Per un primo test si puo' anche sostituire temporaneamente `hey_jarvis` invece di aggiungere un terzo modello, cosi' si riduce il carico runtime.

## Compilazione Prima Del Flash

Prima prova: solo compilazione.

```bash
docker run --rm --network host --user 1000:1000 \
  -e HOME=/config -e UV_CACHE_DIR=/config/.cache/uv \
  -v "$PWD/esphome:/config" \
  ghcr.io/esphome/esphome:2026.9.1 \
  compile /config/galileo-va-afe-identical-board.yaml
```

Se compila, solo allora fare flash USB:

```bash
docker run --rm --network host --user 1000:1000 \
  -e HOME=/config -e UV_CACHE_DIR=/config/.cache/uv \
  -v "$PWD/esphome:/config" \
  --device /dev/ttyACM0 \
  ghcr.io/esphome/esphome:2026.9.1 \
  run /config/galileo-va-afe-identical-board.yaml --device /dev/ttyACM0
```

Adattare `/dev/ttyACM0` se la board appare su una porta diversa.

## Test Minimo Dopo Flash

Verificare in ordine:

1. boot senza errori;
2. Wi-Fi online;
3. API Home Assistant connessa;
4. speaker funzionante;
5. microfono funzionante;
6. wake word ufficiale ancora funzionante;
7. wake word custom;
8. falsi positivi con TV/parlato normale;
9. comportamento VoIP solo se il centralino e' configurato.

## Nota Importante

Questo YAML e' un profilo completo per board uguale. Non e' un modello minimale di training.

Per consegnare la wake word a Denny bastano comunque:

```text
aiuto_aiuto.json
aiuto_aiuto.tflite
README_TEST.md
```

Il firmware definitivo verra' aggiornato e flashato separatamente dopo verifica.
