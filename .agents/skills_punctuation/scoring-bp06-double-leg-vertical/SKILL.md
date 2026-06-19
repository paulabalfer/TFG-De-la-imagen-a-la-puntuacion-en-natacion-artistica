---
name: scoring-bp06-double-leg-vertical
description: Scorer for Double Leg Vertical (BP6) in artistic swimming. Use when the orchestrator tells you to score a swimmer known to be executing a Double Leg Vertical from a pool photograph. Reads the BP6 height chart and returns the raw height score plus the per-axis observations that the common-deductions module will convert into penalties.
---

# BP6 — Double Leg Vertical Scorer

## Position, in one sentence

Swimmer inverted in the water, **both legs pressed together**, **straight**, pointing **perpendicular** to the surface. Body = a single pencil line from crotch to toes.

## Reference height chart

File: `references/Double_leg_vertical_punctuation.png`.

The chart marks 8 height levels along the combined leg-and-trunk line:

| Mark | Water line location                               |
|------|----------------------------------------------------|
| 10   | At the **hip / crotch** (whole body out of water)  |
| 9.5  | Just below the hip                                  |
| 8.5  | Upper thigh                                         |
| 7.5  | Mid-thigh                                           |
| 6.5  | Above the knee                                      |
| 5.5  | At the **knee**                                     |
| 4.5  | Upper calf                                          |
| 3.5  | Mid-calf / toes only                                |

The **height score is the mark at which the water surface crosses the legs**. Higher = better.

---

## Step-by-step height reading

1. Locate the water line in the image (typically a clear horizontal contrast / splash line).
2. Identify the visible **front face of the body**: toes at the top, knee at the midpoint, hip at the bottom (where the body disappears into the water).
3. Map the body between toe and hip to the chart's eight marks (divide the leg into segments roughly like the chart).
4. Report the nearest mark. Use half-steps (3.5, 4.5, 5.5, …) only — do not invent intermediate values such as 6.0 or 7.0.

**Rule of thumb:**
- Hip at or just above surface → **10**
- Just below hip shows, but thigh is dry → **9.5**
- Water at mid-thigh → **7.5**
- Water at the knee → **5.5**
- Water at mid-calf → **4.5**
- Only toes / feet out of water → **3.5**

---

## What to observe (for the deductions module)

BP6 is the most unforgiving position because the visual shape is "one straight line". Observe:

- **Leg axis (D1)** — Is the hip→ankle line truly perpendicular to the water? Look for forward or backward tilt. Bands: almost vertical / 1–15° / 15–30° / >30°.
- **Knee extension (D2)** — Are BOTH knees fully locked? Even a subtle 10° bend must be called out.
- **Foot extension (D3)** — Are both feet pointed? Look at the angle between shin and foot top.
- **Body line (D4)** — Is the trunk straight with the legs, or is there a subtle hip pike? Any visible waist crease → subtle curve.
- **Partner leg (D5)** — N/A for BP6 (both legs are the reference leg).

---

## Disqualifiers (return `MISMATCH` to the orchestrator)

- A clearly visible **split** between the legs (different directions) → this is not BP6, it is BP8/BP14c/BP17.
- A pronounced **arch** in the trunk → this is BP14d or BP17.
- The body is **near the water surface** (reclined) rather than deeply inverted → BP14d.

When unsure whether the two legs are truly together (half-centimetre separation caused by splash), still score BP6 — but drop confidence to MEDIUM and add a note.

---

## Output

Return to the orchestrator:

```yaml
position:      BP6
height_score:  <one of 3.5, 4.5, 5.5, 6.5, 7.5, 8.5, 9.5, 10>
observations:
  leg_axis:    <band>
  knee:        <band>       # worst of the two legs
  foot:        <band>       # worst of the two feet
  body_line:   <band>
  partner_leg: n/a
notes:         <one line>
confidence:    HIGH | MEDIUM | LOW
```
