#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import signal
import subprocess
import threading
import time
from collections import deque
from pathlib import Path

import numpy as np
import onnxruntime as ort
from openwakeword.utils import AudioFeatures


SAMPLE_RATE = 16000
SAMPLE_WIDTH_BYTES = 2


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Continuously listen for Galileo and pulse ReSpeaker LEDs.")
    parser.add_argument("onnx_model", type=Path)
    parser.add_argument("--threshold", type=float, default=0.95)
    parser.add_argument("--device", default="plughw:0,0")
    parser.add_argument("--window-seconds", type=float, default=3.0)
    parser.add_argument("--score-interval", type=float, default=0.75)
    parser.add_argument("--chunk-seconds", type=float, default=0.25)
    parser.add_argument("--cooldown-seconds", type=float, default=2.0)
    parser.add_argument("--led-script", default="/home/denny/galileo/bin/respeaker_leds.py")
    parser.add_argument("--led-brightness", type=int, default=8)
    parser.add_argument("--led-color", default="purple")
    parser.add_argument("--led-seconds", type=float, default=0.8)
    parser.add_argument("--no-led", action="store_true")
    parser.add_argument("--print-every-score", action="store_true")
    return parser.parse_args()


class AudioRing:
    def __init__(self, max_samples: int) -> None:
        self._samples: deque[np.ndarray] = deque()
        self._max_samples = max_samples
        self._sample_count = 0
        self._lock = threading.Lock()

    def append(self, samples: np.ndarray) -> None:
        with self._lock:
            self._samples.append(samples)
            self._sample_count += int(samples.shape[0])
            while self._sample_count > self._max_samples and self._samples:
                removed = self._samples.popleft()
                self._sample_count -= int(removed.shape[0])

    def snapshot(self) -> np.ndarray | None:
        with self._lock:
            if self._sample_count < self._max_samples:
                return None
            data = np.concatenate(list(self._samples))
        return data[-self._max_samples :]


def run_led(script: str, brightness: int, command: list[str]) -> None:
    subprocess.run(["python3", script, "--brightness", str(brightness), *command], check=False)


def pulse_led(script: str, brightness: int, color: str, seconds: float) -> None:
    run_led(script, brightness, ["pulse", color, "--seconds", str(seconds)])


def read_audio(process: subprocess.Popen[bytes], ring: AudioRing, chunk_bytes: int, stop: threading.Event) -> None:
    assert process.stdout is not None
    while not stop.is_set():
        data = process.stdout.read(chunk_bytes)
        if not data:
            stop.set()
            return
        usable = len(data) - (len(data) % SAMPLE_WIDTH_BYTES)
        if usable:
            ring.append(np.frombuffer(data[:usable], dtype=np.int16).copy())


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


def main() -> int:
    args = parse_args()
    window_samples = int(args.window_seconds * SAMPLE_RATE)
    chunk_bytes = int(args.chunk_seconds * SAMPLE_RATE * SAMPLE_WIDTH_BYTES)
    stop = threading.Event()

    def handle_signal(signum: int, frame: object) -> None:
        stop.set()

    signal.signal(signal.SIGINT, handle_signal)
    signal.signal(signal.SIGTERM, handle_signal)

    session = ort.InferenceSession(str(args.onnx_model), providers=["CPUExecutionProvider"])
    input_name = session.get_inputs()[0].name
    features = AudioFeatures(device="cpu")
    ring = AudioRing(max_samples=window_samples)
    arecord = start_arecord(args.device)
    reader = threading.Thread(target=read_audio, args=(arecord, ring, chunk_bytes, stop), daemon=True)
    reader.start()

    last_detection = 0.0
    try:
        print(
            json.dumps(
                {
                    "status": "listening",
                    "model": str(args.onnx_model),
                    "threshold": args.threshold,
                    "window_seconds": args.window_seconds,
                    "score_interval": args.score_interval,
                    "led_color": None if args.no_led else args.led_color,
                }
            ),
            flush=True,
        )
        while not stop.is_set():
            time.sleep(args.score_interval)
            audio = ring.snapshot()
            if audio is None:
                continue
            started = time.monotonic()
            embedded = features.embed_clips(audio[None, :], batch_size=1)
            score = float(session.run(None, {input_name: embedded.astype(np.float32)})[0].reshape(-1)[0])
            now = time.monotonic()
            detected = score >= args.threshold and now - last_detection >= args.cooldown_seconds
            if detected:
                last_detection = now
                if not args.no_led:
                    pulse_led(args.led_script, args.led_brightness, args.led_color, args.led_seconds)
            if detected or args.print_every_score:
                print(
                    json.dumps(
                        {
                            "score": round(score, 6),
                            "detected": detected,
                            "feature_seconds": round(now - started, 3),
                        }
                    ),
                    flush=True,
                )
    finally:
        stop.set()
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
