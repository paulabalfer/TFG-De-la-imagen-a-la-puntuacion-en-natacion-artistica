---
name: scoring-common-deductions
description: Shared deduction rules for artistic-swimming position scoring. Load this reference whenever a per-position scorer needs to apply angle deviations, knee/ankle alignment penalties, or body-line penalties. Encodes the official judge reference charts in a reusable form.
---

# Common Deductions — Reference Module

This module centralises the **deduction catalogue** that every per-position scorer in the Punctuation system applies on top of the raw height score. Keep this file small and normative: the scorers delegate here so that rule changes happen in one place.

All deductions are subtracted from the **height-based maximum** (the value read from the position's height chart, a number in the range [3.5 , 10]). The final score is:

```
final_score = max(0, height_score − Σ deductions)
```

---

## D1 — Leg-axis deviation from vertical

Source image: `references/Deductions.png`.

The "vertical leg" of the figure must be perpendicular to the water surface. Deviation is measured between the **hip → ankle** axis and the **true vertical** (a line normal to the water surface, not to the shoulders).

| Deviation (either forward or backward) | Deduction |
|----------------------------------------|-----------|
| 0° – 1°                                |  0        |
| 1° – 15°                               | −0.2      |
| 15° – 30°                              | −0.5      |
| > 30°                                  | −1.0      |

Notes:
- Deviation is **absolute** — tilting toward the face and tilting toward the back are penalised equally at the same magnitude.
- Lateral tilt (sideways, out of the camera plane) is harder to see from a single 2-D photo. If the pelvis is clearly rotated or the hip-line is not horizontal, treat it as a deviation of at least 15° for safety.
- **Cap at −1.0**: a leg deviated more than 45° is still only penalised −1.0 for this item; severe body-line failures are captured elsewhere (D4).

---

## D2 — Knee extension

The knee of the **reference leg** (the one being measured against the height chart) must be fully locked. A bent knee is a **proportional** penalty:

| Knee flexion (angle between thigh and shin at the knee) | Deduction |
|---------------------------------------------------------|-----------|
| 180° (fully extended)                                   |  0        |
| 170° – 180°                                             | −0.1      |
| 150° – 170°                                             | −0.3      |
| 120° – 150°                                             | −0.6      |
| < 120°                                                  | −1.0      |

Special cases:
- In **Bent-Knee Vertical (BP14c)** and **Bent-Knee Surface Arch (BP14d)** the *designed* bent knee of the position is NOT penalised — it is part of the shape. Only the **reference (vertical) leg** is scored under D2.
- A knee flexion that makes the leg rotate in the hip (external/internal rotation) also counts toward D1 if it bends the hip–ankle axis.

---

## D3 — Ankle / foot extension

The foot must be pointed (plantar-flexed). A cocked or relaxed foot is penalised:

| Foot alignment                                     | Deduction |
|----------------------------------------------------|-----------|
| Pointed, toes in line with shin                    |  0        |
| Slightly relaxed (≤15° dorsiflexion)               | −0.1      |
| Visibly cocked (15°–45° dorsiflexion)              | −0.2      |
| Flat / hooked (> 45° dorsiflexion or heel leading) | −0.3      |

This rule applies to **every foot visible above water**, not only the reference leg. Sum the deductions across feet (cap at −0.5 per foot).

---

## D4 — Body-line / trunk alignment

Applies only to positions where the trunk is expected to be **straight** (BP6, BP8, BP14c):

| Observed trunk         | Deduction |
|------------------------|-----------|
| Straight, aligned with reference leg | 0 |
| Subtle curve (< 10°)   | −0.1      |
| Moderate curve (10°–25°) | −0.3    |
| Pronounced bend        | −0.6      |

For **arched positions** (BP14d, BP17), the arch is *required* by the figure and is not penalised under D4. Instead, a **missing** arch is penalised as a shape failure at the orchestrator level.

---

## D5 — Partner-leg shape (only BP8, BP17, BP14c, BP14d)

In positions with a second non-vertical leg, that leg also has expected angles:

| Position | Expected second-leg shape | Deduction for deviation |
|----------|---------------------------|-------------------------|
| BP8 Fishtail | Straight, horizontal, 90° to vertical leg | Same D1 scale |
| BP17 Knight  | Straight, horizontal, 90° to vertical leg | Same D1 scale |
| BP14c BKV    | Thigh horizontal, shin folded back | Use D1 on thigh, D2 on knee is *expected* |
| BP14d BKSA   | Thigh vertical (down), shin horizontal | Use D1 on thigh |

---

## Evaluation heuristics (single 2-D image)

The scorer is a vision model reading a single photograph. Angles cannot always be measured exactly — use these heuristic bands:

- **"Almost vertical"** (≤5° visible deviation) → treat as 0 deduction.
- **"Clearly tilted, but still mostly up"** → 1°–15° band → −0.2.
- **"Leaning noticeably forward/back"** → 15°–30° band → −0.5.
- **"Collapsed / far from vertical"** → >30° band → −1.0.

When in doubt between two adjacent bands, prefer the **smaller** deduction (err toward the swimmer). Record the chosen band and a one-line justification in the output.

---

## Output convention

Each scorer must emit deductions in this flat form so the orchestrator can sum them:

```
deductions:
  D1_leg_axis:          <value>   # reason: "tilted ~10° toward face"
  D2_knee_extension:    <value>   # reason: "locked"
  D3_foot_extension:    <value>   # reason: "slightly relaxed"
  D4_body_line:         <value>   # reason: "n/a — position expects arch"
  D5_partner_leg:       <value>   # reason: "horizontal leg sagging ~20°"
  total:                <sum>
```

The orchestrator computes `final_score = max(0, height_score − total)` and rounds to 1 decimal.
