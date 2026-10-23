from __future__ import annotations

import math
import struct
from dataclasses import dataclass


@dataclass
class RunningPcmStats:
    samples: int = 0
    sum_samples: float = 0.0
    sum_squares: float = 0.0
    peak: int = 0
    clipped: int = 0

    def update_s16le_mono(self, pcm: bytes) -> None:
        values = struct.unpack("<" + "h" * (len(pcm) // 2), pcm)
        for value in values:
            self.samples += 1
            self.sum_samples += value
            self.sum_squares += value * value
            self.peak = max(self.peak, abs(value))
            if value in (-32768, 32767):
                self.clipped += 1

    @property
    def mean(self) -> float:
        return self.sum_samples / self.samples if self.samples else 0.0

    @property
    def rms(self) -> float:
        return math.sqrt(self.sum_squares / self.samples) if self.samples else 0.0

    @staticmethod
    def dbfs(value: float) -> float | None:
        if value <= 0:
            return None
        return 20 * math.log10(value / 32768)

    def as_dict(self) -> dict[str, float | int | None]:
        return {
            "samples": self.samples,
            "rms": round(self.rms, 2),
            "rms_dbfs": round(self.dbfs(self.rms), 2) if self.dbfs(self.rms) is not None else None,
            "peak": self.peak,
            "peak_dbfs": round(self.dbfs(self.peak), 2) if self.dbfs(self.peak) is not None else None,
            "dc_offset_samples": round(self.mean, 2),
            "clipped_samples": self.clipped,
        }
