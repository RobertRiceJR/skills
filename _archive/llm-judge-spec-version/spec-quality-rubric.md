# Spec-Quality Rubric — IMA 360 LLM Judge

> **Criteria SSOT:** [`dimensions.json`](dimensions.json). This file is the *prose* companion —
> score anchors, gotcha grounding, and the shared grader frame. The exact criteria strings the judge
> grades against live in `dimensions.json` and are referenced, not duplicated here (bug-patterns #19).

## What this is

A semantic LLM judge that grades the **quality** of an existing Playwright spec — *not* whether it
passes, and *not* how to fix it. Green ≠ trustworthy: a passing test can assert nothing meaningful,
wait on the wrong signal, or verify a side-effect instead of its stated intent. The judge scores six
dimensions 0.0–1.0 so we can build confidence in a suite of mixed provenance (Claude-imported, junior,
rushed migration).

It is the **semantic half** of a two-part check. The objective half — waiter *present* and ordered,
raw locators, hardcoded IDs, alias traps, `waitForTimeout`, missing `@CI-T`, placement — is already
caught deterministically by `/spec-review`'s seven static checks, `eslint-plugin-playwright`, and
`/roast-me`. **The judge only grades what grep/lint cannot:** does the waiter target the *right*
operation? does the assertion match the *stated intent*? is the locator *robust*? Don't make the LLM
re-judge what static analysis already settles.

## Two hard design rules (from deep research, task wguwyzi1j)

1. **Score, don't fix.** LLMs judging code-vs-spec are only 52–78% accurate, and adding an
   "explain + suggest a fix" step *collapsed* accuracy (one benchmark: 52.4% → 11.0%) via an
   over-correction bias that fabricates defects in correct code. Every grader call returns **a score
   and a one-line reason only — no fixes, rewrites, or suggestions.** This is enforced in the shared
   grader frame below. Remediation is a separate step owned by `/fix-me` /
   `/playwright-workflow` / a human.
2. **Calibrate before trusting.** Those numbers are from algorithmic benchmarks, not passing E2E
   specs — a cautionary prior, not our ceiling. A human-labeled golden set
   ([`golden/labels.jsonl`](golden/labels.jsonl)) gates whether sweep scores are treated as
   trustworthy. Until calibration separates known-good from known-weak per dimension, scores are
   **provisional**.

## The six dimensions

Each is one `llm-rubric` assertion. Exact criteria → `dimensions.json`. Score anchors and the
gotcha rules each enforces:

| # | Dimension | Score anchors | Grounded in |
| --- | --- | --- | --- |
| **D1** | **Intent fidelity** *(apex · weight 3 · VOTED ×3 · ≥0.8)* | **1.0** an assertion proves the title's claimed outcome (test fails if feature breaks) · **0.5** asserts something real but adjacent to the title · **0.0** vacuous green — only container visibility, a tautology, or a flow with no outcome assertion | the "vacuous green" failure mode; the Test-Fidelity judge in [llm-judge-and-eval-strategy.html](../../../analysis/llm-judge-and-eval-strategy.html) |
| **D2** | **Assertion adequacy** *(weight 2 · ≥0.7)* | **1.0** web-first assertions on the meaningful state change; API specs assert the right error surface · **0.5** asserts an outcome but weakly (one shallow check) · **0.0** assertion-free, only-visibility, or wrong error surface | patterns-quickref §6 (two GraphQL error surfaces); bug-patterns #8 (browser-scope verify); CLAUDE.md fixture rules |
| **D3** | **Wait/sync soundness** *(weight 2 · ≥0.8)* | **1.0** waiter targets the correct operation, promise-before-action holds everywhere, toPass for eventual consistency · **0.5** waiter present but coarse / one ordering gap · **0.0** wrong-operation regex, promise-after-action, or hard waits | bug-patterns #1 (operation ≠ field name), #18 (SPA load + toggle race); waiter pattern in CLAUDE.md & e2e-spec template |
| **D4** | **Locator & interaction resilience** *(weight 1 · ≥0.7)* | **1.0** stable handles in house order + correct MUI/RHF idioms · **0.5** mostly stable with one brittle handle · **0.0** brittle CSS/xpath, guessed testId, or wrong MUI/RHF interaction | bug-patterns #3, #9, #10, #15, #17, #21, #22; patterns-quickref §1 |
| **D5** | **Test-data discipline** *(weight 2 · ≥0.8)* | **1.0** NEWID sampling, CI filter, terminal-status excluded, skip-guard/fresh-data where needed, detail-query verification · **0.5** sampled but one rule missed · **0.0** hardcoded IDs, destructive op on shared data, or browser-scope post-mutation verify | bug-patterns #6, #7, #8, #24, #25; CLAUDE.md CI filter & terminal-state conventions; patterns-quickref §9 |
| **D6** | **Isolation & POM boundary** *(weight 1 · ≥0.7)* | **1.0** order-independent, business asserts in spec, mechanics in POM · **0.5** minor boundary leak · **0.0** order-dependent, asserts in POM, raw locators in spec, or `.only` | bug-patterns #12; patterns-quickref §7; pom/e2e templates |

> **House locator order note:** Playwright's *official* order is role-first; IMA's house order
> (patterns-quickref §1) is **testId-first** because the team intentionally ships `data-testid`. D4
> grades against the **house order** — the judge must not penalize correct house style. (Where a
> stable role exists, bug-patterns #21 prefers it over a churn-prone testid — D4 reflects both.)

> **Applicability:** D3 (wait/sync) and D4 (locator/interaction) are **E2E-only** (`appliesTo` in
> `dimensions.json`) — API specs have no browser waiters or locators. API specs are graded only on
> D1/D2/D5/D6, and confidence is the weighted mean over the *applicable* dimensions, so E2E-only
> dims are never graded for API specs and never deflate their score.

**Per-spec confidence** = weighted mean of the applicable scores (D1's three votes collapsed to their mean
first). **Flagged for triage** if intent fidelity (D1) < 0.5 OR overall confidence < 0.5 — a triage
*filter* calibrated to the judge's measured distribution (~0.15 below human; see `dimensions.json`
`_flag_note`), **not** the quality verdict. It surfaces the weak tail, not every spec. Flagged specs
are a review queue — the judge **never edits a spec**.

## The shared grader frame (rubricPrompt)

One frame serves all six dimensions; `{{rubric}}` swaps in the dimension criteria, `{{output}}` is the
composed artifact (spec body + its referenced POM bodies). This is the SSOT for the frame — it is
copied verbatim into [`promptfooconfig.yaml`](promptfooconfig.yaml) `defaultTest.options.rubricPrompt`
and mirrored by `/spec-review` Phase 3b. The score-only / no-fix / default-low rule lives here so it
applies to every dimension:

```json
[
  {
    "role": "system",
    "content": "You are a senior Playwright test-quality reviewer for the IMA 360 suite. You score ONE quality dimension of a test spec at a time, on the evidence in the artifact only. Be skeptical and judge only what the test actually does (never reward intent or comments) - but score PROPORTIONALLY across the full 0.0-1.0 range, not bimodally. OUTPUT ONLY a JSON object {\"reason\": <one sentence>, \"score\": <number 0.0-1.0>, \"pass\": <boolean>}. Do NOT suggest fixes, rewrites, or improvements. Scoring only."
  },
  {
    "role": "user",
    "content": "ARTIFACT (spec under review + its referenced page objects):\n\n{{output}}\n\nSCORE THIS DIMENSION ONLY:\n{{rubric}}\n\nUse the FULL scale, proportional to how much of the dimension is satisfied:\n- 0.9-1.0 = fully satisfies, no concerns.\n- 0.6-0.8 = largely sound, with a minor or single flaw.\n- 0.4-0.6 = genuinely mixed: real strengths AND real violations.\n- 0.2-0.4 = mostly violates, with a little compliance.\n- 0.0-0.2 = reserve for NO meaningful compliance (the dimension is essentially absent).\nA single flaw in an otherwise-sound test is a deduction, not a zero - weigh it against what the test does right. Score near 0 only when there is no evidence of the dimension at all. Return only the JSON object."
  }
]
```

## Where it runs

- **Whole-suite sweep** — `npm run judge:sweep` → [`scripts/llm-judge/run-sweep.ts`](../../../../scripts/llm-judge/run-sweep.ts) → `npx promptfoo eval` on Haiku → [`scripts/llm-judge/scorecard.ts`](../../../../scripts/llm-judge/scorecard.ts) renders the executive HTML.
- **Single-spec deep review** — `/spec-review <spec>` Phase 3b dispatches the same six dimensions as independent Agent calls and appends a `## Semantic Judge` section to its report.
- **Calibration / judge-of-the-judge** — `npm run judge:calibrate` scores the golden set on Opus and reports per-dimension agreement.

See [`README.md`](README.md) for run details and integration caveats.
