"""Turn a sweep into a table someone can read and a file a test can diff."""

from __future__ import annotations

import json
from collections.abc import Sequence
from dataclasses import asdict

from .evaluate import Report
from .metrics import AGE_BUCKETS, PolicyResult, budget_for_recall


def _pct(value: float) -> str:
    return f"{value * 100:.1f}%"


def sweep_table(report: Report) -> str:
    """Recall and cost for every policy at every budget."""
    lines = [
        "| Budget | Policy | Sees question | Recall | 95% CI | Whole turns | Partial | Tokens |",
        "| ---: | --- | :---: | ---: | --- | ---: | ---: | ---: |",
    ]
    for budget in report.budgets:
        for row in sorted(report.by_budget(budget), key=lambda r: (-r.recall, r.policy)):
            lines.append(
                f"| {row.budget} | `{row.policy}` | {'yes' if row.query_aware else 'no'} "
                f"| {_pct(row.recall)} | {_pct(row.recall_low)}–{_pct(row.recall_high)} "
                f"| {_pct(row.whole_recall)} | {_pct(row.partial)} | {row.tokens:.0f} |"
            )
    return "\n".join(lines)


def age_table(report: Report, budget: int) -> str:
    """Recall split by how many sessions back the evidence sits."""
    rows = sorted(report.by_budget(budget), key=lambda r: (-r.recall, r.policy))
    names = [name for name, _, _ in AGE_BUCKETS if any(name in r.probes_by_age for r in rows)]
    header = "| Policy | " + " | ".join(names) + " |"
    rule = "| --- | " + " | ".join("---:" for _ in names) + " |"
    lines = [header, rule]
    for row in rows:
        cells = [_pct(row.recall_by_age[n]) if n in row.recall_by_age else "—" for n in names]
        lines.append(f"| `{row.policy}` | " + " | ".join(cells) + " |")
    counts = [str(rows[0].probes_by_age.get(n, 0)) for n in names]
    lines.append("| _probes_ | " + " | ".join(counts) + " |")
    return "\n".join(lines)


def frontier_table(report: Report, targets: Sequence[float] = (0.5, 0.8, 0.9)) -> str:
    """The cheapest swept budget at which each policy reaches a recall target."""
    policies = sorted({r.policy for r in report.rows})
    header = "| Policy | " + " | ".join(f"{int(t * 100)}% recall" for t in targets) + " |"
    rule = "| --- | " + " | ".join("---:" for _ in targets) + " |"
    lines = [header, rule]
    for policy in policies:
        cells = []
        for target in targets:
            budget = budget_for_recall(report.rows, policy, target)
            cells.append(f"{budget}" if budget is not None else "not reached")
        lines.append(f"| `{policy}` | " + " | ".join(cells) + " |")
    return "\n".join(lines)


def markdown(report: Report, title: str, budget_focus: int | None = None) -> str:
    """The full written report."""
    focus = budget_focus if budget_focus is not None else report.budgets[len(report.budgets) // 2]
    parts = [
        f"# {title}",
        "",
        f"{report.cases} conversations, {report.probes} probes, "
        f"{report.full_tokens:.0f} tokens of conversation on average "
        f"(`{report.tokenizer}` estimator).",
        "",
    ]
    for key, value in sorted(report.notes.items()):
        parts.append(f"- **{key}**: {value}")
    if report.notes:
        parts.append("")
    parts += [
        "## Recall against budget",
        "",
        sweep_table(report),
        "",
        f"## Recall by how old the evidence is, at {focus} tokens",
        "",
        age_table(report, focus),
        "",
        "## Cheapest budget that reaches a recall target",
        "",
        frontier_table(report),
        "",
    ]
    return "\n".join(parts)


def to_json(report: Report) -> str:
    payload = {
        "cases": report.cases,
        "probes": report.probes,
        "full_tokens": round(report.full_tokens, 3),
        "budgets": list(report.budgets),
        "tokenizer": report.tokenizer,
        "notes": report.notes,
        "rows": [_row(r) for r in report.rows],
    }
    return json.dumps(payload, indent=2, sort_keys=True) + "\n"


def _row(row: PolicyResult) -> dict[str, object]:
    data = asdict(row)
    for key, value in list(data.items()):
        if isinstance(value, float):
            data[key] = round(value, 4)
        elif isinstance(value, dict):
            data[key] = {k: (round(v, 4) if isinstance(v, float) else v) for k, v in value.items()}
    return data
