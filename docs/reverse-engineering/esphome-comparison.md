# Confronto Firmware Originale vs ESPHome

## Baseline ESPHome

Firmware operativo attuale:

```text
esphome/galileo-va-afe.yaml
```

Profilo storico/fallback:

```text
esphome/galileo-va.yaml
```

## Tabella Funzionale

| Funzione | Firmware originale | ESPHome attuale | Stato |
| --- | --- | --- | --- |
| ES7210 input | Confermato | Presente | Coperto |
| ES8311 output | Confermato | Presente | Coperto |
| I2S/TDM | Confermato | Presente | Coperto |
| Due microfoni | Probabile/confermato da log | Presente slot `[0,2]` | Coperto |
| Playback reference AEC | Probabile | Presente slot `1` | Coperto meglio di ESPHome stock |
| AEC | Presente da stringhe AFE | Presente `esp_afe` | Coperto |
| Noise suppression | Presente WebRTC/NSNET | Presente `ns_enabled` | Coperto |
| VAD | Presente `vadnet` | Presente `vad_enabled` e MWW VAD | Coperto, ma diverso |
| Speech enhancement/BSS | Presente | Presente `se_enabled` | Coperto |
| AGC | Presente | Disabilitato nel profilo stabile | Parziale |
| WakeNet | Presente | Non presente | Non coperto |
| microWakeWord | Non originale | Presente | Alternativa |
| Modelli Xiaozhi | Presenti in `model` | Non usati | Non coperto |
| MQTT | Presente | Non usato | Sostituito |
| WebSocket | Presente | Non usato | Sostituito |
| Captive portal | Presente | Non usato | Mancante/non necessario |
| HTTPS OTA Xiaozhi | Presente | ESPHome OTA | Sostituito |
| Opus network audio | Presente | VoIP/Media diversi | Parziale |
| Display/LVGL | Presente nel firmware | Non usato | Mancante |
| Camera | Tentata dal firmware | Non usata | Mancante/non necessaria |
| LED ring | Probabile | Presente GPIO38 | Coperto |
| TCA9555 buttons | Probabile | Presente | Coperto |
| microSD | Sconosciuto | Non usato | Sconosciuto/mancante |

## Cosa ESPHome Fa Gia' Bene

### Confermato

- Usa la stessa famiglia hardware: ESP32-S3 + ES7210 + ES8311.
- Usa 48 kHz TDM e reference per AEC.
- Usa due microfoni fisici.
- Ha una pipeline AFE piu' vicina al firmware factory rispetto al primo profilo
  stock.
- Integra Assist, media player, VoIP e LED runtime.

## Gap Tecnici

### AGC

Il firmware originale contiene AGC WakeNet/WebRTC. Nel profilo stabile:

```yaml
agc_enabled: false
```

Esistono overlay sperimentali:

```text
esphome/galileo-va-afe-agc-test.yaml
esphome/galileo-va-afe-agc-lite.yaml
```

Valutazione:

- miglioramento possibile per wake/STT a distanza;
- rischio di stutter TTS/media e instabilita' AFE, gia' annotato nel YAML.

### Wake Word

Il firmware originale usa WakeNet, ESPHome usa microWakeWord.

Valutazione:

- microWakeWord e' piu' naturale per ESPHome;
- WakeNet originale puo' essere studiato ma non e' automaticamente riusabile.

### Display/Camera

Il firmware originale contiene supporto display/camera, ma la nostra cassa e'
usata come satellite vocale.

Valutazione:

- bassa priorita' operativa;
- utile solo se la board fisica ha display o camera popolati.

### Networking

Il firmware originale ha MQTT/WebSocket/captive portal e OTA cloud. ESPHome usa
Home Assistant API/OTA.

Valutazione:

- non conviene replicare Xiaozhi;
- conviene studiare solo eventuali scelte audio/latency.

## Rischi Di Miglioramento

- Cambiare AGC o AEC puo' peggiorare barge-in e TTS.
- Usare modelli non nativi ESPHome puo' rompere aggiornabilita'.
- Decompilazione senza simboli puo' produrre interpretazioni fragili.
- Modelli nella partizione `model` possono avere licenze/formati non riusabili.
