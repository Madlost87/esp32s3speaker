# Galileo Playback Test

Date: 2026-10-01

## Test Setup

- Device: Raspberry Pi Zero 2 W with KEYESTUDIO ReSpeaker 2-Mic Pi HAT / WM8960
- ALSA playback device: `hw:0,0`
- Output: amplified speaker connected to the HAT jack
- Test signal: stereo sine tone, 880 Hz, 5 seconds, 48 kHz, 16-bit
- Test WAV path on Raspberry: `/tmp/galileo_playback_louder.wav`

## ALSA Result

`aplay` completed without reported errors or xruns:

```text
Playing WAVE '/tmp/galileo_playback_louder.wav' : Signed 16 bit Little Endian, Rate 48000 Hz, Stereo
```

## Mixer Settings That Worked

The following WM8960 mixer settings produced audible output from the amplified speaker:

- `Left Output Mixer PCM`: `on`
- `Right Output Mixer PCM`: `on`
- `Headphone`: left/right `115`, `-6.00 dB`
- `Playback`: left/right `235`, `-10.00 dB`

These settings were saved on the Raspberry with:

```text
sudo alsactl store 0
```

## Interpretation

- WM8960 playback through the HAT jack is working.
- `hw:0,0` is the correct playback device for the HAT.
- The HAT jack can drive the connected amplified speaker.
- The current profile is suitable as an initial playback baseline for later TTS tests.

## Helper Script

The repository now includes:

```text
scripts/galileo-playback-test.sh
```

Run it on the Raspberry to generate and play a temporary stereo tone:

```text
scripts/galileo-playback-test.sh
```

Optional arguments:

```text
scripts/galileo-playback-test.sh DEVICE DURATION_SECONDS FREQUENCY_HZ AMPLITUDE RATE_HZ
```
