# Wake Word Models

I profili in produzione (base `esphome/galileo-va-direct-audio-cutover-base.yaml`, vedi `satellites.md`) usano ESPHome
`micro_wake_word` con modelli v2.

## Stato Attuale

Modelli caricati nel firmware:

- `alexa`
- `okay_nabu`
- `hey_jarvis`

Comportamento al boot:

```text
alexa      disabilitata
okay_nabu  abilitata
hey_jarvis disabilitata
```

Dalla 2026.11.7 l'unica parola di attivazione e' `Okay Nabu`. `Alexa` e
`Hey Jarvis` restano nel firmware, pronte: per riattivarne una basta
`enable()` in `on_boot` di `packages/satellite/wake_word.yaml` e una nuova
release. Home Assistant puo' mostrare le
tendine `Wake word` come `No wake word`, ma il firmware forza direttamente lo
stato dei tre modelli al boot.

## Perche' La UI Puo' Essere Asincrona

Nel profilo AFE il firmware forza lo stato dei modelli con:

```cpp
id(okay_nabu).enable();
id(alexa).disable();
id(hey_jarvis).disable();
```

La UI di Home Assistant espone controlli generati dal componente, ma oggi non e'
la fonte di verita' per la combinazione attiva. La fonte di verita' operativa e'
il firmware ESPHome.

## Procedura Sicura

1. Compilare senza flash.
2. Flashare solo se la compilazione passa.
3. Testare wake word vicina e lontana.
4. Controllare falsi positivi con TV/parlato normale.
5. Ripristinare il firmware precedente se emergono regressioni.

Non affidare ancora la selezione delle combinazioni alle tendine Home Assistant:
prima va resa esplicita la sincronizzazione tra UI e stato reale dei modelli.
