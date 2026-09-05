from retainkit.bm25 import BM25, tokenize


def test_tokenize_lowercases_and_drops_punctuation():
    assert tokenize("Hello, World! 42") == ["hello", "world", "42"]


def test_the_matching_document_ranks_first():
    index = BM25(
        [
            "the weather was fine that week",
            "Nadia has a shellfish allergy",
            "we can decide about the second night",
        ]
    )
    assert index.ranked("what is Nadia allergic to shellfish")[0] == 1


def test_empty_query_scores_zero_and_keeps_original_order():
    index = BM25(["one two", "three four"])
    assert index.scores("") == [0.0, 0.0]
    assert index.ranked("") == [0, 1]


def test_ties_break_on_document_order():
    index = BM25(["same words here", "same words here"])
    assert index.ranked("same words") == [0, 1]


def test_empty_index_is_safe():
    assert BM25([]).ranked("anything") == []
