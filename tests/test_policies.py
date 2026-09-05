import pytest

from retainkit import (
    FactMemory,
    HeadTail,
    KeepAll,
    Oracle,
    Probe,
    Recency,
    Retrieval,
    SessionSummary,
    Transcript,
    Turn,
    char4,
)
from retainkit.policies import DEFAULT_POLICIES
from retainkit.policies.base import fill, turn_fragments
from retainkit.tokens import cost

BUDGET = 200


def transcript(sessions=4, per_session=5):
    turns = [
        Turn(
            id=f"D{s}:{p}",
            session=s,
            speaker="guest",
            text=f"Session {s} turn {p} says something about the trip. And a second sentence.",
        )
        for s in range(1, sessions + 1)
        for p in range(1, per_session + 1)
    ]
    return Transcript(id="c", turns=tuple(turns))


PROBE = Probe(id="q", question="Session 1 turn 2 trip", evidence=("D1:2",))


@pytest.mark.parametrize("policy", DEFAULT_POLICIES, ids=lambda p: p.name)
def test_every_policy_stays_inside_the_budget(policy):
    retained = policy.select(transcript(), PROBE, BUDGET, char4)
    assert retained.tokens <= BUDGET
    assert retained.budget == BUDGET


@pytest.mark.parametrize("policy", DEFAULT_POLICIES, ids=lambda p: p.name)
def test_every_policy_returns_context_in_conversation_order(policy):
    retained = policy.select(transcript(), PROBE, BUDGET, char4)
    orders = [f.order for f in retained.fragments]
    assert orders == sorted(orders)


def test_recency_keeps_the_end_of_the_conversation():
    retained = Recency().select(transcript(), PROBE, BUDGET, char4)
    assert retained.fragments[-1].source_id == "D4:5"
    assert "D1:1" not in retained.source_ids


def test_head_tail_keeps_both_ends():
    retained = HeadTail(head_share=0.5).select(transcript(), PROBE, BUDGET, char4)
    assert "D1:1" in retained.source_ids
    assert "D4:5" in retained.source_ids


def test_oracle_keeps_the_evidence_and_little_else():
    retained = Oracle().select(transcript(), PROBE, BUDGET, char4)
    assert retained.source_ids == {"D1:2"}


def test_retrieval_finds_old_evidence_a_window_would_drop():
    retained = Retrieval().select(transcript(), PROBE, BUDGET, char4)
    assert "D1:2" in retained.source_ids


def test_fact_memory_keeps_the_live_session_and_reaches_back():
    retained = FactMemory().select(transcript(), PROBE, BUDGET, char4)
    assert any(f.session == 4 for f in retained.fragments)
    assert "D1:2" in retained.source_ids


def test_session_summary_marks_partial_fragments():
    retained = SessionSummary().select(transcript(), PROBE, BUDGET, char4)
    assert any(not f.whole for f in retained.fragments)


def test_keep_all_returns_the_whole_conversation():
    t = transcript()
    retained = KeepAll().select(t, PROBE, BUDGET, char4)
    assert len(retained.fragments) == len(t)


def test_policies_survive_an_empty_transcript():
    empty = Transcript(id="c", turns=())
    for policy in (FactMemory(), SessionSummary()):
        assert policy.select(empty, PROBE, BUDGET, char4).fragments == ()


def test_fill_skips_a_fragment_that_no_longer_fits():
    fragments = turn_fragments(transcript(sessions=1, per_session=3))
    room = cost(fragments[0].text, char4) + 1
    kept, spent = fill(fragments, room, char4)
    assert len(kept) == 1
    assert spent <= room


def test_head_share_is_validated():
    with pytest.raises(ValueError, match="head_share"):
        HeadTail(head_share=1.5)
    with pytest.raises(ValueError, match="recent_share"):
        FactMemory(recent_share=-0.1)
