---
name: UI review
description: The checklist run on every shipped page.
items:
- id: hierarchy
  severity: must
  text: Hierarchy is readable at 100% browser zoom.
  pass_criteria:
    - H1 is the largest text on the page
    - Body line-height between 1.4 and 1.6
- id: contrast
  severity: must
  text: Body text contrast meets WCAG 2.1 AA.
  pass_criteria:
    - run tokens-toolkit contrast on every fg/bg token pair used in shipped views
- id: focus
  severity: must
  text: Focus state is visible on every interactive element.
  pass_criteria:
    - Tab from the URL bar reaches every control
    - Focus ring is at least 2px and contrasts with its background
- id: lorem
  severity: must
  text: No placeholder lorem in the ship path.
- id: boundary
  severity: must
  text: Public boundary respected (no PII, no secrets, no confidential brand assets).
  pass_criteria:
    - cross-checked against docs/public-boundary.md
- id: figures
  severity: should
  text: Key numbers cite a real source or are explicitly labelled 'to verify'.
- id: navigation
  severity: should
  text: Primary navigation works without JavaScript where it does not need it.
- id: motion
  severity: may
  text: Motion respects prefers-reduced-motion.
---

# UI review checklist

This checklist is structured data: the YAML frontmatter above is what
`tokens-toolkit checklist checklists/ui-review.md --format json` parses
and renders. The Markdown body below the frontmatter is human-readable.

## How to run

```bash
tokens-toolkit checklist checklists/ui-review.md --format markdown
```

## Items

| ID | Severity | Question |
| --- | --- | --- |
| hierarchy | must | Hierarchy is readable at 100% browser zoom. |
| contrast | must | Body text contrast meets WCAG 2.1 AA. |
| focus | must | Focus state is visible on every interactive element. |
| lorem | must | No placeholder lorem in the ship path. |
| boundary | must | Public boundary respected (no PII, no secrets, no confidential brand assets). |
| figures | should | Key numbers cite a real source or are explicitly labelled 'to verify'. |
| navigation | should | Primary navigation works without JavaScript where it does not need it. |
| motion | may | Motion respects prefers-reduced-motion. |
