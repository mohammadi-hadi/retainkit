"""Context and memory policies for LLM agents, scored by what survives the budget."""

from .evaluate import DEFAULT_BUDGETS, Case, Report, run, score
from .io import dump_cases, load_cases
from .metrics import Outcome, PolicyResult, budget_for_recall
from .policies import (
    DEFAULT_POLICIES,
    FactMemory,
    HeadTail,
    KeepAll,
    Oracle,
    Policy,
    Recency,
    Retrieval,
    SessionSummary,
)
from .report import age_table, frontier_table, markdown, sweep_table, to_json
from .tokens import char4, wordish
from .types import Fragment, Probe, Retained, Transcript, Turn

__version__ = "0.1.0"

__all__ = [
    "DEFAULT_BUDGETS",
    "DEFAULT_POLICIES",
    "Case",
    "FactMemory",
    "Fragment",
    "HeadTail",
    "KeepAll",
    "Oracle",
    "Outcome",
    "Policy",
    "PolicyResult",
    "Probe",
    "Recency",
    "Report",
    "Retained",
    "Retrieval",
    "SessionSummary",
    "Transcript",
    "Turn",
    "__version__",
    "age_table",
    "budget_for_recall",
    "char4",
    "dump_cases",
    "frontier_table",
    "load_cases",
    "markdown",
    "run",
    "score",
    "sweep_table",
    "to_json",
    "wordish",
]
