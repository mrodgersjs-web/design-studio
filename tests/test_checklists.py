"""Tests for tokens_toolkit.checklists."""

from __future__ import annotations

from pathlib import Path

import pytest

from tokens_toolkit import checklists


@pytest.fixture
def sample_path(tmp_path: Path) -> Path:
    path = tmp_path / "ui-review.md"
    path.write_text(
        "---\n"
        "name: UI review\n"
        "description: Spots every shipped page is read.\n"
        "items:\n"
        "- id: contrast\n"
        "  severity: must\n"
        "  text: Contrast meets AA for body text.\n"
        "  pass_criteria: ratio >= 4.5\n"
        "- id: focus\n"
        "  severity: should\n"
        "  text: Focus states visible on keyboard navigation.\n"
        "- id: lorem\n"
        "  severity: must\n"
        "  text: No placeholder lorem in ship path.\n"
        "---\n"
        "Body of the doc.\n"
    )
    return path


def test_parse_checklist_file_returns_named_checklist(sample_path):
    cl = checklists.parse_checklist_file(sample_path)
    assert cl.name == "UI review"
    assert cl.description.startswith("Spots every")
    assert len(cl.items) == 3


def test_parse_checklist_severity_default_is_should():
    raw = "---\nname: X\nitems:\n- id: y\n  text: yep\n---\n"
    cl = checklists.parse_checklist_text(raw)
    assert cl.items[0].severity == "should"


def test_parse_checklist_rejects_unknown_severity():
    raw = '---\nname: X\nitems:\n- id: y\n  severity: often\n  text: "yep"\n---\n'
    with pytest.raises(ValueError, match="severity"):
        checklists.parse_checklist_text(raw)


def test_parse_checklist_requires_unique_ids(tmp_path: Path):
    raw = "---\nname: X\nitems:\n- id: y\n  text: yep\n- id: y\n  text: no\n---\n"
    with pytest.raises(ValueError, match="duplicate item id"):
        checklists.parse_checklist_text(raw)


def test_parse_checklist_requires_non_empty_id_and_text():
    raw = "---\nname: X\nitems:\n- id: ''\n  text: no\n---\n"
    with pytest.raises(ValueError, match="id"):
        checklists.parse_checklist_text(raw)


def test_parse_checklist_rejects_items_missing():
    raw = "---\nname: X\nitems:\n- not_mapping\n---\n"
    with pytest.raises(ValueError, match="items must contain at least one entry"):
        checklists.parse_checklist_text(raw)


def test_render_markdown_includes_severity_label(sample_path):
    cl = checklists.parse_checklist_file(sample_path)
    out = checklists.render_checklist_markdown(cl)
    assert "UI review" in out
    assert "MUST" in out
    assert "should" in out


def test_render_json_round_trip(sample_path):
    import json

    cl = checklists.parse_checklist_file(sample_path)
    payload = json.loads(checklists.render_checklist_json(cl))
    assert payload["name"] == "UI review"
    assert {item["id"] for item in payload["items"]} == {"contrast", "focus", "lorem"}


def test_item_lookup(sample_path):
    cl = checklists.parse_checklist_file(sample_path)
    item = cl.item("focus")
    assert item is not None and item.severity == "should"
    assert cl.item("missing") is None
