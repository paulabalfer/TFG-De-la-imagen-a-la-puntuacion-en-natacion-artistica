#!/usr/bin/env python3
"""
evaluate_scores.py — Compare model-generated scores against judge scores.
A prediction is "correct" if |generated - judge| <= TOLERANCE (default 0.5).

Reads:
  results/subset_puntuation_generated.xlsx  — POSITION, IMAGE, SCORE (model output)
  data/subset_puntuation_juez1.xlsx         — POSITION, IMAGE (hyperlink), SCORE (judge)

Writes:
  results/score_evaluation.json
  results/score_report.html
  results/score_scatter.png

Usage:
    python evaluate_scores.py [--generated PATH] [--judge PATH] [--output-dir DIR] [--tolerance FLOAT]
"""
from __future__ import annotations

import argparse
import json
import re
from collections import defaultdict
from datetime import datetime
from pathlib import Path

import openpyxl
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent

POSITIONS = [
    "Double Leg Vertical",
    "Fishtail",
    "Bent Knee Vertical",
    "Bent Knee Surface Arch Position",
    "Knight",
]
SHORT = {
    "Double Leg Vertical": "DLV",
    "Fishtail": "FT",
    "Bent Knee Vertical": "BKV",
    "Bent Knee Surface Arch Position": "BKSA",
    "Knight": "KN",
}
CODES = {
    "Double Leg Vertical": "BP6",
    "Fishtail": "BP8",
    "Bent Knee Vertical": "BP14c",
    "Bent Knee Surface Arch Position": "BP14d",
    "Knight": "BP17",
}


def _extract_image_name(cell_value: str | None) -> str | None:
    """Extract bare filename from a HYPERLINK formula or return value as-is."""
    if cell_value is None:
        return None
    s = str(cell_value)
    m = re.search(r'[/\\]([^/\\"]+\.(?:jpg|jpeg|png|JPG|JPEG|PNG))', s)
    if m:
        return m.group(1)
    return s.strip()


def load_excel(path: Path, parse_image: bool = False) -> list[tuple[str, str, float]]:
    wb = openpyxl.load_workbook(path, data_only=False)
    ws = wb.active
    rows = []
    for row in ws.iter_rows(min_row=2, values_only=True):
        pos, img, score = row[0], row[1], row[2]
        if pos is None or img is None or score is None:
            continue
        img = _extract_image_name(str(img)) if parse_image else str(img).strip()
        if img:
            rows.append((str(pos).strip(), img, float(score)))
    return rows


def main() -> int:
    parser = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("--generated", type=Path,
                        default=ROOT / "results" / "subset_puntuation_generated.xlsx")
    parser.add_argument("--judge", type=Path,
                        default=ROOT / "data" / "subset_puntuation_expert.xlsx")
    parser.add_argument("--output-dir", type=Path, default=ROOT / "results")
    parser.add_argument("--tolerance", type=float, default=1,
                        help="Half-width of the acceptance band (default 1)")
    args = parser.parse_args()

    tol = args.tolerance

    generated_rows = load_excel(args.generated, parse_image=False)
    judge_rows = load_excel(args.judge, parse_image=True)

    gen_map: dict[tuple[str, str], float] = {
        (pos.lower(), img.upper()): score for pos, img, score in generated_rows
    }
    judge_map: dict[tuple[str, str], float] = {
        (pos.lower(), img.upper()): score for pos, img, score in judge_rows
    }

    matched_keys = set(judge_map.keys()) & set(gen_map.keys())
    missing_in_gen = set(judge_map.keys()) - set(gen_map.keys())
    extra_in_gen = set(gen_map.keys()) - set(judge_map.keys())

    if missing_in_gen:
        print(f"WARNING: {len(missing_in_gen)} judge entries have no generated score:")
        for k in sorted(missing_in_gen):
            print(f"  {k}")
    if extra_in_gen:
        print(f"WARNING: {len(extra_in_gen)} generated entries have no judge score (ignored).")

    print(f"Evaluating {len(matched_keys)} matched entries  |  tolerance ±{tol}\n")

    results_list: list[dict] = []
    for key in sorted(matched_keys):
        pos_norm, img = key
        judge_score = judge_map[key]
        gen_score = gen_map[key]
        diff = gen_score - judge_score
        within = abs(diff) <= tol
        pos_display = next((p for p in POSITIONS if p.lower() == pos_norm), pos_norm)
        results_list.append({
            "image": img,
            "position": pos_display,
            "judge_score": judge_score,
            "generated_score": gen_score,
            "diff": round(diff, 4),
            "abs_diff": round(abs(diff), 4),
            "within_tolerance": within,
        })

    total = len(results_list)
    correct = sum(1 for r in results_list if r["within_tolerance"])
    overall_accuracy = correct / total if total > 0 else 0

    pos_groups: dict[str, list[dict]] = defaultdict(list)
    for r in results_list:
        pos_groups[r["position"]].append(r)

    pos_stats: dict[str, dict | None] = {}
    for pos in POSITIONS:
        group = pos_groups.get(pos, [])
        if not group:
            pos_stats[pos] = None
            continue
        n = len(group)
        n_correct = sum(1 for r in group if r["within_tolerance"])
        out_of_range = [r for r in group if not r["within_tolerance"]]
        pos_stats[pos] = {
            "n": n,
            "correct": n_correct,
            "accuracy": round(n_correct / n, 4),
            "mae": round(sum(r["abs_diff"] for r in group) / n, 4),
            "bias": round(sum(r["diff"] for r in group) / n, 4),
            "mean_excess_deviation": round(
                sum(r["abs_diff"] - tol for r in out_of_range) / len(out_of_range), 4
            ) if out_of_range else 0.0,
            "n_out_of_range": len(out_of_range),
        }

    # ── Print summary ─────────────────────────────────────────────────────────
    print(f"Overall accuracy (within ±{tol}): {overall_accuracy:.1%}  ({correct}/{total})")
    print(f"\nPer-position breakdown:")
    print(f"  {'Code':>5}  {'Acc':>6}  {'MAE':>5}  {'Bias':>6}  {'MeanExcess':>10}  N")
    for pos in POSITIONS:
        s = pos_stats.get(pos)
        if s is None:
            continue
        print(f"  {CODES[pos]:>5}  {s['accuracy']:.1%}  {s['mae']:.3f}"
              f"  {s['bias']:+.3f}  {s['mean_excess_deviation']:>10.3f}  {s['n']}")

    # ── Save JSON ─────────────────────────────────────────────────────────────
    out_data = {
        "date": datetime.now().isoformat(),
        "tolerance": tol,
        "total": total,
        "correct": correct,
        "overall_accuracy": round(overall_accuracy, 4),
        "per_position": {
            pos: ({k: round(v, 4) if isinstance(v, float) else v for k, v in s.items()}
                  if s else None)
            for pos, s in pos_stats.items()
        },
        "per_image": results_list,
    }
    args.output_dir.mkdir(parents=True, exist_ok=True)
    json_path = args.output_dir / "score_evaluation.json"
    json_path.write_text(json.dumps(out_data, indent=2, ensure_ascii=False), encoding="utf-8")

    # ── HTML report ───────────────────────────────────────────────────────────
    html = _build_html(results_list, pos_stats, overall_accuracy, correct, total, tol)
    html_path = args.output_dir / "score_report.html"
    html_path.write_text(html, encoding="utf-8")

    # ── Scatter plot ──────────────────────────────────────────────────────────
    scatter_path = args.output_dir / "score_scatter.png"
    _build_scatter(results_list, tol, scatter_path)

    print(f"\nJSON    -> {json_path}")
    print(f"HTML    -> {html_path}")
    print(f"Scatter -> {scatter_path}")
    return 0


def _build_scatter(results_list: list[dict], tol: float, out_path: Path) -> None:
    COLORS = {
        "Double Leg Vertical":             "#1f77b4",
        "Fishtail":                        "#2ca02c",
        "Bent Knee Vertical":              "#ff7f0e",
        "Bent Knee Surface Arch Position": "#d62728",
        "Knight":                          "#9467bd",
    }

    judge_scores = np.array([r["judge_score"]     for r in results_list])
    gen_scores   = np.array([r["generated_score"] for r in results_list])

    fig, ax = plt.subplots(figsize=(7, 7))

    lo = min(judge_scores.min(), gen_scores.min()) - 0.5
    hi = max(judge_scores.max(), gen_scores.max()) + 0.5
    diag = np.array([lo, hi])

    # Tolerance band
    ax.fill_between(diag, diag - tol, diag + tol, color="#aaaaaa", alpha=0.2,
                    zorder=1, label=f"±{tol} tolerance band")

    # Perfect-agreement diagonal
    ax.plot(diag, diag, color="#333333", linewidth=1.5, linestyle="--",
            zorder=2, label="Perfect agreement")

    # Scatter points coloured by position
    for pos, color in COLORS.items():
        idx = [i for i, r in enumerate(results_list) if r["position"] == pos]
        if not idx:
            continue
        ax.scatter(judge_scores[idx], gen_scores[idx],
                   color=color, s=55, alpha=0.85, edgecolors="white",
                   linewidths=0.5, zorder=3, label=SHORT.get(pos, pos))

    ax.set_xlim(lo, hi)
    ax.set_ylim(lo, hi)
    ax.set_aspect("equal")
    ax.set_xlabel("Expert score", fontsize=12)
    ax.set_ylabel("Generated score", fontsize=12)
    ax.set_title("Expert vs Generated Scores", fontsize=14, pad=12)
    ax.grid(True, linestyle=":", color="#cccccc", linewidth=0.7)
    ax.legend(fontsize=9, loc="upper left", framealpha=0.9)

    fig.tight_layout()
    fig.savefig(out_path, dpi=150, bbox_inches="tight")
    plt.close(fig)


def _build_html(results_list, pos_stats, overall_accuracy, correct, total, tol) -> str:
    mae_overall = sum(r["abs_diff"] for r in results_list) / total if total else 0
    bias_overall = sum(r["diff"] for r in results_list) / total if total else 0
    n_out = total - correct
    badge_class = "badge-high" if overall_accuracy >= 0.8 else "badge-mid" if overall_accuracy >= 0.6 else "badge-low"

    # 1 — accuracy bars
    dist_bars = ""
    for pos in POSITIONS:
        s = pos_stats.get(pos)
        if s is None:
            continue
        pct = s["accuracy"] * 100
        color = "#4CAF50" if s["accuracy"] >= 0.8 else "#FF9800" if s["accuracy"] >= 0.6 else "#f44336"
        dist_bars += f'''
        <div style="margin:8px 0">
          <div style="display:flex;align-items:center;gap:10px">
            <span style="width:60px;text-align:right;font-weight:bold">{SHORT[pos]}</span>
            <div style="flex:1;background:#1a1a2e;border-radius:4px;overflow:hidden">
              <div style="width:{pct:.0f}%;background:{color};padding:4px 8px;color:white;font-size:13px;white-space:nowrap">
                {s["correct"]}/{s["n"]} ({s["accuracy"]:.0%})
              </div>
            </div>
            <span style="font-size:12px;color:#aaa;white-space:nowrap">
              MAE {s["mae"]:.3f} &nbsp;|&nbsp; bias {s["bias"]:+.3f}
            </span>
          </div>
        </div>'''

    # 2 — per-position detail table
    pos_rows = ""
    for pos in POSITIONS:
        s = pos_stats.get(pos)
        if s is None:
            continue
        acc_col = "#81c784" if s["accuracy"] >= 0.8 else "#ffb74d" if s["accuracy"] >= 0.6 else "#ef5350"
        bias_col = "#ef5350" if abs(s["bias"]) > 0.3 else "#ffb74d" if abs(s["bias"]) > 0.1 else "#81c784"
        pos_rows += f'''<tr>
          <td style="padding:8px;font-weight:bold">{SHORT[pos]} ({CODES[pos]})</td>
          <td style="padding:8px">{pos}</td>
          <td style="text-align:center;padding:8px">{s["n"]}</td>
          <td style="text-align:center;padding:8px">{s["correct"]}</td>
          <td style="text-align:center;padding:8px">{s["n_out_of_range"]}</td>
          <td style="text-align:center;padding:8px;font-weight:bold;color:{acc_col}">{s["accuracy"]:.1%}</td>
          <td style="text-align:center;padding:8px">{s["mae"]:.3f}</td>
          <td style="text-align:center;padding:8px;color:{bias_col}">{s["bias"]:+.3f}</td>
          <td style="text-align:center;padding:8px">{s["mean_excess_deviation"]:.3f}</td>
        </tr>\n'''

    # 3 — out-of-range table (sorted by |diff| desc)
    out_rows_sorted = sorted(
        [r for r in results_list if not r["within_tolerance"]], key=lambda x: -x["abs_diff"]
    )
    out_table_rows = ""
    for r in out_rows_sorted:
        diff_col = "#ef5350" if r["diff"] > 0 else "#64b5f6"
        out_table_rows += f'''<tr>
          <td style="padding:6px">{r["image"]}</td>
          <td style="padding:6px">{SHORT.get(r["position"], r["position"])} ({CODES.get(r["position"], "")})</td>
          <td style="text-align:center;padding:6px">{r["judge_score"]}</td>
          <td style="text-align:center;padding:6px">{r["generated_score"]}</td>
          <td style="text-align:center;padding:6px;color:{diff_col};font-weight:bold">{r["diff"]:+.2f}</td>
        </tr>\n'''

    # 4 — all images table
    all_sorted = sorted(results_list, key=lambda x: (x["position"], x["image"]))
    all_table_rows = ""
    for r in all_sorted:
        bg = "background:rgba(45,90,39,0.3)" if r["within_tolerance"] else "background:rgba(90,39,39,0.3)"
        mark = "&#10003;" if r["within_tolerance"] else "&#10007;"
        mark_col = "#81c784" if r["within_tolerance"] else "#ef5350"
        all_table_rows += f'''<tr style="{bg}">
          <td style="padding:5px">{r["image"]}</td>
          <td style="padding:5px">{SHORT.get(r["position"], r["position"])}</td>
          <td style="text-align:center;padding:5px">{r["judge_score"]}</td>
          <td style="text-align:center;padding:5px">{r["generated_score"]}</td>
          <td style="text-align:center;padding:5px">{r["diff"]:+.2f}</td>
          <td style="text-align:center;padding:5px;font-weight:bold;color:{mark_col}">{mark}</td>
        </tr>\n'''

    return f'''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Score Evaluation Report — Artistic Swimming</title>
<style>
  * {{ margin:0; padding:0; box-sizing:border-box; }}
  body {{ font-family:'Segoe UI',system-ui,-apple-system,sans-serif; background:#0f0f1a; color:#e0e0e0; line-height:1.6; }}
  .container {{ max-width:1100px; margin:0 auto; padding:20px 30px; }}
  h1 {{ font-size:28px; color:#64b5f6; margin-bottom:8px; }}
  h2 {{ font-size:22px; color:#81c784; margin:30px 0 15px; border-bottom:2px solid #333; padding-bottom:8px; }}
  h3 {{ font-size:18px; color:#ffb74d; margin:20px 0 10px; }}
  .subtitle {{ color:#aaa; font-size:14px; margin-bottom:20px; }}
  .card {{ background:#1a1a2e; border-radius:8px; padding:20px; margin:15px 0; border:1px solid #333; }}
  .metric-grid {{ display:grid; grid-template-columns:repeat(auto-fit,minmax(160px,1fr)); gap:15px; margin:15px 0; }}
  .metric-box {{ background:#16213e; border-radius:8px; padding:20px; text-align:center; border:1px solid #333; }}
  .metric-box .value {{ font-size:32px; font-weight:bold; color:#64b5f6; }}
  .metric-box .label {{ font-size:13px; color:#aaa; margin-top:5px; }}
  table {{ width:100%; border-collapse:collapse; margin:10px 0; }}
  th {{ background:#16213e; padding:10px 8px; text-align:center; font-size:13px; color:#81c784; border-bottom:2px solid #444; }}
  td {{ border-bottom:1px solid #222; font-size:13px; }}
  tr:hover {{ background:rgba(100,181,246,0.05); }}
  .accuracy-badge {{ display:inline-block; padding:4px 12px; border-radius:20px; font-weight:bold; font-size:28px; }}
  .badge-high {{ background:#2d5a27; color:#81c784; }}
  .badge-mid {{ background:#5a4a27; color:#ffb74d; }}
  .badge-low {{ background:#5a2727; color:#ef5350; }}
  .legend {{ display:flex; gap:20px; font-size:13px; margin-bottom:10px; }}
  .dot {{ width:12px; height:12px; border-radius:50%; display:inline-block; margin-right:4px; }}
  p {{ margin:8px 0; font-size:14px; }}
  .footer {{ margin-top:40px; padding-top:20px; border-top:1px solid #333; color:#666; font-size:12px; text-align:center; }}
  .note {{ color:#aaa; font-size:12px; margin-bottom:12px; }}
</style>
</head>
<body>
<div class="container">

<h1>Artistic Swimming — Score Evaluation Report</h1>
<p class="subtitle">Tolerance band: ±{tol} points &mdash; {datetime.now().strftime('%B %d, %Y')}</p>

<div class="metric-grid">
  <div class="metric-box">
    <div class="value"><span class="{badge_class} accuracy-badge">{overall_accuracy:.1%}</span></div>
    <div class="label">Overall Accuracy (±{tol})</div>
  </div>
  <div class="metric-box">
    <div class="value">{correct}/{total}</div>
    <div class="label">Within tolerance / Total</div>
  </div>
  <div class="metric-box">
    <div class="value">{n_out}</div>
    <div class="label">Out of range</div>
  </div>
  <div class="metric-box">
    <div class="value">{mae_overall:.3f}</div>
    <div class="label">Overall MAE</div>
  </div>
  <div class="metric-box">
    <div class="value">{bias_overall:+.3f}</div>
    <div class="label">Overall Bias</div>
  </div>
</div>

<h2>1. Per-Position Accuracy</h2>
<div class="card">
  {dist_bars}
</div>

<h2>2. Detailed Per-Position Metrics</h2>
<div class="card">
  <p class="note">
    <strong>MAE</strong>: mean absolute error &nbsp;&mdash;&nbsp;
    <strong>Bias</strong>: mean(generated &minus; judge), positive = over-scoring &nbsp;&mdash;&nbsp;
    <strong>Mean Excess Dev.</strong>: how far beyond ±{tol} on average, for out-of-range images only
  </p>
  <table>
    <thead>
      <tr>
        <th style="text-align:left">Code</th>
        <th style="text-align:left">Position</th>
        <th>N</th>
        <th>Within ±{tol}</th>
        <th>Out of range</th>
        <th>Accuracy</th>
        <th>MAE</th>
        <th>Bias</th>
        <th>Mean Excess Dev.</th>
      </tr>
    </thead>
    <tbody>
      {pos_rows}
    </tbody>
  </table>
</div>

<h2>3. Out-of-Range Images ({n_out} total)</h2>
<div class="card">
  <p class="note">Sorted by |diff| descending. <span style="color:#64b5f6">Blue diff</span> = model under-scored; <span style="color:#ef5350">red diff</span> = model over-scored.</p>
  <table>
    <thead>
      <tr>
        <th style="text-align:left">Image</th>
        <th style="text-align:left">Position</th>
        <th>Judge</th>
        <th>Generated</th>
        <th>Diff</th>
      </tr>
    </thead>
    <tbody>
      {out_table_rows}
    </tbody>
  </table>
</div>

<h2>4. All Images</h2>
<div class="card">
  <div class="legend">
    <span><span class="dot" style="background:#2d5a27"></span>Within ±{tol}</span>
    <span><span class="dot" style="background:#5a2727"></span>Out of range</span>
  </div>
  <table>
    <thead>
      <tr>
        <th style="text-align:left">Image</th>
        <th>Position</th>
        <th>Judge</th>
        <th>Generated</th>
        <th>Diff</th>
        <th>OK?</th>
      </tr>
    </thead>
    <tbody>
      {all_table_rows}
    </tbody>
  </table>
</div>

<div class="footer">
  <p>Generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} &mdash; {total} images evaluated &mdash; tolerance ±{tol}</p>
</div>

</div>
</body>
</html>'''


if __name__ == "__main__":
    raise SystemExit(main())
