"""
scorer.py — Automatic scoring of artistic swimming positions via Anthropic API.

Reads the skill files from the Punctuation project (scoring-orchestrator,
scoring-common-deductions, and the per-position scorer) and sends them as the
system prompt to Claude, together with the swimmer photo and the official height
reference chart. Returns the formatted score report.
"""
from __future__ import annotations

import base64
import io
from pathlib import Path

import anthropic
from PIL import Image

# Paths relative to this file
_APP_DIR = Path(__file__).parent
_REPO_ROOT = _APP_DIR.parent
_SKILLS_DIR = _REPO_ROOT / ".agents" / "skills_punctuation"
_CHARTS_DIR = _REPO_ROOT / "Punctuation" / "references"

# Per-position metadata: code, skill folder, height chart filename
POSITION_META: dict[str, dict[str, str]] = {
    "Bent Knee Surface Arch Position": {
        "code": "BP14d",
        "skill": "scoring-bp14d-bent-knee-surface-arch",
        "chart": "Bent_knee_surface_arch_punctuation.png",
    },
    "Bent Knee Vertical": {
        "code": "BP14c",
        "skill": "scoring-bp14c-bent-knee-vertical",
        "chart": "Bent_knee_vertical_punctuation.png",
    },
    "Double Leg Vertical": {
        "code": "BP6",
        "skill": "scoring-bp06-double-leg-vertical",
        "chart": "Double_leg_vertical_punctuation.png",
    },
    "Fishtail": {
        "code": "BP8",
        "skill": "scoring-bp08-fishtail",
        "chart": "Fishtail_punctuation.png",
    },
    "Knight": {
        "code": "BP17",
        "skill": "scoring-bp17-knight",
        "chart": "Knight_punctuation.png",
    },
}

# Shared skill files loaded once
_ORCHESTRATOR = (_SKILLS_DIR / "scoring-orchestrator" / "SKILL.md").read_text(encoding="utf-8")
_COMMON_DEDUCTIONS = (_SKILLS_DIR / "scoring-common-deductions" / "SKILL.md").read_text(encoding="utf-8")


def get_chart_image(position_name: str) -> Image.Image:
    """Return the PIL Image of the official height chart for a position."""
    chart_file = POSITION_META[position_name]["chart"]
    return Image.open(_CHARTS_DIR / chart_file)


def _pil_to_b64_jpeg(image: Image.Image, quality: int = 92) -> str:
    buf = io.BytesIO()
    image.convert("RGB").save(buf, format="JPEG", quality=quality)
    return base64.standard_b64encode(buf.getvalue()).decode()


def _load_position_skill(position_name: str) -> str:
    skill_folder = POSITION_META[position_name]["skill"]
    return (_SKILLS_DIR / skill_folder / "SKILL.md").read_text(encoding="utf-8")


def score_position(
    image: Image.Image,
    position_name: str,
    api_key: str,
    model: str = "claude-sonnet-4-6",
) -> str:
    """
    Score the execution of `position_name` in `image` using the Anthropic API.

    The system prompt embeds:
      1. scoring-orchestrator  (overall pipeline + output format)
      2. scoring-common-deductions  (D1–D5 deduction tables)
      3. per-position scorer  (height chart reading + position-specific rules)

    Two images are sent to the model:
      - The swimmer photograph (first image)
      - The official height reference chart (second image)

    Returns the model's formatted score report as a plain string.
    """
    meta = POSITION_META[position_name]
    position_skill = _load_position_skill(position_name)

    system = (
        f"{_ORCHESTRATOR}\n\n"
        f"---\n\n# COMMON DEDUCTIONS REFERENCE\n\n{_COMMON_DEDUCTIONS}\n\n"
        f"---\n\n# POSITION-SPECIFIC SCORER\n\n{position_skill}"
    )

    swimmer_b64 = _pil_to_b64_jpeg(image)
    chart_b64 = _pil_to_b64_jpeg(get_chart_image(position_name))

    client = anthropic.Anthropic(api_key=api_key)
    response = client.messages.create(
        model=model,
        max_tokens=1024,
        system=system,
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "image",
                        "source": {
                            "type": "base64",
                            "media_type": "image/jpeg",
                            "data": swimmer_b64,
                        },
                    },
                    {
                        "type": "image",
                        "source": {
                            "type": "base64",
                            "media_type": "image/jpeg",
                            "data": chart_b64,
                        },
                    },
                    {
                        "type": "text",
                        "text": (
                            f"Score this image as a **{position_name}** ({meta['code']}).\n"
                            f"The second image is the official height reference chart for this position.\n"
                            f"Follow the orchestrator pipeline exactly and return the full score report."
                        ),
                    },
                ],
            }
        ],
    )
    return response.content[0].text
