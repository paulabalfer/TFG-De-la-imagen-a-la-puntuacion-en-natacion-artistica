# Sistema Basado en Skills con vLLMs

Directorio que implementa la clasificación de posiciones de natación artística mediante **LLM como modelo de visión**, sin ningún entrenamiento ni fine-tuning. La clasificación se realiza a través de prompts estructurados implementados como *skills*, que codifican el conocimiento experto de los árbitros de *World Aquatics*. El sistema escala a datasets completos mediante un pipeline de procesamiento por lotes.

---

## Contenido

```
Sistema basado en skills con vLLMs/
├── README.md
├── data/
|   ├── all_files.txt                                    # ORIGINAL. Lista completa de imágenes en el conjunto 
│   ├── image_labels.json                                # ORIGINAL. Etiquetas reales de todo el dataset
│   └── ground_truth_for_predictions.json                # GENERADO. Ground truth filtrado para las imágenes evaluadas
├── splits/
│   ├── batch_01.txt                                     # GENERADO. Lote 1 de imágenes (hasta 250 imágenes por lote)
│   ├── ...
│   └── batch_27.txt
├── results/
│   ├── splits/
│   │   ├── predictions_batch_01.json                    # GENERADO. Predicciones del lote 1
│   │   ├── ...
│   │   └── predictions_batch_24.json
│   ├── predictions.json                                 # GENERADO. Predicciones unificadas de todos los lotes
│   ├── results.json                                     # GENERADO. Métricas finales y matriz de confusión
│   └── report.html                                      # GENERADO. Informe de evaluación en HTML
├── scripts/
│   ├── split_random.py                                  # Divide all_files.txt en lotes aleatorios
│   ├── merge_results.py                                 # Une las predicciones de todos los lotes
│   ├── generate_ground_truth.py                         # Genera el ground truth para las imágenes evaluadas
│   └── compute_accuracy_and_report.py                   # Calcula métricas y genera el informe HTML
└── .agents/
    └── skills/
        ├── natacion-classifier/SKILL.md                 # Orquestador — evalúa las 5 posiciones y decide la clase
        ├── natacion-bp06-double-leg-vertical/SKILL.md
        ├── natacion-bp08-fishtail/SKILL.md
        ├── natacion-bp14c-bent-knee-vertical/SKILL.md
        ├── natacion-bp14d-bent-knee-surface-arch/SKILL.md
        └── natacion-bp17-knight/SKILL.md
```

---

### Árbol de decisión

```
1. ¿Cuántas direcciones distintas tienen las piernas?
   +-- UNA (ambas juntas) ---------> Double Leg Vertical (BP6)
   +-- DOS (piernas separadas) ----> Paso 2

2. ¿Alguna rodilla está FLEXIONADA?
   +-- SÍ --> Paso 3
   +-- NO --> Paso 4

3. ¿La espalda está ARQUEADA?
   +-- SÍ --> Bent Knee Surface Arch (BP14d)
   +-- NO --> Bent Knee Vertical (BP14c)

4. ¿La espalda está ARQUEADA?
   +-- SÍ --> Knight (BP17)
   +-- NO --> Fishtail (BP8)
```

---

## Arquitectura de las Skills

Cada skill de posición contiene seis componentes:

1. **Definición oficial** — especificación del Manual de Figuras de World Aquatics.
2. **Scratchpad visual** — procedimiento de evaluación de 7 pasos para observación sistemática.
3. **Lista de exclusión** — descalificadores estrictos (cualquiera activado → puntuación 0).
4. **Aprendizaje contrastivo** — tablas comparativas para cada par de posiciones confundibles.
5. **Rúbrica de puntuación** — escala 0-5 con criterios precisos por nivel.
6. **Text shots** — descripciones textuales detalladas de imágenes de entrenamiento verificadas (equivalente a few-shot sin consumir tokens de visión adicionales).

### Orquestador (`natacion-classifier`)

La skill maestra puntúa la imagen contra las **5 posiciones** y aplica reglas de agregación:

- **Regla 1**: Todas las puntuaciones ≤ 1 → INCIERTO.
- **Regla 2**: Ganador claro (≥ 2 puntos de ventaja) → clasificar.
- **Regla 3**: Ganador moderado (≥ 1 punto de ventaja) → clasificar.
- **Regla 4**: Empate → desempate por número de exclusiones, heurísticas de pares confusos y sesgo anti-Fishtail.

---

## Pipeline

### Etapa 1 — División del dataset en lotes

El script `split_random.py` lee `data/all_files.txt` y divide las imágenes en lotes de hasta 250 imágenes, escritos en `splits/batch_XX.txt`. La aleatorización garantiza distribución uniforme de clases por lote.

- **Entrada**: `data/all_files.txt` con todos los nombres de imagen.
- **Salida**: ficheros `splits/batch_01.txt` … `splits/batch_NN.txt`.
- **Parámetro clave**: `IMAGES_PER_FILE = 250`.

---

### Etapa 2 — Clasificación por lotes con skills

Cada lote se procesa mediante la skill orquestadora `natacion-classifier`, que lanza 5 subagentes en paralelo (uno por clase) para cada imagen del lote. Los resultados de cada lote se guardan en `results/splits/predictions_batch_XX.json`.

- **Entrada**: fichero de lote (`splits/batch_XX.txt`) con nombres de imagen.
- **Salida**: `results/splits/predictions_batch_XX.json` con `[{filename, classification}, ...]`.
- **Paralelización**: 5 subagentes concurrentes por imagen para evaluación eficiente.

---

### Etapa 3 — Unión de predicciones

El script `merge_results.py` agrega todos los ficheros `predictions_batch_*.json` en un único `results/predictions.json`.

- **Entrada**: todos los ficheros en `results/splits/`.
- **Salida**: `results/predictions.json` con la lista completa de predicciones.

---

### Etapa 4 — Generación de ground truth y evaluación

El script `generate_ground_truth.py` cruza las predicciones con `data/image_labels.json` para construir el ground truth alineado. A continuación, `compute_accuracy_and_report.py` calcula las métricas y genera el informe.

- **Entrada**: `results/predictions.json` + `data/image_labels.json`.
- **Salidas**: `results/results.json` (métricas y matriz de confusión) y `results/report.html` (informe HTML interactivo).


---

## Cómo ejecutar

### 1. Dividir el dataset en lotes

```bash
cd "Sistema basado en skills con vLLMs"
python scripts/split_random.py
```

Genera los ficheros `splits/batch_XX.txt` (hasta 250 imágenes cada uno).

### 2. Clasificar cada lote con la skill orquestadora

Desde el directorio del proyecto, lanzar la skill para cada lote:

```
Classify all images in @splits/batch_01.txt based on the skill @.agents/skills/natacion-classifier/SKILL.md . 
Save the images on @results/splits/ . Do not evaluate or modify any existing file; just classify the images.
```

Repetir para cada lote o paralelizar entre sesiones.

### 3. Unir las predicciones

```bash
python scripts/merge_results.py
```

Genera `results/predictions.json` con todas las predicciones.

### 4. Generar el ground truth

```bash
python scripts/generate_ground_truth.py
```

Genera `data/ground_truth_for_predictions.json` cruzando predicciones con etiquetas.

### 5. Calcular métricas y generar el informe

```bash
python scripts/compute_accuracy_and_report.py
```

Genera `results/results.json` y `results/report.html`.
