#!/usr/bin/env python3
"""Source-tree MCP contract against frozen legacy six-tool fixtures.

Does not use live `rigds-mcp` as an oracle (that is the current wheel).
Satori FAIL must set isError true. Empty stdout is child EOF, not a timeout spin.
"""
from __future__ import annotations

import json
import os
import select
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent
REPO = ROOT.parent
SKILL = REPO / "skills" / "rig-design-studio-satori-apple"
FIXTURE = ROOT / "fixtures" / "legacy-tools.json"


def rpc(cmd, calls, timeout=8, env=None):
    proc = subprocess.Popen(
        cmd,
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        env=env,
    )
    try:
        def send(obj):
            proc.stdin.write(json.dumps(obj) + "\n")
            proc.stdin.flush()

        def read():
            start = time.time()
            while time.time() - start < timeout:
                ready, _, _ = select.select([proc.stdout], [], [], 0.2)
                if not ready:
                    if proc.poll() is not None:
                        raise SystemExit(
                            f"exit {proc.returncode} stderr={proc.stderr.read()[:800]}"
                        )
                    continue
                line = proc.stdout.readline()
                if line == "":
                    raise SystemExit(
                        f"EOF exit={proc.poll()} stderr={proc.stderr.read()[:800]}"
                    )
                return json.loads(line)
            raise SystemExit(f"timeout cmd={cmd} exit={proc.poll()}")

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
    legacy = {t["name"]: t for t in json.loads(FIXTURE.read_text())}
    cmd = [sys.executable, "-m", "rigds_mcp.server"]
    env = dict(os.environ)
    env["PYTHONPATH"] = str(REPO) + (os.pathsep + env["PYTHONPATH"] if env.get("PYTHONPATH") else "")
    listed = rpc(cmd, [{"method": "tools/list"}], env=env)
    tools = tool_map(listed["tools/list:2"])
    missing = [n for n in legacy if n not in tools]
    if missing:
        raise SystemExit(f"FAIL missing core tools: {missing}")
    for name, spec in legacy.items():
        if tools[name]["inputSchema"] != spec["inputSchema"]:
            raise SystemExit(f"FAIL schema drift on {name}")
        if tools[name]["description"] != spec["description"]:
            raise SystemExit(f"FAIL description drift on {name}")
    if "rigds_satori_skill" not in tools or "rigds_satori_score" not in tools:
        raise SystemExit("FAIL missing satori tools")

    engine = rpc(cmd, [{"method": "tools/call", "params": {"name": "rigds_engine", "arguments": {}}}], env=env)
    engine_txt = text_of(engine["tools/call:2"])
    if engine["tools/call:2"].get("result", {}).get("isError"):
        raise SystemExit(f"FAIL engine isError: {engine_txt[:400]}")

    compose = rpc(cmd, [{"method": "tools/call", "params": {"name": "rigds_compose", "arguments": {"preset": "converter"}}}], env=env)
    compose_txt = text_of(compose["tools/call:2"])
    compose_obj = json.loads(compose_txt)
    if compose_obj.get("error") or compose["tools/call:2"].get("result", {}).get("isError"):
        raise SystemExit(f"FAIL compose: {compose_txt[:400]}")
    if compose_obj.get("preset") != "converter" or not compose_obj.get("stack"):
        raise SystemExit(f"FAIL compose stack: {compose_txt[:400]}")

    pass_path = str(SKILL / "fixtures" / "pass.json")
    fail_path = str(SKILL / "fixtures" / "fail-empty.json")
    scored = rpc(cmd, [
        {"method": "tools/call", "params": {"name": "rigds_satori_score", "arguments": {"path": pass_path}}},
        {"method": "tools/call", "params": {"name": "rigds_satori_score", "arguments": {"path": fail_path}}},
    ], env=env)
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
    print("PASS contract: fixture six-tool schemas + satori PASS/FAIL isError")


if __name__ == "__main__":
    main()
