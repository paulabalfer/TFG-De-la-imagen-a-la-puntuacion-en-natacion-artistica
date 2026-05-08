# TFG: Automatización de la Identificación de Posiciones de Natación Artística

> Trabajo de Fin de Grado

Este proyecto compara distintos enfoques de clasificación automática de **5 posiciones corporales reglamentarias de natación artística (sincronizada)**, desde modelos de aprendizaje profundo hasta sistemas basados en estimación de pose y prompts estructurados con LLMs de visión. El dataset es propio, recogido manualmente; los experimentos cubren aprendizaje supervisado, zero-shot, few-shot, fine-tuning eficiente con LoRA y clasificación por skills sin entrenamiento.

> Cada directorio dispone de su propio `README.md` con la descripción detallada del enfoque, el pipeline y las instrucciones de ejecución.

---

## Contenido

```
TFG_repo/
├── README.md
├── requirements.txt                                       # Dependencias pip del entorno
├── Data/                                                  # Dataset, referencias e índices de imágenes
│   ├── Data_process.ipynb                                 
│   ├── synchronized_swimming.csv                          
│   ├── synchronized_swimming_aug.csv                     
│   ├── Images/                                            
│   ├── Augmented/                                         
│   └── references/                                        # Material de referencia visual
├── Modelos Naïve/                                         # Enfoque Clasificación 1: modelos sobre imagen completa
│   └── Modelos_por_análisis_visual_completo.ipynb
├── Modelo preentrenado basado en coordenadas/             # Enfoque Clasificación 2: clasificación por keypoints
│   ├── MediaPipe_Pose_Classifier.ipynb
│   ├── pose_landmarker_heavy.task                         
│   ├── pose_classifier_model.pkl                          
│   ├── pose_classifier_scaler.pkl                         
│   ├── label_encoder.pkl                                  
│   └── classification_results.pkl                         
├── Fine-tunning de vLLM pequeño/                          # Enfoque Clasificación 3: fine-tuning LoRA de vLLM
│   ├── Fine_tuning_SmolVLM_500M.ipynb
│   └── smolvlm_lora_natacion/                             
└── Sistema basado en skills con vLLMs/                    # Enfoque Clasificación 4: clasificación por skills sin entrenamiento
    ├── data/
    ├── splits/
    ├── results/
    ├── scripts/
    └── .agents/skills/
```

---

## Dataset y sus clases

El dataset recoge **5 posiciones corporales reglamentarias** de natación artística definidas por el manual oficial de figuras de World Aquatics (2022–2025):

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

### `Fine-tunning de vLLM pequeño/` — Fine-tuning LoRA de SmolVLM-500M

Adaptación de **`HuggingFaceTB/SmolVLM-500M-Instruct`** a la tarea mediante LoRA, actualizando solo ~0,22 % de los parámetros. La clasificación se resuelve por logits de elección múltiple, sin generación libre de texto.

---

### `Sistema basado en skills con vLLMs/` — Clasificación por skills sin entrenamiento

Sistema basado en **prompts estructurados como skills** para LLMs de visión, sin ningún entrenamiento ni fine-tuning. Alcanza un **99,38 % de accuracy** sobre 6 000 imágenes. La skill orquestadora evalúa cada imagen contra las 5 posiciones en paralelo y aplica reglas de agregación para emitir la clase.

---

## Instalación

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

## Autor

**Paula Ballesteros**  
Grado en Ciencia de Datos e Inteligencia Artificial · Universidad Politécnica de Madrid
