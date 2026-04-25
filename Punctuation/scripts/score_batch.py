#!/usr/bin/env python3
"""
score_batch.py — Iterate over a labelled image directory and print the
canonical orchestrator prompt for each image.

Expects a directory layout like:

    Data/Images/
        Fishtail/*.jpg
        Knight/*.jpg
        Double Leg Vertical/*.jpg
        Bent Knee Vertical/*.jpg
        Bent Knee Surface Arch Position/*.jpg

Usage:
    python score_batch.py <images_root>
    python score_batch.py ../../Data/Images
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

from score_image import POSITION_LABELS, NAME_TO_CODE, build_prompt

# Accepted folder names → canonical BP code
FOLDER_ALIASES = {
    "Fishtail":                         "BP8",
    "Knight":                           "BP17",
    "Double Leg Vertical":              "BP6",
    "Bent Knee Vertical":               "BP14c",
    "Bent Knee Surface Arch Position":  "BP14d",
    "Bent Knee Surface Arch":           "BP14d",
}

IMAGE_EXTS = {".jpg", ".jpeg", ".png", ".bmp"}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("images_root", type=Path, help="Directory containing one sub-folder per position")
    parser.add_argument("--limit", type=int, default=0, help="Max images per class (0 = all)")
    args = parser.parse_args()

    if not args.images_root.is_dir():
        print(f"ERROR: not a directory: {args.images_root}", file=sys.stderr)
        return 2

    total = 0
    for subdir in sorted(args.images_root.iterdir()):
        if not subdir.is_dir():
            continue
        code = FOLDER_ALIASES.get(subdir.name)
        if not code:
            print(f"[skip] unknown folder: {subdir.name}")
            continue
        imgs = sorted([p for p in subdir.iterdir() if p.suffix.lower() in IMAGE_EXTS])
        if args.limit:
            imgs = imgs[:args.limit]
        for img in imgs:
            total += 1
            print("\n" + "#" * 72)
            print(f"# [{total}] {img.name}")
            print("#" * 72)
            print(build_prompt(img.resolve(), code))

    print(f"\n\nTotal prompts: {total}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
