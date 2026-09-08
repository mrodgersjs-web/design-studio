#!/usr/bin/env python3
"""Validate a Satori/Apple design scorecard.

Every applicable id 1-60 must have a 0-3 int score. Unknown/duplicate ids fail.
applicable must be non-empty and include every GATE id. GATE scores must be >= 2.
At least 90% of applicable criteria must score >= 2.
Proof fields are existing non-empty files, not booleans. Verifier != generator.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

CRITERIA = frozenset(range(1, 61))
GATES = frozenset({1, 2, 3, 4, 11, 21, 31, 41, 51})
PATH_FIELDS = (
    "artifact",
    "decision_ledger",
    "accessibility_report",
    "unresolved_risks",
)


def _is_int(value: object) -> bool:
    return type(value) is int


def _resolve(raw: str, base: Path) -> Path:
    path = Path(raw)
    if path.is_absolute():
        return path
    return (base / path).resolve()


def _require_file(raw: object, label: str, base: Path, reasons: list[str]) -> None:
    if type(raw) is not str or not raw.strip():
        reasons.append(f"{label} must be a non-empty path")
        return
    path = _resolve(raw, base)
    if not path.is_file() or path.stat().st_size == 0:
        reasons.append(f"{label} missing or empty: {raw}")


def evaluate(data: dict, base: Path) -> list[str]:
    reasons: list[str] = []
    raw_scores = data.get("scores")
    if type(raw_scores) is not dict:
        return ["scores must be an object"]
    raw_applicable = data.get("applicable")
    if type(raw_applicable) is not list:
        return ["applicable must be a list"]

    applicable: list[int] = []
    seen: set[int] = set()
    for item in raw_applicable:
        if not _is_int(item):
            reasons.append(f"applicable id {item!r} is not an int")
            continue
        if item in seen:
            reasons.append(f"duplicate applicable id {item}")
            continue
        seen.add(item)
        applicable.append(item)

    if not applicable:
        reasons.append("applicable must be non-empty")

    missing_gates = sorted(GATES - set(applicable))
    if missing_gates:
        reasons.append("missing GATE ids in applicable: " + ",".join(map(str, missing_gates)))

    scores: dict[int, int] = {}
    for key, value in raw_scores.items():
        if type(key) is not str or not key.isdigit() or str(int(key)) != key:
            reasons.append(f"unknown criterion id {key!r}")
            continue
        cid = int(key)
        if cid not in CRITERIA:
            reasons.append(f"unknown criterion id {cid}")
            continue
        if not _is_int(value) or value not in (0, 1, 2, 3):
            reasons.append(f"criterion {cid} score {value!r} not in 0..3")
            continue
        scores[cid] = value

    for cid in applicable:
        if cid not in CRITERIA:
            reasons.append(f"unknown applicable id {cid}")
        elif cid not in scores:
            reasons.append(f"applicable criterion {cid} missing score")

    extra = sorted(set(scores) - set(applicable))
    if extra:
        reasons.append("scores for non-applicable ids: " + ",".join(map(str, extra)))

    for gate in sorted(GATES):
        if gate in applicable and scores.get(gate, 0) < 2:
            reasons.append(f"GATE {gate} scored {scores.get(gate, 0)} < 2")

    if applicable and not any(r.startswith("applicable criterion") for r in reasons):
        scored = [cid for cid in applicable if cid in scores]
        if scored:
            passed = sum(1 for cid in scored if scores[cid] >= 2)
            if passed / len(scored) < 0.90:
                reasons.append(
                    f"applicable pass rate {passed / len(scored):.1%} < 90% ({passed}/{len(scored)})"
                )

    for field in PATH_FIELDS:
        _require_file(data.get(field), field, base, reasons)

    shots = data.get("responsive_screenshots")
    if type(shots) is not list or not shots:
        reasons.append("responsive_screenshots must be a non-empty list of paths")
    else:
        for index, shot in enumerate(shots):
            _require_file(shot, f"responsive_screenshots[{index}]", base, reasons)

    generator = data.get("generator")
    verifier = data.get("verifier")
    if type(generator) is not str or not generator.strip():
        reasons.append("generator must be a non-empty string")
    if type(verifier) is not str or not verifier.strip():
        reasons.append("verifier must be a non-empty string")
    if (
        type(generator) is str
        and type(verifier) is str
        and generator.strip()
        and verifier.strip()
        and generator.strip() == verifier.strip()
    ):
        reasons.append("verifier must be distinct from generator")

    return reasons


def main(argv: list[str]) -> int:
    if len(argv) != 2:
        print("usage: scorecard.py <scorecard.json>", file=sys.stderr)
        return 2
    path = Path(argv[1])
    data = json.loads(path.read_text())
    if type(data) is not dict:
        print("FAIL: scorecard must be an object", file=sys.stderr)
        return 1
    reasons = evaluate(data, path.parent)
    if reasons:
        print("FAIL: " + "; ".join(reasons), file=sys.stderr)
        return 1
    print("PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
