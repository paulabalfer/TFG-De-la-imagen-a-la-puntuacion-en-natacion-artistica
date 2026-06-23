# De la Imagen a la Puntuación: Clasificación y Evaluación técnica de posiciones básicas en Natación Artística mediante modelos multimodales

> Trabajo de Fin de Grado

Este proyecto compara distintos enfoques de clasificación automática de **5 posiciones básicas de natación artística (sincronizada)**, desde modelos de aprendizaje profundo hasta sistemas basados en estimación de pose y prompts estructurados con LLMs de visión, e incluye además un módulo de **puntuación automática de la calidad de ejecución**. El dataset es propio, recogido manualmente; los experimentos cubren aprendizaje supervisado, zero-shot, few-shot, fine-tuning eficiente con LoRA, clasificación por skills sin entrenamiento y evaluación técnica automatizada.

> Cada directorio dispone de su propio `README.md` con la descripción detallada del enfoque, el pipeline y las instrucciones de ejecución.

---

## Contenido

```
TFG_repo/
├── README.md
├── requirements.txt                                       # Dependencias pip del entorno
├── .agents/                                               # Skills externas compartidas por todos los módulos
│   ├── skills_classification/                             # Skills de clasificación (Sistema basado en skills con vLLMs)
│   └── skills_punctuation/                                # Skills de puntuación (Punctuation + App)
├── Data/                                                  # Índices del dataset y documentación
│   ├── Data_process.ipynb                                 
│   ├── synchronized_swimming.csv                          
│   └── synchronized_swimming_aug.csv                     
├── Modelos Naïve/                                         # Enfoque Clasificación 1: modelos sobre imagen completa
│   └── Modelos_por_análisis_visual_completo.ipynb
├── Modelo preentrenado basado en coordenadas/             # Enfoque Clasificación 2: clasificación por keypoints
│   ├── MediaPipe_Pose_Classifier.ipynb
│   ├── pose_landmarker_heavy.task                         
│   ├── pose_classifier_model.pkl                          
│   ├── pose_classifier_scaler.pkl                         
│   ├── label_encoder.pkl                                  
│   └── classification_results.pkl                         
├── Fine-tuning de vLLM pequeño/                           # Enfoque Clasificación 3: fine-tuning LoRA de vLLM
│   ├── Fine_tuning_SmolVLM_500M.ipynb
│   └── smolvlm_lora_natacion/                             
├── Sistema basado en skills con vLLMs/                    # Enfoque Clasificación 4: clasificación por skills sin entrenamiento
│   ├── data/
│   ├── splits/
│   ├── results/
│   └── scripts/
├── Puntuación/                                            # Módulo de puntuación automática de ejecución técnica
│   ├── data/
│   ├── results/
│   └── scripts/
└── App/                                                   # Interfaz web integrada (clasificación + puntuación)
    ├── app.py
    ├── classifier.py
    ├── scorer.py
    └── requirements.txt
```

---

## Dataset y sus clases

El dataset recoge **5 posiciones básicas** de natación artística definidas por el manual oficial de figuras de World Aquatics (2022–2025):

| Clase | Código BP | Características principales |
|---|---|---|
| `Double Leg Vertical` | BP6 | Ambas piernas juntas, rectas y verticales; tronco sumergido |
| `Fishtail` | BP8 | Una pierna vertical + una pierna recta hacia adelante; espalda recta |
| `Bent Knee Vertical` | BP14c | Una pierna vertical + rodilla contraria flexionada, muslo horizontal |
| `Bent Knee Surface Arch` | BP14d | Espalda arqueada + rodilla flexionada, muslo perpendicular; posición en superficie |
| `Knight` | BP17 | Espalda arqueada + una pierna vertical + una pierna recta hacia atrás |

- **Dataset original**: 263 imágenes recogidas manualmente.
- **Dataset aumentado**: 6 575 imágenes (25 variantes por imagen original mediante rotaciones, volteos y ajustes fotométricos).

---

## Enfoques de Clasificación

### `Modelos Naïve/` — Cinco enfoques sobre imagen completa

Notebook único que implementa cinco enfoques de complejidad creciente. El modelo recibe la imagen en bruto sin representaciones intermedias, desde transfer learning supervisado (EfficientNetB3) hasta clasificación zero-shot y few-shot con CLIP. Se incluye también un análisis de interpretabilidad con Grad-CAM.

---

### `Modelo preentrenado basado en coordenadas/` — Clasificación por keypoints

Pipeline alternativo basado en **estimación de poses**: extracción de 33 landmarks 3D con MediaPipe PoseLandmarker Heavy, cálculo de 17 características geométricas y clasificación con Random Forest y SVM. Enfoque invariante al fondo e iluminación.

---

### `Fine-tuning de vLLM pequeño/` — Fine-tuning LoRA de SmolVLM-500M

Adaptación de **`HuggingFaceTB/SmolVLM-500M-Instruct`** a la tarea mediante LoRA, actualizando solo ~0,22 % de los parámetros. La clasificación se resuelve por logits de elección múltiple, sin generación libre de texto.

---

### `Sistema basado en skills con vLLMs/` — Clasificación por skills sin entrenamiento

Sistema basado en **prompts estructurados como skills** para LLMs de visión, sin ningún entrenamiento ni fine-tuning. La skill orquestadora evalúa cada imagen contra las 5 posiciones en paralelo y aplica reglas de agregación para emitir la clase.

### `Puntuación/` — Puntuación automática de ejecución técnica

Sistema de evaluación automática de la **calidad de ejecución** de las posiciones clasificadas, utilizando LLMs de visión con prompts estructurados. Genera una puntuación técnica para cada imagen sin entrenamiento, siguiendo criterios inspirados en el reglamento de World Aquatics.

---

### `App/` — Interfaz web integrada

Aplicación **Gradio** que combina los módulos de clasificación y puntuación en una única interfaz interactiva. El pipeline completo es:

1. El usuario sube una fotografía de una nadadora.
2. **`classifier.py`** clasifica la posición localmente usando SmolVLM-500M + LoRA (92 % accuracy, sin API externa).
3. **`scorer.py`** puntúa la ejecución técnica mediante la Anthropic API (Claude) con el sistema de skills de `Puntuación/` (paso opcional; requiere API key).

La interfaz muestra la posición detectada con su confianza, la distribución de probabilidades sobre las 5 clases, el informe de puntuación y la tabla oficial de alturas de referencia de World Aquatics.

```bash
python App/app.py   # abre http://127.0.0.1:7860
```

---

## Instalación

### 0. Requisito previo: Python 3.11

Por dependencias del proyecto, es necesario trabajar con **Python 3.11** para que todas las librerías sean compatibles. Si no lo tienes instalado:

1. **Descarga Python 3.11** desde [https://www.python.org/downloads/release/python-3119/](https://www.python.org/downloads/release/python-3119/) (busca *"Windows installer (64-bit)"*, o el apropiado para tu equipo).
2. **Instálalo** marcando la opción **"Add python.exe to PATH"** — aunque ya tengas otra versión de Python, Windows permite tener varias instaladas a la vez (cada una con su propio launcher), por lo que no interfiere con instalaciones previas.

### 1. Clonar e instalar dependencias

```bash
# 1. Clonar el repositorio
git clone <URL-del-repositorio>
cd TFG_repo

# 2. Instalar todas las dependencias
pip install -r requirements.txt
```

> **Nota:** Si se dispone de GPU, consultar las instrucciones de instalación de [PyTorch con CUDA](https://pytorch.org/get-started/locally/) y [TensorFlow con GPU](https://www.tensorflow.org/install/pip) para sustituir los paquetes CPU por sus versiones aceleradas.

Cada directorio es independiente y autocontenido; consultar su `README.md` para las instrucciones de ejecución específicas.

---

## Privacidad e imágenes del dataset

Las imágenes de entrenamiento y evaluación muestran deportistas que podrían ser identificables. Por este motivo, **las imágenes no se incluyen en este repositorio**. El código, los scripts, los notebooks y los ficheros de índice CSV están disponibles de forma abierta; el acceso a las imágenes podrá valorarse bajo petición justificada, indicando el uso previsto y con las medidas de protección de datos correspondientes.

---

## Autor

**Paula Ballesteros Fernández**  
Grado en Ciencia de Datos e Inteligencia Artificial · Universidad Politécnica de Madrid
