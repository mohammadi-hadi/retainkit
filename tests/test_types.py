import pytest

from retainkit import Probe, Transcript, Turn


def turn(turn_id="D1:1", session=1, text="Hello there."):
    return Turn(id=turn_id, session=session, speaker="guest", text=text)


def test_sentences_split_and_drop_empties():
    t = turn(text="One thing.  And another!  ")
    assert t.sentences() == ["One thing.", "And another!"]


def test_single_sentence_turn():
    assert turn(text="Just this").sentences() == ["Just this"]


def test_duplicate_turn_ids_are_refused():
    with pytest.raises(ValueError, match="duplicate turn id"):
        Transcript(id="c", turns=(turn(), turn()))


def test_sessions_and_last_session():
    t = Transcript(
        id="c",
        turns=(turn("D1:1", 1), turn("D3:1", 3), turn("D2:1", 2)),
    )
    assert t.sessions == (1, 2, 3)
    assert t.last_session == 3


def test_lookup_by_id():
    t = Transcript(id="c", turns=(turn("D1:1"), turn("D1:2")))
    assert t.by_id("D1:2").id == "D1:2"
    assert t.index_of("D1:2") == 1
    with pytest.raises(KeyError):
        t.by_id("nope")


def test_probe_needs_evidence():
    with pytest.raises(ValueError, match="no evidence"):
        Probe(id="q", question="?", evidence=())
