"""Wake-word integration points."""

from .base import (
    PlaceholderWakeWordDetector,
    WakeWordConfig,
    WakeWordDetector,
    WakeWordEvent,
    build_wakeword_detector,
)

__all__ = [
    "PlaceholderWakeWordDetector",
    "WakeWordConfig",
    "WakeWordDetector",
    "WakeWordEvent",
    "build_wakeword_detector",
]
