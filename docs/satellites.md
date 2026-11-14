# Satelliti in produzione

Fonte unica per sapere quale profilo gira su ogni cassa, con quali parametri e
quale build e' installata. Aggiornare questa pagina a ogni OTA.

## Profili

Tutte le casse compilano la stessa base `esphome/galileo-va-direct-audio-cutover-base.yaml`
(full AFE/AEC, wake word locale, audio diretto verso Galileo Core, VoIP Stack),
con i valori di casa in `esphome/sites/casa.yaml`. Il file di ogni cassa contiene
solo l'identita'. Come si aggiorna la flotta e come si aggiunge una cassa:
[fleet.md](fleet.md).

| | Taverna | Sala | Garage |
| --- | --- | --- | --- |
| Profilo | `galileo-va-direct-audio-cutover.yaml` | `galileo-sala.yaml` | `galileo-garage.yaml` |
| Nome ESPHome | `galileo-va` | `galileo-sala` | `satellite-garage` |
| Nome visibile | Satellite Taverna | Satellite Sala | Satellite Garage |
| Area Home Assistant | Taverna | Salotto 1 | Garage |
| IP (statico) | `192.168.1.171` | `192.168.1.172` | `192.168.1.133` |
| Interno VoIP | `101` | `102` | `103` |
| Gruppi (dal sito) | RG Casa, RG Tutti, CG Casa | uguale | uguale |
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

Tabella generata da `tools/fleet docs` dopo ogni rollout o rollback. L'hash
identifica l'artefatto; i `.bin` non vanno in Git perche' contengono le
credenziali.

<!-- fleet:installed:start -->
<!-- Generata da tools/fleet.py dal file fleet/casa.installed.json: non modificare a mano. -->
| Cassa | Release | Firmware | Build (`build_time`) | Installata | SHA-256 OTA (16) |
| --- | --- | --- | --- | --- | --- |
| Satellite Garage Hybrid | 2026.11.1 | efdae64 | 2026-11-14 14:19:43 +0100 | 2026-11-14 14:29 | `7f8af196bc31d09f` |
| Satellite Sala | pre-2026.11.1 | 026f0c7 | 2026-11-14 11:16:28 +0100 | 2026-11-14 11:26 | `0161ec7b085d55b4` |
| Satellite Taverna | pre-2026.11.1 | 026f0c7 + IP statico e log INFO | 2026-11-14 11:17:37 +0100 | 2026-11-14 11:52 | `d2d7c494c9ea437f` |
<!-- fleet:installed:end -->

Release nel repository: `2026.11.1` (tag `fw-2026.11.1`), compilata il
14/11/2026 e archiviata in `~/esp-firmware-builds/casa/2026.11.1/` (Garage
`7f8af196bc31d09f`, Sala `517fd20dc2928890`, Taverna `9436cb496f28907e`).
Rollout non ancora eseguito: rispetto alle build installate aggiunge solo
l'entita' *Firmware Release* e la versione di progetto.

`pre-2026.11.1` indica le build installate prima del sistema flotta: non
dichiarano la release. La build Garage del 31/10 conteneva gia' il codice finale
di `026f0c7`, e la ricompilazione del 14/11 ha prodotto un binario identico
(stesso hash). ESPHome aggiorna `build_time` solo se cambia la configurazione
YAML, quindi la data mostrata in Home Assistant non basta: fa fede l'hash.

Archivio dei binari:

| Cartella | Contenuto |
| --- | --- |
| `~/esp-firmware-builds/casa/<release>/` | build di ogni release (quelle installate il 14/11 sono in `pre-2026.11.1/`) |
| `/home/denny/esp-firmware-backups/20261114-pre-026f0c7/` | build ancora precedenti: Taverna `2d41348900e96495` (24/10), Sala `8e5865675c960abe` (28/10) |

## Build e OTA

Si usa lo script della flotta (dettagli in [fleet.md](fleet.md)):

```bash
tools/fleet status      # stato live
tools/fleet build       # compila e archivia la release corrente
tools/fleet rollout     # canarino (Garage), test a voce, poi Sala e Taverna
tools/fleet rollback <cassa>
```
