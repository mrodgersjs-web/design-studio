# Workflow: corpus

v0.1 stays a seed until the packet in `references/release-rule.md` is complete. This workflow extends the corpus. It does not promote the skillset.

<required_reading>
1. `../references/release-rule.md`
</required_reading>

<process>
## Step 0: Permission
A public YouTube listing does not authorize scraping or republishing transcripts. Acquire transcripts only via a platform-permitted API or a user-supplied file. Record license/permission, retrieval method, and date on every item. Publish only derived lesson records and short timestamped quotations where that permission allows. Keep raw transcripts out of this repo unless redistribution rights are verified.

## Step 1: Ingest
Build a manifest of every public video from the main and backup Satori Graphics channels. Store URL, video identifier, title, publication date, duration, playlist, transcript status, permission/retrieval method, and content hash. Deduplicate mirrored uploads by normalized title, transcript similarity, and perceptual thumbnail hash. Write the manifest as files; do not claim ingest is complete until both channel manifests exist.

## Step 2: Extract
Use only permitted transcripts. Chunk by lesson, not arbitrary token length. For every candidate lesson record:

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

Skip sponsor copy, jokes, and tool promotion. No claim without transcript evidence (URL + timestamp).

## Step 3: Anti-unify
Cluster repeated lessons into stable procedures: hierarchy, contrast, balance, movement, proximity, unity, typography, color, audience, briefs, workflow, critique. Keep disagreements and evolution over time. Do not flatten the channel into one voice.

## Step 4: Seed lock
Keep `version: 0.1.0` and seed status until every item in the corpus-completion packet exists as a real file. Missing packet item → still v0.1. Do not bump to v1.0 from a partial scrape.

## Step 5: Packet check
The packet is complete only when all of these exist:

- main-channel and backup-channel manifests
- playlist coverage report
- transcript success/failure ledger
- duplicate and mirror map
- lessons with source timestamps
- criterion-to-lesson provenance matrix
- contradiction register
- held-out design benchmark
- evaluator agreement report
- signed skillset version and replay tests

If any item is missing, report the gaps and stop at seed. Independent verifier owns v1.0 promotion.
</process>

<success_criteria>
- [ ] Each transcript has recorded permission and retrieval method
- [ ] Raw transcripts are not in this repo unless redistribution rights are verified
- [ ] Manifest files exist for the channels actually fetched
- [ ] Every extracted claim has URL + timestamp
- [ ] Version remains 0.1.0 unless the full packet is present
- [ ] Generator did not self-promote to v1.0
</success_criteria>
