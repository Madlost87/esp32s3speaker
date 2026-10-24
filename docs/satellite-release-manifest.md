# Manifest di release — Satellite Taverna

Ultimo aggiornamento: 2026-10-24.

Questo documento e' la sorgente di verita' operativa per la cassa ESP32-S3
`galileo-va`. Distingue deliberatamente il firmware di produzione dal golden
di recovery: non sono lo stesso artefatto.

## Identita' e rete

| Campo | Valore |
| --- | --- |
| Satellite | `Satellite Taverna` / `galileo-va` |
| IP osservato | `192.168.1.171` |
| Core | `192.168.1.186` |
| Audio diretto | UDP autenticato verso Core porta `19007` |
| Risposte TTS | HTTP dal Core porta `8099` |
| Ruolo Home Assistant | domotica e VoIP; non orchestrazione vocale ordinaria |

L'IP e' un dato operativo, non una garanzia: prima di introdurre una seconda
cassa va fissato con una prenotazione DHCP o sostituito dalla registrazione
multi-cassa.

## Profilo previsto in esercizio

| Campo | Valore |
| --- | --- |
| Profilo ESPHome | `esphome/galileo-va-direct-audio-cutover.yaml` |
| Base del profilo | `esphome/galileo-va-direct-audio-cutover-base.yaml` |
| Commit sorgente | `3da05f3c71cb4ae4a3e4d22df398931d68cb14c6` |
| Versione ESPHome di riferimento | `2026.9.1` |
| Funzione | wake locale, acquisizione PCM, invio a Galileo Core, riproduzione TTS, VoIP invariato |

Il 2026-10-24 i log del Core hanno confermato un ciclo completo dalla `.171`:
wake, cattura PCM, Vosk, routing, Piper e prelievo HTTP della risposta dalla
cassa. Questo attesta il profilo direct-audio in uso; non attesta il checksum
del binario installato.

## Identificativo binario installato

Lo SHA-256 dell'OTA attualmente installata **non e' ancora registrato**. Non
va dedotto dal commit sorgente: compilazioni diverse possono produrre binari
diversi. Alla prossima OTA registrare qui:

```text
Data e ora OTA:
SHA-256 OTA:
Dimensione OTA:
Comando/profilo usato:
Esito test wake -> STT -> TTS:
Esito test VoIP:
```

Conservare il file `.ota.bin` fuori da Git: puo' contenere credenziali
compilate. Il manifest e l'hash, invece, restano versionati.

## Golden di recovery

| Campo | Valore |
| --- | --- |
| Artefatto | `backups/golden-esp-voip-20261010/galileo-va-golden.ota.bin` |
| SHA-256 | `eaf02581fdd00b615965fe12d8ed4537c1b533802de189243e3bf6e67036d52b` |
| Data golden | 2026-10-10 |
| Funzione | ripristino Assist/VoIP noto e stabile |

Il golden e' un rollback di emergenza. Caricarlo disabilita il flusso vocale
diretto verso Galileo Core e riporta la cassa al percorso Assist di Home
Assistant. La procedura completa resta in
[`golden-firmware-recovery.md`](golden-firmware-recovery.md).

## Criteri di accettazione dopo OTA

1. La cassa e' online e ha l'identita' `galileo-va`.
2. Wake word: LED e bip locale coerenti.
3. Comando breve: wake -> PCM -> Vosk -> TTS udibile.
4. Timer: creazione, scadenza ripetuta e `stop` vocale.
5. VoIP: chiamata, risposta/rifiuto e hang-up vocale.
6. Annotare nel blocco precedente hash, esito e data dell'OTA.
