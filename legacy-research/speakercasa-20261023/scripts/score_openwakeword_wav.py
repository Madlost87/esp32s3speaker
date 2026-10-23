#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
import onnxruntime as ort
import scipy.io.wavfile
from openwakeword.utils import AudioFeatures


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Score one 16 kHz mono WAV with a Galileo ONNX wake-word pilot.")
    parser.add_argument("onnx_model", type=Path)
    parser.add_argument("wav_path", type=Path)
    parser.add_argument("--clip-samples", type=int, default=48000)
    parser.add_argument("--threshold", type=float, default=0.95)
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


def main() -> int:
    args = parse_args()
    audio = read_fixed_clip(args.wav_path, args.clip_samples)[None, :]
    features = AudioFeatures(device="cpu").embed_clips(audio, batch_size=1)

    session = ort.InferenceSession(str(args.onnx_model), providers=["CPUExecutionProvider"])
    input_name = session.get_inputs()[0].name
    score = float(session.run(None, {input_name: features.astype(np.float32)})[0].reshape(-1)[0])

    result = {
        "onnx_model": str(args.onnx_model),
        "wav_path": str(args.wav_path),
        "score": score,
        "threshold": args.threshold,
        "detected": score >= args.threshold,
        "feature_shape": list(features.shape),
    }
    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
