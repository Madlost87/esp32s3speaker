from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class SatelliteState(str, Enum):
    IDLE = "IDLE"
    LISTENING = "LISTENING"
    PROCESSING = "PROCESSING"
    SPEAKING = "SPEAKING"


@dataclass(frozen=True)
class StateTransition:
    from_state: SatelliteState
    to_state: SatelliteState
    reason: str
    time_seconds: float


class SatelliteStateMachine:
    def __init__(self, post_processing_cooldown_ms: int = 1500) -> None:
        self.state = SatelliteState.IDLE
        self.post_processing_cooldown_seconds = post_processing_cooldown_ms / 1000
        self._ignore_speech_until_seconds = 0.0

    def on_speech_start(self, time_seconds: float) -> StateTransition | None:
        if time_seconds < self._ignore_speech_until_seconds:
            return None
        if self.state != SatelliteState.IDLE:
            return None
        return self._transition(SatelliteState.LISTENING, "speech_start", time_seconds)

    def on_speech_end(self, time_seconds: float) -> list[StateTransition]:
        if self.state != SatelliteState.LISTENING:
            return []
        self._ignore_speech_until_seconds = time_seconds + self.post_processing_cooldown_seconds
        return [
            self._transition(SatelliteState.PROCESSING, "speech_end", time_seconds),
            self._transition(SatelliteState.IDLE, "processing_stub_complete", time_seconds),
        ]

    def _transition(
        self,
        to_state: SatelliteState,
        reason: str,
        time_seconds: float,
    ) -> StateTransition:
        transition = StateTransition(
            from_state=self.state,
            to_state=to_state,
            reason=reason,
            time_seconds=time_seconds,
        )
        self.state = to_state
        return transition
