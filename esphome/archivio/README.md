# Archivio profili firmware

Profili di laboratorio e di recovery. Nessuna cassa in produzione li usa: le
casse usano `../galileo-va-direct-audio-cutover-base.yaml` tramite i file per
dispositivo in `esphome/` (vedi `docs/fleet.md`).

| File | Cos'era |
| --- | --- |
| `galileo-va.yaml` | primo profilo stock (pacchetto upstream Waveshare) |
| `galileo-va-afe.yaml` | profilo AFE completo che segue i componenti `@main` |
| `galileo-va-afe-pinned-20261010.yaml` | lo stesso, bloccato agli hash del golden 2026-10-10 |
| `galileo-va-afe-agc-test.yaml`, `-agc-lite.yaml`, `-no-ha-vad-test.yaml` | prove AGC e VAD (`docs/agc-test-plan.md`) |
| `galileo-va-afe-slot-diagnostics.yaml` | diagnostica slot TDM (`docs/tdm-slot-diagnostics.md`) |
| `galileo-va-direct-audio-test.yaml` | primo test di audio diretto (`docs/spec-007-direct-audio-test.md`) |

`galileo-va-afe.yaml` e le prove che lo includono non si compilano piu' con
ESPHome 2026.9.1, perche' i componenti `@main` ora richiedono 2026.10.0.

## Recovery

Il punto di ritorno vero sono i binari in
`backups/golden-esp-voip-20261010/` (`docs/golden-firmware-recovery.md`). Per
ricompilare il golden si usa `galileo-va-afe-pinned-20261010.yaml`.

## Compilare un profilo archiviato

ESPHome cerca `secrets.yaml` accanto al file compilato:

```bash
cd esphome/archivio
ln -s ../secrets.yaml secrets.yaml      # ignorato da git
esphome config galileo-va-afe-pinned-20261010.yaml
```
