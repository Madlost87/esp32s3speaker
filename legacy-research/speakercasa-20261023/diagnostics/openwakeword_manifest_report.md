# Galileo openWakeWord Manifest

Date: 2026-10-02

Manifest on Raspberry:

```text
/home/denny/galileo/dataset/manifests/galileo_openwakeword_initial.json
```

Repository copy:

```text
diagnostics/manifests/galileo_openwakeword_initial.json
```

## Contents

- Positive `galileo`: `33`
- Negative speech: `10`
- Noise: `10`
- Total: `53`
- Train split: `42`
- Validation split: `11`

Split rule:

- deterministic shuffle with seed `42`
- every fifth item assigned to validation

## Notes

- WAV files remain on the Raspberry and are not committed.
- The manifest uses absolute Raspberry paths.
- Older low-level positive samples and the initial clipped/noisy boot-check sample are excluded.

## Next Step

Prepare the openWakeWord training environment and decide whether training will run on this PC or another more capable machine.
