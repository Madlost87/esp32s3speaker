from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol


@dataclass(frozen=True)
class WakeWordConfig:
    engine: str = "placeholder"
    keyword: str = "Galileo"
    model_path: str = ""
    access_key_env: str = "PICOVOICE_ACCESS_KEY"


@dataclass(frozen=True)
class WakeWordEvent:
    keyword: str
    time_seconds: float
    confidence: float | None = None


class WakeWordDetector(Protocol):
    def process(self, pcm: bytes, time_seconds: float) -> WakeWordEvent | None:
        ...


class PlaceholderWakeWordDetector:
    def __init__(self, config: WakeWordConfig) -> None:
        self.config = config

    def process(self, pcm: bytes, time_seconds: float) -> WakeWordEvent | None:
        return None


def build_wakeword_detector(config: WakeWordConfig) -> WakeWordDetector:
    if config.engine == "placeholder":
        return PlaceholderWakeWordDetector(config)
    raise ValueError(
        f"unsupported wakeword engine {config.engine!r}; "
        "Porcupine integration requires credentials and model files first"
    )
