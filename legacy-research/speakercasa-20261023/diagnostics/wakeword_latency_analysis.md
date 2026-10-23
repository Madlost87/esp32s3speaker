# Wake-Word Latency Analysis

Date: 2026-10-02

## Current Behavior

The Raspberry now runs a boot-enabled user service:

```text
galileo-wake-led.service
```

The service starts:

```text
/home/denny/galileo/bin/rpi_continuous_openwakeword_led.py
```

Current test behavior:

1. keep `arecord` open on `plughw:0,0`;
2. keep a rolling audio buffer;
3. score a 3s audio window with openWakeWord;
4. pulse the ReSpeaker LEDs purple when the score passes threshold `0.95`.

This is useful for live sensitivity testing, but it is still a diagnostic loop rather than the final low-latency wake-word service.

## Observed Latency

In the current loop, the LED can appear delayed after the user says `Galileo`.

Measured and expected contributors:

- audio window: up to `3.0s`;
- score interval: currently `0.75s`;
- feature extraction after warmup: about `1.05s` per scored 3s window;
- ONNX classifier inference: fast, usually much smaller than feature extraction;
- LED command: small but currently executed as a subprocess.

Practical effect:

- best case: the word lands near the end of a window and the LED can react in about `1-2s`;
- worse case: the word lands just after a scoring snapshot and the next useful window arrives later, so the LED can feel delayed by several seconds.

## Likely Root Cause

The main delay is not the ONNX classifier.

The likely bottlenecks are:

1. scoring full 3s windows repeatedly;
2. recalculating openWakeWord features for the whole window each time;
3. sleeping between scoring attempts;
4. subprocess calls for LED pulses.

The current script is intentionally simple and testable. It favors correctness and visibility over latency.

## Risk Of Simply Lowering Timings

Lowering `--score-interval` may make the LED feel quicker, but it can also overload the Pi if feature extraction takes longer than the interval.

Lowering `--window-seconds` may make the LED quicker, but it can hurt detection if the model expects enough surrounding audio context.

Lowering `--threshold` may make weak/distant speech trigger more often, but it increases false positives. This matters because we already saw a spoken-negative holdout at `0.806` and a live near-miss at `0.922`.

## Next Experiments

Run these in order.

1. Baseline current boot service:
   - threshold `0.95`;
   - window `3.0s`;
   - score interval `0.75s`;
   - note delay by ear/eye at near distance, low voice, and far distance.

2. Faster scoring interval:
   - keep window `3.0s`;
   - test score interval `0.5s`;
   - verify CPU load and whether LED response improves.

3. Shorter window:
   - test window `2.0s`;
   - keep threshold `0.95`;
   - compare missed detections and false positives.

4. Threshold sweep:
   - compare `0.95`, `0.90`, and `0.85`;
   - only lower threshold if hard negatives remain safe.

5. LED path optimization:
   - avoid launching a new Python process for every LED pulse;
   - control SPI directly inside the listener or keep an LED worker alive.

6. Streaming openWakeWord integration:
   - replace repeated full-window `embed_clips` calls with the library's streaming model path if practical;
   - target sub-second feedback after the word ends.

## Proposed Target

For the final satellite behavior:

- acceptable diagnostic latency: under `2s`;
- preferred wake LED latency: under `1s` after the word ends;
- avoid false positives from normal speech without `Galileo`;
- keep boot behavior automatic and recoverable through `systemd`.

## Tomorrow's Recommended First Step

Start with a controlled A/B run:

1. current settings;
2. `--score-interval 0.5`;
3. `--window-seconds 2.0 --score-interval 0.5`.

For each run, test:

- close normal voice;
- close low voice;
- far normal voice;
- normal speech without `Galileo`.

Keep notes on:

- visible LED delay;
- missed detections;
- false positives;
- printed scores near threshold.
