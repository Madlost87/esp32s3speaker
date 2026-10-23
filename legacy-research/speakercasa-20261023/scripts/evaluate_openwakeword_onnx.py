#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
import onnxruntime as ort


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Evaluate a Galileo openWakeWord ONNX model on feature arrays.")
    parser.add_argument("onnx_model", type=Path)
    parser.add_argument("feature_dir", type=Path)
    parser.add_argument("--threshold", type=float, default=0.5)
    return parser.parse_args()


def score_file(session: ort.InferenceSession, input_name: str, path: Path) -> list[float]:
    features = np.load(path).astype(np.float32)
    scores = []
    for row in features:
        output = session.run(None, {input_name: row[None, :, :]})[0]
        scores.append(float(output.reshape(-1)[0]))
    return scores


def summarize(scores: list[float], positive: bool, threshold: float) -> dict[str, object]:
    predictions = [score >= threshold for score in scores]
    correct = sum(prediction is positive for prediction in predictions)
    return {
        "count": len(scores),
        "min": min(scores) if scores else None,
        "max": max(scores) if scores else None,
        "scores": scores,
        "correct": correct,
        "accuracy": correct / len(scores) if scores else 0.0,
    }


def main() -> int:
    args = parse_args()
    session = ort.InferenceSession(str(args.onnx_model), providers=["CPUExecutionProvider"])
    input_name = session.get_inputs()[0].name

    positive_scores = score_file(session, input_name, args.feature_dir / "positive_features_test.npy")
    negative_scores = score_file(session, input_name, args.feature_dir / "negative_features_test.npy")

    result = {
        "onnx_model": str(args.onnx_model),
        "feature_dir": str(args.feature_dir),
        "threshold": args.threshold,
        "input_name": input_name,
        "input_shape": session.get_inputs()[0].shape,
        "positive": summarize(positive_scores, True, args.threshold),
        "negative": summarize(negative_scores, False, args.threshold),
    }
    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
