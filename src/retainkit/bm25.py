"""Okapi BM25 over short documents, standard library only.

Ties are broken by document index so that a ranking is reproducible on any
machine and any Python build.
"""

from __future__ import annotations

import math
import re
from collections import Counter
from collections.abc import Sequence
from dataclasses import dataclass

_TOKEN = re.compile(r"[a-z0-9]+")

K1 = 1.5
B = 0.75


def tokenize(text: str) -> list[str]:
    return _TOKEN.findall(text.lower())


@dataclass
class BM25:
    """A small BM25 index built once and queried many times."""

    documents: Sequence[str]
    k1: float = K1
    b: float = B

    def __post_init__(self) -> None:
        self._tokens = [tokenize(d) for d in self.documents]
        self._lengths = [len(t) for t in self._tokens]
        self._avg_length = (sum(self._lengths) / len(self._lengths)) if self._lengths else 0.0
        self._frequencies = [Counter(t) for t in self._tokens]
        document_frequency: Counter[str] = Counter()
        for counts in self._frequencies:
            document_frequency.update(counts.keys())
        total = len(self.documents)
        self._idf = {
            term: math.log(1 + (total - freq + 0.5) / (freq + 0.5))
            for term, freq in document_frequency.items()
        }

    def scores(self, query: str) -> list[float]:
        terms = tokenize(query)
        results = [0.0] * len(self.documents)
        if not terms or self._avg_length == 0.0:
            return results
        for index, counts in enumerate(self._frequencies):
            length = self._lengths[index]
            total = 0.0
            for term in terms:
                frequency = counts.get(term, 0)
                if not frequency:
                    continue
                denominator = frequency + self.k1 * (
                    1 - self.b + self.b * length / self._avg_length
                )
                total += self._idf[term] * frequency * (self.k1 + 1) / denominator
            results[index] = total
        return results

    def ranked(self, query: str) -> list[int]:
        """Document indices, best first, ties broken by original order."""
        scored = self.scores(query)
        return sorted(range(len(scored)), key=lambda i: (-scored[i], i))
