# Modelo Preentrenado Basado en Coordenadas

Directorio que implementa un pipeline de clasificación alternativo fundamentado en **estimación de pose**. En lugar de procesar la imagen en bruto, este enfoque extrae las coordenadas tridimensionales de los puntos clave del cuerpo humano y entrena clasificadores clásicos de machine learning sobre dichos vectores de coordenadas.

---

## Contenido

```
Modelo preentrenado basado en coordenadas/
├── MediaPipe_Pose_Classifier.ipynb         # Notebook con el pipeline completo
├── pose_landmarker_heavy.task              # Modelo MediaPipe PoseLandmarker Heavy (~25 MB) - En caso de no estar su descarga se realiza con la ejecución del notebook
├── pose_classifier_model.pkl               # Resultado guardado: Random Forest entrenado
├── pose_classifier_scaler.pkl              # Resultado guardado: StandardScaler ajustado al conjunto de entrenamiento
├── label_encoder.pkl                       # Resultado guardado: LabelEncoder con las 5 clases
└── classification_results.pkl              # Resultado guardado: Métricas y matriz de confusión serializadas
```

---

## Pipeline

### Etapa 1 — Extracción de keypoints con MediaPipe

Se utiliza el modelo **MediaPipe PoseLandmarker Heavy** para detectar y extraer los **33 puntos de referencia 3D** del cuerpo humano definidos por el estándar MediaPipe (caderas, rodillas, tobillos, hombros, codos, muñecas, etc.).

- **Entrada**: imagen RGB de la nadadora.
- **Salida**: vector de 33 × 3 coordenadas normalizadas `(x, y, z)`, donde `x` e `y` son fracciones del ancho y alto de la imagen, y `z` representa la profundidad relativa.
- **Modelo**: `pose_landmarker_heavy.task` (descargado automáticamente en la primera ejecución si no está presente).

> La variante *heavy* ofrece mayor precisión en la detección de poses complejas o parcialmente ocluidas, a costa de un mayor coste computacional respecto a las variantes *lite* y *full*.

---

### Etapa 2 — Extracción de características geométricas

En lugar de usar las coordenadas brutas de los 33 landmarks, se calculan **17 características geométricas** más informativas y compactas:

| Grupo | Características |
|---|---|
| Distancias | Hombros, caderas, cabeza-cadera, rodilla-cadera (izq/der), tobillo-cadera (izq/der) |
| Ratios | Cadera-tobillo / hombro-cadera (izq/der) |
| Ángulos | Pierna izq/der (cadera-rodilla-tobillo), torso (cadera-hombro-nariz) |
| Posición global | Y medio, Z medio del cuerpo |
| Asimetría | Diferencia Y entre hombros, diferencia Y entre caderas |
| Calidad | Visibilidad media de landmarks |

---

### Etapa 3 — Clasificación con Random Forest

El clasificador principal es un **Random Forest** (200 árboles, `max_depth=20`) entrenado sobre el conjunto de entrenamiento (80 %) y evaluado en el conjunto de test (20 %) con accuracy, reporte de clasificación y matriz de confusión.

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

El guardado automático de las imágenes con extensión **.png** está desactivado, en caso de querer guardarlas durante el proceso se ha de descomentar las debidas líneas de código manualmente. 

---

## Motivación

Este enfoque desacopla el problema en dos etapas:

1. **Extracción de estructura corporal** — reducir la imagen a una representación compacta e invariante: las posiciones relativas de las articulaciones.
2. **Clasificación sobre geometría** — entrenar modelos de ML clásico sobre dichas coordenadas, que son intrínsecamente agnósticas al contexto visual.

**Ventajas**:
- **Invarianza al fondo e iluminación**: el clasificador solo ve características geométricas, no píxeles.
- **Bajo coste computacional**: los clasificadores clásicos son órdenes de magnitud más ligeros que una CNN.
- **Interpretabilidad**: es posible analizar qué características son más discriminativas mediante la importancia de características del Random Forest.
- **Menor requisito de datos**: los modelos de ML clásico generalizan bien con conjuntos pequeños cuando las features son informativas.


---

## Cómo ejecutar

### Lanzar el notebook

Desde la raíz del repositorio:

```bash
jupyter notebook "Modelo preentrenado basado en coordenadas/MediaPipe_Pose_Classifier.ipynb"
```

O con JupyterLab:

```bash
jupyter lab "Modelo preentrenado basado en coordenadas/MediaPipe_Pose_Classifier.ipynb"
```

### Orden de ejecución

El notebook es autocontenido. Ejecutar las celdas **en orden de arriba a abajo**. Las secciones están organizadas por etapa:

1. Imports y configuración global (`RANDOM_SEED=42`, `TEST_SIZE=0.2`)
2. Carga del dataset (`synchronized_swimming_aug.csv`)
3. **Etapa 1** — Extracción de 33 landmarks 3D con MediaPipe PoseLandmarker Heavy
4. **Etapa 2** — Cálculo de las 17 características geométricas
5. **Etapa 3** — Entrenamiento del Random Forest y evaluación (accuracy, matriz de confusión, F1)
6. Serialización del modelo, scaler, encoder y resultados en ficheros `.pkl`


> **Nota**: en la primera ejecución, el notebook descarga automáticamente `pose_landmarker_heavy.task` (~25 MB) desde los servidores de Google si no está presente en el directorio. Es necesaria conexión a internet para este paso.
