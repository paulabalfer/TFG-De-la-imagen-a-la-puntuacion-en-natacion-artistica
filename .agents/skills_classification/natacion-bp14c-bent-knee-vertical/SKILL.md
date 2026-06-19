# BP14c — Bent Knee Vertical (BKV) Scorer v2

## CRITICAL WARNING
BKV is the MOST UNDER-DETECTED class. In testing, BKV had only 7.7% recall — 48 out of 52 BKV images were misclassified. The primary errors:
- 26 BKV images were called DLV (knee bend not detected)
- 12 BKV images were called Fishtail (knee bend missed, treated as straight leg)
- 10 BKV images were called Knight (knee bend missed + false arch)

**RULE: If there is ANY possibility of a knee bend, it is likely BKV, not DLV or Fishtail. Even SUBTLE bends (10-15°) count as BKV.**

## Position Description
Swimmer inverted with one leg straight up and the other leg BENT at the knee. The bent leg creates a "4", triangle, or flag shape. The thigh of the bent leg goes outward (roughly horizontal), and the shin folds back. The trunk is STRAIGHT (no arch).

## 7-Step Scratchpad

### S1: Is one leg vertical? (straight up)
- Standard for most positions — confirm presence

### S2: Does the second leg show ANY bend at the knee? (CRITICAL — THE KEY FEATURE)
Apply ALL 4 knee bend sub-tests:
1. **Angle test:** Is there ANY angle at the knee, even 10-15°? → BENT
2. **Shin-thigh test:** Do shin and thigh form DIFFERENT lines? → BENT
3. **Foot position test:** Is the foot near the opposite knee/thigh instead of extended? → BENT
4. **Triangle test:** Does the leg create a triangle, "4", or flag shape? → BENT

**If ANY sub-test is positive → the knee IS bent → BKV is likely.**

### S3: Is the bent leg's thigh approximately horizontal?
- Thigh should be roughly parallel to water surface
- Doesn't need to be perfect — approximately horizontal counts

### S4: Does the shin fold upward/inward from the knee?
- The lower leg (shin) should angle back toward the vertical leg
- Creates the characteristic triangle or "4" shape

### S5: Is the trunk STRAIGHT? (REQUIRED — no arch)
- If trunk is arched → NOT BKV → consider BKSA
- BKV has a straight, linear trunk

### S6: "4" or flag or triangle silhouette?
- The overall shape should resemble the number 4 or a flag

### S7: Swimmer is inverted?
- Standard for these positions

## Hard Exclusions (any YES → score 0)
- E1: Both legs are DEMONSTRABLY perfectly straight lines from hip to toe — no angle at the knee whatsoever. **Note: "I can't clearly see a bend" is NOT enough to trigger this exclusion. Only trigger if you can POSITIVELY confirm straightness.**
- E2: Back is clearly arched (→ BKSA)
- E3: Both legs together same direction (→ DLV)

## Scoring Rubric (GENEROUS — to counteract under-detection)
| Score | Criteria |
|-------|----------|
| 5 | Clear "4" shape, obvious knee bend, straight trunk |
| 4 | Visible knee bend, thigh roughly horizontal, trunk straight |
| 3 | Likely knee bend visible, trunk appears straight |
| 2 | POSSIBLE knee bend — cannot confirm leg is perfectly straight |
| 1 | Slight suggestion of a bend, very uncertain |
| 0 | Both legs are DEMONSTRABLY straight (positively confirmed) OR back is arched |

**KEY: Score 2+ if you CANNOT positively confirm the second leg is perfectly straight. The burden of proof is on STRAIGHTNESS, not on bend.**

## Contrastive Learning

### BKV vs DLV (26 errors — BIGGEST confusion pair for BKV)
| Feature | BKV | DLV |
|---------|-----|-----|
| Legs | SPLIT — one up, one bent outward | TOGETHER — both up as one unit |
| Knee | BENT (even slightly) | Both perfectly STRAIGHT |
| Shape | "4" or triangle | Pencil/stick |
| Second leg | Goes in different direction from first | Same direction as first |

**If you're about to classify as DLV, STOP and ask: "Is the second leg DEMONSTRABLY straight? Or could there be a bend?" If uncertain → BKV.**

### BKV vs Fishtail (12 errors)
| Feature | BKV | Fishtail |
|---------|-----|----------|
| Second leg | BENT at knee | STRAIGHT, extended |
| Shape | "4" or triangle | T or L shape |
| Knee | Angle visible | No angle |
| Foot | Near opposite knee | Extended away |

### BKV vs BKSA
| Feature | BKV | BKSA |
|---------|-----|------|
| Trunk | STRAIGHT | ARCHED |
| Depth | Can be deeply inverted | Near water surface |
| Thigh direction | Horizontal | Often more downward |

## Training Examples

### Correct BKV:
1. "One leg straight up, second leg bends at the knee — thigh goes outward, shin folds back creating a clear '4' shape. Trunk is straight, no curvature."
2. "Inverted swimmer, vertical leg up. The other leg shows a definite angle at the knee — the leg changes direction at that joint. Trunk goes straight down."
3. "Subtle case: One leg vertical, the other leg has a slight bend — maybe 20° at the knee. The foot is closer to the other knee than it would be if the leg were straight. Trunk straight. This IS BKV even though the bend is subtle."
4. "Very subtle: Second leg mostly extended but with a noticeable angle change at the knee joint. Not a straight line from hip to toe. This qualifies as BKV."

### NOT BKV:
1. "Both legs clearly form straight lines from hip to toe, no angle at any knee" → DLV or Fishtail
2. "Knee is bent but the back is arched" → BKSA
3. "Both legs together pointing same direction" → DLV

## Output
Score: [0-5]
Exclusions triggered: [list or "none"]
Confidence: [HIGH/MEDIUM/LOW]
