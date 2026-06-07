"""
classifier.py — SmolVLM-500M + LoRA inference for artistic swimming position classification.

Loads the fine-tuned adapter (mejor_checkpoint, 92% test accuracy) and exposes a
SmolVLMClassifier class with a single predict() method.
"""
from __future__ import annotations

import torch
import torch.nn.functional as F
from pathlib import Path
from PIL import Image
from transformers import AutoProcessor, AutoModelForImageTextToText
from peft import PeftModel

# Sorted alphabetically — must match the order used during training
CLASSES: list[str] = sorted([
    "Bent Knee Surface Arch Position",
    "Bent Knee Vertical",
    "Double Leg Vertical",
    "Fishtail",
    "Knight",
])
# One-letter abbreviations used in the multiple-choice prompt (S, V, D, F, K)
CHOICE_LABELS: list[str] = ["S", "V", "D", "F", "K"]

# Maximum token length — must match the value used during fine-tuning
MAX_LENGTH = 512

BASE_MODEL_ID = "HuggingFaceTB/SmolVLM-500M-Instruct"


def _build_question() -> str:
    """Build the multiple-choice question exactly as used during fine-tuning."""
    options = "\n".join(f"({CHOICE_LABELS[i]}) {cls}" for i, cls in enumerate(CLASSES))
    labels_str = ", ".join(CHOICE_LABELS[:-1]) + f", or {CHOICE_LABELS[-1]}"
    return (
        "Look at this image carefully. "
        "Which synchronized swimming body position is shown?\n"
        f"{options}\n"
        f"Answer with only the abbreviation ({labels_str}):"
    )


QUESTION = _build_question()


class SmolVLMClassifier:
    """
    Wraps the SmolVLM-500M base model + LoRA adapter.

    Processor is loaded from `processor_dir` (adaptador_lora_final, which has all
    tokenizer/processor configs). Model weights are loaded from `adapter_dir`
    (mejor_checkpoint, the epoch with best validation accuracy).
    """

    def __init__(self, adapter_dir: Path, processor_dir: Path) -> None:
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

        print(f"[Classifier] Device: {self.device}")
        print("[Classifier] Loading processor...")
        self.processor = AutoProcessor.from_pretrained(str(processor_dir))

        print(f"[Classifier] Loading base model {BASE_MODEL_ID}...")
        base = AutoModelForImageTextToText.from_pretrained(
            BASE_MODEL_ID,
            torch_dtype=torch.float32,
            trust_remote_code=True,
        )

        print(f"[Classifier] Applying LoRA adapter from {adapter_dir.name}...")
        self.model = PeftModel.from_pretrained(base, str(adapter_dir))
        self.model.eval().to(self.device)

        # Compute token IDs for each choice letter — same method used in training
        self.choice_token_ids = torch.tensor(
            [self._get_token_id(lbl) for lbl in CHOICE_LABELS],
            device=self.device,
        )
        print("[Classifier] Ready.")

    def _get_token_id(self, label: str) -> int:
        ids = self.processor.tokenizer.encode(label, add_special_tokens=False)
        if not ids:
            ids = self.processor.tokenizer.encode(" " + label, add_special_tokens=False)
        return ids[-1]  # last sub-token = the letter character (handles BPE prefix)

    @torch.no_grad()
    def predict(
        self, image: Image.Image
    ) -> tuple[str, float, dict[str, float]]:
        """
        Classify a single PIL image.

        Returns:
            predicted_class  — one of the 5 position names
            confidence       — softmax probability of the top class
            probs_dict       — {class_name: probability} for all 5 classes
        """
        if image.mode != "RGB":
            image = image.convert("RGB")

        messages = [
            {
                "role": "user",
                "content": [
                    {"type": "image"},
                    {"type": "text", "text": QUESTION},
                ],
            }
        ]
        text = self.processor.apply_chat_template(messages, add_generation_prompt=True)

        enc = self.processor(
            text=text,
            images=[image],
            return_tensors="pt",
            padding="max_length",
            max_length=MAX_LENGTH,
            truncation=True,
        ).to(self.device)

        outputs = self.model(**enc)
        # Logit at the last position predicts the first assistant token
        last_logits = outputs.logits[0, -1, :].float()
        choice_logits = last_logits[self.choice_token_ids]
        probs = F.softmax(choice_logits, dim=-1).cpu().numpy()

        pred_idx = int(probs.argmax())
        return (
            CLASSES[pred_idx],
            float(probs[pred_idx]),
            {cls: float(p) for cls, p in zip(CLASSES, probs)},
        )
