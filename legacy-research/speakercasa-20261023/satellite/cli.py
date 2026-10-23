from __future__ import annotations

import argparse
import json
import time
from pathlib import Path

from .config import load_config
from .dataset import record_dataset_sample
from .audio.capture import AlsaCapture, CaptureConfig
from .audio.preprocess import StereoToMonoPreprocessor
from .audio.stats import RunningPcmStats
from .state import SatelliteStateMachine
from .vad import EnergyVad, VadConfig
from .vad.energy import rms_dbfs_s16le


def capture_stats(args: argparse.Namespace) -> int:
    config = load_config(args.config)
    capture_config = CaptureConfig(
        device=config["audio"]["capture"]["device"],
        sample_rate_hz=config["audio"]["capture"]["sample_rate_hz"],
        channels=config["audio"]["capture"]["channels"],
        sample_format=config["audio"]["capture"]["sample_format"],
        chunk_ms=config["audio"]["capture"]["chunk_ms"],
    )
    preprocessor = StereoToMonoPreprocessor(
        input_rate_hz=config["audio"]["capture"]["sample_rate_hz"],
        output_rate_hz=config["audio"]["preprocessing"]["output_sample_rate_hz"],
        dc_removal_alpha=config["audio"]["preprocessing"]["dc_removal_alpha"],
    )
    stats = RunningPcmStats()
    deadline = time.monotonic() + args.duration
    chunks = 0

    with AlsaCapture(capture_config) as capture:
        for chunk in capture.chunks():
            mono = preprocessor.process(chunk.pcm)
            stats.update_s16le_mono(mono)
            chunks += 1
            if time.monotonic() >= deadline:
                break

    print(
        json.dumps(
            {
                "duration_seconds": args.duration,
                "input_device": capture_config.device,
                "input_rate_hz": capture_config.sample_rate_hz,
                "input_channels": capture_config.channels,
                "output_rate_hz": config["audio"]["preprocessing"]["output_sample_rate_hz"],
                "chunks": chunks,
                "mono_stats": stats.as_dict(),
            },
            indent=2,
        )
    )
    return 0


def vad_monitor(args: argparse.Namespace) -> int:
    config = load_config(args.config)
    capture_config = CaptureConfig(
        device=config["audio"]["capture"]["device"],
        sample_rate_hz=config["audio"]["capture"]["sample_rate_hz"],
        channels=config["audio"]["capture"]["channels"],
        sample_format=config["audio"]["capture"]["sample_format"],
        chunk_ms=config["audio"]["capture"]["chunk_ms"],
    )
    output_rate_hz = config["audio"]["preprocessing"]["output_sample_rate_hz"]
    preprocessor = StereoToMonoPreprocessor(
        input_rate_hz=config["audio"]["capture"]["sample_rate_hz"],
        output_rate_hz=output_rate_hz,
        dc_removal_alpha=config["audio"]["preprocessing"]["dc_removal_alpha"],
    )
    vad_config = VadConfig(
        sample_rate_hz=output_rate_hz,
        frame_ms=config["vad"]["frame_ms"],
        start_threshold_dbfs=config["vad"]["start_threshold_dbfs"],
        end_threshold_dbfs=config["vad"]["end_threshold_dbfs"],
        start_trigger_ms=config["vad"]["start_trigger_ms"],
        end_silence_ms=config["vad"]["end_silence_ms"],
    )
    vad = EnergyVad(vad_config)
    deadline = time.monotonic() + args.duration
    events = []
    frame_levels: list[float] = []

    with AlsaCapture(capture_config) as capture:
        for chunk in capture.chunks():
            mono = preprocessor.process(chunk.pcm)
            _, chunk_dbfs = rms_dbfs_s16le(mono)
            if chunk_dbfs is not None:
                frame_levels.append(chunk_dbfs)
            for event in vad.process(mono):
                event_dict = {
                    "kind": event.kind,
                    "time_seconds": event.time_seconds,
                    "frame_index": event.frame_index,
                    "dbfs": event.dbfs,
                }
                events.append(event_dict)
                print(json.dumps(event_dict), flush=True)
            if time.monotonic() >= deadline:
                break

    if args.summary:
        level_summary = None
        if frame_levels:
            sorted_levels = sorted(frame_levels)
            level_summary = {
                "min_dbfs": round(sorted_levels[0], 2),
                "p50_dbfs": round(sorted_levels[len(sorted_levels) // 2], 2),
                "p90_dbfs": round(sorted_levels[int(len(sorted_levels) * 0.9)], 2),
                "max_dbfs": round(sorted_levels[-1], 2),
            }
        print(
            json.dumps(
                {
                    "duration_seconds": args.duration,
                    "events": events,
                    "level_summary": level_summary,
                    "vad": {
                        "frame_ms": vad_config.frame_ms,
                        "start_threshold_dbfs": vad_config.start_threshold_dbfs,
                        "end_threshold_dbfs": vad_config.end_threshold_dbfs,
                        "start_trigger_ms": vad_config.start_trigger_ms,
                        "end_silence_ms": vad_config.end_silence_ms,
                    },
                },
                indent=2,
            )
        )
    return 0


def run_state(args: argparse.Namespace) -> int:
    config = load_config(args.config)
    capture_config = CaptureConfig(
        device=config["audio"]["capture"]["device"],
        sample_rate_hz=config["audio"]["capture"]["sample_rate_hz"],
        channels=config["audio"]["capture"]["channels"],
        sample_format=config["audio"]["capture"]["sample_format"],
        chunk_ms=config["audio"]["capture"]["chunk_ms"],
    )
    output_rate_hz = config["audio"]["preprocessing"]["output_sample_rate_hz"]
    preprocessor = StereoToMonoPreprocessor(
        input_rate_hz=config["audio"]["capture"]["sample_rate_hz"],
        output_rate_hz=output_rate_hz,
        dc_removal_alpha=config["audio"]["preprocessing"]["dc_removal_alpha"],
    )
    vad_config = VadConfig(
        sample_rate_hz=output_rate_hz,
        frame_ms=config["vad"]["frame_ms"],
        start_threshold_dbfs=config["vad"]["start_threshold_dbfs"],
        end_threshold_dbfs=config["vad"]["end_threshold_dbfs"],
        start_trigger_ms=config["vad"]["start_trigger_ms"],
        end_silence_ms=config["vad"]["end_silence_ms"],
    )
    vad = EnergyVad(vad_config)
    machine = SatelliteStateMachine(
        post_processing_cooldown_ms=config["state"]["post_processing_cooldown_ms"]
    )
    deadline = time.monotonic() + args.duration
    transitions = []

    print(json.dumps({"state": machine.state.value, "event": "started"}), flush=True)
    with AlsaCapture(capture_config) as capture:
        for chunk in capture.chunks():
            mono = preprocessor.process(chunk.pcm)
            for event in vad.process(mono):
                if event.kind == "speech_start":
                    transition = machine.on_speech_start(event.time_seconds)
                    if transition is not None:
                        transitions.append(_transition_dict(transition))
                        print(json.dumps(transitions[-1]), flush=True)
                elif event.kind == "speech_end":
                    for transition in machine.on_speech_end(event.time_seconds):
                        transitions.append(_transition_dict(transition))
                        print(json.dumps(transitions[-1]), flush=True)
            if time.monotonic() >= deadline:
                break

    if args.summary:
        print(
            json.dumps(
                {
                    "duration_seconds": args.duration,
                    "final_state": machine.state.value,
                    "post_processing_cooldown_ms": config["state"]["post_processing_cooldown_ms"],
                    "transitions": transitions,
                },
                indent=2,
            )
        )
    return 0


def dataset_record(args: argparse.Namespace) -> int:
    config = load_config(args.config)
    capture_config = CaptureConfig(
        device=config["audio"]["capture"]["device"],
        sample_rate_hz=config["dataset"]["default_sample_rate_hz"],
        channels=config["dataset"]["default_channels"],
        sample_format=config["audio"]["capture"]["sample_format"],
        chunk_ms=config["audio"]["capture"]["chunk_ms"],
    )
    label = args.label
    if args.category == "positive" and label == "":
        label = "galileo"
    if args.category != "positive" and label == "":
        label = args.category

    sample = record_dataset_sample(
        root=Path(config["dataset"]["root"]),
        category=args.category,
        label=label,
        distance=args.distance,
        environment=args.environment,
        speaker=args.speaker,
        duration_seconds=args.duration,
        capture=capture_config,
    )
    print(json.dumps({"recorded": sample.wav_path, "metadata": sample.sample_id}, indent=2))
    return 0


def _transition_dict(transition) -> dict[str, str | float]:
    return {
        "from": transition.from_state.value,
        "to": transition.to_state.value,
        "reason": transition.reason,
        "time_seconds": transition.time_seconds,
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="galileo-satellite")
    parser.add_argument("--config", default="config/galileo.toml")
    subparsers = parser.add_subparsers(dest="command", required=True)

    stats_parser = subparsers.add_parser("capture-stats")
    stats_parser.add_argument("--duration", type=float, default=10.0)
    stats_parser.set_defaults(func=capture_stats)

    vad_parser = subparsers.add_parser("vad-monitor")
    vad_parser.add_argument("--duration", type=float, default=15.0)
    vad_parser.add_argument("--summary", action="store_true")
    vad_parser.set_defaults(func=vad_monitor)

    state_parser = subparsers.add_parser("run-state")
    state_parser.add_argument("--duration", type=float, default=20.0)
    state_parser.add_argument("--summary", action="store_true")
    state_parser.set_defaults(func=run_state)

    dataset_parser = subparsers.add_parser("dataset-record")
    dataset_parser.add_argument("--category", choices=["positive", "negative", "noise"], required=True)
    dataset_parser.add_argument("--label", default="")
    dataset_parser.add_argument("--distance", default="unknown")
    dataset_parser.add_argument("--environment", default="unknown")
    dataset_parser.add_argument("--speaker", default="denny")
    dataset_parser.add_argument("--duration", type=float, default=3.0)
    dataset_parser.set_defaults(func=dataset_record)
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    return args.func(args)
