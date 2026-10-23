# Galileo State Machine Test

Date: 2026-10-01

## Scope

Initial diagnostic state machine wired to the real audio path:

```text
ALSA capture -> preprocess -> VAD -> state transitions
```

Current states:

- `IDLE`
- `LISTENING`
- `PROCESSING`
- `SPEAKING` reserved for later playback/TTS integration

Current diagnostic loop:

```text
IDLE -> LISTENING -> PROCESSING -> IDLE
```

`PROCESSING` is currently a stub.

## Initial Test

Command:

```text
python3 -m satellite run-state --duration 14 --summary
```

First run produced multiple cycles from one interaction, due to VAD retrigger after speech end.

Correction:

- Added `post_processing_cooldown_ms = 1500`.

## Cooldown Test Result

With the cooldown enabled, one spoken phrase produced one clean cycle:

```json
{"from": "IDLE", "to": "LISTENING", "reason": "speech_start", "time_seconds": 0.93}
{"from": "LISTENING", "to": "PROCESSING", "reason": "speech_end", "time_seconds": 4.35}
{"from": "PROCESSING", "to": "IDLE", "reason": "processing_stub_complete", "time_seconds": 4.35}
```

Final state: `IDLE`

## Interpretation

- The real capture/preprocess/VAD path can now drive state transitions.
- The cooldown prevents immediate duplicate interactions after speech end in the tested scenario.
- This is sufficient for the next integration step: wake-word gating and a placeholder processing/playback path.
