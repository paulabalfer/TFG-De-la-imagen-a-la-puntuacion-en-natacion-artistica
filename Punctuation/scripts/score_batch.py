#!/usr/bin/env python3
"""
score_batch.py — Generate one scoring prompt per image listed in subset_puntuation.xlsx
and write them all to data/prompts_<timestamp>.txt (one prompt per entry, separated by ---).

Usage:
    python score_batch.py [--images-root PATH] [--input PATH] [--output PATH] [--limit N]
"""
from __future__ import annotations

import argparse

from datetime import datetime
from pathlib import Path

import openpyxl

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent

IMAGES_ROOT_DEFAULT = ROOT.parent / "Data" / "Images"

# normalised position name → (BP code, skill folder, canonical folder name)
POSITION_MAP: dict[str, tuple[str, str, str]] = {
    "bent knee surface arch position": (
        "BP14d", "scoring-bp14d-bent-knee-surface-arch", "Bent Knee Surface Arch Position"
    ),
    "bent knee vertical": (
        "BP14c", "scoring-bp14c-bent-knee-vertical", "Bent Knee Vertical"
    ),
    "double leg vertical": (
        "BP6",  "scoring-bp06-double-leg-vertical",  "Double Leg Vertical"
    ),
    "fishtail": (
        "BP8",  "scoring-bp08-fishtail",             "Fishtail"
    ),
    "knight": (
        "BP17", "scoring-bp17-knight",               "Knight"
    ),
}


# ── Skill loading ─────────────────────────────────────────────────────────────



def _build_user_message(bp_code: str, position_name: str, image_name: str) -> str:
    image_ref = f"@Data/Images/{position_name}/{image_name}"
    skill_ref = "@.claude/skills/scoring-orchestrator/SKILL.md"
    return (
        f"Score this image.\n\n"
        f"Position: {position_name} ({bp_code})\n"
        f"Image: {image_ref}\n\n"
        f"Follow the orchestrator pipeline exactly: dispatch to the position scorer, "
        f"apply common deductions, and return the final score using the output format "
        f"specified in the orchestrator skill. "
        f"Use the scoring orchestrator {skill_ref}"
    )


# ── Input parsing ─────────────────────────────────────────────────────────────

def read_excel_input(xlsx_path: Path) -> list[tuple[str, str]]:
    wb = openpyxl.load_workbook(xlsx_path)
    ws = wb.active
    pairs = []
    for row in ws.iter_rows(min_row=2, values_only=True):
        pos, img = row[0], row[1]
        if pos and img:
            pairs.append((str(pos).strip(), str(img).strip()))
    return pairs


# ── CLI ───────────────────────────────────────────────────────────────────────

def main() -> int:
    default_output = ROOT / "data" / f"prompts_generated.txt"
    parser = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "--images-root", type=Path, default=IMAGES_ROOT_DEFAULT,
        help="Root containing one sub-folder per position",
    )
    parser.add_argument(
        "--input", type=Path,
        default=ROOT / "data" / "subset_puntuation.xlsx",
        help="Input Excel with POSITION and IMAGE columns",
    )
    parser.add_argument(
        "--output", type=Path, default=default_output,
        help="Output .txt file (JSON Lines, one prompt per line)",
    )
    parser.add_argument(
        "--limit", type=int, default=0,
        help="Max images to process (0 = all)",
    )
    args = parser.parse_args()

    pairs = read_excel_input(args.input)
    if args.limit:
        pairs = pairs[: args.limit]

    total = len(pairs)
    print(f"Generating prompts for {total} images → {args.output}\n")

    blocks: list[str] = []
    skipped = 0
    for i, (position_raw, image_name) in enumerate(pairs, 1):
        key = position_raw.lower()
        entry = POSITION_MAP.get(key)
        if not entry:
            print(f"[{i:3}/{total}] SKIP — unknown position: {position_raw!r}")
            skipped += 1
            continue

        bp_code, _, position_name = entry
        image_path = args.images_root / position_name / image_name

        if not image_path.exists():
            print(f"[{i:3}/{total}] MISSING — {image_path}")
            skipped += 1
            continue

        blocks.append(_build_user_message(bp_code, position_name, image_name))
        print(f"[{i:3}/{total}] OK — {image_name} ({position_name})")

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text("\n---\n".join(blocks) + "\n", encoding="utf-8")

    n_ok = len(blocks)
    print(f"\nDone. {n_ok}/{total} prompts written → {args.output}  ({skipped} skipped)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
