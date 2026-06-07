"""
app.py — Gradio web app for artistic swimming position classification and scoring.

Pipeline:
  1. Upload a swimmer photograph.
  2. SmolVLM-500M + LoRA classifies the position (local inference, 92% test accuracy).
  3. Claude API scores the execution using the official World Aquatics rules (optional).

Run:
    python app.py
    # then open http://127.0.0.1:7860
"""
from __future__ import annotations

import sys
from pathlib import Path
import gradio as gr
from PIL import Image

# Resolve paths relative to this file so the app works from any working directory
_APP_DIR = Path(__file__).parent
_REPO_ROOT = _APP_DIR.parent
_ADAPTER_BEST = _REPO_ROOT / "Fine-tunning de vLLM pequeño" / "smolvlm_lora_natacion" / "mejor_checkpoint"
_ADAPTER_PROC = _REPO_ROOT / "Fine-tunning de vLLM pequeño" / "smolvlm_lora_natacion" / "adaptador_lora_final"

sys.path.insert(0, str(_APP_DIR))
from classifier import SmolVLMClassifier
from scorer import score_position, get_chart_image, POSITION_META

# ---------------------------------------------------------------------------
# Load the classifier once at startup (expensive — ~30–60 s on CPU)
# ---------------------------------------------------------------------------
print("=" * 60)
print(" Natación Artística — cargando clasificador SmolVLM...")
print("=" * 60)
_classifier = SmolVLMClassifier(adapter_dir=_ADAPTER_BEST, processor_dir=_ADAPTER_PROC)
print("Clasificador listo. Iniciando interfaz Gradio...\n")

# ---------------------------------------------------------------------------
# CSS
# ---------------------------------------------------------------------------
_CSS = """
.title-block { text-align: center; padding: 0.6rem 0 0.2rem 0; }
.title-block h1 { font-size: 1.75rem; margin: 0; }
.title-block p  { color: #555; margin: 0.2rem 0 0 0; }
.result-card    { border-left: 4px solid #2563eb; padding: 0.7rem 1rem;
                  background: #f0f6ff; border-radius: 6px; margin-bottom: 0.5rem; }
.score-block    { font-family: monospace; white-space: pre-wrap; font-size: 0.88rem;
                  background: #1e1e2e; color: #cdd6f4; padding: 1rem;
                  border-radius: 8px; max-height: 480px; overflow-y: auto; }
"""

# ---------------------------------------------------------------------------
# Pipeline function
# ---------------------------------------------------------------------------
try:
    from anthropic import AuthenticationError as _AnthropicAuthError
except ImportError:
    _AnthropicAuthError = Exception  # type: ignore[assignment,misc]


def run_pipeline(
    image: Image.Image | None,
    api_key: str,
    progress: gr.Progress = gr.Progress(),
) -> tuple:
    if image is None:
        empty = "_Sube una fotografía y pulsa **Clasificar y puntuar**._"
        return empty, {}, empty, None

    # Step 1 — classify
    progress(0.1, desc="Clasificando posición…")
    position, confidence, probs = _classifier.predict(image)
    meta = POSITION_META[position]

    # Build classification HTML card
    confidence_bar = "█" * int(confidence * 20) + "░" * (20 - int(confidence * 20))
    cls_md = (
        f'<div class="result-card">'
        f"<strong>Posición detectada:</strong> {position} ({meta['code']})<br>"
        f"<strong>Confianza:</strong> {confidence:.1%} &nbsp; <code>{confidence_bar}</code>"
        f"</div>"
    )

    # Step 2 — height chart
    progress(0.5, desc="Cargando tabla de referencia…")
    chart_img = get_chart_image(position)

    # Step 3 — score (optional)
    if api_key and api_key.strip():
        progress(0.7, desc="Puntuando con Claude API…")
        try:
            score_text = score_position(image, position, api_key.strip())
        except _AnthropicAuthError as exc:
            score_text = f"**Error de autenticación:** API key inválida o sin permisos.\n\n`{exc}`"
        except Exception as exc:
            score_text = f"**Error al puntuar:**\n\n```\n{exc}\n```"
    else:
        score_text = (
            "_Introduce una **Anthropic API key** en el panel izquierdo para obtener la "
            "puntuación automática basada en las reglas oficiales de World Aquatics._"
        )

    progress(1.0, desc="Listo.")
    return cls_md, probs, score_text, chart_img


# ---------------------------------------------------------------------------
# Gradio UI
# ---------------------------------------------------------------------------
with gr.Blocks(
    title="Natación Artística — Clasificador y Puntuador",
    theme=gr.themes.Soft(primary_hue="blue", neutral_hue="slate"),
    css=_CSS,
) as demo:

    # Header
    gr.HTML("""
    <div class="title-block">
      <h1>Natación Artística Sincronizada</h1>
      <p>Clasificación automática de figuras + puntuación oficial World Aquatics 2022–2025</p>
    </div>
    """)

    with gr.Row(equal_height=False):

        # ── Left column: inputs ──────────────────────────────────────────
        with gr.Column(scale=1, min_width=290):
            img_input = gr.Image(
                type="pil",
                label="Fotografía del nadador",
                height=320,
            )
            api_key_input = gr.Textbox(
                label="Anthropic API Key",
                type="password",
                placeholder="sk-ant-api03-...",
                info="Opcional. Solo necesaria para la puntuación.",
            )
            run_btn = gr.Button(
                "Clasificar y puntuar",
                variant="primary",
                size="lg",
            )

            gr.Markdown("""
---
**Modelo de clasificación**
SmolVLM-500M + LoRA (92 % accuracy)
Inferencia local · sin API

**Modelo de puntuación**
Claude API · reglas World Aquatics
Requiere API key de Anthropic
""")

        # ── Right column: outputs ─────────────────────────────────────────
        with gr.Column(scale=2):

            cls_output = gr.HTML(
                '<p style="color:#888">Sube una imagen y pulsa el botón.</p>'
            )

            probs_output = gr.Label(
                label="Probabilidades por posición",
                num_top_classes=5,
            )

            with gr.Tabs():
                with gr.Tab("Puntuación"):
                    score_output = gr.Markdown(
                        "_La puntuación aparecerá aquí tras clasificar._"
                    )
                with gr.Tab("Tabla de alturas de referencia"):
                    chart_output = gr.Image(
                        label="Tabla oficial de puntuación por altura",
                        interactive=False,
                        height=420,
                    )

    # ── Ejemplos rápidos ──────────────────────────────────────────────────
    _example_dir = _REPO_ROOT / "Data" / "Images"
    _examples: list[list] = []
    for _pos_dir in sorted(_example_dir.iterdir()):
        if _pos_dir.is_dir():
            imgs = sorted(_pos_dir.glob("*.JPG")) + sorted(_pos_dir.glob("*.jpg"))
            if imgs:
                _examples.append([str(imgs[0]), ""])

    if _examples:
        gr.Examples(
            examples=_examples,
            inputs=[img_input, api_key_input],
            label="Ejemplos rápidos (una imagen por posición)",
            cache_examples=False,
        )

    # ── Bind ──────────────────────────────────────────────────────────────
    run_btn.click(
        fn=run_pipeline,
        inputs=[img_input, api_key_input],
        outputs=[cls_output, probs_output, score_output, chart_output],
    )

# ---------------------------------------------------------------------------
if __name__ == "__main__":
    demo.launch(
        server_name="127.0.0.1",
        server_port=7860,
        share=False,
        show_error=True,
    )
