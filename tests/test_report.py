import json

from retainkit import DEFAULT_POLICIES, Case, Probe, Transcript, Turn, run
from retainkit.report import age_table, frontier_table, markdown, sweep_table, to_json

BUDGETS = (256, 1024)


def report():
    turns = [
        Turn(id=f"D{s}:{p}", session=s, speaker="guest", text=f"Session {s} turn {p} about trains.")
        for s in range(1, 6)
        for p in range(1, 5)
    ]
    probes = (Probe(id="q", question="Session 1 turn 1 trains", evidence=("D1:1",), tag="old"),)
    case = Case(transcript=Transcript(id="c", turns=tuple(turns)), probes=probes)
    return run([case], DEFAULT_POLICIES, BUDGETS)


def test_sweep_table_has_a_row_per_policy_and_budget():
    rows = [line for line in sweep_table(report()).splitlines() if line.startswith("| ")]
    assert len(rows) == 2 + len(DEFAULT_POLICIES) * len(BUDGETS)


def test_age_table_names_every_policy_and_counts_the_probes():
    table = age_table(report(), 1024)
    for policy in DEFAULT_POLICIES:
        assert f"`{policy.name}`" in table
    assert "_probes_" in table


def test_frontier_table_says_when_a_target_is_never_reached():
    table = frontier_table(report(), targets=(1.01,))
    assert "not reached" in table


def test_markdown_carries_the_notes_and_the_three_tables():
    text = markdown(report(), "Title", 1024)
    assert text.startswith("# Title")
    assert "Recall against budget" in text
    assert "Recall by how old the evidence is" in text
    assert "Cheapest budget" in text


def test_json_is_sorted_and_round_trips():
    payload = json.loads(to_json(report()))
    assert payload["budgets"] == list(BUDGETS)
    assert payload["tokenizer"] == "char4"
    assert len(payload["rows"]) == len(DEFAULT_POLICIES) * len(BUDGETS)
    assert to_json(report()) == to_json(report())
