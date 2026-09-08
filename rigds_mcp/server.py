#!/usr/bin/env python3
"""rigds MCP server — newline JSON-RPC on stdio (stdlib only).

Self-contained: six studio tools plus Satori/Apple scorecard.
Does not import rig95_harness.
"""
from __future__ import annotations

import glob
import json
import os
import re
import subprocess
import sys
import urllib.request
from importlib.resources import as_file, files as pkg_files
from pathlib import Path

PROTOCOL = "2024-11-05"
STR = {"type": "string"}
_REPO_SKILL = Path(__file__).resolve().parent.parent / "skills" / "rig-design-studio-satori-apple"

CORE_TOOLS = [
    {"name": "rigds_missions", "description": "List design-studio missions with their criteria ledgers.",
     "inputSchema": {"type": "object", "properties": {}}},
    {"name": "rigds_ledger", "description": "Read the last N round rows from a mission's CRITERIA ledger.",
     "inputSchema": {"type": "object", "properties": {"mission": STR, "n": {"type": "integer"}}, "required": ["mission"]}},
    {"name": "rigds_compose", "description": "Emit a section-composition manifest from the 54-variant catalog (presets: converter, flagship, organic; optional slot overrides).",
     "inputSchema": {"type": "object", "properties": {"preset": STR, "slots": {"type": "object"}}, "required": ["preset"]}},
    {"name": "rigds_artifacts", "description": "List studio artifact HTML files (optionally per mission).",
     "inputSchema": {"type": "object", "properties": {"mission": STR}}},
    {"name": "rigds_engine", "description": "Design-quality engine status: loop/gate/ledger/providers (import-verified).",
     "inputSchema": {"type": "object", "properties": {}}},
    {"name": "rigds_backend", "description": "Studio backend health + live funnel stats (:8744).",
     "inputSchema": {"type": "object", "properties": {}}},
]

SATORI_TOOLS = [
    {"name": "rigds_satori_skill", "description": "Show the Satori/Apple communication-first skill path, version, and seed/unverified-attribution status.",
     "inputSchema": {"type": "object", "properties": {}}},
    {"name": "rigds_satori_score", "description": "Run the Satori/Apple scorecard validator on a JSON file. GATE ids must be >=2; applicable must include every GATE; proof fields must be existing files.",
     "inputSchema": {"type": "object", "properties": {"path": STR}, "required": ["path"]}},
]

TOOLS = CORE_TOOLS + SATORI_TOOLS


def studio_root():
    env = os.environ.get("RIGDS_ROOT")
    if env and os.path.isdir(env):
        return env
    default = os.path.expanduser("~/Developer/rig-design-studio")
    if os.path.isdir(os.path.join(default, "engine")) and os.path.isdir(os.path.join(default, "missions")):
        return default
    d = os.path.dirname(os.path.abspath(__file__))
    for _ in range(6):
        if os.path.isdir(os.path.join(d, "engine")) and os.path.isdir(os.path.join(d, "missions")):
            return d
        d = os.path.dirname(d)
    return None


def missions(root):
    ms = []
    for d in sorted(glob.glob(os.path.join(root, "missions", "*/"))):
        crit = glob.glob(os.path.join(d, "CRITERIA-*.md"))
        ms.append({"mission": os.path.basename(d.rstrip("/")),
                   "criteria": os.path.basename(crit[0]) if crit else None})
    return ms


def artifacts(root, mission=None):
    base = os.path.join(root, "missions", mission, "artifacts") if mission else os.path.join(root, "missions")
    out = []
    for p in sorted(glob.glob(os.path.join(base, "**", "*.html"), recursive=True))[:60]:
        out.append(os.path.relpath(p, root))
    return out


def ledger(root, mission, n=5):
    crit = glob.glob(os.path.join(root, "missions", mission, "CRITERIA-*.md"))
    if not crit:
        return {"error": f"no CRITERIA in {mission}"}
    lines = open(crit[0]).read().splitlines()
    rows = [l for l in lines if l.startswith("| ") and ("r" in l[:6] or "i" in l[:6])]
    return {"mission": mission, "rounds_shown": rows[-n:], "total_rows": len(rows)}


def compose(preset, slot_overrides):
    txt = pkg_files("rigds_mcp").joinpath("references", "SECTION-CATALOG.md").read_text(encoding="utf-8")
    presets = {}
    for m in re.finditer(r"- \*\*(\w+)\*\*[^:]*: (.+?)(?=\n- \*\*|\n## |\Z)", txt, re.S):
        presets[m.group(1)] = [s.strip() for s in m.group(2).replace("→", ">").split(">") if s.strip()]
    if preset not in presets:
        return {"error": f"unknown preset {preset!r}", "available": sorted(presets)}
    stack = presets[preset]
    for slot, variant in (slot_overrides or {}).items():
        stack = [f"{slot}:{variant}" if s.startswith(slot) or s.startswith(variant.split("-")[0]) else s for s in stack]
    return {"preset": preset, "stack": stack,
            "composer": "http://127.0.0.1:8743/site-composer.html",
            "note": "manifest for the composer/agent; render happens in site-composer.html or a build agent"}


def backend():
    out = {}
    for name, url in (("health", "http://127.0.0.1:8744/api/health"), ("stats", "http://127.0.0.1:8744/api/stats")):
        try:
            out[name] = json.loads(urllib.request.urlopen(url, timeout=4).read())
        except Exception as e:
            out[name] = {"error": f"{type(e).__name__}: {e}"}
    return out


def engine_status(root):
    sys.path.insert(0, root)
    try:
        import engine.loop, engine.ledger, engine.governance, engine.gate  # noqa: F401
        led = engine.ledger.ProvenanceLedger()
        return {"engine": "import OK", "loop": "run_loop", "gate": "RigQualityGate",
                "ledger_records": len(led.read_all()),
                "providers": ["higgsfield (prompt-gate + Gate-D credit stop)", "opendesign_router (3-tier degradation)"]}
    except Exception as e:
        return {"engine": "IMPORT FAILED", "error": f"{type(e).__name__}: {e}"}


def satori_root() -> Path:
    env = os.environ.get("RIGDS_SATORI_ROOT")
    if env:
        return Path(env)
    return _REPO_SKILL


def _is_error(text: str) -> bool:
    return (
        text.startswith("STUDIO ROOT NOT FOUND")
        or text.startswith("FAIL:")
        or "unknown tool" in text
    )


def call(name, args):
    if name == "rigds_satori_skill":
        root = satori_root()
        skill = root / "SKILL.md"
        return json.dumps({
            "root": str(root) if skill.is_file() else None,
            "skill": str(skill) if skill.is_file() else None,
            "version": "0.1.0",
            "attribution": "unverified-seed",
            "install": "npx skills add mrodgersjs-web/design-studio --skill rig-design-studio-satori-apple",
            "scorecard": "package:rigds_mcp/scorecard.py",
        }, indent=1)
    if name == "rigds_satori_score":
        scorecard = args.get("path", "")
        if not scorecard:
            return "FAIL: path is required"
        script_ref = pkg_files("rigds_mcp").joinpath("scorecard.py")
        with as_file(script_ref) as script:
            proc = subprocess.run([sys.executable, str(script), scorecard], capture_output=True, text=True)
        out = ((proc.stdout or "") + (proc.stderr or "")).strip()
        if proc.returncode != 0 and not out.startswith("FAIL:"):
            return f"FAIL: scorecard exit {proc.returncode}: {out or 'no output'}"
        return out or f"FAIL: empty scorecard output exit {proc.returncode}"
    root = studio_root()
    if not root:
        return "STUDIO ROOT NOT FOUND — set RIGDS_ROOT to the rig-design-studio repo"
    if name == "rigds_missions":
        return json.dumps(missions(root), indent=1)
    if name == "rigds_ledger":
        return json.dumps(ledger(root, args.get("mission", ""), int(args.get("n", 5))), indent=1)
    if name == "rigds_compose":
        return json.dumps(compose(args.get("preset", "converter"), args.get("slots")), indent=1)
    if name == "rigds_artifacts":
        return json.dumps(artifacts(root, args.get("mission")), indent=1)
    if name == "rigds_engine":
        return json.dumps(engine_status(root), indent=1)
    if name == "rigds_backend":
        return json.dumps(backend(), indent=1)
    return f"unknown tool {name}"


def send(obj):
    sys.stdout.write(json.dumps(obj) + "\n")
    sys.stdout.flush()


def main():
    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
        try:
            msg = json.loads(line)
        except json.JSONDecodeError:
            continue
        mid, method = msg.get("id"), msg.get("method", "")
        if method == "initialize":
            send({"jsonrpc": "2.0", "id": mid, "result": {"protocolVersion": PROTOCOL,
                  "capabilities": {"tools": {}}, "serverInfo": {"name": "rigds", "version": "1.1.0"}}})
        elif method == "notifications/initialized":
            continue
        elif method == "ping":
            send({"jsonrpc": "2.0", "id": mid, "result": {}})
        elif method == "tools/list":
            send({"jsonrpc": "2.0", "id": mid, "result": {"tools": TOOLS}})
        elif method == "tools/call":
            name = msg.get("params", {}).get("name", "")
            args = msg.get("params", {}).get("arguments", {}) or {}
            text = call(name, args)
            send({"jsonrpc": "2.0", "id": mid, "result": {
                "content": [{"type": "text", "text": text}],
                "isError": _is_error(text)}})
        elif mid is not None:
            send({"jsonrpc": "2.0", "id": mid, "error": {"code": -32601, "message": f"unknown method {method}"}})


if __name__ == "__main__":
    main()
