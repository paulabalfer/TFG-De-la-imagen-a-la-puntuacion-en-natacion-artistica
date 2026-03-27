# Modelo Preentrenado Basado en Coordenadas

Directorio que implementa un pipeline de clasificación alternativo fundamentado en **estimación de pose**. En lugar de procesar la imagen en bruto, este enfoque extrae las coordenadas tridimensionales de los puntos clave del cuerpo humano y entrena clasificadores clásicos de machine learning sobre dichos vectores de coordenadas.

---

## Contenido

```
Modelo preentrenado basado en coordenadas/
├── MediaPipe_Pose_Classifier.ipynb    # Pipeline completo de extracción y clasificación
├── pose_landmarker_heavy.task         # Modelo MediaPipe PoseLandmarker Heavy (~25 MB)
├── pose_classifier_model.pkl          # Random Forest entrenado
├── pose_classifier_scaler.pkl         # StandardScaler ajustado al conjunto de entrenamiento
├── label_encoder.pkl                  # LabelEncoder con las 5 clases
└── classification_results.pkl         # Métricas y matriz de confusión serializadas
```

---

## Motivación

Los modelos que trabajan directamente sobre la imagen completa pueden verse afectados por variaciones en el fondo, la iluminación, el color del bañador o el ángulo de la cámara. Este enfoque desacopla el problema en dos etapas:

1. **Extracción de estructura corporal** — reducir la imagen a una representación compacta e invariante: las posiciones relativas de las articulaciones.
2. **Clasificación sobre geometría** — entrenar modelos de ML clásico sobre dichas coordenadas, que son intrínsecamente agnósticas al contexto visual.

---

## Pipeline

### Etapa 1: Extracción de Keypoints con MediaPipe

Se utiliza el modelo **MediaPipe PoseLandmarker Heavy** para detectar y extraer los **33 puntos de referencia 3D** del cuerpo humano definidos por el estándar MediaPipe (caderas, rodillas, tobillos, hombros, codos, muñecas, etc.).

- **Entrada**: imagen RGB de la nadadora.
- **Salida**: vector de 33 × 3 coordenadas normalizadas `(x, y, z)`, donde `x` e `y` son fracciones del ancho y alto de la imagen, y `z` representa la profundidad relativa.
- **Modelo**: `pose_landmarker_heavy.task` (descargado automáticamente en la primera ejecución si no está presente).

> La variante *heavy* ofrece mayor precisión en la detección de poses complejas o parcialmente ocluidas, a costa de un mayor coste computacional respecto a las variantes *lite* y *full*.

### Etapa 2: Extracción de características geométricas

En lugar de usar las coordenadas brutas de los 33 landmarks, se calculan **17 características geométricas** más informativas y compactas:

| Grupo | Características |
|---|---|
| Distancias | Hombros, caderas, cabeza-cadera, rodilla-cadera (izq/der), tobillo-cadera (izq/der) |
| Ratios | Cadera-tobillo / hombro-cadera (izq/der) |
| Ángulos | Pierna izq/der (cadera-rodilla-tobillo), torso (cadera-hombro-nariz) |
| Posición global | Y medio, Z medio del cuerpo |
| Asimetría | Diferencia Y entre hombros, diferencia Y entre caderas |
| Calidad | Visibilidad media de landmarks |

### Etapa 2b: Análisis exploratorio de la matriz de características

Antes del entrenamiento se generan tres visualizaciones:

- **Boxplots** — distribución de cada característica por clase (sin outliers extremos).
- **Heatmap de correlación** — correlación de Pearson entre las 17 características.
- **PCA 2D** — proyección de todas las muestras en dos componentes principales para evaluar la separabilidad visual de las clases.

### Etapa 3: Clasificación con Random Forest

El clasificador principal es un **Random Forest** (200 árboles, `max_depth=20`) entrenado sobre el conjunto de entrenamiento (80 %) y evaluado en el conjunto de test (20 %) mediante accuracy, un reporte de clasificación en formato heatmap (precision, recall y F1 por clase) y una matriz de confusión visual.

---

## Salidas generadas

| Fichero | Contenido |
|---|---|
| `pose_classifier_model.pkl` | Modelo Random Forest entrenado |
| `pose_classifier_scaler.pkl` | StandardScaler ajustado al conjunto de entrenamiento |
| `label_encoder.pkl` | LabelEncoder con las 5 clases |
| `classification_results.pkl` | Métricas y matriz de confusión en formato pickle |
| `feature_boxplots_by_class.png` | Boxplots de las 17 características por clase |
| `feature_correlation_heatmap.png` | Heatmap de correlación entre características |
| `feature_pca_2d.png` | Proyección PCA 2D de todas las muestras |
| `confusion_matrix.png` | Matriz de confusión del test set |
| `classification_report_heatmap.png` | Heatmap de precision / recall / F1 por clase |
| `confidence_by_class.png` | Confianza media del modelo en aciertos y fallos por clase |

---

## Ventajas de este enfoque

- **Invarianza al fondo e iluminación**: el clasificador solo ve características geométricas, no píxeles.
- **Bajo coste computacional**: los clasificadores clásicos son órdenes de magnitud más ligeros que una CNN.
- **Interpretabilidad**: es posible analizar qué características son más discriminativas mediante la importancia de características del Random Forest.
- **Menor requisito de datos**: los modelos de ML clásico generalizan bien con conjuntos pequeños cuando las features son informativas.

---

## Tecnologías

| Componente | Librería / Herramienta |
|---|---|
| Estimación de pose | MediaPipe (`mediapipe`) |
| Clasificador | scikit-learn (Random Forest) |
| Procesamiento de imagen | OpenCV, Pillow |
| Cálculo numérico | NumPy, pandas |
| Visualización | matplotlib |
| Entorno de ejecución | Jupyter Notebook |

---

## Ejecución

```bash
pip install -r requirements.txt
jupyter notebook "Modelo preentrenado basado en coordenadas/MediaPipe_Pose_Classifier.ipynb"
```

> En la primera ejecución, el notebook descarga automáticamente el fichero `pose_landmarker_heavy.task` (~25 MB) desde los servidores de Google si no se encuentra en el directorio de trabajo. Es necesaria conexión a internet para este paso.
