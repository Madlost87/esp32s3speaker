# GALILEO SATELLITE VALIDATION

Date: 2026-10-01

## Hardware

- Raspberry: Raspberry Pi Zero 2 W
- ReSpeaker: KEYESTUDIO ReSpeaker 2-Mic Pi HAT v1.0 / WM8960
- Speaker: amplified speaker connected to HAT jack

## System

- OS: Debian GNU/Linux 12 bookworm
- Kernel: `6.12.25+rpt-rpi-v8`
- CPU: Raspberry Pi Zero 2 W / ARM64
- RAM: 416 MiB observed
- Storage: 7.4 GiB microSD observed
- Temperature: about 42 C during initial diagnostics
- Undervoltage/throttling: `throttled=0x0` during initial diagnostics
- Wi-Fi: working
- SSH: working as user `denny`

## Audio

- Codec: WM8960
- Driver/overlay: Raspberry Pi `wm8960-soundcard`
- ALSA capture: `hw:0,0`, stereo
- ALSA playback: `hw:0,0`, stereo
- Tested formats: `S16_LE`, 16 kHz and 48 kHz, stereo

### Microphones

- Initial ALSA capture worked but did not react usefully to voice.
- Root cause found: `Left Input Mixer Boost` and `Right Input Mixer Boost` were off.
- Corrected capture route:
  - `Left Input Mixer Boost`: `on`
  - `Right Input Mixer Boost`: `on`
  - `Left Boost Mixer LINPUT1`: `on`
  - `Right Boost Mixer RINPUT1`: `on`
- Working close-voice recording:
  - `/home/denny/galileo/recordings/voice_close_input_mixer_repeat.wav`
- Close-voice stats:
  - Channel 0 RMS `-30.47 dBFS`, peak `-24.42 dBFS`, clipping `0`
  - Channel 1 RMS `-33.56 dBFS`, peak `-25.99 dBFS`, clipping `0`
- Listening test: recognizable voice heard from temporary amplified playback copy.
- Normal-voice recording:
  - `/home/denny/galileo/recordings/voice_normal.wav`
- Normal-voice stats:
  - Channel 0 RMS `-30.62 dBFS`, peak `-27.37 dBFS`, clipping `0`
  - Channel 1 RMS `-33.72 dBFS`, peak `-29.60 dBFS`, clipping `0`
- Corrected-routing stereo test:
  - `/home/denny/galileo/recordings/stereo_test_corrected_routing.wav`
  - Left/right spatial separation remains weak; both channels respond similarly.
  - Analysis should remove DC offset before comparing channel levels.

Current microphone status:

- MIC LEFT: partial pass; capture works, separation still needs corrected-routing retest
- MIC RIGHT: partial pass; capture works, separation still needs corrected-routing retest
- CAPTURE: pass for real voice
- QUALITY: partial pass; normal voice level is usable, DC offset and channel separation still need calibration

### Playback

- Playback path through HAT jack works.
- Working playback mixer:
  - `Left Output Mixer PCM`: `on`
  - `Right Output Mixer PCM`: `on`
  - `Headphone`: left/right `115`, `-6.00 dB`
  - `Playback`: left/right `235`, `-10.00 dB`
- Playback helper:
  - `scripts/galileo-playback-test.sh`

### Simultaneous Audio

- Full duplex: pass in initial test
- Speaker leakage: not macroscopically visible at moderate test level
- Full-duplex recording:
  - `/home/denny/galileo/recordings/speaker_echo_test.wav`
- Silence/noise-floor recording:
  - `/home/denny/galileo/recordings/silence.wav`

## Audio Files Produced

Personal voice recordings remain on the Raspberry and are not committed:

- `/home/denny/galileo/recordings/voice_close_input_mixer_repeat.wav`
- `/home/denny/galileo/recordings/voice_normal.wav`
- `/home/denny/galileo/recordings/stereo_test_corrected_routing.wav`
- `/home/denny/galileo/recordings/silence.wav`
- `/home/denny/galileo/recordings/speaker_echo_test.wav`
- `/home/denny/galileo/recordings/onboard_led_guided_input_mixer_moderate.wav`
- `/home/denny/galileo/recordings/onboard_led_guided_input_mixer_boost.wav`

## Software

- Satellite skeleton: started
- Capture/preprocessing command: `python3 -m satellite capture-stats --duration 5`
- Raspberry test result: command ran successfully against `hw:0,0`
- State machine: initial diagnostic state loop implemented
- State machine test:
  - `IDLE -> LISTENING -> PROCESSING -> IDLE`
  - One spoken phrase produced one clean cycle after adding post-processing cooldown
- VAD: initial energy-based diagnostic implemented
- VAD Raspberry test:
  - Detected `speech_start` and `speech_end`
  - Structured silence/speech/noise tests passed with current thresholds
- Wake word engine: primary path selected as openWakeWord custom `Galileo` model
- Galileo custom wake feasibility: feasible through real ReSpeaker dataset plus synthetic/augmented data; Porcupine kept as optional fallback
- Dataset recorder: implemented and tested with WAV + JSON sidecar under `/home/denny/galileo/dataset/`
- Dataset capture profile: `Capture 28`, `ADC PCM 230`, saved with `alsactl store 0`
- Dataset current total: `64` WAV files on Raspberry; first clean subset is about `50` files.
- openWakeWord initial manifest: `53` files, `42` train / `11` validation
- openWakeWord local environment: inference and CPU pilot-training dependencies installed in `.venv-oww`
- openWakeWord Raspberry workspace: created at `/home/denny/galileo/openwakeword_workspace/galileo_initial`
- openWakeWord local pilot: CPU feature generation, small DNN training, and ONNX export succeeded; pilot needs more data/augmentation before deployment
- openWakeWord live capture scoring: Raspberry capture plus local ONNX scoring works; current pilot is not reliable enough on live positives
- ReSpeaker LED cue: SPI enabled on the Raspberry; APA102 LEDs verified and integrated into live capture scoring
- openWakeWord LED-guided v3 pilot: fresh holdouts passed for silence, spoken non-keyword, and `Galileo`; still needs more holdout coverage before promotion
- Raspberry-side openWakeWord inference: v3 ONNX model runs locally on the Pi; `Galileo` live score `0.998`, silence `0.003`, spoken negative `0.806`
- Continuous Raspberry-side LED listener: rolling-window diagnostic pulses ReSpeaker LEDs purple on `Galileo`; initial detections scored `0.996`, `0.998`, and `0.976`
- Boot service: `galileo-wake-led.service` is enabled for user `denny`; linger is enabled so it can start without SSH login
- Python environment: satellite runtime not created; local `.venv-oww` exists for openWakeWord setup checks
- Services: not created
- Git: local `.git-local` repository in the project workspace

## Performance

- Idle CPU: not yet measured for final service
- Capture CPU: not yet measured
- RAM usage: not yet measured for final service
- Audio latency: not yet measured
- Known bottlenecks: Pi Zero 2 W resource limits; microphone calibration incomplete

## Status

- [ ] hardware validated
- [x] microphones objectively tested
- [x] microphone recording listened/testable
- [x] speaker validated
- [x] full duplex tested
- [x] audio pipeline ready
- [x] Galileo software base ready
- [x] VAD ready
- [x] wake word path selected
- [x] dataset recorder ready

## Issues

- Left/right microphone separation is weak even with corrected routing.
- Normal-distance voice capture has been recorded and played back; listening confirmation is pending.
- Capture has a significant DC offset.
- Full-duplex works in initial test; leakage should be retested with realistic TTS volume.
- Current gain is a working baseline, not final calibration.

## Next Action

Use the continuous purple-LED listener for distance/volume tests, while collecting more hard spoken negatives.

## Final Classification

🟡 FUNCTIONAL — OPTIMIZATION REQUIRED
