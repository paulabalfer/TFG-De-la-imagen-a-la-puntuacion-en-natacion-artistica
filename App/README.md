# App — Interfaz Web Integrada

Directorio que contiene la **aplicación web Gradio** que integra los dos módulos principales del TFG en una única interfaz interactiva: clasificación automática de la posición corporal y puntuación de la calidad de ejecución.

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

### Etapa 1 — Clasificación local (SmolVLM-500M + LoRA)

El módulo `classifier.py` carga el adaptador LoRA entrenado (directorio `Fine-tunning de vLLM pequeño/smolvlm_lora_natacion/mejor_checkpoint`) sobre el modelo base `HuggingFaceTB/SmolVLM-500M-Instruct`.

- **Entrada**: imagen PIL de la nadadora (cualquier tamaño; se normaliza internamente).
- **Mecanismo**: pregunta de elección múltiple con 5 opciones (S, V, D, F, K); se evalúan los logits de las letras de respuesta en la última posición del generador, sin generación libre de texto.
- **Salida**: clase predicha, confianza (probabilidad softmax) y distribución completa de probabilidades sobre las 5 posiciones.
- **Precisión**: 92 % de accuracy en el conjunto de test.
- **Inferencia**: completamente local, sin llamadas a ninguna API externa.

| Clase | Código |
|---|---|
| Bent Knee Surface Arch Position | BP14d |
| Bent Knee Vertical | BP14c |
| Double Leg Vertical | BP6 |
| Fishtail | BP8 |
| Knight | BP17 |

---

### Etapa 2 — Puntuación automática (Claude API)

El módulo `scorer.py` llama a la **Anthropic API** con el mismo sistema de skills estructuradas desarrollado en `Punctuation/`. El prompt de sistema combina tres skills:

1. `scoring-orchestrator` — pipeline general de evaluación y formato de salida.
2. `scoring-common-deductions` — tablas de deducciones comunes D1–D5.
3. Scorer específico de la posición detectada (p.ej. `scoring-bp06-double-leg-vertical`).

Al modelo se le envían **dos imágenes**: la fotografía de la nadadora y la tabla oficial de puntuación por altura de World Aquatics correspondiente a la posición clasificada. La API devuelve un informe de puntuación técnica completo.

> Esta etapa es **opcional**: si no se proporciona una API key de Anthropic, la app muestra únicamente la clasificación.

---

## Interfaz Gradio

La interfaz (`app.py`) se organiza en dos columnas:

**Panel izquierdo (inputs)**
- Carga de fotografía (drag & drop o selector de archivo).
- Campo de contraseña para la Anthropic API key.
- Botón "Clasificar y puntuar".
- Ejemplos rápidos precargados (una imagen por posición, desde `Data/Images/`).

**Panel derecho (outputs)**
- Tarjeta con la posición detectada, código BP y barra de confianza.
- Gráfico de barras con la distribución de probabilidades sobre las 5 clases.
- Pestaña **Puntuación**: informe técnico generado por Claude.
- Pestaña **Tabla de alturas de referencia**: imagen oficial de World Aquatics para la posición detectada.

---

## Cómo ejecutar

### Instalación

```bash
pip install -r App/requirements.txt
```

> Para aceleración GPU con CUDA 12.x, descomentar las líneas correspondientes al final de `requirements.txt`.

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

---

## Dependencias externas necesarias

- **Adaptador LoRA**: `Fine-tunning de vLLM pequeño/smolvlm_lora_natacion/mejor_checkpoint` y `adaptador_lora_final` deben estar presentes (generados al ejecutar el notebook de fine-tuning).
- **Skills de puntuación**: `.agents/skills_punctuation/` (raíz del repositorio) debe contener las carpetas de skills correspondientes.
- **Tablas de referencia**: `Punctuation/references/` debe contener las imágenes PNG de las tablas oficiales de World Aquatics.
- **Anthropic API key**: necesaria únicamente para la puntuación; la clasificación funciona sin ella.
