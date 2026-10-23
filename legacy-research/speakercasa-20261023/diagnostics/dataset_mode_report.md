# Galileo Dataset Mode

Date: 2026-10-02

## Purpose

Dataset mode records wake-word training and validation samples through the same ReSpeaker/WM8960 capture path used by the Galileo satellite.

Primary target:

```text
openWakeWord custom model for "Galileo"
```

## Dataset Layout

Root on Raspberry:

```text
/home/denny/galileo/dataset/
```

Categories:

```text
positive/galileo/
negative/
noise/
```

Each sample has:

- `.wav` audio file
- `.json` sidecar metadata

Personal WAV files are not committed to git.

## Command

```text
python3 -m satellite dataset-record \
  --category positive \
  --label galileo \
  --distance 30cm \
  --environment quiet \
  --speaker denny \
  --duration 3
```

Supported categories:

- `positive`
- `negative`
- `noise`

## Metadata

The sidecar JSON includes:

- sample id
- category
- label
- distance
- environment
- speaker
- ALSA device
- sample rate
- channel count
- sample format
- duration
- WAV path

## Validation

A first dataset recorder check was run on the Raspberry:

```text
python3 -m satellite dataset-record \
  --category noise \
  --label room_silence \
  --distance none \
  --environment boot_check \
  --speaker none \
  --duration 2
```

Created:

```text
/home/denny/galileo/dataset/noise/20261002-143351-noise-room_silence.wav
/home/denny/galileo/dataset/noise/20261002-143351-noise-room_silence.json
```

Result: dataset recorder created WAV and metadata successfully.

## Dataset Capture Profile

The first positive samples showed that the normal satellite capture profile was too quiet for dataset collection.

A temporary gain test used:

- `Capture`: left/right `28`, `+3.75 dB`
- `ADC PCM`: left/right `230`, `+17.50 dB`
- `Left Input Boost Mixer LINPUT1`: `0`, `0.00 dB`
- `Right Input Boost Mixer RINPUT1`: `0`, `0.00 dB`
- `Left Input Mixer Boost`: `on`
- `Right Input Mixer Boost`: `on`

Three positive `Galileo` samples at 30 cm with LED guidance produced:

- Sample 1: channel AC RMS about `-43.63 dBFS` / `-38.72 dBFS`
- Sample 2: channel AC RMS about `-48.89 dBFS` / `-46.95 dBFS`
- Sample 3: channel AC RMS about `-47.21 dBFS` / `-46.25 dBFS`
- Clipping: `0`

This profile was saved on the Raspberry with:

```text
sudo alsactl store 0
```

It is the current dataset collection profile.

## Next Collection Plan

Current dataset summary:

- Total WAV files on Raspberry: `64`
- Positive `Galileo`: `43`
- Negative normal speech: `10`
- Noise: `11`
- Recommended clean subset for first experiments:
  - Positive: `30` samples with `quiet_led_guided_dataset_c28_adc230`
  - Negative: `10` samples with `quiet_led_guided_dataset_c28_adc230`
  - Noise: `10` samples with `quiet_room_dataset_c28_adc230`

Note: older positive samples with very low levels and the first `boot_check` noise sample should be excluded from the first training pass.

Next:

- collect more positive `Galileo` at 1 m and 2 m;
- collect phonetically similar negatives;
- prepare an openWakeWord training manifest.

Then review levels and metadata before scaling up.
