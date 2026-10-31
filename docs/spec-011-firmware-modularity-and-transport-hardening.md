# Spec 011 — Modularità e hardening del firmware satellite

## Stato

Proposta. Nessuna modifica firmware, Core, OTA o protocollo è autorizzata da
questa spec senza una fase successiva esplicita.

## Gate di ingresso — obbligatorio prima del codice

Il refactor inizia soltanto dopo avere registrato, in un report sanitizzato,
queste quattro informazioni:

1. **Sorgente autorevole:** scegliere un solo albero ESPHome modificabile. Le
   copie storiche o di handoff restano di sola lettura; non si applicano patch
   in due alberi diversi.
2. **Versionamento:** la sorgente autorevole deve stare in un repository Git
   con branch pulito e commit iniziale della baseline. Binari, `secrets.yaml`,
   audio e log restano esclusi.
3. **Golden verificabili:** per Taverna, Sala e Garage annotare profilo,
   versione ESPHome, SHA delle dipendenze, hash del binario o build e metodo
   di rollback OTA/USB effettivamente disponibile.
4. **Build ripetibile:** ESPHome 2026.9.1 e segreti locali di test devono
   compilare tutti e tre i profili senza upload.

Se anche un solo punto manca, il lavoro si ferma all'inventario: non si
estrae codice e non si carica una cassa.

## Problema

Il firmware diretto è funzionale e ha già validato wake word locale, AFE/AEC,
VoIP, cattura PCM, TTS diretto e LED. Tuttavia la logica con maggiore rischio
operativo è concentrata in due punti:

- `esphome/galileo-va-direct-audio-cutover-base.yaml` contiene hardware,
  audio, VoIP, wake word, LED, callback e policy runtime;
- `components/galileo_audio_tap/galileo_audio_tap.cpp` contiene insieme
  socket UDP, formato pacchetti, cattura, endpoint detector, lifecycle TTS e
  dialogo sperimentale.

Questo rende costoso isolare regressioni e aumenta il rischio che una modifica
di dialogo, TTS o LED alteri wake word, VoIP o una cassa non coinvolta.

Inoltre il protocollo UDP corrente controlla una sessione condivisa, ma non ha
un MAC per datagramma né una protezione contro replay. È sufficiente solo per
la fase LAN fidata attuale; non deve essere presentato come protezione
crittografica dell'audio o dei comandi.

## Obiettivo

Rendere il firmware delle casse più manutenibile e verificabile, mantenendo il
comportamento operativo delle tre casse, e progettare una futura evoluzione
sicura del protocollo senza tagli incompatibili.

```text
profilo della cassa
  -> pacchetti YAML condivisi
  -> componenti runtime con responsabilità singola
  -> protocollo diretto versionato
  -> Galileo Core
```

Al termine della prima parte, una nuova cassa deve richiedere soltanto un
profilo di identità/capacità. Non deve duplicare logica di audio, LED, VoIP o
trasporto.

## Fuori ambito

- sostituire ESPHome, AFE/AEC, VoIP Stack o Home Assistant;
- attivare il dialogo senza wake word;
- cambiare wake word, soglie audio o qualità VoIP senza una prova dedicata;
- deploy simultaneo del Core e di tutte le casse;
- cifrare retroattivamente l'audio UDP v1;
- introdurre discovery Wi-Fi: resta soggetta alla Spec 017 del Galileo Core.

## Invarianti da preservare

- Taverna, Sala e Garage mantengono identità, porte, interno VoIP e sessione
  distinti;
- una wake word avvia al massimo una cattura; la cassa rimane silenziosa fino
  alla risposta o all'errore correlato;
- il TTS torna alla stessa cassa sorgente e non interrompe una chiamata VoIP;
- AFE/AEC, buffer TTS Garage da 250 ms, endpoint adattivo e limite di 4,5 s
  non cambiano nella fase di refactor;
- il dialogo senza wake rimane disabilitato in firmware e Core;
- segreti Wi-Fi, API, OTA e sessioni non entrano nel repository né nei log;
- una cassa che non riconosce un messaggio nuovo lo ignora senza aprire audio
  o riprodurre TTS.

## Architettura target

### Profili delle casse

Ogni file di cassa contiene solo:

- nome e nome visualizzato;
- IP o DHCP, interno e gruppi VoIP;
- host/porte dirette, `satellite_id` e capability;
- riferimenti a segreti locali;
- eventuali differenze fisiche esplicitamente documentate, come AFE/AEC e
  buffering Garage.

Non contiene callback audio, logica LED, parser di pacchetti o workaround TTS.

### Pacchetti YAML

Il base viene diviso per responsabilità, senza cambiare i componenti ESPHome
usati:

```text
packages/
  board/             pinout, codec, PSRAM, rete
  audio/             AFE, mixer, speaker e microfono
  voice/             micro-wake-word e cattura post-wake
  voip/              codec, chiamate, gruppi e tasti
  presentation/      LED e bip locali proiettati dallo stato
  direct_runtime/    binding del tap, callback e capability
```

Ogni pacchetto espone ID e eventi già documentati; non può invocare ID di un
altro pacchetto se non tramite un evento nominato nel contratto runtime.

### Componenti C++

`galileo_audio_tap` viene separato gradualmente, senza modificare inizialmente
il wire format v1:

```text
direct_transport      socket, frame, sessione, invio/ricezione
capture_controller    OPEN/CLOSE, PCM, endpoint e contatori
tts_lifecycle         avvio, idle guard, timeout e tts_finished
dialogue_experiment   finestra VAD, compilata ma non inclusa nei profili normali
```

Il transport non conosce LED, player o soglie VAD. Il controller cattura non
conosce URL TTS. Il dialogo sperimentale non è linkato nel profilo operativo
finché non avrà una validazione autonoma.

### Macchina a stati

Lo stato logico deve essere unico e osservabile:

```text
IDLE
  -> CAPTURING       wake word o tasto autorizzato
  -> WAITING_REPLY   CLOSE inviato
  -> SPEAKING        TTS valido ricevuto
  -> IDLE            TTS terminato, errore o timeout

IDLE/CAPTURING/WAITING_REPLY/SPEAKING
  -> IN_CALL         chiamata VoIP prevale quando supportato
IN_CALL
  -> IDLE            chiamata conclusa
```

Le sole transizioni che possono aprire il microfono sono `IDLE -> CAPTURING`
da wake word o input fisico autorizzato. Ogni transizione registra solo stato,
motivo, `turn_id`/`response_id` troncato e contatori, mai PCM o transcript.

## Evoluzione sicura del protocollo

### Fase A — refactor compatibile

Il protocollo `GLA1` resta identico. Questa fase non modifica dimensioni
pacchetto, porte, session ID o Core: riduce esclusivamente l'accoppiamento del
firmware.

### Fase B — protocollo v2 coordinato

Solo dopo l'accettazione della Fase A si scrive una spec gemella nel Core e si
introduce un protocollo versionato. `GLA2` deve contenere:

- `satellite_id` o fingerprint assegnata;
- boot nonce casuale e contatore monotono per direzione;
- tipo, lunghezza e payload con limiti fissi;
- tag HMAC-SHA-256 troncato, calcolato sull'intero header e payload;
- finestra anti-replay e rifiuto di pacchetti fuori sequenza;
- chiave per cassa diversa dalla sessione v1, conservata solo nei segreti
  locali e ruotabile.

La v2 protegge autenticità e integrità dei datagrammi; non rende confidenziale
il PCM. La cifratura del flusso audio richiede una decisione separata su DTLS,
tunnel locale o trasporto affidabile, con benchmark di CPU e latenza.

La migrazione è dual-stack: Core e firmware accettano v1 e v2 per una sola
cassa pilota; v1 resta l'autorità per Sala e Taverna finché ogni migrazione
non ha rollback verificato. Non esiste downgrade automatico dopo che una
cassa è marcata v2 attiva.

## Piano di esecuzione

### 1. Inventario e golden

1. Chiudere il gate di ingresso e creare il report baseline.
2. Annotare versione ESPHome, SHA delle dipendenze, profilo, hash OTA e stato
   Core di Taverna, Sala e Garage.
3. Conservare un binario golden e il suo metodo di flash/OTA per ogni board.
4. Creare una matrice profilo/capability; nessun profilo può usare valori
   impliciti della cassa Taverna.

### 2. Estrarre i pacchetti YAML

1. Estrarre un pacchetto alla volta, senza cambiare chiavi, ID, ordini di
   callback o valori audio.
2. Compilare tutti i profili dopo ogni estrazione.
3. Confrontare la configurazione ESPHome risolta e l'uso memoria con il golden.

### 3. Estrarre il runtime C++

1. Introdurre test del parser e frame v1 prima di spostare codice.
2. Estrarre `direct_transport`, mantenendo API e pacchetti invariati.
3. Estrarre controller cattura e lifecycle TTS.
4. Collegare LED e bip esclusivamente agli eventi della macchina a stati.
5. Spostare il dialogo in pacchetto sperimentale escluso dai profili normali.

### 4. Pilot controllato

1. Compilare e caricare solo Garage, con Taverna e Sala immutate.
2. Fare test presidiati e rollback immediato al primo errore bloccante.
3. Lasciare Garage in osservazione almeno 24 ore e ripetere i test dopo un
   reboot Wi-Fi/ESPHome.
4. Solo con esito stabile portare lo stesso candidato su Sala, poi Taverna.

### 5. Progettare v2 separatamente

Non iniziare v2 nello stesso commit della modularità. Richiede protocol spec,
test cross-repository, rotazione chiavi, migration flag e un nuovo pilot.

## Test richiesti

### Automatici, a ogni modifica

- compilazione ESPHome dei profili Taverna, Sala e Garage con segreti locali
  di test, senza upload;
- validazione che ogni profilo risolva un nome, `source`, interno, porte e
  sessione distinti;
- test host-side del parser `GLA1`: header corto, magic/versione errati,
  payload oltre limite, sessione errata, URL non HTTP, response ID non valido;
- test deterministici della macchina a stati: wake, close, TTS, timeout,
  errore, chiamata VoIP e ritorno a idle;
- test di regressione TTS: idle immediato, player occupato, callback idle
  ritardata, timeout di 30 s e una sola emissione `tts_finished`;
- controllo che `direct_dialogue_enabled` resti `false` nei tre profili di
  produzione.

Comandi indicativi, da eseguire solo con ambiente ESPHome e `secrets.yaml`
locale disponibili:

```bash
esphome compile esphome/galileo-va-direct-audio-cutover.yaml
esphome compile esphome/galileo-sala.yaml
esphome compile esphome/galileo-garage-hybrid.yaml
```

I test host-side devono compilare le funzioni pure fuori da ESPHome; socket,
microfono e media player sono adapter finti. Nessun test trasmette PCM reale o
usa una sessione di produzione.

### Test manuali sul pilot Garage

| Caso | Esito atteso |
|---|---|
| Avvio e reconnect Wi-Fi | API/OTA disponibili, LED idle, nessuna cattura spontanea |
| Wake + comando domotico | una cattura, una risposta e LED torna idle |
| Wake + LLM | PCM, TTS e `tts_finished` correlati alla stessa risposta |
| Silenzio, radio e rumore | nessuna cattura prolungata oltre 4,5 s |
| TTS lungo | risposta udibile completa, nessun blocco o doppio `tts_finished` |
| Chiamata VoIP entrante/uscente | suoneria, risposta, chiusura e audio invariati |
| Wake durante VoIP | comportamento definito, nessuna sovrapposizione audio o crash |
| Reboot durante cattura/TTS | boot pulito e ritorno a idle |
| Core non raggiungibile | timeout visibile, LED d'errore limitato, nessun loop di cattura |
| Dialogo senza wake | non avvia alcuna seconda cattura |

Per ogni caso registrare solo esito, versione firmware, hash candidato,
timestamp e contatori sanitizzati. Audio, transcript, URL asset e segreti non
vanno archiviati nel repository.

## Precauzioni di deploy

1. Un solo satellite candidato alla volta; Garage è il primo.
2. Non aggiornare Core, firmware e dipendenze esterne nella stessa finestra.
3. Prima dell'OTA verificare: alimentazione stabile, Wi-Fi raggiungibile,
   chiamate VoIP inattive, golden disponibile e accesso USB fisico possibile.
4. Usare OTA assistito: un operatore ascolta wake, TTS e VoIP durante il test.
5. Interrompere e fare rollback se compaiono reset, perdita API, TTS muto,
   audio VoIP degradato, cattura spontanea, loop di LED o pacchetti rifiutati
   senza causa diagnosticabile.
6. Non registrare o pubblicare session ID, chiavi v2, indirizzi URL firmati,
   audio o transcript nei report.
7. Non abilitare `direct_dialogue_enabled` per verificare il refactor.

## Criteri di accettazione Fase A

- tre profili compilano con le dipendenze pin-nate;
- il gate di ingresso è chiuso e il report baseline è versionato senza
  segreti;
- Garage completa tutti i test manuali senza regressioni per 24 ore;
- almeno 30 turni wake → risposta, 10 TTS lunghi e 10 eventi VoIP completano
  senza reset, doppio lifecycle o risposta alla cassa sbagliata;
- Taverna e Sala mantengono il golden fino al loro pilot individuale;
- una nuova identità di cassa può essere descritta senza copiare callback o
  codice runtime;
- test automatici coprono parser, stati e lifecycle prima della migrazione
  dell'ultima cassa;
- non cambia il contratto GLA1 con Galileo Core.

## Rollback

Il rollback di ogni fase è locale al satellite candidato:

1. fermare l'OTA e non aggiornare altre casse;
2. ricaricare il golden della stessa board via OTA o USB;
3. riportare il Core al comportamento GLA1 già attivo, senza modifiche ai
   registry delle altre casse;
4. salvare un report sanitizzato con versione, hash e caso di fallimento;
5. riprendere solo dopo riproduzione in test host-side o su board di banco.

Il rollback non richiede di disabilitare AEC, VoIP, Home Assistant o le casse
non candidate.
