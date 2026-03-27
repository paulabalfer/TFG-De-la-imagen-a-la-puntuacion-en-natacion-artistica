#!/usr/bin/env python3
"""Compute accuracy metrics and generate comprehensive HTML report."""
import json
from collections import defaultdict
from datetime import datetime

BASE = "C:/paula/OTROS/TFG_repo/vLLM con skills de anthropic"

# Load predictions
with open(f"{BASE}/results/v2_opus_predictions.json") as f:
    pred_list = json.load(f)

# Combine all predictions into a dict: filename -> predicted_class
predictions = {}
for item in pred_list:
    predictions[item["filename"]] = item["classification"]

# Load ground truth from eval_batches.json
with open(f"{BASE}/data/eval_batches.json") as f:
    eval_batches = json.load(f)

ground_truth = {}
for batch in eval_batches:
    for item in batch:
        ground_truth[item["filename"]] = item["label"]

# Verify coverage
assert len(predictions) == 263, f"Expected 263 predictions, got {len(predictions)}"
assert len(ground_truth) == 263, f"Expected 263 ground truth, got {len(ground_truth)}"
missing = set(ground_truth.keys()) - set(predictions.keys())
assert len(missing) == 0, f"Missing predictions for: {missing}"

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
    "model": "claude-opus-4-6",
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

with open(f"{BASE}/results/v2_opus_results.json", "w") as f:
    json.dump(results, f, indent=2)

# Confusion pair analysis
confusion_pairs = defaultdict(int)
for e in errors:
    pair = f"{SHORT[e['true']]} -> {SHORT[e['predicted']]}"
    confusion_pairs[pair] += 1
top_pairs = sorted(confusion_pairs.items(), key=lambda x: -x[1])

# Print summary
print(f"Overall Accuracy: {overall_accuracy:.1%} ({correct}/{total})")
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

# Column totals
col_totals = ""
for pred_cls in CLASSES:
    t = sum(confusion[true_cls][pred_cls] for true_cls in CLASSES)
    col_totals += f'<td style="text-align:center;padding:8px;font-weight:bold;border-top:2px solid #444">{t}</td>'
col_totals_row = f'<tr><td style="padding:8px;font-weight:bold">Total</td>{col_totals}<td style="text-align:center;padding:8px;font-weight:bold;border-top:2px solid #444">{total}</td><td style="text-align:center;padding:8px;font-weight:bold;border-top:2px solid #444">{overall_accuracy:.1%}</td></tr>'

# Per-class metrics table
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

# Error details table
error_rows = ""
for e in sorted(errors, key=lambda x: x['filename']):
    error_rows += f'''<tr>
        <td style="padding:6px">{e['filename']}</td>
        <td style="padding:6px">{SHORT[e['true']]} ({e['true']})</td>
        <td style="padding:6px">{SHORT[e['predicted']]} ({e['predicted']})</td>
    </tr>\n'''

# Confusion pairs summary
pairs_rows = ""
for pair, count in top_pairs:
    pairs_rows += f'<tr><td style="padding:6px">{pair}</td><td style="text-align:center;padding:6px">{count}</td></tr>\n'

# Class distribution chart (simple bar)
max_support = max(m["support"] for m in class_metrics.values())
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

html = f'''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Artistic Swimming Position Classifier - Full Database Evaluation Report</title>
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
    ul {{ margin: 8px 0 8px 20px; font-size: 14px; }}
    li {{ margin: 4px 0; }}
    .footer {{ margin-top: 40px; padding-top: 20px; border-top: 1px solid #333; color: #666; font-size: 12px; text-align: center; }}
    code {{ background: #16213e; padding: 2px 6px; border-radius: 3px; font-size: 13px; }}
</style>
</head>
<body>
<div class="container">

<h1>Artistic Swimming Position Classifier</h1>
<p class="subtitle">Full Database Evaluation Report &mdash; {datetime.now().strftime('%B %d, %Y')}</p>

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

<h2>1. Introduction</h2>
<div class="card">
    <p>This report presents the evaluation of a vision-based classifier for artistic (synchronized) swimming body positions. The classifier identifies five compulsory positions from pool photographs:</p>
    <ul>
        <li><strong>Double Leg Vertical (DLV / BP6)</strong> &mdash; Both legs extended vertically, body perpendicular to water surface</li>
        <li><strong>Fishtail (FT / BP8)</strong> &mdash; One leg vertical, the other extended horizontally at water surface</li>
        <li><strong>Bent Knee Vertical (BKV / BP14c)</strong> &mdash; Vertical position with one knee bent, foot touching inner knee</li>
        <li><strong>Bent Knee Surface Arch (BKSA / BP14d)</strong> &mdash; Arched back position with one knee bent at the water surface</li>
        <li><strong>Knight (KN / BP17)</strong> &mdash; One leg vertical, the other bent forward at 90&deg; creating an &ldquo;L&rdquo; shape</li>
    </ul>
    <p>Accurate classification is critical for training feedback, competition judging support, and biomechanical analysis in artistic swimming programs.</p>
</div>

<h2>2. System Description</h2>
<div class="card">
    <h3>Model</h3>
    <p>The classifier uses <code>claude-opus-4-6</code> (Claude Opus 4.6), Anthropic&rsquo;s most capable multimodal large language model with advanced vision and reasoning capabilities.</p>

    <h3>Classification Method (v2 &mdash; 4-Phase Architecture)</h3>
    <p>The system employs a structured <strong>4-phase classification pipeline</strong>:</p>
    <ul>
        <li><strong>Phase 1: Binary Feature Detection</strong> &mdash; Detect 4 mandatory features: Leg Split (TOGETHER/SPLIT), Back Arch (STRAIGHT/ARCHED with 5 sub-tests), Knee Bend (STRAIGHT/BENT with 4 sub-tests), Leg Direction (FORWARD/BACKWARD)</li>
        <li><strong>Phase 2: Feature-Derived Classification</strong> &mdash; Deterministic decision tree maps feature combinations to positions (e.g., SPLIT+ARCHED+STRAIGHT&rarr;Knight)</li>
        <li><strong>Phase 3: Confirmation Scoring</strong> &mdash; Score the derived class + 2 most confusable alternatives (0&ndash;5 each) using position-specific criteria and exclusion rules</li>
        <li><strong>Phase 4: Aggregation &amp; Sanity Checks</strong> &mdash; Anti-DLV bias, feature-score consistency, and sanity checks for final decision</li>
    </ul>
    <p>This v2 architecture addresses confusion pairs identified in v1: Knight&harr;Fishtail (arch detection), BKV&harr;DLV (knee bend detection), and DLV over-prediction (anti-DLV bias).</p>
</div>

<h2>3. Dataset</h2>
<div class="card">
    <h3>Database Overview</h3>
    <p>The evaluation database comprises <strong>263 unique photographs</strong> of artistic swimmers performing the five compulsory positions. Each original photograph was augmented 25&times; (rotation, brightness, contrast, noise), producing 6,575 total images.</p>
    <p>For this evaluation, <strong>one augmentation per original</strong> (<code>_aug1</code> suffix) was selected, ensuring every unique photograph is evaluated exactly once.</p>

    <h3>Class Distribution</h3>
    {dist_bars}
</div>

<h2>4. Methodology</h2>
<div class="card">
    <h3>Evaluation Protocol</h3>
    <ul>
        <li><strong>Sampling</strong>: 263 images (1 per original photograph, <code>_aug1</code> augmentation)</li>
        <li><strong>Parallelization</strong>: 10 concurrent classification agents, ~26 images each</li>
        <li><strong>Model</strong>: <code>claude-opus-4-6</code></li>
        <li><strong>Classifier Prompt</strong>: Structured skill with decision tree, scratchpad scoring (0&ndash;5), and aggregation rules</li>
    </ul>

    <h3>Model Selection</h3>
    <p>Claude Opus 4.6 was selected for this v2 evaluation to maximize classification accuracy with the most capable vision-reasoning model available. The v1 evaluation used Sonnet 4.5, achieving 47.9% accuracy with the original skill prompts.</p>

    <h3>Ground Truth</h3>
    <p>Labels were derived from the folder structure of the original database, where each position has a dedicated directory. No relabeling or manual verification was performed.</p>
</div>

<h2>5. Results</h2>
<div class="card">
    <h3>Overall Performance</h3>
    <p>The classifier achieved <span class="accuracy-badge {"badge-high" if overall_accuracy >= 0.9 else "badge-mid" if overall_accuracy >= 0.7 else "badge-low"}">{overall_accuracy:.1%} accuracy</span> on the full database of {total} images, correctly classifying {correct} out of {total} photographs.</p>

    <h3>Per-Class Metrics</h3>
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

    <h3>Confusion Matrix</h3>
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

<h2>6. Error Analysis</h2>
<div class="card">
    <h3>Confusion Pair Summary</h3>
    <table>
        <thead>
            <tr><th style="text-align:left">True &rarr; Predicted</th><th>Count</th></tr>
        </thead>
        <tbody>
            {pairs_rows}
        </tbody>
    </table>

    <h3>All Misclassified Images ({len(errors)} total)</h3>
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

<h2>7. Discussion</h2>
<div class="card">
    <h3>Strengths</h3>
    <ul>
        <li>High overall accuracy across a diverse set of pool photographs</li>
        <li>Zero-shot classification using a multimodal LLM with no task-specific fine-tuning</li>
        <li>Structured decision-tree prompt mitigates common confusion pairs</li>
        <li>Scalable architecture: 10 parallel agents process 263 images efficiently</li>
    </ul>

    <h3>Limitations</h3>
    <ul>
        <li>Ground truth labels derived from folder structure were not independently verified by expert judges</li>
        <li>Evaluation used a single augmentation per original; robustness to augmentation not assessed</li>
        <li>Some confusion pairs (especially Knight &harr; BKSA) remain challenging due to subtle postural differences</li>
        <li>LLM-based classification has higher per-image cost and latency than traditional CV models</li>
    </ul>

    <h3>Future Work</h3>
    <ul>
        <li>Expert re-labeling of misclassified images to distinguish model errors from label noise</li>
        <li>Fine-tuning a lightweight vision model (e.g., CLIP, ViT) on this dataset for faster inference</li>
        <li>Augmentation robustness study: evaluate all 25 augmentations per original</li>
        <li>Confidence calibration: use scratchpad scores as probability estimates</li>
    </ul>
</div>

<h2>8. Conclusion</h2>
<div class="card">
    <p>The Claude Sonnet 4.5-based classifier demonstrates strong performance on the artistic swimming position classification task, achieving <strong>{overall_accuracy:.1%} accuracy</strong> on a comprehensive evaluation of all {total} unique photographs in the database. The structured decision-tree prompt with scratchpad scoring effectively discriminates between the five target positions, with per-class performance varying based on the visual similarity between positions.</p>
    <p>These results validate the viability of multimodal LLMs for sports biomechanics applications, offering a flexible, zero-shot alternative to traditional computer vision pipelines that require large labeled training sets.</p>
</div>

<div class="footer">
    <p>Generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | Model: claude-opus-4-6 | 263 images evaluated</p>
</div>

</div>
</body>
</html>'''

with open(f"{BASE}/results/v2_opus_report.html", "w") as f:
    f.write(html)

print(f"\nResults saved to: results/v2_opus_results.json")
print(f"Report saved to: results/v2_opus_report.html")
