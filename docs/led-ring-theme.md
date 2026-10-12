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

- usa il colore dello stato quando viene assegnato a uno stato visibile;
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

### Talk Glow Color

Variante colorata di `Talk Glow`, pensata per la fase `listening`.

Caratteristiche:

- accende tutto il ring;
- varia la luminosita' in modo non regolare;
- non usa il colore dello stato come tinta unica;
- attraversa una palette rosso -> viola -> blu;
- viene assegnata a `listening`, cioe' quando il satellite e' davvero pronto ad
  acquisire la frase.

`KITT Scan` resta disponibile come effetto nel package, ma non e' assegnato al
tema corrente.

Lo stato `wake` resta spento: se la wake word viene rilevata ma la pipeline non
entra in `listening`, la cassa non deve sembrare pronta ad ascoltare.

## Mapping Attuale

Palette sostitutiva locale rispetto al preset `ws2812_ring`:

| Stato | Colore | Effetto | Brightness |
| --- | --- | --- | --- |
| `idle` | off | `None` | `0.0` |
| `muted` | `[1.0, 0.0, 0.0]` | `Slow Pulse` | `0.45` |
| `mic_muted` | `[1.0, 0.0, 0.08]` | `None` | `0.35` |
| `speaker_muted` | `[0.9, 0.0, 0.45]` | `None` | `0.35` |
| `wake` | off | `None` | `0.0` |
| `listening` | rosso -> viola -> blu | `Talk Glow Color` | `0.9` |
| `thinking` | `[0.55, 0.15, 1.0]` | `Spin` | `0.75` |
| `responding` | `[0.0, 0.25, 1.0]` | `Talk Glow` | `1.0` |
| `voip_ringing` | `[1.0, 0.0, 0.0]` | `Ringing` | `1.0` |
| `voip_calling` | `[0.85, 0.0, 0.7]` | `Calling` | `1.0` |
| `voip_remote_ringing` | `[0.85, 0.0, 0.7]` | `Ringing` | `1.0` |
| `voip_in_call` | `[0.15, 0.0, 0.9]` | `None` | `1.0` |
| `error` | `[1.0, 0.0, 0.0]` | `None` | `0.75` |
| `media` | `[0.2, 0.0, 1.0]` | `Spin` | `1.0` |
| `boot` | `[0.75, 0.0, 0.35]` | `None` | `0.65` |
| `no_wifi` | `[0.95, 0.0, 0.35]` | `Blink` | `0.75` |
| `no_ha` | `[0.1, 0.15, 1.0]` | `Blink` | `0.65` |
| `no_va` | `[0.55, 0.15, 1.0]` | `Blink` | `0.65` |
| `timer_ringing` | `[0.9, 0.0, 0.75]` | `Fast Pulse` | `1.0` |

La palette evita verde, giallo e arancione nel tema principale. Le differenze di
stato sono affidate a posizione nella scala rosso/viola/blu, animazione e
brightness.

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
   - wake senza `listening`: nessun LED ascolto e nessun bip;
   - `listening`: `Talk Glow Color` rosso/viola/blu ed eventuale bip;
   - `responding`: ring blu con Talk Glow.
5. Verificare che VoIP, mute, timer e stati errore mantengano colori leggibili.

## Validazione 2026-10-12

- `esphome config`: PASS.
- `esphome compile`: PASS.
- OTA su `192.168.1.171`: PASS.
- Post-OTA: device online, ESPHome API raggiungibile, audio stack e VoIP
  inizializzati.
- Secondo OTA palette rosso/viola/blu: PASS.
- Post-secondo OTA: boot riuscito, safe mode ha confermato avvio sano, Wi-Fi
  `100%`, VoIP `idle`, PSRAM libera circa `4.29 MB`.
- Terzo OTA feedback su `listening` reale: PASS.
- Post-terzo OTA: boot riuscito; log reale con `Listen feedback sound` e LED
  `Talk Glow Color` nello stesso istante dello stato ascolto; poi `thinking`,
  `responding` e ritorno OFF.
