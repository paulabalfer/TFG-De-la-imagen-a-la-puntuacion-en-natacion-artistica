#!/usr/bin/env python3
"""
score_image.py — Entry point to score a single artistic-swimming image
against a KNOWN position, using the `scoring-orchestrator` skill.

This script is a thin driver. The real scoring logic lives in the
Claude skills under `.agents/skills_punctuation/`. This file:

  1. Validates inputs (image path + position label).
  2. Prints the canonical prompt to send to Claude so the orchestrator
     skill is invoked.

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
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
REFERENCES = ROOT.parent / "Data"/ "references" / "scoring"
AUGMENTED = ROOT.parent / "Data" / "Images"

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
    orchestrator_ref = "@.agents/skills_punctuation/scoring-orchestrator/SKILL.md"
    scorer_ref = f"@.agents/skills_punctuation/{skill}/SKILL.md"
    return (
        f"Use the `scoring-orchestrator` skill to score this image.\n\n"
        f"Image:        {image_path}\n"
        f"Position:     {name} ({code})\n"
        f"Scorer skill: {scorer_ref}\n"
        f"Height chart: {chart_path}\n\n"
        f"Follow {orchestrator_ref}: dispatch to the scorer, apply scoring-common-deductions, "
        f"and return the final 0–10 score in the orchestrator's output format."
    )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("image", type=Path, help="Path to the pool photograph")
    parser.add_argument("position", type=str, help="Position label (BP6 / Fishtail / etc.)")
    args = parser.parse_args()

    code = resolve_position(args.position)

    if not args.image.exists():
        position_name = POSITION_LABELS[code][0]
        candidate = AUGMENTED / position_name / args.image.name
        if candidate.exists():
            args.image = candidate
        else:
            print(f"ERROR: image not found: {args.image}", file=sys.stderr)
            print(f"       also tried:    {candidate}", file=sys.stderr)
            return 2

    prompt = build_prompt(args.image.resolve(), code)

    print("=" * 72)
    print("COPY THE FOLLOWING PROMPT INTO CLAUDE (with the image attached):")
    print("=" * 72)
    print(prompt)
    print("=" * 72)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
