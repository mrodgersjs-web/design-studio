"""Export a parsed :class:`TokenFile` to common developer formats.

Three formats are supported:

* ``css`` -- a `:root { --token: value; ... }` block plus a list of named classes.
* ``json`` -- a stable JSON dump (sorted keys, deterministic ordering).
* ``tailwind`` -- a ``@theme`` block reading from the CSS custom properties.

All export functions are pure: they take a parsed token file and return
a string. None of them read the filesystem.
"""

from __future__ import annotations

import json
import re

from . import parser

_CSS_VAR = re.compile(r"[^a-zA-Z0-9_-]")


def _css_name(name: str) -> str:
    """Convert a dotted token name into a CSS custom property name."""
    return "--" + _CSS_VAR.sub("-", name.strip("."))


def to_css(tf: parser.TokenFile) -> str:
    """Render the tokens as a ``:root { ... }`` CSS custom-property block.

    The output is sorted by token name to keep it deterministic; the brief
    marks determinism as part of the production standard.
    """
    tokens = sorted(tf.tokens, key=lambda t: t.name)
    lines: list[str] = [":root {"]
    for tok in tokens:
        lines.append(f"  {_css_name(tok.name)}: {tok.value};")
    lines.append("}")
    return "\n".join(lines) + "\n"


def to_json(tf: parser.TokenFile, *, indent: int = 2, sort_keys: bool = True) -> str:
    """Render the tokens as a JSON object keyed by dotted token name.

    Boolean indent and sort_keys match the json module defaults. The
    output is deterministic only when sort_keys is true; the toolkit
    defaults to true.
    """
    payload = {
        "$schema": tf.schema,
        "tokens": [tok.to_dict() for tok in sorted(tf.tokens, key=lambda t: t.name)],
    }
    return json.dumps(payload, indent=indent, sort_keys=sort_keys) + "\n"


def to_tailwind(tf: parser.TokenFile) -> str:
    """Render the tokens as a Tailwind v4 ``@theme { ... }`` CSS block.

    Each token becomes a CSS custom property and an alias is provided
    so the generated CSS variable name matches what :func:`to_css` would
    produce. Consumers can then reference each token with the standard
    ``bg-bg``, ``text-fg`` etc. utilities, or with the literal
    ``var(--color-bg)`` form.
    """
    tokens = sorted(tf.tokens, key=lambda t: t.name)
    block: list[str] = ["@theme {"]
    for tok in tokens:
        alias = _css_name(tok.name)
        block.append(f"  --color-{tok.name.replace('.', '-')}: var({alias});")
        if tok.kind == "font":
            block.append(f"  --font-{tok.name.replace('.', '-')}: var({alias});")
        else:
            block.append(f"  {alias}: {tok.value};")
    block.append("}")
    return "\n".join(block) + "\n"


def to_markdown_table(tf: parser.TokenFile) -> str:
    """Render the tokens as a Markdown table (name, kind, value) for docs."""
    tokens = sorted(tf.tokens, key=lambda t: t.name)
    lines = ["| Token | Kind | Value |", "| --- | --- | --- |"]
    for tok in tokens:
        # escape pipe in value
        v = tok.value.replace("|", "\\|")
        lines.append(f"| `{tok.name}` | {tok.kind} | `{v}` |")
    return "\n".join(lines) + "\n"
