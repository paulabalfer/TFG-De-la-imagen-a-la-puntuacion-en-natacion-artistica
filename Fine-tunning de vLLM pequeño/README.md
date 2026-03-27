# Fine-tuning de vLLM Pequeño

Directorio que implementa la clasificación de posiciones de natación artística mediante **fine-tuning supervisado de un modelo de lenguaje visual pequeño (vLLM)**. A diferencia de los enfoques anteriores, este paradigma adapta un modelo multimodal generativo preentrenado directamente a la tarea, actualizando únicamente un subconjunto mínimo de sus parámetros mediante LoRA.

---

## Contenido

```
Fine-tunning de vLLM pequeño/
├── Fine_tuning_SmolVLM_500M.ipynb     # Pipeline completo de fine-tuning y evaluación
└── smolvlm_lora_natacion/             # Artefactos generados tras el entrenamiento
    ├── mejor_checkpoint/              # Pesos LoRA del mejor epoch según val_acc
    ├── adaptador_lora_final/          # Adaptador LoRA + procesador al final del entrenamiento
    ├── distribucion_clases.png        # Distribución de clases del dataset (barras + tarta)
    ├── curvas_entrenamiento.png       # Curvas de loss y accuracy por época
    ├── confusion_matrix.png           # Matriz de confusión sobre el conjunto de test
    ├── classification_report.png      # Informe de clasificación (precisión, recall, F1) como imagen
    └── predicciones_muestra.png       # Predicciones de muestra con confianza por clase
```

---

## Motivación

Los enfoques previos (CNN, CLIP, MediaPipe) requieren o bien un dataset grande para generalizar bien (CNN), o bien son incapaces de adaptarse a la tarea específica (CLIP zero-shot). Este enfoque explora una vía intermedia:

- **Capacidad visual-semántica** de un modelo preentrenado en millones de pares imagen-texto.
- **Adaptación eficiente** al dominio de natación artística con pocos ejemplos por clase.
- **Sin generación libre de texto**: la clasificación se resuelve extrayendo logits sobre tokens de elección múltiple, lo que elimina el problema de coincidencia de cadenas y hace la inferencia determinista y rápida.

---

## Modelo elegido: SmolVLM-500M-Instruct

| Característica | BLIP base | BLIP-2 | **SmolVLM-500M** |
|---|---|---|---|
| Parámetros totales | ~224 M | ~2.7 B | **~500 M** |
| Tamaño en disco | ~990 MB | ~3 GB | **~1 GB (fp16)** |
| Modelo de lenguaje acoplado | BERT decoder | OPT-2.7B | SmolLM2-360M |
| Instruction following | Limitado | Moderado | **Bueno** |
| Cuantización necesaria | No | Sí (8-bit) | **No** |

**SmolVLM-500M-Instruct** (`HuggingFaceTB/SmolVLM-500M-Instruct`) combina:
- **SigLIP-400M** como encoder visual (ViT-So400M).
- **SmolLM2-360M** como modelo de lenguaje decoder (arquitectura LLaMA).
- Un **conector MLP** que proyecta los tokens visuales al espacio del LM.

---

## Pipeline

### Etapa 1: Preparación del dataset

Se carga el CSV del dataset aumentado (`synchronized_swimming_aug.csv`), se resuelven las rutas absolutas y se realiza una **partición estratificada 70 / 15 / 15** (train / val / test).

Para la **primera prueba** se extrae un **subconjunto pequeño y balanceado**:

| Partición | Imágenes por clase | Total |
|---|---|---|
| Train | 20 | 100 |
| Validación | 10 | 50 |
| Test | 15 | 75 |

> Cambiar `SUBSET_*_PER_CLASS = None` en la celda de configuración para entrenar con el dataset completo.

### Etapa 2: Clasificación por logits (multiple-choice)

En lugar de generación libre, se utiliza un enfoque de **elección múltiple por logits**:

1. El prompt pregunta `¿Cuál es la posición? (A) ... (E) ...` adjuntando la imagen.
2. Se obtienen los **logits del modelo en la última posición** (primer token de respuesta esperado).
3. Se comparan únicamente los logits de los tokens `A`, `B`, `C`, `D`, `E`.
4. El `argmax` determina la clase — sin generación, sin coincidencia de texto.

Este enfoque es más rápido, completamente determinista y no depende de que el modelo genere exactamente la cadena esperada.

### Etapa 3: Fine-tuning con LoRA

Se aplica **Low-Rank Adaptation (LoRA)** sobre las proyecciones `q_proj` y `v_proj` de todas las capas de atención del modelo (tanto el encoder visual como el LM decoder), actualizando solo **~1 %** de los parámetros totales.

| Hiperparámetro | Valor por defecto |
|---|---|
| LoRA rank (`r`) | 8 |
| LoRA alpha | 16 |
| Dropout | 0.05 |
| Módulos objetivo | `q_proj`, `v_proj` |
| Learning rate | 2 × 10⁻⁴ |
| Scheduler | Cosine Annealing |
| Épocas | 5 |
| Batch size | 2 |

La **función de pérdida** es `cross_entropy` sobre los 5 logits de elección, no sobre el vocabulario completo (~32 000 tokens). Esto acelera el entrenamiento y estabiliza la convergencia.

### Etapa 4: Evaluación

- **Distribución de clases** del dataset aumentado (barras + tarta).
- **Accuracy** sobre el conjunto de test con el mejor checkpoint de validación.
- **Informe de clasificación** (precisión, recall, F1 por clase) renderizado como imagen.
- **Matriz de confusión** y **predicciones de muestra** con confianza (softmax sobre logits de elección).

---

## Tecnologías

| Componente | Librería / Herramienta |
|---|---|
| Modelo base (vLLM) | SmolVLM-500M-Instruct (`transformers` 5.x, HuggingFace) |
| Fine-tuning eficiente | PEFT / LoRA (`peft`) |
| Aceleración | `accelerate` |
| Deep Learning | PyTorch |
| Procesamiento de imagen | Pillow |
| Cálculo numérico | NumPy, pandas |
| Evaluación | scikit-learn |
| Visualización | matplotlib |
| Entorno de ejecución | Jupyter Notebook |

---

## Ejecución

```bash
pip install -r requirements.txt
jupyter notebook "Fine-tunning de vLLM pequeño/Fine_tuning_SmolVLM_500M.ipynb"
```

> El notebook descarga automáticamente el modelo `HuggingFaceTB/SmolVLM-500M-Instruct` (~1 GB) desde HuggingFace Hub en la primera ejecución. Es necesaria conexión a internet para este paso.

> Para entrenar con el dataset completo (~5 200 imágenes), cambiar `SUBSET_*_PER_CLASS = None` en la celda de configuración global (sección 1).

---

## Evaluación sin reentrenar

El notebook incluye una celda dedicada a **cargar el mejor checkpoint** directamente desde `smolvlm_lora_natacion/mejor_checkpoint/`, lo que permite ejecutar la evaluación completa (test accuracy, informe de clasificación, matriz de confusión, predicciones de muestra) sin necesidad de repetir el entrenamiento:

```python
from peft import PeftModel

base  = AutoModelForImageTextToText.from_pretrained(MODEL_ID, torch_dtype=DTYPE)
model = PeftModel.from_pretrained(base, str(MODEL_SAVE / 'mejor_checkpoint'))
model.eval()
```

---

## Guardado y reutilización del adaptador

Al finalizar el entrenamiento se guardan únicamente los **pesos LoRA** (pocos MB), no el modelo base completo. Para cargar el modelo fine-tuned en otra sesión:

```python
from transformers import AutoProcessor, AutoModelForImageTextToText
from peft import PeftModel
import torch

base  = AutoModelForImageTextToText.from_pretrained(
    'HuggingFaceTB/SmolVLM-500M-Instruct',
    torch_dtype=torch.bfloat16,
)
model = PeftModel.from_pretrained(base, 'smolvlm_lora_natacion/adaptador_lora_final')
proc  = AutoProcessor.from_pretrained('smolvlm_lora_natacion/adaptador_lora_final')
```
