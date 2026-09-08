#!/usr/bin/env python3
"""Parity + Satori contract for the governed rigds MCP server.

Compares the live pipx `rigds-mcp` six-tool surface to mcp/rigds_mcp.py
before any pipx cutover. Satori FAIL must set isError true.
"""
from __future__ import annotations

import json
import select
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent
NEW = ROOT / "rigds_mcp.py"
SKILL = ROOT.parent / "skills" / "rig-design-studio-satori-apple"
CORE = [
    "rigds_missions",
    "rigds_ledger",
    "rigds_compose",
    "rigds_artifacts",
    "rigds_engine",
    "rigds_backend",
]


def rpc(cmd, calls, timeout=8):
    proc = subprocess.Popen(
        cmd,
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    out = []
    try:
        def send(obj):
            proc.stdin.write(json.dumps(obj) + "\n")
            proc.stdin.flush()

        def read():
            start = time.time()
            while time.time() - start < timeout:
                ready, _, _ = select.select([proc.stdout], [], [], 0.2)
                if proc.poll() is not None and not ready:
                    raise SystemExit(f"exit {proc.returncode} stderr={proc.stderr.read()[:800]}")
                if not ready:
                    continue
                line = proc.stdout.readline()
                if line:
                    return json.loads(line)
            raise SystemExit(f"timeout cmd={cmd}")

        send({"jsonrpc": "2.0", "id": 1, "method": "initialize",
              "params": {"protocolVersion": "2024-11-05", "capabilities": {},
                         "clientInfo": {"name": "contract", "version": "0"}}})
        init = read()
        send({"jsonrpc": "2.0", "method": "notifications/initialized"})
        results = {"initialize": init}
        for i, msg in enumerate(calls, start=2):
            msg = dict(msg)
            msg["jsonrpc"] = "2.0"
            msg["id"] = i
            send(msg)
            results[msg["method"] + ":" + str(i)] = read()
        return results
    finally:
        proc.kill()


def tool_map(listed):
    tools = ((listed.get("result") or {}).get("tools")) or []
    return {t["name"]: t for t in tools}


def text_of(msg):
    return (((msg.get("result") or {}).get("content") or [{}])[0]).get("text", "")


def main():
    old_cmd = ["rigds-mcp"]
    new_cmd = [sys.executable, str(NEW)]
    list_call = [{"method": "tools/list"}]
    old = rpc(old_cmd, list_call)
    new = rpc(new_cmd, list_call)
    old_tools = tool_map(old["tools/list:2"])
    new_tools = tool_map(new["tools/list:2"])
    missing = [n for n in CORE if n not in new_tools]
    if missing:
        raise SystemExit(f"FAIL missing core tools: {missing}")
    for name in CORE:
        if name not in old_tools:
            raise SystemExit(f"FAIL live server missing {name}")
        if old_tools[name]["inputSchema"] != new_tools[name]["inputSchema"]:
            raise SystemExit(f"FAIL schema drift on {name}")
        if old_tools[name]["description"] != new_tools[name]["description"]:
            raise SystemExit(f"FAIL description drift on {name}")
    if "rigds_satori_skill" not in new_tools or "rigds_satori_score" not in new_tools:
        raise SystemExit("FAIL missing satori tools")

    engine_old = rpc(old_cmd, [{"method": "tools/call", "params": {"name": "rigds_engine", "arguments": {}}}])
    engine_new = rpc(new_cmd, [{"method": "tools/call", "params": {"name": "rigds_engine", "arguments": {}}}])
    old_txt = text_of(engine_old["tools/call:2"])
    new_txt = text_of(engine_new["tools/call:2"])
    if engine_new["tools/call:2"].get("result", {}).get("isError"):
        raise SystemExit(f"FAIL new engine isError: {new_txt[:400]}")
    if json.loads(old_txt) != json.loads(new_txt):
        raise SystemExit(f"FAIL engine parity\nOLD {old_txt[:400]}\nNEW {new_txt[:400]}")

    compose_new = rpc(new_cmd, [{"method": "tools/call", "params": {"name": "rigds_compose", "arguments": {"preset": "converter"}}}])
    compose_txt = text_of(compose_new["tools/call:2"])
    compose_obj = json.loads(compose_txt)
    if compose_obj.get("error") or compose_new["tools/call:2"].get("result", {}).get("isError"):
        raise SystemExit(f"FAIL compose: {compose_txt[:400]}")
    if compose_obj.get("preset") != "converter" or not compose_obj.get("stack"):
        raise SystemExit(f"FAIL compose stack: {compose_txt[:400]}")

    pass_path = str(SKILL / "fixtures" / "pass.json")
    fail_path = str(SKILL / "fixtures" / "fail-empty.json")
    scored = rpc(new_cmd, [
        {"method": "tools/call", "params": {"name": "rigds_satori_score", "arguments": {"path": pass_path}}},
        {"method": "tools/call", "params": {"name": "rigds_satori_score", "arguments": {"path": fail_path}}},
    ])
    ok = scored["tools/call:2"]
    bad = scored["tools/call:3"]
    if ok.get("result", {}).get("isError"):
        raise SystemExit(f"FAIL pass fixture isError: {text_of(ok)}")
    if not text_of(ok).startswith("PASS"):
        raise SystemExit(f"FAIL pass fixture text: {text_of(ok)}")
    if not bad.get("result", {}).get("isError"):
        raise SystemExit(f"FAIL empty fixture isError false: {text_of(bad)}")
    if not text_of(bad).startswith("FAIL:"):
        raise SystemExit(f"FAIL empty fixture text: {text_of(bad)}")
    print("PASS contract: 6-tool parity + satori PASS/FAIL isError")


if __name__ == "__main__":
    main()
