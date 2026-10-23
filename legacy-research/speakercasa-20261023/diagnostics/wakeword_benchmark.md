# Galileo Wake-Word Benchmark

Model: `local_data/openwakeword_training/galileo_led_batch_v3_pilot/galileo_pilot.onnx`
Workspace: `local_data/openwakeword_workspace/galileo_led_batch_v3_16k`
Primary threshold: `0.95`

## Primary Metrics

| metric | value |
| --- | ---: |
| tp | 7 |
| fp | 0 |
| fn | 1 |
| tn | 10 |
| recall | 0.8750 |
| precision | 1.0000 |
| false_positive_rate | 0.0000 |
| miss_rate | 0.1250 |
| false_accepts_per_hour | 0.0000 |

## Timings

- Feature extraction total: `0.606s`
- ONNX scoring total: `0.014s`
- Files scored: `18`

## Threshold Sweep Notes

Lowest swept threshold with zero false positives: `0.95` (recall `0.8750`, FN `1`).

## Highest-Scoring Negatives

| score | category | split | file |
| ---: | --- | --- | --- |
| 0.937939 | hard_negative | negative_test | `0006-negative-20261002-144903-negative-normal_speech.wav` |
| 0.229888 | hard_negative | negative_test | `0041-negative-20261002-144856-negative-normal_speech.wav` |
| 0.011660 | noise | negative_test | `0016-noise-20261002-145033-noise-room_noise.wav` |
| 0.006478 | noise | negative_test | `0026-noise-20261002-145106-noise-room_noise.wav` |
| 0.005789 | noise | negative_test | `20261002-154912-silence-led-batch-10-16k-mono.wav` |
| 0.005390 | noise | negative_test | `20261002-154905-silence-led-batch-9-16k-mono.wav` |
| 0.004871 | hard_negative | negative_test | `20261002-155306-speech-no-galileo-led-batch-10-16k-mono.wav` |
| 0.003364 | hard_negative | negative_test | `0021-negative-20261002-144850-negative-normal_speech.wav` |
| 0.003357 | noise | negative_test | `0011-noise-20261002-145057-noise-room_noise.wav` |
| 0.003328 | hard_negative | negative_test | `20261002-155259-speech-no-galileo-led-batch-9-16k-mono.wav` |

## Lowest-Scoring Positives

| score | split | file |
| ---: | --- | --- |
| 0.003668 | positive_test | `20261002-155039-galileo-led-batch-10-16k-mono.wav` |
| 0.984236 | positive_test | `0051-positive-20261002-143920-positive-galileo.wav` |
| 0.988597 | positive_test | `0001-positive-20261002-144244-positive-galileo.wav` |
| 0.995556 | positive_test | `20261002-153533-galileo-led-series-5-16k-mono.wav` |
| 0.996574 | positive_test | `20261002-155032-galileo-led-batch-9-16k-mono.wav` |
| 0.997921 | positive_test | `0031-positive-20261002-144518-positive-galileo.wav` |
| 0.998175 | positive_test | `0036-positive-20261002-144417-positive-galileo.wav` |
| 0.998217 | positive_test | `0046-positive-20261002-144238-positive-galileo.wav` |

## Raw Files

- Per-file CSV: `diagnostics/wakeword_scores.csv`
- Threshold CSV: `diagnostics/wakeword_threshold_report.csv`
