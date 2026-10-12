# LED Ring Theme

## Obiettivo

Personalizzare il comportamento visivo del ring WS2812 della cassa senza
cambiare la logica del runtime controller.

La regola resta:

```text
stato logico -> colore + effetto + luminosita'
```

Gli stati non cambiano. Cambiano solo gli effetti assegnati ad alcuni stati e
il package LED diventa locale per rendere il rollback semplice.

## File Coinvolti

Firmware operativo:

```text
esphome/galileo-va-afe.yaml
```

Package LED locale:

```text
esphome/packages/status_ws2812_ring_galileo.yaml
```

Il package locale deriva dal package upstream `status_ws2812_ring.yaml`, ma
aggiunge gli effetti specifici Galileo. Non modificare la cache `.esphome/`.

## Effetti Aggiunti

### KITT Scan

Effetto scanner avanti/indietro ispirato alla barra luminosa KITT.

Caratteristiche:

- usa il colore dello stato, oggi rosso su `wake` e `listening`;
- scorre da un lato all'altro del ring e torna indietro;
- usa una piccola scia per rendere il movimento meno secco sui 7 LED;
- non cambia il significato dello stato, cambia solo la resa visiva.

### Talk Glow

Effetto pensato per quando il satellite sta rispondendo.

Caratteristiche:

- accende tutto il ring;
- usa il colore dello stato, oggi blu su `responding`;
- varia la luminosita' in modo non regolare, con piu' onde sovrapposte;
- non usa colori arcobaleno;
- serve a dare l'impressione che la cassa stia parlando, non solo pulsando.

## Mapping Attuale

Override locali rispetto al preset `ws2812_ring`:

| Stato | Colore | Effetto | Brightness |
| --- | --- | --- | --- |
| `wake` | red | `KITT Scan` | `0.75` |
| `listening` | red | `KITT Scan` | `0.75` |
| `responding` | blue | `Talk Glow` | `1.0` |

Tutti gli altri stati restano quelli del preset `ws2812_ring`.

## Rollback

Rollback minimo:

1. in `esphome/galileo-va-afe.yaml`, rimuovere gli override
   `runtime_controller.outputs.led.states`;
2. riportare il package LED a:

```yaml
status_led: github://n-IA-hane/esphome-intercom/packages/led/status_ws2812_ring.yaml@main
```

3. compilare;
4. fare OTA solo se la compilazione passa.

Rollback Git:

```bash
git revert <commit-led-theme>
```

poi compilare e caricare OTA.

## Test

1. `esphome config esphome/galileo-va-afe.yaml`.
2. `esphome compile esphome/galileo-va-afe.yaml`.
3. OTA solo se compila.
4. Test wake word:
   - `wake` / `listening`: scanner KITT rosso.
   - `responding`: ring blu con Talk Glow.
5. Verificare che VoIP, mute, timer e stati errore mantengano colori leggibili.

## Validazione 2026-10-12

- `esphome config`: PASS.
- `esphome compile`: PASS.
- OTA su `192.168.1.171`: PASS.
- Post-OTA: device online, ESPHome API raggiungibile, audio stack e VoIP
  inizializzati.
- Validazione visiva da completare guardando fisicamente il ring durante wake,
  listening e risposta TTS.
