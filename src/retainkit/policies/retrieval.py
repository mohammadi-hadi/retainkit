"""Policies that read the incoming question before deciding what to keep."""

from __future__ import annotations

from dataclasses import dataclass

from ..bm25 import BM25
from ..tokens import Tokenizer, char4
from ..types import Fragment, Probe, Retained, Transcript
from .base import fill, package, sentence_fragments, turn_fragments


@dataclass
class Retrieval:
    """Rank whole turns against the question and keep the best ones that fit.

    Selection is out of order; the kept turns are put back in conversation
    order before the model sees them.
    """

    name: str = "retrieval"
    query_aware: bool = True

    def select(
        self,
        transcript: Transcript,
        probe: Probe,
        budget: int,
        tokenizer: Tokenizer = char4,
    ) -> Retained:
        fragments = turn_fragments(transcript)
        index = BM25([f.text for f in fragments])
        ranked = [fragments[i] for i in index.ranked(probe.question)]
        kept, _ = fill(ranked, budget, tokenizer)
        return package(self.name, budget, kept, tokenizer)


@dataclass
class FactMemory:
    """A long-term store beside the live session.

    Everything before the most recent session is broken into sentences and kept
    in a store that is searched when a question arrives; the most recent session
    stays in front of the model verbatim. ``recent_share`` is the part of the
    budget the live session gets, and whatever it does not use goes to the store.
    """

    recent_share: float = 0.4
    name: str = "fact_memory"
    query_aware: bool = True

    def __post_init__(self) -> None:
        if not 0.0 <= self.recent_share <= 1.0:
            raise ValueError("recent_share must be between 0 and 1")

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

        stored: list[Fragment] = [f for f in sentence_fragments(transcript) if f.session != current]
        if not stored:
            return package(self.name, budget, recent, tokenizer)
        index = BM25([f.text for f in stored])
        ranked = [stored[i] for i in index.ranked(probe.question)]
        recalled, _ = fill(ranked, budget - recent_spend, tokenizer)
        return package(self.name, budget, recent + recalled, tokenizer)


@dataclass
class Oracle:
    """Keep the evidence and nothing else: the cheapest context that can work.

    It cannot be run in production — it reads the answer key — but it is the
    floor every other policy is priced against.
    """

    name: str = "oracle"
    query_aware: bool = True

    def select(
        self,
        transcript: Transcript,
        probe: Probe,
        budget: int,
        tokenizer: Tokenizer = char4,
    ) -> Retained:
        wanted = set(probe.evidence)
        fragments = [f for f in turn_fragments(transcript) if f.source_id in wanted]
        kept, _ = fill(fragments, budget, tokenizer)
        return package(self.name, budget, kept, tokenizer)
