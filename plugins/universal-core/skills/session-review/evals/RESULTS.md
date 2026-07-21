# session-review — activation eval (measured)

**Measured 2026-05-29** with the (now cross-platform) skill-creator harness `run_eval.py`, against
the deployed `session-review` description. Replaces the earlier *manual estimate* with data.

> **Fixture drift note (2026-07-03):** one on-script positive was reworded after measurement
> ("i just finished the ruby migration batch…" → "…the shell implementation batch…", Ruby-purge pass —
> semantically equivalent wrap-up trigger). Its 3/3 PASS below reflects the OLD wording; re-measure on
> the next full eval run (the harness has no single-case flag — whole-set only).

- **Reproduce:** from the repo root —
  `PYTHONPATH=<skill-creator> python -m scripts.run_eval --skill-path .claude/skills/session-review --eval-set .claude/skills/session-review/evals/trigger-eval.json --runs-per-query 3 --num-workers 6 --timeout 75 --verbose`
- **Mechanism:** synthetic-or-deployed skill + `claude -p` (MCP disabled via `--mcp-config <empty> --strict-mcp-config`), 3 runs/case; a case passes when its trigger-rate is ≥0.5 (positives) / <0.5 (negatives).

## Headline

| Metric | Result |
| --- | --- |
| Overall | **22 / 27 (81.5%)** |
| Negatives (should NOT trigger) | **12 / 12 (100%)** — zero false positives, never nags |
| Positives (should trigger) | 10 / 15 (67%) |
| Failure mode | all 5 failures are **under**-triggers (0 over-triggers) |

## Per-case (rate = triggers / 3 runs)

**On-script positives**
| rate | result | query |
| --- | --- | --- |
| 3/3 | PASS | before we move on to the next ticket, anything we missed… |
| 3/3 | PASS | ok i think the contracts.grid fix is done… are we good? |
| 3/3 | PASS | is this done? the type-check passed and i'm about to commit… |
| 3/3 | PASS | let's wrap this up — i just finished the shell implementation batch… |
| 3/3 | PASS | tests just went green across the board… what now |
| **1/3** | **FAIL** | i'm about to commit and push the summary panel locator changes, good to go? |
| 3/3 | PASS | ok the vault frontmatter cleanup pass is settled… stopping point |
| 2/3 | PASS | that's the whole fix-loop round finished… ready to close it out? |

**On-script negatives** — all **0/3 PASS** (fix import / keep digging mergeParties / bump copyright year / keep moving fast / rename var / walk me through the DOM / add a comment / what does the CI filter restrict).

**Off-script paraphrased positives**
| rate | result | query |
| --- | --- | --- |
| 3/3 | PASS | ok I think that is everything for the seasonal-contract work |
| **0/3** | **FAIL** | lets lock this in and move on to CI-7728 |
| 3/3 | PASS | cool, green run. think we can call it for today? |
| 3/3 | PASS | that POM refactor is settled and both grids pass now |

**Off-script paraphrased negatives** — all **0/3 PASS** (tweak one import / quick typo fix / still chasing why this waiter / blast through the rest).

**Off-script ambiguous** (labelled should-trigger; genuinely 50/50)
| rate | result | query |
| --- | --- | --- |
| **0/3** | **FAIL** | should I push? |
| **0/3** | **FAIL** | what is left? |
| **1/3** | **FAIL** | are we done here or is there more to do? |

## Measured vs. the prior manual estimate

Manual estimate said: "plausibly under-triggers on ~3–5 terse/ambiguous positives (e.g. *should I push?*, *what is left?*, statement-form *that POM refactor is settled…*); zero false positives."

- **Magnitude + direction: correct.** 5 under-triggers, 0 false positives — the conservative-bias prediction held.
- **Per-case: ~60% accurate.** Correctly called *should I push?*, *what is left?*, *are we done here…* (all FAIL). **Wrongly** flagged *that POM refactor is settled…* and *cool, green run…* as at-risk — both actually PASS 3/3. **Missed** two real failures: *lets lock this in and move on* (0/3) and the on-script *about to commit and push… good to go?* (1/3, flaky despite "about to commit and push" being a verbatim cue).
- This per-case gap is exactly why measured beats estimate (Pattern #20).

## Verdict — description left UNCHANGED

Not below bar; the under-triggering reflects the skill's intended **"don't nag"** bias.
- 100% precision on negatives — the skill never interrupts active work, which is the design goal.
- 3 of 5 misses are deliberately-ambiguous terse questions where firing a full reflection *would* be nagging — defensibly-correct non-triggers.
- The 2 arguable gaps (*about to commit and push… good to go?* at 1/3; *lock this in and move on* at 0/3) are real but minor. Making the description more aggressive to catch paraphrases risks the perfect negative record, and `/session-review` is manually invocable as a cheap fallback. The trigger contract (don't interrupt) is worth more than catching every paraphrase.

If a future pass wants to lift positive recall, the highest-value, lowest-risk target is the flaky near-verbatim **"about to commit and push"** case (1/3) — re-measure after any wording change to confirm negatives stay at 0.
