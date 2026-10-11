"""Behaviour tests for the rigds MCP server and the Satori/Apple scorecard.

These exercise real code paths: the scorecard rules on real fixtures and
mutated copies of them, the scorecard CLI on malformed input, the catalog
parser behind rigds_compose, the studio-root helpers on a temporary studio
tree, the backend probe under network failure, and the stdio JSON-RPC
entrypoint (`python -m rigds_mcp.server`) end to end, including that one bad
tool call does not kill the server.
"""
from __future__ import annotations

import copy
import json
import os
import subprocess
import sys
import urllib.error
from pathlib import Path

import pytest

from rigds_mcp import scorecard, server

REPO = Path(__file__).resolve().parent.parent
SKILL = REPO / "skills" / "rig-design-studio-satori-apple"
FIXTURES = SKILL / "fixtures"
SCORECARD = REPO / "rigds_mcp" / "scorecard.py"


def load(name: str) -> dict:
    return json.loads((FIXTURES / name).read_text())


def reasons_for(data: dict) -> list[str]:
    return scorecard.evaluate(data, FIXTURES)


# --------------------------------------------------------------- scorecard rules


def test_pass_fixture_has_no_reasons():
    assert reasons_for(load("pass.json")) == []


@pytest.mark.parametrize(
    "fixture, expected",
    [
        ("fail-empty.json", "applicable must be non-empty"),
        ("fail-gate.json", "GATE 1 scored 1 < 2"),
        ("fail-impl.json", "responsive_screenshots must be a non-empty list of paths"),
        ("fail-omit-gate.json", "missing GATE ids in applicable: 1"),
        ("fail-omit.json", "applicable criterion 12 missing score"),
        ("fail-unknown.json", "unknown criterion id 99"),
    ],
)
def test_each_fail_fixture_fails_for_its_own_reason(fixture, expected):
    assert expected in reasons_for(load(fixture))


def test_pass_rate_boundary_is_exactly_90_percent():
    data = load("pass.json")
    non_gates = [c for c in range(1, 61) if c not in scorecard.GATES]
    for cid in non_gates[:6]:  # 54/60 = 90.0% -> still passes
        data["scores"][str(cid)] = 1
    assert reasons_for(data) == []
    data["scores"][str(non_gates[6])] = 1  # 53/60 = 88.3% -> fails
    assert reasons_for(data) == ["applicable pass rate 88.3% < 90% (53/60)"]


def test_every_gate_below_two_is_reported():
    data = load("pass.json")
    for gate in scorecard.GATES:
        bad = copy.deepcopy(data)
        bad["scores"][str(gate)] = 1
        assert f"GATE {gate} scored 1 < 2" in reasons_for(bad)


@pytest.mark.parametrize(
    "value, needle",
    [
        (True, "criterion 5 score True not in 0..3"),  # bool is not an int score
        (4, "criterion 5 score 4 not in 0..3"),
        (-1, "criterion 5 score -1 not in 0..3"),
        (2.0, "criterion 5 score 2.0 not in 0..3"),
        ("2", "criterion 5 score '2' not in 0..3"),
    ],
)
def test_score_values_must_be_int_0_to_3(value, needle):
    data = load("pass.json")
    data["scores"]["5"] = value
    reasons = reasons_for(data)
    assert needle in reasons
    assert "applicable criterion 5 missing score" in reasons


def test_non_canonical_and_out_of_range_ids_are_rejected():
    data = load("pass.json")
    data["scores"]["05"] = 2
    data["scores"]["0"] = 2
    data["scores"]["x"] = 2
    reasons = reasons_for(data)
    assert "unknown criterion id '05'" in reasons
    assert "unknown criterion id 0" in reasons
    assert "unknown criterion id 'x'" in reasons


def test_duplicate_and_non_int_applicable_ids():
    data = load("pass.json")
    data["applicable"] = data["applicable"] + [7, "8", True]
    reasons = reasons_for(data)
    assert "duplicate applicable id 7" in reasons
    assert "applicable id '8' is not an int" in reasons
    assert "applicable id True is not an int" in reasons


def test_scores_for_non_applicable_ids_fail():
    data = load("pass.json")
    data["applicable"].remove(60)
    assert "scores for non-applicable ids: 60" in reasons_for(data)


def test_wrong_top_level_types_short_circuit():
    data = load("pass.json")
    assert scorecard.evaluate({**data, "scores": []}, FIXTURES) == ["scores must be an object"]
    assert scorecard.evaluate({**data, "applicable": {}}, FIXTURES) == ["applicable must be a list"]


def test_proof_paths_must_be_real_non_empty_files(tmp_path):
    data = load("pass.json")
    (tmp_path / "empty.md").write_text("")
    data["artifact"] = str(tmp_path / "empty.md")  # absolute, exists, empty
    data["decision_ledger"] = "proof/nope.md"  # relative, missing
    data["accessibility_report"] = True  # boolean is not proof
    data["responsive_screenshots"] = ["proof/shot-1440.png", "  "]
    reasons = reasons_for(data)
    assert f"artifact missing or empty: {tmp_path / 'empty.md'}" in reasons
    assert "decision_ledger missing or empty: proof/nope.md" in reasons
    assert "accessibility_report must be a non-empty path" in reasons
    assert "responsive_screenshots[1] must be a non-empty path" in reasons


def test_relative_proof_paths_resolve_against_scorecard_dir_not_cwd(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    assert reasons_for(load("pass.json")) == []
    assert "artifact missing or empty: proof/artifact.html" in scorecard.evaluate(load("pass.json"), tmp_path)


def test_verifier_must_differ_from_generator():
    data = load("pass.json")
    data["verifier"] = " design-agent "
    assert reasons_for(data) == ["verifier must be distinct from generator"]
    data["verifier"] = ""
    assert reasons_for(data) == ["verifier must be a non-empty string"]


def test_packaged_and_skill_scorecards_are_identical():
    skill_copy = SKILL / "scripts" / "scorecard.py"
    assert SCORECARD.read_bytes() == skill_copy.read_bytes()


# --------------------------------------------------------------- scorecard CLI


def run_scorecard(*args: str) -> subprocess.CompletedProcess:
    return subprocess.run([sys.executable, str(SCORECARD), *args], check=False, capture_output=True, text=True)


def test_cli_pass_and_fail_exit_codes():
    ok = run_scorecard(str(FIXTURES / "pass.json"))
    assert (ok.returncode, ok.stdout.strip()) == (0, "PASS")
    bad = run_scorecard(str(FIXTURES / "fail-gate.json"))
    assert bad.returncode == 1
    assert bad.stderr.strip() == "FAIL: GATE 1 scored 1 < 2"


def test_cli_usage_error():
    proc = run_scorecard()
    assert proc.returncode == 2
    assert "usage:" in proc.stderr


@pytest.mark.parametrize("body", ["{not json", "", "\xff\xfe"])
def test_cli_malformed_json_is_a_clean_fail(tmp_path, body):
    path = tmp_path / "bad.json"
    path.write_bytes(body.encode("latin-1"))
    proc = run_scorecard(str(path))
    assert proc.returncode == 1
    assert proc.stderr.startswith("FAIL: scorecard is not valid JSON")
    assert "Traceback" not in proc.stderr


def test_cli_missing_file_is_a_clean_fail(tmp_path):
    proc = run_scorecard(str(tmp_path / "absent.json"))
    assert proc.returncode == 1
    assert proc.stderr.startswith("FAIL: cannot read scorecard")
    assert "Traceback" not in proc.stderr


def test_cli_non_object_json(tmp_path):
    path = tmp_path / "list.json"
    path.write_text("[1, 2]")
    proc = run_scorecard(str(path))
    assert (proc.returncode, proc.stderr.strip()) == (1, "FAIL: scorecard must be an object")


# --------------------------------------------------------------- compose (catalog parser)


EXPECTED_STACKS = {
    "converter": [
        "hero-editorial-split", "proof-named-claims", "product-deck-strip", "pricing-tier-cards",
        "objections-inline-adjacent", "ask-sticky-rail", "footer-encore",
    ],
    "flagship": [
        "hero-instrument-deck", "narrative-day-arc", "media-scrubbed-cinema", "proof-artifact-frames",
        "pricing-tier-cards", "ask-mechanics-list", "footer-signature",
    ],
    "organic": [
        "hero-organic-collage", "narrative-manifesto-scroll", "product-before-after",
        "proof-artifact-frames", "pricing-boarding-table", "ask-minimal", "footer-encore",
    ],
}


@pytest.mark.parametrize("preset", sorted(EXPECTED_STACKS))
def test_compose_presets_match_catalog(preset):
    out = server.compose(preset, None)
    assert out["preset"] == preset
    assert out["stack"] == EXPECTED_STACKS[preset]


def test_compose_stack_ids_are_catalog_variants():
    catalog = (REPO / "rigds_mcp" / "references" / "SECTION-CATALOG.md").read_text()
    for stack in EXPECTED_STACKS.values():
        for variant in stack:
            assert f"`{variant}`" in catalog, variant


def test_compose_unknown_preset_lists_available():
    out = server.compose("brutalist", None)
    assert out == {"error": "unknown preset 'brutalist'", "available": ["converter", "flagship", "organic"]}


def test_compose_slot_override_replaces_only_matching_slot():
    out = server.compose("converter", {"pricing": "pricing-boarding-table"})
    expected = list(EXPECTED_STACKS["converter"])
    expected[3] = "pricing:pricing-boarding-table"
    assert out["stack"] == expected


def test_compose_rejects_non_object_slots():
    assert server.compose("converter", ["hero"]) == {"error": "slots must be an object mapping slot to variant"}


# --------------------------------------------------------------- studio-root helpers


@pytest.fixture
def studio(tmp_path, monkeypatch):
    root = tmp_path / "studio"
    (root / "missions" / "alpha" / "artifacts" / "r1").mkdir(parents=True)
    (root / "missions" / "beta").mkdir(parents=True)
    (root / "engine").mkdir()
    (root / "missions" / "alpha" / "CRITERIA-alpha.md").write_text(
        "# Criteria\n| round | score |\n|---|---|\n| r1 | 0.61 |\n| r2 | 0.74 |\n| r3 | 0.88 |\nnot a row\n"
    )
    (root / "missions" / "alpha" / "artifacts" / "r1" / "index.html").write_text("<html></html>")
    (root / "missions" / "alpha" / "artifacts" / "notes.txt").write_text("x")
    (root / "secret").mkdir()
    (root / "secret" / "CRITERIA-x.md").write_text("| r9 | leaked |\n")
    monkeypatch.setenv("RIGDS_ROOT", str(root))
    return root


def test_studio_root_prefers_env(studio):
    assert server.studio_root() == str(studio)


def test_missions_lists_criteria_or_none(studio):
    assert server.missions(str(studio)) == [
        {"mission": "alpha", "criteria": "CRITERIA-alpha.md"},
        {"mission": "beta", "criteria": None},
    ]


def test_artifacts_only_html_relative_to_root(studio):
    assert server.artifacts(str(studio)) == ["missions/alpha/artifacts/r1/index.html"]
    assert server.artifacts(str(studio), "alpha") == ["missions/alpha/artifacts/r1/index.html"]
    assert server.artifacts(str(studio), "beta") == []


def test_ledger_last_n_rows(studio):
    out = server.ledger(str(studio), "alpha", 2)
    assert out == {"mission": "alpha", "rounds_shown": ["| r2 | 0.74 |", "| r3 | 0.88 |"], "total_rows": 4}


def test_ledger_n_zero_returns_no_rows(studio):
    # rows[-0:] is the whole list; n=0 must mean "show none"
    assert server.ledger(str(studio), "alpha", 0)["rounds_shown"] == []


@pytest.mark.parametrize("n", ["abc", None, -1])
def test_ledger_bad_n_is_an_error_not_a_crash(studio, n):
    assert "error" in server.ledger(str(studio), "alpha", n)


@pytest.mark.parametrize("mission", ["../secret", "..", "a/b", "", 5])
def test_ledger_rejects_path_escaping_mission_names(studio, mission):
    out = server.ledger(str(studio), mission, 5)
    assert out == {"error": f"invalid mission name {mission!r}"}


def test_ledger_missing_criteria(studio):
    assert server.ledger(str(studio), "beta", 5) == {"error": "no CRITERIA in beta"}


def test_call_without_studio_root(monkeypatch, tmp_path):
    monkeypatch.setenv("RIGDS_ROOT", str(tmp_path / "missing"))
    monkeypatch.setattr(server.os.path, "expanduser", lambda p: str(tmp_path / "nohome"))
    text = server.call("rigds_missions", {})
    assert text.startswith("STUDIO ROOT NOT FOUND")
    assert server._is_error(text)


# --------------------------------------------------------------- backend under network failure


def test_backend_reports_network_failures(monkeypatch):
    def refuse(url, timeout):
        raise urllib.error.URLError(ConnectionRefusedError(61, "Connection refused"))

    monkeypatch.setattr(server.urllib.request, "urlopen", refuse)
    out = server.backend()
    assert set(out) == {"health", "stats"}
    assert out["health"]["error"].startswith("URLError")
    assert out["stats"]["error"].startswith("URLError")


def test_backend_reports_non_json_body(monkeypatch):
    class Body:
        def read(self):
            return b"<html>502</html>"

    monkeypatch.setattr(server.urllib.request, "urlopen", lambda url, timeout: Body())
    out = server.backend()
    assert out["health"]["error"].startswith("JSONDecodeError")


# --------------------------------------------------------------- error flagging


@pytest.mark.parametrize(
    "text, flagged",
    [
        ("PASS", False),
        ("FAIL: x", True),
        ("unknown tool foo", True),
        ('{"error": "unknown preset \'x\'"}', True),
        ('{"preset": "converter", "stack": []}', False),
        ('{"health": {"error": "URLError"}}', False),
        ("[]", False),
    ],
)
def test_is_error(text, flagged):
    assert server._is_error(text) is flagged


# --------------------------------------------------------------- stdio entrypoint end to end


def run_server(lines: list, env_extra: dict | None = None) -> list[dict]:
    env = dict(os.environ)
    env["PYTHONPATH"] = str(REPO)
    env.update(env_extra or {})
    payload = "".join((ln if isinstance(ln, str) else json.dumps(ln)) + "\n" for ln in lines)
    proc = subprocess.run(
        [sys.executable, "-m", "rigds_mcp.server"],
        check=False, input=payload, capture_output=True, text=True, env=env, timeout=30,
    )
    assert proc.returncode == 0, proc.stderr
    return [json.loads(ln) for ln in proc.stdout.splitlines() if ln.strip()]


def tool_call(mid: int, name: str, arguments=None) -> dict:
    params = {"name": name}
    if arguments is not None:
        params["arguments"] = arguments
    return {"jsonrpc": "2.0", "id": mid, "method": "tools/call", "params": params}


def text(msg: dict) -> str:
    return msg["result"]["content"][0]["text"]


def test_stdio_handshake_list_ping_and_unknown_method():
    out = run_server([
        {"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {}},
        {"jsonrpc": "2.0", "method": "notifications/initialized"},
        {"jsonrpc": "2.0", "id": 2, "method": "ping"},
        {"jsonrpc": "2.0", "id": 3, "method": "tools/list"},
        {"jsonrpc": "2.0", "id": 4, "method": "resources/list"},
        {"jsonrpc": "2.0", "method": "no/such/notification"},
    ])
    assert [m["id"] for m in out] == [1, 2, 3, 4]
    assert out[0]["result"]["protocolVersion"] == "2024-11-05"
    assert out[0]["result"]["serverInfo"] == {"name": "rigds", "version": "1.1.0"}
    assert out[1]["result"] == {}
    names = [t["name"] for t in out[2]["result"]["tools"]]
    assert names == [t["name"] for t in server.TOOLS] and len(names) == 8
    assert out[3]["error"]["code"] == -32601


def test_stdio_survives_malformed_lines_and_bad_calls(tmp_path):
    studio = tmp_path / "studio"
    (studio / "missions" / "alpha").mkdir(parents=True)
    (studio / "missions" / "alpha" / "CRITERIA-a.md").write_text("| r1 | 1 |\n")
    out = run_server(
        [
            "{not json",
            "[1, 2, 3]",
            "",
            tool_call(1, "rigds_ledger", {"mission": "alpha", "n": "abc"}),
            tool_call(2, "rigds_compose", {"preset": "converter", "slots": ["hero"]}),
            tool_call(3, "rigds_satori_score", {"path": 42}),
            tool_call(4, "rigds_compose", "not-an-object"),
            {"jsonrpc": "2.0", "id": 5, "method": "tools/call", "params": "junk"},
            tool_call(6, "rigds_ledger", {"mission": "alpha", "n": 1}),
            tool_call(7, "rigds_compose", {"preset": "nope"}),
            tool_call(8, "rigds_nope", {}),
            tool_call(9, "rigds_compose", {"preset": "converter", "slots": {"hero": 5}}),
            tool_call(10, "rigds_ledger", {"mission": "alpha"}),
        ],
        {"RIGDS_ROOT": str(studio)},
    )
    by_id = {m["id"]: m for m in out}
    assert sorted(by_id) == list(range(1, 11))
    for mid in (1, 2, 3, 4, 5, 7, 8, 9):
        assert by_id[mid]["result"]["isError"] is True, (mid, text(by_id[mid]))
    assert "n must be an integer" in text(by_id[1])
    assert text(by_id[3]) == "FAIL: path is required (string)"
    assert text(by_id[4]) == "FAIL: arguments must be an object"
    # an exception inside a tool is reported, not fatal to the process
    assert text(by_id[9]).startswith("FAIL: rigds_compose raised AttributeError")
    assert by_id[10]["result"]["isError"] is False
    # the server is still alive and answering after all of the above
    assert by_id[6]["result"]["isError"] is False
    assert json.loads(text(by_id[6]))["rounds_shown"] == ["| r1 | 1 |"]


def test_stdio_satori_score_fixtures_and_missing_file(tmp_path):
    out = run_server([
        tool_call(1, "rigds_satori_score", {"path": str(FIXTURES / "pass.json")}),
        tool_call(2, "rigds_satori_score", {"path": str(FIXTURES / "fail-unknown.json")}),
        tool_call(3, "rigds_satori_score", {"path": str(tmp_path / "absent.json")}),
        tool_call(4, "rigds_satori_score", {}),
        tool_call(5, "rigds_satori_skill"),
    ])
    assert (text(out[0]), out[0]["result"]["isError"]) == ("PASS", False)
    assert text(out[1]) == "FAIL: unknown criterion id 99; unknown applicable id 99"
    assert out[1]["result"]["isError"] is True
    assert text(out[2]).startswith("FAIL: cannot read scorecard")
    assert "Traceback" not in text(out[2])
    assert out[3]["result"]["isError"] is True
    skill = json.loads(text(out[4]))
    assert skill["skill"] == str(SKILL / "SKILL.md")
    assert skill["attribution"] == "unverified-seed"


def test_stdio_engine_status_with_and_without_engine(tmp_path):
    studio = tmp_path / "studio"
    (studio / "missions").mkdir(parents=True)
    eng = studio / "engine"
    eng.mkdir()
    for mod in ("__init__", "loop", "governance", "gate"):
        (eng / f"{mod}.py").write_text("")
    (eng / "ledger.py").write_text(
        "class ProvenanceLedger:\n    def read_all(self):\n        return [1, 2, 3]\n"
    )
    ok = run_server([tool_call(1, "rigds_engine")], {"RIGDS_ROOT": str(studio)})[0]
    assert ok["result"]["isError"] is False
    assert json.loads(text(ok))["ledger_records"] == 3

    (eng / "gate.py").write_text("raise RuntimeError('gate broken')\n")
    bad = run_server([tool_call(1, "rigds_engine")], {"RIGDS_ROOT": str(studio)})[0]
    body = json.loads(text(bad))
    assert body["engine"] == "IMPORT FAILED"
    assert "gate broken" in body["error"]
    assert bad["result"]["isError"] is True


def test_console_script_entrypoint_is_wired():
    import tomllib

    scripts = tomllib.loads((REPO / "pyproject.toml").read_text())["project"]["scripts"]
    assert scripts == {"rigds-mcp": "rigds_mcp.server:main"}
