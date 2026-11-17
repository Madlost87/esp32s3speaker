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
| Guadagno microfono | +18 dB | +18 dB | +18 dB |
| Pre-roll voce diretta | 500 ms | 500 ms | 500 ms |

Nomi ESPHome diversi (`galileo-va`, `galileo-sala`, `satellite-garage`) sono
storici: cambiarli crea un nuovo dispositivo in Home Assistant e richiede di
aggiornare Galileo Core, rubrica e dashboard. Non rinominare senza un piano.

Il guadagno del microfono (`number.*_mic_gain`, da -20 a +30 dB) si regola da
Home Assistant e resta salvato nella cassa anche dopo riavvii e OTA; il
firmware parte da 0 dB solo su una cassa nuova o dopo un flash completo. A
0 dB la voce arrivava a circa -31 dBFS e Vosk dava trascrizioni vuote oltre
30-50 cm; a +18 dB arriva a circa -23 dBFS (misure sul Garage, 14/11/2026).
Su una cassa nuova va impostato a +18 dB dopo il primo avvio.

Dalla 2026.11.3 la cassa tiene in PSRAM gli ultimi 500 ms di audio mentre
aspetta la wake word (`pre_roll_ms` in `packages/satellite/direct_voice.yaml`)
e li manda al Core prima della registrazione. Senza, la prima parola detta
subito dopo la wake word si perdeva: sulla Sala, il 15/11/2026, "che ore sono"
non veniva capito in nessuno di 10 tentativi; con il pre-roll e' stato capito
in 2 tentativi su 3.

Dalla 2026.11.5, riattivando il microfono riparte davvero anche la wake word.
La 2026.11.4 chiamava gia' `start_mww_when_ready` all'unmute, ma lo script
non partiva mai: `init_in_progress` veniva azzerato solo dall'Assist di Home
Assistant, che nel profilo a voce diretta non si collega. Ogni muto, cambio di
modo AEC o OTA annullato lasciava la cassa sorda a "Okay Nabu" fino al
riavvio. Ora l'avvio si chiude in `on_boot` (`packages/satellite/wake_word.yaml`);
verificato sul Garage il 15/11/2026: dopo muto e unmute la wake word riparte
in 2 s e "Okay Nabu" viene riconosciuto. Per lo stesso motivo il cambio del
modo AEC da Home Assistant prima veniva ignorato e ora si applica.

Dalla 2026.11.6:

- dopo una domanda del Core ("A che ora ti sveglio?") la cassa fa il bip e
  riapre il microfono per la risposta, senza wake word. Lo chiede il Core con
  il comando `listen:<response_id>` subito dopo la fine della risposta; la
  cassa lo accetta solo per la risposta appena finita, entro 5 secondi.
  Cattura senza pre-roll (conterrebbe la voce della cassa), al massimo 7
  secondi (`followup_maximum_capture_ms`), con il rumore di fondo misurato
  all'ultimo "Okay Nabu". Guida: `homeassistant/docs/operations/risposte-senza-parola-di-attivazione.md`;
- la cattura passa per una coda di 32 blocchi (circa mezzo secondo). Prima
  c'era un solo blocco da 16 ms e ogni giro lento del loop ne perdeva uno:
  il 10-13% dell'audio spariva, anche nei comandi con wake word, e Vosk dava
  trascrizioni vuote (misure sul Garage, 17/11/2026). Il log della chiusura
  riporta i blocchi persi della singola cattura.

Dalla 2026.11.7 l'unica parola di attivazione e' "Okay Nabu". "Alexa" e
"Hey Jarvis" restano nel firmware ma spente all'avvio (vedi
`wake-word-models.md` per riattivarle).

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
| Satellite Garage | 2026.11.7 | 5545642 | 2026-11-17 16:31:08 +0100 | 2026-11-17 16:35 | `d2d70911fb397b5b` |
| Satellite Sala | 2026.11.7 | 5545642 | 2026-11-17 16:32:18 +0100 | 2026-11-17 16:35 | `03402d5111615bab` |
| Satellite Taverna | 2026.11.7 | 5545642 | 2026-11-17 16:33:43 +0100 | 2026-11-17 16:36 | `54f14e15407dc107` |
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
