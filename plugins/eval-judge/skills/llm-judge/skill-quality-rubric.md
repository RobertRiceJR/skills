# Skill-Quality Rubric

The prose companion to [`dimensions.json`](dimensions.json). `dimensions.json` is the criteria
SSOT (what each dimension asks); this file is the **score anchors** (what a 0.9 vs a 0.5 vs a 0.2
looks like) and the shared grader frame. Do not restate the criteria text here — link to it.

The judge scores a **Claude Code skill** — primarily its `SKILL.md`, plus supporting files when
they matter to the dimension — **one dimension at a time**, on the evidence in the skill only.

## The shared grader frame (single source of truth)

Every dimension is graded by the same persona, defined once in
[`promptfooconfig.yaml`](promptfooconfig.yaml) `rubricPrompt` and mirrored by the interactive judge
in [`SKILL.md`](SKILL.md):

> You are a senior skill-design reviewer. You score ONE quality dimension of a skill at a time, on
> the evidence in the skill only. Be skeptical — judge what the skill actually says, never reward
> intent or good vibes — but score **proportionally** across the full 0.0–1.0 range, not bimodally.
> Output only `{"reason": <one sentence>, "score": <0.0–1.0>, "pass": <boolean>}`. Do **not** suggest
> fixes — scoring only.

## Full-scale anchoring (applies to every dimension)

- **0.9–1.0** — fully satisfies the dimension; no concerns.
- **0.6–0.8** — largely sound, one minor or single flaw.
- **0.4–0.6** — genuinely mixed: real strengths *and* real violations.
- **0.2–0.4** — mostly violates, a little compliance.
- **0.0–0.2** — reserve for essentially no compliance (the dimension is absent).

A single flaw in an otherwise-sound skill is a deduction, not a zero.

## Per-dimension anchors

### D1 — Trigger accuracy *(apex · weight 3 · VOTED ×3 · pass ≥ 0.8)*
When a live eval set exists, the score **is** the `run_eval.py` pass rate — the rubric only frames
the static fallback.
- **1.0** — description enumerates concrete trigger phrases AND an explicit boundary/"do NOT use for
  X → that's `/sibling`" clause; unambiguous lane.
- **0.6** — fires for its own job but the boundary against siblings is soft, or trigger phrasings are
  thin.
- **0.2** — generic enough to fire on unrelated requests, or so long the trigger list is truncated by
  the ~1024-char cap.

### D2 — Description clarity & anti-shadowing *(weight 2 · pass ≥ 0.75)*
- **1.0** — one read tells you what it does, what it produces, and where its lane ends; no overlap
  with a sibling's trigger space.
- **0.5** — readable but either overlaps a sibling (shadowing risk) or over/undersells the body.
- **0.2** — vague verbs ("helps with", "handles"), no scope, would steal sibling activations.

### D3 — Body coherence & altitude *(weight 2 · pass ≥ 0.75)*
- **1.0** — phases match the description's promises; gates it claims are actually enforced; concrete
  output contract; right altitude (judgment where judgment is needed, specificity where it is).
- **0.5** — mostly coherent but a promised gate is missing, or an unstructured section, or hardcoded
  example data presented as law.
- **0.2** — contradictory/out-of-order phases, wall of prose, or altitude badly wrong throughout.

### D4 — Portability *(weight 2 · pass ≥ 0.8)*
- **1.0** — every project-specific dependency carries an explicit "if present, use it; else
  skip/degrade"; paths are relative/self-resolved; no repo-layout assumption.
- **0.6** — mostly portable but one hardcoded path or one unguarded external command remains.
- **0.2** — hardcoded absolute paths, mandatory reads of maybe-absent files, or `npm run X` as a
  required step with no fallback.

### D5 — Reference integrity *(weight 2 · pass ≥ 0.8)*
- **1.0** — every depended-on `/sibling` exists here or is marked optional; every cited path
  resolves; no `../../../` escape out of the repo.
- **0.6** — one soft/dead reference, but nothing the skill hard-requires.
- **0.2** — a required handoff to a `/sibling` that doesn't exist here, or a dead path treated as
  present. *(Historical-provenance notes clearly labeled as such are exempt — do not penalize them.)*

### D6 — Self-containment *(weight 1 · pass ≥ 0.75)*
- **1.0** — runs from its own folder + the target project; bundles or degrades without everything it
  needs.
- **0.5** — one supporting script/asset referenced but not shipped, with a plausible fallback.
- **0.2** — depends on tooling that lives only in an uninstalled plugin or an old repo.

## Per-skill confidence

The scorecard collapses the per-dimension scores into a weighted mean (weights in
`dimensions.json`), D1 as the voted ×3 apex. A skill is **flagged for triage** when its D1 (trigger)
score OR its overall confidence falls below the `flag` floors in `dimensions.json`. The flag says
"look here first" — the honest per-dimension scores are the verdict.

## Calibration is not optional

Deep research on LLMs-as-judges over code found 52–78% accuracy on benchmarks — a cautionary prior.
The [`golden/labels.jsonl`](golden/labels.jsonl) set is how we learn whether *this* rubric separates
strong from weak skills on *these* skills. Hand-label a spread (exemplary portability vs. hardcoded
old-project coupling; tight trigger vs. shadowing description) and require the judge to reproduce the
ordering before its scores gate anything.
