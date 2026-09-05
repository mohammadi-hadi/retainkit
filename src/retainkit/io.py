"""Read conversations and probes from JSON, so the package works on your own data.

{"cases": [{"id": "trip-1",
            "turns":  [{"id": "D1:1", "session": 1, "speaker": "guest",
                        "text": "...", "timestamp": "2026-05-07"}],
            "probes": [{"id": "q1", "question": "...", "evidence": ["D1:1"],
                        "answer": "...", "tag": "single-hop"}]}]}
"""

from __future__ import annotations

import json
from collections.abc import Iterable
from pathlib import Path
from typing import Any

from .evaluate import Case
from .types import Probe, Transcript, Turn


def case_from_dict(data: dict[str, Any]) -> Case:
    turns = tuple(
        Turn(
            id=str(t["id"]),
            session=int(t["session"]),
            speaker=str(t.get("speaker", "")),
            text=str(t["text"]),
            timestamp=t.get("timestamp"),
        )
        for t in data["turns"]
    )
    known = {t.id for t in turns}
    probes = []
    for p in data.get("probes", []):
        evidence = tuple(str(e) for e in p["evidence"] if str(e) in known)
        if not evidence:
            continue
        probes.append(
            Probe(
                id=str(p["id"]),
                question=str(p["question"]),
                evidence=evidence,
                answer=p.get("answer"),
                tag=p.get("tag"),
            )
        )
    return Case(
        transcript=Transcript(id=str(data.get("id", "case")), turns=turns),
        probes=tuple(probes),
    )


def load_cases(path: str | Path) -> list[Case]:
    payload = json.loads(Path(path).read_text(encoding="utf-8"))
    cases = payload["cases"] if isinstance(payload, dict) else payload
    return [case_from_dict(c) for c in cases]


def dump_cases(cases: Iterable[Case], path: str | Path) -> None:
    payload = {
        "cases": [
            {
                "id": case.transcript.id,
                "turns": [
                    {
                        "id": t.id,
                        "session": t.session,
                        "speaker": t.speaker,
                        "text": t.text,
                        "timestamp": t.timestamp,
                    }
                    for t in case.transcript.turns
                ],
                "probes": [
                    {
                        "id": p.id,
                        "question": p.question,
                        "evidence": list(p.evidence),
                        "answer": p.answer,
                        "tag": p.tag,
                    }
                    for p in case.probes
                ],
            }
            for case in cases
        ]
    }
    Path(path).write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
