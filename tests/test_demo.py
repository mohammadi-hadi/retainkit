from retainkit.cli import main
from retainkit.demo import build_cases


def test_the_fixture_is_the_same_every_time():
    first = build_cases(count=2, sessions=6, turns_per_session=8, seed=5)
    second = build_cases(count=2, sessions=6, turns_per_session=8, seed=5)
    assert [t.text for t in first[0].transcript] == [t.text for t in second[0].transcript]
    assert [p.question for p in first[0].probes] == [p.question for p in second[0].probes]


def test_a_different_seed_gives_a_different_conversation():
    a = build_cases(count=1, sessions=6, turns_per_session=8, seed=5)
    b = build_cases(count=1, sessions=6, turns_per_session=8, seed=6)
    assert [t.text for t in a[0].transcript] != [t.text for t in b[0].transcript]


def test_every_probe_points_at_a_turn_that_exists():
    for case in build_cases(count=2, sessions=6, turns_per_session=8, seed=5):
        ids = {t.id for t in case.transcript}
        for probe in case.probes:
            assert set(probe.evidence) <= ids


def test_the_last_session_carries_no_planted_fact():
    case = build_cases(count=1, sessions=6, turns_per_session=8, seed=5)[0]
    last = case.transcript.last_session
    assert all(case.transcript.by_id(e).session != last for p in case.probes for e in p.evidence)


def test_demo_command_writes_the_three_result_files(tmp_path, capsys):
    assert main(["demo", "--out", str(tmp_path), "--seed", "3"]) == 0
    assert {p.name for p in tmp_path.iterdir()} == {"table.md", "report.md", "demo.json"}
    assert "Evidence recall" in capsys.readouterr().out


def test_eval_command_reads_a_case_file(tmp_path, capsys):
    from retainkit import dump_cases

    path = tmp_path / "cases.json"
    dump_cases(build_cases(count=1, sessions=5, turns_per_session=6, seed=2), path)
    assert main(["eval", str(path), "--budget", "512", "--tokenizer", "wordish"]) == 0
    assert "Recall against budget" in capsys.readouterr().out
