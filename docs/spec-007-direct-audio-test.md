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

Il profilo di test resta inattivo fino a un comando API autenticato. Il profilo
cutover era stato installato in OTA assistito e apre/chiude il tap
automaticamente dopo wake word e fine parlato, ma rimuove Assist dal percorso
voce: non e' percio' adatto all'uso quotidiano con il Core diretto disabilitato.

## Prossimo Passo

L'ultima prova Vosk ha trascritto esattamente `che ore sono` (30,624 s di
cattura, 1,46 s dopo taglio silenzi, zero frame mancanti). Il codice Core ora
gestisce `local.time`; la risposta e' stata sintetizzata e ascoltata in un
test separato. Non esiste ancora un turno automatico completo.

Il 2026-10-22 il candidato ha completato il primo turno automatico: wake ->
505 frame PCM senza perdite -> STT -> `local.time` -> Piper -> TTS. Il
satellite ha prelevato l'asset monouso con HTTP 200. Il Core e' stato subito
riportato alla compose ordinaria, con runner disabilitato e HTTP su loopback.
Il rollback OTA al golden verificato e' stato eseguito e l'utente ha confermato
il ritorno di Assist e delle animazioni LED originali. Seguono prove di
errori/timeout, wake durante VoIP e una soluzione LED validata sul candidato.

## Candidato Cutover

`galileo-va-direct-audio-cutover.yaml` ora include il profilo statico
`galileo-va-direct-audio-cutover-base.yaml`: rimuove Assist, conserva AFE,
wake word, LED, pulsanti, player e `voip_stack`, e fissa tutte le dipendenze
agli SHA del golden. Compilazione ESPHome 2026.9.1 riuscita: OTA 2.996.048
byte, DIRAM 49,1%, flash 36,9%. Il tap chiude dopo 1,2 s di silenzio rilevato,
con limite massimo di sicurezza di 15 s. Il candidato e' stato installato in
OTA assistito per il test, poi rimosso con rollback golden. Micro Wake Word e'
avviato esplicitamente al boot. Hash della prima OTA candidata:
`56730239b6e75506edd32909da54b80998bd21aec0537f8c890e1a8898cc589f`.

La parita' post-OTA del profilo test e' confermata dall'utente per Assist,
VoIP e hang-up vocale, mute, Boot, LED e volume. Prima dell'OTA candidato
manca ancora il runner automatico Core `wake -> PCM -> STT -> risposta -> TTS`
e la successiva prova di rollback.

## Ripresa del Goal

## Finestra assistita 2026-10-23 — rollback obbligatorio

Il candidato con il runner Core, timeout espliciti e segnalazione UDP
autenticata di errore e' stato compilato e caricato in OTA assistito. Il Core
e' stato avviato temporaneamente con receiver UDP autenticato e server HTTP
LAN per il WAV monouso. Al primo wake l'utente ha osservato LED rosso bloccato
e un breve lampeggio arancione, senza risposta vocale.

Il receiver avviato localmente non ha ricevuto `OPEN` o frame PCM, ma era
stato erroneamente associato all'IP `.173`, che non e' l'orchestratore. La
configurazione corretta resta `.186`. I log del Core reale hanno poi
confermato piu' turni completi `wake -> PCM -> Vosk -> Piper -> WAV`, con
frame completi e prelievo HTTP dell'asset da parte della cassa.

Il LED arancione persistente e' riproducibile quando il router produce
`unknown` o `llm.ask` senza testo da pronunciare: il Core tornava idle solo
internamente e non inviava alcun comando al firmware. La correzione Core
segnala in quel ramo l'attivita' UDP autenticata `error`; il candidato gia'
prevede rosso per due secondi e poi idle. Non e' stata eseguita una nuova OTA:
il golden e' stato verificato con `sha256sum -c` e ricaricato
(`eaf02581fdd00b615965fe12d8ed4537c1b533802de189243e3bf6e67036d52b`), e
l'utente ha confermato il ritorno di Assist e dell'anello LED normale.

Prima di un nuovo candidato: distribuire prima il Core corretto su `.186`,
acquisire un log continuo del wake e provare sia una risposta locale sia una
richiesta senza risposta; conservare ELF/bin corrispondenti.

Obiettivo: Galileo Core proprietario della voce; Home Assistant solo domotica;
`voip_stack` invariato, incluso riaggancio vocale in chiamata.

La cassa ora esegue il golden con Assist operativo; il runner Core e'
disabilitato in configurazione ordinaria. Alla ripresa: progettare e validare
la parita' LED senza dipendere da eventi `voice_assistant`, poi ritestare
errori, timeout e VoIP reale prima di un nuovo OTA candidato.
