---
name: scoring-bp08-fishtail
description: Scorer for Fishtail (BP8) in artistic swimming. Use when the orchestrator declares the image is a Fishtail. Reads the BP8 height chart on the VERTICAL leg, returns the raw height score, and emits observations covering the horizontal forward leg, knee/ankle extension, and body line for the common-deductions module.
---

# BP8 — Fishtail Scorer

## Position, in one sentence

Inverted swimmer with **one vertical leg pointing straight up** and **one straight leg extended horizontally FORWARD** (toward the face/chest). Both legs fully straight, trunk straight, no arch. Shape = an L or T.

## Reference height chart

File: `references/Fishtail_punctuation.png`.

The 8 marks (3.5 → 10) run along the **vertical leg only**. The horizontal leg is not on the chart — it is evaluated under deductions (D5).

| Mark | Water line location on the vertical leg            |
|------|----------------------------------------------------|
| 10   | Water at the **crotch** (full vertical leg dry)    |
| 9.5  | Just below the crotch                               |
| 8.5  | Upper thigh                                         |
| 7.5  | Mid-thigh                                           |
| 6.5  | Above the knee                                      |
| 5.5  | At the **knee**                                     |
| 4.5  | Upper calf                                          |
| 3.5  | Mid-calf / only foot visible                        |

---

## Step-by-step height reading

1. Identify the **vertical** leg (the one pointing up). In the chart it is the upper leg; in the photo it is the one whose ankle is highest.
2. Ignore the horizontal leg for height scoring — even if it is above water, it does not change the height score.
3. Find where the water crosses the vertical leg.
4. Map to one of the 8 marks (half-steps only).

**If the horizontal leg obscures part of the vertical leg's water line**, read the score from the side of the vertical leg that is free of overlap.

---

## What to observe (for the deductions module)

- **Leg axis (D1)** — Is the vertical leg perpendicular to the water? Fishtail frequently leans **forward** (over the face) because the horizontal leg pulls the centre of mass. Bands: almost vertical / 1–15° forward / 15–30° forward / >30°. Backward tilt is rare but scored equally.
- **Knee extension (D2)** — Both knees must be locked. The vertical-leg knee is the reference; if the horizontal leg bends at the knee, this is a major shape failure — report it but primarily weigh the vertical leg.
- **Foot extension (D3)** — Both feet pointed. Evaluate both.
- **Body line (D4)** — The trunk must be **straight**, in line with the vertical leg. Any arch is a shape failure.
- **Partner leg — horizontal leg (D5)** — The horizontal leg must be:
  - **Forward** (face side). If it goes backward, this is Knight, not Fishtail → `MISMATCH`.
  - **Horizontal** (parallel to the water). Sagging below the water line or rising above 90° each count as D5 deviation with the same D1 scale (1–15° = −0.2, 15–30° = −0.5, >30° = −1.0).
  - **Straight**. A bent horizontal leg is a shape failure (→ BP14c/BP14d).

---

## Disqualifiers (return `MISMATCH` to the orchestrator)

- Horizontal leg extends **backward** (toward spine) → this is BP17 (Knight).
- Trunk is **arched** → BP17 or BP14d.
- A knee is **clearly bent** in a designed way → BP14c or BP14d.
- Both legs together, no split → BP6.

When there is barely any split (legs almost touching), first check for a subtle knee bend; if none, still score as Fishtail with LOW confidence.

---

## Output

```yaml
position:      BP8
height_score:  <one of 3.5, 4.5, 5.5, 6.5, 7.5, 8.5, 9.5, 10>
observations:
  leg_axis:    <band>          # vertical leg
  knee:        <band>          # worst of the two legs
  foot:        <band>          # worst of the two feet
  body_line:   <band>
  partner_leg: <band>          # horizontal leg deviation from true horizontal
notes:         <one line>
confidence:    HIGH | MEDIUM | LOW
```
