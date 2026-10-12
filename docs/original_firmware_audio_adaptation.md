# Original Firmware Audio Adaptation

Date: 2026-10-07

> Stato: documento storico.
>
> Questo file descrive il passaggio iniziale dal firmware factory Xiaozhi allo
> stock ESPHome e poi al profilo AFE. Dopo la validazione del 2026-10-08, il
> profilo operativo e' `esphome/galileo-va-afe.yaml`.

This note captures the result of comparing the original Xiaozhi factory firmware
with the ESPHome firmware used for Galileo Voice.

## Factory Firmware Evidence

The original firmware identifies itself as `xiaozhi` for board
`waveshare-s3-audio-board`. Strings and boot logs show a richer audio stack than
plain ESPHome:

- ES7210 ADC and ES8311 DAC are initialized.
- The firmware creates duplex I2S channels with `i2s_new_channel`.
- The ES7210 path enables MIC1, MIC2, MIC3 and MIC4.
- ESP-SR / AFE components are present:
  - WakeNet
  - VAD
  - WebRTC noise suppression
  - digital AGC
  - 1-mic and 2-mic AFE paths
  - microphone array speech enhancement / BSS
- The factory firmware has model loading from the `model` SPIFFS partition.

Important hardware implication: the board is not just a single microphone plus a
speaker. It exposes a dual-mic ES7210 path and likely has a playback reference
channel for echo cancellation.

## Stock ESPHome Adaptation

The first maintained firmware was based on
`MichalZaniewicz/esphome-waveshare-esp32-s3-audio-va` pinned to `v1.1.1`.

The safe "top within stock ESPHome" adaptation is in:

```text
esphome/galileo-va.yaml
```

It now:

- Keeps the known-working two-I2S-bus shared-clock architecture.
- Extends `i2s_mics` to stereo capture.
- Keeps `micro_wake_word` on channel `0`.
- Sends Assist two mono microphone sources, channels `0` and `1`.
- Raises Assist preprocessing to:
  - `noise_suppression_level: 4`
  - `auto_gain: 31dBFS`
  - `volume_multiplier: 3`
- Keeps `Okay Nabu` and `Hey Jarvis` enabled at boot.

This profile validates and compiles with ESPHome 2026.9.1.

Latest verification:

- Config validation: PASS
- Compile: PASS
- `galileo-va.bin`: `0x1b8280`
- App partition free: 78%
- RAM used: 43.5%, 148,707 / 341,760 bytes
- Flash used: 22.2%, 1,802,755 / 8,126,464 app bytes

## AFE Profile

The closer factory-style profile is:

```text
esphome/galileo-va-afe.yaml
```

This profile started as the experimental attempt, then became the operational
baseline after runtime validation. It uses external components from the
`n-IA-hane` ESPHome audio/VoIP/AFE stack and models the hardware more like the
factory firmware:

- ES7210/ES8311 through an ESP audio stack.
- 48 kHz TDM capture.
- Dual physical microphone slots.
- Playback reference slot for AEC.
- ESP AFE with AEC, noise suppression, VAD and speech enhancement.
- Optional VoIP pipeline.

The profile documents the observed slot mapping used for that experiment:

- slot `2`: left microphone
- slot `0`: right microphone
- slot `1`: playback reference for AEC
- slot `3`: near-silent / unused

Treat the old stock profile as the comparison/fallback path. The AFE profile is
the current stable firmware path.

## Current Conclusion

The original firmware uses more of the audio hardware than the first ESPHome
YAML did. The stock profile showed what could be done without replacing the
audio stack, but the full factory-style hardware path requires an AFE-capable
component stack.

The current baseline is `galileo-va-afe.yaml`: full AFE, dual mic, TDM reference
for AEC, wake/Assist, VoIP, LED and physical controls.
