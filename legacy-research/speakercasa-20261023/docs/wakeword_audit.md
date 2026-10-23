# GALILEO WAKE WORD AUDIT

Date: 2026-10-03

Scope: technical audit of the current Galileo wake-word path for false-positive reduction. This document does not authorize a wake engine replacement or a main pipeline rewrite.

## 1. Current Architecture

There are two different wake-related architectures in the repository right now.

Repository satellite skeleton:

```text
ReSpeaker / WM8960 microphones
-> ALSA capture `hw:0,0`, S16_LE, 48 kHz, stereo
-> `satellite.audio.capture.AlsaCapture`
-> stereo L/R arithmetic average
-> integer downsample 48 kHz -> 16 kHz
-> DC blocker
-> energy VAD
-> diagnostic state machine
```

This path is used by `capture-stats`, `vad-monitor`, `run-state`, and dataset recording helpers. It does not currently run the deployed wake-word model. `satellite/wakeword/` is still a placeholder.

Currently deployed purple-LED wake diagnostic:

```text
ReSpeaker / WM8960 microphones
-> `arecord -D plughw:0,0 -f S16_LE -r 16000 -c 1 -t raw`
-> rolling 3s mono buffer
-> `openwakeword.utils.AudioFeatures.embed_clips`
-> ONNX Runtime classifier
-> decision: score >= 0.95 and outside cooldown
-> pulse ReSpeaker LEDs purple
```

This path is started by the Raspberry user service:

```text
galileo-wake-led.service
```

The Raspberry was initially unreachable, then came back online at `192.168.1.151` / `galileo.local`. Board measurements are captured in:

```text
diagnostics/wakeword_board_measurements.md
```

The deployed service is active, enabled, and user linger is enabled.

## 2. Current Model

Engine: openWakeWord custom model.

Model: local v3 Galileo pilot.

Model format: ONNX plus external data file.

Repository-local training artifact:

```text
local_data/openwakeword_training/galileo_led_batch_v3_pilot/galileo_pilot.onnx
local_data/openwakeword_training/galileo_led_batch_v3_pilot/galileo_pilot.onnx.data
```

Raspberry deployed artifact, from previous diagnostics:

```text
/home/denny/galileo/models/openwakeword/galileo_v3.onnx
/home/denny/galileo/models/openwakeword/galileo_pilot.onnx.data
```

Runtime: `onnxruntime` CPU execution provider.

Feature extractor: openWakeWord `AudioFeatures(device="cpu")`.

Input format in deployed diagnostic: 16 kHz mono S16_LE raw audio from `plughw:0,0`.

Window: 3 seconds, `48000` samples.

Threshold: `0.95`.

VAD: not used in the deployed wake diagnostic.

Temporal logic: no smoothing, no hysteresis, no consecutive confirmation. The current logic is one-window thresholding plus cooldown.

Decision rule:

```text
score >= threshold and now - last_detection >= cooldown_seconds
```

Cooldown: `2.0s`.

Score interval: `0.75s`.

LED action: subprocess call to `respeaker_leds.py pulse purple`.

Known latency: feature extraction for one 3s live scoring window was about `1.05s` after warmup on the continuous diagnostic. Earlier single-shot scoring took about `2.7-3.1s` for feature extraction on the Pi Zero 2 W.

## 3. Hardware Input

Hardware:

- Raspberry Pi Zero 2 W.
- KEYESTUDIO ReSpeaker 2-Mic Pi HAT v1.0 / WM8960.
- amplified speaker connected to the HAT jack.

Known working audio:

- ALSA capture: `hw:0,0`, stereo.
- ALSA playback: `hw:0,0`, stereo.
- Tested capture/playback formats include 16 kHz and 48 kHz S16_LE.

Known capture mixer profile:

- `Capture`: `28`
- `ADC PCM`: `230`
- `Left Input Mixer Boost`: on
- `Right Input Mixer Boost`: on
- `Left Boost Mixer LINPUT1`: on
- `Right Boost Mixer RINPUT1`: on

Important input mismatch:

- Dataset/satellite recorder path uses 48 kHz stereo and then normalizes/downmixes to 16 kHz mono.
- Deployed live wake diagnostic uses ALSA `plughw:0,0` to deliver 16 kHz mono directly.

This may be acceptable, but it has not yet been proven equivalent. It is a serious audit item because training/inference preprocessing mismatch is a common source of unstable wake-word behavior.

Known audio issues from previous diagnostics:

- microphone capture works;
- DC offset exists;
- L/R spatial separation is weak;
- both channels often respond similarly;
- speaker leakage was only lightly tested and must be retested at realistic TTS volume.

## 4. Current Performance

Benchmark tool added:

```text
scripts/benchmark_openwakeword_wavs.py
```

Canonical test-only outputs generated:

```text
diagnostics/wakeword_scores.csv
diagnostics/wakeword_threshold_report.csv
diagnostics/wakeword_benchmark.md
```

Test-only v3 workspace benchmark:

```text
workspace: local_data/openwakeword_workspace/galileo_led_batch_v3_16k
splits: positive_test, negative_test
files: 18
threshold: 0.95
```

Metrics at threshold `0.95`:

| Metric | Value |
| --- | ---: |
| True positives | 7 |
| False positives | 0 |
| False negatives | 1 |
| True negatives | 10 |
| Recall | 0.875 |
| Precision | 1.000 |
| False positive rate | 0.000 |
| Miss rate | 0.125 |

Threshold sweep summary:

- thresholds `0.50` through `0.90`: `1` false positive, `1` false negative;
- threshold `0.95`: `0` false positives, `1` false negative;
- threshold `0.99`: `0` false positives, `3` false negatives.

Timing on local PC for 18 WAVs:

- feature extraction: `0.606s`;
- ONNX scoring: `0.014s`.

Timing on Raspberry from previous live diagnostic:

- continuous feature extraction after warmup: about `1.05s` per scored 3s window;
- ONNX classifier itself is not the bottleneck.

Live board resource measurement on 2026-10-03:

- wake listener Python process: about `85-87%` CPU during repeated samples;
- wake listener RSS: about `190-193 MB`;
- `arecord` child: about `0.6%` CPU and about `2.7 MB` RSS;
- board temperature: `47.8 C`;
- throttling: `0x0`;
- RAM available: about `152 MB`.

This is acceptable for a temporary diagnostic, but too expensive to call final 24/7 behavior on a Pi Zero 2 W.

False accepts/hour: not yet measurable from the current dataset because there is no long negative recording corpus. The existing negative test set is only 10 clips of 3 seconds each, which is far too small for a 24/7 false accept estimate.

## 5. False Positive Analysis

Observed evidence:

- The v3 test set contains a hard negative with score `0.937939`.
- At thresholds up to `0.90`, that file becomes a false positive.
- At threshold `0.95`, it barely remains negative.
- A previous live continuous test also observed a near-threshold non-detection at `0.922`.
- Before v3 retraining, LED-guided silence/spoken-negative batches produced multiple false positives at threshold `0.95`.
- A Raspberry-side spoken negative previously scored `0.806`.

Highest-scoring test negatives:

| Score | Category | File |
| ---: | --- | --- |
| 0.937939 | hard negative / normal speech | `0006-negative-20261002-144903-negative-normal_speech.wav` |
| 0.229888 | hard negative / normal speech | `0041-negative-20261002-144856-negative-normal_speech.wav` |
| 0.011660 | noise | `0016-noise-20261002-145033-noise-room_noise.wav` |

The current false-positive risk is concentrated in speech-like negatives, not room silence/noise. The model has learned silence fairly well, but the separation between `Galileo` and some normal speech is still too narrow.

Likely current false-positive mechanisms:

1. The model was trained with too few hard negatives compared with real domestic speech/TV/speaker conditions.
2. The final decision is a single threshold crossing, with no temporal confirmation.
3. The live system has no VAD/state/playback gating.
4. Training/inference preprocessing is not fully proven equivalent.
5. The current test corpus is too small to estimate rare false accepts.
6. The current Python feature-extraction loop consumes most of a Pi Zero 2 W core, leaving too little headroom for the final satellite.

## 6. False Negative Analysis

Lowest-scoring test positives:

| Score | File |
| ---: | --- |
| 0.003668 | `20261002-155039-galileo-led-batch-10-16k-mono.wav` |
| 0.984236 | `0051-positive-20261002-143920-positive-galileo.wav` |
| 0.988597 | `0001-positive-20261002-144244-positive-galileo.wav` |

The failed positive is not a threshold-margin issue; it is an extreme miss. That sample should be inspected/listened to locally on the Raspberry or PC, but not committed. Possible causes include mistimed LED capture, missing/partial spoken word, bad level, wrong label, or unusual pronunciation/position.

The remaining positives are high, but several sit in the `0.984-0.996` band. Raising the threshold to `0.99` reduces false-positive risk but drops recall to `0.625` on the tiny test set, so threshold alone is not a safe solution.

## 7. Root Causes

Ordered by technical importance:

1. Dataset is too small and not representative enough for 24/7 domestic conditions.

   The clean v3 test set has only 10 negatives. It lacks enough TV, music, distant speech, words similar to Galileo, speaker echo, and long negative recordings.

2. Hard-negative margin is inadequate.

   A normal-speech negative scoring `0.937939` means the current threshold `0.95` is sitting very close to a known failure boundary.

3. Current live decision logic is too simple.

   It is essentially `score >= 0.95 -> wake`, with cooldown only after a wake. There is no consecutive-frame confirmation, smoothing, hysteresis, VAD assist, or playback guard.

4. Training/inference audio path mismatch has not been closed.

   Dataset path and deployed wake path do not currently share exactly the same capture/preprocess code.

5. Self-wake and playback leakage are not yet measured.

   The speaker works, but the project has not yet proven that its own audio cannot trigger wake.

6. The wake diagnostic is not yet integrated into the satellite state machine.

   The real service path is separate from the package-level wake abstraction, so central state such as `SPEAKING` cannot currently suppress wake.

## 8. Proposed Improvements

### A. Add diagnostic false-wake capture with volatile ring buffer

EXPECTED BENEFIT: high. It will reveal what actually triggered false positives.

RISK: privacy/storage if implemented incorrectly.

CPU COST: low.

RAM COST: low to moderate; a 10s 16 kHz mono int16 ring is about 320 KB.

LATENCY COST: none.

IMPLEMENTATION COMPLEXITY: low to medium.

Notes: save audio only on detection and only in explicit diagnostic mode. Include JSON sidecar with score, threshold, recent scores, service config, timestamp, and whether playback was active.

### B. Add benchmark-first threshold policy

EXPECTED BENEFIT: high.

RISK: low.

CPU COST: none at runtime.

RAM COST: none.

LATENCY COST: none.

IMPLEMENTATION COMPLEXITY: low.

Notes: never tune threshold from live impressions alone. Use `diagnostics/wakeword_threshold_report.csv` and expand the negative corpus before changing deployed threshold.

### C. Add consecutive confirmation / score smoothing

EXPECTED BENEFIT: medium to high for isolated false positives.

RISK: may increase wake latency and miss short/quiet `Galileo`.

CPU COST: none beyond existing inference.

RAM COST: trivial.

LATENCY COST: likely `0.5-1.5s`, depending on settings.

IMPLEMENTATION COMPLEXITY: low.

Notes: test rules like two detections above threshold inside 1.5s, or max/mean score over recent windows. Do not deploy until benchmarked.

### D. Align live capture preprocessing with training/evaluation

EXPECTED BENEFIT: medium to high.

RISK: changing audio path may change model scores.

CPU COST: low.

RAM COST: low.

LATENCY COST: small if done with simple downmix/downsample.

IMPLEMENTATION COMPLEXITY: medium.

Notes: choose one official path: either train/evaluate exactly on 16 kHz mono `plughw:0,0` captures, or make live wake use the same 48 kHz stereo -> downmix -> DC blocker path as dataset mode.

### E. Add playback guard / self-wake suppression

EXPECTED BENEFIT: high once TTS/playback enters the loop.

RISK: could ignore a user saying `Galileo` during playback.

CPU COST: none.

RAM COST: none.

LATENCY COST: short guard interval after playback, if used.

IMPLEMENTATION COMPLEXITY: low if state machine owns playback state.

Notes: initially prefer deterministic inhibition while `SPEAKING` plus a short post-playback guard over heavy AEC.

### F. Expand hard negatives and retrain

EXPECTED BENEFIT: very high.

RISK: overfitting if splits are not strict.

CPU COST: none at runtime if model size stays the same.

RAM COST: unchanged if model size stays the same.

LATENCY COST: unchanged if model architecture stays the same.

IMPLEMENTATION COMPLEXITY: medium.

Notes: false wake captures should become hard-negative candidates. Keep a truly separate test set.

## 9. Model Retraining

Classification: STRONGLY RECOMMENDED.

Reason:

- the current model works, but known hard negatives score too close to the threshold;
- the test set is much too small for 24/7 confidence;
- the current false-positive complaint is consistent with insufficient hard-negative diversity;
- raising threshold alone quickly harms recall.

Retraining should not be blind. Recommended loop:

```text
false wake real event
-> save diagnostic ring-buffer sample
-> label as hard_negative if it does not contain Galileo
-> add to train/validation/test split carefully
-> retrain
-> run benchmark + threshold sweep
-> deploy only if hard negatives improve without breaking positives
```

Dataset targets before the next serious model promotion:

- positives: near, far, quiet, loud, slow, fast, different orientations;
- hard negatives: words/syllables similar to Galileo, normal conversation, names, TV speech;
- noise: realistic home noise;
- TV/music: several minutes segmented into testable clips;
- speaker_echo: satellite speaker output at realistic volume;
- strict holdout set not derived from training recordings.

## 10. Recommended Galileo Architecture

Recommended next architecture for this hardware:

```text
ALSA capture
-> one canonical 16 kHz mono preprocessing path
-> optional lightweight VAD/energy metadata, not aggressive gating
-> openWakeWord feature extraction/model
-> temporal decision layer:
   - threshold
   - short smoothing/consecutive confirmation
   - cooldown
   - playback guard
-> diagnostic event logger
-> state machine wake event
```

Keep openWakeWord for now. The current evidence does not justify switching engines before fixing measurement, hard negatives, and decision logic.

Do not add heavy beamforming or AEC yet. The Pi Zero 2 W budget is tight, and the current highest-risk failures are model/data/decision issues, not proven spatial filtering issues.

## 11. Implementation Plan

### PHASE A: simple measurable fixes

1. Keep using the benchmark script and expand it to category summaries.
2. Add diagnostic false-wake ring-buffer capture mode.
3. Treat the current Raspberry service as a diagnostic only; it is confirmed active but too CPU-heavy for final 24/7 operation.
4. Run controlled tests:
   - current settings;
   - score interval `0.5s`;
   - window `2.0s`;
   - threshold `0.95` vs `0.98`;
   - do not change boot defaults until measured.
5. Add a simple decision-layer experiment: two near-threshold confirmations before wake.

### PHASE B: dataset/model

1. Collect real false-positive events with diagnostic ring buffer.
2. Build categories:
   - `positive`;
   - `negative`;
   - `hard_negative`;
   - `noise`;
   - `tv`;
   - `speaker_echo`.
3. Create strict train/validation/test splits.
4. Retrain v4 with hard negatives.
5. Run threshold sweep and compare v3 vs v4 before deployment.

### PHASE C: later optimization

1. Move from full-window repeated `embed_clips` to a more streaming-friendly path if openWakeWord supports it cleanly.
2. Integrate wake detection into `satellite/wakeword/`.
3. Gate the real satellite state machine on wake events.
4. Add playback state suppression.
5. Consider one alternative wake engine only if openWakeWord remains unreliable after the hard-negative loop.

## Final Answers

### Why does Galileo produce many false positives now?

The best-supported answer is: the current model and live decision layer are not yet robust enough for real domestic speech. The model has at least one normal-speech hard negative scoring `0.937939`, very close to the deployed `0.95` threshold, and previous live tests saw spoken negatives as high as `0.806` plus a near miss at `0.922`. The live service then makes a wake decision from a single threshold crossing, with no smoothing, no confirmation, no playback guard, and no VAD/state context. On top of that, the training/evaluation and deployed capture paths are not yet proven identical.

### What is the most effective path to make Galileo reliable on Pi Zero 2 W + ReSpeaker 2-Mic HAT?

Do not switch engines yet. The most effective path is:

1. instrument false positives with a privacy-conscious ring buffer;
2. turn real false wakes into hard negatives;
3. benchmark every candidate model with threshold sweeps;
4. add a small temporal decision layer;
5. align training and live preprocessing;
6. add playback/self-wake suppression before TTS integration;
7. retrain a v4 model only when there are enough hard negatives and strict holdouts.

This path directly attacks the observed failure mode while staying compatible with Pi Zero 2 W resources.
