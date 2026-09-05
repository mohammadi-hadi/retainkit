"""Download the LoCoMo conversations.

LoCoMo is released by Snap Research with the paper *Evaluating Very Long-Term
Conversational Memory of LLM Agents* (Maharana et al., ACL 2024). The file is
fetched into `examples/locomo/data/`, which is not tracked here: the dataset
carries its own terms and is not redistributed with this package.

    python examples/locomo/fetch_data.py
"""

from __future__ import annotations

import sys
import urllib.request
from pathlib import Path

URL = "https://raw.githubusercontent.com/snap-research/locomo/main/data/locomo10.json"
DATA = Path(__file__).parent / "data" / "locomo10.json"


def main() -> int:
    DATA.parent.mkdir(parents=True, exist_ok=True)
    if DATA.exists():
        print(f"already here: {DATA} ({DATA.stat().st_size / 1e6:.1f} MB)")
        return 0
    print(f"fetching {URL}")
    urllib.request.urlretrieve(URL, DATA)  # noqa: S310
    print(f"wrote {DATA} ({DATA.stat().st_size / 1e6:.1f} MB)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
