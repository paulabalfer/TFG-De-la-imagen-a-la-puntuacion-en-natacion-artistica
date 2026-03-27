# Data

Directorio que centraliza el dataset de natación artística utilizado en el proyecto, incluyendo las imágenes originales, las versiones aumentadas y los ficheros de índice que vinculan cada imagen con su etiqueta de clase.

---

## Contenido

```
Data/
├── synchronized_swimming.csv       # Índice del dataset original
├── synchronized_swimming_aug.csv   # Índice del dataset aumentado
├── Data_process.ipynb              # Notebook de preprocesado y data augmentation
├── Figures-Manual-2022-2025-ALL.pdf          # Manual oficial de figuras de World Aquatics
├── JUDGES SUPPORT_Height Chart Jan 2025.pdf  # Material de apoyo para jueces
├── Fotos/                          # Imágenes originales por clase (no versionadas en el repo)
│   ├── Bent Knee Surface Arch Position/
│   ├── Bent Knee Vertical/
│   ├── Double Leg Vertical/
│   ├── Fishtail/
│   └── Knight/
└── Augmented/                      # Imágenes generadas por data augmentation
    ├── Bent Knee Surface Arch Position/
    ├── Bent Knee Vertical/
    ├── Double Leg Vertical/
    ├── Fishtail/
    └── Knight/
```

---

## Descripción del dataset

### Clases

El dataset recoge **5 posiciones corporales reglamentarias** de natación artística, definidas por el manual oficial de figuras de World Aquatics:

| Clase | Código BP | Características principales |
|---|---|---|
| `Double Leg Vertical` | BP6 | Ambas piernas juntas, rectas y verticales; tronco sumergido |
| `Fishtail` | BP8 | Una pierna vertical + una pierna recta hacia adelante; espalda recta |
| `Bent Knee Vertical` | BP14c | Una pierna vertical + rodilla contraria flexionada, muslo horizontal; espalda recta |
| `Bent Knee Surface Arch` | BP14d | Espalda arqueada + rodilla flexionada, muslo perpendicular; posición en superficie |
| `Knight` | BP17 | Espalda arqueada + una pierna vertical + una pierna recta hacia atrás |

### Volumen

| Subconjunto | Imágenes |
|---|---|
| Dataset original (`Fotos/`) | ~264 |
| Dataset aumentado (`Augmented/`) | ~6 600 |

Las imágenes originales fueron recopiladas manualmente. El directorio `Fotos/` no se incluye en el repositorio por su tamaño; debe añadirse localmente siguiendo la misma estructura de carpetas por clase.

---

## Ficheros CSV de índice

Ambos ficheros siguen el mismo esquema de dos columnas:

| Columna | Descripción |
|---|---|
| `filepath` | Ruta relativa a la imagen desde la raíz del repositorio |
| `label` | Nombre de la clase (coincide con el nombre del subdirectorio) |

- **`synchronized_swimming.csv`** — lista las imágenes originales de `Fotos/`.
- **`synchronized_swimming_aug.csv`** — lista las imágenes aumentadas de `Augmented/`.

Estos índices son consumidos directamente por los notebooks del proyecto para cargar y particionar los datos sin depender de la estructura de directorios en tiempo de ejecución.

---

## Notebook de preprocesado: `Data_process.ipynb`

Notebook que implementa la exploración inicial del dataset y la generación del conjunto aumentado. Sus etapas principales son:

1. **Carga y verificación** — lectura del CSV original, comprobación de rutas y distribución de clases.
2. **Data augmentation** — aplicación de transformaciones geométricas y fotométricas a cada imagen original para generar 25 variantes derivadas.
3. **Exportación** — escritura de las imágenes aumentadas en `Augmented/` y generación de `synchronized_swimming_aug.csv`.

---

## Data Augmentation

Para compensar el tamaño reducido del dataset original (~264 imágenes), se aplicaron transformaciones geométricas y fotométricas que generan **25 versiones derivadas por cada imagen original**, multiplicando el conjunto de entrenamiento por un factor de 25.

Las transformaciones aplicadas incluyen:

- **Rotaciones** en distintos ángulos
- **Volteos** horizontales y verticales
- **Ajustes de brillo**
- **Ajustes de contraste**

Las imágenes aumentadas se nombran siguiendo el patrón `IMG_<id>_aug<n>.jpg`, donde `<n>` va de 1 a 25.

---

## Documentación de referencia

- **`Figures-Manual-2022-2025-ALL.pdf`** — Manual oficial de figuras de World Aquatics (2022-2025). Define las especificaciones biomecánicas de cada posición y es la fuente primaria de los criterios de clasificación.
- **`JUDGES SUPPORT_Height Chart Jan 2025.pdf`** — Material de apoyo para jueces con la tabla de alturas y referencia visual de posiciones.
