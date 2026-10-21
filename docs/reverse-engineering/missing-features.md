# Missing Features

Questo documento elenca funzionalita' osservate o probabili nel firmware
originale che non sono presenti, sono parziali o sono sostituite nel firmware
ESPHome.

## Non Presenti O Non Riutilizzate

### WakeNet Originale Xiaozhi

Confermato nel firmware originale:

```text
WakeNet
wakenet9
wakenet9l
wakenet9s
wn9_nihaoxiaozhi_tts
```

Stato ESPHome:

- non usato;
- sostituito da `micro_wake_word`.

Possibile recupero:

- documentare i modelli;
- verificare compatibilita' con ESP-SR custom component;
- bassa priorita' finche' microWakeWord funziona.

### Modelli Della Partizione `model`

Confermato:

```text
model partition offset 0x010000 size 0x0f0000
```

Stato ESPHome:

- non usata.

Possibile recupero:

- estrazione read-only in `/tmp`;
- catalogo dei modelli;
- confronto con ESP-SR target model layout.

### Display/LVGL

Confermato nel firmware originale:

```text
LVGL
esp_lcd_jd9853.c
Display
MipiLcdDisplay
SpiLcdDisplay
```

Stato ESPHome:

- non usato.

Possibile recupero:

- solo se la board fisica ha display popolato;
- richiede mappa pin display.

### Camera

Confermato:

- firmware originale tenta inizializzazione camera;
- boot log indica camera non supportata o assente.

Stato ESPHome:

- non usata.

Priorita':

- bassa, salvo scoperta hardware fisica.

### Captive Portal Xiaozhi

Confermato:

```text
http://192.168.4.1
Xiaozhi-B819
saved Wi-Fi list
advanced config
ota_url
remember_bssid
```

Stato ESPHome:

- sostituito da provisioning/configurazione ESPHome.

Priorita':

- bassa.

### MQTT/WebSocket Xiaozhi

Confermato:

```text
MQTT
WebSocket
audio packet encryption/decryption
```

Stato ESPHome:

- sostituito da Home Assistant API e VoIP stack.

Possibile recupero:

- solo come riferimento per architettura audio/rete.

## Parziali

### AGC

Firmware originale:

```text
AGC(WakeNet)
AGC(WebRTC)
digital_agc.c
```

ESPHome:

```text
agc_enabled: false
```

Overlay sperimentali presenti ma non baseline:

```text
galileo-va-afe-agc-test.yaml
galileo-va-afe-agc-lite.yaml
```

Possibile miglioramento:

- test controllato su wake word distante;
- misurare falsi positivi, latenza, stutter TTS, barge-in.

### Opus E Audio Di Rete

Firmware originale:

```text
OpusEncoderWrapper
OpusDecoderWrapper
OpusResampler
```

ESPHome:

- VoIP e media pipeline diverse;
- non replica il protocollo Xiaozhi.

Possibile miglioramento:

- confrontare frame size e sample rate solo se emergono problemi VoIP.

## Sconosciute

- Uso microSD.
- Gestione Bluetooth applicativa.
- Parametri esatti AFE runtime.
- Pin display/camera.
- Mappa funzioni C++ senza Ghidra.
