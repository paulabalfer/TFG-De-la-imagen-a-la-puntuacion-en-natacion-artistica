# App — Interfaz Web Integrada

Directorio que contiene la **aplicación web Gradio** que integra los dos módulos principales del TFG en una única interfaz interactiva: clasificación automática de la posición corporal y puntuación de la calidad de ejecución. El pipeline es completamente secuencial — clasificación local primero, puntuación vía API después (opcional).

---

## Contenido

```
App/
├── app.py              # Punto de entrada: interfaz Gradio y pipeline principal
├── classifier.py       # Inferencia local con SmolVLM-500M + LoRA
├── scorer.py           # Puntuación automática via Anthropic API (Claude)
└── requirements.txt    # Dependencias específicas de la app
```

---

## Pipeline

```
imagen de la nadadora
        │
        ▼
  classifier.py
  SmolVLM-500M + LoRA
  (inferencia local, sin API)
        │
        ├─── posición detectada + confianza + distribución de probabilidades
        │
        ▼
   scorer.py  (opcional — requiere API key)
   Claude API + skills de puntuación
   (2 imágenes: nadadora + tabla oficial de alturas)
        │
        └─── informe de puntuación técnica 0–10
```

---

## Módulos

### `classifier.py` — Clasificación local

Carga el modelo `HuggingFaceTB/SmolVLM-500M-Instruct` con el adaptador LoRA entrenado y expone la clase `SmolVLMClassifier`.

---

### `scorer.py` — Puntuación automática

Construye el prompt de sistema a partir de tres skills de `.agents/skills_punctuation/`, envía dos imágenes a la Anthropic API y devuelve el informe de puntuación.

El prompt de sistema se compone de tres skills concatenadas:
1. `scoring-orchestrator` — pipeline general y formato de salida.
2. `scoring-common-deductions` — tablas de deducciones comunes D1–D5.
3. Scorer específico de la posición (p.ej. `scoring-bp14d-bent-knee-surface-arch`).

Al modelo se le envían **dos imágenes** codificadas en base64 (JPEG, calidad 92):
- La fotografía de la nadadora.
- La tabla oficial de puntuación por altura de World Aquatics correspondiente a la posición.

---

## Dependencias externas

La app espera encontrar los siguientes recursos en la raíz del repositorio:

| Recurso | Ruta | Requerido para |
|---|---|---|
| Pesos LoRA (mejor epoch) | `Fine-tuning de vLLM pequeño/smolvlm_lora_natacion/mejor_checkpoint/` | Clasificación (obligatorio) |
| Configuración del procesador | `Fine-tuning de vLLM pequeño/smolvlm_lora_natacion/adaptador_lora_final/` | Clasificación (obligatorio) |
| Skills de puntuación | `.agents/skills_punctuation/` | Puntuación (obligatorio si se usa API key) |
| Tablas de alturas PNG | `Data/references/scoring/` | Puntuación (obligatorio si se usa API key) |
| Imágenes de ejemplo | `Data/Images/` | Ejemplos rápidos en la interfaz (opcional) |

---

## Cómo ejecutar

### Instalación

```bash
pip install -r App/requirements.txt
```

### Lanzar la app

Desde la raíz del repositorio:

```bash
python App/app.py
```

La app carga el clasificador al arrancar (puede tardar 30–60 segundos en CPU la primera vez). Una vez lista, abrir en el navegador:

```
http://127.0.0.1:7860
```

### Uso

1. Subir una fotografía de una nadadora en una posición de las 5 clases soportadas.
2. *(Opcional)* Introducir una Anthropic API key para activar la puntuación automática.
3. Pulsar **Clasificar y puntuar**.

La clasificación siempre se ejecuta localmente. La puntuación solo se ejecuta si se proporciona API key; en caso contrario, la app muestra únicamente la clasificación y la tabla de alturas correspondiente.
