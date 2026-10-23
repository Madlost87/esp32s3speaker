# Galileo openWakeWord Environment

Date: 2026-10-02

## Local Environment

Created local virtual environment:

```text
.venv-oww
```

Python:

```text
3.11.14
```

Installed:

```text
openwakeword==0.6.0
onnxruntime==1.30.0
tflite-runtime==2.14.0
numpy==2.4.6
scipy==1.17.1
scikit-learn==1.9.1
```

Note: `scipy` was later pinned to `1.15.3` for training compatibility with `acoustics==0.2.6`.

Verification:

- `from openwakeword.model import Model` works.
- The package exposes modules including `model`, `train`, `vad`, and `custom_verifier_model`.

## Training Dependency Status

Initial import of `openwakeword.train` failed because `torch` was not installed:

```text
ModuleNotFoundError: No module named 'torch'
```

This means:

- openWakeWord inference dependencies were installed locally first;
- CPU training dependencies were then added successfully;
- `openwakeword.train` now imports successfully.

## Recommendation

Use this PC environment for local CPU pilot training and inference-side tooling.

Before treating a model as deployable:

- add more negative and background examples;
- add synthetic/augmented positive examples;
- run live false-positive testing on the Raspberry;
- decide whether heavier training should move to a notebook/Colab-style environment.

## Workspace Preparation

The repository now includes:

```text
scripts/prepare_openwakeword_workspace.py
```

It converts the clean Galileo manifest into the folder layout expected by the openWakeWord training script:

```text
positive_train/
positive_test/
negative_train/
negative_test/
```

`noise` samples are intentionally mapped into the negative folders.

Example on the Raspberry:

```text
python3 scripts/prepare_openwakeword_workspace.py \
  /home/denny/galileo/dataset/manifests/galileo_openwakeword_initial.json \
  /home/denny/galileo/openwakeword_workspace/galileo_initial \
  --mode symlink
```

Onboard result:

```text
/home/denny/galileo/openwakeword_workspace/galileo_initial
```

Created with symlinks:

- `positive_train`: `28`
- `positive_test`: `5`
- `negative_train`: `14`
- `negative_test`: `6`

The workspace sidecar was written at:

```text
/home/denny/galileo/openwakeword_workspace/galileo_initial/galileo_openwakeword_workspace_manifest.json
```

## Local Training Pilot

Local CPU training dependencies were installed in `.venv-oww`:

```text
torch==2.14.1+cpu
torchaudio==2.11.0+cpu
torchinfo==1.8.0
torchmetrics==1.9.0
speechbrain==1.1.1
scipy==1.15.3
onnx==1.23.1
onnxscript==0.7.2
```

Notes:

- `scipy` was pinned below `1.16` because `acoustics==0.2.6` needs `scipy.special.sph_harm`.
- The local pilot avoids `torchaudio.load` and reads WAV files through SciPy because the current `torchcodec` package tried to load CUDA-linked libraries.
- openWakeWord base feature models were downloaded with `download_models(model_names=["__none__"])`.

Local generated data, features, and pilot artifacts are under ignored `local_data/`.

Pilot pipeline result:

- copied Raspberry workspace locally: `53` WAV files;
- normalized to 16 kHz mono: `53` WAV files;
- generated feature arrays:
  - positive train: `28`
  - positive test: `5`
  - negative train: `14`
  - negative test: `6`
- trained a small DNN pilot model for `200` epochs on CPU;
- exported local artifacts:
  - `local_data/openwakeword_training/galileo_pilot/galileo_pilot_state.pt`
  - `local_data/openwakeword_training/galileo_pilot/galileo_pilot.onnx`

Pilot validation on the tiny held-out set:

- threshold `0.5`: recall `1.0`, false-positive rate `0.1667`;
- positive scores: `0.964` to `0.998`;
- negative scores: `0.004` to `0.930`;
- threshold `0.95` separates this tiny validation set, but this is not yet robust enough for deployment.

Reusable helper scripts:

```text
scripts/normalize_openwakeword_workspace.py
scripts/build_openwakeword_features.py
scripts/train_openwakeword_pilot.py
scripts/evaluate_openwakeword_onnx.py
scripts/score_openwakeword_wav.py
```

Pilot ONNX evaluation examples:

```text
.venv-oww/bin/python scripts/evaluate_openwakeword_onnx.py \
  local_data/openwakeword_training/galileo_pilot/galileo_pilot.onnx \
  local_data/openwakeword_training/galileo_initial_features \
  --threshold 0.95
```

End-to-end single-WAV scoring also works:

```text
.venv-oww/bin/python scripts/score_openwakeword_wav.py \
  local_data/openwakeword_training/galileo_pilot/galileo_pilot.onnx \
  local_data/openwakeword_workspace/galileo_initial_16k/positive_test/0001-positive-20261002-144244-positive-galileo.wav \
  --threshold 0.95
```

Observed pilot examples:

- positive test WAV: score `0.989`, detected `true`;
- negative test WAV: score `0.930`, detected `false` at threshold `0.95`.

## Live Raspberry Capture Scoring

The helper below captures on the Raspberry and scores locally on the PC:

```text
.venv-oww/bin/python scripts/score_rpi_openwakeword_capture.py \
  local_data/openwakeword_training/galileo_pilot/galileo_pilot.onnx \
  --label galileo-live \
  --threshold 0.95 \
  --highpass-hz 0
```

Observed live scoring:

- no spoken keyword / room capture: score `0.004`, detected `false`;
- manually timed spoken attempt: score `0.437`, detected `false` at threshold `0.95`;
- spoken ALSA cue (`Front_Center.wav`) contaminated validation and produced false positives;
- short sine beep was not audible enough for the user;
- pure-beep negative with delay: score `0.007`, detected `false`.

Conclusion:

- local ONNX scoring from live Raspberry captures works;
- the current pilot can distinguish some live silence/noise, but live positives are not reliable yet;
- next collection should use a reliable visual cue or confirmed timing, then add those live captures into the training set.

## LED-Guided Live Scoring

SPI was enabled on the Raspberry so the ReSpeaker APA102 LEDs are available:

```text
/dev/spidev0.0
/dev/spidev0.1
```

The repository now includes:

```text
scripts/respeaker_leds.py
```

The live scorer supports `--led-cue`:

```text
.venv-oww/bin/python scripts/score_rpi_openwakeword_capture.py \
  local_data/openwakeword_training/galileo_pilot/galileo_pilot.onnx \
  --label galileo-led-cue \
  --threshold 0.95 \
  --highpass-hz 0 \
  --led-cue
```

LED cue behavior:

- yellow: prepare;
- red: recording window, speak now;
- off: recording finished.

Initial LED-guided results with the first pilot:

- silence LED cue: score `0.026`, detected `false`;
- Galileo LED cue: score `0.025`, detected `false`;
- five Galileo LED series scores: `0.025`, `0.897`, `0.049`, `0.081`, `0.115`.

After adding the LED-guided live samples to a local augmented training set:

- live augmented workspace: `34` positive train, `6` positive test, `18` negative train, `6` negative test;
- new pilot positive holdout: score `0.998`, detected `true`;
- new pilot silence holdout: score `0.600`, detected `false` at threshold `0.95`.

Conclusion:

- LED-guided collection works and is now the preferred live data path;
- the retrained pilot can detect a new live Galileo sample;
- the negative margin is still too narrow, so more negative/noise examples are needed before deployment.

## LED-Guided Batch V3

Additional LED-guided live data was collected locally:

- `10` silence samples;
- `10` positive `Galileo` samples;
- `10` spoken negative samples without saying `Galileo`.

Observed before retraining:

- silence batch produced several near-threshold negatives and `3` false positives at threshold `0.95`;
- spoken-negative batch produced `5` false positives at threshold `0.95`;
- positive batch produced `8/10` detections, with `2` weak positives.

These samples were added as hard examples to a local v3 workspace:

```text
local_data/openwakeword_workspace/galileo_led_batch_v3_16k
```

Counts:

- positive train: `42`
- positive test: `8`
- negative train: `34`
- negative test: `10`

V3 pilot test-set result at threshold `0.95`:

- positive: `7/8` correct, scores `0.004` to `0.998`;
- negative: `10/10` correct, scores `0.003` to `0.938`.

Fresh v3 holdout results:

- silence: score `0.003`, detected `false`;
- spoken negative without `Galileo`: score `0.003`, detected `false`;
- `Galileo`: score `0.998`, detected `true`.

Conclusion:

- v3 is the best pilot so far and is good enough for the next Raspberry inference experiment;
- it is still not final because one positive test sample is missed and one negative test sample is close to threshold;
- next step is to run more fresh holdouts and then attempt Raspberry-side inference deployment.

## Raspberry-Side Inference Diagnostic

Inference dependencies were installed on the Raspberry in:

```text
/home/denny/galileo/venv-oww-infer
```

Installed inference package:

```text
openwakeword==0.6.0
onnxruntime==1.30.0
numpy==2.4.6
scipy==1.17.1
tflite-runtime==2.14.0
```

Model and feature assets were copied outside git:

```text
/home/denny/galileo/models/openwakeword/galileo_v3.onnx
/home/denny/galileo/models/openwakeword/galileo_pilot.onnx.data
/home/denny/galileo/venv-oww-infer/lib/python3.11/site-packages/openwakeword/resources/models/
```

The repository now includes the Raspberry-side live diagnostic:

```text
scripts/rpi_live_openwakeword_score.py
scripts/rpi_continuous_openwakeword_led.py
```

The single-shot diagnostic runs fully on the Raspberry:

- LED cue;
- `arecord` capture at 16 kHz mono through `plughw:0,0`;
- openWakeWord feature extraction;
- ONNX scoring.

Fresh Raspberry-side results at threshold `0.95`:

- silence: score `0.003`, detected `false`;
- `Galileo`: score `0.998`, detected `true`;
- spoken negative without `Galileo`: score `0.806`, detected `false`.

Timing on Pi Zero 2 W:

- recording window: about `3.35s`;
- feature extraction for a 3s clip: about `2.7-3.1s`;
- ONNX classifier inference: about `0.03-0.12s`;
- diagnostic total: about `7.0-7.6s`.

Conclusion:

- Raspberry-side inference works.
- The ONNX classifier is fast enough; feature extraction is the part to optimize before streaming/continuous wake detection.
- Spoken-negative margin is still narrower than desired, so more hard negatives are useful before 24/7 deployment.

## Continuous LED Test

A first continuous Raspberry-side listener was added:

```text
scripts/rpi_continuous_openwakeword_led.py
scripts/install_rpi_wake_led_service.sh
```

It keeps `arecord` open in raw capture mode, maintains a rolling 3s audio window, scores the current window with the v3 ONNX model, and pulses the ReSpeaker LEDs purple when the score passes threshold.

Initial 70s onboard test at threshold `0.95`:

- detections: scores `0.996`, `0.998`, `0.976`;
- normal low scores: around `0.003-0.020`;
- near miss / useful margin sample: score `0.922`, detected `false`;
- feature extraction per scored 3s window: about `1.05s` after warmup.

This is good enough for hands-on sensitivity tests at different distances and voice levels. It is still a diagnostic loop, not the final satellite wake-word service.

Latency analysis and next experiments are tracked separately:

```text
diagnostics/wakeword_latency_analysis.md
```

The current Raspberry has a user `systemd` service installed and enabled:

```text
/home/denny/.config/systemd/user/galileo-wake-led.service
```

`linger` is enabled for user `denny`, so the continuous listener can start at boot without an SSH login. The service runs the continuous listener at threshold `0.95` and pulses the LEDs purple when `Galileo` is detected.

## Path To Deployment

Next steps to reach the wake-word goal:

1. Collect more LED-guided live data.
2. Build an updated manifest with train, validation, and holdout splits.
3. Retrain locally and evaluate multiple thresholds.
4. Promote an ONNX model only when fresh holdout negatives stay comfortably below threshold.
5. Use the continuous LED test to gather sensitivity notes and hard negatives.
6. Add an openWakeWord detector behind `satellite/wakeword/`.
7. Gate the satellite state machine on wake detection, then use VAD for the following utterance.

## Current Dataset Manifest

```text
diagnostics/manifests/galileo_openwakeword_initial.json
```

Counts:

- positive: `33`
- negative: `10`
- noise: `10`
- total: `53`
- train: `42`
- validation: `11`
