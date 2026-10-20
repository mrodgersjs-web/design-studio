"""Parse and validate a design-token JSON file.

The parser is rule-based. A token is a `{group}.{name}` dotted path
mapping to either a plain string value or a `{"$value": ...}` record.
Allowed groups: color, font, size, space. The parser never mutates
the source file.
"""

from __future__ import annotations

from dataclasses import dataclass, field

KINDS = {"color", "font", "size", "space"}


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
