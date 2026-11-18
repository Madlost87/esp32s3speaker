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

Dalla 2026.11.8 il mute della card media player in Home Assistant e lo switch
`Speaker Mute` sono lo stesso mute: attivarne uno attiva l'altro, in entrambe
le direzioni (`packages/satellite/controls.yaml`). Prima il mute della card
silenziava solo le pipeline media e TTS, non le chiamate, e non accendeva il
LED arancione. `Mic Mute` resta separato: silenziare l'ascolto non impedisce
di sentire chiamate e sveglie. Verificato sul Garage il 18/11/2026: card e
switch si seguono e con la card mutata il TTS non si sente.

La 2026.11.9 e' solo pulizia, senza funzioni nuove. Toglie tre pacchetti
upstream rimasti dall'era Assist che nessuno usava:

- `voice_assistant/local_commands.yaml`: l'azione API `voice_quiet`, che non
  era chiamata da Home Assistant, dal Core o dalle dashboard;
- `voip/debug.yaml`: i sensori `VoIP Transport` e `VoIP SIP Snapshot`. Erano
  6 entita' che nessuno leggeva e che riempivano la cronologia di HA. Per
  una diagnosi SIP si rimette la riga `voip_debug` nella base;
- `voice_assistant/timers_runtime.yaml`: suoneria e loop dei timer di Assist.
  Con la voce diretta timer e sveglie li gestisce il Core e li fa suonare dal
  media player, quindi l'attivita' `timer_ringing` non si accendeva piu'. E'
  stata tolta anche la funzione `timers` del runtime controller (i binding
  sono in archivio) e il ramo "ferma timer" del clic singolo sul tasto BOOT.

Il clic singolo e' identico al vecchio ramo senza timer: con una chiamata in
corso risponde o riaggancia, altrimenti avvia l'ascolto. Doppio clic e
pressione lunga sono invariati. Verifica: la configurazione risolta delle tre
casse cambia solo in questi punti e nel numero di release.
Installata il 19/11/2026: `fleet check --active --core` OK su tutte e tre e
Home Assistant ha rimosso da solo i 6 sensori. La prova a mano del tasto
BOOT (clic per l'ascolto, clic per rispondere e per riagganciare) e' ancora
da fare.

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
| Satellite Garage | 2026.11.9 | 0bf24e1 | 2026-11-18 23:50:31 +0100 | 2026-11-18 23:56 | `ad9d4540488a1e5a` |
| Satellite Sala | 2026.11.9 | 0bf24e1 | 2026-11-18 23:52:22 +0100 | 2026-11-19 00:00 | `c5b19d5c712db1b1` |
| Satellite Taverna | 2026.11.9 | 0bf24e1 | 2026-11-18 23:54:14 +0100 | 2026-11-19 00:01 | `e4c4a28f8e489687` |
<!-- fleet:installed:end -->

Tutte e tre le casse sono sulla release `2026.11.9` dal 19/11/2026 (tag da
`fw-2026.11.1` a `fw-2026.11.9`). Fa fede la tabella generata qui sopra.

ESPHome aggiorna `build_time` solo se cambia la configurazione YAML, quindi la
data mostrata in Home Assistant non basta: fa fede l'hash. `pre-2026.11.1`
indica le build installate prima del sistema flotta, che non dichiarano la
release.

Archivio dei binari:

| Cartella | Contenuto |
| --- | --- |
| `~/esp-firmware-builds/casa/<release>/` | build di ogni release (quelle installate il 14/11 sono in `pre-2026.11.1/`) |
| `/home/denny/esp-firmware-backups/20261114-pre-026f0c7/` | build ancora precedenti: Taverna `2d41348900e96495` (24/10), Sala `8e5865675c960abe` (28/10) |

## Build e OTA

Build, rollout, rollback e controlli si fanno con `tools/fleet`: vedi
[fleet.md](fleet.md).

## VoIP

- Ogni cassa e' un peer SIP diretto del VoIP Stack dentro Home Assistant
  (`192.168.1.186`): non registra un account SIP e non usa digest
  authentication.
- Interno in `voip_extension` del file della cassa; gruppi squillo e
  conferenza in `esphome/sites/casa.yaml` (`voip_ring_groups`,
  `voip_conference_groups`), usati da `packages/satellite/voip.yaml`.
- La rubrica e' di Home Assistant, che la manda alla cassa come roster.
  `static_contacts` in `packages/satellite/voip.yaml` (Casa, RG Casa, RG Tutti,
  ESP Cucina, Softphone 200) sono solo nomi di riserva per i tasti finche' la
  rubrica non arriva dopo un riavvio. Se cambiano i nomi nella rubrica HA,
  aggiornare anche questa lista.
- L'IP e' fisso: `wifi.manual_ip` in `packages/satellite/connectivity.yaml`,
  con `static_ip` dal file della cassa. Conviene comunque riservarlo nel router.
- Non esporre SIP/RTP della cassa su Internet; fuori casa usare la VPN.
- Cronologia della prima messa in servizio (ottobre 2026):
  [history/voip-centralino-esp32.md](history/voip-centralino-esp32.md).
