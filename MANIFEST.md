# Manifest — repository firmware delle casse Galileo

Mappa del repository: a cosa serve, cosa contiene ogni cartella, dove finisce
e dove stanno i dati che non sono qui. Lo stato delle casse e l'hardware sono
nel [README](README.md).

## A cosa serve

E' il repository del **firmware ESPHome** delle casse vocali ESP32-S3 (board
diymore / Waveshare ESP32-S3-AUDIO) e degli strumenti per gestirle come una
flotta: compilare, installare con un canarino, controllare, tornare indietro.

Il resto del sistema (Galileo Core, Home Assistant, centralino VoIP) e' nel
repository gemello `homeassistant` (vedi [in fondo](#il-repository-gemello-homeassistant)).

## Come e' fatto il firmware

Ogni cassa e' costruita da tre livelli; un fix si fa una volta sola, nel
livello giusto, e arriva a tutte le casse con un rollout.

```text
esphome/galileo-va-direct-audio-cutover-base.yaml   FIRMWARE   uguale per tutte le casse
  + esphome/packages/satellite/*.yaml                           (audio, board, rete, tasti e mute,
  + esphome/components/                                          voce diretta, VoIP, wake word)
esphome/sites/casa.yaml                              SITO       rete, indirizzo del Core, Wi-Fi, gruppi VoIP
esphome/galileo-garage.yaml                          CASSA      solo identita': nome, IP, interno, porte, sessione
esphome/galileo-sala.yaml
esphome/galileo-va-direct-audio-cutover.yaml        (Taverna: nome storico del file, da non rinominare)
```

## Cartelle

| Cartella / file | Contenuto | Dove finisce |
| --- | --- | --- |
| `esphome/` | Configurazione ESPHome attiva: base, `packages/satellite/`, `sites/`, un file per cassa, `secrets.example.yaml` | compilata e installata via OTA sulle casse |
| `esphome/components/` | Componenti locali: `galileo_audio_tap/` (C++, cattura audio per la voce diretta) e `galileo_direct_runtime/` (pacchetti YAML del runtime) | dentro il firmware |
| `esphome/archivio/` | Profili superati (vecchio AFE, profilo stock, golden di ottobre) e, in `non-inclusi-2026-11-18/`, i YAML che nessuna cassa include piu'. Ogni sottocartella ha un README | da nessuna parte: solo storia e recupero |
| `fleet/` | `casa.yaml`: quali casse esistono, ordine di rollout, canarino (Garage). `casa.installed.json`: release e hash installati su ogni cassa, scritto da `tools/fleet` | — |
| `tools/` | `fleet` / `fleet.py`: `status`, `check`, `build`, `rollout`, `rollback`, `release`, `new`, `docs` | eseguito dal PC di sviluppo |
| `scripts/` | `check_esphome_secrets.py`: controlla che i segreti richiesti esistano | PC di sviluppo |
| `docs/` | Documentazione attuale e `history/` con quella superata. Indice: [docs/README.md](docs/README.md) | — |
| `diagnostics/` | Diagnostica hardware della board (chip, USB, sicurezza, partizioni, stringhe del firmware di fabbrica) | — |
| `legacy-research/` | Ricerca precedente (Raspberry + ReSpeaker, openWakeWord), non usata dal firmware | — |
| `AUDIT_HARDWARE.md` | Inventario hardware della board e analisi iniziale | — |

## Fonti di verita'

| Dato | Fonte |
| --- | --- |
| Nome, IP, interno, porte audio, sessione di ogni cassa | il file della cassa in `esphome/` |
| Rete, indirizzo di Galileo Core, gruppi VoIP del sito | `esphome/sites/casa.yaml` |
| Numero di release | `firmware_release` nella base (lo cambia `tools/fleet release`) |
| Cosa e' installato su ogni cassa | `fleet/casa.installed.json` (e la tabella generata in `docs/satellites.md`) |
| Stato dal vivo delle casse | `tools/fleet status` / `tools/fleet check` |

## Cosa non c'e' (e dove sta)

| Cosa | Dove sta |
| --- | --- |
| Password Wi-Fi, chiavi API/OTA, sessioni audio | `esphome/secrets.yaml`, solo sul PC (fuori da Git; modello in `secrets.example.yaml`) |
| Binari compilati di ogni release | `~/esp-firmware-builds/casa/<release>/` sul PC (contengono le credenziali Wi-Fi) |
| Backup della flash di fabbrica e catture audio locali | `backups/` (fuori da Git); il dump di fabbrica anche in `../hardware/` accanto al repository |
| Cache di compilazione ESPHome | `esphome/.esphome/`, `esphome/.cache/` (fuori da Git) |
| Toolchain | ESPHome 2026.9.1 in `/home/denny/esphome/.venv-2026.9.1` |

## Una modifica, dall'inizio alla fine

1. Si modifica la base (o un pacchetto) e si prova su una cassa:
   `cd esphome && esphome run galileo-garage.yaml --device 192.168.1.133`.
2. `tools/fleet release AAAA.M.N`, commit e tag `fw-AAAA.M.N`.
3. `tools/fleet build`: compila tutte le casse dal commit pulito.
4. `tools/fleet rollout`: canarino, prova a voce, poi le altre.
5. `tools/fleet check --active --core http://192.168.1.186:8099`.
6. Commit di `fleet/casa.installed.json` e `docs/satellites.md`.

Guida completa: [docs/fleet.md](docs/fleet.md).

## Il repository gemello (`homeassistant`)

| | |
| --- | --- |
| Percorso locale | `../../homeassistant` |
| Remote | `github.com/Madlost87/homeassistant` |
| Contiene | Galileo Core, configurazione di Home Assistant, rubrica VoIP, manifest dei servizi del Raspberry |

Cosa passa tra i due:

- le casse mandano la voce a Galileo Core (`192.168.1.186`) e ne scaricano le
  risposte parlate; porte audio e sessioni del file di ogni cassa devono
  coincidere con `GALILEO_DIRECT_VOICE_SATELLITES_JSON` nel `.env` del Core;
- le casse sono telefoni SIP del VoIP Stack dentro Home Assistant; la rubrica
  e' `voip/phonebook.json` nell'altro repository e `tools/fleet new
  --phonebook` la aggiorna quando si aggiunge una cassa.
