# Puntuación — Sistema de puntuación de posiciones de natación artística

Directorio que implementa la **puntuación automática** de las 5 posiciones básicas de natación artística mediante **Claude Sonnet como modelo de visión**, sin entrenamiento, con el conocimiento experto codificado como *skills*. A diferencia del módulo de clasificación, este sistema **asume que la posición ya es conocida** — su único trabajo es emitir una puntuación 0–10 siguiendo la metodología oficial de World Aquatics:

```
final_score = max(0, height_score − Σ deducciones)
```

donde `height_score` se lee en la carta de alturas propia de cada posición y las deducciones penalizan desviaciones del eje vertical, rodillas/tobillos no estirados, línea del cuerpo y pierna partner. Cada carta marca 7–8 niveles sobre la pierna de referencia. El `height_score` es el valor de la marca donde el agua cruza esa pierna.

---

## Contenido

Las skills residen en el directorio externo compartido de la raíz del repositorio: `.agents/skills_punctuation/`.

```
Puntuación/
├── README.md
├── scripts/
│   ├── score_image.py                                       # Genera el prompt canónico para una imagen individual
│   ├── score_batch.py                                       # Genera prompts en lote desde un Excel de entrada
│   └── evaluate_scores.py                                   # Compara predicciones del modelo con puntuaciones del juez
├── data/
│   ├── subset_puntuation.xlsx                               # Lista de imágenes a puntuar (POSITION, IMAGE)
│   ├── subset_puntuation_juez1.xlsx                         # Ground truth — puntuaciones reales del juez
│   └── prompts_generated.txt                                # Prompts generados por score_batch.py
└── results/
    ├── subset_puntuation_generated.xlsx                     # Puntuaciones emitidas por el modelo
    ├── score_evaluation.json                                # Métricas de evaluación (JSON estructurado)
    └── score_report.html                                    # Informe visual interactivo
```

---

## Skills del sistema

### scoring-orchestrator

Punto de entrada único. Recibe la imagen y el nombre/código de la posición, y coordina el pipeline completo: delega en el scorer de posición, aplica las deducciones comunes y devuelve el informe final. Nunca clasifica la posición — si lo que ve en la imagen no coincide con la posición declarada, devuelve `MISMATCH`.

### scoring-common-deductions

Módulo centralizado con el catálogo completo de deducciones D1–D5, derivado de la carta oficial de World Aquatics (`references/Deductions.png`). Cualquier cambio en las reglas de deducción se hace aquí y se propaga a todos los scorers.

| ID  | Concepto                                         | Escala                                                     |
|-----|--------------------------------------------------|------------------------------------------------------------|
| D1  | Desviación del eje de la pierna vertical         | 0° → 0 / 1–15° → −0.2 / 15–30° → −0.5 / >30° → −1.0      |
| D2  | Extensión de rodilla (pierna de referencia)      | 180° → 0 / 170° → −0.1 / 150° → −0.3 / 120° → −0.6 / <120° → −1.0 |
| D3  | Extensión del pie (por pie visible)              | pointed → 0 / relajado → −0.1 / cocked → −0.2 / flat → −0.3 |
| D4  | Línea del tronco (solo posiciones rectas)        | recto → 0 / leve → −0.1 / moderado → −0.3 / pronunciado → −0.6 |
| D5  | Pierna partner (posiciones con split: BP8, BP14c, BP14d, BP17) | misma escala que D1 |

En las posiciones con arco (BP14d, BP17), el arco es la forma esperada y **no se penaliza**; en cambio, su ausencia se penaliza bajo D4.

### Scorers por posición

Cada skill (`scoring-bp06-*`, `scoring-bp08-*`, etc.) encapsula:
- La lectura de la carta de alturas específica de la posición.
- Las reglas de observación particulares (p.ej. en BP14c el arco penaliza; en BP17, su ausencia).
- Los disqualifiers que generan `MISMATCH` hacia el orquestador.

---

## Pipeline

```
usuario → imagen + nombre de posición
                    │
                    ▼
        (1) scoring-orchestrator
                    │
                    ▼
        (2) scorer de posición específico
                    │   · lee su carta de alturas
                    │   · emite { height_score, observations }
                    ▼
        (3) scoring-common-deductions
                    │   · mapea observations → D1..D5
                    │   · emite tabla de deducciones + total
                    ▼
        (4) Agregación final
                    │   final_score = max(0, height_score − total)
                    │   redondeo a 1 decimal
                    ▼
                informe
```

El orquestador imprime el desglose completo de cada línea para que un juez humano pueda auditar cada decisión:

```
=== ARTISTIC SWIMMING POSITION SCORE ===

IMAGE:      IMG_1364.JPG
POSITION:   Knight (BP17)

--- HEIGHT READING ---
Height chart:    references/Knight_punctuation.png
Water line on:   just below the hip of the vertical leg
Height score:    9.5

--- OBSERVATIONS ---
Leg axis:        1–15° backward tilt   → arch pulls the top of the leg slightly back
Knee extension:  locked                → both legs straight
Foot extension:  pointed               → both feet well extended
Body line:       arched (expected)     → pronounced arch present, not penalised
Partner leg:     1–15° below horizontal → slight sag in the backward leg

--- DEDUCTIONS ---
D1 leg axis           -0.2
D2 knee extension      0.0
D3 foot extension      0.0
D4 body line           0.0
D5 partner leg        -0.2
total                 -0.4

--- FINAL ---
Final score:     9.1
Confidence:      HIGH
Notes:           Clean Knight with minimal deductions; the arch is well-defined.
```

---

## Scripts

### score_image.py — Imagen individual

Genera el prompt canónico para enviar a Claude con una imagen y una posición conocida. La lógica de puntuación reside en los skills; este script es solo un driver de entrada.

```bash
python scripts/score_image.py <ruta/a/imagen.jpg> Fishtail
python scripts/score_image.py <ruta/a/imagen.jpg> BP17
```

Acepta tanto el nombre completo de la posición como el código BP.

---

### score_batch.py — Procesamiento en lote

Lee `data/subset_puntuation.xlsx` (columnas `POSITION`, `IMAGE`) y genera un prompt por entrada en `data/prompts_generated.txt`, separados por `---`. Permite procesar el subset completo de imágenes sin construir cada mensaje manualmente.

```bash
python scripts/score_batch.py
python scripts/score_batch.py --limit 10          # solo las primeras 10
python scripts/score_batch.py --input data/otro.xlsx --output data/mis_prompts.txt
```

| Argumento        | Descripción                                           | Por defecto                              |
|------------------|-------------------------------------------------------|------------------------------------------|
| `--input`        | Excel con columnas POSITION e IMAGE                   | `data/subset_puntuation.xlsx`            |
| `--output`       | Fichero de texto con los prompts generados            | `data/prompts_generated.txt`             |
| `--images-root`  | Carpeta raíz con subcarpetas por posición             | `../Data/Images`                         |
| `--limit`        | Máximo de imágenes a procesar (0 = todas)             | `0`                                      |

---

### evaluate_scores.py — Evaluación del rendimiento

Compara las puntuaciones generadas por el modelo (`results/subset_puntuation_generated.xlsx`) con las puntuaciones reales de un juez humano (`data/subset_puntuation_juez1.xlsx`). Una predicción se considera **correcta** si la diferencia con la puntuación del juez cae dentro de una banda de tolerancia configurable (por defecto ±1 puntos), lo que refleja la naturaleza continua y subjetiva de la puntuación en natación artística.

```bash
python scripts/evaluate_scores.py
python scripts/evaluate_scores.py --tolerance 0.3   # banda más estricta
python scripts/evaluate_scores.py --tolerance 1.5   # banda más permisiva
```

| Argumento       | Descripción                                         | Por defecto                                      |
|-----------------|-----------------------------------------------------|--------------------------------------------------|
| `--generated`   | Excel con puntuaciones del modelo                   | `results/subset_puntuation_generated.xlsx`       |
| `--judge`       | Excel con puntuaciones del juez (acepta fórmulas HYPERLINK) | `data/subset_puntuation_juez1.xlsx`     |
| `--output-dir`  | Carpeta donde guardar los resultados                | `results/`                                       |
| `--tolerance`   | Semiancho de la banda de aceptación                 | `1.0`                                            |

**Salidas generadas:**

- `results/score_evaluation.json` — métricas globales y por posición, más el detalle imagen a imagen.
- `results/score_report.html` — informe visual con barras de precisión por posición, tabla de imágenes fuera de rango ordenadas por error, y tabla completa con filas en verde/rojo.

---

## Motivación

Los otros módulos del TFG abordan la **clasificación** de la posición. Este módulo da un paso más allá: asumida la posición, cuantifica la calidad de la ejecución. Este es exactamente el trabajo de un juez en competición. La aproximación con skills permite codificar reglas de World Aquatics directamente en el sistema prompt, sin datos etiquetados de entrenamiento, y mantener el conocimiento experto actualizable de forma independiente del modelo subyacente.

---

## Cómo ejecutar

### Puntuar una imagen individual

```bash
python scripts/score_image.py <ruta/a/imagen.jpg> Fishtail
```

El script imprime el prompt a copiar en Claude con la imagen adjunta.

### Generar prompts en lote

```bash
python scripts/score_batch.py
```

Los prompts quedan en `data/prompts_generated.txt`. Cada bloque separado por `---` corresponde a una imagen; se envían a Claude de forma secuencial.

### Evaluar los resultados

Una vez que `results/subset_puntuation_generated.xlsx` contiene las puntuaciones del modelo:

```bash
python scripts/evaluate_scores.py
```

Abre `results/score_report.html` en el navegador para el informe visual completo.

---

## Modelo y herramientas

- **Modelo**: Claude Sonnet con visión multimodal (sin fine-tuning, sin entrenamiento).
- **Invocación**: skills cargadas desde `.agents/skills_punctuation/` (directorio externo en la raíz del repositorio).
- **Cartas de referencia**: ubicadas en `Data/references/scoring/` (raíz del repositorio), compartidas con el módulo App.
- **Limitación principal**: la estimación de ángulos es heurística (bandas), no medición exacta por keypoints. El siguiente paso natural sería integrar un detector de pose (MediaPipe, OpenPose) que inyecte ángulos calculados en el prompt, convirtiendo las bandas de D1 en valores exactos.
