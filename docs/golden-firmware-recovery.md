# Golden Firmware Recovery

> Il rollback normale tra release si fa con `tools/fleet rollback <cassa>`
> ([fleet.md](fleet.md)). Questa guida serve solo come ultima risorsa.
>
> Il golden e' lo stato Assist/AFE di Taverna del 10/10/2026, non il firmware
> di produzione: aveva `Alexa + Okay Nabu` attive e usava l'Assist di Home
> Assistant, mentre oggi le casse hanno solo `Okay Nabu` e la voce diretta
> verso Galileo Core.

Questa guida descrive il punto di ritorno locale per rimettere una cassa
ESP32-S3 nello stato salvato il 10/10/2026.

## Golden Attuale

Creato il 2026-10-10:

```text
backups/golden-esp-voip-20261010/
backups/golden-esp-voip-20261010.tar.gz
```

Il pacchetto contiene:

```text
galileo-va-golden.factory.bin
galileo-va-golden.ota.bin
galileo-va-app.bin
galileo-va-afe.yaml
README.md
SHA256SUMS
git-head.txt
git-status.txt
```

Il firmware e' stato compilato con:

```text
ghcr.io/esphome/esphome:2026.9.1
```

Stato salvato:

- device ESPHome `galileo-va`;
- IP atteso `192.168.1.171`;
- Home Assistant / VoIP Stack `192.168.1.186`;
- wake word attive al boot: `Alexa + Okay Nabu`;
- `Hey Jarvis` caricato ma disabilitato;
- VoIP ESPHome attivo verso Home Assistant.

## Perche' Non Va In Git

I binari generati possono contenere credenziali compilate nel firmware, per
esempio Wi-Fi, API o OTA. Per questo il pacchetto resta sotto `backups/`,
ignorato da Git.

Il repository tiene invece la procedura, il sorgente YAML e la documentazione.

## Verifica Integrita'

```bash
cd /home/denny/progerttidenny/galileovianicolini/speakersatellite/esp32-s3-audio-docs/backups/golden-esp-voip-20261010
sha256sum -c SHA256SUMS
```

## Recovery Via OTA

Usare questa strada se la cassa e' ancora online. I profili sono in
`esphome/archivio/`: si compila `galileo-va-afe-pinned-20261010.yaml`
(bloccato agli hash del golden; `galileo-va-afe.yaml` non si compila piu' con
ESPHome 2026.9.1). Prima serve il link a `secrets.yaml` descritto in
`esphome/archivio/README.md`.

```bash
cd /home/denny/progerttidenny/galileovianicolini/speakersatellite/esp32-s3-audio-docs
docker run --rm --network host --user 1000:1000 \
  -e HOME=/config -e UV_CACHE_DIR=/config/.cache/uv \
  -v "$PWD/esphome:/config" \
  ghcr.io/esphome/esphome:2026.9.1 \
  run /config/archivio/galileo-va-afe-pinned-20261010.yaml --device 192.168.1.171
```

In alternativa, senza ricompilare, si carica il binario del golden con
`--file`:

```bash
docker run --rm --network host --user 1000:1000 \
  -e HOME=/config -e UV_CACHE_DIR=/config/.cache/uv \
  -v "$PWD/esphome:/config" \
  -v "$PWD/backups/golden-esp-voip-20261010:/golden:ro" \
  ghcr.io/esphome/esphome:2026.9.1 \
  upload /config/archivio/galileo-va-afe-pinned-20261010.yaml \
  --device 192.168.1.171 --file /golden/galileo-va-golden.ota.bin
```

## Recovery Via USB

Usare questa strada se la cassa non e' raggiungibile via rete.

1. Collegare la cassa via USB.
2. Verificare la porta:

```bash
ls /dev/ttyACM* /dev/ttyUSB*
```

3. Flashare:

```bash
cd /home/denny/progerttidenny/galileovianicolini/speakersatellite/esp32-s3-audio-docs
docker run --rm --network host --user 1000:1000 \
  --device /dev/ttyACM0 \
  -e HOME=/config -e UV_CACHE_DIR=/config/.cache/uv \
  -v "$PWD/esphome:/config" \
  ghcr.io/esphome/esphome:2026.9.1 \
  run /config/archivio/galileo-va-afe-pinned-20261010.yaml --device /dev/ttyACM0
```

Oppure, come sopra, `upload ... --file` con il binario del golden
(`galileo-va-golden.factory.bin` per la flash completa via USB).

Se la porta non e' `/dev/ttyACM0`, sostituirla con quella vista dal comando
`ls`.

## Test Dopo Il Ripristino

1. Home Assistant vede `galileo-va` online.
2. L'IP della cassa e' `192.168.1.171`.
3. Il sensore VoIP torna `idle`.
4. Test wake/STT:

```text
Okay Nabu, che ore sono?
Alexa, che ore sono?
```

5. Test VoIP:

```text
Okay Nabu, chiama casa
Okay Nabu, chiudi la chiamata
```

## Dipendenze Fuori Dal Firmware

Il firmware ripristina la cassa, ma per avere il sistema completo servono anche:

- Raspberry/Home Assistant raggiungibile a `192.168.1.186`;
- pipeline Assist preferita `jarvis`;
- STT `stt.vosk`;
- TTS `tts.piper`;
- voce `it_IT-paola-medium`;
- VoIP Stack attivo;
- rubrica VoIP con `Satellite Taverna` interno `101`.
