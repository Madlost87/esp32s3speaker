from __future__ import annotations

import json
import subprocess
import time
from dataclasses import dataclass, asdict
from pathlib import Path

from .audio.capture import CaptureConfig


@dataclass(frozen=True)
class DatasetSample:
    sample_id: str
    category: str
    label: str
    distance: str
    environment: str
    speaker: str
    device: str
    sample_rate_hz: int
    channels: int
    sample_format: str
    duration_seconds: float
    created_monotonic_ns: int
    wav_path: str


def category_path(root: Path, category: str, label: str) -> Path:
    if category == "positive":
        return root / "positive" / label
    if category in {"negative", "noise"}:
        return root / category
    raise ValueError("category must be one of: positive, negative, noise")


def record_dataset_sample(
    root: Path,
    category: str,
    label: str,
    distance: str,
    environment: str,
    speaker: str,
    duration_seconds: float,
    capture: CaptureConfig,
) -> DatasetSample:
    created = time.strftime("%Y%m%d-%H%M%S")
    monotonic_ns = time.monotonic_ns()
    safe_label = label.replace("/", "_").replace(" ", "_").lower()
    sample_id = f"{created}-{category}-{safe_label}"
    out_dir = category_path(root, category, safe_label)
    out_dir.mkdir(parents=True, exist_ok=True)
    wav_path = out_dir / f"{sample_id}.wav"
    metadata_path = out_dir / f"{sample_id}.json"

    subprocess.run(
        [
            "arecord",
            "-D",
            capture.device,
            "-f",
            capture.sample_format,
            "-r",
            str(capture.sample_rate_hz),
            "-c",
            str(capture.channels),
            "-d",
            str(int(duration_seconds)),
            str(wav_path),
        ],
        check=True,
    )

    sample = DatasetSample(
        sample_id=sample_id,
        category=category,
        label=label,
        distance=distance,
        environment=environment,
        speaker=speaker,
        device=capture.device,
        sample_rate_hz=capture.sample_rate_hz,
        channels=capture.channels,
        sample_format=capture.sample_format,
        duration_seconds=duration_seconds,
        created_monotonic_ns=monotonic_ns,
        wav_path=str(wav_path),
    )
    metadata_path.write_text(json.dumps(asdict(sample), indent=2) + "\n", encoding="utf-8")
    return sample
