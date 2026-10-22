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

Il tap e' inattivo fino a un comando API autenticato: non riceve attivazioni
automatiche da wake word, Assist o VoIP. Il test non modifica il percorso TTS
e non sostituisce la pipeline Assist. Non installare
`galileo-va-direct-audio-cutover.yaml`: rimane un candidato solo da compilare.

## Prossimo Passo

Provare STT locale su una cattura effimera e confrontare il transcript, senza
collegare ancora wake word, risposta o stati VoIP al bridge.
