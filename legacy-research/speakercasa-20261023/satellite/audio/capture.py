from __future__ import annotations

import subprocess
import time
from dataclasses import dataclass
from typing import Iterator


@dataclass(frozen=True)
class CaptureConfig:
    device: str = "hw:0,0"
    sample_rate_hz: int = 48000
    channels: int = 2
    sample_format: str = "S16_LE"
    chunk_ms: int = 20

    @property
    def bytes_per_sample(self) -> int:
        if self.sample_format != "S16_LE":
            raise ValueError(f"unsupported sample format: {self.sample_format}")
        return 2

    @property
    def frames_per_chunk(self) -> int:
        frames = self.sample_rate_hz * self.chunk_ms // 1000
        if frames <= 0:
            raise ValueError("chunk_ms is too small")
        return frames

    @property
    def bytes_per_chunk(self) -> int:
        return self.frames_per_chunk * self.channels * self.bytes_per_sample


@dataclass(frozen=True)
class AudioChunk:
    sequence: int
    monotonic_ns: int
    pcm: bytes


class AlsaCapture:
    def __init__(self, config: CaptureConfig) -> None:
        self.config = config
        self._process: subprocess.Popen[bytes] | None = None

    def __enter__(self) -> "AlsaCapture":
        command = [
            "arecord",
            "-D",
            self.config.device,
            "-f",
            self.config.sample_format,
            "-r",
            str(self.config.sample_rate_hz),
            "-c",
            str(self.config.channels),
            "-t",
            "raw",
        ]
        self._process = subprocess.Popen(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        if self._process is None:
            return
        if self._process.poll() is None:
            self._process.terminate()
            try:
                self._process.wait(timeout=2)
            except subprocess.TimeoutExpired:
                self._process.kill()
                self._process.wait(timeout=2)

    def chunks(self) -> Iterator[AudioChunk]:
        if self._process is None or self._process.stdout is None:
            raise RuntimeError("capture is not started")

        size = self.config.bytes_per_chunk
        sequence = 0
        while True:
            data = self._process.stdout.read(size)
            if not data:
                break
            if len(data) != size:
                raise RuntimeError(f"short audio chunk: {len(data)} != {size}")
            yield AudioChunk(sequence=sequence, monotonic_ns=time.monotonic_ns(), pcm=data)
            sequence += 1

    def stderr_text(self) -> str:
        if self._process is None or self._process.stderr is None:
            return ""
        try:
            return self._process.stderr.read().decode("utf-8", errors="replace")
        except Exception:
            return ""
