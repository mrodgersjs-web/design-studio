"""tokens-toolkit CLI:

  validate     parse a token JSON file and run per-kind validators
  export       write CSS, JSON, Tailwind or Markdown for a token file
  contrast     compare two colors; print the WCAG 2.1 result
  checklist    print the parsed UI review checklist as JSON or Markdown
  tokens       print the parsed tokens as JSON

All commands return 0 on success, 1 on a validation failure, 2 on bad
input. Output is JSON for ``tokens``, ``checklist``, and ``contrast``,
and the requested format for ``export``.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from . import checklists, contrast, exporter, parser

__version__ = "0.1.0"


EXIT_OK = 0
EXIT_VALIDATION_FAILED = 1
EXIT_BAD_INPUT = 2


def _read_tokens(path_arg: str) -> parser.TokenFile:
    if path_arg == "-":
        text = sys.stdin.read()
        return parser.parse_token_object(json.loads(text), source="<stdin>")
    return parser.parse_token_file(Path(path_arg))


def _emit(obj: object) -> None:
    print(json.dumps(obj, indent=2, sort_keys=True, default=str))


def cmd_validate(args: argparse.Namespace) -> int:
    tf = _read_tokens(args.file)
    errors = parser.validate(tf)
    payload = {
        "schema": tf.schema,
        "count": len(tf.tokens),
        "kinds": tf.kinds(),
        "errors": errors,
        "ok": not errors,
    }
    _emit(payload)
    return EXIT_OK if not errors else EXIT_VALIDATION_FAILED


def cmd_export(args: argparse.Namespace) -> int:
    tf = _read_tokens(args.file)
    errors = parser.validate(tf)
    fmt = args.format
    if fmt == "css":
        text = exporter.to_css(tf)
    elif fmt == "json":
        text = exporter.to_json(tf)
    elif fmt == "tailwind":
        text = exporter.to_tailwind(tf)
    elif fmt == "markdown":
        text = exporter.to_markdown_table(tf)
    else:
        print(json.dumps({"ok": False, "error": f"unknown format: {fmt}"}), file=sys.stderr)
        return EXIT_BAD_INPUT
    if args.out:
        Path(args.out).write_text(text, encoding="utf-8")
        _emit({"ok": not errors, "written": args.out, "bytes": len(text)})
    else:
        sys.stdout.write(text)
    return EXIT_OK if not errors else EXIT_VALIDATION_FAILED


def cmd_contrast(args: argparse.Namespace) -> int:
    try:
        result = contrast.check(args.foreground, args.background)
    except contrast.ContrastError as exc:
        _emit({"ok": False, "error": str(exc)})
        return EXIT_BAD_INPUT
    fg = contrast.parse_color(args.foreground)
    bg = contrast.parse_color(args.background)
    # If foreground is translucent, compose it for the printed pair.
    if fg.alpha < 1.0:
        fg = contrast.composite(fg, bg)
    payload = {
        "ok": True,
        "foreground": args.foreground,
        "background": args.background,
        "result": result.to_dict(),
    }
    _emit(payload)
    return EXIT_OK if result.aa_normal else EXIT_VALIDATION_FAILED


def cmd_checklist(args: argparse.Namespace) -> int:
    path = Path(args.file)
    try:
        cl = checklists.parse_checklist_file(path)
    except (OSError, ValueError) as exc:
        _emit({"ok": False, "error": str(exc)})
        return EXIT_BAD_INPUT
    if args.format == "json":
        sys.stdout.write(checklists.render_checklist_json(cl))
    elif args.format == "markdown":
        sys.stdout.write(checklists.render_checklist_markdown(cl))
    else:
        print(json.dumps({"ok": False, "error": f"unknown format: {args.format}"}), file=sys.stderr)
        return EXIT_BAD_INPUT
    return EXIT_OK


def cmd_tokens(args: argparse.Namespace) -> int:
    tf = _read_tokens(args.file)
    payload = {
        "schema": tf.schema,
        "tokens": [tok.to_dict() for tok in sorted(tf.tokens, key=lambda t: t.name)],
    }
    _emit(payload)
    return EXIT_OK


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="tokens-toolkit",
        description="Validate, export, and check design tokens.",
    )
    p.add_argument("--version", action="version", version=f"tokens-toolkit {__version__}")
    sub = p.add_subparsers(dest="cmd", required=True)

    v = sub.add_parser("validate", help="validate a token JSON file")
    v.add_argument("file", help="JSON file path, or '-' for stdin")
    v.set_defaults(func=cmd_validate)

    e = sub.add_parser("export", help="export tokens to CSS / JSON / Tailwind / Markdown")
    e.add_argument("file", help="JSON file path, or '-' for stdin")
    e.add_argument("--format", required=True, help="css | json | tailwind | markdown")
    e.add_argument("--out", help="write to this path instead of stdout")
    e.set_defaults(func=cmd_export)

    c = sub.add_parser("contrast", help="WCAG contrast between two colors")
    c.add_argument("foreground", help="foreground CSS color (hex, rgb(), rgba())")
    c.add_argument("background", help="background CSS color (hex, rgb(), rgba())")
    c.set_defaults(func=cmd_contrast)

    k = sub.add_parser("checklist", help="render a UI review checklist")
    k.add_argument("file", help="Markdown checklist file")
    k.add_argument("--format", default="markdown", help="json | markdown (anything else returns 'unknown format')")
    k.set_defaults(func=cmd_checklist)

    t = sub.add_parser("tokens", help="print the parsed tokens as JSON")
    t.add_argument("file")
    t.set_defaults(func=cmd_tokens)
    return p


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    return int(args.func(args))


if __name__ == "__main__":
    raise SystemExit(main())
