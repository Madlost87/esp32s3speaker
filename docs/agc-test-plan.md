# AGC test plan

Experimental firmware:

```text
esphome/galileo-va-afe-agc-test.yaml
```

This profile keeps the full AFE baseline and only enables AGC:

```yaml
esp_afe:
  agc_enabled: true
  post_afe_agc_support: true
  agc_compression_gain: 9
  agc_target_level: 3
```

## What AGC should improve

- Quieter speech.
- Wake word detection from farther away.
- More constant STT level when the speaker is not close to the user.

## What can get worse

- More room noise.
- More false wake activations.
- TTS/media stutter if CPU or buffering becomes stressed.
- Pumping artifacts, where background noise rises between words.

## Test

Run the same commands on baseline and AGC firmware:

| Distance | Test |
| --- | --- |
| 0.5 m | 10x Nabu, 10x Jarvis, normal voice |
| 1 m | 10x Nabu, 10x Jarvis, normal voice |
| 2 m | 10x Nabu, 10x Jarvis, normal voice |
| 3 m | 10x Nabu, 10x Jarvis, normal voice |

Then repeat with:

- TV/music in the room;
- device TTS/media playing;
- quiet voice.

Record:

- detections / attempts;
- false activations;
- `stt-no-text-recognized` errors;
- TTS/media dropouts;
- free heap and PSRAM after the run.

Keep AGC only if it improves detection without adding false positives or playback
instability.
