#!/usr/bin/env python3
"""
score_image.py — Entry point to score a single artistic-swimming image
against a KNOWN position, using the `scoring-orchestrator` skill.

This script is a thin driver. The real scoring logic lives in the
Claude skills under `.claude/skills/`. This file:

  1. Validates inputs (image path + position label).
  2. Prints the canonical prompt to send to Claude so the orchestrator
     skill is invoked.
  3. If a predictions JSON already exists in results/, updates it with
     any new score the user pastes back.

Usage:
    python score_image.py <image_path> <position>
    python score_image.py ../../Data/Images/Fishtail/001.jpg Fishtail
    python score_image.py <image> BP8

Valid position labels:
    BP6   | Double Leg Vertical
    BP8   | Fishtail
    BP14c | Bent Knee Vertical
    BP14d | Bent Knee Surface Arch
    BP17  | Knight
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
RESULTS = ROOT / "results"
REFERENCES = ROOT / "references"

POSITION_LABELS = {
    "BP6":  ("Double Leg Vertical",            "scoring-bp06-double-leg-vertical",    "Double_leg_vertical_punctuation.png"),
    "BP8":  ("Fishtail",                       "scoring-bp08-fishtail",               "Fishtail_punctuation.png"),
    "BP14c":("Bent Knee Vertical",             "scoring-bp14c-bent-knee-vertical",    "Bent_knee_vertical_punctuation.png"),
    "BP14d":("Bent Knee Surface Arch Position","scoring-bp14d-bent-knee-surface-arch","Bent_knee_surface_arch_punctuation.png"),
    "BP17": ("Knight",                         "scoring-bp17-knight",                 "Knight_punctuation.png"),
}

NAME_TO_CODE = {name.lower(): code for code, (name, _, _) in POSITION_LABELS.items()}


def resolve_position(raw: str) -> str:
    """Accept BP6, 'Fishtail', 'fishtail', etc. Return canonical BP code."""
    s = raw.strip()
    if s in POSITION_LABELS:
        return s
    if s.lower() in NAME_TO_CODE:
        return NAME_TO_CODE[s.lower()]
    raise SystemExit(f"Unknown position '{raw}'. Valid: {list(POSITION_LABELS.keys())}")


def build_prompt(image_path: Path, code: str) -> str:
    name, skill, chart = POSITION_LABELS[code]
    chart_path = REFERENCES / chart
    return (
        f"Use the `scoring-orchestrator` skill to score this image.\n\n"
        f"Image:       {image_path}\n"
        f"Position:    {name} ({code})\n"
        f"Scorer:      {skill}\n"
        f"Height chart: {chart_path}\n\n"
        f"Dispatch to the scorer, apply scoring-common-deductions, and return "
        f"the final 0–10 score in the orchestrator's output format."
    )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("image", type=Path, help="Path to the pool photograph")
    parser.add_argument("position", type=str, help="Position label (BP6 / Fishtail / etc.)")
    parser.add_argument("--out", type=Path, default=RESULTS / "predictions.json",
                        help="Path to predictions JSON (appended)")
    args = parser.parse_args()

    if not args.image.exists():
        print(f"ERROR: image not found: {args.image}", file=sys.stderr)
        return 2

    code = resolve_position(args.position)
    prompt = build_prompt(args.image.resolve(), code)

    print("=" * 72)
    print("COPY THE FOLLOWING PROMPT INTO CLAUDE (with the image attached):")
    print("=" * 72)
    print(prompt)
    print("=" * 72)

    # Bootstrap an empty predictions file if none exists.
    args.out.parent.mkdir(parents=True, exist_ok=True)
    if not args.out.exists():
        args.out.write_text("[]", encoding="utf-8")
        print(f"\nInitialised empty predictions file at {args.out}")
    else:
        print(f"\nExisting predictions file: {args.out}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
