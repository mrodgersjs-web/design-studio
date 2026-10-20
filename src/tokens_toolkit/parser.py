"""Parse and validate a design-token JSON file.

The schema this toolkit accepts is small and intentionally documentable.
A plain string value is also accepted as shorthand for a single-``$value``
record. Allowed kinds are color, font, size and space.

The parser is strictly read-only; it never mutates the source file.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field

KINDS = {"color", "font", "size", "space"}

HEX3 = re.compile(r"^#([0-9a-fA-F]{3})$")
HEX6 = re.compile(r"^#([0-9a-fA-F]{6})$")
HEX8 = re.compile(r"^#([0-9a-fA-F]{8})$")
RGB_FN = re.compile(
    r"^rgba?\(\s*([0-9.]+)\s*,\s*([0-9.]+)\s*,\s*([0-9.]+)(?:\s*,\s*([0-9.]+))?\s*\)$"
)
LENGTH = re.compile(r"^-?\d+(\.\d+)?(rem|em|px|pt|%|vw|vh)?$")


class TokenError(ValueError):
    """The spec cannot be turned into an app. The message says how to fix it."""


@dataclass(frozen=True)
class Token:
    name: str
    kind: str
    value: str
    source: str

    def to_dict(self) -> dict:
        return {"name": self.name, "kind": self.kind, "value": self.value, "source": self.source}


@dataclass
class TokenFile:
    schema: str | None
    tokens: list = field(default_factory=list)

    def by_kind(self, kind):
        return [t for t in self.tokens if t.kind == kind]

    def get(self, name):
        for t in self.tokens:
            if t.name == name:
                return t
        return None

    def names(self):
        return [t.name for t in self.tokens]

    def kinds(self):
        return sorted({t.kind for t in self.tokens})


def _resolve_value(record):
    """Accept plain-string or {"$value": ...} shapes; reject non-string records."""
    if isinstance(record, dict):
        if "$value" in record:
            return record["$value"]
        raise TokenError(
            f"token record must have a '$value' key when not a plain string; got keys {sorted(record)}"
        )
    if record is None or isinstance(record, (bool, int, float)):
        raise TokenError(
            f"token record must be a string or {{'$value': ...}}; got {type(record).__name__}"
        )
    return record
