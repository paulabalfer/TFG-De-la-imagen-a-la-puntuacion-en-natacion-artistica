# Fine-tuning de vLLM Pequeño

Directorio que implementa la clasificación de posiciones de natación artística mediante **fine-tuning supervisado de un modelo de lenguaje visual pequeño (vLLM)**. A diferencia de los enfoques anteriores, este paradigma adapta un modelo multimodal generativo preentrenado directamente a la tarea, actualizando únicamente un subconjunto mínimo de sus parámetros mediante LoRA.

---

## Contenido

```
Fine-tuning de vLLM pequeño/
├── Fine_tuning_SmolVLM_500M.ipynb     # Notebook con el pipeline completo
└── smolvlm_lora_natacion/             # Artefactos generados tras el entrenamiento
    ├── mejor_checkpoint/              # Pesos LoRA del mejor epoch según val_acc
    │   ├── adapter_config.json
    │   ├── adapter_model.safetensors
    │   └── README.md
    └── adaptador_lora_final/          # Adaptador LoRA + procesador al final del entrenamiento
        ├── adapter_config.json
        ├── adapter_model.safetensors  # ~4.3 MB — solo los pesos LoRA
        ├── chat_template.jinja
        ├── processor_config.json
        ├── tokenizer.json
        ├── tokenizer_config.json
        └── README.md
```

---

## Modelo: SmolVLM-500M-Instruct

| Característica | BLIP base | BLIP-2 | **SmolVLM-500M** |
|---|---|---|---|
| Parámetros totales | ~224 M | ~2,7 B | **~500 M** |
| Tamaño en disco | ~990 MB | ~3 GB | **~1 GB (fp16)** |
| Modelo de lenguaje acoplado | BERT decoder | OPT-2.7B | SmolLM2-360M |
| Instruction following | Limitado | Moderado | **Bueno** |
| Cuantización necesaria | No | Sí (8-bit) | **No** |

**`HuggingFaceTB/SmolVLM-500M-Instruct`** combina:
- **SigLIP-400M** como encoder visual (ViT-So400M).
- **SmolLM2-360M** como modelo de lenguaje decoder (arquitectura LLaMA).
- Un **conector MLP** que proyecta los tokens visuales al espacio del LM.

---

## Pipeline

### Etapa 1 — Preparación del dataset

Se carga `synchronized_swimming_aug.csv`, se resuelven las rutas absolutas y se realiza una **partición estratificada 70 / 15 / 15** (train / val / test).

Por defecto se extrae un **subconjunto balanceado** para agilizar el entrenamiento:

| Partición | Imágenes por clase | Total |
|---|---|---|
| Train | 60 | 300 |
| Validación | 20 | 100 |
| Test | 30 | 150 |

> Cambiar `SUBSET_*_PER_CLASS = None` en la celda de configuración para entrenar con el dataset completo (4 601 / 987 / 987).

---

### Etapa 2 — Clasificación por logits (multiple-choice)

En lugar de generación libre de texto, se utiliza un enfoque de **elección múltiple por logits**:

1. El prompt pregunta `¿Cuál es la posición? (A) ... (E) ...` adjuntando la imagen.
2. Se extraen los **logits del modelo en la última posición** (primer token de respuesta esperado).
3. Se comparan únicamente los logits de los tokens `A`, `B`, `C`, `D`, `E`.
4. El `argmax` determina la clase — sin generación, sin coincidencia de cadenas.

Este enfoque es determinista, más rápido que la generación y no depende de que el modelo produzca exactamente la cadena esperada.

---

### Etapa 3 — Fine-tuning con LoRA

Se aplica **Low-Rank Adaptation (LoRA)** sobre las proyecciones `q_proj` y `v_proj` de todas las capas de atención (encoder visual + LM decoder), actualizando solo **~0,22 %** de los parámetros totales.

| Hiperparámetro | Valor |
|---|---|
| LoRA rank (`r`) | 8 |
| LoRA alpha | 16 |
| Dropout | 0,05 |
| Módulos objetivo | `q_proj`, `v_proj` |
| Learning rate | 2 × 10⁻⁴ |
| Scheduler | Cosine Annealing |
| Épocas | 5 |
| Batch size | 2 |
| Parámetros entrenables | 1 114 112 (0,22 % del total) |

La función de pérdida es `cross_entropy` sobre los 5 logits de elección, no sobre el vocabulario completo (~49 000 tokens).

---

### Etapa 4 — Evaluación

- **Informe de clasificación** (precisión, recall, F1 por clase).
- **Matriz de confusión** sobre el conjunto de test.
- **Predicciones de muestra** con confianza (softmax sobre logits de elección).
- **Distribución de clases** del dataset (barras + tarta).

---

## Artefactos guardados

| Fichero / Carpeta | Contenido |
|---|---|
| `mejor_checkpoint/adapter_model.safetensors` | Pesos LoRA del epoch con mayor val_acc (epoch 5) |
| `adaptador_lora_final/adapter_model.safetensors` | Pesos LoRA del último epoch (~4,3 MB) |
| `adaptador_lora_final/processor_config.json` | Configuración del procesador de imagen (512×512) |
| `adaptador_lora_final/tokenizer.json` | Vocabulario y reglas BPE del tokenizador |
| `adaptador_lora_final/chat_template.jinja` | Plantilla de formato de mensajes (user / assistant) |

Solo se guardan los **pesos LoRA** (pocos MB), no el modelo base completo (~1 GB).

---

## Motivación

Los enfoques previos (CNN, CLIP, MediaPipe) requieren o bien un dataset grande para generalizar (CNN), o bien son incapaces de adaptarse a la tarea específica (CLIP zero-shot). Este enfoque explora una vía intermedia:

- **Capacidad visual-semántica** de un modelo preentrenado en millones de pares imagen-texto.
- **Adaptación eficiente** al dominio de natación artística con pocos ejemplos por clase.
- **Sin generación libre**: la clasificación se resuelve por logits, lo que hace la inferencia determinista y rápida.

---

## Cómo ejecutar

### Lanzar el notebook

Desde la raíz del repositorio:

```bash
jupyter notebook "Fine-tuning de vLLM pequeño/Fine_tuning_SmolVLM_500M.ipynb"
```

O con JupyterLab:

```bash
jupyter lab "Fine-tuning de vLLM pequeño/Fine_tuning_SmolVLM_500M.ipynb"
```

### Orden de ejecución

El notebook es autocontenido. Ejecutar las celdas **en orden de arriba a abajo**:

1. Imports y configuración global (`SEED=42`, hiperparámetros LoRA, tamaños de subconjunto)
2. **Etapa 1** — Carga del CSV, resolución de rutas y partición estratificada
3. **Etapa 2** — Diseño del prompt de elección múltiple y extracción de token IDs
4. **Etapa 3** — Carga del modelo base + aplicación de LoRA + definición de DataLoaders
5. Bucle de entrenamiento (5 épocas con guardado del mejor checkpoint por val_acc)
6. **Etapa 4** — Evaluación en test (accuracy, F1, matriz de confusión, predicciones de muestra)
7. Guardado del adaptador final en `smolvlm_lora_natacion/adaptador_lora_final/`

> **Nota**: en la primera ejecución el notebook descarga `HuggingFaceTB/SmolVLM-500M-Instruct` (~1 GB) desde HuggingFace Hub. Es necesaria conexión a internet.

### Evaluación sin reentrenar

El notebook incluye una celda para **cargar el mejor checkpoint** y ejecutar la evaluación completa sin repetir el entrenamiento:

```python
from peft import PeftModel
base  = AutoModelForImageTextToText.from_pretrained(MODEL_ID, torch_dtype=DTYPE)
model = PeftModel.from_pretrained(base, str(MODEL_SAVE / 'mejor_checkpoint'))
model.eval()
```
