#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import subprocess
import time
from pathlib import Path

from score_openwakeword_wav import main as score_main


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Capture audio on the Raspberry and score it locally.")
    parser.add_argument("onnx_model", type=Path)
    parser.add_argument("--host", default="denny@192.168.1.151")
    parser.add_argument("--ssh-config", default="/dev/null")
    parser.add_argument("--device", default="hw:0,0")
    parser.add_argument("--duration", type=int, default=3)
    parser.add_argument("--label", default="live")
    parser.add_argument("--threshold", type=float, default=0.95)
    parser.add_argument("--highpass-hz", type=int, default=80)
    parser.add_argument("--cue", action="store_true", help="Play a short tone cue on the Raspberry before recording.")
    parser.add_argument("--post-cue-delay", type=float, default=0.6)
    parser.add_argument("--playback-device", default="plughw:0,0")
    parser.add_argument("--led-cue", action="store_true", help="Use ReSpeaker LEDs as the recording cue.")
    parser.add_argument("--led-script", default="/home/denny/galileo/respeaker_leds.py")
    parser.add_argument("--led-brightness", type=int, default=8)
    parser.add_argument("--led-pre-seconds", type=float, default=0.5)
    parser.add_argument("--output-dir", type=Path, default=Path("local_data/live_captures"))
    return parser.parse_args()


def run(command: list[str]) -> None:
    subprocess.run(command, check=True)


def main() -> int:
    args = parse_args()
    args.output_dir.mkdir(parents=True, exist_ok=True)

    stamp = time.strftime("%Y%m%d-%H%M%S")
    remote_wav = f"/tmp/galileo-{stamp}-{args.label}.wav"
    local_raw = args.output_dir / f"{stamp}-{args.label}-48k-stereo.wav"
    local_16k = args.output_dir / f"{stamp}-{args.label}-16k-mono.wav"

    ssh_base = ["ssh", "-F", args.ssh_config, args.host]
    scp_base = ["scp", "-F", args.ssh_config]

    if args.cue:
        run(
            ssh_base
            + [
                "sh",
                "-lc",
                (
                    f"timeout 0.35 speaker-test -D {args.playback_device} "
                    "-t sine -f 1200 -c 2 >/dev/null 2>&1 || true"
                ),
            ]
        )
        if args.post_cue_delay > 0:
            time.sleep(args.post_cue_delay)

    record_command = [
        "arecord",
        "-D",
        args.device,
        "-f",
        "S16_LE",
        "-r",
        "48000",
        "-c",
        "2",
        "-d",
        str(args.duration),
        remote_wav,
    ]
    if args.led_cue:
        remote_record = (
            f"python3 {args.led_script} --brightness {args.led_brightness} set yellow; "
            f"sleep {args.led_pre_seconds}; "
            f"python3 {args.led_script} --brightness {args.led_brightness} set red; "
            + " ".join(record_command)
            + f"; status=$?; python3 {args.led_script} off; exit $status"
        )
        run(ssh_base + ["sh", "-lc", remote_record])
    else:
        run(ssh_base + record_command)
    run(scp_base + [f"{args.host}:{remote_wav}", str(local_raw)])
    run(ssh_base + ["rm", "-f", remote_wav])
    run(
        [
            "ffmpeg",
            "-hide_banner",
            "-loglevel",
            "error",
            "-y",
            "-i",
            str(local_raw),
            "-ac",
            "1",
            "-ar",
            "16000",
            "-sample_fmt",
            "s16",
            "-af",
            f"highpass=f={args.highpass_hz}",
            str(local_16k),
        ]
    )

    print(
        json.dumps(
            {
                "captured": str(local_raw),
                "normalized": str(local_16k),
                "duration_seconds": args.duration,
                "label": args.label,
                "highpass_hz": args.highpass_hz,
                "cue": args.cue,
                "post_cue_delay": args.post_cue_delay,
                "led_cue": args.led_cue,
                "led_pre_seconds": args.led_pre_seconds,
            },
            indent=2,
        )
    )

    import sys

    sys.argv = [
        "score_openwakeword_wav.py",
        str(args.onnx_model),
        str(local_16k),
        "--threshold",
        str(args.threshold),
    ]
    return score_main()


if __name__ == "__main__":
    raise SystemExit(main())
