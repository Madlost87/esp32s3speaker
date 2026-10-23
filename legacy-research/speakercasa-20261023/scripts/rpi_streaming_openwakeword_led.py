#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import signal
import subprocess
import time
from pathlib import Path

import numpy as np
from openwakeword.model import Model


SAMPLE_RATE = 16000
SAMPLES_PER_FRAME = 1280
SAMPLE_WIDTH_BYTES = 2


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Streaming Galileo wake-word listener for 24/7 Raspberry use.")
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

    model = Model(wakeword_models=[str(args.onnx_model)], inference_framework="onnx")
    model_name = args.onnx_model.stem
    threshold = {model_name: args.threshold}
    patience = {model_name: args.patience} if args.patience > 1 else {}
    frame_samples = SAMPLES_PER_FRAME * args.chunk_frames
    frame_bytes = frame_samples * SAMPLE_WIDTH_BYTES
    arecord = start_arecord(args.device)

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
                    "mode": "streaming",
                    "model": str(args.onnx_model),
                    "model_name": model_name,
                    "threshold": args.threshold,
                    "patience": args.patience,
                    "cooldown_seconds": args.cooldown_seconds,
                    "chunk_samples": frame_samples,
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
            scores = model.predict(audio, patience=patience, threshold=threshold)
            predict_seconds = time.monotonic() - predict_started
            score = float(scores.get(model_name, 0.0))
            now = time.monotonic()
            detected = score >= args.threshold and now - last_detection >= args.cooldown_seconds
            frames += 1

            if detected:
                detections += 1
                last_detection = now
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
