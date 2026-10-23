# Galileo Full-Duplex And Noise-Floor Test

Date: 2026-10-01

## Capture Baseline

Working capture route:

- `Capture`: left/right `20`, `-2.25 dB`
- `ADC PCM`: left/right `215`, `+10.00 dB`
- `Left Input Mixer Boost`: `on`
- `Right Input Mixer Boost`: `on`
- `ADC High Pass Filter`: `on`
- `Noise Gate`: `off`

## Silence Test

Recording:

- `/home/denny/galileo/recordings/silence.wav`

Format:

- 48 kHz
- 16-bit
- stereo
- 10 seconds

Measured result, with DC offset removed for AC RMS:

- Channel 0 AC RMS: `70.94`, `-53.29 dBFS`
- Channel 1 AC RMS: `98.75`, `-50.42 dBFS`
- Channel 0 DC offset: `979.79` samples
- Channel 1 DC offset: `679.45` samples
- Clipping: `0`

## Full-Duplex Speaker Leakage Test

Recording:

- `/home/denny/galileo/recordings/speaker_echo_test.wav`

Playback source:

- `/tmp/galileo_echo_source.wav`
- Pulsed stereo two-tone signal, 660 Hz + 990 Hz
- Played through `hw:0,0` while recording from `hw:0,0`

ALSA result:

- `arecord` and `aplay` ran at the same time without reported errors.
- No xruns were reported in command output.

Measured result, with DC offset removed for AC RMS:

- Channel 0 AC RMS: `64.89`, `-54.07 dBFS`
- Channel 1 AC RMS: `59.85`, `-54.77 dBFS`
- Channel 0 DC offset: `1043.86` samples
- Channel 1 DC offset: `735.48` samples
- Clipping: `0`

Compared with silence:

- Channel 0 echo over silence: `-0.77 dB`
- Channel 1 echo over silence: `-4.35 dB`

## Interpretation

- Full-duplex capture and playback is technically working on `hw:0,0`.
- The moderate speaker leakage test did not raise microphone AC RMS above the silence/noise-floor recording.
- At the tested output level, speaker leakage is not macroscopically visible in RMS.
- This is a first leakage check, not a final acoustic echo characterization.
- A future test should use a realistic TTS-style voice sample and the intended physical speaker volume.
- Capture has a significant DC offset; analysis and software capture should apply high-pass/DC-removal before VAD/wake processing.
