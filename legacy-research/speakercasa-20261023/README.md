# Archivio storico Speakercasa — 2026-10-23

Questa cartella conserva materiale di ricerca proveniente dal precedente
workspace `speakercasa`. Non è runtime attivo e non deve essere incluso in un
OTA senza confronto esplicito con i file in `esphome/`.

Contenuto copiato senza rimuovere gli originali:

- `docs/`: note di progetto e audit wake-word;
- `diagnostics/`: risultati di prove hardware, AFE, VAD e wake-word;
- `scripts/`: strumenti di raccolta, benchmark e sperimentazione ReSpeaker /
  OpenWakeWord;
- `satellite/`: prototipo Python del satellite;
- `yaml-candidates/`: configurazioni ESPHome storiche, esclusivamente per
  confronto.

Non sono stati copiati: dump raw e golden (conservati in
`/home/denny/galileo-backups/`), file audio e dati di training, virtualenv,
cache `.esphome`, build e segreti.

La configurazione attiva della cassa resta in `esphome/`; in particolare ogni
YAML qui archiviato è un candidato storico e non una sorgente di deploy.
