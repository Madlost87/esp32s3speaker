#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import signal
import subprocess
import time
from collections import deque
from pathlib import Path

import numpy as np
import onnxruntime as ort
from openwakeword.utils import AudioFeatures


SAMPLE_RATE = 16000
SAMPLES_PER_FRAME = 1280
SAMPLE_WIDTH_BYTES = 2


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Hybrid 24/7 Galileo listener: TFLite features + ONNX classifier.")
    parser.add_argument("onnx_model", type=Path)
    parser.add_argument("--threshold", type=float, default=0.95)
    parser.add_argument("--patience", type=int, default=2)
    parser.add_argument("--cooldown-seconds", type=float, default=2.0)
    parser.add_argument("--device", default="plughw:0,0")
    parser.add_argument("--chunk-frames", type=int, default=1)
    parser.add_argument("--led-script", default="/home/denny/galileo/bin/respeaker_leds.py")
    parser.add_argument("--led-brightness", type=int, default=8)
    parser.add_argument("--led-color", default="purple")
    parser.add_argument("--led-seconds", type=float, default=0.8)
    parser.add_argument("--status-seconds", type=float, default=60.0)
    parser.add_argument("--no-led", action="store_true")
    parser.add_argument("--print-every-score", action="store_true")
    return parser.parse_args()


def run_led(script: str, brightness: int, command: list[str]) -> None:
    subprocess.run(["python3", script, "--brightness", str(brightness), *command], check=False)


def pulse_led(script: str, brightness: int, color: str, seconds: float) -> None:
    run_led(script, brightness, ["pulse", color, "--seconds", str(seconds)])


def start_arecord(device: str) -> subprocess.Popen[bytes]:
    return subprocess.Popen(
        [
            "arecord",
            "-D",
            device,
            "-f",
            "S16_LE",
            "-r",
            str(SAMPLE_RATE),
            "-c",
            "1",
            "-t",
            "raw",
        ],
        stdout=subprocess.PIPE,
        stderr=subprocess.DEVNULL,
    )


def read_exact(stream, size: int) -> bytes:
    chunks: list[bytes] = []
    remaining = size
    while remaining > 0:
        chunk = stream.read(remaining)
        if not chunk:
            return b""
        chunks.append(chunk)
        remaining -= len(chunk)
    return b"".join(chunks)


def main() -> int:
    args = parse_args()
    stop = False

    def handle_signal(signum: int, frame: object) -> None:
        nonlocal stop
        stop = True

    signal.signal(signal.SIGINT, handle_signal)
    signal.signal(signal.SIGTERM, handle_signal)

    session_options = ort.SessionOptions()
    session_options.inter_op_num_threads = 1
    session_options.intra_op_num_threads = 1
    session = ort.InferenceSession(str(args.onnx_model), sess_options=session_options, providers=["CPUExecutionProvider"])
    input_name = session.get_inputs()[0].name
    model_frames = int(session.get_inputs()[0].shape[1])
    features = AudioFeatures(inference_framework="tflite")

    frame_samples = SAMPLES_PER_FRAME * args.chunk_frames
    frame_bytes = frame_samples * SAMPLE_WIDTH_BYTES
    arecord = start_arecord(args.device)
    recent_scores: deque[float] = deque(maxlen=max(1, args.patience))

    frames = 0
    detections = 0
    last_detection = 0.0
    last_status = time.monotonic()
    started = last_status
    try:
        assert arecord.stdout is not None
        print(
            json.dumps(
                {
                    "status": "listening",
                    "mode": "hybrid_tflite_features_onnx_classifier",
                    "model": str(args.onnx_model),
                    "threshold": args.threshold,
                    "patience": args.patience,
                    "cooldown_seconds": args.cooldown_seconds,
                    "chunk_samples": frame_samples,
                    "model_feature_frames": model_frames,
                    "led_color": None if args.no_led else args.led_color,
                }
            ),
            flush=True,
        )

        while not stop:
            data = read_exact(arecord.stdout, frame_bytes)
            if not data:
                break
            audio = np.frombuffer(data, dtype=np.int16).copy()
            predict_started = time.monotonic()
            prepared_samples = features(audio)
            score = 0.0
            if prepared_samples >= SAMPLES_PER_FRAME:
                model_input = features.get_features(model_frames)
                score = float(session.run(None, {input_name: model_input.astype(np.float32)})[0].reshape(-1)[0])
            predict_seconds = time.monotonic() - predict_started
            now = time.monotonic()
            frames += 1
            recent_scores.append(score)
            confirmed = (
                len(recent_scores) >= args.patience
                and sum(item >= args.threshold for item in recent_scores) >= args.patience
            )
            detected = confirmed and now - last_detection >= args.cooldown_seconds

            if detected:
                detections += 1
                last_detection = now
                recent_scores.clear()
                if not args.no_led:
                    pulse_led(args.led_script, args.led_brightness, args.led_color, args.led_seconds)

            if detected or args.print_every_score:
                print(
                    json.dumps(
                        {
                            "score": round(score, 6),
                            "detected": detected,
                            "predict_seconds": round(predict_seconds, 4),
                        }
                    ),
                    flush=True,
                )

            if args.status_seconds > 0 and now - last_status >= args.status_seconds:
                elapsed = now - started
                print(
                    json.dumps(
                        {
                            "status": "running",
                            "frames": frames,
                            "detections": detections,
                            "uptime_seconds": round(elapsed, 1),
                            "avg_frames_per_second": round(frames / elapsed, 2) if elapsed else 0.0,
                        }
                    ),
                    flush=True,
                )
                last_status = now
    finally:
        arecord.terminate()
        try:
            arecord.wait(timeout=2)
        except subprocess.TimeoutExpired:
            arecord.kill()
        if not args.no_led:
            run_led(args.led_script, args.led_brightness, ["off"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
