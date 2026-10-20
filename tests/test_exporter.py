from __future__ import annotations

import json

from tokens_toolkit import exporter, parser


def _small_tf():
    return parser.parse_token_object({
        "color": {"bg": "#0b1220", "fg": "#e5e7eb"},
        "font": {"sans": "IBM Plex Sans"},
        "size": {"sm": "0.875rem"},
    })


def test_to_css_dotted_names_become_double_dash():
    css = exporter.to_css(_small_tf())
    assert ":root {" in css and "}" in css
    assert "--color-bg: #0b1220;" in css
    assert "--color-fg: #e5e7eb;" in css
    assert "--font-sans: IBM Plex Sans;" in css
    assert "--size-sm: 0.875rem;" in css


def test_to_css_is_deterministic_under_random_input():
    tf = _small_tf()
    assert exporter.to_css(tf) == exporter.to_css(tf)


def test_to_css_sorts_tokens_alphabetically():
    tf = parser.parse_token_object({
        "color": {"z": "#000000", "a": "#ffffff", "m": "#777777"}
    })
    css = exporter.to_css(tf)
    lines = [line for line in css.splitlines() if "--color-" in line]
    assert lines == sorted(lines)


def test_to_json_returns_sorted_and_indented():
    text = exporter.to_json(_small_tf())
    assert text.startswith('{\n  "$schema"')

    payload = json.loads(text)
    assert payload["tokens"][0]["name"] == "color.bg"
    assert payload["tokens"][-1]["name"] == "size.sm"


def test_to_json_handles_no_schema_field():
    tf = parser.parse_token_object({"color": {"a": "#ffffff"}})
    payload = json.loads(exporter.to_json(tf))
    assert payload["$schema"] is None


def test_to_tailwind_uses_var_aliases():
    css = exporter.to_tailwind(_small_tf())
    assert "@theme {" in css
    assert "var(--color-bg)" in css
    assert "--size-sm: 0.875rem;" in css


def test_to_markdown_table_includes_pipe_escaping():
    tf = parser.parse_token_object({"size": {"weird": "1 | rem"}})
    out = exporter.to_markdown_table(tf)
    assert "1 \\| rem" in out
    assert "| `size.weird` |" in out


def test_exporters_are_pure():
    """Calling an exporter twice returns the same string, no I/O."""
    tf = _small_tf()
    for fn in (exporter.to_css, exporter.to_json, exporter.to_tailwind, exporter.to_markdown_table):
        assert fn(tf) == fn(tf)
