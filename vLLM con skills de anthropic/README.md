# vLLM con Skills de Anthropic

Directorio que implementa la clasificación de posiciones de natación artística mediante **Claude Sonnet como modelo de visión**, sin ningún entrenamiento ni fine-tuning. La clasificación se realiza a través de prompts estructurados implementados como *skills* de Claude Code, que codifican el conocimiento experto de los árbitros de World Aquatics.

---

## Contenido

```
vLLM con skills de anthropic/
├── README.md              # Este fichero
├── all_files.txt          # Lista completa de imágenes del dataset aumentado a clasificar
└── processed_files.txt    # Registro de imágenes ya procesadas (para reanudar ejecuciones)
```

Las *skills* de clasificación se encuentran en el directorio raíz del repositorio, bajo `.claude/skills/`:

```
.claude/skills/
├── natacion-classifier/              # Orquestador — evalúa las 5 posiciones y decide la clase
├── natacion-bp06-double-leg-vertical/   # Scorer específico para BP6
├── natacion-bp08-fishtail/              # Scorer específico para BP8
├── natacion-bp14c-bent-knee-vertical/   # Scorer específico para BP14c
├── natacion-bp14d-bent-knee-surface-arch/ # Scorer específico para BP14d
└── natacion-bp17-knight/                # Scorer específico para BP17
```

---

## Las 5 Posiciones

| # | Posición | Código BP | Rasgo diferenciador |
|---|---|---|---|
| 1 | Double Leg Vertical | BP6 | Ambas piernas juntas, rectas y verticales |
| 2 | Fishtail | BP8 | Una pierna vertical + una pierna recta hacia ADELANTE, espalda recta |
| 3 | Bent Knee Vertical | BP14c | Una pierna vertical + rodilla contraria FLEXIONADA, muslo horizontal, espalda recta |
| 4 | Bent Knee Surface Arch | BP14d | Espalda ARQUEADA + rodilla flexionada, muslo perpendicular, en superficie |
| 5 | Knight | BP17 | Espalda ARQUEADA + una pierna vertical + una pierna recta hacia ATRÁS |

### Árbol de decisión

```
1. ¿Cuántas direcciones distintas tienen las piernas?
   +-- UNA (ambas juntas) ---------> Double Leg Vertical (BP6)
   +-- DOS (piernas separadas) ----> Paso 2

2. ¿Alguna rodilla está FLEXIONADA?
   +-- SÍ --> Paso 3
   +-- NO --> Paso 4

3. ¿La espalda está ARQUEADA?
   +-- SÍ --> Bent Knee Surface Arch (BP14d)
   +-- NO --> Bent Knee Vertical (BP14c)

4. ¿La espalda está ARQUEADA?
   +-- SÍ --> Knight (BP17)
   +-- NO --> Fishtail (BP8)
```

---

## Arquitectura de las Skills

Cada skill de posición contiene seis componentes:

1. **Definición oficial** — especificación del Manual de Figuras de World Aquatics.
2. **Scratchpad visual** — procedimiento de evaluación de 7 pasos para observación sistemática.
3. **Lista de exclusión** — descalificadores estrictos (cualquiera activado → puntuación 0).
4. **Aprendizaje contrastivo** — tablas comparativas para cada par de posiciones confundibles.
5. **Rúbrica de puntuación** — escala 0-5 con criterios precisos por nivel.
6. **Text shots** — descripciones textuales detalladas de imágenes de entrenamiento verificadas (equivalente a few-shot sin consumir tokens de visión adicionales).

### Orquestador (`natacion-classifier`)

La skill maestra puntúa la imagen contra las **5 posiciones** y aplica reglas de agregación:

- **Regla 1**: Todas las puntuaciones ≤ 1 → INCIERTO.
- **Regla 2**: Ganador claro (≥ 2 puntos de ventaja) → clasificar.
- **Regla 3**: Ganador moderado (≥ 1 punto de ventaja) → clasificar.
- **Regla 4**: Empate → desempate por número de exclusiones, heurísticas de pares confusos y sesgo anti-Fishtail.

---

## Ficheros de seguimiento

- **`all_files.txt`** — lista completa de nombres de imagen del dataset aumentado pendientes de clasificar. Permite lanzar la clasificación en lotes sobre el conjunto de datos completo.
- **`processed_files.txt`** — registro acumulativo de imágenes ya clasificadas. Permite reanudar una ejecución interrumpida sin reprocesar imágenes.

---

## Resultados

### Conjunto de desarrollo (train) — usado para refinar las skills

| Clase | Correctas | Total | Accuracy |
|---|---|---|---|
| Double Leg Vertical | 3 | 3 | 100 % |
| Fishtail | 3 | 3 | 100 % |
| Bent Knee Vertical | 3 | 3 | 100 % |
| Bent Knee Surface Arch | 3 | 3 | 100 % |
| Knight | 3 | 3 | 100 % |
| **Total** | **15** | **15** | **100 %** |

### Conjunto de test (held-out) — evaluación final

| Clase | Correctas | Total | Accuracy |
|---|---|---|---|
| Double Leg Vertical | 3 | 3 | 100 % |
| Fishtail | 3 | 3 | 100 % |
| Bent Knee Vertical | 3 | 3 | 100 % |
| Bent Knee Surface Arch | 3 | 3 | 100 % |
| Knight | 2 | 3 | 66.7 % |
| **Total** | **14** | **15** | **93.3 %** |

### Análisis del error

**1 error de clasificación**: una imagen de Knight fue clasificada como Bent Knee Surface Arch. Ambas posiciones comparten espalda arqueada; el rasgo diferenciador es si la pierna no-vertical está **recta** (Knight) o **flexionada en la rodilla** (BKSA). El modelo percibió una flexión de rodilla donde la pierna era recta, activando la clasificación BKSA. La frontera Knight / BKSA es el par más difícil del dataset.

---

## Metodología

1. **Estudio de materiales de referencia** — lectura del Manual de Figuras de World Aquatics y material de jueces para entender la biomecánica de cada posición.
2. **Creación de skills con text shots** — construcción de prompts estructurados con conocimiento experto, usando descripciones textuales de imágenes de entrenamiento como ejemplos few-shot.
3. **Evaluación en el conjunto de desarrollo** — clasificación de las 15 imágenes de entrenamiento con agentes Claude Sonnet en paralelo.
4. **Iteración sobre las skills** — refinamiento de prompts hasta alcanzar 100 % de accuracy en desarrollo.
5. **Evaluación final en test** — clasificación del conjunto held-out una única vez, sin iteración posterior (93.3 %).

---

## Modelo y herramientas

- **Modelo de clasificación**: Claude Sonnet 4.5 (`claude-sonnet-4-5-20250929`) con capacidades de visión multimodal.
- **Método de evaluación**: cada imagen se lee con la herramienta `Read` de Claude (visión) y se clasifica con la skill orquestadora.
- **Paralelización**: 5 subagentes concurrentes (uno por clase) para evaluación eficiente en lote.
- **Entorno**: Claude Code CLI / SDK de Anthropic.
