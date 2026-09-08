# Workflow: critique

<required_reading>
1. `../references/criteria.md`
2. `../references/release-rule.md`
</required_reading>

<process>
## Step 1: Independent critic
A separate pass from the generator. Score every applicable criterion 0–3. Name failed criteria with evidence (what is on screen, not taste). Do not silently redesign.

## Step 2: Grill
At least three generator/critic rounds. Generator returns explicit fixes plus before/after proof for each failed GATE.

## Step 3: Machine gate
```bash
python3 skills/rig-design-studio-satori-apple/scripts/scorecard.py path/to/scorecard.json
```
Exit 1 blocks ship.

## Step 4: Human-scale checks
Two-second read: product, value, next action. Non-designer test. Responsive screenshots. Accessibility report. Every visible element has a function.

## Step 5: Verdict
Only the independent verifier ships. Generator output is a proposal. If any release-rule bullet fails, verdict is NO-SHIP with the failed ids.
</process>

<success_criteria>
- [ ] Scorecard ran through `scripts/scorecard.py`
- [ ] GATE ids 1, 2, 3, 4, 11, 21, 31, 41, 51 are all ≥ 2
- [ ] ≥90% of applicable criteria are ≥ 2
- [ ] Verifier, not generator, issued the verdict
</success_criteria>
