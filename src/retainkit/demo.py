"""A synthetic fixture, built from a fixed seed, that CI diffs.

It is not a benchmark. It exists so that a change to a policy or a metric shows
up as a moved number in `results/`, and so the package can be tried without
downloading anything. The measured claims in the README come from LoCoMo, in
`examples/locomo/`.

The shape is the one a travel assistant meets: a standing fact about a
traveller stated once, small talk that mentions the same people, near misses
that use the same words as the question without answering it, and the question
arriving many sessions later.
"""

from __future__ import annotations

import random

from .evaluate import Case
from .types import Probe, Transcript, Turn

FACTS: tuple[tuple[str, str, str, str], ...] = (
    ("Nadia", "allergy", "shellfish", "What allergy does Nadia have?"),
    ("Nadia", "seat", "aisle", "Which seat does Nadia book?"),
    ("Tomas", "city", "Ljubljana", "Which city does Tomas return to?"),
    ("Tomas", "loyalty", "Genius", "Which loyalty tier does Tomas hold?"),
    ("Priya", "budget", "ninety euro", "What budget does Priya keep to?"),
    ("Priya", "checkin", "late", "What check-in does Priya ask for?"),
    ("Bram", "transport", "night train", "What transport does Bram prefer?"),
    ("Bram", "room", "courtyard", "What room does Bram ask for?"),
    ("Lena", "diet", "vegetarian", "What diet does Lena follow?"),
    ("Lena", "trip", "walking", "What trip is Lena planning?"),
    ("Sofia", "airport", "Schiphol", "Which airport does Sofia fly from?"),
    ("Sofia", "luggage", "cabin only", "What luggage does Sofia travel with?"),
    ("Ivan", "payment", "invoice", "What payment does Ivan use?"),
    ("Ivan", "insurance", "annual", "What insurance does Ivan hold?"),
    ("Mira", "language", "Portuguese", "What language does Mira speak?"),
    ("Mira", "weekend", "shoulder season", "What weekend does Mira book?"),
)

CHAFF: tuple[str, ...] = (
    "That sounds good, let me look at the dates again.",
    "The weather looked fine for that week when I checked.",
    "I will send the confirmation over once it comes through.",
    "We can decide about the second night later.",
    "It was busier than last time, but not by much.",
    "I still have to sort out the trains on the way back.",
    "No rush, whenever you get a moment.",
    "Someone said the market is worth an early start.",
    "I forgot to mention it earlier, sorry about that.",
    "Fine by me either way, you choose.",
)

NAMED_CHAFF: tuple[str, ...] = (
    "{person} said the same thing about the last trip.",
    "I should check with {person} before anything is confirmed.",
    "{person} was happy with how the previous booking went.",
    "We spoke to {person} about the dates but nothing is fixed.",
)


def _statement(person: str, attribute: str, value: str) -> str:
    return f"Note for the file: {person} has a {attribute} of {value}, so book accordingly."


def _near_miss(person: str, attribute: str) -> str:
    """Same words as the question, no answer in it — what retrieval has to beat."""
    return f"Note for the file: {person} raised the {attribute} again, nothing fixed yet."


def build_case(
    case_id: str,
    sessions: int,
    turns_per_session: int,
    rng: random.Random,
) -> Case:
    """One conversation with a fact planted in each session but the last."""
    facts = list(FACTS)
    rng.shuffle(facts)
    planted = facts[: min(len(facts), sessions - 1)]

    turns: list[Turn] = []
    probes: list[Probe] = []
    for session in range(1, sessions + 1):
        fact_at = 1 + (session * 5) % turns_per_session
        miss_at = {1 + (session * 7 + offset) % turns_per_session for offset in (3, 9, 15)} - {
            fact_at
        }
        for position in range(1, turns_per_session + 1):
            turn_id = f"D{session}:{position}"
            speaker = "guest" if position % 2 else "agent"
            if session <= len(planted) and position == fact_at:
                person, attribute, value, question = planted[session - 1]
                text = _statement(person, attribute, value)
                probes.append(
                    Probe(
                        id=f"{case_id}-q{session}",
                        question=question,
                        evidence=(turn_id,),
                        answer=value,
                        tag=attribute,
                    )
                )
            elif session > 1 and position in miss_at:
                person, attribute, _, _ = planted[rng.randrange(min(session - 1, len(planted)))]
                text = _near_miss(person, attribute)
            elif rng.random() < 0.25:
                person = planted[rng.randrange(len(planted))][0]
                text = rng.choice(NAMED_CHAFF).format(person=person)
            else:
                text = rng.choice(CHAFF)
            turns.append(Turn(id=turn_id, session=session, speaker=speaker, text=text))
    return Case(transcript=Transcript(id=case_id, turns=tuple(turns)), probes=tuple(probes))


def build_cases(
    count: int = 8,
    sessions: int = 16,
    turns_per_session: int = 24,
    seed: int = 7,
) -> list[Case]:
    """The fixture used by ``retainkit demo``."""
    rng = random.Random(seed)
    return [build_case(f"case-{i + 1}", sessions, turns_per_session, rng) for i in range(count)]
