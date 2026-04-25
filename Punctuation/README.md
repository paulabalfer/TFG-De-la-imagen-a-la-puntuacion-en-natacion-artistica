# Punctuation — Sistema de puntuación de posiciones básicas de natación artística

Este directorio implementa un **sistema de puntuación** (no de clasificación) para las 5 posiciones básicas de natación artística, siguiendo el mismo patrón que el directorio hermano `vLLM con skills de anthropic/`: **Claude Sonnet como modelo de visión**, sin entrenamiento, con el conocimiento experto codificado como *skills* de Claude Code.

A diferencia del clasificador, el **sistema ya sabe a priori qué posición contiene la imagen** (lo indica el usuario). Su trabajo es emitir una puntuación 0–10 siguiendo la metodología oficial de World Aquatics:

```
final_score = max(0, height_score − Σ deducciones)
```

donde `height_score` es la lectura en la **carta de alturas** propia de la posición (marcas 3.5 → 10) y las deducciones penalizan desviaciones del eje vertical, rodillas/tobillos no estirados, línea del cuerpo y pierna partner.

---

## Contenido

```
Punctuation/
├── README.md                              # Este fichero
├── .claude/
│   └── skills/
│       ├── scoring-orchestrator/          # Orquestador — entrada del sistema
│       ├── scoring-common-deductions/     # Catálogo central de deducciones (D1..D5)
│       ├── scoring-bp06-double-leg-vertical/
│       ├── scoring-bp08-fishtail/
│       ├── scoring-bp14c-bent-knee-vertical/
│       ├── scoring-bp14d-bent-knee-surface-arch/
│       └── scoring-bp17-knight/
├── references/                            # Cartas oficiales de alturas
│   ├── Fishtail_punctuation.png
│   ├── Bent_knee_vertical_punctuation.png
│   ├── Knight_punctuation.png
│   ├── Double_leg_vertical_punctuation.png
│   ├── Bent_knee_surface_arch_punctuation.png
│   └── Deductions.png
├── scripts/
│   ├── score_image.py                     # Entry point para una imagen
│   └── score_batch.py                     # Iteración sobre Data/Images
├── data/                                  # (Ground truth y splits aquí)
└── results/                               # predictions.json, reports
```

---

## Las 5 posiciones y sus cartas

| # | Posición                        | Código | Carta de alturas                               | Rango   |
|---|---------------------------------|--------|------------------------------------------------|---------|
| 1 | Double Leg Vertical             | BP6    | `Double_leg_vertical_punctuation.png`          | 3.5–10  |
| 2 | Fishtail                        | BP8    | `Fishtail_punctuation.png`                     | 3.5–10  |
| 3 | Bent Knee Vertical              | BP14c  | `Bent_knee_vertical_punctuation.png`           | 3.5–10  |
| 4 | Bent Knee Surface Arch Position | BP14d  | `Bent_knee_surface_arch_punctuation.png`       | 5.0–10  |
| 5 | Knight                          | BP17   | `Knight_punctuation.png`                       | 3.5–10  |

Cada carta marca 7–8 niveles (3.5, 4.5, 5.5, 6.5, 7.5, 8.5, 9.5, 10) sobre la **pierna vertical** de la figura. El **height_score** es el valor de la marca donde el agua cruza la pierna. Para BP14d la referencia es el **muslo vertical** de la pierna flexionada (por eso su rango empieza en 5).

---

## Catálogo de deducciones (resumido)

Definido en detalle en `scoring-common-deductions/SKILL.md`.

| ID  | Concepto                               | Escala                                      |
|-----|----------------------------------------|---------------------------------------------|
| D1  | Desviación del eje de la pierna vertical | 0° → 0 · 1–15° → −0.2 · 15–30° → −0.5 · >30° → −1.0 |
| D2  | Extensión de rodilla (pierna de referencia) | 180° → 0 · ... · <120° → −1.0             |
| D3  | Extensión del pie (por pie visible)    | pointed → 0 · ... · hooked → −0.3           |
| D4  | Línea del tronco (solo posiciones rectas) | recto → 0 · ... · flexión marcada → −0.6 |
| D5  | Pierna partner (en posiciones con split) | usa la misma escala que D1              |

D1 refleja exactamente la carta oficial de deducciones (`references/Deductions.png`).

---

## Flujo de una puntuación

```
usuario → (imagen + "esto es un Fishtail")
                ↓
    scoring-orchestrator
                ↓
    scoring-bp08-fishtail    ←→ references/Fishtail_punctuation.png
                ↓
        {height_score, observations}
                ↓
    scoring-common-deductions
                ↓
        {D1..D5, total}
                ↓
    final_score = max(0, height_score − total)
```

---

## Uso

### 1. Desde Claude Code / Cowork

Con la imagen adjunta y el nombre de la posición:

```
>> Use the `scoring-orchestrator` skill to score this image as a Fishtail.
```

El orquestador invoca la skill específica (`scoring-bp08-fishtail`), aplica la carta de alturas, llama a `scoring-common-deductions`, y devuelve el informe final.

### 2. Desde la línea de comandos

Generar el prompt canónico para una imagen:

```
python scripts/score_image.py ../Data/Images/Fishtail/001.jpg Fishtail
```

Para procesar toda la carpeta `Data/Images/`:

```
python scripts/score_batch.py ../Data/Images
```

---

## Formato de salida

```
=== ARTISTIC SWIMMING POSITION SCORE ===

IMAGE:      001.jpg
POSITION:   Fishtail (BP8)

--- HEIGHT READING ---
Height chart:    references/Fishtail_punctuation.png
Water line on:   upper thigh of the vertical leg
Height score:    8.5

--- OBSERVATIONS ---
Leg axis:        1–15° tilt forward   → vertical leg leans slightly over the face
Knee extension:  locked               → both knees straight
Foot extension:  slightly relaxed     → pointed but not maximal on one foot
Body line:       straight             → expected
Partner leg:     1–15° below horizontal → horizontal leg sags just below surface

--- DEDUCTIONS ---
D1 leg axis            -0.2
D2 knee extension       0.0
D3 foot extension      -0.1
D4 body line            0.0
D5 partner leg         -0.2
total                  -0.5

--- FINAL ---
Final score:     8.0
Confidence:      HIGH
Notes:           Clear Fishtail with minor forward tilt and a small sag in the horizontal leg.
```

---

## Primera versión — alcance y limitaciones

Esta es la **v1** del sistema:

- Funciona con **una imagen estática** (no vídeo).
- **Asume** la posición. No intenta re-clasificar; si las observaciones contradicen la posición declarada, devuelve `MISMATCH`.
- La estimación de ángulos es **heurística** (bandas), no medida exacta por keypoints. Si en el futuro se quiere precisión, el siguiente paso es integrar un detector de pose (MediaPipe, OpenPose) y reemplazar las bandas por ángulos calculados.
- La lectura de la altura se hace por comparación visual contra la carta; es lo más sensible a la calidad de la foto (encuadre lateral claro).

### Siguientes pasos razonables

1. **Ground truth**: generar `data/ground_truth_scores.json` con la puntuación que daría un juez para cada imagen de `Data/Images/`.
2. **Evaluación**: añadir `scripts/compute_score_error.py` que compare predicciones vs ground truth con MAE / exact-match dentro de ±0.5.
3. **Integración de pose**: opcional — un preproceso que extraiga keypoints y los inyecte en el prompt, convirtiendo D1 en un ángulo exacto.
4. **Regla de consistencia**: si la pierna vertical medida está fuera de vertical > 30°, re-verificar si el usuario acertó con la posición (muchas ejecuciones colapsadas parecen otra posición).

---

## Modelo y herramientas

- **Modelo**: Claude Sonnet 4.5 con visión multimodal.
- **Invocación**: skills de Claude Code cargadas desde `.claude/skills/`.
- **Cartas de referencia**: copiadas desde `Data/references/punctuation/` para que el orquestador pueda abrirlas con la tool `Read` sin dependencia cruzada entre carpetas.
