from retainkit import DEFAULT_BUDGETS, DEFAULT_POLICIES, char4, run, wordish
from retainkit.demo import build_cases
from retainkit.tokens import FRAGMENT_OVERHEAD, cost

AWARE = ("retrieval", "fact_memory", "oracle")
BLIND = ("recency", "head_tail", "session_summary")


def test_estimators_are_positive_and_grow_with_text():
    for estimator in (char4, wordish):
        assert estimator("") >= 1
        assert estimator("a short line") < estimator("a considerably longer line of prose here")


def test_cost_charges_the_fragment_overhead():
    assert cost("hello", char4) == char4("hello") + FRAGMENT_OVERHEAD


def test_both_estimators_give_the_same_verdict():
    """Absolute recall moves with the estimator; which policies win does not."""
    cases = build_cases(count=3, sessions=8, turns_per_session=12, seed=11)
    for estimator in (char4, wordish):
        report = run(cases, DEFAULT_POLICIES, DEFAULT_BUDGETS[:4], tokenizer=estimator)
        for budget in report.budgets:
            scores = {r.policy: r.recall for r in report.by_budget(budget)}
            aware = min(scores[p] for p in AWARE)
            blind = max(scores[p] for p in BLIND)
            # A budget wide enough for the whole conversation saturates every
            # policy, so the ordering is only strict while the budget bites.
            assert aware >= blind
            if budget == report.budgets[0]:
                assert aware > blind
