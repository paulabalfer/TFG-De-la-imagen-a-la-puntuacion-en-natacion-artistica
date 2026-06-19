# BP14d — Bent Knee Surface Arch (BKSA) Scorer v2

## STATUS: EXCELLENT PERFORMANCE
BKSA achieved 100% accuracy (39/39 correct) in testing. This scorer works well. Minor enhancements added for completeness.

## Position Description
Swimmer with an ARCHED back (curved backward like a bow) and one knee BENT. Body is often near the water surface rather than deeply inverted. Overall posture is reclined/curved. Both arch AND bent knee are required.

## 5-Step Scratchpad

### S1: Is the back ARCHED? (REQUIRED)
- Spine curves backward, forming a bow or crescent
- Apply the 5 arch sub-tests:
  1. Trunk line curves?
  2. Hips/shoulders misaligned?
  3. Trunk enters water at angle?
  4. Spine curvature visible?
  5. Crescent/bow body shape?
- If trunk is straight → NOT BKSA (→ BKV)

### S2: Is the body near the water surface?
- BKSA swimmers are often NOT deeply inverted
- Body closer to surface than other positions
- Reclined posture rather than fully inverted

### S3: Is one knee BENT? (REQUIRED)
- At least one leg must show a bend at the knee
- If both legs are straight → NOT BKSA (→ Knight)

### S4: Does the bent thigh point downward?
- Thigh roughly perpendicular to water surface
- (In contrast to BKV where thigh is more horizontal)

### S5: Overall reclined/arched posture?
- The whole body suggests a curved, surface-level position
- Not a deeply inverted vertical position

## Hard Exclusions (any YES → score 0)
- E1: Trunk is clearly STRAIGHT (no arch) → consider BKV
- E2: Both legs completely straight (no knee bend) → consider Knight
- E3: Both legs together same direction → consider DLV

## Scoring Rubric
| Score | Criteria |
|-------|----------|
| 5 | Clear arch + clear bent knee + near surface. Textbook BKSA. |
| 4 | Arch and bent knee both visible, surface position. |
| 3 | Likely arch and bent knee, somewhat near surface. |
| 2 | Arch or bent knee present but other feature uncertain. |
| 1 | Possible but very unclear. |
| 0 | Any exclusion triggered. |

## Contrastive Learning

### BKSA vs BKV (key distinction)
| Feature | BKSA | BKV |
|---------|------|-----|
| Back | ARCHED | STRAIGHT |
| Depth | Near surface | Can be deeply inverted |
| Thigh | Often more downward | Often more horizontal |
| Posture | Reclined, curved | Inverted, angular |

### BKSA vs Knight (both have arched backs)
| Feature | BKSA | Knight |
|---------|------|--------|
| Knee | BENT | Both legs STRAIGHT |
| Shape | Curved with triangle | Curved arabesque |
| Legs | One bent, one may vary | Both straight, split |

## Training Examples

### Correct BKSA:
1. "Back clearly arched in a bow shape. One knee bent with thigh pointing down. Body near the water surface, not deeply inverted. Reclined posture."
2. "Curved spine, crescent body shape. Visible knee bend. Swimmer is at surface level, arched backward."

### NOT BKSA:
1. "Knee bent but back is perfectly straight" → BKV
2. "Back arched but both legs are straight" → Knight

## Output
Score: [0-5]
Exclusions triggered: [list or "none"]
Confidence: [HIGH/MEDIUM/LOW]
