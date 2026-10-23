# Galileo Microphone Calibration

Date: 2026-10-01

## Working Capture Route

The WM8960 capture route that produced recognizable voice is:

- `Capture`: left/right `20`, `-2.25 dB`
- `ADC PCM`: left/right `215`, `+10.00 dB`
- `Left Boost Mixer LINPUT1`: `on`
- `Right Boost Mixer RINPUT1`: `on`
- `Left Input Boost Mixer LINPUT1`: `0`, `0.00 dB`
- `Right Input Boost Mixer RINPUT1`: `0`, `0.00 dB`
- `Left Input Mixer Boost`: `on`
- `Right Input Mixer Boost`: `on`
- `ADC High Pass Filter`: `on`
- `Noise Gate`: `off`

These settings were saved on the Raspberry with `sudo alsactl store 0`.

## Close Voice Reference

Recording:

- `/home/denny/galileo/recordings/voice_close_input_mixer_repeat.wav`

Measured result:

- Channel 0 RMS: `981.72`, `-30.47 dBFS`
- Channel 1 RMS: `688.15`, `-33.56 dBFS`
- Channel 0 peak: `1970`, `-24.42 dBFS`
- Channel 1 peak: `1645`, `-25.99 dBFS`
- Clipping: `0`

Listening result:

- A temporary amplified listening copy was played through the HAT speaker output.
- The user confirmed recognizable voice.

## Normal Voice Test

Recording:

- `/home/denny/galileo/recordings/voice_normal.wav`

Measured result:

- Channel 0 RMS: `964.98`, `-30.62 dBFS`
- Channel 1 RMS: `674.99`, `-33.72 dBFS`
- Channel 0 peak: `1403`, `-27.37 dBFS`
- Channel 1 peak: `1085`, `-29.60 dBFS`
- Clipping: `0`
- DC offset:
  - Channel 0: `953.66` samples
  - Channel 1: `653.88` samples

Listening playback:

- Original file: `/home/denny/galileo/recordings/voice_normal.wav`
- Temporary amplified copy: `/tmp/voice_normal_listen.wav`
- Listening confirmation: pending.

## Corrected-Routing Stereo Test

Recording:

- `/home/denny/galileo/recordings/stereo_test_corrected_routing.wav`

Procedure:

- 0-2s: LEDs off
- 2-8s: left LED red, speak/tap near left microphone
- 8-10s: LEDs off
- 10-16s: right LED red, speak/tap near right microphone

Window analysis uses AC RMS with DC offset removed.

### 2-8s Left Window

- Channel 0 AC RMS: `38.11`, `-58.69 dBFS`
- Channel 1 AC RMS: `41.22`, `-58.01 dBFS`
- Channel 0 over channel 1: `-0.68 dB`
- Channel 0 peak: `1456`, `-27.05 dBFS`
- Channel 1 peak: `1223`, `-28.56 dBFS`
- Clipping: `0`

### 10-16s Right Window

- Channel 0 AC RMS: `53.01`, `-55.82 dBFS`
- Channel 1 AC RMS: `56.03`, `-55.34 dBFS`
- Channel 0 over channel 1: `-0.48 dB`
- Channel 0 peak: `1573`, `-26.37 dBFS`
- Channel 1 peak: `1405`, `-27.36 dBFS`
- Clipping: `0`

## Interpretation

- Real microphone capture is confirmed.
- Close voice is recognizable after playback amplification.
- Normal voice has usable level and no clipping, but listening confirmation is still pending.
- The channels have a strong DC offset, so future analysis should remove DC before comparing acoustic levels.
- Left/right spatial separation is weak in the corrected-routing stereo test; both channels respond similarly.
- Current mixer settings are a working baseline, not final calibration.

## Next Tests

- Confirm listening quality of `voice_normal.wav`.
- Record a true silence/noise-floor sample with the corrected route.
- Test mono downmix quality after DC removal or high-pass filtering.
- Run full-duplex speaker playback plus capture to measure leakage.
