---
name: scoring-bp14c-bent-knee-vertical
description: Scorer for Bent Knee Vertical (BP14c) in artistic swimming. Use when the orchestrator declares the image is a Bent Knee Vertical. Reads the BP14c height chart on the VERTICAL leg; the bent partner leg is scored only on its thigh angle (horizontal) and knee positioning — the knee flexion itself is the shape and is NOT penalised.
---

# BP14c — Bent Knee Vertical Scorer

## Position, in one sentence

Inverted swimmer with **one vertical leg up** and the **other leg bent sharply at the knee**: the bent thigh stays horizontal, the shin folds back toward the vertical leg, forming a "4" silhouette. Trunk is **straight**, no arch.

## Reference height chart

File: `references/Bent_knee_vertical_punctuation.png`.

The marks run along the **vertical leg** (same layout as BP6 and BP8).

| Mark | Water line location on the vertical leg            |
|------|----------------------------------------------------|
| 10   | At the crotch                                       |
| 9.5  | Just below the crotch                               |
| 8.5  | Upper thigh                                         |
| 7.5  | Mid-thigh                                           |
| 6.5  | Above the knee                                      |
| 5.5  | At the knee of the vertical leg                     |
| 4.5  | Upper calf                                          |
| 3.5  | Mid-calf / foot only                                |

The bent partner leg is **not** used for height. Read the vertical leg alone.

---

## Step-by-step height reading

1. Identify the **vertical** leg (uninterrupted, going straight up). Do not confuse it with the bent thigh — the bent thigh is near-horizontal.
2. Find the water line on the vertical leg.
3. Map to one of the 8 marks (half-steps only).

If the bent shin crosses in front of the vertical leg and hides the water line, use the back edge of the vertical leg to read the mark.

---

## What to observe (for the deductions module)

- **Leg axis (D1)** — Vertical leg perpendicular to water. Forward/backward tilt banded as 1–15° / 15–30° / >30°.
- **Knee extension (D2)** — Applies **only to the vertical leg**. The bent knee of the partner leg is the shape itself and is NOT penalised here. If the vertical leg shows any bend, apply D2.
- **Foot extension (D3)** — Both feet pointed. The bent-leg foot is usually near the opposite thigh; it still must be pointed.
- **Body line (D4)** — Trunk must be straight. Any visible back arch is a shape failure — re-check whether this is actually BP14d (BKSA).
- **Partner leg — bent leg (D5)** — The expected shape is:
  - **Thigh horizontal** (90° to the vertical leg). Thigh rising above or sagging below horizontal → D1-scale deviation.
  - **Shin folded back** so the foot points toward the inner thigh of the vertical leg. A shin that continues outward (open triangle) is a shape failure.

---

## Disqualifiers (return `MISMATCH` to the orchestrator)

- Trunk is **arched** → BP14d (BKSA).
- BOTH legs are straight (no knee bend) → BP8 or BP17.
- Both legs together → BP6.
- No visible vertical leg at all → not BP14c.

---

## Output

```yaml
position:      BP14c
height_score:  <one of 3.5, 4.5, 5.5, 6.5, 7.5, 8.5, 9.5, 10>
observations:
  leg_axis:    <band>    # vertical leg only
  knee:        <band>    # vertical leg only (bent leg is expected)
  foot:        <band>    # worst of the two feet
  body_line:   <band>
  partner_leg: <band>    # thigh-horizontal deviation of the bent leg
notes:         <one line>
confidence:    HIGH | MEDIUM | LOW
```
