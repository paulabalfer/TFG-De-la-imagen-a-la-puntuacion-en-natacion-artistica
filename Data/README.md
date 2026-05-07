# Data

Directorio que centraliza el dataset de natación artística utilizado en el proyecto, incluyendo las imágenes originales, las versiones aumentadas, los ficheros de índice que vinculan cada imagen con su etiqueta de clase, y el material de referencia documental.

---

## Contenido

```
Data/
├── Data_process.ipynb                            # Notebook de preprocesado y data augmentation
├── synchronized_swimming.csv                     # Índice del dataset original (263 imágenes)
├── synchronized_swimming_aug.csv                 # Índice del dataset aumentado (6 575 imágenes)
├── Figures-Manual-2022-2025-ALL.pdf              # Manual oficial de figuras de World Aquatics
├── JUDGES SUPPORT_Height Chart Jan 2025.pdf      # Material de apoyo para jueces
├── Images/                                       # Imágenes originales por clase
│   ├── Bent Knee Surface Arch Position/          # 39 imágenes
│   ├── Bent Knee Vertical/                       # 52 imágenes
│   ├── Double Leg Vertical/                      # 50 imágenes
│   ├── Fishtail/                                 # 59 imágenes
│   └── Knight/                                   # 63 imágenes
├── Augmented/                                    # Imágenes generadas por data augmentation
│   ├── Bent Knee Surface Arch Position/          # 975 imágenes
│   ├── Bent Knee Vertical/                       # 1 300 imágenes
│   ├── Double Leg Vertical/                      # 1 250 imágenes
│   ├── Fishtail/                                 # 1 475 imágenes
│   └── Knight/                                   # 1 575 imágenes
└── references/                                   # Material de referencia visual
    ├── positions/                                # 1 fotografía de referencia por clase
    └── punctuation/                              # Diagramas de puntuación y deducciones
```

---

## Dataset

### Clases

El dataset recoge **5 posiciones corporales reglamentarias** de natación artística, definidas por el manual oficial de figuras de World Aquatics:

| Clase | Código BP | Características principales |
|---|---|---|
| `Double Leg Vertical` | BP6 | Ambas piernas juntas, rectas y verticales; tronco sumergido |
| `Fishtail` | BP8 | Una pierna vertical + una pierna recta hacia adelante; espalda recta |
| `Bent Knee Vertical` | BP14c | Una pierna vertical + rodilla contraria flexionada, muslo horizontal |
| `Bent Knee Surface Arch` | BP14d | Espalda arqueada + rodilla flexionada, muslo perpendicular; posición en superficie |
| `Knight` | BP17 | Espalda arqueada + una pierna vertical + una pierna recta hacia atrás |

---

## Ficheros CSV de índice

Ambos ficheros siguen el mismo esquema de dos columnas:

| Columna | Descripción |
|---|---|
| `filepath` | Ruta relativa a la imagen desde la raíz del repositorio |
| `label` | Nombre de la clase (coincide con el nombre del subdirectorio) |

- **`synchronized_swimming.csv`** — lista las imágenes originales de `Images/`.
- **`synchronized_swimming_aug.csv`** — lista las imágenes aumentadas de `Augmented/`.

Estos índices son consumidos directamente por los notebooks del proyecto para cargar y particionar los datos sin depender de la estructura de directorios en tiempo de ejecución.

---

## Notebook de preprocesado: `Data_process.ipynb`

### Etapa 1 — Construcción del índice original

Lectura de las imágenes de `Images/`, verificación de rutas y generación de `synchronized_swimming.csv` con las columnas `filepath` y `label`.

- **Formatos admitidos**: `.jpg`, `.jpeg`, `.png`.
- **Salida**: `synchronized_swimming.csv` (263 entradas).

---

### Etapa 2 — Data augmentation

Para compensar el tamaño reducido del dataset original, se generan **25 variantes por imagen** mediante transformaciones geométricas y fotométricas, multiplicando el conjunto de entrenamiento por un factor de 25.

| Transformación | Configuración |
|---|---|
| Rotación | ±20° |
| Desplazamiento horizontal/vertical | ±10 % de la dimensión |
| Zoom | 85 %–115 % |
| Brillo | 70 %–130 % |
| Volteo horizontal | Activado |
| Volteo vertical | Desactivado (preserva la orientación corporal) |
| Relleno de bordes | `nearest` |

Las imágenes aumentadas se nombran siguiendo el patrón `IMG_<id>_aug<n>.jpg`, donde `<n>` va de 1 a 25.

- **Semilla**: `RANDOM_SEED = 42`.
- **Salida**: directorio `Augmented/` + `synchronized_swimming_aug.csv` (6 575 entradas).

---

## Material de referencia

### `references/positions/`

Contiene una fotografía de referencia por clase (5 imágenes JPG), utilizadas como ejemplos few-shot en el enfoque CLIP del directorio [`Modelos Naïve/`](../Modelos\ Naïve/README.md).

### `references/punctuation/`

Contiene 6 diagramas PNG con los criterios de puntuación y deducción por posición, extraídos del reglamento oficial:

| Fichero | Contenido |
|---|---|
| `Double_leg_vertical_punctuation.png` | Criterios BP6 |
| `Fishtail_punctuation.png` | Criterios BP8 |
| `Bent_knee_vertical_punctuation.png` | Criterios BP14c |
| `Bent_knee_surface_arch_punctuation.png` | Criterios BP14d |
| `Knight_punctuation.png` | Criterios BP17 |
| `Deductions.png` | Tabla general de deducciones |

### PDFs de documentación

- **`Figures-Manual-2022-2025-ALL.pdf`** — Manual oficial de figuras de World Aquatics (2022–2025). Define las especificaciones biomecánicas de cada posición y es la fuente primaria de los criterios de clasificación.
- **`JUDGES SUPPORT_Height Chart Jan 2025.pdf`** — Material de apoyo para jueces con tabla de alturas y referencia visual de posiciones.

---

## Cómo ejecutar

### Lanzar el notebook

Desde la raíz del repositorio:

```bash
jupyter notebook "Data/Data_process.ipynb"
```

O con JupyterLab:

```bash
jupyter lab "Data/Data_process.ipynb"
```

### Orden de ejecución

El notebook es autocontenido. Ejecutar las celdas **en orden de arriba a abajo**:

1. Imports y configuración global 
2. **Etapa 1** — Lectura de `Images/` y generación de `synchronized_swimming.csv`
3. **Etapa 2** — Data augmentation (25 variantes por imagen) y escritura en `Augmented/`
4. Generación de `synchronized_swimming_aug.csv` con el índice del dataset aumentado

> **Nota**: la augmentation de 263 imágenes a 6 575 puede tardar varios minutos. Las imágenes originales deben estar presentes en `Images/` antes de ejecutar.
