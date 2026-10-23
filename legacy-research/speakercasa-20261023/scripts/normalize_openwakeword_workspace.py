#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import subprocess
from pathlib import Path


CLIP_DIRS = ("positive_train", "positive_test", "negative_train", "negative_test")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Convert an openWakeWord workspace to 16 kHz mono WAV clips."
    )
    parser.add_argument("input_dir", type=Path)
    parser.add_argument("output_dir", type=Path)
    parser.add_argument("--sample-rate", type=int, default=16000)
    parser.add_argument("--highpass-hz", type=int, default=80)
    parser.add_argument("--overwrite", action="store_true")
    return parser.parse_args()


def convert_clip(source: Path, destination: Path, sample_rate: int, highpass_hz: int, overwrite: bool) -> bool:
    destination.parent.mkdir(parents=True, exist_ok=True)
    if destination.exists() and not overwrite:
        return False

    command = [
        "ffmpeg",
        "-hide_banner",
        "-loglevel",
        "error",
        "-y" if overwrite else "-n",
        "-i",
        str(source),
        "-ac",
        "1",
        "-ar",
        str(sample_rate),
        "-sample_fmt",
        "s16",
    ]
    if highpass_hz > 0:
        command.extend(["-af", f"highpass=f={highpass_hz}"])
    command.extend(
        [
        str(destination),
        ]
    )
    subprocess.run(command, check=True)
    return True


def main() -> int:
    args = parse_args()
    counts: dict[str, int] = {}
    converted = 0
    skipped = 0

    for clip_dir in CLIP_DIRS:
        input_clip_dir = args.input_dir / clip_dir
        output_clip_dir = args.output_dir / clip_dir
        wavs = sorted(input_clip_dir.glob("*.wav"))
        counts[clip_dir] = len(wavs)

        for source in wavs:
            destination = output_clip_dir / source.name
            if convert_clip(source, destination, args.sample_rate, args.highpass_hz, args.overwrite):
                converted += 1
            else:
                skipped += 1

    summary = {
        "input_dir": str(args.input_dir),
        "output_dir": str(args.output_dir),
        "sample_rate": args.sample_rate,
        "highpass_hz": args.highpass_hz,
        "counts": counts,
        "converted": converted,
        "skipped": skipped,
    }
    args.output_dir.mkdir(parents=True, exist_ok=True)
    (args.output_dir / "normalization_summary.json").write_text(
        json.dumps(summary, indent=2) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(summary, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
