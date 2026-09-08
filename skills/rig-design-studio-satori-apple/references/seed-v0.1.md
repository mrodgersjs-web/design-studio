---
title: RIG Design Studio Skillset — Satori Corpus + Apple Communication-First Gate v0.1
tags:
  - "Design Studio"
  - "Agent Skills"
  - "Harness Design"
  - "Skill Crystallization"
  - "Web Design"
createdAt: Tue Sep 08 2026 07:17:55 GMT-0600 (Mountain Daylight Time)
updatedAt: Tue Sep 08 2026 07:17:55 GMT-0600 (Mountain Daylight Time)
---



## Purpose
A governed design skillset for RIG Design Studio and its coding agents. It converts Satori Graphics lessons into testable design behavior rather than stylistic imitation.

**Transformation authored:** turn an unclear interface into a product whose value, action, and emotional promise are understood almost immediately.

**Cheapest vehicle:** a compact, versioned rubric plus evidence packet, not a giant inspiration prompt.


## Constitutional Apple gate
Every design decision begins with:

> **What helps people understand and desire this product?**

Apple’s operating pattern in the seed lesson is communication-first: define the communication problem, remove anything competing with the product, and add only what is necessary to solve the problem. Every element must earn its place. A design fails even when attractive if it cannot explain why each decision improves comprehension, desire, trust, or action.


### Non-negotiable proof questions
1. What must the user understand first?
2. What should the user desire or feel?
3. What single action should happen next?
4. Which element currently competes with that outcome?
5. Why does every visible element deserve to remain?
6. Can every design choice be defended aloud without appealing to personal taste?

## Harness contract
```yaml
name: rig-design-studio-satori-apple
version: 0.1.0
identity: communication-first product design director
method: brief -> communication problem -> hierarchy -> constrained composition -> implementation -> independent critique -> verification
allowed_inputs:
  - product brief
  - audience and context
  - brand system
  - interface requirements
  - verified Satori lesson records
required_outputs:
  - rendered artifact
  - criterion scorecard
  - decision ledger
  - responsive screenshots
  - accessibility report
  - unresolved-risk list
termination_authority: independent_design_verifier
forbidden:
  - decoration without communicative function
  - unsupported attribution
  - self-approval by generator
  - hidden retries
  - shipping with missing proof
```


## 60 design criteria
Score each criterion **0 = fail, 1 = weak, 2 = pass, 3 = exceptional**. Criteria marked **GATE** must score at least 2. A total score cannot compensate for a failed gate.


### A. Communication and product desire
1. **GATE — Primary understanding:** the intended meaning is identifiable without explanation.
2. **GATE — Product primacy:** the product or core outcome is the visual center of gravity.
3. **GATE — Communication problem:** the brief names the exact misunderstanding the design must eliminate.
4. **GATE — Desire mechanism:** the composition makes the benefit emotionally desirable, not merely legible.
5. **Message compression:** the core promise can be stated in one sentence.
6. **Two-second read:** the first impression communicates the correct category and value.
7. **One dominant idea:** the artifact has one unmistakable concept rather than several competing concepts.
8. **Attention competition:** decorative elements do not fight with the product, offer, or next action.
9. **Audience language:** copy and imagery match the audience’s vocabulary and sophistication.
10. **Decision traceability:** every major visual choice maps to comprehension, desire, trust, or action.

### B. Brief, audience, and journey
11. **GATE — Brief before polish:** audience, goal, constraints, and success condition exist before high-fidelity work.
12. **Audience specificity:** the intended user is behavioral and contextual, not a vague demographic.
13. **Viewing context:** distance, device, lighting, fatigue, motion, and attention scarcity are considered.
14. **Journey-first structure:** information order follows the user’s decision sequence.
15. **Expectation match:** the interface meets category conventions unless deviation has a reason.
16. **Emotional target:** the intended feeling is explicitly named.
17. **Brand fit:** premium, playful, technical, urgent, or calm choices fit the actual buyer.
18. **CTA fit:** action tone matches context; it does not scream when a quiet nudge is appropriate.
19. **Reverse brief test:** an evaluator can infer audience, goal, emotion, and CTA from the artifact.
20. **Non-designer test:** an ordinary user can identify purpose and next step without design vocabulary.

### C. Hierarchy and attention
21. **GATE — First fixation:** the intended first element reliably wins attention.
22. **Second and third order:** subsequent reading order is deliberate and stable.
23. **Visual-weight separation:** primary, secondary, and tertiary elements do not speak at equal volume.
24. **Hero dominance:** hero scale reflects its communicative importance.
25. **Offer visibility:** value and offer can be understood in seconds.
26. **CTA visibility:** the next action is findable without scanning the whole screen.
27. **Spacing hierarchy:** spacing groups related elements and separates unrelated ones.
28. **Color hierarchy:** color directs attention rather than coating everything equally.
29. **Weight hierarchy:** font and stroke weights encode importance consistently.
30. **90-second repair test:** hierarchy can be improved using only size, weight, color, and spacing before adding effects.

### D. Layout, balance, movement, and flow
31. **GATE — Reading path:** the eye has a clear entry, route, and destination.
32. **Alignment discipline:** alignment is consistent or intentionally broken for communication.
33. **Grid coherence:** placement follows a visible structural logic.
34. **Proximity:** related elements form perceptual groups.
35. **Balance:** visual mass feels intentional, whether symmetrical or asymmetrical.
36. **Movement:** direction, cropping, diagonals, gaze, and repetition guide the eye.
37. **Flow continuity:** no dead end or accidental loop interrupts the journey.
38. **Whitespace function:** negative space clarifies grouping and emphasis.
39. **Center of gravity:** composition feels anchored rather than scattered.
40. **Responsive preservation:** hierarchy and reading order survive all required breakpoints.

### E. Typography
41. **GATE — Readability:** essential text remains readable at real size and realistic conditions.
42. **Typographic voice:** weight, scale, tracking, italics, and alignment express the intended personality.
43. **Role clarity:** headline, subhead, body, metadata, and CTA roles are unmistakable.
44. **Typeface restraint:** additional typefaces are introduced only when one family cannot solve the role.
45. **Superfamily leverage:** available widths and weights are explored before font proliferation.
46. **Measure and leading:** line length and spacing support effortless reading.
47. **Contrast compliance:** text/background contrast passes accessibility requirements.
48. **Copy density:** text volume matches the user’s available attention.
49. **Microtype consistency:** casing, punctuation, numerals, and labels follow one system.
50. **Typography-only test:** hierarchy and mood still work when imagery and color are removed.

### F. Color, imagery, and emotional signal
51. **GATE — Emotional congruence:** color and imagery produce the feeling named in the brief.
52. **Color-ratio intent:** dominant, supporting, and accent colors have explicit proportions.
53. **Accent scarcity:** accent color is reserved for true emphasis.
54. **Premium restraint:** luxury cues use muted fields and sparse accents rather than constant gold or visual noise.
55. **Accessible distinction:** state and meaning never depend on color alone.
56. **Image relevance:** imagery advances product understanding or desire.
57. **Image focal control:** crop, gaze, contrast, and scale reinforce the intended focal point.
58. **Memorable anomaly:** any unexpected element strengthens the core idea rather than becoming random novelty.
59. **Cross-touchpoint unity:** typography, color, image treatment, and interaction feel like one identity.
60. **Neutral-state integrity:** the design remains coherent in grayscale and low-brightness conditions.

## Additional implementation gates for coding agents
- Semantic HTML and correct landmarks.
- Keyboard-complete interaction.
- Visible focus states.
- Reduced-motion support.
- No layout shift that damages hierarchy.
- Defined loading, empty, error, success, and disabled states.
- Components use design tokens instead of unexplained one-off values.
- Touch targets meet platform accessibility guidance.
- Copy does not truncate at required breakpoints.
- Performance preserves the authored first impression.

## Agent workflow

### 1. Ingest
Build a manifest of every public video from the main and backup Satori Graphics channels. Store URL, video identifier, title, publication date, duration, playlist, transcript status, and content hash. Deduplicate mirrored uploads by normalized title, transcript similarity, and perceptual thumbnail hash.


### 2. Extract
Chunk transcripts by lesson rather than arbitrary token length. For every candidate lesson record:

```yaml
lesson_id: stable_hash
claim: actionable design principle
problem: failure it addresses
mechanism: why it works
procedure: steps an agent can perform
evidence: exact video URL and timestamp
applies_to: [web, app, brand, typography, layout, color, logo]
counterexample: when misuse causes failure
confidence: calibrated_probability
```

Never treat sponsor copy, jokes, or tool promotion as doctrine. Never attribute a claim without transcript evidence.


### 3. Anti-unify
Cluster repeated lessons into stable procedures: hierarchy, contrast, balance, movement, proximity, unity, typography, color, audience, briefs, workflow, and critique. Preserve disagreements and evolution over time instead of flattening them.


### 4. Generate
The coding agent receives the brief, applicable lesson records, constraints, and criterion subset. It must emit the artifact plus a decision ledger showing which communication problem each major decision solves.


### 5. Grill
Run at least three generator/critic rounds. The critic names failed criteria and evidence; it does not redesign silently. The generator returns explicit fixes and before/after proof.


### 6. Verify
An independent verifier checks rendered output, scorecard, accessibility, responsiveness, and decision traceability. The generator cannot declare completion.


## Release rule
Do not ship when:

- any GATE criterion scores below 2;
- fewer than 90% of applicable criteria score at least 2;
- the evaluator cannot identify product, value, and next action in two seconds;
- any visible element lacks a defensible function;
- accessibility or responsive proofs are missing;
- a cited Satori lesson lacks URL/timestamp evidence.

## Training drills
1. **One typeface, three voices:** express elegant, dynamic, and authoritative using only weight, scale, tracking, italics, and alignment.
2. **Reverse brief:** infer audience, goal, emotion, and CTA from an existing design.
3. **90-second hierarchy repair:** change only size, weight, color, and spacing.
4. **Five-constraint sprint:** 20 minutes, one typeface, three base colors, one hero image, five words.
5. **Style inversion:** translate a design into an opposing visual language while preserving its communication goal.
6. **Decision defense:** explain every choice aloud; inability to justify a choice marks the weakest point.
7. **Color-ratio transfer:** preserve color proportions while replacing the palette.
8. **Two-second field test:** test with tired, distracted non-designers at realistic device brightness.

## Corpus-completion proof packet
The full-channel scrape is complete only when the packet contains:

- main-channel and backup-channel manifests;
- playlist coverage report;
- transcript success/failure ledger;
- duplicate and mirror map;
- lessons with source timestamps;
- criterion-to-lesson provenance matrix;
- contradiction register;
- held-out design benchmark;
- evaluator agreement report;
- signed skillset version and replay tests.

## Current evidence status
This v0.1 is a **seed harness**, grounded in the selected saved video and an initial public-channel survey. It is not a claim that every Satori Graphics upload has already been transcribed and normalized. Promotion to v1.0 requires the corpus-completion proof packet above.



## Sources
- [website](https://www.youtube.com/@SatoriGraphics)
