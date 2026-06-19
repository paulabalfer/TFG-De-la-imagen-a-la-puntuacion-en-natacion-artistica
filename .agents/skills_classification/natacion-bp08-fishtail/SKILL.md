# BP8 — Fishtail Scorer v2

## CRITICAL WARNING
Fishtail is often confused with Knight (16 errors where Fishtail was called Knight) and with DLV (17 errors where Fishtail was called DLV). The key distinguishing features:
- vs Knight: Fishtail has a STRAIGHT trunk (NO arch). Knight has an ARCHED back.
- vs DLV: Fishtail has SPLIT legs. DLV has legs TOGETHER.

**RULE: Fishtail requires: split legs + BOTH straight + NO arch + horizontal leg FORWARD.**

## Position Description
Swimmer inverted with one leg straight up and another leg extending straight FORWARD (toward face/chest). Both legs are completely straight. Trunk is STRAIGHT with no arch. Forms a T or L shape.

## 6-Step Scratchpad

### S1: Are the legs SPLIT? (REQUIRED)
- Two legs going in different directions
- If legs are together → NOT Fishtail (→ DLV)

### S2: Are BOTH legs completely STRAIGHT? (REQUIRED)
- No knee bend on either leg
- If either knee is bent → NOT Fishtail (→ BKV or BKSA)

### S3: Is the trunk STRAIGHT with NO arch? (REQUIRED)
- The trunk must be linear, no backward curvature
- **THIS IS THE KEY TEST vs Knight**
- Apply all 5 arch sub-tests from the orchestrator
- If ANY arch is detected → NOT Fishtail (→ Knight)

### S4: Does the horizontal leg extend FORWARD?
- Toward the face/chest side of the swimmer
- If backward (toward spine) → NOT Fishtail (→ Knight)

### S5: Is one leg vertical?
- Pointing straight up, perpendicular to water

### S6: T-shape or L-shape silhouette?
- The overall body should form a clean angular shape

## Hard Exclusions (any YES → score 0)
- E1: Back is arched or curved (→ Knight)
- E2: Either knee is bent (→ BKV or BKSA)
- E3: Both legs together same direction (→ DLV)
- E4: Horizontal leg extends BACKWARD (→ Knight)

## Scoring Rubric
| Score | Criteria |
|-------|----------|
| 5 | Clear T/L shape, both legs straight, trunk straight, forward horizontal leg |
| 4 | Good split, both straight, trunk straight, direction somewhat clear |
| 3 | Split legs visible, both seem straight, trunk appears straight |
| 2 | Split visible but direction or straightness uncertain |
| 1 | Might have features but very unclear |
| 0 | Any exclusion triggered |

## Contrastive Learning

### Fishtail vs Knight (THE CRITICAL DISTINCTION)
| Feature | Fishtail | Knight |
|---------|----------|--------|
| Trunk | STRAIGHT, no curvature | ARCHED, curved backward |
| Horizontal leg | FORWARD (face side) | BACKWARD (spine side) |
| Body shape | Angular T/L | Curved arabesque |
| Kneecap of horizontal leg | Faces UP | Faces DOWN |

### Fishtail vs BKV
| Feature | Fishtail | BKV |
|---------|----------|-----|
| Second leg | STRAIGHT, extended | BENT at knee |
| Shape | T/L shape | "4" or triangle |
| Knee | No bend | Visible bend |

### Fishtail vs DLV
| Feature | Fishtail | DLV |
|---------|----------|-----|
| Legs | SPLIT, two directions | TOGETHER, one unit |
| Shape | T/L shape | Pencil/stick |
| Second leg | Extended outward | No second leg direction |

## Training Examples

### Correct Fishtail:
1. "One leg vertical, other leg horizontal toward the face. Both legs completely straight. Trunk goes straight down — no curvature. Clean T-shape."
2. "L-shaped silhouette. Vertical leg up, horizontal leg forward at roughly 90°. Back is perfectly straight."

### NOT Fishtail:
1. "Looks like Fishtail but the trunk has a slight backward curve" → Knight
2. "Split legs but one has a bend at the knee" → BKV
3. "Both legs appear to go in the same direction" → DLV

## Output
Score: [0-5]
Exclusions triggered: [list or "none"]
Confidence: [HIGH/MEDIUM/LOW]
