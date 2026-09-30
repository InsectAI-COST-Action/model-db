#!/usr/bin/env python3
"""Validate registry schemas using the shared Python schema IR compiler."""

import argparse
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from iai_model_zoo.formats.schema import FormatError, Schema, compatible  # noqa: E402,F401

DEFAULT_ROOT = ROOT / "static" / "formats"


def validate(document):
    Schema.from_dict(document)


def check_file(path):
    Schema.load(path)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "paths",
        nargs="*",
        type=Path,
        help="Files or directories; defaults to static/formats",
    )
    args = parser.parse_args()
    files = sorted(
        {
            file
            for path in (args.paths or [DEFAULT_ROOT])
            for file in (path.rglob("*.json") if path.is_dir() else [path])
        }
    )
    if not files:
        parser.error("no format descriptors found")
    failed = False
    for path in files:
        try:
            check_file(path)
        except (ValueError, OSError) as exc:
            print(f"{path}: {exc}", file=sys.stderr)
            failed = True
    if failed:
        return 1
    print(f"Validated {len(files)} format descriptors.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
