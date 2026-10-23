from __future__ import annotations

import math
import struct
from dataclasses import dataclass


@dataclass(frozen=True)
class VadConfig:
    sample_rate_hz: int = 16000
    frame_ms: int = 30
    start_threshold_dbfs: float = -50.0
    end_threshold_dbfs: float = -56.0
    start_trigger_ms: int = 120
    end_silence_ms: int = 500

    @property
    def samples_per_frame(self) -> int:
        return self.sample_rate_hz * self.frame_ms // 1000

    @property
    def start_trigger_frames(self) -> int:
        return max(1, math.ceil(self.start_trigger_ms / self.frame_ms))

    @property
    def end_silence_frames(self) -> int:
        return max(1, math.ceil(self.end_silence_ms / self.frame_ms))


@dataclass(frozen=True)
class VadFrame:
    index: int
    rms: float
    dbfs: float | None
    speech: bool


@dataclass(frozen=True)
class VadEvent:
    kind: str
    frame_index: int
    time_seconds: float
    dbfs: float | None


def rms_dbfs_s16le(pcm: bytes) -> tuple[float, float | None]:
    values = struct.unpack("<" + "h" * (len(pcm) // 2), pcm)
    if not values:
        return 0.0, None
    rms = math.sqrt(sum(value * value for value in values) / len(values))
    dbfs = 20 * math.log10(rms / 32768) if rms > 0 else None
    return rms, dbfs


class EnergyVad:
    def __init__(self, config: VadConfig) -> None:
        self.config = config
        self._buffer = bytearray()
        self._frame_index = 0
        self._in_speech = False
        self._speech_candidate_frames = 0
        self._silence_frames = 0

    def process(self, pcm: bytes) -> list[VadEvent]:
        self._buffer.extend(pcm)
        frame_bytes = self.config.samples_per_frame * 2
        events: list[VadEvent] = []

        while len(self._buffer) >= frame_bytes:
            frame = bytes(self._buffer[:frame_bytes])
            del self._buffer[:frame_bytes]
            events.extend(self._process_frame(frame))

        return events

    def _process_frame(self, frame: bytes) -> list[VadEvent]:
        rms, dbfs = rms_dbfs_s16le(frame)
        is_start_level = dbfs is not None and dbfs >= self.config.start_threshold_dbfs
        is_end_level = dbfs is not None and dbfs >= self.config.end_threshold_dbfs
        events: list[VadEvent] = []

        if self._in_speech:
            if is_end_level:
                self._silence_frames = 0
            else:
                self._silence_frames += 1
                if self._silence_frames >= self.config.end_silence_frames:
                    self._in_speech = False
                    self._speech_candidate_frames = 0
                    self._silence_frames = 0
                    events.append(self._event("speech_end", dbfs))
        else:
            if is_start_level:
                self._speech_candidate_frames += 1
                if self._speech_candidate_frames >= self.config.start_trigger_frames:
                    self._in_speech = True
                    self._silence_frames = 0
                    events.append(self._event("speech_start", dbfs))
            else:
                self._speech_candidate_frames = 0

        self._frame_index += 1
        return events

    def _event(self, kind: str, dbfs: float | None) -> VadEvent:
        return VadEvent(
            kind=kind,
            frame_index=self._frame_index,
            time_seconds=round(self._frame_index * self.config.frame_ms / 1000, 3),
            dbfs=round(dbfs, 2) if dbfs is not None else None,
        )
