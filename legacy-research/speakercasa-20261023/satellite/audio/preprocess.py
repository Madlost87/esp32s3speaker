from __future__ import annotations

import struct
from dataclasses import dataclass


@dataclass
class DcBlocker:
    alpha: float = 0.995
    previous_input: float = 0.0
    previous_output: float = 0.0

    def process_sample(self, sample: float) -> int:
        output = sample - self.previous_input + self.alpha * self.previous_output
        self.previous_input = sample
        self.previous_output = output
        return max(-32768, min(32767, int(output)))


class StereoToMonoPreprocessor:
    def __init__(
        self,
        input_rate_hz: int = 48000,
        output_rate_hz: int = 16000,
        dc_removal_alpha: float = 0.995,
    ) -> None:
        self.input_rate_hz = input_rate_hz
        self.output_rate_hz = output_rate_hz
        self._resample_state = None
        self._dc = DcBlocker(alpha=dc_removal_alpha)

    def process(self, stereo_s16le: bytes) -> bytes:
        interleaved = struct.unpack("<" + "h" * (len(stereo_s16le) // 2), stereo_s16le)
        mono_samples = [
            int((interleaved[index] + interleaved[index + 1]) / 2)
            for index in range(0, len(interleaved), 2)
        ]
        samples = self._resample_mono(mono_samples)
        filtered = [self._dc.process_sample(sample) for sample in samples]
        return struct.pack("<" + "h" * len(filtered), *filtered)

    def _resample_mono(self, samples: list[int]) -> list[int]:
        if self.input_rate_hz == self.output_rate_hz:
            return samples
        if self.input_rate_hz % self.output_rate_hz != 0:
            raise ValueError(
                f"only integer downsampling is supported: "
                f"{self.input_rate_hz} -> {self.output_rate_hz}"
            )
        factor = self.input_rate_hz // self.output_rate_hz
        if factor <= 1:
            return samples
        return [
            int(sum(samples[index : index + factor]) / factor)
            for index in range(0, len(samples) - factor + 1, factor)
        ]
