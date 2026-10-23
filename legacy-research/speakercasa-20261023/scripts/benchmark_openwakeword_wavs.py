#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import json
import time
from dataclasses import dataclass
from pathlib import Path

import numpy as np
import onnxruntime as ort
import scipy.io.wavfile
from openwakeword.utils import AudioFeatures


@dataclass(frozen=True)
class ScoredFile:
    path: Path
    split: str
    label: str
    category: str
    expected_positive: bool
    score: float
    duration_seconds: float


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Benchmark Galileo openWakeWord ONNX on WAV workspaces.")
    parser.add_argument("onnx_model", type=Path)
    parser.add_argument("workspace", type=Path)
    parser.add_argument("--output-dir", type=Path, default=Path("diagnostics"))
    parser.add_argument("--prefix", default="wakeword")
    parser.add_argument("--clip-samples", type=int, default=48000)
    parser.add_argument("--batch-size", type=int, default=8)
    parser.add_argument(
        "--splits",
        nargs="+",
        default=["positive_test", "negative_test", "positive_train", "negative_train"],
        help="Workspace split directories to score.",
    )
    parser.add_argument("--threshold-start", type=float, default=0.50)
    parser.add_argument("--threshold-stop", type=float, default=0.99)
    parser.add_argument("--threshold-step", type=float, default=0.05)
    parser.add_argument("--primary-threshold", type=float, default=0.95)
    parser.add_argument("--negative-hours", type=float, default=0.0)
    return parser.parse_args()


def read_fixed_clip(path: Path, clip_samples: int) -> tuple[np.ndarray, float]:
    sample_rate, data = scipy.io.wavfile.read(path)
    if sample_rate != 16000:
        raise ValueError(f"{path} has sample rate {sample_rate}, expected 16000")
    if data.ndim != 1:
        raise ValueError(f"{path} is not mono")
    data = data.astype(np.int16)
    duration_seconds = data.shape[0] / sample_rate
    if data.shape[0] > clip_samples:
        data = data[:clip_samples]
    elif data.shape[0] < clip_samples:
        data = np.pad(data, (0, clip_samples - data.shape[0]))
    return data, duration_seconds


def infer_category(path: Path) -> str:
    name = path.name.lower()
    if "speech-no-galileo" in name or "normal_speech" in name:
        return "hard_negative"
    if "noise" in name or "silence" in name:
        return "noise"
    if "speaker" in name or "echo" in name:
        return "speaker_echo"
    if "tv" in name:
        return "tv"
    if "positive" in path.parent.name:
        return "positive"
    return "negative"


def find_wavs(workspace: Path, split_dirs: list[str]) -> list[Path]:
    paths: list[Path] = []
    for split in split_dirs:
        paths.extend(sorted((workspace / split).glob("*.wav")))
    return paths


def score_workspace(args: argparse.Namespace) -> tuple[list[ScoredFile], dict[str, float]]:
    wavs = find_wavs(args.workspace, args.splits)
    if not wavs:
        raise SystemExit(f"no WAV files found in {args.workspace}")

    audio_rows: list[np.ndarray] = []
    durations: dict[Path, float] = {}
    for wav in wavs:
        audio, duration = read_fixed_clip(wav, args.clip_samples)
        audio_rows.append(audio)
        durations[wav] = duration

    timings: dict[str, float] = {}
    feature_start = time.monotonic()
    features = AudioFeatures(device="cpu").embed_clips(np.stack(audio_rows), batch_size=args.batch_size)
    timings["feature_seconds"] = time.monotonic() - feature_start

    infer_start = time.monotonic()
    session = ort.InferenceSession(str(args.onnx_model), providers=["CPUExecutionProvider"])
    input_name = session.get_inputs()[0].name
    scores: list[float] = []
    for row in features.astype(np.float32):
        scores.append(float(session.run(None, {input_name: row[None, :, :]})[0].reshape(-1)[0]))
    timings["inference_seconds"] = time.monotonic() - infer_start

    scored: list[ScoredFile] = []
    for wav, score in zip(wavs, scores, strict=True):
        split = wav.parent.name
        expected_positive = split.startswith("positive")
        scored.append(
            ScoredFile(
                path=wav,
                split=split,
                label="positive" if expected_positive else "negative",
                category=infer_category(wav),
                expected_positive=expected_positive,
                score=score,
                duration_seconds=durations[wav],
            )
        )
    return scored, timings


def metrics_for(scored: list[ScoredFile], threshold: float, negative_hours: float) -> dict[str, float | int]:
    tp = fp = fn = tn = 0
    for item in scored:
        predicted = item.score >= threshold
        if item.expected_positive and predicted:
            tp += 1
        elif item.expected_positive and not predicted:
            fn += 1
        elif not item.expected_positive and predicted:
            fp += 1
        else:
            tn += 1
    recall = tp / (tp + fn) if tp + fn else 0.0
    precision = tp / (tp + fp) if tp + fp else 0.0
    fpr = fp / (fp + tn) if fp + tn else 0.0
    miss_rate = fn / (tp + fn) if tp + fn else 0.0
    false_accepts_per_hour = fp / negative_hours if negative_hours > 0 else 0.0
    return {
        "threshold": threshold,
        "tp": tp,
        "fp": fp,
        "fn": fn,
        "tn": tn,
        "recall": recall,
        "precision": precision,
        "false_positive_rate": fpr,
        "miss_rate": miss_rate,
        "false_accepts_per_hour": false_accepts_per_hour,
    }


def threshold_values(start: float, stop: float, step: float) -> list[float]:
    values: list[float] = []
    current = start
    while current <= stop + 1e-9:
        values.append(round(current, 4))
        current += step
    if stop not in values:
        values.append(round(stop, 4))
    return values


def write_per_file(path: Path, scored: list[ScoredFile], primary_threshold: float) -> None:
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=[
                "path",
                "split",
                "label",
                "category",
                "expected_positive",
                "score",
                "detected_at_primary_threshold",
                "duration_seconds",
            ],
        )
        writer.writeheader()
        for item in scored:
            writer.writerow(
                {
                    "path": str(item.path),
                    "split": item.split,
                    "label": item.label,
                    "category": item.category,
                    "expected_positive": item.expected_positive,
                    "score": f"{item.score:.9f}",
                    "detected_at_primary_threshold": item.score >= primary_threshold,
                    "duration_seconds": f"{item.duration_seconds:.3f}",
                }
            )


def write_thresholds(path: Path, rows: list[dict[str, float | int]]) -> None:
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        for row in rows:
            writer.writerow(row)


def write_report(
    path: Path,
    args: argparse.Namespace,
    scored: list[ScoredFile],
    timings: dict[str, float],
    threshold_rows: list[dict[str, float | int]],
) -> None:
    primary = metrics_for(scored, args.primary_threshold, args.negative_hours)
    hardest_negatives = sorted((item for item in scored if not item.expected_positive), key=lambda item: item.score, reverse=True)[:12]
    weakest_positives = sorted((item for item in scored if item.expected_positive), key=lambda item: item.score)[:12]
    best_zero_fp = [row for row in threshold_rows if row["fp"] == 0]

    lines = [
        "# Galileo Wake-Word Benchmark",
        "",
        f"Model: `{args.onnx_model}`",
        f"Workspace: `{args.workspace}`",
        f"Primary threshold: `{args.primary_threshold}`",
        "",
        "## Primary Metrics",
        "",
        "| metric | value |",
        "| --- | ---: |",
    ]
    for key in ["tp", "fp", "fn", "tn", "recall", "precision", "false_positive_rate", "miss_rate", "false_accepts_per_hour"]:
        value = primary[key]
        lines.append(f"| {key} | {value:.4f} |" if isinstance(value, float) else f"| {key} | {value} |")

    lines.extend(
        [
            "",
            "## Timings",
            "",
            f"- Feature extraction total: `{timings['feature_seconds']:.3f}s`",
            f"- ONNX scoring total: `{timings['inference_seconds']:.3f}s`",
            f"- Files scored: `{len(scored)}`",
            "",
            "## Threshold Sweep Notes",
            "",
        ]
    )
    if best_zero_fp:
        first = best_zero_fp[0]
        lines.append(
            f"Lowest swept threshold with zero false positives: `{first['threshold']}` "
            f"(recall `{first['recall']:.4f}`, FN `{first['fn']}`)."
        )
    else:
        lines.append("No swept threshold achieved zero false positives.")

    lines.extend(["", "## Highest-Scoring Negatives", "", "| score | category | split | file |", "| ---: | --- | --- | --- |"])
    for item in hardest_negatives:
        lines.append(f"| {item.score:.6f} | {item.category} | {item.split} | `{item.path.name}` |")

    lines.extend(["", "## Lowest-Scoring Positives", "", "| score | split | file |", "| ---: | --- | --- |"])
    for item in weakest_positives:
        lines.append(f"| {item.score:.6f} | {item.split} | `{item.path.name}` |")

    lines.extend(
        [
            "",
            "## Raw Files",
            "",
            f"- Per-file CSV: `{args.output_dir / (args.prefix + '_scores.csv')}`",
            f"- Threshold CSV: `{args.output_dir / (args.prefix + '_threshold_report.csv')}`",
        ]
    )
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    args = parse_args()
    args.output_dir.mkdir(parents=True, exist_ok=True)
    scored, timings = score_workspace(args)
    threshold_rows = [
        metrics_for(scored, threshold, args.negative_hours)
        for threshold in threshold_values(args.threshold_start, args.threshold_stop, args.threshold_step)
    ]

    write_per_file(args.output_dir / f"{args.prefix}_scores.csv", scored, args.primary_threshold)
    write_thresholds(args.output_dir / f"{args.prefix}_threshold_report.csv", threshold_rows)
    write_report(args.output_dir / f"{args.prefix}_benchmark.md", args, scored, timings, threshold_rows)

    print(
        json.dumps(
            {
                "files": len(scored),
                "primary": metrics_for(scored, args.primary_threshold, args.negative_hours),
                "timings": {key: round(value, 3) for key, value in timings.items()},
                "outputs": {
                    "scores": str(args.output_dir / f"{args.prefix}_scores.csv"),
                    "thresholds": str(args.output_dir / f"{args.prefix}_threshold_report.csv"),
                    "report": str(args.output_dir / f"{args.prefix}_benchmark.md"),
                },
            },
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
