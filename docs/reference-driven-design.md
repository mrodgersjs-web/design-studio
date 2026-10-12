# Reference-driven design with AI surfaces

How to get production-grade output from an AI design tool instead of the tool's house style.

The claim this document rests on: **curated references from real shipped products outperform
prompting from scratch, and the first generation is never the deliverable.** Two unrelated
practitioners arrived at that independently within a five-day window (sources at the bottom);
the checklist form is [`checklists/ai-design-review.md`](../checklists/ai-design-review.md).

## Why references beat prompting

A prompt describes intent in words. A reference *shows* a solved problem — one where somebody
already resolved density, empty states, error states, and real data lengths under production
pressure. Prompting from scratch asks the model to re-derive all of that from its prior, and
its prior is the average of everything it saw. The average is exactly what "AI-looking" means.

This is why the sourcing rule is specific: pull from libraries of **shipped** app and web
screens, not from concept galleries. Concept work optimizes for the portfolio shot — one state,
ideal data, no error path. It transfers aesthetics without transferring constraints.

## The procedure

### 1. Write the PRD first

Functional jobs, not visuals. Skipping this and going straight to UI is the named failure mode:
you end up with something attractive that "doesn't really feel like it does the thing that you
were intending for it to do." The PRD is also what you reconcile against at the end.

### 2. Curate 3–6 real references

Hand-pick the strongest shipped screens or flows for the specific problem. Quantity is not the
goal — a small set of exactly-right references outperforms a large mood dump.

### 3. Annotate them

Put the references on a board and mark up *what specifically* works about each: typography,
spacing, hierarchy, motion, layering. This is the step most people skip, and it is the step that
converts a reference from "vibe" into "instruction." An unannotated screenshot leaves the model
guessing which property you actually wanted.

### 4. Structure the prompt

Four parts plus a gate:

1. Role.
2. The assignment.
3. The exact style/vibe target.
4. An explicit instruction to read the annotations.
5. **The confidence gate** — require the model to ask clarifying questions until it is
   near-certain, and explicitly forbid assuming.

The gate is the highest-value line in the prompt. Answer every question it asks; more questions
is a better signal, not a worse one.

### 5. Generate, then iterate surgically

The first pass is a starting point. Iterate with named-element, named-change feedback — *this*
font to *that* font, uppercase it, remove these three elements, make the text full-bleed, fix
the layering so tiles flow over the headline. Vague feedback ("make it better") returns noise
because it contains no information.

### 6. Pull specific patterns on demand

When a particular component is needed — a picker, an onboarding sequence, an empty state — pull
a real reference for *that pattern* rather than describing it. Same principle, finer grain.

### 7. Reconcile and hand off

Take the final designs back to the PRD and align schema, data model, and implementation stories
before building. Then export to code and ship through the normal pipeline.

## Connecting a reference corpus programmatically

Manual export works and needs no setup: build the annotated board, export it, attach it with any
project assets. That is sufficient for a single surface.

At corpus scale the better path is an **MCP connector**. A reference library exposed over MCP
lets the design surface query it directly — searching screens, flows, and sections — instead of
you pre-selecting and uploading everything. In the sourced walkthrough this was set up once in
the desktop client's connector settings and then became available in the web design surface
automatically, exposing search over a library the presenter described as "over half a million
screens."

The tradeoff is honest: manual upload gives you tight curatorial control, MCP gives you reach
and lets you pull a matching pattern mid-iteration without leaving the tool. Corpus reach does
not remove the annotation step — it only removes the fetching step.

## Failure modes

| Failure | What it looks like | Fix |
|---|---|---|
| No PRD | Beautiful, doesn't do the job | Write functional jobs first |
| No references | Generic, "AI-looking" | Pull 3–6 shipped screens |
| References unannotated | Vibe transferred, intent lost | Mark up what specifically works |
| Stopped at first pass | The most common failure | Treat pass 1 as a draft, always |
| Vague feedback | Noise in, noise out | Name the element, name the change |
| Concept galleries as source | No real constraints carried | Use shipped product screens |

## Sources

Two independent practitioner walkthroughs, no shared affiliation, five days apart:

- Tae Online HD — *The Workflow That Makes My AI Designs Look UNREAL* (2026-08-07). Manual
  path: curate → annotate on a board → structured prompt with the confidence gate → surgical
  iteration → export to code → deploy.
- Sean Kochel — *I Fed Claude Code 600,000 Designs. Here's What Happened* (2026-08-05).
  Corpus path: PRD first → reference library over MCP → generate multiple directions → pull
  specific patterns mid-iteration → reconcile to PRD.

Where they agree — references over prompting, first pass is a draft, precise feedback — the
guidance above is stated as a rule. Where only one covers a topic (MCP wiring, deployment
path), it is described as one practitioner's path rather than doctrine.
