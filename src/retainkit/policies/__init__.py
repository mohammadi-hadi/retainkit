"""The context policies this package compares."""

from .base import ORDER_STRIDE, Policy, fill, package, sentence_fragments, spend, turn_fragments
from .retrieval import FactMemory, Oracle, Retrieval
from .simple import HeadTail, KeepAll, Recency
from .summary import SessionSummary, lead

#: The set reported by ``retainkit demo`` and by the LoCoMo example.
DEFAULT_POLICIES: tuple[Policy, ...] = (
    Recency(),
    HeadTail(),
    SessionSummary(),
    Retrieval(),
    FactMemory(),
    Oracle(),
)

__all__ = [
    "DEFAULT_POLICIES",
    "ORDER_STRIDE",
    "FactMemory",
    "HeadTail",
    "KeepAll",
    "Oracle",
    "Policy",
    "Recency",
    "Retrieval",
    "SessionSummary",
    "fill",
    "lead",
    "package",
    "sentence_fragments",
    "spend",
    "turn_fragments",
]
