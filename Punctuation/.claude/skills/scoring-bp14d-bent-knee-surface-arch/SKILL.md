---
name: scoring-bp14d-bent-knee-surface-arch
description: Scorer for Bent Knee Surface Arch (BP14d) in artistic swimming. Use when the orchestrator declares the image is a Bent Knee Surface Arch. Reads the BP14d height chart on the VERTICAL thigh (the body is near the surface with an arched back), and emits observations that treat the arch and the bent knee as expected shape, not as deductions.
---

# BP14d — Bent Knee Surface Arch Scorer

## Position, in one sentence

Swimmer lies near the surface with an **arched back** (curved backward, bow shape). **One knee is bent**: its thigh points **straight down** (vertical), its shin is horizontal toward the face. The other leg extends along the surface. The score is read on the **vertical thigh** of the bent leg.

## Reference height chart

File: `references/Bent_knee_surface_arch_punctuation.png`.

The marks are denser around the thigh because the body is close to the surface. The chart begins at **5**, not 3.5 — this is position-specific.

| Mark | Water line location on the **vertical thigh**       |
|------|-----------------------------------------------------|
| 10   | At the hip of the bent leg (thigh fully dry)        |
| 9.5  | Just below the hip                                  |
| 8.5  | Upper thigh                                         |
| 7.5  | Mid-thigh                                           |
| 6.5  | Above the knee                                      |
| 5.5  | At the knee                                         |
| 5    | Just below the knee (minimum possible)              |

**Allowed values: 5, 5.5, 6.5, 7.5, 8.5, 9.5, 10.** Do not emit 3.5 or 4.5 for BP14d.

---

## Step-by-step height reading

1. Identify the **bent leg**: the leg whose knee is flexed roughly 90°.
2. The bent leg's **thigh** should be vertical (perpendicular to the water). Find the water line on that thigh.
3. Map to one of the 7 marks.

The **horizontal partner leg** (the extended one along the surface) is NOT used for height scoring.

---

## What to observe (for the deductions module)

- **Leg axis (D1)** — Applies to the **vertical thigh of the bent leg**. Forward/backward tilt banded as 1–15° / 15–30° / >30°.
- **Knee extension (D2)** — Applies to the **extended partner leg only**. The bent knee of the scored leg is the shape and is NOT penalised.
- **Foot extension (D3)** — Both feet pointed. The bent-leg foot (usually near the face) and the extended-leg foot (at the surface) each evaluated.
- **Body line (D4)** — The arch is **required**. Do NOT penalise the arch; instead, penalise its **absence**:
  - Pronounced, smooth arch → 0
  - Shallow arch → −0.1
  - Barely arched / flat trunk → −0.3 and flag the position (may be BP14c)
- **Partner leg — extended leg (D5)** — Expected shape:
  - Lies **horizontal at the surface**.
  - **Straight** knee. A bend here (D2 above) is also a shape concern.
  - Sagging below the water or rising above the surface → D1-scale deviation.

---

## Disqualifiers (return `MISMATCH` to the orchestrator)

- Trunk is **straight**, no arch → BP14c (BKV).
- **Both** legs straight → BP17 (Knight) or BP8 (Fishtail).
- Body is **deeply inverted** (not at the surface) → BP14c.

---

## Output

```yaml
position:      BP14d
height_score:  <one of 5, 5.5, 6.5, 7.5, 8.5, 9.5, 10>
observations:
  leg_axis:    <band>    # vertical thigh of the bent leg
  knee:        <band>    # extended partner leg
  foot:        <band>    # worst of the two feet
  body_line:   <band>    # scored as missing-arch here
  partner_leg: <band>    # extended leg horizontality
notes:         <one line>
confidence:    HIGH | MEDIUM | LOW
```
