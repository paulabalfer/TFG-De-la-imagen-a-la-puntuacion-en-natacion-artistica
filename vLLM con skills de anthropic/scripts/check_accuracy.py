
import json

TRACES_FILE = 'C:/paula/OTROS/TFG_repo/vLLM con skills de anthropic/data/all_evaluation_traces.json'
LABELS_FILE = 'C:/paula/OTROS/TFG_repo/vLLM con skills de anthropic/data/image_labels.json'

with open(TRACES_FILE, 'r') as f:
    traces = json.load(f)

with open(LABELS_FILE, 'r') as f:
    ground_truth = json.load(f).get('all_labels', {})

correct = 0
total = 0
unknowns = 0

print(f"Analyzing {len(traces)} traces...")

for trace in traces:
    filename = trace['filename']
    prediction = trace['phase4_final_decision']['classification']
    actual = ground_truth.get(filename)

    total += 1

    if prediction == actual:
        correct += 1
    elif prediction == "Unknown":
        unknowns += 1
        print(f"Skipping {filename}: pred={prediction}, actual={actual}")
    else:
        print(f"Mismatch: {filename} -> Pred: {prediction}, Actual: {actual}")

accuracy = (correct / total) * 100 if total > 0 else 0

print(f"\nTotal: {total}")
print(f"Correct: {correct}")
print(f"Unknown/Skipped: {unknowns}")
print(f"Accuracy: {accuracy:.2f}%")
