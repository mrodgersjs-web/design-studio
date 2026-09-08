#!/usr/bin/env python3
"""Build a wheel, install it in a fresh venv, prove compose + Satori tools."""
from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
SKILL = REPO / "skills" / "rig-design-studio-satori-apple"


def run(cmd, **kwargs):
    return subprocess.check_output(cmd, text=True, **kwargs)


def main():
    py = sys.executable
    with tempfile.TemporaryDirectory(prefix="rigds-wheel-") as tmp:
        tmp = Path(tmp)
        dist = tmp / "dist"
        venv = tmp / "venv"
        dist.mkdir()
        run([py, "-m", "pip", "wheel", str(REPO), "-w", str(dist), "--no-deps"], cwd=str(REPO))
        wheels = list(dist.glob("rigds_mcp-*.whl"))
        if not wheels:
            raise SystemExit(f"FAIL no wheel in {list(dist.iterdir())}")
        run([py, "-m", "venv", str(venv)])
        vpy = venv / "bin" / "python"
        run([str(vpy), "-m", "pip", "install", str(wheels[0])])
        probe = r"""
import json
from rigds_mcp.server import call, compose
c = compose("converter", None)
assert c.get("preset") == "converter" and c.get("stack"), c
info = json.loads(call("rigds_satori_skill", {}))
assert info.get("version") == "0.1.0", info
assert info.get("scorecard") == "package:rigds_mcp/scorecard.py", info
print("COMPOSE", len(c["stack"]))
print("SKILL_OK", info["version"])
"""
        out = run([str(vpy), "-c", probe])
        print(out.strip())
        pass_path = SKILL / "fixtures" / "pass.json"
        fail_path = SKILL / "fixtures" / "fail-empty.json"
        score = r"""
import json, sys
from rigds_mcp.server import call
ok = call("rigds_satori_score", {"path": sys.argv[1]})
bad = call("rigds_satori_score", {"path": sys.argv[2]})
assert ok.startswith("PASS"), ok
assert bad.startswith("FAIL:"), bad
print("SCORE_PASS")
print("SCORE_FAIL")
"""
        scored = run([str(vpy), "-c", score, str(pass_path), str(fail_path)])
        print(scored.strip())
        # prove catalog file is inside the venv site-packages, not the source tree
        loc = run([str(vpy), "-c", "import rigds_mcp, pathlib; print(pathlib.Path(rigds_mcp.__file__).resolve())"])
        loc_p = Path(loc.strip())
        if REPO.resolve() in loc_p.parents or loc_p == REPO.resolve():
            raise SystemExit(f"FAIL wheel import still source tree: {loc_p}")
        print("WHEEL_MODULE", loc_p)
    print("PASS wheel: compose stack + satori skill/score from isolated install")


if __name__ == "__main__":
    main()
