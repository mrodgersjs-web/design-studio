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


def _classify(group, raw_value):
    group_kind = {
        "color": "color", "colour": "color", "font": "font",
        "fonts": "font", "typography": "font", "size": "size",
        "sizes": "size", "font-size": "size", "space": "space",
        "spacing": "space",
    }.get(group.lower())
    value_kind = None
    if isinstance(raw_value, str):
        if HEX3.match(raw_value) or HEX6.match(raw_value) or HEX8.match(raw_value) or RGB_FN.match(raw_value):
            value_kind = "color"
        elif LENGTH.match(raw_value):
            low = group.lower()
            if "size" in low:
                value_kind = "size"
            elif "space" in low or "spacing" in low:
                value_kind = "space"
            else:
                value_kind = None
        else:
            value_kind = "font" if "font" in group.lower() else None
    if group_kind and value_kind and group_kind != value_kind:
        raise TokenError(f"group '{group}' expects {group_kind} but value {raw_value!r} looks like {value_kind}")
    return group_kind or value_kind


def parse_token_file(path):
    import json
    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise TokenError(f"{path}: not valid JSON ({exc.msg} at line {exc.lineno})") from exc
    return parse_token_object(raw, source=str(path))


def parse_token_object(raw, *, source: str = "<memory>"):
    if not isinstance(raw, dict):
        raise TokenError(
            f"{source}: top-level must be a JSON object; got {type(raw).__name__}"
        )
    schema = raw.get("$schema") if isinstance(raw.get("$schema"), str) else None
    tokens: list = []
    _walk(raw, prefix="", out=tokens, source=source)
    return TokenFile(schema=schema, tokens=tokens)


def _walk(node, prefix, out, source):
    for key, value in node.items():
        if key.startswith("$"):
            continue
        path = f"{prefix}{key}" if not prefix else f"{prefix}.{key}"
        if isinstance(value, dict) and "$value" not in value:
            _walk(value, path, out, source)
            continue
        kind = _classify(
            path.split(".", 1)[0] if "." in path else path,
            value if not isinstance(value, dict) else value.get("$value"),
        )
        if kind is None:
            if isinstance(value, str) and (
                HEX3.match(value) or HEX6.match(value)
                or HEX8.match(value) or RGB_FN.match(value)
            ):
                kind = "color"
            else:
                kind = "font"
        if kind not in KINDS:
            raise TokenError(f"{source}: token {path!r} has unrecognised kind {kind!r}")
        token_value = _resolve_value(value)
        if not isinstance(token_value, str):
            raise TokenError(
                f"{source}: token {path!r} resolved value must be a string; "
                f"got {type(token_value).__name__}"
            )
        out.append(Token(name=path, kind=kind, value=token_value, source=repr(value)))


def validate_color(value):
    if HEX3.match(value) or HEX6.match(value) or HEX8.match(value):
        return
    if RGB_FN.match(value):
        return
    raise TokenError(f"not a valid CSS color: {value!r}")


def validate_font(value):
    if not value or len(value) > 200:
        raise TokenError(f"font token {value!r} must be a non-empty string under 200 chars")
    if "\n" in value or "\r" in value:
        raise TokenError(f"font token must not contain newlines; got {value!r}")


def validate_size_or_space(value):
    if value.lower() in {"auto", "inherit", "initial", "unset"}:
        return
    if LENGTH.match(value):
        return
    if value.startswith("clamp(") and value.endswith(")"):
        return
    raise TokenError(
        f"size/space token {value!r} is not a recognised length or CSS keyword; "
        "expected e.g. '1rem', '16px', 'clamp(2rem, 5vw, 3.5rem)', or 'auto'."
    )


VALIDATORS = {
    "color": validate_color, "font": validate_font,
    "size": validate_size_or_space, "space": validate_size_or_space,
}


def validate(tf):
    errors: list = []
    for tok in tf.tokens:
        try:
            VALIDATORS[tok.kind](tok.value)
        except TokenError as exc:
            errors.append(f"{tok.name}: {exc}")
    return errors


def tokens_by_group(tf, group):
    prefix = group if group.endswith(".") else f"{group}."
    return [t for t in tf.tokens if t.name == group or t.name.startswith(prefix)]


def iter_groups(tf):
    seen: set = set()
    for t in tf.tokens:
        head = t.name.split(".", 1)[0]
        if head not in seen:
            seen.add(head)
            yield head
