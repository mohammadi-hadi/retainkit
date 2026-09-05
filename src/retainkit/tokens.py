"""Token accounting.

The default estimator is the usual four-characters-per-token approximation. It
is an estimate, not a tokenizer: absolute numbers move if you swap it. On the
fixture, changing estimator moves one policy's recall by 22 points, so treat any
single figure here as approximate and pass your model's own tokenizer through
``Tokenizer`` when it has to be exact. What does not move is the comparison:
``tests/test_tokens.py`` holds the two estimators to the same verdict about
which policies beat which.
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
