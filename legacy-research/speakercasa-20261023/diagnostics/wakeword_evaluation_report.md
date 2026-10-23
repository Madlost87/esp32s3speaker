# Galileo Wake Word Evaluation

Date: 2026-10-01

Wake word target:

```text
Galileo
```

## Requirements

- Local inference on Raspberry Pi Zero 2 W
- Low CPU and RAM
- Custom wake word support
- Italian-friendly phrase/model path
- No large LLM on the Raspberry
- Compatible with the existing Galileo audio path:
  - mono PCM
  - 16 kHz
  - 16-bit
  - VAD-gated stream

## Candidate: Picovoice Porcupine

Primary sources checked:

- Picovoice Raspberry Pi quick start
- Picovoice C quick start
- Picovoice Model API documentation
- Picovoice Porcupine GitHub repository

Observed fit:

- Explicit Raspberry Pi support includes Raspberry Pi Zero / Zero 2 W.
- C, Python, and other SDKs are available.
- Custom wake word models are created as `.ppn` files.
- The Model API supports `it` for Italian and `raspberry-pi` as a target platform.
- On-device inference is supported.

Tradeoffs:

- Requires a Picovoice AccessKey.
- Custom wake-word generation depends on Picovoice Console/API.
- Licensing/account constraints must be accepted before committing.

Assessment:

- Best immediate robustness path for Galileo if AccessKey/licensing are acceptable.
- Recommended first integration path because the platform support explicitly covers Raspberry Pi Zero-class boards.

## Candidate: openWakeWord

Primary sources checked:

- `dscripka/openWakeWord` GitHub README
- openWakeWord custom model configuration example

Observed fit:

- Open-source wake-word framework.
- Supports custom wake-word model training.
- Produces local models suitable for on-device inference.
- Existing project documentation includes custom training workflows.

Tradeoffs:

- Custom `Galileo` model quality depends on training data and evaluation.
- Training is more work than Porcupine's hosted model generation.
- Needs careful testing for false accepts/rejects on Pi Zero 2 W.

Assessment:

- Best open-source fallback path.
- Good fit if avoiding AccessKey/vendor dependency is more important than immediate robustness.

## Candidate: sherpa-onnx Keyword Spotting

Primary sources checked:

- sherpa-onnx keyword spotting documentation
- sherpa-onnx README

Observed fit:

- Supports keyword spotting.
- Supports ARM / Raspberry Pi targets broadly.
- Part of a broader offline speech toolkit.

Tradeoffs:

- Heavier and broader than a dedicated wake-word engine.
- Needs a deeper prototype before committing on Pi Zero 2 W.

Assessment:

- Keep as an evaluation candidate, not the first implementation path.

## Decision

Primary path:

```text
Porcupine custom keyword: "Galileo"
```

Fallback:

```text
openWakeWord custom Galileo model
```

Reasoning:

- Porcupine has explicit Raspberry Pi Zero-class support and custom keyword tooling.
- It is the most likely to provide a stable first wake-word implementation quickly.
- openWakeWord remains attractive if vendor/account dependency is unacceptable.

## Blocker / Required Human Input

Porcupine integration requires:

- Picovoice AccessKey
- A Raspberry Pi `.ppn` model for the phrase `Galileo`
- Matching language model, likely Italian if the intended pronunciation is Italian

No AccessKey or model file is currently present in the project, and neither should be committed to git.

## Next Action

Add a wake-word abstraction and placeholder integration point in the satellite state machine. Do not activate Porcupine until credentials/model files are provided outside git.
