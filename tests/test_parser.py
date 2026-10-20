"""Tests for tokens_toolkit.parser."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from tokens_toolkit.parser import (
    KINDS,
    TokenError,
    parse_token_file,
    parse_token_object,
    validate,
)


def test_load_minimal_file(tmp_path: Path):
    path = tmp_path / "tokens.json"
    path.write_text(json.dumps({
        "color": {"bg": {"$value": "#0b1220"}, "fg": {"$value": "#e5e7eb"}},
        "font": {"sans": {"$value": "IBM Plex Sans"}},
    }))
    tf = parse_token_file(path)
    assert tf.schema is None
    assert {t.name for t in tf.tokens} == {"color.bg", "color.fg", "font.sans"}


def test_string_shorthand_is_accepted():
    tf = parse_token_object({"color": {"bg": "#0b1220"}})
    assert tf.tokens[0].name == "color.bg"
    assert tf.tokens[0].value == "#0b1220"


def test_nested_groups_walk_by_dotted_name(tmp_path: Path):
    path = tmp_path / "t.json"
    path.write_text(json.dumps({
        "color": {
            "background": {
                "primary": {"$value": "#0b1220"},
                "secondary": {"$value": "#1e293b"},
            }
        }
    }))
    tf = parse_token_file(path)
    names = {t.name for t in tf.tokens}
    assert names == {"color.background.primary", "color.background.secondary"}


def test_kind_inferred_from_group():
    tf = parse_token_object({"font": {"mono": "JetBrains Mono"}})
    assert tf.tokens[0].kind == "font"


def test_group_and_value_kind_clash_raises():
    with pytest.raises(TokenError, match="looks like"):
        parse_token_object({"font": {"weird": "#112233"}})


def test_value_kind_for_known_color_and_unknown_group():
    tf = parse_token_object({"accent": {"link": "#abcdef"}})
    assert tf.tokens[0].kind == "color"


def test_kinds_constant_covers_taxonomy():
    assert KINDS == {"color", "font", "size", "space"}


def test_validate_color_accepts_hex_and_rgb():
    tf = parse_token_object({
        "color": {
            "a": "#0b1220",
            "b": "#fff",
            "c": "rgb(0,0,0)",
            "d": "rgba(255,255,255,1.0)",
        }
    })
    assert validate(tf) == []


def test_validate_color_rejects_garbage():
    tf = parse_token_object({"color": {"bad": "not-a-color"}})
    errors = validate(tf)
    assert errors and errors[0].startswith("color.bad:")


def test_validate_size_accepts_rem_px_clamp_and_keywords():
    tf = parse_token_object({
        "size": {"a": "1rem", "b": "16px", "c": "clamp(1rem, 5vw, 2rem)"},
        "space": {"gap": "auto"},
    })
    assert validate(tf) == []


def test_validate_size_rejects_unknown():
    tf = parse_token_object({"size": {"bad": "not-a-length"}})
    errors = validate(tf)
    assert errors and errors[0].startswith("size.bad:")


def test_validate_font_rejects_empty_and_newlines():
    tf = parse_token_object({"font": {"bad": "\nInter\n"}})
    errors = validate(tf)
    assert any("font.bad" in e for e in errors)


def test_get_and_names_methods():
    tf = parse_token_object({"color": {"a": "#000000", "b": "#ffffff"}})
    assert tf.get("color.a").value == "#000000"
    assert sorted(tf.names()) == ["color.a", "color.b"]
    assert "color" in tf.kinds()


def test_tokens_by_group_helper():
    tf = parse_token_object({
        "color": {"a": "#000000", "b": "#ffffff"},
        "size": {"s": "1rem"},
    })
    colors = tf.by_kind("color")
    assert len(colors) == 2
    assert all(t.kind == "color" for t in colors)


def test_top_level_must_be_object():
    with pytest.raises(TokenError, match="top-level must be a JSON object"):
        parse_token_object(["not", "an", "object"])


def test_malformed_json_raises(tmp_path: Path):
    path = tmp_path / "bad.json"
    path.write_text("{ this : is not json")
    with pytest.raises(TokenError, match="not valid JSON"):
        parse_token_file(path)


def test_schema_field_is_captured():
    tf = parse_token_object({"$schema": "https://example.invalid/v1", "color": {"a": "#000000"}})
    assert tf.schema == "https://example.invalid/v1"


def test_resolve_value_requires_dollar_value_in_dict():
    # A top-level non-object raises a different message ("top-level must be a JSON object").
    with pytest.raises(TokenError, match="token record"):
        parse_token_object({"color": {"bad": {"unexpected": 1}}})
