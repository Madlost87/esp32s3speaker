# Wake Word Models

Il profilo operativo `esphome/galileo-va-afe.yaml` usa ESPHome
`micro_wake_word` con modelli v2.

## Stato Attuale

Modelli caricati nel firmware:

- `alexa`
- `okay_nabu`
- `hey_jarvis`

Comportamento al boot:

```text
alexa      abilitata
okay_nabu  abilitata
hey_jarvis caricata ma disabilitata
```

Questa e' la configurazione di test caricata il 2026-10-09 per provare
`Alexa` insieme a `Okay Nabu`. Home Assistant puo' mostrare le tendine
`Wake word` come `No wake word`, ma il firmware abilita direttamente i modelli
al boot.

Il default stabile precedente era `Okay Nabu + Hey Jarvis`, con `Alexa`
caricata ma disabilitata.

## Perche' La UI Puo' Essere Asincrona

Nel profilo AFE il firmware forza lo stato dei modelli con:

```cpp
id(alexa).enable();
id(okay_nabu).enable();
id(hey_jarvis).disable();
```

La UI di Home Assistant espone controlli generati dal componente, ma oggi non e'
la fonte di verita' per la combinazione attiva. La fonte di verita' operativa e'
il firmware ESPHome.

## Profili Di Test

Per testare Alexa senza cambiare architettura, modificare solo il blocco
`on_boot`.

Default stabile:

```cpp
id(alexa).disable();
id(okay_nabu).enable();
id(hey_jarvis).enable();
```

Test Alexa + Nabu:

```cpp
id(alexa).enable();
id(okay_nabu).enable();
id(hey_jarvis).disable();
```

Test Alexa + Jarvis:

```cpp
id(alexa).enable();
id(okay_nabu).disable();
id(hey_jarvis).enable();
```

Test solo Alexa:

```cpp
id(alexa).enable();
id(okay_nabu).disable();
id(hey_jarvis).disable();
```

## Procedura Sicura

1. Compilare senza flash.
2. Flashare solo se la compilazione passa.
3. Testare wake word vicina e lontana.
4. Controllare falsi positivi con TV/parlato normale.
5. Tornare al default stabile se Alexa crea falsi positivi o consuma troppa
   memoria.

Non affidare ancora la selezione delle combinazioni alle tendine Home Assistant:
prima va resa esplicita la sincronizzazione tra UI e stato reale dei modelli.
