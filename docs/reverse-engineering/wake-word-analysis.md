# Wake Word Analysis

## Evidenze Nel Firmware Originale

### Confermato

La partizione `model` contiene stringhe:

```text
0x010004  wn9_nihaoxiaozhi_tts
0x010028  wn9_data
0x010050  wn9_index
0x010078  _MODEL_INFO_
0x0570b6  wakenet9l_tts1h8_
```

L'app `ota_0` contiene:

```text
AfeWakeWord
Failed to initialize wakenet model
Set WakeNet Model: %s
Set Second WakeNet Model: %s
WakeNet is not initialized
wakenet model not found. please load wakenet model...
wakenet is deactivated. vadnet model is used to select trigger channel.
wakenet is activated, disable WebRTC AGC.
```

Componenti WakeNet/VAD:

```text
wakenet9_quantized.c
wakenet9l_quantized.c
wakenet9s_quantized_mc.c
vadnet1_quantized.c
vadnet
nsnet
```

Stringhe modello osservate:

```text
vadnet1_mediumv1_Speech_1_0.5_0.1
wakeNet9_v1h24_Hi,ESP_3_0.63_0.635
```

## Interpretazione

### Confermato

- Il firmware originale integra WakeNet.
- Il firmware originale carica modelli da una partizione dedicata.
- Il firmware include VAD neural (`vadnet`) e noise suppression neural
  (`nsnet`).

### Probabile

- La wake word factory e' collegata a Xiaozhi, probabilmente
  `ni hao xiaozhi`.
- La stringa `wn9_nihaoxiaozhi_tts` indica un modello WakeNet 9 specifico.
- La pipeline usa VAD e WakeNet insieme per ridurre falsi positivi e selezionare
  il canale di trigger.

### Sconosciuto

- Soglia esatta della wake word.
- Numero di modelli attivi a runtime.
- Parametri di sensibilita'.
- Compatibilita' dei modelli WakeNet con ESPHome `micro_wake_word`.

## Confronto Con ESPHome

### Presente

Nel profilo stabile:

```yaml
micro_wake_word:
  models:
    - alexa.json
    - okay_nabu.json
    - hey_jarvis.json
```

Il profilo usa `mic_main`, cioe' l'uscita della pipeline audio/AFE.

### Differenze

- ESPHome `micro_wake_word` usa modelli JSON/TFLite del progetto ESPHome.
- Il firmware originale usa WakeNet/ESP-SR e modelli nella partizione `model`.
- I due formati non sono automaticamente intercambiabili.

### Possibili Miglioramenti

- Estrarre la partizione `model` in una directory temporanea e identificare i
  file/modelli.
- Documentare nome, dimensione e metadati di ogni modello.
- Verificare se esiste un modo supportato per usare modelli ESP-SR/WakeNet in
  componenti ESPHome custom.
- Continuare a preferire modelli microWakeWord per il profilo operativo se
  l'obiettivo e' mantenere aggiornabilita' ESPHome.
