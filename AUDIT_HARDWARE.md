# Audit hardware e firmware - Waveshare ESP32-S3-AUDIO-Board

Data: 2026-10-08

Stato operativo al momento dell'audit: firmware attivo `galileo-va-afe.yaml`, compilato con ESPHome 2026.9.1, caricato OTA e confermato avviato. La variante `galileo-va-afe-assist.yaml` e' stata rimossa dal ramo principale perche' avviava hardware audio e VAD ma non ripristinava correttamente il runtime voce.

## Fonti

Fonti primarie usate o da mantenere come riferimento:

| Fonte | URL / path | Uso |
| --- | --- | --- |
| Waveshare ESP32-S3-AUDIO-Board docs | https://docs.waveshare.com/ESP32-S3-AUDIO-Board | Identita' board, componenti dichiarati, risorse |
| Waveshare ESP32-S3-AUDIO-Board wiki | https://www.waveshare.com/wiki/ESP32-S3-AUDIO-Board | Specifiche, demo, link a schematici |
| Schematico Waveshare v1.1 | https://files.waveshare.com/wiki/ESP32-S3-AUDIO-Board/ESP32-S3-AUDIO-Board_1.1.pdf | Pinout, codec, expander, alimentazione, periferiche |
| Espressif ESP32-S3 datasheet | https://www.espressif.com/sites/default/files/documentation/esp32-s3_datasheet_en.pdf | MCU, PSRAM, flash, periferiche |
| Espressif ESP32-S3 TRM | https://www.espressif.com/sites/default/files/documentation/esp32-s3_technical_reference_manual_en.pdf | I2S/TDM, DMA, periferiche |
| ESPHome ES7210 | https://esphome.io/components/audio_adc/es7210/ | Supporto ADC audio |
| ESPHome ES8311 | https://esphome.io/components/audio_dac/es8311 | Supporto DAC audio |
| ESPHome I2S audio | https://esphome.io/components/i2s_audio/ | Bus audio standard ESPHome |
| ESPHome microphone | https://esphome.io/components/microphone/ | Input audio |
| ESPHome speaker/media_player | https://esphome.io/components/speaker/ | Output audio e pipeline speaker |
| ESPHome micro_wake_word | https://esphome.io/components/micro_wake_word/ | Wake word locale, soglie modello |
| ESPHome voice_assistant | https://esphome.io/components/voice_assistant/ | Home Assistant Assist |
| Firmware originale backup | `../hardware/esp32-s3-audio/backups/esp32_s3_audio_factory_FULL.bin` | Evidenza firmware Xiaozhi |
| Stringhe firmware originale | `diagnostics/factory_strings_selected.txt` | Componenti, board id, audio stack |
| Diagnostica chip | `diagnostics/chip_info.txt` | ESP32-S3, flash, PSRAM |
| Partition table originale | `diagnostics/partition_table.csv` | Layout flash factory |

## Identificazione board

| Campo | Evidenza |
| --- | --- |
| Produttore | Waveshare |
| Modello | ESP32-S3-AUDIO-Board |
| Board id firmware originale | `waveshare-s3-audio-board` |
| Firmware originale osservato | `xiaozhi`, app version `1.8.9`, ESP-IDF `v5.4.1`, build `Aug 30 2025 11:02:12` |
| MCU | ESP32-S3, package QFN56, revision v0.2 |
| CPU | dual core, 240 MHz |
| Flash | 16 MB, manufacturer `0x20`, device `0x4018`, quad 3.3 V |
| PSRAM | 8 MB embedded PSRAM, configurata nel nostro firmware come octal 80 MHz |
| USB | USB Serial/JTAG, VID:PID `303a:1001` |
| Sicurezza flash | secure boot disabled, flash encryption disabled |

## Partizioni firmware originale

| Partizione | Offset | Size | Nota |
| --- | ---: | ---: | --- |
| `nvs` | `0x009000` | `0x004000` | configurazione |
| `otadata` | `0x00d000` | `0x002000` | OTA |
| `phy_init` | `0x00f000` | `0x001000` | radio |
| `model` | `0x010000` | `0x0f0000` | SPIFFS modelli/asset Xiaozhi |
| `ota_0` | `0x100000` | `0x600000` | app slot |
| `ota_1` | `0x700000` | `0x600000` | app slot |

Backup factory completo: `../hardware/esp32-s3-audio/backups/esp32_s3_audio_factory_FULL.bin`, SHA256 `d0b72eddaf4486a1bd25f4852f42d78dcd763c82e0bc0ffc3653991b317b75e8`.

## Inventario hardware

| Componente | Chip | Funzione | Bus | GPIO / EXIO | Supportato FW attuale | Utilizzato | Note |
| --- | --- | --- | --- | --- | --- | --- | --- |
| MCU | ESP32-S3R8 | CPU, Wi-Fi, BLE, USB, I2S, I2C | interno | USB native | Si | Si | 240 MHz, 8 MB PSRAM embedded |
| Flash | SPI NOR 16 MB | firmware e dati | SPI flash | interno | Si | Si | rilevata da esptool |
| PSRAM | embedded 8 MB | buffer audio, stack, asset | OPI PSRAM | interno | Si | Si | `psram: mode octal, speed 80MHz` |
| Audio ADC | ES7210 | ingressi microfonici | I2C + I2S/TDM | I2C `0x40`; DIN GPIO15 | Si | Si | firmware attuale usa TDM 4 slot, mic slots 0 e 2 |
| Audio DAC | ES8311 | uscita speaker | I2C + I2S | I2C `0x18`; DOUT GPIO16 | Si | Si | `use_mclk: true`, `no_dac_ref: true` |
| Amplificatore | NS4150 | speaker mono 3 W | analogico + enable | TCA9555 EXIO8 | Si | Si | enable gestito da switch GPIO expander |
| Microfono fisico destro | via ES7210 | input voce | TDM | slot 0 | Si | Si | mapping empirico nel YAML |
| Microfono fisico sinistro | via ES7210 | input voce | TDM | slot 2 | Si | Si | mapping empirico nel YAML |
| Playback reference | ES7210/ES8311 feedback | riferimento AEC | TDM | slot 1 | Si | Si | usato da `use_tdm_reference: true` |
| Slot TDM 3 | ES7210 | canale non utile/near silent | TDM | slot 3 | Parziale | No | osservato come quasi silente |
| I2S/TDM MCLK | ESP32-S3 | master clock codec | I2S | GPIO12 | Si | Si | condiviso ADC/DAC |
| I2S/TDM BCLK | ESP32-S3 | bit clock | I2S | GPIO13 | Si | Si | condiviso |
| I2S/TDM LRCLK | ESP32-S3 | word/select clock | I2S | GPIO14 | Si | Si | condiviso |
| I2S DIN | ESP32-S3 | ingresso ADC -> ESP32 | I2S | GPIO15 | Si | Si | ES7210 |
| I2S DOUT | ESP32-S3 | uscita ESP32 -> DAC | I2S | GPIO16 | Si | Si | ES8311 |
| I2C bus | ESP32-S3 | controllo codec/expander | I2C | SDA GPIO11, SCL GPIO10 | Si | Si | scan disabilitato |
| IO expander | TCA9555 | amp enable, pulsanti | I2C | address `0x20` | Si | Si | EXIO8-11 usati |
| BOOT button | GPIO0 | controllo utente | GPIO | GPIO0 | Si | Si | single/double/long click |
| Key 1 | TCA9555 | VoIP call toggle | I2C expander | EXIO9 | Si | Si | internal entity |
| Key 2 | TCA9555 | next contact | I2C expander | EXIO10 | Si | Si | internal entity |
| Key 3 | TCA9555 | decline/prev contact | I2C expander | EXIO11 | Si | Si | internal entity |
| LED ring | WS2812 x7 | stato visivo | RMT/GPIO | GPIO38 | Si | Si | runtime controller preset ring |
| RTC | PCF85063 | real-time clock | I2C | address da schematico | Non nel YAML | No | presente sulla board, non necessario per satellite HA |
| microSD | slot TF | storage | SPI/SDMMC | da schematico | Non nel YAML | No | non usato da ESPHome attuale |
| Display | LCD Waveshare/JD9853 path nel factory | UI locale | SPI/RGB secondo board | da schematico | Non nel YAML | No | factory prova a inizializzare display/LVGL |
| Camera | connettore/probe factory | visione | camera peripheral | da schematico | Non nel YAML | No | factory falliva probe `ESP_ERR_NOT_SUPPORTED` |
| Batteria/carica | circuito board | alimentazione | power | connettore Li-ion | Non nel YAML | Parziale HW | nessuna telemetria nota nel YAML |

## Firmware originale

Evidenze affidabili dal backup/binario e dai boot log:

- nome app `xiaozhi`;
- board `waveshare-s3-audio-board`;
- Wi-Fi AP di provisioning `Xiaozhi-B819`;
- inizializzazione display/LVGL e tentativo camera;
- codec ES8311 ed ES7210;
- `BoxAudioCodec::CreateDuplexChannels`;
- `i2s_channel_init_std_mode(tx_handle_, ...)` per TX;
- `i2s_channel_init_tdm_mode(rx_handle_, ...)` per RX;
- ES7210 in slave mode e TDM mode;
- abilita `ES7210_INPUT_MIC1`, `MIC2`, `MIC3`, `MIC4`;
- componenti WakeNet, AFE wake word, VAD, WebRTC noise suppression, digital AGC, BSS/microphone array speech enhancement;
- codifica Opus e websocket/audio communication;
- partizione SPIFFS `model` per modelli.

Limite: non abbiamo sorgenti completi del firmware factory dentro il repository locale. Il binario e le stringhe consentono deduzioni forti sull'architettura audio, ma non ricostruiscono con certezza tutti i registri codec, gain e timing.

## ESPHome attuale

Profilo attivo: `../hardware/esp32-s3-audio/esphome/galileo-va-afe.yaml`.

Uso hardware audio:

- ES7210 + ES8311 attraverso external component `esp_audio_stack`;
- bus TDM 48 kHz con 4 slot;
- `tdm_mic_slots: [0, 2]`;
- `tdm_ref_slot: 1`;
- `use_tdm_reference: true`;
- gain ES7210 `24.0 dB`;
- output ES8311 con MCLK;
- speaker hardware `48000 Hz`, 16 bit;
- AFE produce output voce a 16 kHz per VA/MWW/VoIP;
- `esp_afe` in full-duplex `fd`, `high_perf`, `mic_num: 2`;
- AEC attivo, NS attivo, VAD continuo attivo, SE attivo;
- AGC disattivato per stabilita' perche' causava stutter su TTS/media in questo profilo;
- buffer e task stack audio/VoIP/AFE spostati in PSRAM dove possibile.

Uso software:

- Home Assistant API;
- runtime controller completo;
- micro wake word locale con `Okay Nabu` e `Hey Jarvis`;
- voice_assistant con `noise_suppression_level: 0`, `auto_gain: 0dBFS`, `volume_multiplier: 2.0`, per evitare doppio preprocessing sopra AFE;
- VoIP stack presente anche se non e' l'obiettivo primario: oggi e' una dipendenza funzionale del profilo stabile per runtime/controller/audio graph;
- LED ring e pulsanti via TCA9555.

Evidenze runtime recenti:

- `tdm: total_slots=4 mic=0 mic2=2 tx_slot=0 reference=hardware ref_slot=1`;
- `processor: present=YES enabled=YES`;
- `voip_stack: Configured: SIP=udp/5060 RTP=40000 audio=full_duplex`;
- `audio_stack.mic: Microphone started`;
- `Voice Detected` ON/OFF;
- `voice_assistant` si avvia; errore osservato `stt-no-text-recognized` indica tentativo Assist senza testo riconosciuto, non assenza di pipeline.

## Gap analysis

| Funzione | Hardware disponibile | FW originale | ESPHome attuale | Stato | Miglioramento possibile |
| --- | --- | --- | --- | --- | --- |
| Doppio microfono fisico | ES7210 + 2 mic utili | Si, TDM multi-input | Si, slot 0+2 | OK | Misure MIC1/MIC2 separate per conferma SNR |
| 4 ingressi ES7210 | ES7210 4 canali | abilita MIC1-4 | usa 2 mic + ref + slot 3 non utile | PARZIALE | Verificare fisicamente se slot 3 e' davvero non cablato |
| Playback reference AEC | reference TDM slot 1 | probabile/compatibile AFE | Si | OK | Test barge-in durante TTS |
| AEC | ESP-SR/AFE | Si | Si | OK | Confronto `fd_high_perf` vs `fd_low_cost` |
| Noise suppression | ESP-SR/WebRTC | Si | Si in AFE | OK | Misura SNR e intelligibilita' |
| AGC | firmware originale include digital AGC | Si | No nel full AFE stabile | PARZIALE | P2: provare AGC in profilo di test, rischio stutter |
| VAD | ESP-SR/AFE | Si | Si, continuo | OK | Log diagnostici piu' espliciti |
| Beamforming/BSS/SE | dual mic + ESP-SR | stringhe BSS/SE | `se_enabled: true` | PARZIALE | Verifica percettiva e metrica, non solo config |
| Barge-in | mic+ref+full duplex | probabile | architettura supporta | DA VERIFICARE | Test wake word mentre TTS/media suona |
| Wake word Nabu | MWW | factory usa WakeNet cinese/Xiaozhi | Si | OK osservato | Misurare detection rate |
| Wake word Jarvis | MWW | non factory | configurata ma non affidabile | CONFIGURATO MALE / DA TARARE | P0: soglia modello Jarvis |
| Speaker | ES8311 + NS4150 | Si | Si | OK | Test volume/clipping |
| Volume hardware | ES8311/amp | Si | master min dB e media player | PARZIALE | Taratura scala volume |
| Mute hardware amp | NS4150 enable | Si/probabile | Si, EXIO8 | OK | Verifica click/pop |
| LED ring | WS2812 | probabile UI factory | Si | OK | Stato wake/listen/speak piu' leggibile |
| Pulsanti | BOOT + TCA9555 | Si | Si | OK | Rimappare se VoIP non serve |
| Display | LCD/JD9853 | Si/tentato | No | NON UTILIZZATO | P4: inutile per satellite voce |
| Camera | connettore/probe | tentata ma fallisce | No | NON UTILIZZATO | P4: non prioritaria |
| RTC | PCF85063 | probabile | No | NON UTILIZZATO | P4: non utile con HA/NTP |
| microSD | slot board | non confermato | No | NON UTILIZZATO | P4: logging/audio capture locale |
| BLE | ESP32-S3 | chip supporta | No | NON UTILIZZATO | P4, evitare carico |
| PSRAM | 8 MB | Si | Si | OK | Continuare a spostare buffer non realtime |
| SPIFFS model partition factory | 960 KB | Si | No, layout ESPHome diverso | NON UTILIZZATO | Non necessario; MWW modelli inclusi in firmware |

## Lezione dalla variante Assist-only

La rimozione dello stack VoIP e del preset full runtime ha prodotto un firmware che:

- compilava;
- si avviava;
- inizializzava ES7210/ES8311, TDM, AFE e VAD;
- mostrava `Voice Detected`;
- pero' non ripristinava correttamente il comportamento wake/Assist completo.

Conclusione: oggi il profilo full AFE e' la base stabile. Una variante senza VoIP va ricostruita partendo dalle dipendenze reali del preset, non rimuovendo pacchetti a mano.

## Piano interventi

### P0 - Problemi importanti

| Intervento | Beneficio | Rischio | Difficolta' | RAM/PSRAM | CPU | Test |
| --- | --- | --- | --- | --- | --- | --- |
| Tarare `Hey Jarvis` con `probability_cutoff` piu' permissiva | Riduce falsi negativi Jarvis | Falsi positivi | Bassa | invariata | invariata | 20 ripetizioni a 0.5/1/2 m, confronto Nabu |
| Aggiungere logging wake word piu' esplicito | Capire quale modello scatta | Basso | Bassa | minima | minima | Pronuncia Nabu/Jarvis e verifica log |
| Verificare che entrambi i modelli siano abilitati dopo reboot | Evita regressione | Basso | Bassa | nulla | nulla | Log boot + HA entity |

### P1 - Hardware presente ma non sfruttato

| Intervento | Beneficio | Rischio | Difficolta' | RAM/PSRAM | CPU | Test |
| --- | --- | --- | --- | --- | --- | --- |
| Diagnostica MIC slot 0/2/3 e ref slot 1 | Conferma mapping reale | Medio se cambia audio graph | Media | buffer test | basso | RMS/clipping per slot |
| Esposizione diagnostica AFE/AEC mode | Debug remoto | Basso | Media | minima | minima | Switch mode idle e log |
| microSD per cattura WAV diagnostica | Misure reali offline | Medio | Media | buffer file | basso/medio | registrazione 10 s ambiente |

### P2 - Miglioramenti audio importanti

| Intervento | Beneficio | Rischio | Difficolta' | RAM/PSRAM | CPU | Test |
| --- | --- | --- | --- | --- | --- | --- |
| Test AGC AFE in profilo sperimentale | Migliora distanza wake/STT | Stutter TTS/media gia' osservato | Media | aumenta | medio | A/B con TTS e wake |
| Confronto `fd_high_perf` vs `fd_low_cost` | Qualita' vs CPU | basso | Bassa | invariata | varia | STT e barge-in |
| Taratura gain ES7210 | Migliore SNR senza clipping | clipping o bassa sensibilita' | Media | invariata | invariata | RMS/clipping a distanze |

### P3 - Ottimizzazioni

| Intervento | Beneficio | Rischio | Difficolta' | RAM/PSRAM | CPU | Test |
| --- | --- | --- | --- | --- | --- | --- |
| Ridurre log rumorosi dopo stabilizzazione | meno carico seriale/API | basso | Bassa | nulla | minima | uptime 24h |
| Profilo senza VoIP ricostruito con dipendenze minime corrette | meno RAM/socket | Medio, gia' fallito una volta | Alta | riduce | riduce | compilazione + wake/Assist + rollback pronto |
| Ottimizzare buffer speaker | riduce latenza barge-in | rischio underrun | Media | varia | varia | TTS lungo + wake |

### P4 - Esperimenti

| Intervento | Beneficio | Rischio | Difficolta' | RAM/PSRAM | CPU | Test |
| --- | --- | --- | --- | --- | --- | --- |
| Display LCD | UI locale | alto carico e irrilevante | Alta | alta | medio | rendering + audio simultaneo |
| Camera | funzioni visive | probabilmente non montata/supportata | Alta | alta | alto | probe hardware |
| BLE | presenza/provisioning | interferenze memoria/radio | Media | medio | medio | Wi-Fi + BLE stress |
| Wake word custom | Jarvis/trigger affidabili | training dataset | Alta | modello MWW | medio | benchmark dataset |

## Test audio consigliati

Per ogni firmware candidato:

| Test | Metodo | Metriche |
| --- | --- | --- |
| Wake word distanza | 20 frasi per wake word a 0.5, 1, 2, 3, 4 m | detection rate, false rejection, latenza |
| Falsi positivi | 30 min ambiente silenzioso + TV | attivazioni spurie/ora |
| Barge-in | TTS/media a volume 50/70/90%, dire wake word | detection rate con speaker attivo |
| STT | 10 comandi standard | testo riconosciuto, errori `stt-no-text-recognized` |
| Rumore | silenzio, TV, musica, parlato lontano | RMS, clipping, SNR se disponibile |
| Speaker | sweep volume con frase TTS | distorsione, clipping, drop |

## Stato finale concreto

### Hardware presente

ESP32-S3R8, 16 MB flash, 8 MB PSRAM, ES7210, ES8311, NS4150, TCA9555, due microfoni utili, reference TDM per AEC, WS2812 x7, BOOT, tre pulsanti expander, RTC PCF85063, microSD, display/camera path secondo board.

### Hardware che stavamo usando

Nel firmware full AFE attuale usiamo MCU, flash, PSRAM, ES7210, ES8311, NS4150, TCA9555, doppio microfono, reference hardware, I2C, I2S/TDM, LED ring, pulsanti.

### Hardware che non stavamo usando

RTC, microSD, display, camera, BLE, slot TDM 3 se fisicamente cablato, eventuale telemetria batteria se presente.

### Funzioni del firmware originale che avevamo perso

Nel profilo ESPHome stock precedente mancavano AFE full-duplex, reference hardware AEC, TDM factory-like, dual-mic AFE/SE, VAD continuo e audio graph simile al factory. Nel profilo full AFE attuale molte di queste sono recuperate.

### Miglioramenti implementati

Full AFE, doppio mic slot 0/2, reference slot 1, AEC, NS, VAD, SE, PSRAM per buffer/task, LED/pulsanti, wake word Nabu/Jarvis entrambe abilitate a boot, rollback del profilo Assist-only non funzionante.

### Miglioramenti ancora possibili

Taratura Jarvis, logging wake word, test quantitativi MIC/AEC/barge-in, AGC sperimentale, gain ES7210, diagnostica raw/processed, eventuale profilo no-VoIP ricostruito con metodo.

### Limiti di ESPHome

ESPHome standard non espone da solo tutta la catena factory ESP-SR/AFE/TDM/reference. Per il massimo hardware servono external components AFE/audio stack. La configurazione che compila non basta: serve verifica runtime per wake, VAD, Assist, TTS e barge-in.

### Prossimo step consigliato

P0: tarare solo `Hey Jarvis` nel profilo full AFE attivo, aggiungendo soglia per-modello e logging detection. Non cambiare audio stack, AFE, pin, buffer o VoIP nello stesso step.
