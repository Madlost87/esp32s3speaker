#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path

import numpy as np
import scipy.io.wavfile
from openwakeword.utils import compute_features_from_generator


CLIP_DIRS = {
    "positive_train": "positive_features_train.npy",
    "positive_test": "positive_features_test.npy",
    "negative_train": "negative_features_train.npy",
    "negative_test": "negative_features_test.npy",
}

def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Build openWakeWord feature arrays from a 16 kHz mono workspace."
    )
    parser.add_argument("workspace_dir", type=Path)
    parser.add_argument("output_dir", type=Path)
    parser.add_argument("--clip-samples", type=int, default=48000)
    parser.add_argument("--batch-size", type=int, default=8)
    parser.add_argument("--ncpu", type=int, default=max(1, (os.cpu_count() or 2) // 2))
    parser.add_argument("--overwrite", action="store_true")
    return parser.parse_args()


def read_fixed_clip(path: Path, clip_samples: int) -> np.ndarray:
    sample_rate, data = scipy.io.wavfile.read(path)
    if sample_rate != 16000:
        raise ValueError(f"{path} has sample rate {sample_rate}, expected 16000")
    if data.ndim != 1:
        raise ValueError(f"{path} is not mono")

    data = data.astype(np.int16)
    if data.shape[0] > clip_samples:
        return data[:clip_samples]
    if data.shape[0] < clip_samples:
        return np.pad(data, (0, clip_samples - data.shape[0]))
    return data


def fixed_clip_batches(clips: list[Path], clip_samples: int, batch_size: int):
    for index in range(0, len(clips), batch_size):
        batch = clips[index:index + batch_size]
        yield np.vstack([read_fixed_clip(path, clip_samples) for path in batch])


def main() -> int:
    args = parse_args()
    args.output_dir.mkdir(parents=True, exist_ok=True)

    summary = {
        "workspace_dir": str(args.workspace_dir),
        "output_dir": str(args.output_dir),
        "clip_samples": args.clip_samples,
        "batch_size": args.batch_size,
        "ncpu": args.ncpu,
        "features": {},
    }

    for clip_dir, output_name in CLIP_DIRS.items():
        clips = sorted((args.workspace_dir / clip_dir).glob("*.wav"))
        if not clips:
            raise SystemExit(f"No WAV files found in {args.workspace_dir / clip_dir}")

        output_file = args.output_dir / output_name
        if output_file.exists() and not args.overwrite:
            summary["features"][clip_dir] = {
                "clips": len(clips),
                "output": str(output_file),
                "status": "skipped",
            }
            continue

        batch_size = min(args.batch_size, len(clips))
        generator = fixed_clip_batches(clips, args.clip_samples, batch_size)
        compute_features_from_generator(
            generator,
            n_total=len(clips),
            clip_duration=args.clip_samples,
            output_file=str(output_file),
            device="cpu",
            ncpu=args.ncpu,
        )
        summary["features"][clip_dir] = {
            "clips": len(clips),
            "output": str(output_file),
            "status": "built",
        }

    summary_path = args.output_dir / "feature_summary.json"
    summary_path.write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(summary, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
