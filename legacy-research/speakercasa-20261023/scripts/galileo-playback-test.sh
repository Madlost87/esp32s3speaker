#!/usr/bin/env bash
set -euo pipefail

DEVICE=${1:-hw:0,0}
DURATION_SECONDS=${2:-5}
FREQUENCY_HZ=${3:-880}
AMPLITUDE=${4:-12000}
RATE_HZ=${5:-48000}
OUT=${OUT:-/tmp/galileo_playback_test.wav}

python3 - "$OUT" "$DURATION_SECONDS" "$FREQUENCY_HZ" "$AMPLITUDE" "$RATE_HZ" <<'PY'
import math
import struct
import sys
import wave

out, duration, frequency, amplitude, rate = sys.argv[1:]
duration = float(duration)
frequency = float(frequency)
amplitude = int(amplitude)
rate = int(rate)

frames = []
for index in range(int(rate * duration)):
    sample = int(amplitude * math.sin(2 * math.pi * frequency * index / rate))
    frames.append(struct.pack("<hh", sample, sample))

with wave.open(out, "wb") as wav:
    wav.setnchannels(2)
    wav.setsampwidth(2)
    wav.setframerate(rate)
    wav.writeframes(b"".join(frames))

print(out)
PY

aplay -D "$DEVICE" "$OUT"
