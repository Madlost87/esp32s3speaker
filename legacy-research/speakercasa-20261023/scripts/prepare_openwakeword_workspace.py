#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import shutil
from pathlib import Path


TARGET_DIRS = {
    ("positive", "train"): "positive_train",
    ("positive", "validation"): "positive_test",
    ("negative", "train"): "negative_train",
    ("negative", "validation"): "negative_test",
    ("noise", "train"): "negative_train",
    ("noise", "validation"): "negative_test",
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Prepare a local openWakeWord clip workspace from a Galileo dataset manifest."
    )
    parser.add_argument("manifest", type=Path)
    parser.add_argument("output_dir", type=Path)
    parser.add_argument(
        "--mode",
        choices=["symlink", "copy"],
        default="symlink",
        help="How WAV files are placed in the output workspace.",
    )
    parser.add_argument(
        "--root-override",
        type=Path,
        help="Replace the manifest root with this path when resolving WAV files.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Only report planned actions and missing files.",
    )
    parser.add_argument(
        "--max-missing",
        type=int,
        default=20,
        help="Maximum number of missing paths to print.",
    )
    return parser.parse_args()


def resolve_source(path: str, manifest_root: str, root_override: Path | None) -> Path:
    source = Path(path)
    if root_override is None:
        return source

    try:
        relative = source.relative_to(manifest_root)
    except ValueError:
        relative = Path(source.name)
    return root_override / relative


def safe_name(item: dict[str, str], index: int) -> str:
    source = Path(item["path"])
    stem = source.stem.replace(" ", "_")
    return f"{index:04d}-{item['class']}-{stem}.wav"


def place_file(source: Path, destination: Path, mode: str) -> None:
    destination.parent.mkdir(parents=True, exist_ok=True)
    if destination.exists() or destination.is_symlink():
        destination.unlink()
    if mode == "copy":
        shutil.copy2(source, destination)
    else:
        os.symlink(source, destination)


def main() -> int:
    args = parse_args()
    manifest = json.loads(args.manifest.read_text(encoding="utf-8"))
    manifest_root = manifest.get("root", "")

    counts: dict[str, int] = {}
    missing: list[str] = []
    planned: list[dict[str, str]] = []

    for index, item in enumerate(manifest["items"], start=1):
        key = (item["class"], item["split"])
        target_dir = TARGET_DIRS.get(key)
        if target_dir is None:
            raise SystemExit(f"Unsupported manifest item: class={key[0]!r} split={key[1]!r}")

        source = resolve_source(item["path"], manifest_root, args.root_override)
        destination = args.output_dir / target_dir / safe_name(item, index)
        counts[target_dir] = counts.get(target_dir, 0) + 1
        planned.append(
            {
                "source": str(source),
                "destination": str(destination),
                "class": item["class"],
                "split": item["split"],
            }
        )
        if not source.exists():
            missing.append(str(source))

    summary = {
        "manifest": str(args.manifest),
        "output_dir": str(args.output_dir),
        "mode": args.mode,
        "dry_run": args.dry_run,
        "counts": counts,
        "missing_count": len(missing),
    }
    print(json.dumps(summary, indent=2))

    if missing:
        print("\nMissing files:")
        for path in missing[: args.max_missing]:
            print(path)
        if len(missing) > args.max_missing:
            print(f"... {len(missing) - args.max_missing} more")
        return 2

    if args.dry_run:
        return 0

    for action in planned:
        place_file(Path(action["source"]), Path(action["destination"]), args.mode)

    sidecar = args.output_dir / "galileo_openwakeword_workspace_manifest.json"
    sidecar.parent.mkdir(parents=True, exist_ok=True)
    sidecar.write_text(json.dumps({"source_manifest": manifest, "files": planned}, indent=2) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
