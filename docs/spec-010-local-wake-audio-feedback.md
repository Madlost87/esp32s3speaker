# Spec 010 — Feedback sonoro locale alla wake word

## Obiettivo

Dare una conferma udibile immediata quando il satellite riconosce una wake
word, senza dipendere da Galileo Core, Home Assistant o dalla rete.

## Comportamento

1. Il micro wake word conferma la rilevazione.
2. Il satellite genera localmente un tono sintetico di 120 ms, circa 1,4 kHz,
   a bassa ampiezza e con rampa anti-click.
3. Dopo 160 ms avvia la cattura PCM diretta verso Galileo Core.
4. Il LED continua a passare al rosso di ascolto come prima.

Il ritardo evita che il tono finisca nella registrazione STT. L'utente deve
iniziare il comando dopo il bip.

## Non cambia

- Wake word, AEC, endpoint adattivo e limite massimo di cattura (4,5 s).
- Audio VoIP, radio, TTS del Core e ringtone.
- Protocollo UDP autenticato tra satellite e Core.

## Verifica

- Dopo «Okay Nabu» si sente una sola conferma locale.
- Dopo il chime il LED entra in ascolto e un comando breve riceve TTS.
- Con radio attiva, il chime non deve produrre una trascrizione o prolungare
  la cattura.

## Rollback

Ricaricare il backup OTA immediatamente precedente a questa modifica oppure
rimuovere le quattro azioni del chime dalla sezione `on_wake_word_detected` e
ricompilare il profilo direct-audio.
