"""Session summaries, without a model in the loop.

An abstractive summariser rewrites what it keeps, and a rewritten sentence
cannot be traced back to the turn it came from, so this package cannot score
one: every metric here asks whether a named span survived. The default is
therefore extractive — the opening sentences of each closed session, the
oldest and most standard compression baseline there is. Pass a ``selector`` to
swap in your own extractive scheme.
"""

from __future__ import annotations

from collections.abc import Callable, Sequence
from dataclasses import dataclass, field

from ..tokens import Tokenizer, char4
from ..types import Fragment, Probe, Retained, Transcript
from .base import fill, package, sentence_fragments, turn_fragments

Selector = Callable[[Sequence[Fragment], int], list[Fragment]]


def lead(fragments: Sequence[Fragment], per_session: int) -> list[Fragment]:
    """The first ``per_session`` sentences of a session, in order."""
    return list(fragments[:per_session])


@dataclass
class SessionSummary:
    """Summarise every closed session, keep the live one verbatim.

    The budget is split: ``recent_share`` for the session in progress, the rest
    spread evenly over the closed sessions so that an old session is not
    crowded out by a recent one.
    """

    per_session: int = 3
    recent_share: float = 0.4
    selector: Selector = field(default=lead)
    name: str = "session_summary"
    query_aware: bool = False

    def select(
        self,
        transcript: Transcript,
        probe: Probe,
        budget: int,
        tokenizer: Tokenizer = char4,
    ) -> Retained:
        if not transcript.turns:
            return package(self.name, budget, [], tokenizer)
        current = transcript.last_session
        live = [f for f in turn_fragments(transcript) if f.session == current]
        recent, recent_spend = fill(reversed(live), int(budget * self.recent_share), tokenizer)

        closed = [s for s in transcript.sessions if s != current]
        remaining = budget - recent_spend
        if not closed or remaining <= 0:
            return package(self.name, budget, recent, tokenizer)

        sentences = sentence_fragments(transcript)
        share = remaining // len(closed)
        kept: list[Fragment] = []
        carried = remaining - share * len(closed)
        for session in closed:
            in_session = [f for f in sentences if f.session == session]
            picked, spent = fill(self.selector(in_session, self.per_session), share + carried, tokenizer)
            kept.extend(picked)
            carried = share + carried - spent
        return package(self.name, budget, recent + kept, tokenizer)
