#!/usr/bin/env python3
"""Generate ground truth file from all_files.txt + image_labels.json."""
import json
import math

BASE = "C:/paula/OTROS/TFG_repo/vLLM con skills de anthropic"
BATCH_SIZE = 20

# Load ground truth labels
with open(f"{BASE}/data/image_labels.json") as f:
    labels_data = json.load(f)
all_labels = labels_data["all_labels"]

# Load filenames to evaluate
with open(f"{BASE}/all_files.txt") as f:
    filenames = [line.strip() for line in f if line.strip()]

# Look up label for each file
missing = []
items = []
for fname in filenames:
    if fname in all_labels:
        items.append({"filename": fname, "label": all_labels[fname]})
    else:
        missing.append(fname)
        print(f"WARNING: no label found for {fname}")

# Split into batches
n_batches = math.ceil(len(items) / BATCH_SIZE)
batches = [items[i * BATCH_SIZE:(i + 1) * BATCH_SIZE] for i in range(n_batches)]

# Save
out_path = f"{BASE}/data/eval_batches_generated.json"
with open(out_path, "w") as f:
    json.dump(batches, f, indent=2)

# Class distribution
from collections import Counter
dist = Counter(item["label"] for item in items)

print(f"\nGround truth generado: {len(items)} imagenes en {n_batches} batches")
print(f"Guardado en: data/eval_batches_generated.json")
if missing:
    print(f"\nSin etiqueta ({len(missing)} imagenes): {missing}")
print("\nDistribucion de clases:")
for cls, count in sorted(dist.items()):
    print(f"  {cls}: {count}")
