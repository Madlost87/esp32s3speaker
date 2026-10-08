#!/usr/bin/env python3
"""Fail fast when local ESPHome secrets still contain placeholders."""

from __future__ import annotations

import sys
from pathlib import Path


REQUIRED = ("wifi_ssid", "wifi_password")
BAD_MARKERS = ("PLACEHOLDER", "DO_NOT_UPLOAD", "CHANGE_ME", "CHANGEME")


def parse_simple_yaml(path: Path) -> dict[str, str]:
    values: dict[str, str] = {}
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or ":" not in line:
            continue
        key, value = line.split(":", 1)
        values[key.strip()] = value.strip().strip("\"'")
    return values


def main() -> int:
    path = Path("esphome/secrets.yaml")
    if not path.exists():
        print("Missing esphome/secrets.yaml. Copy secrets.example.yaml and fill local values.", file=sys.stderr)
        return 2

    values = parse_simple_yaml(path)
    failed = False
    for key in REQUIRED:
        value = values.get(key, "")
        upper = value.upper()
        if not value or any(marker in upper for marker in BAD_MARKERS):
            print(f"{key}: invalid or placeholder value", file=sys.stderr)
            failed = True
        else:
            print(f"{key}: set (length {len(value)})")
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
