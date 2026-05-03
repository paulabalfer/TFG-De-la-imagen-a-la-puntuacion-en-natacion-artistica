import json
import glob
import os

splits_dir = os.path.join(os.path.dirname(__file__), "..", "results", "splits")
output_path = os.path.join(os.path.dirname(__file__), "..", "results", "predictions.json")

batch_files = sorted(glob.glob(os.path.join(splits_dir, "predictions_batch_*.json")))

if not batch_files:
    print(f"No batch files found in {splits_dir}")
    exit(1)

all_predictions = []
for path in batch_files:
    with open(path, "r", encoding="utf-8") as f:
        batch = json.load(f)
    all_predictions.extend(batch)
    print(f"  {os.path.basename(path)}: {len(batch)} predictions")

with open(output_path, "w", encoding="utf-8") as f:
    json.dump(all_predictions, f, indent=2, ensure_ascii=False)

print(f"\nMerged {len(batch_files)} files → {len(all_predictions)} total predictions")
print(f"Output: {os.path.abspath(output_path)}")
