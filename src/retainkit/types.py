"""Core records: a transcript of turns, a probe over it, and what a policy keeps."""

from __future__ import annotations

import re
from collections.abc import Iterable, Iterator, Sequence
from dataclasses import dataclass, field

_SENTENCE_END = re.compile(r"(?<=[.!?])\s+")


@dataclass(frozen=True, slots=True)
class Turn:
    """One utterance in one session of a conversation."""

    id: str
    session: int
    speaker: str
    text: str
    timestamp: str | None = None

    def sentences(self) -> list[str]:
        """Split the turn into sentences, keeping order and dropping empties."""
        parts = [p.strip() for p in _SENTENCE_END.split(self.text.strip())]
        return [p for p in parts if p]


@dataclass(frozen=True, slots=True)
class Transcript:
    """An ordered conversation, grouped into sessions."""

    id: str
    turns: tuple[Turn, ...]

    def __post_init__(self) -> None:
        seen: set[str] = set()
        for turn in self.turns:
            if turn.id in seen:
                raise ValueError(f"duplicate turn id {turn.id!r} in transcript {self.id!r}")
            seen.add(turn.id)

    def __len__(self) -> int:
        return len(self.turns)

    def __iter__(self) -> Iterator[Turn]:
        return iter(self.turns)

    @property
    def sessions(self) -> tuple[int, ...]:
        """Every session number that appears, in ascending order."""
        return tuple(sorted({t.session for t in self.turns}))

    @property
    def last_session(self) -> int:
        if not self.turns:
            raise ValueError("empty transcript has no last session")
        return self.sessions[-1]

    def by_id(self, turn_id: str) -> Turn:
        for turn in self.turns:
            if turn.id == turn_id:
                return turn
        raise KeyError(turn_id)

    def index_of(self, turn_id: str) -> int:
        for position, turn in enumerate(self.turns):
            if turn.id == turn_id:
                return position
        raise KeyError(turn_id)

    @classmethod
    def from_turns(cls, transcript_id: str, turns: Iterable[Turn]) -> Transcript:
        """Build a transcript, sorting turns by session and original order."""
        ordered = tuple(sorted(turns, key=lambda t: (t.session,)))
        return cls(id=transcript_id, turns=ordered)


@dataclass(frozen=True, slots=True)
class Probe:
    """A question whose answer is supported by named turns of the transcript.

    ``evidence`` holds turn ids. A probe is used to ask what a context policy
    would still have in front of the model at the moment the question arrives.
    """

    id: str
    question: str
    evidence: tuple[str, ...]
    answer: str | None = None
    tag: str | None = None

    def __post_init__(self) -> None:
        if not self.evidence:
            raise ValueError(f"probe {self.id!r} has no evidence turns")


@dataclass(frozen=True, slots=True)
class Fragment:
    """A piece of retained context and the turn it came from.

    A policy that keeps whole turns emits fragments with ``whole=True``. One
    that keeps sentences, or a summary built out of them, emits ``whole=False``
    so that partial survival stays visible in the metrics.
    """

    source_id: str
    session: int
    order: int
    text: str
    whole: bool = True


@dataclass(frozen=True, slots=True)
class Retained:
    """What one policy handed to the model for one probe, under one budget."""

    policy: str
    budget: int
    fragments: tuple[Fragment, ...] = field(default_factory=tuple)
    tokens: int = 0

    @property
    def source_ids(self) -> frozenset[str]:
        return frozenset(f.source_id for f in self.fragments)

    @property
    def whole_source_ids(self) -> frozenset[str]:
        return frozenset(f.source_id for f in self.fragments if f.whole)

    def position_of(self, source_id: str) -> int | None:
        """Where a turn's first surviving fragment sits in the retained context."""
        for position, fragment in enumerate(self.fragments):
            if fragment.source_id == source_id:
                return position
        return None


def chronological(fragments: Sequence[Fragment]) -> tuple[Fragment, ...]:
    """Restore conversation order after a policy has selected out of sequence."""
    return tuple(sorted(fragments, key=lambda f: (f.order, f.source_id)))
