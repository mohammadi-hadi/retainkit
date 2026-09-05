"""Draw the two figures in the README from the committed LoCoMo results.

pip install "retainkit[viz]"
python examples/locomo/plot_frontier.py
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

RESULTS = Path(__file__).parent / "results"
FIGURES = RESULTS / "figures"
FOCUS = 2048

STYLE = {
    "oracle": ("#c3c7cb", "--"),
    "fact_memory": ("#1e3a5f", "-"),
    "retrieval": ("#4a7ba7", "-"),
    "session_summary": ("#b07d2b", "-"),
    "head_tail": ("#6b8f71", "-"),
    "recency": ("#b23a48", "-"),
}
AGES = ("same session", "1-2 back", "3-5 back", "6-10 back", "11+ back")


def main() -> int:
    path = RESULTS / "locomo.json"
    if not path.exists():
        print("run examples/locomo/run_locomo.py first", file=sys.stderr)
        return 1
    data = json.loads(path.read_text(encoding="utf-8"))
    rows = data["rows"]
    budgets = data["budgets"]

    figure, (left, right) = plt.subplots(1, 2, figsize=(11, 4.2))

    for policy, (color, dash) in STYLE.items():
        series = {r["budget"]: r["recall"] for r in rows if r["policy"] == policy}
        left.plot(
            budgets,
            [series[b] * 100 for b in budgets],
            dash,
            color=color,
            marker="o",
            markersize=3.5,
            linewidth=1.6,
            label=policy,
        )
    left.set_xscale("log", base=2)
    left.set_xticks(budgets)
    left.set_xticklabels([str(b) for b in budgets], fontsize=8)
    left.set_xlabel("context budget (tokens)")
    left.set_ylabel("evidence recall (%)")
    left.set_title("What survives the budget", fontsize=11)
    left.set_ylim(0, 103)
    left.grid(alpha=0.25, linewidth=0.6)
    left.legend(fontsize=8, frameon=False)

    focus = {r["policy"]: r for r in rows if r["budget"] == FOCUS}
    order = sorted(STYLE, key=lambda p: -focus[p]["recall"])
    width = 0.14
    for index, policy in enumerate(order):
        by_age = focus[policy]["recall_by_age"]
        right.bar(
            [i + index * width for i in range(len(AGES))],
            [by_age.get(age, 0.0) * 100 for age in AGES],
            width=width,
            color=STYLE[policy][0],
            label=policy,
        )
    right.set_xticks([i + width * 2.5 for i in range(len(AGES))])
    right.set_xticklabels(AGES, fontsize=8)
    right.set_xlabel("sessions between the evidence and the question")
    right.set_ylabel("evidence recall (%)")
    right.set_title(f"Where it is lost, at {FOCUS} tokens", fontsize=11)
    right.set_ylim(0, 122)
    right.grid(alpha=0.25, axis="y", linewidth=0.6)
    right.legend(fontsize=7, frameon=False, ncol=3, loc="upper center")

    figure.tight_layout()
    FIGURES.mkdir(parents=True, exist_ok=True)
    out = FIGURES / "locomo.png"
    figure.savefig(out, dpi=170)
    print(f"wrote {out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
