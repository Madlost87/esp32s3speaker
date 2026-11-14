# Satelliti in produzione

Fonte unica per sapere quale profilo gira su ogni cassa, con quali parametri e
quale build e' installata. Aggiornare questa pagina a ogni OTA.

## Profili

Tutti e tre usano la stessa base `esphome/galileo-va-direct-audio-cutover-base.yaml`
(full AFE/AEC, wake word locale, audio diretto verso Galileo Core, VoIP Stack).
I componenti esterni sono fissati per SHA nella base: due build dello stesso
commit sono equivalenti. Ogni profilo cambia solo identita' e trasporto.

| | Taverna | Sala | Garage |
| --- | --- | --- | --- |
| Profilo | `galileo-va-direct-audio-cutover.yaml` | `galileo-sala.yaml` | `galileo-garage-hybrid.yaml` |
| Nome ESPHome | `galileo-va` | `galileo-sala` | `satellite-garage` |
| Nome visibile | Satellite Taverna | Satellite Sala | Satellite Garage Hybrid |
| Area Home Assistant | Taverna | Salotto 1 | Garage |
| IP (statico) | `192.168.1.171` | `192.168.1.172` | `192.168.1.133` |
| Interno VoIP | `101` | `102` | `103` |
| Gruppi | RG Casa, RG Tutti, CG Casa | uguale | uguale |
| Audio / controllo diretto | UDP `19007` / `19008` | `19009` / `19010` | `19011` / `19012` |
| Segreto sessione | `galileo_audio_bridge_session_id` | `..._sala` | `..._garage` |
| Dialogo diretto | off | off | off |
| Log | INFO | INFO | INFO |

Nomi ESPHome diversi (`galileo-va`, `galileo-sala`, `satellite-garage`) sono
storici: cambiarli crea un nuovo dispositivo in Home Assistant e richiede di
aggiornare Galileo Core, rubrica e dashboard. Non rinominare senza un piano.

Le sessioni dirette devono coincidere con
`GALILEO_DIRECT_VOICE_SATELLITES_JSON` nel `.env` di Galileo Core sul Raspberry.

## Allineamento con il repository Home Assistant

| Elemento | Dove |
| --- | --- |
| Rubrica e interni | `homeassistant/voip/phonebook.json` |
| Sorgenti audio dirette | `.env` di Galileo Core (`GALILEO_DIRECT_VOICE_SATELLITES_JSON`) |
| Aree, dashboard, package | `homeassistant/docs/operations/home-assistant-config.md` |
| Centralino VoIP | `homeassistant/docs/operations/voip-centralino.md` |

## Build installate

Aggiornare a ogni OTA. L'hash identifica l'artefatto; i `.bin` non vanno in Git
(contengono credenziali).

| Cassa | Build (`build_time`) | OTA installata | Firmware | SHA-256 OTA (16) |
| --- | --- | --- | --- | --- |
| Taverna | 2026-11-14 11:17 | 2026-11-14 11:52 | `026f0c7` + IP statico e log INFO | `d2d7c494c9ea437f` |
| Sala | 2026-11-14 11:16 | 2026-11-14 11:26 | `026f0c7` | `0161ec7b085d55b4` |
| Garage | 2026-10-31 10:49 | 2026-11-14 11:45 (stesso binario) | `026f0c7` | `b85f6e3a8effac6f` |

La build Garage del 31/10 conteneva gia' il codice finale di `026f0c7`: la
ricompilazione del 14/11 ha prodotto un binario identico (stesso hash).
ESPHome aggiorna `build_time` solo se cambia la configurazione YAML, quindi la
data mostrata in Home Assistant non basta: fa fede l'hash.

Build precedenti (rollback) in `/home/denny/esp-firmware-backups/20261114-pre-026f0c7/`:
Taverna `2d41348900e96495` (24/10), Sala `8e5865675c960abe` (28/10).

## Build e OTA

```bash
cd esphome
esphome compile galileo-sala.yaml
esphome upload galileo-sala.yaml --device 192.168.1.172
```

Ordine consigliato per un aggiornamento comune: Sala, poi Taverna, poi Garage,
con test vocale (wake word, "che ore sono", chiamata VoIP) dopo ciascuna.

Rollback: `esphome upload <profilo> --file /home/denny/esp-firmware-backups/<data>/<nome>.ota.bin --device <ip>`.
