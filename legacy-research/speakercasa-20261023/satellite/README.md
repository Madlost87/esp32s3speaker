# Galileo Satellite Software Skeleton

This package is the lightweight Raspberry-side foundation for the Galileo voice satellite.

Current scope:

- ALSA capture from `hw:0,0`
- 48 kHz stereo `S16_LE` input
- stereo-to-mono downmix
- integer downsampling to 16 kHz
- simple DC removal
- capture statistics for diagnostics
- energy-based VAD diagnostics

It intentionally does not implement wake word, streaming, or services yet.

## Diagnostic Command

On the Raspberry, from the project root:

```text
python3 -m satellite capture-stats --duration 5
```

Expected output is JSON with chunk count and mono PCM statistics.

The first Raspberry test produced:

```text
chunks: 244
samples: 78080
rms: 13.46
rms_dbfs: -67.73
peak: 267
peak_dbfs: -41.78
dc_offset_samples: 2.17
clipped_samples: 0
```

The low DC offset confirms that the software DC-removal stage is active.

## VAD Diagnostic

```text
python3 -m satellite vad-monitor --duration 15 --summary
```

The initial VAD is energy-based and intended for bring-up only. It emits:

- `speech_start`
- `speech_end`

Thresholds live in `config/galileo.toml`.

Initial Raspberry test:

- first threshold pass (`-68 dBFS`, 120 ms trigger) detected speech start/end;
- it also retriggered once near the end of the test;
- default start threshold was tightened to `-64 dBFS` with a 180 ms trigger.

## State Machine Diagnostic

```text
python3 -m satellite run-state --duration 20 --summary
```

Current state loop:

```text
IDLE -> LISTENING -> PROCESSING -> IDLE
```

`PROCESSING` is currently a stub. `SPEAKING` is reserved for the later playback/TTS path.

A short post-processing cooldown suppresses immediate VAD retriggers after an utterance.

## Wake Word Hook

`satellite/wakeword/` contains a placeholder detector and configuration surface for the future wake-word engine.

Current selected path:

- primary: openWakeWord custom `Galileo`
- fallback: Porcupine custom model, only if the open path stalls

The placeholder intentionally never fires. Real model activation should wait until a trained model is provided outside git.

## Dataset Mode

```text
python3 -m satellite dataset-record \
  --category positive \
  --label galileo \
  --distance 30cm \
  --environment quiet \
  --speaker denny \
  --duration 3
```

Dataset files are written outside git under:

```text
/home/denny/galileo/dataset/
```

Each WAV has a sidecar JSON metadata file.
