# Galileo Left/Right Spoken Microphone Test

Date: 2026-10-01

## Test Setup

- Device: Raspberry Pi Zero 2 W with KEYESTUDIO ReSpeaker 2-Mic Pi HAT / WM8960
- ALSA capture device: `hw:0,0`
- Recording path on Raspberry: `/home/denny/galileo/recordings/left_right_spoken_test.wav`
- Local analysis source: temporary copy in `/tmp`, not committed
- Format: WAV, 16 kHz, 16-bit, stereo
- Duration: 12 seconds
- Intended procedure:
  - 0-6s: speak close to left microphone
  - 6-12s: speak close to right microphone

## ALSA Result

`arecord` completed without reported errors or xruns.

## Window Analysis

### 0-6 seconds

- Channel 0 RMS: `20.41`, `-64.11 dBFS`
- Channel 1 RMS: `16.85`, `-65.77 dBFS`
- Channel 0 over channel 1: `+1.66 dB`
- Peak channel 0: `280`, `-41.37 dBFS`
- Peak channel 1: `230`, `-43.07 dBFS`
- Clipping: `0`

### 6-12 seconds

- Channel 0 RMS: `1.09`, `-89.57 dBFS`
- Channel 1 RMS: `1.04`, `-89.95 dBFS`
- Channel 0 over channel 1: `+0.38 dB`
- Peak channel 0: `5`, `-76.33 dBFS`
- Peak channel 1: `4`, `-78.27 dBFS`
- Clipping: `0`

## Interpretation

- The recording path works and reports no ALSA errors.
- The first half contains low-level signal on both channels.
- The second half is almost silence, so this run does not conclusively validate right-side microphone separation.
- The current capture gain is conservative/low, consistent with the previous microphone test.

## Next Repeat

Repeat the test with a clearer protocol:

- 3 seconds silence
- 5 seconds close to left microphone
- 2 seconds silence
- 5 seconds close to right microphone
- Speak loudly and within roughly 5-10 cm of each microphone.

No permanent gain changes should be applied until this repeat is complete.

## Repeat 2026-10-01

Additional recordings were made as separate left-only and right-only tests to avoid timing ambiguity.

Remote recording paths:

- `/home/denny/galileo/recordings/left_only_repeat2.wav`
- `/home/denny/galileo/recordings/right_only_repeat2.wav`

Local analysis sources were temporary copies in `/tmp`, not committed.

### Mixer Baseline

Relevant baseline WM8960 mixer values:

- `Capture`: left/right `39`, `+12.00 dB`, enabled
- `Left Input Boost Mixer LINPUT1`: `0`, `0.00 dB`
- `Right Input Boost Mixer RINPUT1`: `0`, `0.00 dB`
- `ADC Data Output Select`: `Left Data = Left ADC; Right Data = Right ADC`

### Separate Spoken Tests

Left-only recording:

- Channel 0 RMS: `20.39`, `-64.12 dBFS`
- Channel 1 RMS: `16.81`, `-65.80 dBFS`
- Channel 0 over channel 1: `+1.67 dB`
- Peak channel 0: `273`, `-41.59 dBFS`
- Peak channel 1: `227`, `-43.19 dBFS`
- Clipping: `0`

Right-only recording:

- Channel 0 RMS: `20.41`, `-64.11 dBFS`
- Channel 1 RMS: `16.83`, `-65.79 dBFS`
- Channel 0 over channel 1: `+1.68 dB`
- Peak channel 0: `287`, `-41.15 dBFS`
- Peak channel 1: `237`, `-42.81 dBFS`
- Clipping: `0`

### Temporary Boost Test

Runtime-only mixer change tested:

- `Capture`: left/right `55`, `+24.00 dB`
- `Left Input Boost Mixer LINPUT1`: `1`, `+13.00 dB`
- `Right Input Boost Mixer RINPUT1`: `1`, `+13.00 dB`

The temporary change was not stored with `alsactl store`.

Boosted left-only recording:

- Channel 0 RMS: `20.40`, `-64.12 dBFS`
- Channel 1 RMS: `16.81`, `-65.80 dBFS`
- Channel 0 over channel 1: `+1.68 dB`
- Peak channel 0: `288`, `-41.12 dBFS`
- Peak channel 1: `237`, `-42.81 dBFS`
- Clipping: `0`

Boosted right-only recording:

- Channel 0 RMS: `20.42`, `-64.11 dBFS`
- Channel 1 RMS: `16.84`, `-65.78 dBFS`
- Channel 0 over channel 1: `+1.68 dB`
- Peak channel 0: `308`, `-40.54 dBFS`
- Peak channel 1: `255`, `-42.18 dBFS`
- Clipping: `0`

After the boosted tests, the mixer was restored to the baseline values above.

## Repeat Interpretation

- ALSA capture continues to complete successfully with no reported xruns.
- The left-only and right-only spoken tests are effectively identical.
- The boosted test is also effectively identical to baseline, despite the runtime mixer values changing.
- The consistent result is a low-level signal with channel 0 about `+1.7 dB` above channel 1.
- This does not validate physical left/right microphone separation.
- Current evidence suggests the WAV capture path is alive, but the expected microphone input is not responding to spoken audio or to the tested WM8960 input gain path.

## Next Diagnostic Step

Investigate why the WM8960 capture path is not reacting to the microphone capsules:

- Inspect whether the HAT has hardware switches, jumpers, or solder bridges for microphone input/routing.
- Compare the KEYESTUDIO HAT documentation against the active `wm8960-soundcard` overlay and mixer controls.
- Test alternate WM8960 input routes only as temporary runtime changes.
- Run a close physical tap/scratch test on each microphone capsule and the board, then analyze peaks per channel.
- Do not store mixer settings permanently until real microphone response is confirmed.

## Capture Routing Fix 2026-10-01

The missing capture path was identified as the WM8960 input mixer boost switches.

Controls that were required for real microphone response:

- `Left Input Mixer Boost`: `on`
- `Right Input Mixer Boost`: `on`

The earlier tests changed `Capture` and `Left/Right Input Boost Mixer LINPUT1/RINPUT1`, but left these switches off. With these switches off, ALSA produced WAV files but did not react usefully to spoken audio.

### Saturation Test

An intentionally high-gain runtime test confirmed that the microphones/capture path became active:

- `Capture`: left/right `63`
- `ADC PCM`: left/right `255`
- `Left Input Mixer Boost`: `on`
- `Right Input Mixer Boost`: `on`
- `Left Input Boost Mixer LINPUT1`: `1`
- `Right Input Boost Mixer RINPUT1`: `1`

Result: the recording clipped heavily, proving the route was active but the gain was unusable.

### Working Close-Voice Test

Recording path on Raspberry:

- `/home/denny/galileo/recordings/voice_close_input_mixer_repeat.wav`

Mixer settings used:

- `Capture`: left/right `20`, `-2.25 dB`
- `ADC PCM`: left/right `215`, `+10.00 dB`
- `Left Boost Mixer LINPUT1`: `on`
- `Right Boost Mixer RINPUT1`: `on`
- `Left Input Boost Mixer LINPUT1`: `0`, `0.00 dB`
- `Right Input Boost Mixer RINPUT1`: `0`, `0.00 dB`
- `Left Input Mixer Boost`: `on`
- `Right Input Mixer Boost`: `on`
- `ADC High Pass Filter`: `on`
- `Noise Gate`: `off`

Measured result:

- Channel 0 RMS: `981.72`, `-30.47 dBFS`
- Channel 1 RMS: `688.15`, `-33.56 dBFS`
- Channel 0 peak: `1970`, `-24.42 dBFS`
- Channel 1 peak: `1645`, `-25.99 dBFS`
- Clipping: `0`

Listening result:

- The original file and a temporary amplified listening copy were played through the HAT jack speaker path.
- The amplified listening copy contained recognizable voice.

The working mixer settings were saved on the Raspberry with:

```text
sudo alsactl store 0
```

## Updated Interpretation

- Capture is now confirmed to work with real microphone audio.
- Playback is already confirmed separately.
- The next microphone task is no longer basic bring-up; it is calibration:
  - record `voice_normal.wav`;
  - re-run left/right separation with the corrected routing;
  - choose a conservative permanent gain profile;
  - verify speaker leakage/full-duplex behavior.
