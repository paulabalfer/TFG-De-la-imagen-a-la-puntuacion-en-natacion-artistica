# Modelos Naïve

Directorio que agrupa los experimentos de clasificación que operan directamente sobre la **imagen completa** de la nadadora. Se denominan *naïve* en el sentido de que no extraen ninguna representación intermedia del cuerpo (como esqueletos o coordenadas); el modelo recibe la imagen en bruto y aprende —o infiere— la clase a partir de los píxeles.

Se implementan cinco enfoques de complejidad creciente dentro del notebook principal, más un notebook complementario de análisis por clase.

---

## Contenido

```
Modelos Naïve/
├── Automatización Natación Artistica_Paula Ballesteros.ipynb   # Notebook principal
└── Modelos_por_análisis_visual_completo.ipynb                  # Análisis visual por clase
```

---

## Enfoques implementados

### 1. CNN con Transfer Learning

Red neuronal convolucional basada en **EfficientNetB3** preentrenada en ImageNet, con fine-tuning supervisado sobre el dataset etiquetado de natación artística.

- **Paradigma**: aprendizaje supervisado con datos aumentados.
- **Entrada**: imagen RGB redimensionada.
- **Salida**: distribución de probabilidad sobre las 5 clases.
- **Motivación**: establecer una línea base sólida de aprendizaje profundo con la que comparar el resto de enfoques.

---

### 2. CLIP Zero-Shot

Clasificación mediante el modelo visión-lenguaje **CLIP** (OpenAI) sin ningún entrenamiento adicional. Las imágenes se comparan con descripciones textuales de cada posición extraídas directamente del reglamento oficial de World Aquatics.

- **Paradigma**: zero-shot, sin ajuste de parámetros.
- **Entrada**: imagen + texto descriptivo por clase.
- **Salida**: clase con mayor similitud coseno entre embedding visual y textual.
- **Motivación**: evaluar hasta qué punto el conocimiento previo de un modelo multimodal generalista es suficiente para la tarea.

---

### 3. CLIP Multi-Prompt

Extensión del enfoque anterior que combina **múltiples descripciones por clase** (definiciones reglamentarias + descripción coloquial), explorando tres estrategias distintas de agregación de embeddings:

1. **Promedio de embeddings** — media de los vectores textuales de cada prompt.
2. **Suma de probabilidades** — promedia las probabilidades finales de cada prompt.
3. **Votación** — elige la clase que obtiene más votos individuales.

- **Motivación**: reducir la sensibilidad a la formulación exacta del prompt y mejorar la robustez de la clasificación zero-shot.

---

### 4. CLIP + Few-Shot con Imágenes de Referencia

Enriquece las descripciones textuales de CLIP con **imágenes de referencia** verificadas de cada clase, incorporando información visual directa como ejemplos (few-shot).

- **Paradigma**: few-shot visual, sin reentrenamiento del modelo base.
- **Entrada**: imagen a clasificar + imágenes de referencia por clase.
- **Motivación**: estudiar si añadir ejemplos visuales explícitos mejora la discriminación en clases confusas.

---

### 5. Grad-CAM — Análisis de Interpretabilidad

Aplicación de **Gradient-weighted Class Activation Mapping (Grad-CAM)** sobre el modelo CLIP para visualizar las regiones de la imagen que mayor influencia tienen en cada predicción.

- **Salida**: mapas de calor superpuestos sobre las imágenes originales (exportados a `Images para redacción/`).
- **Motivación**: aportar explicabilidad al sistema, identificar si el modelo atiende a las regiones corporales relevantes (posición de piernas, arco de espalda) o a artefactos del fondo.

---

## Tecnologías

| Componente | Librería / Herramienta |
|---|---|
| Transfer Learning (CNN) | TensorFlow / Keras, EfficientNetB3 |
| Modelo visión-lenguaje | CLIP (`transformers`, HuggingFace) |
| Procesamiento de imagen | OpenCV, Pillow |
| Cálculo numérico | NumPy, PyTorch |
| Visualización | matplotlib |
| Entorno de ejecución | Jupyter Notebook |

---

## Ejecución

Los notebooks son autocontenidos. Ejecutar las celdas en orden desde la raíz del repositorio con el entorno instalado (`requirements.txt`):

```bash
pip install -r requirements.txt
jupyter notebook "Modelos Naïve/Automatización Natación Artistica_Paula Ballesteros.ipynb"
```

> El notebook carga los datos desde `../Data/synchronized_swimming_aug.csv` por defecto. Asegúrese de que el directorio `Data/` está correctamente estructurado antes de ejecutar. La generación del dataset aumentado se realiza mediante el notebook `Data/Data_process.ipynb`.
