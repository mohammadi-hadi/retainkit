"""What every context policy has to provide, and the budget arithmetic they share."""

from __future__ import annotations

from collections.abc import Iterable, Sequence
from typing import Protocol, runtime_checkable

from ..tokens import Tokenizer, char4, cost
from ..types import Fragment, Probe, Retained, Transcript, chronological

#: Sentences of one turn are ordered inside the slot reserved for that turn.
ORDER_STRIDE = 1000


def turn_fragments(transcript: Transcript) -> list[Fragment]:
    """One whole-turn fragment per turn, in conversation order."""
    return [
        Fragment(
            source_id=turn.id,
            session=turn.session,
            order=index * ORDER_STRIDE,
            text=turn.text,
            whole=True,
        )
        for index, turn in enumerate(transcript.turns)
    ]


def sentence_fragments(transcript: Transcript) -> list[Fragment]:
    """One fragment per sentence, carrying the turn it came from."""
    fragments: list[Fragment] = []
    for index, turn in enumerate(transcript.turns):
        sentences = turn.sentences()
        whole = len(sentences) == 1
        for ordinal, sentence in enumerate(sentences):
            fragments.append(
                Fragment(
                    source_id=turn.id,
                    session=turn.session,
                    order=index * ORDER_STRIDE + min(ordinal, ORDER_STRIDE - 1),
                    text=sentence,
                    whole=whole,
                )
            )
    return fragments


def fill(
    candidates: Iterable[Fragment],
    budget: int,
    tokenizer: Tokenizer = char4,
) -> tuple[list[Fragment], int]:
    """Take fragments in the order offered, skipping any that no longer fit.

    Skipping rather than stopping means a long fragment does not shut the door
    on the shorter ones behind it. It is greedy, and it is deterministic.
    """
    kept: list[Fragment] = []
    spent = 0
    for fragment in candidates:
        price = cost(fragment.text, tokenizer)
        if spent + price > budget:
            continue
        kept.append(fragment)
        spent += price
    return kept, spent


def spend(fragments: Sequence[Fragment], tokenizer: Tokenizer = char4) -> int:
    return sum(cost(f.text, tokenizer) for f in fragments)


@runtime_checkable
class Policy(Protocol):
    """Decides what part of a conversation the model still gets to see."""

    #: Name used in reports.
    name: str
    #: Whether the policy is allowed to look at the incoming question.
    query_aware: bool

    def select(
        self,
        transcript: Transcript,
        probe: Probe,
        budget: int,
        tokenizer: Tokenizer = char4,
    ) -> Retained: ...


def package(
    name: str,
    budget: int,
    fragments: Sequence[Fragment],
    tokenizer: Tokenizer = char4,
) -> Retained:
    """Put a selection back in conversation order and price it."""
    ordered = chronological(fragments)
    return Retained(policy=name, budget=budget, fragments=ordered, tokens=spend(ordered, tokenizer))
