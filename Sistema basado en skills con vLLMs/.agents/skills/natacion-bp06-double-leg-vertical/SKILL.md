# BP6 — Double Leg Vertical (DLV) Scorer v2

## CRITICAL WARNING
DLV is the MOST OVER-PREDICTED class. In testing, DLV had 92% recall but only 46% precision — meaning over half of DLV predictions were WRONG. The model defaults to DLV when it cannot clearly identify features.

**RULE: DLV requires OVERWHELMING positive evidence. If there is ANY doubt, it is NOT DLV.**

## Position Description
Both legs pressed tightly together pointing straight up. Body forms a single straight vertical line. No separation, no bend, no arch. Like a pencil standing on its point.

## 5-Step Scratchpad

### S1: Are BOTH legs visible as a SINGLE unit? (CRITICAL)
- Both legs must be pressed together with NO gap
- If you see two separate legs going in different directions → NOT DLV (score 0)
- If there is ANY separation between the legs → NOT DLV (score 0)

### S2: Are both legs fully STRAIGHT?
- No knee bend whatsoever (even slight)
- If either knee shows any angle → NOT DLV (score 0, consider BKV)

### S3: Do legs point straight UP?
- Perpendicular to the water surface
- Not angled to the side

### S4: Is the trunk STRAIGHT?
- No arch or curvature in the back
- Body forms one continuous straight line
- If arched → NOT DLV

### S5: Anti-DLV verification
- Can you POSITIVELY confirm both legs are together? (not just "I can't see a split")
- Is there truly NO second leg extending in another direction?
- Remember: the absence of visible features ≠ DLV

## Hard Exclusions (any YES → score 0)
- E1: A second leg extends in a DIFFERENT direction
- E2: Either knee is bent (even slightly)
- E3: Back is arched or curved
- E4: Legs are separated with a visible gap

## Scoring Rubric
| Score | Criteria |
|-------|----------|
| 5 | Both legs CLEARLY together, straight, vertical. No doubt whatsoever. |
| 4 | Legs appear together and straight, minor water distortion. |
| 3 | Probably together but image quality makes it slightly uncertain. |
| 2 | Might be together but could also be a subtle split. |
| 1 | Unclear — could be DLV or something else. DO NOT default here. |
| 0 | Any exclusion triggered, or legs clearly split/bent/arched. |

## Contrastive Learning

### DLV vs Fishtail
| Feature | DLV | Fishtail |
|---------|-----|----------|
| Legs | Together, one unit | Split, two directions |
| Gap | No gap | Visible separation |
| Shape | Pencil/stick | T or L shape |

### DLV vs BKV
| Feature | DLV | BKV |
|---------|-----|-----|
| Knees | Both perfectly straight | One knee bent |
| Shape | Straight line | "4" or triangle |
| Legs | Together | Split (bent leg goes different direction) |

## Training Examples

### Correct DLV:
1. "Single straight vertical line. Both feet at the top, pressed together. No gap between legs. Trunk goes straight down."
2. "Pencil-like shape. Both legs form one unit pointing up. No curvature anywhere."

### NOT DLV (commonly misclassified as DLV):
1. "Legs look close together but there's a slight gap and one leg angles slightly outward" → Fishtail or BKV
2. "One leg is straight up but the other has a subtle bend at the knee" → BKV
3. "Legs seem together but the trunk curves backward" → Check for Knight/BKSA

## Output
Score: [0-5]
Exclusions triggered: [list or "none"]
Confidence: [HIGH/MEDIUM/LOW]
