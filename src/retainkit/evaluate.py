"""Run policies over conversations and collect the sweep."""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass, field

from .metrics import Outcome, PolicyResult, summarise
from .policies import DEFAULT_POLICIES, Policy, turn_fragments
from .policies.base import spend
from .tokens import Tokenizer, char4
from .types import Probe, Retained, Transcript

#: Budgets swept unless the caller names their own, in tokens.
DEFAULT_BUDGETS: tuple[int, ...] = (256, 512, 1024, 2048, 4096, 8192)


@dataclass(frozen=True, slots=True)
class Case:
    """One conversation and the probes asked against it."""

    transcript: Transcript
    probes: tuple[Probe, ...]


@dataclass(frozen=True, slots=True)
class Report:
    """Every row of a sweep, plus what it was run over."""

    rows: tuple[PolicyResult, ...]
    cases: int
    probes: int
    full_tokens: float
    budgets: tuple[int, ...]
    tokenizer: str
    notes: dict[str, str] = field(default_factory=dict)

    def by_budget(self, budget: int) -> tuple[PolicyResult, ...]:
        return tuple(r for r in self.rows if r.budget == budget)

    def by_policy(self, policy: str) -> tuple[PolicyResult, ...]:
        return tuple(r for r in self.rows if r.policy == policy)


def evidence_age(transcript: Transcript, probe: Probe) -> int:
    """Sessions between the oldest evidence turn and the end of the conversation."""
    sessions = [transcript.by_id(e).session for e in probe.evidence if _has(transcript, e)]
    if not sessions:
        return 0
    return transcript.last_session - min(sessions)


def _has(transcript: Transcript, turn_id: str) -> bool:
    try:
        transcript.by_id(turn_id)
    except KeyError:
        return False
    return True


def middle_share(retained: Retained, probe: Probe) -> float | None:
    """How much of the surviving evidence sits in the middle half of the context.

    Long-context models attend least well there, so a policy can retain the
    evidence and still bury it. ``None`` when nothing survived.
    """
    positions = [retained.position_of(e) for e in probe.evidence]
    found = [p for p in positions if p is not None]
    if not found or len(retained.fragments) < 4:
        return None
    size = len(retained.fragments)
    low, high = size * 0.25, size * 0.75
    return sum(1 for p in found if low <= p <= high) / len(found)


def score(retained: Retained, transcript: Transcript, probe: Probe) -> Outcome:
    """Turn one policy's selection into one measured outcome."""
    evidence = set(probe.evidence)
    kept = retained.source_ids & evidence
    whole = retained.whole_source_ids & evidence
    return Outcome(
        probe_id=probe.id,
        tag=probe.tag,
        age=evidence_age(transcript, probe),
        covered=kept == evidence,
        covered_whole=whole == evidence,
        partial=len(kept) / len(evidence),
        tokens=retained.tokens,
        middle=middle_share(retained, probe) if kept == evidence else None,
    )


def run(
    cases: Sequence[Case],
    policies: Sequence[Policy] = DEFAULT_POLICIES,
    budgets: Sequence[int] = DEFAULT_BUDGETS,
    tokenizer: Tokenizer = char4,
    seed: int = 0,
    notes: dict[str, str] | None = None,
) -> Report:
    """Sweep every policy over every budget and summarise each combination."""
    if not cases:
        raise ValueError("nothing to evaluate")
    full = [spend(turn_fragments(c.transcript), tokenizer) for c in cases]
    full_tokens = sum(full) / len(full)

    rows: list[PolicyResult] = []
    probe_count = sum(len(c.probes) for c in cases)
    for budget in budgets:
        for policy in policies:
            outcomes: list[Outcome] = []
            for case in cases:
                for probe in case.probes:
                    retained = policy.select(case.transcript, probe, budget, tokenizer)
                    outcomes.append(score(retained, case.transcript, probe))
            rows.append(
                summarise(
                    policy=policy.name,
                    budget=budget,
                    query_aware=policy.query_aware,
                    outcomes=outcomes,
                    full_tokens=full_tokens,
                    seed=seed,
                )
            )
    return Report(
        rows=tuple(rows),
        cases=len(cases),
        probes=probe_count,
        full_tokens=full_tokens,
        budgets=tuple(budgets),
        tokenizer=getattr(tokenizer, "__name__", "custom"),
        notes=notes or {},
    )
