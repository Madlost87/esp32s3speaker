# Developer Quick Training Guide

Guida rapida per produrre una wake word custom compatibile con il satellite ESP32-S3.

## Obiettivo

Produrre un modello **ESPHome micro_wake_word v2** per esecuzione locale su ESP32-S3.

Wake word consigliata:

```text
aiuto aiuto
```

Evitare `aiuto` singolo: e' troppo corto e comune, quindi piu' esposto a falsi positivi.

## Output Da Consegnare

Consegnare esattamente due file:

```text
aiuto_aiuto.json
aiuto_aiuto.tflite
```

Il file JSON deve essere un manifest ESPHome microWakeWord v2 e deve puntare al `.tflite` relativo:

```json
{
  "type": "micro",
  "wake_word": "aiuto aiuto",
  "author": "AUTHOR_NAME",
  "model": "aiuto_aiuto.tflite",
  "trained_languages": ["it"],
  "version": 2,
  "micro": {
    "probability_cutoff": 0.97,
    "feature_step_size": 10,
    "sliding_window_size": 5,
    "tensor_arena_size": 22860,
    "minimum_esphome_version": "2024.7.0"
  }
}
```

I valori `probability_cutoff`, `sliding_window_size` e `tensor_arena_size` possono cambiare, ma devono essere quelli realmente consigliati dal training/test.

## Vincoli Del Target

- Runtime finale: ESPHome `micro_wake_word`.
- Formato finale: JSON microWakeWord v2 + TensorFlow Lite Micro `.tflite`.
- Non consegnare solo modello openWakeWord server/Wyoming, ONNX o TFLite generico.
- Device: ESP32-S3, 240 MHz, 8 MB PSRAM, 16 MB flash.
- Microfono: ES7210 via I2S, ADC esterno, non PDM.
- Audio wake: mono, 16 kHz, 16 bit.
- Lingua/pronuncia: italiano.
- Uso reale: ambiente domestico/ufficio, parlato far-field, rumore di stanza.

Dettagli hardware completi: `DEVICE_AUDIO_TARGET.md`.
Versioni software: `SOFTWARE_VERSIONS.md`.
Esempio modello valido: `example_model/hey_jarvis.json` + `example_mod
el/hey_jarvis.tflite`.

## Dati Consigliati

Dataset positivo:

- frase: `aiuto aiuto`;
- molte voci diverse, almeno uomo/donna/accenti diversi;
- distanze diverse dal microfono: vicino, 1 metro, 3 metri;
- volumi diversi: normale, forte, concitato;
- registrazioni pulite e registrazioni con rumore domestico/ufficio.

Dataset negativo:

- parlato italiano normale senza wake word;
- frasi simili: `aiutami`, `aiuto`, `ciao`, `auto`, `hai tutto`, `aiuto per favore`;
- TV, musica, conversazioni, rumore cucina, passi, silenzio;
- audio ambientale lungo per stimare falsi positivi per ora.

Audio reale dal device:

- se possibile, raccogliere qualche minuto dalla board target nello stesso ambiente d'uso;
- includere rumore reale, voce da stanza, voce laterale e voce lontana;
- usare questo materiale almeno per test/validazione, anche se il training usa campioni sintetici.

## Training

Usare il progetto microWakeWord:

```text
https://github.com/OHF-Voice/micro-wake-word
```

Il training puo' partire dal notebook/procedura base del progetto, ma serve tuning: un modello che compila non e' automaticamente usabile.

Punti da verificare:

- modello quantizzato compatibile TensorFlow Lite Micro;
- manifest JSON versione 2;
- `feature_step_size` coerente con microWakeWord/ESPHome;
- stima falsi positivi su audio ambientale;
- recall della frase `aiuto aiuto` con voci non viste;
- dimensione e `tensor_arena_size` adatti a ESP32-S3.

## Criteri Minimi Di Accettazione

Prima della consegna, verificare almeno:

- nessun falso positivo evidente su audio ambiente lungo;
- riconoscimento affidabile di `aiuto aiuto` da piu' voci;
- bassa sensibilita' a `aiuto` singolo;
- nessuna attivazione frequente con TV/conversazioni;
- file JSON valido e `.tflite` referenziato correttamente;
- note scritte su soglia consigliata e compromesso falsi positivi/falsi negativi.

## Consegna

Consegnare:

```text
aiuto_aiuto.json
aiuto_aiuto.tflite
README_TEST.md
```

`README_TEST.md` deve indicare:

- dataset usato a grandi linee;
- soglia consigliata;
- falsi positivi osservati;
- falsi negativi osservati;
- eventuali limiti noti;
- versione/commit del tool microWakeWord usato.

## Test Sul Nostro Sistema

Il primo test lato firmware sara' solo compilazione ESPHome, senza flash.

Poi, se la compilazione passa, il modello verra' provato in modo reversibile affiancandolo ai modelli attuali (`okay_nabu` / `hey_jarvis`) o sostituendone uno temporaneamente.

Non modificare firmware o YAML nel pacchetto di consegna: bastano i file del modello e le note di test.
