#!/usr/bin/env python3
from __future__ import annotations

import argparse
import time

import spidev


COLORS = {
    "off": (0, 0, 0),
    "red": (255, 0, 0),
    "green": (0, 255, 0),
    "blue": (0, 0, 255),
    "purple": (180, 0, 255),
    "white": (255, 255, 255),
    "yellow": (255, 128, 0),
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Control ReSpeaker 2-Mic HAT APA102 LEDs.")
    parser.add_argument("--bus", type=int, default=0)
    parser.add_argument("--device", type=int, default=0)
    parser.add_argument("--brightness", type=int, default=4)
    parser.add_argument("--leds", type=int, default=3)
    subparsers = parser.add_subparsers(dest="command", required=True)

    set_parser = subparsers.add_parser("set")
    set_parser.add_argument("color", choices=sorted(COLORS))
    set_parser.add_argument("--index", type=int, help="Set only one LED index.")

    subparsers.add_parser("off")

    pulse_parser = subparsers.add_parser("pulse")
    pulse_parser.add_argument("color", choices=sorted(COLORS))
    pulse_parser.add_argument("--seconds", type=float, default=1.0)

    cue_parser = subparsers.add_parser("cue")
    cue_parser.add_argument("--pre-seconds", type=float, default=0.5)
    cue_parser.add_argument("--speak-seconds", type=float, default=3.0)

    return parser.parse_args()


def frame(red: int, green: int, blue: int, brightness: int) -> list[int]:
    level = max(0, min(31, brightness))
    return [0b11100000 | level, blue, green, red]


def write_leds(colors: list[tuple[int, int, int]], brightness: int, bus: int, device: int) -> None:
    spi = spidev.SpiDev()
    spi.open(bus, device)
    spi.max_speed_hz = 8000000
    try:
        data = [0, 0, 0, 0]
        for red, green, blue in colors:
            data.extend(frame(red, green, blue, brightness))
        data.extend([255, 255, 255, 255])
        spi.xfer2(data)
    finally:
        spi.close()


def set_all(color: tuple[int, int, int], count: int) -> list[tuple[int, int, int]]:
    return [color for _ in range(count)]


def main() -> int:
    args = parse_args()
    if args.command == "off":
        write_leds(set_all(COLORS["off"], args.leds), args.brightness, args.bus, args.device)
        return 0

    if args.command == "set":
        colors = set_all(COLORS["off"], args.leds)
        if args.index is None:
            colors = set_all(COLORS[args.color], args.leds)
        else:
            colors[args.index] = COLORS[args.color]
        write_leds(colors, args.brightness, args.bus, args.device)
        return 0

    if args.command == "pulse":
        write_leds(set_all(COLORS[args.color], args.leds), args.brightness, args.bus, args.device)
        time.sleep(args.seconds)
        write_leds(set_all(COLORS["off"], args.leds), args.brightness, args.bus, args.device)
        return 0

    if args.command == "cue":
        write_leds(set_all(COLORS["yellow"], args.leds), args.brightness, args.bus, args.device)
        time.sleep(args.pre_seconds)
        write_leds(set_all(COLORS["red"], args.leds), args.brightness, args.bus, args.device)
        time.sleep(args.speak_seconds)
        write_leds(set_all(COLORS["off"], args.leds), args.brightness, args.bus, args.device)
        return 0

    raise AssertionError(args.command)


if __name__ == "__main__":
    raise SystemExit(main())
