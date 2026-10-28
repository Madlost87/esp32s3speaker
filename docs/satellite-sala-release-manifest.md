# Manifest di release — Satellite Sala

Ultimo aggiornamento: 2026-10-28.

Questo documento registra il firmware installato su `galileo-sala` e la
correzione applicata al percorso TTS. Non sostituisce il manifest di Taverna.

## Identita' e rete

| Campo | Valore |
| --- | --- |
| Satellite | `Satellite Sala` / `galileo-sala` |
| IP | `192.168.1.172` |
| Core | `192.168.1.186` |
| Audio diretto | UDP autenticato verso Core porta `19009` |
| Controllo/TTS diretto | UDP porta `19010`; asset HTTP dal Core |
| Estensione VoIP | `102` |

## OTA installata

| Campo | Valore |
| --- | --- |
| Data e ora compilazione | `2026-10-28 08:36:01 +01:00` |
| Versione ESPHome | `2026.9.1` |
| Profilo | `esphome/galileo-sala.yaml` |
| SHA-256 OTA | `8e5865675c960abe0cba6a283a2682e4c305ba31f0541e7948aee16f65d917c7` |
| Dimensione OTA | `2,999,856` byte |
| Upload | riuscito via ESPHome OTA v2 su `192.168.1.172` |
| Verifica post-OTA | API ESPHome online, identita' `galileo-sala` confermata |

Il file `firmware.ota.bin` non viene versionato: puo' incorporare credenziali.
L'hash consente invece di identificare esattamente l'artefatto installato.

## Correzione TTS / watchdog

La build precedente di Sala usava il buffer del resampler TTS di `100ms`.
Durante la risposta Piper HTTP questo causava audio frammentato e un reset
`Task wdt` sul core 1. Taverna, con la stessa versione ESPHome e pipeline,
usa `250ms`.

Il profilo di Sala imposta ora `tts_speaker_input.buffer_duration: 250ms`.
Non sono stati modificati codec, AFE, pinout, VoIP, porte o credenziali.

## Accettazione ancora richiesta

1. Pronunciare wake word e chiedere l'ora a Sala.
2. Confermare TTS continuo, senza LED d'errore o reboot.
3. Controllare il log ESPHome: assenza di `Task wdt` dopo la risposta.
4. Verificare una chiamata VoIP in uscita e una in ingresso sull'estensione
   `102`.
