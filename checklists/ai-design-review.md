# AI design review checklist

For work generated with an AI design surface (Claude Design, v0, Lovable, or similar).
Complements [`ui-review.md`](./ui-review.md) — that one checks the artifact, this one checks
the *process that produced it*, because generic AI output is a process failure, not a taste
failure.

## Gate 1 — Before generating

- [ ] A functional PRD exists and is written down — what jobs the product must perform, not
      what it should look like. Design that starts at the visual layer produces something that
      "doesn't feel like it does the thing."
- [ ] 3–6 references pulled from **real shipped products**, not concept galleries. Shipped
      screens carry solved constraints — empty states, error states, dense real data. Concept
      art carries none of that.
- [ ] References are **annotated**, not merely attached. Each one says *what specifically*
      works: typography, spacing, hierarchy, motion, z-index, hover behavior. An unannotated
      screenshot transfers vibe; an annotated one transfers intent.
- [ ] The prompt states role, assignment, target style, and an explicit instruction to read the
      annotations.
- [ ] The prompt ends with a confidence gate — require clarifying questions until the model is
      near-certain, and forbid assuming. More clarifying questions is a better signal, not a
      worse one.

## Gate 2 — After the first pass

- [ ] The first generation was treated as a **starting point, not a deliverable.** Stopping
      here is the single most common failure and it is what "AI-looking" means.
- [ ] Feedback given was surgical and component-specific — name the element, name the change.
      "Make it look better" is not feedback and will be answered with noise.
- [ ] At least one iteration addressed a detail class the model does not volunteer:
      micro-interactions, hover states, z-index/layering, full-bleed treatment, or type
      consistency.
- [ ] Where a specific pattern was needed (a picker, an onboarding sequence, an empty state), a
      real reference for *that pattern* was pulled rather than described in prose.

## Gate 3 — Before it ships

- [ ] Output is editorial and purposeful rather than busy — hierarchy reads, whitespace is
      intentional, type is not default.
- [ ] The references beat the model's default taste in every major element. If the result looks
      like the tool's house style, the references did not land.
- [ ] Final design was reconciled back against the PRD — the screens serve the jobs.
- [ ] [`ui-review.md`](./ui-review.md) passes: hierarchy at 100% zoom, AA contrast, visible
      focus states, no lorem in the ship path, public boundary respected.

## Scoring

Gate 1 and Gate 2 are pass/fail as a set — a miss in either is what produces generic output.
Ship requires all three gates. A design that passes Gate 3 while failing Gate 1 is a design that
got lucky and will not reproduce.

## Provenance

Distilled from two independent practitioner walkthroughs published five days apart
(Tae Online HD, 2026-08-07; Sean Kochel, 2026-08-05). They share no affiliation and converge on
the same core claim: **references from real shipped products beat prompting from scratch**, and
the first pass is never the deliverable. Convergence across unrelated sources is the reason this
is a checklist and not a preference. See
[`docs/reference-driven-design.md`](../docs/reference-driven-design.md) for the full procedure
and tooling.
