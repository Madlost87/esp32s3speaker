# TDM slot diagnostics

Use this only when intentionally testing the ES7210 slot map.

Diagnostic firmware:

```text
esphome/galileo-va-afe-slot-diagnostics.yaml
```

It includes the full AFE baseline and adds four diagnostic sensors:

| Sensor | Expected signal |
| --- | --- |
| `TDM Slot 0 Level` | right microphone |
| `TDM Slot 1 Level` | playback / AEC reference |
| `TDM Slot 2 Level` | left microphone |
| `TDM Slot 3 Level` | unused or near silent |

## Test procedure

1. Flash the diagnostic profile only for the measurement run.
2. Keep the device silent for 10 seconds and record the four dBFS values.
3. Speak close to the right microphone and record which slot rises most.
4. Speak close to the left microphone and record which slot rises most.
5. Play TTS/media from the device speaker and record which slot tracks playback.
6. Repeat once at normal voice distance.
7. Restore or keep the full AFE baseline depending on results.

Expected result for the current board:

- slot 0 rises on right-side speech;
- slot 2 rises on left-side speech;
- slot 1 rises with local speaker playback;
- slot 3 stays near the noise floor.

If slot 3 rises with speech, the current firmware is not using all available
microphone input and the AFE mapping should be revisited.
