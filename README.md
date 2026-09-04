# design-studio
<p align="center"><img src="docs/rig-design-studio-demo.gif" alt="demo" width="720" /></p>

> **Public-safe design systems surface for FDE delivery — tokens, components, and review checklists.**
**Outcome:** One-command smoke (`bash scripts/smoke.sh`) verifies the studio in a 60-second proof path.


![status](https://img.shields.io/badge/status-public-studio-blue)
![license](https://img.shields.io/badge/license-MIT-green)

## Employer summary
Shows design discipline next to systems work: clear tokens, component contracts, and a review checklist used when embedding with customers.

## Proof in 60 seconds
```bash
git clone https://github.com/mrodgersjs-web/design-studio.git
cd design-studio && bash scripts/smoke.sh
```

## Architecture
```text
brief → tokens → components → a11y/review checklist → handoff
```

## Checklists
- [`checklists/ui-review.md`](checklists/ui-review.md) — artifact review (hierarchy, contrast, focus states).
- [`checklists/ai-design-review.md`](checklists/ai-design-review.md) — process review for AI-generated design; three gates that separate production output from the tool's house style.

## Reference-driven AI design
[`docs/reference-driven-design.md`](docs/reference-driven-design.md) — curated references from real shipped products beat prompting from scratch, and the first generation is never the deliverable. Derived from two independent practitioner walkthroughs that converge on the same rule.

## Public boundary
No private brand OS dumps, no customer Figma exports with confidential product IP.
See `docs/public-boundary.md`.

## Video
- [`assets/demo.mp4`](assets/demo.mp4)

## Related
- [fde-portfolio](https://github.com/mrodgersjs-web/fde-portfolio)
- [doctrine](https://github.com/mrodgersjs-web/doctrine)
