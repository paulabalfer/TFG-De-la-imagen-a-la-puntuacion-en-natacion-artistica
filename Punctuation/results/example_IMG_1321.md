# Example run — IMG_1321.JPG (Fishtail)

Trace of the `scoring-orchestrator` skill applied to `Data/Images/Fishtail/IMG_1321.JPG`, with the user declaring the position as **Fishtail (BP8)**. This is a worked example used to sanity-check the v1 system.

---

## Step 1 — Dispatch

Orchestrator loads `scoring-bp08-fishtail`.

## Step 2 — Height reading (scorer)

Opens `references/Fishtail_punctuation.png` and inspects the photo:

- Vertical leg clearly identifiable on the right side of the frame (ankle high, thigh entering water).
- Horizontal leg visible extending forward (toward the face/chest side), mostly under the water.
- Water line crosses the **vertical leg at mid-thigh**.
- Mapping to the chart → mark **7.5**.

## Step 3 — Observations

- **Leg axis (D1)**: vertical leg tilts slightly forward, ~8° → band "1–15° tilt forward".
- **Knee extension (D2)**: vertical-leg knee locked; horizontal leg appears straight → "locked".
- **Foot extension (D3)**: visible foot (vertical leg) well pointed → "pointed". Horizontal-leg foot under water, cannot evaluate → default to 0 with a confidence note.
- **Body line (D4)**: trunk submerged, straight as far as visible → "straight".
- **Partner leg (D5)**: horizontal leg sits slightly **below** the water surface (~10° sag) → band "1–15°".

## Step 4 — Apply `scoring-common-deductions`

```
D1 leg axis           -0.2   (8° forward tilt → 1–15° band)
D2 knee extension      0.0   (locked)
D3 foot extension      0.0   (pointed, water hides second foot)
D4 body line           0.0   (straight, as expected)
D5 partner leg        -0.2   (horizontal leg sagging ~10° below surface)
─────────────────────────────
total                 -0.4
```

## Step 5 — Final

```
final_score = max(0, 7.5 − 0.4) = 7.1
```

---

## Orchestrator output

```
=== ARTISTIC SWIMMING POSITION SCORE ===

IMAGE:      IMG_1321.JPG
POSITION:   Fishtail (BP8)

--- HEIGHT READING ---
Height chart:    references/Fishtail_punctuation.png
Water line on:   mid-thigh of the vertical leg
Height score:    7.5

--- OBSERVATIONS ---
Leg axis:        1–15° tilt forward     → vertical leg leans ~8° over the face
Knee extension:  locked                  → both knees straight
Foot extension:  pointed                 → visible foot well extended; second foot under water
Body line:       straight                → trunk submerged, no visible curvature
Partner leg:     1–15° below horizontal  → horizontal leg sags ~10° below surface

--- DEDUCTIONS ---
D1 leg axis            -0.2
D2 knee extension       0.0
D3 foot extension       0.0
D4 body line            0.0
D5 partner leg         -0.2
total                  -0.4

--- FINAL ---
Final score:     7.1
Confidence:      MEDIUM
Notes:           Horizontal leg is partly under water, which makes its exact angle
                 uncertain; re-score from a second frame for HIGH confidence.
```

---

## What this example validates

- The orchestrator correctly dispatches to the BP8 scorer.
- The BP8 scorer reads its own height chart (mid-thigh → 7.5).
- The `scoring-common-deductions` scale maps observations to deductions (−0.2 and −0.2).
- Final score is clamped to one decimal in [0.0, 10.0].
- `MISMATCH` logic is not triggered (no bent knee, no arch).
- Confidence drops to MEDIUM because the horizontal leg is under water.
