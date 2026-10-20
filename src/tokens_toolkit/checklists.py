"""Structured UI review checklist.

The toolkit reads ``checklists/ui-review.md`` (Markdown + YAML frontmatter)
and exposes each check as a small dataclass. Each check has an id, a
question, optional details, an optional severity, and an optional list
of pass criteria.

Consumers (CI, the CLI, the docs site) can iterate over the checks,
render them as Markdown or as a JSON block, and grade a design review
against them.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
import re

YAML_FRONT = re.compile(r"^---\s*\n(.*?)\n---\s*\n(.*)$", re.DOTALL)


@dataclass(frozen=True)
class ChecklistItem:
    id: str
    text: str
    severity: str = "should"     # "must" | "should" | "may"
    pass_criteria: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class Checklist:
    name: str
    description: str
    items: list[ChecklistItem]

    def item(self, key: str) -> ChecklistItem | None:
        for it in self.items:
            if it.id == key:
                return it
        return None


def parse_checklist_file(path: Path) -> Checklist:
    """Parse a Markdown checklist file with YAML frontmatter."""
    raw = path.read_text(encoding="utf-8")
    return parse_checklist_text(raw, source=str(path))


def parse_checklist_text(raw: str, *, source: str = "<memory>") -> Checklist:
    m = YAML_FRONT.match(raw)
    if not m:
        raise ValueError(f"{source}: expected YAML frontmatter delimited by '---' at the top")
    front, body = m.group(1), m.group(2)
    meta = _tiny_yaml(front, source=source + ":frontmatter")
    if "name" not in meta or "items" not in meta:
        raise ValueError(f"{source}: frontmatter must include 'name' and 'items'")
    description = str(meta.get("description", ""))
    raw_items = meta["items"]
    if not isinstance(raw_items, list):
        raise ValueError(f"{source}: items must be a list")
    if not raw_items:
        raise ValueError(f"{source}: items must contain at least one entry")
    items: list[ChecklistItem] = []
    known_ids: set[str] = set()
    for entry in raw_items:
        if not isinstance(entry, dict):
            raise ValueError(f"{source}: each item must be a mapping; got {type(entry).__name__}")
        item_id = str(entry.get("id", "")).strip()
        text = str(entry.get("text", "")).strip()
        if not item_id or not text:
            raise ValueError(f"{source}: each item needs non-empty 'id' and 'text'; got {entry!r}")
        if item_id in known_ids:
            raise ValueError(f"{source}: duplicate item id {item_id!r}")
        known_ids.add(item_id)
        severity = str(entry.get("severity", "should")).strip().lower()
        if severity not in {"must", "should", "may"}:
            raise ValueError(f"{source}: item {item_id!r} severity must be must/should/may; got {entry!r}")
        criteria = entry.get("pass_criteria", [])
        if criteria is None:
            criteria = []
        if isinstance(criteria, str):
            # Allow a one-line scalar (``pass_criteria: ratio >= 4.5``) as
            # a single-element list -- the practical shape we accept.
            criteria = [criteria]
        if not isinstance(criteria, list) or not all(isinstance(c, str) for c in criteria):
            raise ValueError(f"{source}: item {item_id!r} pass_criteria must be a list of strings")
        items.append(ChecklistItem(id=item_id, text=text, severity=severity, pass_criteria=list(criteria)))
    return Checklist(name=str(meta["name"]), description=description, items=items)


def render_checklist_markdown(cl: Checklist) -> str:
    """Render a checklist back to its Markdown form (id, severity, question, criteria)."""
    out: list[str] = [f"## {cl.name}", ""]
    if cl.description:
        out += [cl.description, ""]
    for it in cl.items:
        bullet = {"must": "- [ ] MUST", "should": "- [ ] should", "may": "- [ ] may"}.get(it.severity, "- [ ]")
        out.append(f"{bullet} **{it.id}** — {it.text}")
        if it.pass_criteria:
            for c in it.pass_criteria:
                out.append(f"    - {c}")
    out.append("")
    return "\n".join(out)


def render_checklist_json(cl: Checklist) -> str:
    """Render a checklist as a JSON object for tool consumers."""
    import json

    payload = {
        "name": cl.name,
        "description": cl.description,
        "items": [
            {
                "id": it.id,
                "severity": it.severity,
                "text": it.text,
                "pass_criteria": it.pass_criteria,
            }
            for it in cl.items
        ],
    }
    return json.dumps(payload, indent=2, sort_keys=True) + "\n"


# ----- tiny YAML subset parser ------------------------------------------------
# We don't depend on PyYAML. The Checklist format is constrained:
# top-level is a mapping of scalars and one list-of-mappings called "items".


def _tiny_yaml(text: str, *, source: str = "<yaml>") -> dict:
    """Parse the frontmatter into a dict of scalars plus an 'items' list.

    Supports:
    * ``key: value`` scalars (value is a string)
    * ``items:`` followed by an indented block of ``- id: ... / text: ...``
      mappings whose continuation lines may share the same indent as the
      list bullets (two spaces here, matching our Markdown format).
    * line continuations for multi-line ``>`` folded scalars (not used here)
    """
    out: dict = {}
    lines = text.splitlines()
    i = 0
    while i < len(lines):
        line = lines[i]
        if not line.strip() or line.lstrip().startswith("#"):
            i += 1
            continue
        if ":" not in line:
            i += 1
            continue
        head_indent = len(line) - len(line.lstrip())
        key, value = line.split(":", 1)
        key = key.strip()
        value = value.strip()
        next_line = lines[i + 1] if i + 1 < len(lines) else ""
        next_is_list_item = next_line.lstrip().startswith("- ")
        if value == "" and next_is_list_item:
            next_indent = len(next_line) - len(next_line.lstrip())
            list_indent = next_indent
            items: list[dict] = []
            i += 1
            while i < len(lines):
                cur = lines[i]
                cur_indent = len(cur) - len(cur.lstrip())
                cur_stripped = cur.strip()
                if cur_stripped == "":
                    i += 1
                    continue
                is_item_bullet = cur.lstrip().startswith("- ")
                if is_item_bullet:
                    if cur_indent < list_indent:
                        break
                    first = cur.lstrip()[2:]
                    if not first.strip() or ":" not in first:
                        i += 1
                        continue
                    current: dict = {}
                    k, v = first.split(":", 1)
                    current[k.strip()] = _coerce_scalar(v.strip())
                    i += 1
                    # Eat continuation lines for THIS item until the next
                    # bullet or a less-indented line.
                    while i < len(lines):
                        cont = lines[i]
                        cont_indent = len(cont) - len(cont.lstrip())
                        cont_stripped = cont.strip()
                        if cont_stripped == "":
                            i += 1
                            continue
                        if cont_indent < list_indent + 2:
                            break
                        if cont.lstrip().startswith("- "):
                            break
                        if ":" not in cont_stripped:
                            i += 1
                            continue
                        k2, v2 = cont_stripped.split(":", 1)
                        current[k2.strip()] = _coerce_scalar(v2.strip())
                        i += 1
                    items.append(current)
                    continue
                # not a bullet line inside a list
                if cur_indent < list_indent:
                    break
                i += 1
            out[key] = items
            continue
        out[key] = _coerce_scalar(value)
        i += 1
    return out


def _coerce_scalar(value: str):
    """A scalar in our subset is a quoted string or an empty string.

    YAML scalars are strings; we do not interpret them.
    """
    value = value.strip()
    if not value:
        return ""
    if (value.startswith('"') and value.endswith('"')) or (value.startswith("'") and value.endswith("'")):
        return value[1:-1]
    return value
