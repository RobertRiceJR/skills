---
name: session-review
description: >
    End-of-phase reflection discipline — fires at the natural seams of a working session (a
    meaningful piece settling), not after every edit. Auto-activate when a task/feature/phase/
    debugging session is just declared complete, a verification step just passed (tests green,
    build succeeds), or the user is poised to transition (about to commit and push, switch tasks,
    end the session, or scale something just approved). Explicit cues: "before we move on", "wrap
    this up", "anything else?", "is this done?", "are we good?", "are we done here?", "what's
    left?", "should I push?", "lock this in and move on", "call it for today", "that's settled /
    done with this work", or naming the NEXT task to move to (the pivot is the seam). Do NOT
    activate after single-file edits or minor fixes, mid-problem-solving where reflection breaks
    flow, on doc-only/cosmetic edits, or when the user signaled they want to keep moving fast.
    Manual invocation: /session-review
user_invocable: true
argument: '(optional) a topic or scope to focus the review on; omit to review the full session surface'
---

# Session-Review

## Purpose

Encode the discipline: **look before you ship**. At the seams of a working session — a batch of
edits finished, a fix round closed, a refactor or docs pass settling — but *before* declaring it
done, ask the questions that couldn't be asked while the work was in progress.

This skill is reflection, not inspection. It does not look only at the lines that changed. It
looks at the surface the session touched, its neighbors in this repo, the goal the session was
working toward, and the trail of decisions made along the way.

The workflow is fixed, and the order is the whole point:
**report first → approval gate → fixes → verify → record.**
The report always comes before any fix. **Nothing is changed on disk until the user explicitly
approves** — "fix it all", "fix items 2 and 4", or similar. Skipping that gate is the one
failure mode that defeats the skill.

**Portability:** GLOBAL skill — it adapts to **whatever project the session is in**. Its
sibling-pattern catalog, verification commands, and durable-record targets are resolved from the
current project (see Phase 1's "Wired references"); where a project has no equivalent, that step is
skipped, not faked. The examples below (Playwright/TypeScript, a `bug-patterns.md` catalog,
`npm run type-check`) come from one such project and are **illustrative** — substitute the current
project's equivalents.

---

## When This Skill Activates

**Auto-activate at these session seams:**

- A task, feature, phase, or debugging session was just declared complete
- A verification step just passed (Playwright suite green, `type-check` clean, manual confirmation logged)
- The user says: "before we move on", "wrap this up", "anything else?", "is this done?",
  "are we good?", "are we done here?", "what's left?", "should I push?", "let's lock this in and
  move on", "call it for today", "that's settled / done with this work", or similar
  session-closing language
- A long working session (migration batch, fix-loop, skills/docs pass) is reaching a natural stop
- The user is about to commit and push, switch tickets, or end the session — including when they
  name the next ticket/task to move on to (that pivot is itself the seam)
- The user just approved something significant and is poised to scale or extend it

**Skip (do not activate) for:**

- Single-file edits, minor fixes, or individual tool calls
- Active problem-solving where reflection would break flow
- Documentation-only or cosmetic edits
- When the user has signaled they want to keep moving fast

**Boundaries vs. neighbors.** This is the *reflection* skill. For raw token/cost stats of past
sessions use `/codeburn`; recovering an interrupted orchestrator or running an
autonomous failure-fix loop are separate skills where a project provides them. Session-review does
**not** re-run suites, fetch external trackers, or fix failing tests — it surfaces what a finished
session may have left unsettled.

---

## Phase 1 — Report: the five questions

Walk these in order. The report has one section per question. Keep each section tight — one to
four bullets for findings, one sentence for "none." This phase produces a **report only**; no
file is touched until the Phase 2 gate clears.

**Wired references — consult whichever of these the current project has (skip the absent ones):**

- **A recurring-defect / pattern catalog** (e.g. `.claude/skills/_shared/knowledge/reference/bug-patterns.md`
  in a project that has one) — **the single source of truth for sibling patterns** when present: read it
  for Question 2 and recommend additions to it in Question 4; don't restate or re-invent its entries.
- **A repo-root `TODO.md`** — the canonical open-decisions / pending-follow-ups list. Question 3
  cross-checks against it — a deferral may already be tracked there (manage via `/todo` if available).
- **Append-only history** (changelog / skill-ledger, if the project keeps one) — use it to recognize
  repetition ("we keep making the same mistake") for Question 4.
- **The project's conventions docs** (CLAUDE.md, a skill-architecture/routing doc) — Question 2 should
  ask whether a change just made a convention there stale.

---

### Question 1 — Is the stated goal actually complete?

What did the session set out to do? Was that goal met, or redefined along the way? Are any
sub-goals incomplete or deferred?

If the goal is unclear — the session drifted, or the original ask was never stated — say so
rather than fabricating one. "Goal was not clearly stated" is a valid finding.

If the goal was "fix failing test X" or "implement Y," ask: is it done end-to-end, or only
locally? Something that passes under a narrow filter but hasn't run in its real environment (full
auth, fixtures/config, the right target) is not yet confirmed. A stub that was *characterized* is
not the same as one that was *implemented*.

---

### Question 2 — Are there siblings that share the same risk?

The most valuable finding in a session review is usually a sibling issue. Walk outward from the
session's surface — callers, peers in the same directory, the POMs / specs / queries that share
the same shape — and look for the same *class* of problem, not just for new problems.

**If the project has a recurring-defect catalog, read it and sweep for siblings of whatever the
session touched.** The table below is an *example* family map (from a Playwright/TypeScript project)
showing the shape of this thinking — build the equivalent from the current project's own catalog and
domain:

| Family (example) | What to sweep for | catalog ref |
| --- | --- | --- |
| **Locator / selector drift** | MUI hidden radio/checkbox clicks, MUI Select option-click not registering in React state, RFF→RHF select breakage, testid-vs-role choices, stale-local-source vs. deployed DOM, MUI modal `aria-hidden` isolation | #3, #10, #15, #16, #17, #21, #22 |
| **Waiter / race** | operation-name ≠ field-name regex, SPA initial-load race, deselect-toggle with no waiter | #1, #18 |
| **SQL & env-routing test-data fragility** | `ORDER BY NEWID()` timeout, `o.CreateDate` vs. `p.CreateDate`, data-consuming mutations needing a skip guard, browser-scope rep scoping, env-hardcoded SQL/endpoint host, hardcoded actor-ID + unconstrained data-pick no-op | #5, #6, #7, #8, #23, #24 |
| **Test-suite hygiene** | untagged shells in a secondary `describe`, FE-duplicate API filter tests, dead-POM-property / 0%-coverage false signals | #4, #12, #13, #14 |
| **Skill / doc drift & verification** | `--grep` regex escaping, duplicated facts that should be single-sourced, grep-only verification of a behavior-changing edit | #2, #19, #20 |

If the project has an autonomous fix loop that runs this same sweep inline at round end (and logs
it to a run-log), **read that entry and extend it** rather than redoing a sweep it already recorded.

These families are a starting point, not a ceiling. If the session surfaced a class that doesn't
fit any of them, carry it to Question 4.

---

### Question 3 — What was deferred, and should it stay deferred?

Sessions accumulate deferrals: "fix this later," "blocked on a PR that isn't deployed to INT
yet," "needs a separate design pass." List every deferral that came up.

For each: is the reason still valid? Did the session itself make it tractable? Some deferrals
graduate to "fix now" once their original blocker is removed by the very work just completed.
Cross-check against repo-root `TODO.md` — an item may already be tracked there, in which
case the finding is "still tracked, no action" rather than "newly surfaced."

If no deferrals were explicitly named, say so — but consider whether the session's final state
left anything in a provisional condition (a `test.fixme` with a fresh blocker note, a POM method
stubbed pending a locator, an SQL helper that's INT-hardcoded).

---

### Question 4 — Did the session reveal a durable pattern?

Working sessions surface patterns that weren't visible going in. A bug that looks novel the first
time is often the third instance of a deeper class.

If the session found and fixed the same class of issue more than once, name it and recommend
where it belongs:

- **The project's recurring-defect / pattern catalog** (if it has one) — the home for an
  implementation/debugging pattern. Usually the right target when present.
- **repo-root `TODO.md`** (via `/todo add`) — if it's a candidate not yet ready to formalize
  (the parking lot for future pattern-catalog entries).
- **The project's domain-knowledge / gotchas doc** — if it's domain *behavior* rather than an
  implementation pattern.

"No new pattern candidates" is a meaningful result, not a gap — say it explicitly.

---

### Question 5 — Were the session's success conditions strong enough?

What did "done" mean here? `type-check` clean? A green Playwright run? A verification table
matching? A rolled-back SQL probe? Ask whether that evidence was sufficient or the session moved
on too quickly. This is the hardest question and the most valuable — it catches premature
declarations of victory.

Consider:

- Were the passing tests actually exercising the changed behavior, or incidentally green?
- Was verification scoped to the happy path, or did it include the edge case the bug lived in?
- Was anything declared working on local evidence (a single `-g` run, a QA-sampled ID) that has
  not been confirmed in the real target (a full project run, INT data)?
- **Has the changed thing been exercised since the change, and what did its first run reveal?**
  A test's first real run, a function's first caller, a skill's first invocation, a doc's first
  reader — these first outputs surface gaps the edit-time check missed. If a first run happened,
  report what it told us. If not, say the smoke test is still pending. (Grep-only confirmation of a
  behavior-changing edit is **not** a smoke test.)

---

### The verdict

After the five sections, state one of three verdicts. The verdict is a recommendation, not a
command — the user decides whether to act on it.

**Complete and clean** — the goal was met, no siblings found, no deferrals worth revisiting, no
new patterns, success conditions were strong. Safe to move on.

**Complete with notes** — the goal was met, but the review surfaced sibling issues, worthwhile
deferrals, or pattern candidates. Worth a follow-up pass before the work is fully settled.

**Incomplete** — the stated goal was not actually met, or the success conditions were too weak to
trust the result. Recommend not moving on until specific gaps are closed. Name the gaps.

**Confidence line.** After the verdict, add one line stating confidence in the verdict itself:
`Confidence: high | medium | low — [one-sentence reason].` High means goal evidence is strong, no
major unknowns, the sibling sweep was exhaustive enough. Medium means most evidence is there but
one or two things were inferred rather than verified. Low means there's enough unknown that the
verdict could flip. Be honest — "medium because the smoke test was inherently partial" is more
useful than a reflexive "high."

---

### Output format

```
## Session Review

### 1. Goal Completeness
[findings]

### 2. Siblings
[findings — for each sibling, cite the bug-patterns #N it matches, e.g. "opportunities.grid.page.ts pins the same stale `*-grid-data` testid → #21"]

### 3. Deferrals
[findings]

### 4. Pattern Candidates
[findings]

### 5. Success Conditions
[findings]

---
**Verdict:** [Complete and clean | Complete with notes | Incomplete]
[One sentence explaining the verdict.]
**Confidence:** [high | medium | low] — [one-sentence reason]
```

Keep each section to 1–5 bullets. Prose is fine for complex findings. No section should run
longer than a short paragraph — if it does, the session needs a deeper debrief, not a longer
review report.

---

## Phase 2 — Approval gate

After presenting the report and verdict, **stop.** State the gate clearly:

> "Review the findings above. Say 'fix it all' or name specific items to apply fixes."

**Do not touch any file until the user responds to the gate.** This is the discipline the skill
exists to enforce — the report always comes first, the gate always second. (This gate is what
separates `/session-review` from `/fix-loop`, which *is* authorized to edit autonomously within
its loop.)

---

## Phase 3 — Apply approved fixes

Apply only what the user approved. For each fix:

1. Edit the specific file and line(s) named in the finding.
2. State what changed in one sentence — don't re-explain the pattern.
3. If a fix forces follow-on changes (a signature change forcing caller updates, a POM rename
   rippling into specs), apply those too and note them.

Run the project's fast static check after any code edit (e.g. a type-check / compile step, where the
project mandates one). After all approved fixes are applied, move immediately to Phase 4.

---

## Phase 4 — Verify

Run in this order, using **the current project's** commands (the ones below are illustrative).
Stop and report if any step fails.

1. **Static check** — the project's type-check / compile step (e.g. `npm run type-check` →
   `tsc --noEmit`), where one exists.
2. **Lint** — the project's linter (e.g. `npm run lint`), where one exists.
3. **Exercise touched code** — if a fix touched a test or its support code, run it in its real
   environment so auth / fixtures / config load (not just a narrow filtered run). Escape regex
   metacharacters when running by title, and use the project's default config.
4. **Exercise touched skills / docs** — static checks say nothing about a skill or doc edit. The
   smoke test for a behavior-changing skill/doc edit is to **trace one representative invocation
   end-to-end** — and for a skill, actually run it once — before declaring done. A grep that
   confirms the new wording landed is not a smoke test. This is the meta-gap that most often bites
   skill-editing sessions; Question 5 is where it surfaces.

Report results as:

```
## Verification
- Static check: PASS / FAIL / N/A
- Lint: PASS / FAIL / N/A
- Code run: PASS / FAIL / N/A
- Skill/doc smoke test: PASS / FAIL / N/A
```

If all pass, the session is settled. If any fail, report the failure and wait for direction. Do
not start a second fix loop without explicit instruction.

---

## Phase 5 — Record

If the current project keeps a run history (a skill ledger / changelog), append one row to it,
matching its existing columns. For a project using the `_shared/skill-ledger.md` convention
(`Date · Skill · Ticket · By · Quality · Produced · Notes · Enhancement`):

```
| {YYYY-MM-DD} | `/session-review` | {ticket or local} | {user} | {✅/⚠️/❌} | {verdict + n findings, n approved fixes} | {most significant finding} | {enhancement idea or —} |
```

Quality key: ✅ clean review, fixes verified · ⚠️ findings needed correction or a verify step
partially failed · ❌ review aborted or the approval gate was skipped.

If the project has no such ledger, skip this phase (the report in-session is the record).

---

## Worked example

A real-shape review of a `/fix-loop` round that fixed two `contracts.grid` tests by replacing a
stale `data-testid` with `getByRole('grid')` (bug-patterns #21). Report first, then the records:

```
## Session Review

### 1. Goal Completeness
- Clear the 2 failing contracts.grid tests. Met — both pass in isolation after the locator swap.

### 2. Siblings
- The swap matches #21 (role over testid). Swept `src/pages/` for `getByTestId(` on grid/dialog
  elements → `opportunities.grid.page.ts` pins the same `*-grid-data` testid and is still failing
  → almost certainly the same fix. (#21)
- No waiter/race siblings (#1/#18) — the change didn't touch response timing.

### 3. Deferrals
- The opportunities.grid sibling, named above, was not attempted this round. Reason still valid
  (out of this round's scope); not yet in wiki/state.md.

### 4. Pattern Candidates
- None new — #21 already covers it.

### 5. Success Conditions
- Both targets pass under `-g` in isolation, but the full `contract` project run has NOT happened
  since the POM change, so blast radius on the other contracts.grid tests is unverified. Smoke
  test pending.

---
**Verdict:** Complete with notes
The two target tests are green, but a named sibling and a full-project run remain.
**Confidence:** medium — the fix is sound, but verification was single-test, not project-wide.
```

**Phase 5 record for that review** — the ledger row:

```
| 2026-05-29 | `/session-review` | local | Robert | ⚠️ | Complete-with-notes; 2 findings, 0 fixes (report only) | opportunities.grid has the same stale-testid sibling (#21); full contract-project run still pending | — |
```

---

## What this skill does not do

- It does not fix without approval. Report first, gate second. Skipping the gate is the one
  failure mode that defeats the skill.
- It does not assume the goal. The goal is inferred from context; if ambiguous, that ambiguity is
  surfaced in Question 1.
- It does not expand scope beyond the session's natural surface. If a sibling sweep uncovers
  something far outside scope, flag it in one line and don't chase it.
- It does not demand perfectionism. Some deferrals are correct; some success conditions are
  intentionally light. The skill surfaces decisions for review — the user decides what to do.
- It does not re-run suites, query MCP servers, or implement failing tests. Those belong to
  `/fix-loop`, `/ready-for-playwright`, and the reporters.
