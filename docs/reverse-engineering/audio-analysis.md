# Audio Analysis

## Catena Audio Originale

### Confermato

Il firmware originale contiene riferimenti a:

```text
AudioCodec
BoxAudioCodec
AudioService
opus_codec
ES7210
ES8311
Adev_Codec
i2s_channel_enable
i2s_channel_init_std_mode
i2s_channel_init_tdm_mode
```

Stringhe significative:

```text
BoxAudioCodec::CreateDuplexChannels(...)
i2s_new_channel(&chan_cfg, &tx_handle_, &rx_handle_)
i2s_channel_init_std_mode(tx_handle_, &std_cfg)
i2s_channel_init_tdm_mode(rx_handle_, &tdm_cfg)
Audio codec started
Duplex channels created
```

Il boot log documentato conferma:

```text
ES8311: Work in Slave mode
ES7210: Work in Slave mode
ES7210_INPUT_MIC1 enabled
ES7210_INPUT_MIC2 enabled
ES7210_INPUT_MIC3 enabled
ES7210_INPUT_MIC4 enabled
ES7210: Enable TDM mode
ES7210: Unmuted
Audio codec started
```

## AFE, DSP E Speech Processing

### Confermato

Il firmware originale contiene componenti ESP-SR/AFE:

```text
AfeAudioProcessor
esp_afe_sr_2mic.c
esp_afe_sr_1mic.c
AFE_CONFIG
afe_init_wn
afe_feed
afe_fetch_with_delay
afe_enable_aec
afe_enable_se
afe_enable_vad
afe_enable_ns
afe_print_pipeline
```

Stringhe pipeline:

```text
|AEC(%s)| ->
|VAD(%s)| ->
|AGC(WakeNet)| ->
|AGC(WebRTC)| ->
|WakeNet(%s,%s)| ->
|SE(BSS)| ->
AFE Pipeline: [input] -> %s%s%s%s%s%s[output]
```

### Componenti DSP Confermati Da Stringhe

```text
WebRTC
digital_agc.c
webrtc_ns.c
esp_ns.c
esp_bss_728.c
esp_bss_hps16fft.c
vad_filterbank.c
vad_sp.c
downsample_fast.c
```

### Probabile

- Il firmware originale usa AFE full-duplex o almeno una pipeline con reference
  playback per AEC.
- Il firmware e' costruito per due microfoni al massimo, come indicano le
  stringhe AFE:

```text
The AFE supports two microphone channels at the most.
The playback reference channel is 0, the AEC is deactivated.
```

Queste stringhe dimostrano la presenza della logica, non il valore effettivo di
configurazione runtime.

## Codec E Formati

### Confermato

Il firmware originale include Opus:

```text
OpusHead
OpusTags
OpusEncoderWrapper
OpusDecoderWrapper
OpusResampler
```

Include anche errori/log per cifratura audio:

```text
Failed to encrypt audio data
Failed to decrypt audio data
Invalid audio packet size
Invalid audio packet type
```

### Probabile

- Audio compresso con Opus per comunicazioni cloud o rete.
- Resampling interno tra rate diversi.

### Sconosciuto

- Sample rate effettivo di ogni stadio senza log runtime o decompilazione.
- Formato pacchetto audio esatto.
- Chiavi o schema di cifratura.

## Confronto Con ESPHome Attuale

### Presente Nel Nostro Profilo

`esphome/galileo-va-afe.yaml` implementa:

```text
ES7210 input
ES8311 output
48 kHz TDM capture
tdm_total_slots: 4
tdm_mic_slots: [0, 2]
tdm_ref_slot: 1
AEC enabled
NS enabled
VAD enabled
SE/BSS enabled
micro_wake_word
VoIP stack
```

### Differenze Note

- Il firmware originale sembra usare ESP-SR/WakeNet direttamente.
- ESPHome usa `micro_wake_word` con modelli ESPHome, non i modelli WakeNet
  originali.
- Il profilo stabile ESPHome ha `agc_enabled: false`, mentre il firmware
  originale contiene AGC WakeNet/WebRTC.
- Il firmware originale include MQTT/WebSocket/Opus cloud-style; ESPHome usa
  Home Assistant API, media player, Assist e VoIP.

## Limiti Attuali

- Nessuna decompilazione Ghidra ancora eseguita.
- Nessuna estrazione della partizione `model`.
- Nessuna conferma diretta dei parametri AFE runtime originali.
