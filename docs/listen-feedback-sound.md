# Listen Feedback Sound

## Obiettivo

Aggiungere un feedback locale, configurabile per singola cassa ESPHome, quando
il satellite vocale entra in ascolto dopo la wake word.

La feature distingue solo due comportamenti:

- solo LED;
- LED + suono breve locale.

Il TTS non fa parte di questa prima feature.

## Perche' Sta Nel Firmware

Il feedback di ascolto e' temporale e locale:

```text
wake word rilevata -> Assist entra in listening -> LED ascolto -> eventuale bip
```

Non deve dipendere da `galileo-core` o TTS. Il segnale deve pero' indicare solo
lo stato realmente utile: se la wake word viene rilevata ma Assist non entra in
`listening`, la cassa non deve illuminarsi come pronta e non deve suonare.

## Configurazione

Ogni satellite espone uno switch Home Assistant:

```text
Listen Feedback Sound
```

Stati:

- `on`: quando la cassa entra in ascolto, il firmware riproduce un bip breve;
- `off`: nessun audio, resta solo il LED/stato visivo.

Lo switch e' locale al device, salvato dal firmware, e non dipende dal comando
domotico pronunciato.

## Profilo Target

Prima implementazione:

```text
esphome/galileo-va-afe.yaml
```

Questo e' il profilo full AFE stabile usato dal satellite taverna.

## Comportamento Runtime

Quando il runtime controller risolve `va_state: listening`:

1. il ring LED mostra lo stato `listening`;
2. se `Listen Feedback Sound` e' attivo e lo speaker non e' in mute, parte un
   bip PCM locale breve;
3. se lo switch e' disattivato, non viene riprodotto nulla.

Lo stato `wake` resta visivamente spento: non deve comunicare "puoi parlare"
prima che il satellite sia davvero in ascolto.

Il suono non e' una frase, non usa Piper, non usa Home Assistant TTS e non passa
da `galileo-core`.

## Fuori Scope Per La Prima Versione

Questa prima versione copre solo il momento in cui il satellite entra in
ascolto. Non decide ancora come confermare un comando eseguito, perche' quel
risultato nasce dopo l'intent, dentro Home Assistant / `galileo-core`.

## Vincoli

- Non cambiare modelli wake word.
- Non cambiare AFE, AEC, slot TDM, pin, VoIP o media pipeline.
- Non aggiungere TTS locale.
- Non bloccare l'avvio di Assist se il bip non puo' essere riprodotto.
- Rispettare `Speaker Mute`: se lo speaker e' muto, niente bip.

## Test

1. Compilare il firmware.
2. Flashare solo se la compilazione passa.
3. In Home Assistant verificare lo switch `Listen Feedback Sound`.
4. Con switch ON:
   - dire la wake word;
   - verificare LED ascolto;
   - verificare bip breve;
   - completare un comando Assist.
5. Con switch OFF:
   - dire la wake word;
   - verificare LED ascolto;
   - verificare assenza del bip;
   - completare un comando Assist.
6. Con `Speaker Mute` ON:
   - verificare che il bip non venga riprodotto.

## Regola Di Aggancio

Il bip non e' agganciato direttamente alla wake word. Viene eseguito come
azione della policy runtime `va_state` quando il valore diventa `listening`.
Questo mantiene lo stesso significato tra LED e suono:

```text
nessun listening -> nessun LED ascolto -> nessun bip
listening reale -> LED ascolto -> eventuale bip
```

L'AFE/AEC dovrebbe gestire il suono locale come playback reference, ma il test
reale deve continuare a verificare che il bip non degradi la prima parola
pronunciata subito dopo la wake word.

## Future: Feedback Di Comando Eseguito

Serve una seconda feature, separata dal feedback di ascolto, per confermare che
un comando operativo e' stato eseguito.

Esempi:

```text
accendi luce cucina       -> esegue, poi feedback breve
apri cancelletto          -> se autorizzato, esegue, poi feedback breve
spegni luce taverna       -> esegue, poi feedback breve
```

La regola desiderata e':

- se l'utente chiede di eseguire qualcosa, il satellite puo' confermare con un
  beep oppure con una frase breve, in base alla configurazione;
- se l'utente chiede una informazione, una domanda o uno stato, il satellite
  deve rispondere parlando normalmente;
- se il comando richiede sicurezza, conferma, parola segreta, o fallisce, il
  satellite deve parlare: un solo beep non basta a spiegare cosa serve.

Esempi di distinzione:

```text
accendi luce cucina
-> comando operativo
-> feedback configurabile: beep oppure "Fatto"

stato cancelletto
-> richiesta di informazione
-> risposta parlata: "Il cancelletto risulta chiuso."

che ore sono?
-> domanda
-> risposta parlata normale

apri cancelletto
-> comando rischioso
-> se manca autorizzazione, risposta parlata: "Serve la parola di sicurezza."
```

### Configurazione Futuro

La configurazione deve essere per device/satellite, non per singolo comando.

Possibile forma:

```json
{
  "command_done_feedback": {
    "enabled": true,
    "mode": "beep"
  }
}
```

Modalita' previste:

- `beep`: solo suono breve quando un comando viene eseguito correttamente;
- `speech`: frase breve, per esempio `Fatto`;
- `off`: nessuna conferma extra, salvo risposte necessarie per errori,
  sicurezza o domande.

### Dove Implementarla

Questa feature non deve stare solo nel firmware, perche' la cassa non sa se un
comando domotico e' riuscito davvero.

Responsabilita' proposta:

- firmware ESPHome: riprodurre un eventuale beep locale quando gli viene chiesto;
- `galileo-core` / Home Assistant intent: decidere se l'intent era comando,
  domanda, lettura stato, errore o sicurezza;
- policy per-device: scegliere `beep`, `speech` o `off` per i comandi eseguiti.

### Vincoli Future

- Non sostituire le risposte informative con un beep.
- Non usare il beep per errori o richieste di sicurezza.
- Evitare doppie conferme: se Home Assistant sta gia' generando una risposta
  utile, non aggiungere anche un beep.
- Tenere separati:
  - feedback di ascolto;
  - feedback di comando eseguito;
  - risposta informativa;
  - errore/sicurezza.
