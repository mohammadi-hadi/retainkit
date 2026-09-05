from retainkit import Case, Probe, Recency, Retrieval, Transcript, Turn, char4, run
from retainkit.evaluate import evidence_age, middle_share, score
from retainkit.types import Fragment, Retained


def case(sessions=5, per_session=4):
    turns = [
        Turn(id=f"D{s}:{p}", session=s, speaker="guest", text=f"Session {s} turn {p} about trains.")
        for s in range(1, sessions + 1)
        for p in range(1, per_session + 1)
    ]
    probes = (
        Probe(id="old", question="Session 1 turn 1 trains", evidence=("D1:1",), tag="old"),
        Probe(id="new", question="Session 5 turn 4 trains", evidence=("D5:4",), tag="new"),
    )
    return Case(transcript=Transcript(id="c", turns=tuple(turns)), probes=probes)


def test_evidence_age_counts_sessions_back_from_the_end():
    c = case()
    assert evidence_age(c.transcript, c.probes[0]) == 4
    assert evidence_age(c.transcript, c.probes[1]) == 0


def test_evidence_age_of_an_unknown_turn_is_zero():
    c = case()
    probe = Probe(id="x", question="?", evidence=("nope",))
    assert evidence_age(c.transcript, probe) == 0


def test_middle_share_is_none_when_nothing_survived():
    empty = Retained(policy="p", budget=10, fragments=(), tokens=0)
    assert middle_share(empty, case().probes[0]) is None


def test_middle_share_flags_evidence_buried_in_the_middle():
    fragments = tuple(
        Fragment(source_id=f"D1:{i}", session=1, order=i, text="x") for i in range(1, 9)
    )
    retained = Retained(policy="p", budget=99, fragments=fragments, tokens=8)
    middle = Probe(id="m", question="?", evidence=("D1:4",))
    edge = Probe(id="e", question="?", evidence=("D1:1",))
    assert middle_share(retained, middle) == 1.0
    assert middle_share(retained, edge) == 0.0


def test_score_reports_partial_coverage():
    c = case()
    probe = Probe(id="both", question="?", evidence=("D1:1", "D5:4"))
    retained = Recency().select(c.transcript, probe, 200, char4)
    outcome = score(retained, c.transcript, probe)
    assert outcome.covered is False
    assert 0.0 < outcome.partial < 1.0


def test_run_sweeps_every_policy_and_budget():
    report = run([case()], (Recency(), Retrieval()), (128, 4096))
    assert report.cases == 1
    assert report.probes == 2
    assert {r.policy for r in report.rows} == {"recency", "retrieval"}
    assert len(report.by_budget(128)) == 2
    assert len(report.by_policy("recency")) == 2


def test_recall_never_falls_as_the_budget_grows():
    budgets = (128, 256, 512, 1024, 4096)
    report = run([case()], (Recency(),), budgets)
    recalls = [report.by_budget(b)[0].recall for b in budgets]
    assert recalls == sorted(recalls)


def test_run_needs_at_least_one_case():
    try:
        run([], (Recency(),), (128,))
    except ValueError as error:
        assert "nothing to evaluate" in str(error)
    else:  # pragma: no cover
        raise AssertionError("expected a ValueError")
