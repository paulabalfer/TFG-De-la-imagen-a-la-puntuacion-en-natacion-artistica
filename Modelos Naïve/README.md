# Modelos Naïve

Directorio que agrupa los experimentos de clasificación que operan directamente sobre la **imagen completa** de la nadadora. Se denominan *naïve* en el sentido de que no extraen ninguna representación intermedia del cuerpo (los modelos se presentan en su forma básica/elemental); el modelo recibe la imagen en bruto y aprende —o infiere— la clase a partir de los píxeles.

Se implementan cinco enfoques de complejidad creciente dentro de un único notebook.

---

## Contenido

```
Modelos Naïve/
└── Modelos_por_análisis_visual_completo.ipynb   # Notebook con los 5 enfoques
```

---

## Enfoques implementados

### 1. CNN con Transfer Learning

Red neuronal convolucional basada en **EfficientNetB3** preentrenada en ImageNet, con fine-tuning supervisado sobre el dataset etiquetado.

- **Paradigma**: aprendizaje supervisado con datos aumentados.
- **Entrada**: imagen RGB redimensionada a 300×300 px.
- **Salida**: distribución de probabilidad sobre las 5 clases.
- **Dataset**: 6 575 imágenes aumentadas — train 4 749 / val 839 / test 987.
- **Motivación**: establecer una línea base sólida de aprendizaje profundo con la que comparar el resto de enfoques.

---

### 2. CLIP Zero-Shot

Clasificación mediante el modelo visión-lenguaje **CLIP** (*OpenAI*) sin ningún entrenamiento adicional. Las imágenes se comparan con descripciones textuales de cada posición extraídas directamente del reglamento oficial de *World Aquatics*.

- **Paradigma**: zero-shot, sin ajuste de parámetros.
- **Entrada**: imagen + texto descriptivo por clase (una definición reglamentaria por posición).
- **Salida**: clase con mayor similitud coseno entre embedding visual y textual.
- **Motivación**: evaluar hasta qué punto el conocimiento previo de un modelo multimodal generalista es suficiente para la tarea.

---

### 3. CLIP Multi-Prompt

Extensión del enfoque anterior que combina **múltiples descripciones por clase** (definición reglamentaria + descripción coloquial), explorando tres estrategias de agregación: ***Ensemble Mean***, ***Ensemble Max***, ***Concatenación***.

- **Motivación**: reducir la sensibilidad a la formulación exacta del prompt y mejorar la robustez de la clasificación zero-shot.

---

### 4. CLIP + Few-Shot con Imágenes de Referencia

Enriquece las descripciones textuales de CLIP con **imágenes de referencia** verificadas de cada clase (extraídas del reglamento), incorporando información visual directa como ejemplos few-shot.

- **Paradigma**: few-shot visual, sin reentrenamiento del modelo base.
- **Entrada**: imagen a clasificar + imágenes de referencia por clase + definiciones textuales.
- **Motivación**: estudiar si añadir ejemplos visuales explícitos mejora la discriminación en clases confusas.

---

### 5. Grad-CAM — Análisis de Interpretabilidad

Aplicación de **Gradient-weighted Class Activation Mapping (Grad-CAM)** sobre el modelo CLIP para visualizar las regiones de la imagen que mayor influencia tienen en cada predicción.

- **Entrada**: imágenes originales (no aumentadas) — 5 muestras representativas por posición.
- **Salida**: mapas de calor superpuestos sobre las imágenes originales.
- **Motivación**: aportar explicabilidad al sistema e identificar si el modelo atiende a las regiones corporales relevantes (posición de piernas, arco de espalda) o a artefactos del fondo.

---

## Cómo ejecutar

### Lanzar el notebook

Desde la raíz del repositorio:

```bash
jupyter notebook "Modelos Naïve/Modelos_por_análisis_visual_completo.ipynb"
```

O con JupyterLab:

```bash
jupyter lab "Modelos Naïve/Modelos_por_análisis_visual_completo.ipynb"
```

### Orden de ejecución

El notebook es autocontenido. Ejecutar las celdas **en orden de arriba a abajo**. Las secciones están organizadas por enfoque:

1. Imports y configuración global
2. Carga del dataset (`synchronized_swimming_aug.csv`)
3. **Enfoque 1** — CNN EfficientNetB3 (entrenamiento + evaluación)
4. **Enfoque 2** — CLIP Zero-Shot (una definición por clase)
5. **Enfoque 3** — CLIP Multi-Prompt (7 definiciones por clase, 3 estrategias)
6. **Enfoque 4** — CLIP Few-Shot con imágenes de referencia
7. **Enfoque 5** — Grad-CAM sobre imágenes de ejemplo

> **Nota**: el entrenamiento de la CNN (Enfoque 1) puede tardar varios minutos si se ejecuta en CPU. Se recomienda disponer de GPU o reducir `NUM_EPOCHS` para pruebas rápidas.
