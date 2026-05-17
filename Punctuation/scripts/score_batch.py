#!/usr/bin/env python3
"""
score_batch.py — Score every image listed in subset_puntuation.xlsx using
the Claude API with the full scoring-orchestrator skill pipeline.
Numerical results (height score, D1-D5 deductions, final score, confidence)
are written to results/scores_<timestamp>.xlsx.

Usage:
    python score_batch.py [--images-root PATH] [--input PATH] [--output PATH] [--limit N]

Requires the ANTHROPIC_API_KEY environment variable to be set.
"""
from __future__ import annotations

import argparse
import base64
import os
import re
import sys
from datetime import datetime
from pathlib import Path

import anthropic
import openpyxl
from openpyxl.styles import Alignment, Font, PatternFill

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
SKILLS_DIR = ROOT / ".claude" / "skills"
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

def _load_skill(folder: str) -> str:
    """Read a SKILL.md, stripping the YAML frontmatter block."""
    path = SKILLS_DIR / folder / "SKILL.md"
    text = path.read_text(encoding="utf-8")
    if text.startswith("---"):
        end = text.index("---", 3)
        text = text[end + 3:].lstrip()
    return text


def _build_system_prompt(position_skill_folder: str) -> str:
    orchestrator     = _load_skill("scoring-orchestrator")
    common_deductions = _load_skill("scoring-common-deductions")
    position_scorer  = _load_skill(position_skill_folder)
    return (
        "You are an artistic-swimming judge assistant operating within the "
        "Punctuation scoring system.\n\n"
        "## ORCHESTRATOR\n\n" + orchestrator + "\n\n"
        "## COMMON DEDUCTIONS\n\n" + common_deductions + "\n\n"
        "## POSITION SCORER\n\n" + position_scorer
    )


# ── Image helpers ─────────────────────────────────────────────────────────────

def _encode_image(path: Path) -> tuple[str, str]:
    """Return (base64_data, media_type)."""
    media = {
        ".jpg":  "image/jpeg",
        ".jpeg": "image/jpeg",
        ".png":  "image/png",
        ".bmp":  "image/bmp",
    }.get(path.suffix.lower(), "image/jpeg")
    data = base64.standard_b64encode(path.read_bytes()).decode()
    return data, media


# ── Response parsing ──────────────────────────────────────────────────────────

def _parse_response(text: str) -> dict:
    """Extract numerical and qualitative fields from the orchestrator output."""

    def find(pattern: str, default=None):
        m = re.search(pattern, text, re.IGNORECASE | re.MULTILINE)
        return m.group(1).strip() if m else default

    return {
        "height_score":  find(r"Height score:\s*([\d.]+)"),
        "d1_leg_axis":   find(r"D1\s+leg\s+axis\s+([-\d.]+)"),
        "d2_knee":       find(r"D2\s+knee(?:\s+extension)?\s+([-\d.]+)"),
        "d3_foot":       find(r"D3\s+foot(?:\s+extension)?\s+([-\d.]+)"),
        "d4_body_line":  find(r"D4\s+body(?:\s+line)?\s+([-\d.]+)"),
        "d5_partner":    find(r"D5\s+partner(?:\s+leg)?\s+([-\d.]+)"),
        "total_ded":     find(r"^total\s+([-\d.]+)", ),
        "final_score":   find(r"Final score:\s*([\d.]+)"),
        "confidence":    find(r"Confidence:\s*(\w+)"),
        "notes":         find(r"Notes:\s*(.+)"),
        "mismatch":      "MISMATCH" in text,
        "raw":           text,
    }


# ── Scoring ───────────────────────────────────────────────────────────────────

def score_image(
    client: anthropic.Anthropic,
    image_path: Path,
    bp_code: str,
    position_name: str,
    skill_folder: str,
    model: str,
) -> dict:
    img_data, media_type = _encode_image(image_path)
    system = _build_system_prompt(skill_folder)

    user_msg = (
        f"Score this image.\n\n"
        f"Position: {position_name} ({bp_code})\n"
        f"Image: {image_path.name}\n\n"
        f"Follow the orchestrator pipeline exactly: dispatch to the position scorer, "
        f"apply common deductions, and return the final score using the output format "
        f"specified in the orchestrator skill."
    )

    message = client.messages.create(
        model=model,
        max_tokens=1024,
        system=system,
        messages=[{
            "role": "user",
            "content": [
                {
                    "type": "image",
                    "source": {
                        "type": "base64",
                        "media_type": media_type,
                        "data": img_data,
                    },
                },
                {"type": "text", "text": user_msg},
            ],
        }],
    )

    result = _parse_response(message.content[0].text)
    result["image"]    = image_path.name
    result["position"] = position_name
    result["bp_code"]  = bp_code
    return result


# ── Excel output ──────────────────────────────────────────────────────────────

_HEADER_FILL = PatternFill("solid", fgColor="1F4E79")
_HEADER_FONT = Font(bold=True, color="FFFFFF")
_ERROR_FILL  = PatternFill("solid", fgColor="FFC7CE")

_COLUMNS: list[tuple[str, str, int]] = [
    ("Image",             "image",        20),
    ("Position",          "position",     32),
    ("Code",              "bp_code",       8),
    ("Height Score",      "height_score", 13),
    ("D1 Leg Axis",       "d1_leg_axis",  13),
    ("D2 Knee",           "d2_knee",      12),
    ("D3 Foot",           "d3_foot",      12),
    ("D4 Body Line",      "d4_body_line", 13),
    ("D5 Partner Leg",    "d5_partner",   14),
    ("Total Deductions",  "total_ded",    17),
    ("Final Score",       "final_score",  13),
    ("Confidence",        "confidence",   12),
    ("Notes",             "notes",        50),
    ("Mismatch",          "mismatch",     10),
    ("Error",             "error",        30),
]

_NUMERIC_KEYS = {"height_score", "d1_leg_axis", "d2_knee", "d3_foot",
                 "d4_body_line", "d5_partner", "total_ded", "final_score"}


def _to_num(v):
    try:
        return float(v) if v is not None else None
    except (ValueError, TypeError):
        return None


def save_results(rows: list[dict], output_path: Path) -> None:
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Scores"

    for col_idx, (header, _, width) in enumerate(_COLUMNS, 1):
        cell = ws.cell(row=1, column=col_idx, value=header)
        cell.fill = _HEADER_FILL
        cell.font = _HEADER_FONT
        cell.alignment = Alignment(horizontal="center")
        ws.column_dimensions[
            openpyxl.utils.get_column_letter(col_idx)
        ].width = width

    for row_idx, r in enumerate(rows, 2):
        is_error = bool(r.get("error")) or bool(r.get("mismatch"))
        for col_idx, (_, key, _) in enumerate(_COLUMNS, 1):
            value = r.get(key)
            if key in _NUMERIC_KEYS:
                value = _to_num(value)
            cell = ws.cell(row=row_idx, column=col_idx, value=value)
            if is_error:
                cell.fill = _ERROR_FILL

    output_path.parent.mkdir(parents=True, exist_ok=True)
    wb.save(output_path)


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
    default_output = (
        ROOT / "results" / f"scores_{datetime.now():%Y%m%d_%H%M%S}.xlsx"
    )
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
        help="Output Excel file path",
    )
    parser.add_argument(
        "--limit", type=int, default=0,
        help="Max images to score (0 = all)",
    )
    parser.add_argument(
        "--model", type=str, default="claude-opus-4-7",
        help="Claude model to use (default: claude-opus-4-7)",
    )
    args = parser.parse_args()

    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        print("ERROR: ANTHROPIC_API_KEY environment variable is not set.", file=sys.stderr)
        return 1

    client = anthropic.Anthropic(api_key=api_key)

    pairs = read_excel_input(args.input)
    if args.limit:
        pairs = pairs[: args.limit]

    total = len(pairs)
    print(f"Scoring {total} images → {args.output}\n")

    results: list[dict] = []
    for i, (position_raw, image_name) in enumerate(pairs, 1):
        key = position_raw.lower()
        entry = POSITION_MAP.get(key)
        if not entry:
            print(f"[{i:3}/{total}] SKIP — unknown position: {position_raw!r}")
            results.append({"image": image_name, "position": position_raw,
                            "error": "unknown position"})
            continue

        bp_code, skill_folder, position_name = entry
        image_path = args.images_root / position_name / image_name

        if not image_path.exists():
            print(f"[{i:3}/{total}] MISSING — {image_path}")
            results.append({"image": image_name, "position": position_name,
                            "bp_code": bp_code,
                            "error": f"file not found: {image_path}"})
            continue

        print(f"[{i:3}/{total}] {image_name} ({position_name}) ...", end=" ", flush=True)
        try:
            r = score_image(client, image_path, bp_code, position_name,
                            skill_folder, args.model)
            results.append(r)
            tag = " [MISMATCH]" if r.get("mismatch") else ""
            print(f"→ {r.get('final_score', '?')}  [{r.get('confidence', '?')}]{tag}")
        except Exception as exc:
            print(f"ERROR: {exc}")
            results.append({"image": image_name, "position": position_name,
                            "bp_code": bp_code, "error": str(exc)})

    save_results(results, args.output)
    n_ok = sum(1 for r in results if r.get("final_score") is not None)
    print(f"\nDone. {n_ok}/{total} images scored successfully → {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
