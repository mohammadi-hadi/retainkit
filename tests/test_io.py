import json

from retainkit import dump_cases, load_cases
from retainkit.demo import build_cases
from retainkit.io import case_from_dict


def test_cases_round_trip_through_json(tmp_path):
    original = build_cases(count=2, sessions=4, turns_per_session=5, seed=1)
    path = tmp_path / "cases.json"
    dump_cases(original, path)
    loaded = load_cases(path)
    assert [c.transcript.id for c in loaded] == [c.transcript.id for c in original]
    assert [len(c.transcript) for c in loaded] == [len(c.transcript) for c in original]
    assert [len(c.probes) for c in loaded] == [len(c.probes) for c in original]


def test_a_bare_list_of_cases_is_accepted(tmp_path):
    path = tmp_path / "cases.json"
    path.write_text(
        json.dumps(
            [{"id": "c", "turns": [{"id": "D1:1", "session": 1, "text": "hello"}], "probes": []}]
        )
    )
    assert len(load_cases(path)) == 1


def test_probes_whose_evidence_is_missing_are_dropped():
    case = case_from_dict(
        {
            "id": "c",
            "turns": [{"id": "D1:1", "session": 1, "speaker": "guest", "text": "hello"}],
            "probes": [
                {"id": "keep", "question": "?", "evidence": ["D1:1", "gone"]},
                {"id": "drop", "question": "?", "evidence": ["gone"]},
            ],
        }
    )
    assert [p.id for p in case.probes] == ["keep"]
    assert case.probes[0].evidence == ("D1:1",)
