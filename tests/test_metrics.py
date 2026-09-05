import pytest

from retainkit.metrics import Outcome, bootstrap_ci, bucket_for, budget_for_recall, summarise
from retainkit.report import PolicyResult


def outcome(covered=True, age=0, tokens=100, tag="single", whole=True, partial=1.0, middle=0.5):
    return Outcome(
        probe_id="q",
        tag=tag,
        age=age,
        covered=covered,
        covered_whole=whole,
        partial=partial,
        tokens=tokens,
        middle=middle,
    )


def test_buckets_cover_every_age():
    assert bucket_for(0) == "same session"
    assert bucket_for(2) == "1-2 back"
    assert bucket_for(4) == "3-5 back"
    assert bucket_for(9) == "6-10 back"
    assert bucket_for(40) == "11+ back"


def test_bucket_refuses_a_negative_age():
    with pytest.raises(ValueError, match="no bucket"):
        bucket_for(-1)


def test_bootstrap_is_seeded_and_brackets_the_mean():
    values = [1.0] * 7 + [0.0] * 3
    low, high = bootstrap_ci(values, seed=4)
    assert bootstrap_ci(values, seed=4) == (low, high)
    assert low <= 0.7 <= high
    assert bootstrap_ci([], seed=4) == (0.0, 0.0)


def test_bootstrap_on_a_constant_sample_has_no_width():
    assert bootstrap_ci([1.0] * 5) == (1.0, 1.0)


def test_summarise_folds_outcomes_into_one_row():
    outcomes = [
        outcome(covered=True, age=0),
        outcome(covered=False, age=7, partial=0.0, middle=None),
    ]
    row = summarise("p", 512, True, outcomes, full_tokens=1000.0)
    assert isinstance(row, PolicyResult)
    assert row.probes == 2
    assert row.recall == 0.5
    assert row.partial == 0.5
    assert row.compression == pytest.approx(0.1)
    assert row.recall_by_age == {"same session": 1.0, "6-10 back": 0.0}
    assert row.probes_by_age == {"same session": 1, "6-10 back": 1}
    assert row.recall_by_tag == {"single": 0.5}


def test_summarise_needs_outcomes():
    with pytest.raises(ValueError, match="no outcomes"):
        summarise("p", 512, True, [], full_tokens=1.0)


def test_budget_for_recall_takes_the_cheapest_hit():
    rows = [
        PolicyResult("p", 512, True, 10, 0.4, 0.3, 0.5, 0.4, 0.4, 100, 0.1, 0.0),
        PolicyResult("p", 1024, True, 10, 0.9, 0.8, 1.0, 0.9, 0.9, 200, 0.2, 0.0),
        PolicyResult("p", 2048, True, 10, 0.95, 0.9, 1.0, 0.95, 0.95, 400, 0.4, 0.0),
    ]
    assert budget_for_recall(rows, "p", 0.8) == 1024
    assert budget_for_recall(rows, "p", 0.99) is None
