# Galileo Wake-Word Board Measurements

Date: 2026-10-03

Board reached at:

```text
192.168.1.151
galileo.local
```

## Service State

```text
galileo-wake-led.service: active
enabled: yes
linger: yes
```

Service file:

```text
/home/denny/.config/systemd/user/galileo-wake-led.service
```

ExecStart:

```text
/home/denny/galileo/venv-oww-infer/bin/python /home/denny/galileo/bin/rpi_continuous_openwakeword_led.py /home/denny/galileo/models/openwakeword/galileo_v3.onnx --threshold 0.95
```

Child capture process:

```text
arecord -D plughw:0,0 -f S16_LE -r 16000 -c 1 -t raw
```

## Resource Snapshot

Repeated process samples showed:

```text
python wake listener: about 85-87% CPU, about 190-193 MB RSS, about 45% MEM
arecord: about 0.6% CPU, about 2.7 MB RSS
```

System snapshot:

```text
temperature: 47.8 C
throttled: 0x0
RAM: 416 MB total, 264 MB used, 152 MB available
swap: 511 MB total, 1 MB used
load average: 0.99, 0.36, 0.13
```

Interpretation:

- The service is running and boot-enabled.
- The ALSA capture child is cheap.
- The Python/openWakeWord feature extraction loop is expensive on Pi Zero 2 W.
- This confirms the current listener is a diagnostic/field-test loop, not yet the final 24/7 implementation.

## ALSA Devices

Capture:

```text
card 0: wm8960-soundcard, device 0
```

Playback:

```text
card 0: wm8960-soundcard, device 0
card 1: vc4-hdmi, device 0
```

## Mixer Profile

Relevant controls:

```text
Capture: 28 / 28, +3.75 dB, on
ADC PCM: 230 / 230, +17.50 dB
Left Boost Mixer LINPUT1: on
Right Boost Mixer RINPUT1: on
Left Input Mixer Boost: on
Right Input Mixer Boost: on
```

## Follow-Up

Priority follow-up:

1. Reduce CPU by replacing repeated full-window feature extraction with a streaming/incremental path, if feasible.
2. Test a lower score frequency only as an experiment, because it trades latency for CPU.
3. Avoid treating the current service as the final 24/7 wake-word service until CPU and memory are improved.
