#!/usr/bin/env python3
"""Fail if the skill claims verified Satori or Apple grounding without the ledger."""
from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LEDGER = ROOT / "references" / "evidence-ledger-v0.1.md"
BANNED = (
    "verified Satori or Apple grounding",
    "Apple’s operating pattern in the seed lesson is communication-first",
    "Apple's operating pattern in the seed lesson is communication-first",
)


def main() -> int:
    if not LEDGER.is_file() or LEDGER.stat().st_size == 0:
        print("FAIL: missing evidence ledger")
        return 1
    text = LEDGER.read_text()
    if "AMLFTIb42t8" not in text or "00:02:26-00:03:26" not in text:
        print("FAIL: ledger lacks URL and timestamp for the saved lesson")
        return 1
    if "Not verified" not in text:
        print("FAIL: ledger must keep unverified Apple operating-pattern claim")
        return 1
    bad = []
    for path in [ROOT / "SKILL.md", *sorted((ROOT / "references").glob("*.md"))]:
        body = path.read_text()
        for phrase in BANNED:
            if phrase in body:
                bad.append(f"{path.name}: {phrase}")
    if bad:
        print("FAIL: unsupported verified claim remains")
        print("\n".join(bad))
        return 1
    print("PASS attribution")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
