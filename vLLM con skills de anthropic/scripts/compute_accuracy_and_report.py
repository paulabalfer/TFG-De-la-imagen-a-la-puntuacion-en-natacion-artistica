#!/usr/bin/env python3
"""Compute accuracy metrics and generate comprehensive HTML report."""
import json
from collections import defaultdict
from datetime import datetime

BASE = "C:/paula/OTROS/TFG_repo/vLLM con skills de anthropic"

# Load predictions  (formato: [{filename, classification, confidence?}, ...])
with open(f"{BASE}/results/predictions.json") as f:
    pred_list = json.load(f)

predictions = {}
for item in pred_list:
    predictions[item["filename"]] = item["classification"]

# Load ground truth from eval_batches_generated.json
with open(f"{BASE}/data/eval_batches_generated.json") as f:
    eval_batches = json.load(f)

ground_truth = {}
for batch in eval_batches:
    for item in batch:
        ground_truth[item["filename"]] = item["label"]

# Verify coverage
n_pred = len(predictions)
n_gt = len(ground_truth)
missing = set(ground_truth.keys()) - set(predictions.keys())
extra   = set(predictions.keys()) - set(ground_truth.keys())
assert len(missing) == 0, f"Faltan predicciones para: {missing}"
if extra:
    print(f"AVISO: {len(extra)} predicciones sin ground truth (se ignoraran): {extra}")
    for k in extra:
        del predictions[k]

print(f"Imagenes a evaluar: {len(ground_truth)}  |  Predicciones cargadas: {n_pred}")

# Class names in display order
CLASSES = ["Double Leg Vertical", "Fishtail", "Bent Knee Vertical",
           "Bent Knee Surface Arch", "Knight"]
SHORT = {"Double Leg Vertical": "DLV", "Fishtail": "FT", "Bent Knee Vertical": "BKV",
         "Bent Knee Surface Arch": "BKSA", "Knight": "KN"}
CODES = {"Double Leg Vertical": "BP6", "Fishtail": "BP8", "Bent Knee Vertical": "BP14c",
         "Bent Knee Surface Arch": "BP14d", "Knight": "BP17"}

# Compute confusion matrix and metrics
confusion = defaultdict(lambda: defaultdict(int))
correct = 0
errors = []

for filename in sorted(ground_truth.keys()):
    true_label = ground_truth[filename]
    pred_label = predictions[filename]
    confusion[true_label][pred_label] += 1
    if true_label == pred_label:
        correct += 1
    else:
        errors.append({"filename": filename, "true": true_label, "predicted": pred_label})

total = len(ground_truth)
overall_accuracy = correct / total

# Per-class metrics
class_metrics = {}
for cls in CLASSES:
    tp = confusion[cls][cls]
    fn = sum(confusion[cls][p] for p in CLASSES if p != cls)
    fp = sum(confusion[t][cls] for t in CLASSES if t != cls)
    support = tp + fn
    precision = tp / (tp + fp) if (tp + fp) > 0 else 0
    recall = tp / support if support > 0 else 0
    f1 = 2 * precision * recall / (precision + recall) if (precision + recall) > 0 else 0
    class_metrics[cls] = {
        "precision": precision, "recall": recall, "f1": f1,
        "support": support, "correct": tp, "errors": fn
    }

# Save results JSON
results = {
    "date": datetime.now().isoformat(),
    "total_images": total,
    "correct": correct,
    "errors_count": len(errors),
    "overall_accuracy": round(overall_accuracy, 4),
    "class_metrics": {cls: {k: round(v, 4) if isinstance(v, float) else v
                            for k, v in m.items()} for cls, m in class_metrics.items()},
    "confusion_matrix": {t: dict(confusion[t]) for t in CLASSES},
    "error_details": errors,
    "per_image_results": [
        {"filename": fn, "true_label": ground_truth[fn], "predicted": predictions[fn],
         "correct": ground_truth[fn] == predictions[fn]}
        for fn in sorted(ground_truth.keys())
    ]
}

with open(f"{BASE}/results/results.json", "w") as f:
    json.dump(results, f, indent=2)

# Confusion pair analysis
confusion_pairs = defaultdict(int)
for e in errors:
    pair = f"{SHORT[e['true']]} -> {SHORT[e['predicted']]}"
    confusion_pairs[pair] += 1
top_pairs = sorted(confusion_pairs.items(), key=lambda x: -x[1])

# Print summary
print(f"\nOverall Accuracy: {overall_accuracy:.1%} ({correct}/{total})")
print(f"\nPer-class metrics:")
for cls in CLASSES:
    m = class_metrics[cls]
    print(f"  {SHORT[cls]:>4}: P={m['precision']:.3f} R={m['recall']:.3f} F1={m['f1']:.3f} ({m['correct']}/{m['support']})")
print(f"\nTop confusion pairs:")
for pair, count in top_pairs[:10]:
    print(f"  {pair}: {count}")
print(f"\nTotal errors: {len(errors)}")

# Generate HTML Report
confusion_rows = ""
for true_cls in CLASSES:
    cells = ""
    for pred_cls in CLASSES:
        val = confusion[true_cls][pred_cls]
        is_diag = true_cls == pred_cls
        bg = "#2d5a27" if is_diag and val > 0 else ("#5a2727" if val > 0 and not is_diag else "#1a1a2e")
        cells += f'<td style="background:{bg};text-align:center;padding:8px;font-weight:{"bold" if is_diag else "normal"}">{val}</td>'
    total_row = class_metrics[true_cls]["support"]
    acc = class_metrics[true_cls]["recall"]
    cells += f'<td style="text-align:center;padding:8px;font-weight:bold">{total_row}</td>'
    cells += f'<td style="text-align:center;padding:8px;font-weight:bold">{acc:.1%}</td>'
    confusion_rows += f'<tr><td style="padding:8px;font-weight:bold">{SHORT[true_cls]} ({CODES[true_cls]})</td>{cells}</tr>\n'

col_totals = ""
for pred_cls in CLASSES:
    t = sum(confusion[true_cls][pred_cls] for true_cls in CLASSES)
    col_totals += f'<td style="text-align:center;padding:8px;font-weight:bold;border-top:2px solid #444">{t}</td>'
col_totals_row = f'<tr><td style="padding:8px;font-weight:bold">Total</td>{col_totals}<td style="text-align:center;padding:8px;font-weight:bold;border-top:2px solid #444">{total}</td><td style="text-align:center;padding:8px;font-weight:bold;border-top:2px solid #444">{overall_accuracy:.1%}</td></tr>'

metrics_rows = ""
for cls in CLASSES:
    m = class_metrics[cls]
    metrics_rows += f'''<tr>
        <td style="padding:8px;font-weight:bold">{SHORT[cls]} ({CODES[cls]})</td>
        <td style="padding:8px">{cls}</td>
        <td style="text-align:center;padding:8px">{m['support']}</td>
        <td style="text-align:center;padding:8px">{m['correct']}</td>
        <td style="text-align:center;padding:8px">{m['errors']}</td>
        <td style="text-align:center;padding:8px;font-weight:bold">{m['recall']:.1%}</td>
        <td style="text-align:center;padding:8px">{m['precision']:.3f}</td>
        <td style="text-align:center;padding:8px">{m['f1']:.3f}</td>
    </tr>\n'''

error_rows = ""
for e in sorted(errors, key=lambda x: x['filename']):
    error_rows += f'''<tr>
        <td style="padding:6px">{e['filename']}</td>
        <td style="padding:6px">{SHORT[e['true']]} ({e['true']})</td>
        <td style="padding:6px">{SHORT[e['predicted']]} ({e['predicted']})</td>
    </tr>\n'''

pairs_rows = ""
for pair, count in top_pairs:
    pairs_rows += f'<tr><td style="padding:6px">{pair}</td><td style="text-align:center;padding:6px">{count}</td></tr>\n'

max_support = max(m["support"] for m in class_metrics.values()) or 1
dist_bars = ""
for cls in CLASSES:
    m = class_metrics[cls]
    pct = m["support"] / max_support * 100
    color = "#4CAF50" if m["recall"] >= 0.9 else ("#FF9800" if m["recall"] >= 0.7 else "#f44336")
    dist_bars += f'''<div style="margin:8px 0">
        <div style="display:flex;align-items:center;gap:10px">
            <span style="width:60px;text-align:right;font-weight:bold">{SHORT[cls]}</span>
            <div style="flex:1;background:#1a1a2e;border-radius:4px;overflow:hidden">
                <div style="width:{pct}%;background:{color};padding:4px 8px;color:white;font-size:13px;white-space:nowrap">
                    {m['support']} images ({m['recall']:.0%} acc)
                </div>
            </div>
        </div>
    </div>'''

badge_class = "badge-high" if overall_accuracy >= 0.9 else "badge-mid" if overall_accuracy >= 0.7 else "badge-low"

html = f'''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Artistic Swimming Position Classifier - Evaluation Report</title>
<style>
    * {{ margin: 0; padding: 0; box-sizing: border-box; }}
    body {{ font-family: 'Segoe UI', system-ui, -apple-system, sans-serif; background: #0f0f1a; color: #e0e0e0; line-height: 1.6; }}
    .container {{ max-width: 1100px; margin: 0 auto; padding: 20px 30px; }}
    h1 {{ font-size: 28px; color: #64b5f6; margin-bottom: 8px; }}
    h2 {{ font-size: 22px; color: #81c784; margin: 30px 0 15px; border-bottom: 2px solid #333; padding-bottom: 8px; }}
    h3 {{ font-size: 18px; color: #ffb74d; margin: 20px 0 10px; }}
    .subtitle {{ color: #aaa; font-size: 14px; margin-bottom: 20px; }}
    .card {{ background: #1a1a2e; border-radius: 8px; padding: 20px; margin: 15px 0; border: 1px solid #333; }}
    .metric-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 15px; margin: 15px 0; }}
    .metric-box {{ background: #16213e; border-radius: 8px; padding: 20px; text-align: center; border: 1px solid #333; }}
    .metric-box .value {{ font-size: 36px; font-weight: bold; color: #64b5f6; }}
    .metric-box .label {{ font-size: 13px; color: #aaa; margin-top: 5px; }}
    table {{ width: 100%; border-collapse: collapse; margin: 10px 0; }}
    th {{ background: #16213e; padding: 10px 8px; text-align: center; font-size: 13px; color: #81c784; border-bottom: 2px solid #444; }}
    td {{ border-bottom: 1px solid #222; font-size: 13px; }}
    tr:hover {{ background: rgba(100,181,246,0.05); }}
    .accuracy-badge {{ display: inline-block; padding: 4px 12px; border-radius: 20px; font-weight: bold; font-size: 14px; }}
    .badge-high {{ background: #2d5a27; color: #81c784; }}
    .badge-mid {{ background: #5a4a27; color: #ffb74d; }}
    .badge-low {{ background: #5a2727; color: #ef5350; }}
    p {{ margin: 8px 0; font-size: 14px; }}
    .footer {{ margin-top: 40px; padding-top: 20px; border-top: 1px solid #333; color: #666; font-size: 12px; text-align: center; }}
</style>
</head>
<body>
<div class="container">

<h1>Artistic Swimming Position Classifier</h1>
<p class="subtitle">Evaluation Report &mdash; {datetime.now().strftime('%B %d, %Y')}</p>

<div class="metric-grid">
    <div class="metric-box">
        <div class="value">{overall_accuracy:.1%}</div>
        <div class="label">Overall Accuracy</div>
    </div>
    <div class="metric-box">
        <div class="value">{correct}/{total}</div>
        <div class="label">Correct / Total</div>
    </div>
    <div class="metric-box">
        <div class="value">{len(errors)}</div>
        <div class="label">Misclassifications</div>
    </div>
    <div class="metric-box">
        <div class="value">5</div>
        <div class="label">Position Classes</div>
    </div>
</div>

<h2>1. Class Distribution</h2>
<div class="card">
    {dist_bars}
</div>

<h2>2. Per-Class Metrics</h2>
<div class="card">
    <table>
        <thead>
            <tr>
                <th style="text-align:left">Class</th>
                <th style="text-align:left">Full Name</th>
                <th>Support</th>
                <th>Correct</th>
                <th>Errors</th>
                <th>Recall</th>
                <th>Precision</th>
                <th>F1 Score</th>
            </tr>
        </thead>
        <tbody>
            {metrics_rows}
        </tbody>
    </table>
</div>

<h2>3. Confusion Matrix</h2>
<div class="card">
    <table>
        <thead>
            <tr>
                <th style="text-align:left">True \\ Pred</th>
                {"".join(f'<th>{SHORT[c]}</th>' for c in CLASSES)}
                <th>Total</th>
                <th>Recall</th>
            </tr>
        </thead>
        <tbody>
            {confusion_rows}
            {col_totals_row}
        </tbody>
    </table>
</div>

<h2>4. Error Analysis</h2>
<div class="card">
    <h3>Top Confusion Pairs</h3>
    <table>
        <thead>
            <tr><th style="text-align:left">True &rarr; Predicted</th><th>Count</th></tr>
        </thead>
        <tbody>
            {pairs_rows}
        </tbody>
    </table>

    <h3 style="margin-top:20px">All Misclassified Images ({len(errors)} total)</h3>
    <table>
        <thead>
            <tr>
                <th style="text-align:left">Filename</th>
                <th style="text-align:left">True Label</th>
                <th style="text-align:left">Predicted</th>
            </tr>
        </thead>
        <tbody>
            {error_rows}
        </tbody>
    </table>
</div>

<div class="footer">
    <p>Generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} &mdash; {total} images evaluated</p>
</div>

</div>
</body>
</html>'''

with open(f"{BASE}/results/report.html", "w") as f:
    f.write(html)

print(f"\nResults saved to: results/results.json")
print(f"Report saved to:  results/report.html")
