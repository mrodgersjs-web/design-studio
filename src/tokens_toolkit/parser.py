"""Parse and validate a design-token JSON file.

The parser is rule-based. A token is a `{group}.{name}` dotted path
mapping to either a plain string value or a `{"$value": ...}` record.
Allowed groups: color, font, size, space. The parser never mutates
the source file.
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
