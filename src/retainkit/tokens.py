"""Token accounting.

The default estimator is the usual four-characters-per-token approximation. It
is an estimate, not a tokenizer: absolute budgets move if you swap it, so any
count reported by this package is only as exact as the callable behind it. Pass
your model's own tokenizer through ``Tokenizer`` when the exact number matters.
``tests/test_tokens.py`` checks that the policy ordering this package reports is
the same under both estimators shipped here.
"""

from __future__ import annotations

import math
import re
from collections.abc import Callable

Tokenizer = Callable[[str], int]

#: Tokens charged for the speaker label and separators around every fragment.
FRAGMENT_OVERHEAD = 4

_WORD = re.compile(r"\w+|[^\w\s]")


def char4(text: str) -> int:
    """Four characters per token, the common rule of thumb for English prose."""
    return max(1, math.ceil(len(text) / 4))


def wordish(text: str) -> int:
    """Words and punctuation, inflated by the usual 4/3 sub-word factor."""
    return max(1, math.ceil(len(_WORD.findall(text)) * 4 / 3))


def cost(text: str, tokenizer: Tokenizer = char4, overhead: int = FRAGMENT_OVERHEAD) -> int:
    """What one fragment costs once its speaker label and separators are counted."""
    return tokenizer(text) + overhead
