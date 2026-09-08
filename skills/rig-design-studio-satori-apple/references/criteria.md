# 60 design criteria

Score each criterion **0 = fail, 1 = weak, 2 = pass, 3 = exceptional**.
**GATE** criteria must score at least 2. A total score cannot compensate for a failed gate.

## A. Communication and product desire
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

## B. Brief, audience, and journey
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

## C. Hierarchy and attention
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

## D. Layout, balance, movement, and flow
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

## E. Typography
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

## F. Color, imagery, and emotional signal
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

## Coding-agent implementation gates
These are pass/fail, not 0–3. Fail any one and the scorecard cannot ship.

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
