"""Tests for tokens_toolkit.cli (the CLI surface)."""

from __future__ import annotations

import io
import json
import sys
from pathlib import Path
from unittest import mock

import pytest

from tokens_toolkit import cli


SAMPLE_TOKENS = {
    "color": {"bg": "#0b1220", "fg": "#e5e7eb"},
    "font": {"sans": "IBM Plex Sans"},
}


@pytest.fixture
def tmp_tokens(tmp_path: Path) -> Path:
    p = tmp_path / "tokens.json"
    p.write_text(json.dumps(SAMPLE_TOKENS))
    return p


def _run(argv):
    """Invoke main with argv, capturing stdout/stderr. Returns (rc, out, err)."""
    captured = io.StringIO()
    captured_err = io.StringIO()
    with mock.patch.object(sys, "argv", ["tokens-toolkit", *argv]), \
         mock.patch.object(sys, "stdout", captured), \
         mock.patch.object(sys, "stderr", captured_err):
        try:
            rc = cli.main(argv)
        except SystemExit as exc:
            rc = exc.code if isinstance(exc.code, int) else 1
    return rc, captured.getvalue(), captured_err.getvalue()


def test_validate_clean_file_returns_zero(tmp_tokens):
    rc, out, _ = _run(["validate", str(tmp_tokens)])
    assert rc == 0
    payload = json.loads(out)
    assert payload["ok"] is True
    assert payload["count"] == 3


def test_validate_reports_bad_color(tmp_path: Path):
    p = tmp_path / "tokens.json"
    p.write_text(json.dumps({"color": {"bad": "yellow"}}))
    rc, out, _ = _run(["validate", str(p)])
    assert rc == 1
    assert "color.bad" in out


def test_export_css_writes_root_block(tmp_tokens):
    rc, out, _ = _run(["export", str(tmp_tokens), "--format", "css"])
    assert rc == 0
    assert ":root {" in out
    assert "--color-bg: #0b1220;" in out


def test_export_json_emits_sorted_payload(tmp_tokens):
    rc, out, _ = _run(["export", str(tmp_tokens), "--format", "json"])
    assert rc == 0
    payload = json.loads(out)
    assert payload["tokens"][0]["name"] == "color.bg"


def test_export_markdown_writes_table(tmp_tokens):
    rc, out, _ = _run(["export", str(tmp_tokens), "--format", "markdown"])
    assert rc == 0
    assert "| Token | Kind | Value |" in out


def test_export_with_out_file_writes_file(tmp_tokens, tmp_path: Path):
    out_path = tmp_path / "out.css"
    rc, _out, _err = _run(["export", str(tmp_tokens), "--format", "css", "--out", str(out_path)])
    assert rc == 0
    assert out_path.exists()
    assert "--color-bg" in out_path.read_text()


def test_export_unknown_format(tmp_tokens):
    rc, _out, err = _run(["export", str(tmp_tokens), "--format", "rust"])
    assert rc == 2
    assert "unknown format" in err


def test_contrast_high_contrast_passes():
    rc, out, _ = _run(["contrast", "#000000", "#ffffff"])
    assert rc == 0
    payload = json.loads(out)
    assert payload["result"]["grade"] == "AAA"
    assert payload["result"]["ratio"] > 19


def test_contrast_low_contrast_fails():
    rc, out, _ = _run(["contrast", "#cccccc", "#dddddd"])
    assert rc == 1
    payload = json.loads(out)
    assert payload["result"]["aa_normal"] is False


def test_contrast_bad_color_returns_two():
    rc, out, _ = _run(["contrast", "not-a-color", "#ffffff"])
    assert rc == 2
    payload = json.loads(out)
    assert payload["ok"] is False


def test_checklist_markdown_for_checklist_file(tmp_path: Path):
    p = tmp_path / "ui-review.md"
    p.write_text(
        "---\n"
        "name: UI review\n"
        "description: spots\n"
        "items:\n"
        "- id: contrast\n"
        "  severity: must\n"
        "  text: Contrast meets AA.\n"
        "---\n"
    )
    rc, out, _ = _run(["checklist", str(p), "--format", "markdown"])
    assert rc == 0
    assert "UI review" in out and "MUST" in out


def test_checklist_json(tmp_path: Path):
    p = tmp_path / "ui-review.md"
    p.write_text(
        "---\n"
        "name: UI review\n"
        "items:\n"
        "- id: contrast\n"
        "  text: Contrast meets AA.\n"
        "---\n"
    )
    rc, out, _ = _run(["checklist", str(p), "--format", "json"])
    assert rc == 0
    payload = json.loads(out)
    assert payload["name"] == "UI review"


def test_tokens_command_emits_sorted_list(tmp_tokens):
    rc, out, _ = _run(["tokens", str(tmp_tokens)])
    assert rc == 0
    payload = json.loads(out)
    names = [t["name"] for t in payload["tokens"]]
    assert names == sorted(names)


def test_checklist_unknown_format_rejected(tmp_path: Path):
    p = tmp_path / "ui-review.md"
    p.write_text("---\nname: X\nitems:\n- id: y\n  text: yep\n---\n")
    rc, _out, err = _run(["checklist", str(p), "--format", "yaml"])
    assert rc == 2
    assert "unknown format" in err


def test_validate_stdin(tmp_path: Path, monkeypatch):
    stdin_data = io.StringIO(json.dumps(SAMPLE_TOKENS))
    monkeypatch.setattr(sys, "stdin", stdin_data)
    rc, out, _ = _run(["tokens", "-"])
    assert rc == 0
    assert "color.bg" in out
