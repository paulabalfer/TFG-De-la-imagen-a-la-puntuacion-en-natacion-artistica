# BP17 — Knight Scorer v2

## CRITICAL WARNING
Knight is SEVERELY UNDER-DETECTED. In testing, only 11 out of 63 Knight images were correctly classified (17.5% recall). The dominant error:
- **42 Knight images were called Fishtail** (arch not detected → treated as straight trunk with split legs)
- 10 Knight images were called DLV (both split and arch missed)

**RULE: If there is ANY possibility of a back arch AND the legs are split and straight, it is likely Knight, NOT Fishtail.**

## Position Description
Swimmer inverted with an ARCHED back, one leg pointing up and the other extending straight BACKWARD (toward the spine/back). Both legs are STRAIGHT. The body forms an "inverted arabesque" shape. The arch is the KEY feature distinguishing Knight from Fishtail.

## 6-Step Scratchpad

### S1: Are there TWO legs in DIFFERENT directions? (REQUIRED)
- One leg up, one extending outward
- If both legs together → NOT Knight (→ DLV)

### S2: Is the back ARCHED? (CRITICAL — THE KEY FEATURE)
This is THE feature that makes it Knight instead of Fishtail. Apply ALL 5 arch sub-tests:

1. **Trunk line test:** Draw a line from hips to shoulders. Does it CURVE? Even slightly? → ARCHED
2. **Alignment test:** Are hips and shoulders NOT vertically aligned? Hips pushed forward? → ARCHED
3. **Entry point test:** Does the trunk enter the water at an ANGLE rather than straight down? → ARCHED
4. **Spine curvature test:** Is there ANY visible curvature in the spine/back area? → ARCHED
5. **Body shape test:** Does the body form a crescent, bow, banana, or arabesque shape? → ARCHED

**SCORING: If ANY ONE of these 5 tests is positive → the back IS arched → likely Knight.**

**CRITICAL: In underwater photography, arches are EASY TO MISS due to water distortion, refraction, and angle. Be GENEROUS in detecting arches. The most common error is failing to see a real arch.**

### S3: Are BOTH legs STRAIGHT? (REQUIRED)
- No knee bend on either leg
- If either knee is bent → NOT Knight (→ BKSA)

### S4: Does the horizontal leg extend BACKWARD?
- Toward the back/spine side of the swimmer
- The arch naturally makes the leg go backward
- If the back is arched, the horizontal leg is almost certainly backward

### S5: "Inverted arabesque" silhouette?
- The overall body should look like a ballet arabesque, but upside down
- Curved, graceful, with legs split and back arched

### S6: Kneecap direction check
- If horizontal leg's kneecap faces DOWN → Knight
- If horizontal leg's kneecap faces UP → Fishtail

## Hard Exclusions (any YES → score 0)
- E1: Trunk is DEMONSTRABLY straight with ZERO curvature in ALL 5 sub-tests (all 5 must be negative to exclude)
- E2: Either knee is bent (→ BKSA)
- E3: Both legs together same direction (→ DLV)

**NOTE: E1 requires ALL 5 arch tests to be negative. If even ONE is positive, do NOT trigger E1.**

## Scoring Rubric (GENEROUS — to counteract severe under-detection)
| Score | Criteria |
|-------|----------|
| 5 | Clear arch + split straight legs + backward horizontal leg. Textbook Knight. |
| 4 | Arch visible (2+ sub-tests positive) + split straight legs. |
| 3 | Likely arch (1-2 sub-tests positive) + split straight legs. |
| 2 | POSSIBLE arch (1 sub-test positive or uncertain) + split straight legs. |
| 1 | Very slight suggestion of arch, legs are split and straight. |
| 0 | ALL 5 arch tests negative (demonstrably straight trunk) OR knee is bent OR legs together. |

**KEY: Score 2+ if you CANNOT positively confirm the trunk is perfectly straight. The burden of proof is on STRAIGHTNESS, not on arch detection.**

## Contrastive Learning

### Knight vs Fishtail (42 errors — THE BIGGEST confusion pair)
| Feature | Knight | Fishtail |
|---------|--------|----------|
| Back | ARCHED (curved) | STRAIGHT (no curve) |
| Horizontal leg | BACKWARD (spine side) | FORWARD (face side) |
| Body shape | Arabesque/crescent | Angular T/L |
| Trunk under water | Curves backward | Goes straight down |
| Kneecap direction | DOWN | UP |

**DECISIVE TEST: Is the trunk perfectly straight? If NO (any curvature) → Knight. If YES (demonstrably straight) → Fishtail.**

### Knight vs DLV (10 errors)
| Feature | Knight | DLV |
|---------|--------|-----|
| Legs | SPLIT, two directions | TOGETHER, one unit |
| Back | ARCHED | STRAIGHT |
| Shape | Arabesque | Pencil/stick |

### Knight vs BKSA (both have arched backs)
| Feature | Knight | BKSA |
|---------|--------|------|
| Legs | Both STRAIGHT | One BENT at knee |
| Shape | Arabesque | Curved with triangle |
| Knee | No bend | Visible bend |

## Training Examples

### Correct Knight:
1. "One leg up, other leg extending backward. The trunk has a clear backward curve — arch is visible. Both legs are straight. Classic arabesque shape inverted."
2. "Split legs, both straight. The back shows curvature — hips are pushed slightly forward of the shoulders. Trunk enters water at an angle, not straight down. This is Knight."
3. "Subtle arch case: The trunk is NOT perfectly straight — there's a slight curvature. The body forms a very subtle crescent shape. Legs are split and both straight. Even this subtle arch means Knight, NOT Fishtail."
4. "Very similar to Fishtail at first glance, but looking carefully: the spine has a slight curve, the hips and shoulders are not perfectly aligned. This arch, even though subtle, makes it Knight."

### NOT Knight:
1. "Split legs, both straight, but the trunk goes PERFECTLY straight down with zero curvature. ALL 5 arch tests negative." → Fishtail
2. "Back is arched but one knee is bent" → BKSA
3. "Both legs together pointing same direction" → DLV

## Output
Score: [0-5]
Exclusions triggered: [list or "none"]
Confidence: [HIGH/MEDIUM/LOW]
