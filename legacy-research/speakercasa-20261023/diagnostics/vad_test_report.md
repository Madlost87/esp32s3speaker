# Galileo VAD Test Report

Date: 2026-10-01

## VAD Configuration

Initial energy-based VAD over the preprocessed stream:

- Input to VAD: mono PCM, 16 kHz, 16-bit
- Frame size: `30 ms`
- Start threshold: `-64.0 dBFS`
- End threshold: `-72.0 dBFS`
- Start trigger: `180 ms`
- End silence: `500 ms`

Command:

```text
python3 -m satellite vad-monitor --duration N --summary
```

## Structured Tests

### Silence

Duration: `10 seconds`

Result:

- Events: none
- Level summary:
  - min: `-90.14 dBFS`
  - p50: `-83.69 dBFS`
  - p90: `-77.61 dBFS`
  - max: `-38.55 dBFS`

Interpretation: pass; no false speech event.

### Normal Speech

Duration: `14 seconds`

Result:

- `speech_start`: `4.47 s`, `-62.57 dBFS`
- `speech_end`: `6.27 s`, `-85.47 dBFS`
- Level summary:
  - min: `-89.36 dBFS`
  - p50: `-71.22 dBFS`
  - p90: `-61.60 dBFS`
  - max: `-36.73 dBFS`

Interpretation: pass; speech start/end were detected cleanly.

### Ambient / Non-Speech Noise

Duration: `10 seconds`

Result:

- Events: none
- Level summary:
  - min: `-89.38 dBFS`
  - p50: `-79.28 dBFS`
  - p90: `-71.36 dBFS`
  - max: `-36.09 dBFS`

Interpretation: pass for this light ambient/noise test; no false speech event.

## Conclusion

- The initial energy VAD is usable as a diagnostic VAD.
- It correctly emitted `speech_start` and `speech_end` for a normal speech test.
- It did not false-trigger during the silence or light ambient/noise tests.
- This is not a final wake-word-grade VAD, but it is sufficient for early Galileo capture/listening state-machine work.

## Next Step

Use this VAD inside the satellite state skeleton, then evaluate whether WebRTC VAD or another lightweight VAD improves robustness.
