"""Policies that do not look at the question: keep everything, keep the end, keep both ends."""

from __future__ import annotations

from dataclasses import dataclass

from ..tokens import Tokenizer, char4
from ..types import Probe, Retained, Transcript
from .base import fill, package, turn_fragments


@dataclass
class KeepAll:
    """No management at all. Useful as the reference cost of a conversation."""

    name: str = "keep_all"
    query_aware: bool = False

    def select(
        self,
        transcript: Transcript,
        probe: Probe,
        budget: int,
        tokenizer: Tokenizer = char4,
    ) -> Retained:
        return package(self.name, budget, turn_fragments(transcript), tokenizer)


@dataclass
class Recency:
    """The sliding window every agent framework starts with: keep the newest turns."""

    name: str = "recency"
    query_aware: bool = False

    def select(
        self,
        transcript: Transcript,
        probe: Probe,
        budget: int,
        tokenizer: Tokenizer = char4,
    ) -> Retained:
        kept, _ = fill(reversed(turn_fragments(transcript)), budget, tokenizer)
        return package(self.name, budget, kept, tokenizer)


@dataclass
class HeadTail:
    """Keep the opening of the conversation and its most recent turns.

    The opening usually carries the standing facts about a user, which a plain
    window drops first.
    """

    head_share: float = 0.3
    name: str = "head_tail"
    query_aware: bool = False

    def __post_init__(self) -> None:
        if not 0.0 <= self.head_share <= 1.0:
            raise ValueError("head_share must be between 0 and 1")

    def select(
        self,
        transcript: Transcript,
        probe: Probe,
        budget: int,
        tokenizer: Tokenizer = char4,
    ) -> Retained:
        fragments = turn_fragments(transcript)
        head_budget = int(budget * self.head_share)
        head, head_spend = fill(fragments, head_budget, tokenizer)
        taken = {f.order for f in head}
        tail_candidates = [f for f in reversed(fragments) if f.order not in taken]
        tail, _ = fill(tail_candidates, budget - head_spend, tokenizer)
        return package(self.name, budget, head + tail, tokenizer)
