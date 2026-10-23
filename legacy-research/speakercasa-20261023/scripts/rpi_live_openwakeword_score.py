#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import subprocess
import time
from pathlib import Path

import numpy as np
import onnxruntime as ort
import scipy.io.wavfile
from openwakeword.utils import AudioFeatures


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Capture and score Galileo wake word fully on the Raspberry.")
    parser.add_argument("onnx_model", type=Path)
    parser.add_argument("--threshold", type=float, default=0.95)
    parser.add_argument("--duration", type=int, default=3)
    parser.add_argument("--device", default="plughw:0,0")
    parser.add_argument("--output-dir", type=Path, default=Path("/home/denny/galileo/live_wake_tests"))
    parser.add_argument("--label", default="live")
    parser.add_argument("--led-script", default="/home/denny/galileo/bin/respeaker_leds.py")
    parser.add_argument("--led-brightness", type=int, default=8)
    parser.add_argument("--led-pre-seconds", type=float, default=0.5)
    parser.add_argument("--no-led", action="store_true")
    return parser.parse_args()


def run(command: list[str]) -> None:
    subprocess.run(command, check=True)


def set_led(script: str, brightness: int, color: str) -> None:
    run(["python3", script, "--brightness", str(brightness), "set", color])


def leds_off(script: str) -> None:
    run(["python3", script, "off"])


def read_fixed_clip(path: Path, clip_samples: int = 48000) -> np.ndarray:
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
    args.output_dir.mkdir(parents=True, exist_ok=True)
    stamp = time.strftime("%Y%m%d-%H%M%S")
    wav_path = args.output_dir / f"{stamp}-{args.label}-16k-mono.wav"

    timings: dict[str, float] = {}
    start = time.monotonic()
    if not args.no_led:
        set_led(args.led_script, args.led_brightness, "yellow")
        time.sleep(args.led_pre_seconds)
        set_led(args.led_script, args.led_brightness, "red")

    record_start = time.monotonic()
    try:
        run(
            [
                "arecord",
                "-D",
                args.device,
                "-f",
                "S16_LE",
                "-r",
                "16000",
                "-c",
                "1",
                "-d",
                str(args.duration),
                str(wav_path),
            ]
        )
    finally:
        if not args.no_led:
            leds_off(args.led_script)
    timings["record_seconds"] = time.monotonic() - record_start

    feature_start = time.monotonic()
    audio = read_fixed_clip(wav_path)[None, :]
    features = AudioFeatures(device="cpu").embed_clips(audio, batch_size=1)
    timings["feature_seconds"] = time.monotonic() - feature_start

    infer_start = time.monotonic()
    session = ort.InferenceSession(str(args.onnx_model), providers=["CPUExecutionProvider"])
    input_name = session.get_inputs()[0].name
    score = float(session.run(None, {input_name: features.astype(np.float32)})[0].reshape(-1)[0])
    timings["inference_seconds"] = time.monotonic() - infer_start
    timings["total_seconds"] = time.monotonic() - start

    result = {
        "onnx_model": str(args.onnx_model),
        "wav_path": str(wav_path),
        "score": score,
        "threshold": args.threshold,
        "detected": score >= args.threshold,
        "feature_shape": list(features.shape),
        "timings": {key: round(value, 3) for key, value in timings.items()},
    }
    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
