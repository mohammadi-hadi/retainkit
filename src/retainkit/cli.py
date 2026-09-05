"""Command line: run the fixture, or run a sweep over your own conversations."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from .demo import build_cases
from .evaluate import DEFAULT_BUDGETS, run
from .io import load_cases
from .policies import DEFAULT_POLICIES
from .report import markdown, sweep_table, to_json
from .tokens import char4, wordish

TOKENIZERS = {"char4": char4, "wordish": wordish}


def _write(report, out: Path, title: str, focus: int, stem: str) -> None:
    out.mkdir(parents=True, exist_ok=True)
    (out / "table.md").write_text(sweep_table(report) + "\n", encoding="utf-8")
    (out / "report.md").write_text(markdown(report, title, focus) + "\n", encoding="utf-8")
    (out / f"{stem}.json").write_text(to_json(report), encoding="utf-8")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="retainkit", description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)

    demo = sub.add_parser("demo", help="run the built-in fixture and write results")
    demo.add_argument("--out", default="results", type=Path)
    demo.add_argument("--seed", default=7, type=int)
    demo.add_argument("--tokenizer", default="char4", choices=sorted(TOKENIZERS))

    evaluate = sub.add_parser("eval", help="sweep policies over conversations in a JSON file")
    evaluate.add_argument("cases", type=Path)
    evaluate.add_argument("--out", default=None, type=Path)
    evaluate.add_argument("--title", default="retainkit sweep")
    evaluate.add_argument("--tokenizer", default="char4", choices=sorted(TOKENIZERS))
    evaluate.add_argument(
        "--budget",
        action="append",
        type=int,
        help="repeat to sweep several budgets; defaults to 256 … 8192",
    )

    args = parser.parse_args(argv)
    tokenizer = TOKENIZERS[args.tokenizer]

    if args.command == "demo":
        cases = build_cases(seed=args.seed)
        report = run(
            cases,
            DEFAULT_POLICIES,
            DEFAULT_BUDGETS,
            tokenizer=tokenizer,
            notes={"source": "synthetic fixture, seed " + str(args.seed)},
        )
        _write(report, args.out, "retainkit fixture", 1024, "demo")
        print(sweep_table(report))
        return 0

    cases = load_cases(args.cases)
    budgets = tuple(args.budget) if args.budget else DEFAULT_BUDGETS
    report = run(cases, DEFAULT_POLICIES, budgets, tokenizer=tokenizer)
    if args.out:
        _write(report, args.out, args.title, budgets[len(budgets) // 2], "sweep")
    print(markdown(report, args.title, budgets[len(budgets) // 2]))
    return 0


if __name__ == "__main__":  # pragma: no cover
    sys.exit(main())
