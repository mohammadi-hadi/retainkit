"""Sweep the context policies over LoCoMo and write the committed results.

    python examples/locomo/fetch_data.py
    python examples/locomo/run_locomo.py

LoCoMo gives ten conversations that run over dozens of sessions, and questions
whose supporting turns are named by id. That is exactly the shape this package
measures: at a given context budget, is the turn that carries the answer still
in front of the model?

Two choices worth stating, both visible in the output header:

* **Adversarial questions are left out.** Category 5 has no answer in the
  conversation — it ships an ``adversarial_answer`` instead — so asking whether
  its evidence survived measures nothing. Every other category is kept.
* **A question whose evidence names a turn that is not in the transcript is
  dropped whole**, rather than scored on the turns that do resolve, which would
  quietly make it easier.

Image turns contribute their caption alongside their text, which is how the
LoCoMo baselines present them to a model.
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

from retainkit import Case, Probe, Transcript, Turn, run
from retainkit.policies import DEFAULT_POLICIES
from retainkit.report import markdown, to_json

DATA = Path(__file__).parent / "data" / "locomo10.json"
RESULTS = Path(__file__).parent / "results"
BUDGETS = (512, 1024, 2048, 4096, 8192, 16384, 32768)
FOCUS = 2048

# The five question types of the LoCoMo paper. Category 5 is the only one that
# ships an `adversarial_answer` field, which is how the mapping was checked
# against the released file; category 1 is 95% multi-session, as multi-hop
# questions should be.
CATEGORIES = {
    1: "multi-hop",
    2: "temporal",
    3: "open-domain",
    4: "single-hop",
    5: "adversarial",
}
EXCLUDED = 5
SESSION_KEY = re.compile(r"^session_(\d+)$")


def build_case(sample: dict) -> tuple[Case, int]:
    """One LoCoMo conversation, and how many of its questions were dropped."""
    conversation = sample["conversation"]
    turns: list[Turn] = []
    for key, value in conversation.items():
        match = SESSION_KEY.match(key)
        if not match or not isinstance(value, list):
            continue
        session = int(match.group(1))
        stamp = conversation.get(f"{key}_date_time")
        for entry in value:
            text = entry["text"]
            caption = entry.get("blip_caption")
            if caption:
                text = f"{text} [shared an image: {caption}]"
            turns.append(
                Turn(
                    id=entry["dia_id"],
                    session=session,
                    speaker=entry.get("speaker", ""),
                    text=text,
                    timestamp=stamp,
                )
            )
    turns.sort(key=lambda t: (t.session, int(t.id.split(":")[1])))
    known = {t.id for t in turns}

    probes: list[Probe] = []
    dropped = 0
    for position, qa in enumerate(sample["qa"]):
        category = qa.get("category")
        if category == EXCLUDED:
            continue
        evidence = qa.get("evidence") or []
        if isinstance(evidence, str):
            evidence = [evidence]
        evidence = [str(e) for e in evidence]
        if not evidence or any(e not in known for e in evidence):
            dropped += 1
            continue
        probes.append(
            Probe(
                id=f"{sample['sample_id']}-{position}",
                question=str(qa["question"]),
                evidence=tuple(evidence),
                answer=str(qa.get("answer", "")),
                tag=CATEGORIES.get(category, str(category)),
            )
        )
    case = Case(
        transcript=Transcript(id=str(sample["sample_id"]), turns=tuple(turns)), probes=tuple(probes)
    )
    return case, dropped


def category_table(report) -> str:
    """Recall per question type at the focus budget."""
    rows = sorted(report.by_budget(FOCUS), key=lambda r: (-r.recall, r.policy))
    names = sorted({name for row in rows for name in row.recall_by_tag})
    lines = [
        "| Policy | " + " | ".join(names) + " |",
        "| --- | " + " | ".join("---:" for _ in names) + " |",
    ]
    for row in rows:
        cells = [
            f"{row.recall_by_tag[n] * 100:.1f}%" if n in row.recall_by_tag else "—" for n in names
        ]
        lines.append(f"| `{row.policy}` | " + " | ".join(cells) + " |")
    return "\n".join(lines)


def main() -> int:
    if not DATA.exists():
        print("run examples/locomo/fetch_data.py first", file=sys.stderr)
        return 1
    samples = json.loads(DATA.read_text(encoding="utf-8"))
    cases, dropped = [], 0
    for sample in samples:
        case, lost = build_case(sample)
        cases.append(case)
        dropped += lost

    sessions = sorted(len(c.transcript.sessions) for c in cases)
    notes = {
        "dataset": "LoCoMo (Maharana et al., ACL 2024), 10 conversations",
        "sessions per conversation": f"{sessions[0]}–{sessions[-1]}",
        "questions": f"{sum(len(c.probes) for c in cases)} scored, "
        f"{dropped} dropped for unresolvable evidence, adversarial category excluded",
    }
    report = run(cases, DEFAULT_POLICIES, BUDGETS, notes=notes)

    RESULTS.mkdir(parents=True, exist_ok=True)
    text = markdown(report, "Context policies on LoCoMo", FOCUS)
    text += f"\n## Recall by question type, at {FOCUS} tokens\n\n{category_table(report)}\n"
    (RESULTS / "locomo.md").write_text(text, encoding="utf-8")
    (RESULTS / "locomo.json").write_text(to_json(report), encoding="utf-8")
    print(text)
    return 0


if __name__ == "__main__":
    sys.exit(main())
