"""What is measured, and how.

Every number here is about survival: whether the turns that support an answer
are still in the context a policy hands over. That is a necessary condition for
a correct answer, not a sufficient one — a model can be handed the evidence and
still get the answer wrong. Read these as an upper bound on what any model
behind the policy could do.
"""

from __future__ import annotations

import random
from collections.abc import Sequence
from dataclasses import dataclass, field

#: Buckets for how many sessions back a probe's oldest evidence sits.
AGE_BUCKETS: tuple[tuple[str, int, int | None], ...] = (
    ("same session", 0, 0),
    ("1-2 back", 1, 2),
    ("3-5 back", 3, 5),
    ("6-10 back", 6, 10),
    ("11+ back", 11, None),
)


def bucket_for(age: int) -> str:
    for name, low, high in AGE_BUCKETS:
        if age >= low and (high is None or age <= high):
            return name
    raise ValueError(f"no bucket for age {age}")


@dataclass(frozen=True, slots=True)
class Outcome:
    """One probe, under one policy, at one budget."""

    probe_id: str
    tag: str | None
    age: int
    covered: bool
    covered_whole: bool
    partial: float
    tokens: int
    middle: float | None


@dataclass(frozen=True, slots=True)
class PolicyResult:
    """One row of the sweep."""

    policy: str
    budget: int
    query_aware: bool
    probes: int
    recall: float
    recall_low: float
    recall_high: float
    whole_recall: float
    partial: float
    tokens: float
    compression: float
    middle_share: float
    recall_by_age: dict[str, float] = field(default_factory=dict)
    probes_by_age: dict[str, int] = field(default_factory=dict)
    recall_by_tag: dict[str, float] = field(default_factory=dict)


def bootstrap_ci(
    values: Sequence[float],
    seed: int = 0,
    resamples: int = 1000,
    level: float = 0.95,
) -> tuple[float, float]:
    """Percentile interval on a mean, from a seeded resample."""
    if not values:
        return (0.0, 0.0)
    rng = random.Random(seed)
    size = len(values)
    means = []
    for _ in range(resamples):
        total = 0.0
        for _ in range(size):
            total += values[rng.randrange(size)]
        means.append(total / size)
    means.sort()
    tail = (1.0 - level) / 2.0
    low = means[int(tail * (resamples - 1))]
    high = means[int((1.0 - tail) * (resamples - 1))]
    return (low, high)


def summarise(
    policy: str,
    budget: int,
    query_aware: bool,
    outcomes: Sequence[Outcome],
    full_tokens: float,
    seed: int = 0,
) -> PolicyResult:
    """Fold a policy's per-probe outcomes into one row."""
    if not outcomes:
        raise ValueError("no outcomes to summarise")
    covered = [1.0 if o.covered else 0.0 for o in outcomes]
    low, high = bootstrap_ci(covered, seed=seed)
    tokens = sum(o.tokens for o in outcomes) / len(outcomes)
    middles = [o.middle for o in outcomes if o.middle is not None]

    by_age: dict[str, list[float]] = {}
    for outcome in outcomes:
        by_age.setdefault(bucket_for(outcome.age), []).append(1.0 if outcome.covered else 0.0)
    by_tag: dict[str, list[float]] = {}
    for outcome in outcomes:
        if outcome.tag is not None:
            by_tag.setdefault(outcome.tag, []).append(1.0 if outcome.covered else 0.0)

    return PolicyResult(
        policy=policy,
        budget=budget,
        query_aware=query_aware,
        probes=len(outcomes),
        recall=sum(covered) / len(covered),
        recall_low=low,
        recall_high=high,
        whole_recall=sum(1 for o in outcomes if o.covered_whole) / len(outcomes),
        partial=sum(o.partial for o in outcomes) / len(outcomes),
        tokens=tokens,
        compression=(tokens / full_tokens) if full_tokens else 0.0,
        middle_share=(sum(middles) / len(middles)) if middles else 0.0,
        recall_by_age={k: sum(v) / len(v) for k, v in by_age.items()},
        probes_by_age={k: len(v) for k, v in by_age.items()},
        recall_by_tag={k: sum(v) / len(v) for k, v in by_tag.items()},
    )


def budget_for_recall(rows: Sequence[PolicyResult], policy: str, target: float) -> int | None:
    """The smallest swept budget at which a policy reaches a recall target."""
    reached = sorted(
        (r.budget for r in rows if r.policy == policy and r.recall >= target),
    )
    return reached[0] if reached else None
