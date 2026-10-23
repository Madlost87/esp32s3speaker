#!/usr/bin/env python3
import json
import math
import struct
import sys
import wave
from pathlib import Path


def main() -> int:
    if len(sys.argv) != 2:
        print(f"usage: {Path(sys.argv[0]).name} FILE.wav", file=sys.stderr)
        return 2

    path = Path(sys.argv[1])
    with wave.open(str(path), "rb") as wav:
        channels = wav.getnchannels()
        rate = wav.getframerate()
        sample_width = wav.getsampwidth()
        frames = wav.getnframes()
        data = wav.readframes(frames)

    if sample_width != 2:
        raise SystemExit(f"unsupported sample width: {sample_width} bytes")

    samples = struct.unpack("<" + "h" * (len(data) // 2), data)
    per_channel = [[] for _ in range(channels)]
    for index, sample in enumerate(samples):
        per_channel[index % channels].append(sample)

    result = {
        "path": str(path),
        "size_bytes": path.stat().st_size,
        "duration_seconds": frames / rate,
        "sample_rate_hz": rate,
        "bit_depth": sample_width * 8,
        "channels": channels,
        "frames": frames,
        "channel_stats": [],
    }

    for channel, values in enumerate(per_channel):
        count = len(values)
        peak = max((abs(v) for v in values), default=0)
        mean = sum(values) / count if count else 0
        rms = math.sqrt(sum(v * v for v in values) / count) if count else 0
        clipped = sum(1 for v in values if v in (-32768, 32767))
        result["channel_stats"].append(
            {
                "channel": channel,
                "samples": count,
                "rms": rms,
                "rms_dbfs": 20 * math.log10(rms / 32768) if rms > 0 else None,
                "peak": peak,
                "peak_dbfs": 20 * math.log10(peak / 32768) if peak > 0 else None,
                "dc_offset_samples": mean,
                "dc_offset_percent_fullscale": mean / 32768 * 100,
                "clipped_samples": clipped,
                "clipped_percent": clipped / count * 100 if count else 0,
            }
        )

    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
