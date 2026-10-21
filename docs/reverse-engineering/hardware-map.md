# Hardware Map

## Identita' Board

### Confermato

- MCU: ESP32-S3.
- Flash: 16 MB.
- PSRAM: 8 MB.
- USB: Espressif USB Serial/JTAG.
- Firmware factory board SKU: `waveshare-s3-audio-board`.

Evidenze:

- `hardware/esp32-s3-audio/docs/initial_board_audit.md`.
- `hardware/esp32-s3-audio/docs/compatibility_audit.md`.
- Stringa firmware: `waveshare-s3-audio-board`.

### Probabile

- Board commerciale diymore compatibile con Waveshare ESP32-S3-AUDIO-Board.
- Non e' dimostrato che sia una board Waveshare originale.

## GPIO E Bus

### Confermato Nel Nostro Firmware ESPHome

Il profilo attuale `esphome/galileo-va-afe.yaml` usa:

```text
I2C SDA   GPIO11
I2C SCL   GPIO10
I2S MCLK  GPIO12
I2S BCLK  GPIO13
I2S LRCLK GPIO14
I2S DIN   GPIO15
I2S DOUT  GPIO16
LED data  GPIO38
BOOT      GPIO0
```

Codec e periferiche I2C:

```text
ES8311   0x18
ES7210   0x40
TCA9555  0x20
```

### Probabile Nel Firmware Originale

Il firmware originale contiene il file path:

```text
./main/boards/waveshare-s3-audio-board/esp32-s3-audio_board.cc
```

e inizializza:

```text
ES7210
ES8311
i2c_new_master_bus
i2s_new_channel
i2s_channel_init_std_mode
i2s_channel_init_tdm_mode
esp_io_expander_new_i2c_tca95xx_16bit
```

Questo rende probabile che usi lo stesso bus hardware della famiglia
Waveshare, ma la conferma puntuale dei GPIO nel binario richiede decompilazione.

### Sconosciuto

- Valori esatti passati dal firmware originale alle strutture GPIO/I2C/I2S.
- Eventuali GPIO per display, camera, microSD e backlight.
- Eventuali differenze tra board diymore e reference Waveshare.

## Periferiche

### Audio

Confermato da boot log/stringhe:

```text
ES7210 ADC
ES8311 DAC
I2S/TDM
BoxAudioCodec
```

Probabile:

- Amplificatore NS4150 controllato tramite TCA9555 EXIO 8, come nel nostro
  profilo ESPHome.

### LED

Probabile:

- Ring WS2812 a 7 LED su GPIO38.

Evidenza:

- Profilo ESPHome attuale.
- Documentazione Waveshare.

Sconosciuto:

- Se il firmware originale usa lo stesso LED ring e con quali effetti.

### Pulsanti

Probabile nel nostro profilo:

```text
TCA9555 channel 9   Key1 / volume down
TCA9555 channel 10  Key2 / play-pause
TCA9555 channel 11  Key3 / volume up
GPIO0               BOOT button
```

Sconosciuto:

- Mappatura completa nel firmware originale senza decompilazione.

### Display E Camera

Confermato nel firmware originale:

- stringhe LVGL/display;
- path `esp_lcd_jd9853.c`;
- inizializzazione camera tentata;
- boot log con camera non supportata o non presente.

Sconosciuto:

- Display effettivamente popolato sulla board fisica.
- Camera effettivamente presente.
- Pin esatti per display/camera sulla board in uso.

### microSD

Probabile da documentazione Waveshare.

Sconosciuto nel firmware originale analizzato:

- Uso runtime della microSD.
- Pin effettivi nella board diymore.
