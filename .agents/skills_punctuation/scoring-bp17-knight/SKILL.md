---
name: scoring-bp17-knight
description: Scorer for Knight (BP17) in artistic swimming. Use when the orchestrator declares the image is a Knight. Reads the BP17 height chart on the VERTICAL leg (same chart layout as Fishtail), but expects an ARCHED trunk and a straight horizontal leg going BACKWARD. The arch is part of the shape and is NOT penalised — only a missing arch is.
---

# BP17 — Knight Scorer

## Position, in one sentence

Inverted swimmer with **one vertical leg up**, **back arched** (spine curves backward), and **one straight leg extending BACKWARD** (toward the spine) at horizontal. Silhouette = an "inverted arabesque".

## Reference height chart

File: `references/Knight_punctuation.png`.

The 8 marks (3.5 → 10) run along the **vertical leg**, same as BP8. The horizontal backward leg is scored via deductions (D5).

| Mark | Water line location on the vertical leg            |
|------|----------------------------------------------------|
| 10   | At the hip                                         |
| 9.5  | Just below the hip                                 |
| 8.5  | Upper thigh                                        |
| 7.5  | Mid-thigh                                          |
| 6.5  | Above the knee                                     |
| 5.5  | At the knee                                        |
| 4.5  | Upper calf                                         |
| 3.5  | Mid-calf / foot only                               |

**Important:** because the trunk is arched, the "hip" in BP17 is displaced forward relative to the shoulders. Read the mark from where water meets the **vertical leg itself**, not the hip bone.

---

## Step-by-step height reading

1. Identify the **vertical** leg. It should be the one going more-or-less straight up.
2. Ignore the backward leg and the arched trunk for height scoring.
3. Find the water line on the vertical leg.
4. Map to the 8 marks (half-steps only).

---

## What to observe (for the deductions module)

- **Leg axis (D1)** — The vertical leg must be perpendicular to the water. In Knight, the arch pushes the hip forward, which can pull the vertical leg **backward** at the top. Bands: almost vertical / 1–15° / 15–30° / >30°.
- **Knee extension (D2)** — **Both legs must be straight.** Any bend in either leg is a shape failure (re-check whether this is actually BP14d).
- **Foot extension (D3)** — Both feet pointed.
- **Body line (D4)** — The **arch is required**. Do NOT penalise a present arch; instead, penalise its absence:
  - Pronounced, smooth arch → 0
  - Shallow arch → −0.1
  - Barely arched / trunk almost straight → −0.3 and flag (may be BP8)
- **Partner leg — horizontal backward leg (D5)** — Expected shape:
  - **Backward** (spine side). If it goes forward, this is BP8 → `MISMATCH`.
  - **Horizontal** relative to the water. Sagging below or rising above horizontal → D1-scale deviation.
  - **Straight**. A bent back leg is a shape failure.

---

## Disqualifiers (return `MISMATCH` to the orchestrator)

- Horizontal leg extends **forward** (face side) → BP8 (Fishtail).
- A knee is **bent** → BP14c (BKV) or BP14d (BKSA).
- Both legs together → BP6.

Special attention to **Knight ↔ Fishtail** confusion: they differ ONLY in back arch + leg direction. If in doubt, prefer the position the orchestrator declared — this skill's job is not to re-classify.

---

## Output

```yaml
position:      BP17
height_score:  <one of 3.5, 4.5, 5.5, 6.5, 7.5, 8.5, 9.5, 10>
observations:
  leg_axis:    <band>    # vertical leg only
  knee:        <band>    # worst of the two legs
  foot:        <band>    # worst of the two feet
  body_line:   <band>    # scored as missing-arch here
  partner_leg: <band>    # horizontal backward leg deviation from horizontal
notes:         <one line>
confidence:    HIGH | MEDIUM | LOW
```
