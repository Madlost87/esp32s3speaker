# Spec 007: PCM Direct-Audio Test

## Esito 2026-10-22

Il profilo `esphome/galileo-va-direct-audio-test.yaml`, derivato dalla
baseline golden e con riferimenti esterni fissati a SHA, e' stato compilato e
installato con la stessa identita' ESPHome del golden (`galileo-va`).

Un receiver effimero sul Core ha ricevuto una sessione autenticata avviata e
chiusa manualmente mediante l'API nativa ESPHome:

- PCM mono, 16 kHz;
- durata: 18,64 s;
- frame mancanti: 0;
- il WAV e il receiver sono stati eliminati subito dopo la verifica.

Nella stessa sessione sono stati verificati Assist, TTS e VoIP, incluso
l'hang-up vocale durante una chiamata. Non e' emersa alcuna regressione.

## Confini Operativi

Aggiornamento TTS 2026-10-22: aggiunto `media_player: speaker_media_player`
al tap del profilo di test, compilato con ESPHome 2026.9.1 e installato OTA.
Servizio nativo `galileo_direct_tts` verificato dopo il riavvio, stato VoIP
`idle`. Primo WAV dell'ora prelevato dalla cassa via server temporaneo Core:
trasferimento riuscito e ascolto confermato dall'utente. Ripetere i test Assist/TTS/VoIP
e hang-up vocale prima di attestare nuovamente la parita'. Golden invariato.

Il tap e' inattivo fino a un comando API autenticato: non riceve attivazioni
automatiche da wake word, Assist o VoIP. Il test non modifica il percorso TTS
quotidiano e non sostituisce la pipeline Assist. Non installare
`galileo-va-direct-audio-cutover.yaml`: rimane un candidato solo da compilare.

## Prossimo Passo

L'ultima prova Vosk ha trascritto esattamente `che ore sono` (30,624 s di
cattura, 1,46 s dopo taglio silenzi, zero frame mancanti). Il codice Core ora
gestisce `local.time`; la risposta e' stata sintetizzata e ascoltata in un
test separato. Non esiste ancora un turno automatico completo.

Prima ripetere la parita' dopo l'ultimo OTA, poi integrare wake/fine parlato,
STT/risposta/TTS e gestione errori/stati VoIP. Cutover solo dopo test ripetuti
e rollback della versione candidata. Nessun listener o audio temporaneo resta
attivo; il golden e lo stack VoIP non sono stati modificati.

## Candidato Cutover

`galileo-va-direct-audio-cutover.yaml` ora include il profilo statico
`galileo-va-direct-audio-cutover-base.yaml`: rimuove Assist, conserva AFE,
wake word, LED, pulsanti, player e `voip_stack`, e fissa tutte le dipendenze
agli SHA del golden. Compilazione ESPHome 2026.9.1 riuscita: OTA 2.995.871
byte, DIRAM 49,1%, flash 36,9%. Non e' stato installato.

La parita' post-OTA del profilo test e' confermata dall'utente per Assist,
VoIP e hang-up vocale, mute, Boot, LED e volume. Prima dell'OTA candidato
manca ancora il runner automatico Core `wake -> PCM -> STT -> risposta -> TTS`
e la successiva prova di rollback.
