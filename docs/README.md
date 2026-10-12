# Documentation Index

Questo indice separa i documenti operativi attuali dai documenti storici di
bring-up. La fonte di verita' per il firmware operativo e':

```text
esphome/galileo-va-afe.yaml
```

Profilo corrente:

- device ESPHome: `galileo-va`;
- friendly name: `Satellite Taverna`;
- IP osservato: `192.168.1.171`;
- ESPHome: `2026.9.1`;
- audio: full AFE, TDM 48 kHz, dual mic, AEC/NS/SE, reference hardware;
- wake word attive al boot: `Alexa + Okay Nabu`;
- `Hey Jarvis`: caricato ma disabilitato;
- VoIP: interno `101`, SIP `5060/udp`, RTP base `40000`;
- feedback ascolto: switch per-device `Listen Feedback Sound`.

## Operativi

- `voip-centralino-esp32.md`: guida principale per deploy, VoIP, tasti,
  audio, endpoint e regole operative del satellite.
- `golden-firmware-recovery.md`: procedura di recovery verso lo stato
  funzionante salvato localmente.
- `wake-word-models.md`: stato corrente dei modelli `micro_wake_word` e
  profili di test.
- `listen-feedback-sound.md`: specifica del bip locale opzionale quando il
  satellite entra in ascolto.
- `runtime-validation-20261008.md`: evidenza runtime della baseline full AFE.

## Analisi E Piani

- `../AUDIT_HARDWARE.md`: audit hardware/firmware aggiornato e piano interventi.
- `tdm-slot-diagnostics.md`: note diagnostiche sugli slot TDM.
- `agc-test-plan.md`: piano di test per eventuale AGC AFE in profilo separato.
- `references.md`: fonti hardware/software usate durante gli audit.

## Storici

Questi documenti restano utili per capire il percorso, ma non sono la guida
operativa corrente:

- `initial_board_audit.md`: audit iniziale e backup factory.
- `compatibility_audit.md`: valutazione iniziale di compatibilita'.
- `first_flash_checklist.md`: checklist del primo flash con profilo stock.
- `original_firmware_audio_adaptation.md`: confronto storico tra firmware
  Xiaozhi, profilo stock ESPHome e successivo profilo AFE.
- `project-overview.md`: panoramica iniziale del progetto, superata dal README
  principale e da `voip-centralino-esp32.md`.
