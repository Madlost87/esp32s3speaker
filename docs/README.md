# Indice della documentazione

Casse in produzione, parametri e build installate: [satellites.md](satellites.md).
Release, rollout, rollback e nuove casse: [fleet.md](fleet.md).

## Attuali

- [satellites.md](satellites.md): le tre casse (Taverna, Sala, Garage), parametri,
  novita' per release, VoIP e build installate.
- [fleet.md](fleet.md): `tools/fleet` (status, check, build, rollout, rollback,
  release, new, docs), nuova cassa e nuovo sito.
- [wake-word-models.md](wake-word-models.md): modelli `micro_wake_word` nel
  firmware (attiva solo `Okay Nabu`).
- [spec-010-local-wake-audio-feedback.md](spec-010-local-wake-audio-feedback.md):
  bip locale alla wake word.
- [spec-011-firmware-modularity-and-transport-hardening.md](spec-011-firmware-modularity-and-transport-hardening.md):
  modularita' del firmware e hardening del trasporto.
- [specs-index.md](specs-index.md): stato delle spec e ordine dei lavori.
- [golden-firmware-recovery.md](golden-firmware-recovery.md): recovery verso il
  golden del 10/10/2026 (il rollback normale e' `tools/fleet rollback`).
- [reverse-engineering/README.md](reverse-engineering/README.md): analisi del
  firmware originale Xiaozhi.

## Analisi e riferimenti

- [../AUDIT_HARDWARE.md](../AUDIT_HARDWARE.md): audit hardware della board.
- [references.md](references.md): fonti hardware/software.
- [tdm-slot-diagnostics.md](tdm-slot-diagnostics.md): diagnostica degli slot TDM
  (profilo archiviato).
- [agc-test-plan.md](agc-test-plan.md): piano di test AGC (profilo archiviato).

## Storici

Utili per capire il percorso, non descrivono il firmware attuale.

- [history/voip-centralino-esp32.md](history/voip-centralino-esp32.md): prima
  messa in servizio VoIP di Taverna (ottobre 2026).
- [history/satellite-release-manifest.md](history/satellite-release-manifest.md)
  e [history/satellite-sala-release-manifest.md](history/satellite-sala-release-manifest.md):
  manifest di release prima di `tools/fleet`.
- [history/led-ring-theme.md](history/led-ring-theme.md): tema LED custom
  KITT/Talk Glow, solo nei file archiviati.
- [history/listen-feedback-sound.md](history/listen-feedback-sound.md): switch
  `Listen Feedback Sound`, solo nel profilo archiviato.
- `history/handoff-micro-wake-word-2026-10-12/`: pacchetto per chiedere una wake
  word custom, fermo al 12/10/2026.
- [runtime-validation-20261008.md](runtime-validation-20261008.md): validazione
  della baseline full AFE.
- [spec-007-direct-audio-test.md](spec-007-direct-audio-test.md): test PCM
  diretto verso Galileo Core (ottobre 2026).
- [initial_board_audit.md](initial_board_audit.md): audit iniziale e backup factory.
- [compatibility_audit.md](compatibility_audit.md): valutazione iniziale di
  compatibilita'.
- [first_flash_checklist.md](first_flash_checklist.md): primo flash con profilo stock.
- [original_firmware_audio_adaptation.md](original_firmware_audio_adaptation.md):
  passaggio da Xiaozhi a stock ESPHome e poi ad AFE.
- [project-overview.md](project-overview.md): panoramica iniziale del progetto.
