---
name: devils-advocate
description: >
    Adversarial review of a populated ticket.md. Generates 8–12
    pointed challenges to the test plan using lenses the orchestrator does not use
    (malicious user, panicking dev, skeptical senior QE, single-point-of-failure
    auditor). Forces the user to rebut or revise each challenge. Appends a
    rebuttal/acceptance log to the source doc. this is
    a review pass that runs AFTER those have produced a populated doc.
user_invocable: true
argument: '<path to a populated test-plan / ticket doc> — or a ticket ID (e.g., CI-7461) if the project uses the _shared/tickets convention'
---

# Devils Advocate — Adversarial Test Plan Review

> **Portability.** The review logic (lenses, challenge format, rebuttal gate) is project-agnostic.
> Only the **input doc** is convention-bound: this skill was built around IMA-360's
> `_shared/tickets/**/ticket.md` layout. When that layout isn't present, accept an **explicit path**
> to any populated test-plan / ticket / spec doc as the argument, and append the review log there.
> Never hard-stop because the `_shared/tickets/` glob found nothing — ask for the doc path instead.

Argues with the test plan. Every orchestrator and its user share a frame — this skill
uses different frames on purpose to surface what was missed.

**Read-and-append only.** Never deletes or rewrites existing doc content.
**User-driven.** Every challenge requires explicit disposition before anything is written.

---

## Phase 1 — Locate and Load the Doc

If the argument is an explicit file path, read that doc. Otherwise, if the project uses the
`_shared/tickets` convention, glob for the ticket's unified lifecycle doc:

```
Glob: .claude/skills/_shared/tickets/**/CI-{number}*/ticket.md
```

Read the entire doc into context.

If nothing is found:

> "No populated test-plan doc found. Point me at the doc directly (a path to your test plan /
> ticket / spec), or if this project has a plan-authoring skill (e.g. `/three-amigos`,
> `/ready-for-testing`), run that first and come back."
>
> Stop here.

---

## Phase 2 — Generate Challenges

Apply each lens to the doc. For each lens, generate 1–3 challenges grounded in
specific content from the doc — section names, TC numbers, AC numbers, named methods,
entity IDs. No generic filler; if a lens produces nothing real for this ticket, skip it.

Target 8–12 total challenges across all lenses. If you find more, prioritize the ones
with the highest risk if the user is wrong.

### Lenses

| Lens                       | Core question to ask                                                                                                                                                                  |
| -------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Malicious user**         | What does an attacker or bad actor try that the plan ignores? Boundary abuse, unexpected input types, race conditions, auth boundary crossing.                                        |
| **Panicking dev**          | If this ships broken at 4pm Friday, what gets shipped that the test plan doesn't cover? Focus on blast radius beyond stated scope.                                                    |
| **Skeptical senior QE**    | Where would someone with 10 years on this codebase say "that's not how this actually works"? Watch for over-trusting framework conventions, silent null handling, or inherited assumptions.     |
| **Burned dev**             | Where would a tired dev push back on this plan? Are any TCs testing the framework/codegen rather than the feature's actual behavior?                                                  |
| **SPOF auditor**           | If one entity gets deleted, one MCP is down, or one env data set is stale — which TCs fail simultaneously? Hidden single points of failure in test data or infrastructure.            |
| **Tension finder**         | Do any TCs contradict each other? Does one TC's success implicitly require another's failure? Are two TCs using the same precondition data in ways that could contaminate each other? |
| **Priority challenger**    | For each Normal TC: what's the worst-case business impact if this ships broken (should it really be High)? For each High/Critical TC: is the assertion strong enough for that tier — and is any TC marked Critical that isn't the component's registry smoke?    |
| **Unhappy-path scout**     | For each TC's action — what happens midway through? Are partial states tested? Is reset/undo/cancel after an action covered?                                                          |
| **Assumption auditor**     | Every "we assume X" / "out of scope: Y" / "INT-only" — has anyone actually verified it, or is it inherited belief?                                                                    |
| **Data freshness checker** | Are the sampled entity IDs or data preconditions still valid? Have any CI filter conditions or data shapes changed since the doc was written?                                         |

### Challenge format

```
**Challenge {n}: {one-line summary}**
Lens: {lens name}

{2–4 sentences — specific to this doc. Cite section, TC#, AC#, method name, or entity ID by name.}

**Risk if the user is wrong:** {concrete outcome — what production failure looks like if this gap ships}
**Suggested action:** {add TC / revise precondition / acknowledge as risk / verify assumption}
```

---

## Phase 3 — Force Rebuttal or Revision

Present challenges **one at a time** — do not dump all 12 at once.

For each challenge, use `AskUserQuestion` with these options:

```
Question: "{Challenge N one-liner} — how do you want to handle this?"
Options:
  A) Rebut — this doesn't apply (explain why)
  B) Accept — add a test case
  C) Accept as acknowledged risk — won't fix; goes in Acknowledged Risks log
  D) Defer — log it, no action now
```

- **Rebut:** Record the user's rebuttal verbatim. Move to next challenge.
- **Accept (add TC):** Draft the TC in the same format as the doc's TC table, present it to the user for confirmation, then proceed. Do NOT write to the doc yet — collect all new TCs until Phase 4.
- **Accept as acknowledged risk:** Record the risk statement. Move to next challenge.
- **Defer:** Log it. Move to next challenge.

After all challenges, present a summary:

> "{N} challenges processed: {X} rebutted, {Y} accepted (TC added), {Z} acknowledged risk, {W} deferred."
>
> "Proceed to write the review log to the doc?"

Do not write to the doc until the user confirms.

---

## Phase 4 — Write the Review Log

Use `Edit` to append to the source doc:

```markdown
---

## Adversarial Review Log — {YYYY-MM-DD}

**Reviewer:** /devils-advocate
**Challenges raised:** {N}
**Outcomes:** {X} rebutted · {Y} TCs added · {Z} acknowledged risks · {W} deferred

### Challenge Outcomes

| # | Summary | Lens | Outcome | Notes |
| - | ------- | ---- | ------- | ----- |
| 1 | {summary} | {lens} | Rebutted | {user rebuttal, 1 sentence} |
| 2 | {summary} | {lens} | TC added | {TC title added} |
| 3 | {summary} | {lens} | Risk acknowledged | — |
| 4 | {summary} | {lens} | Deferred | — |

### New TCs Added by This Review

(Only present if any TCs were accepted)

| TC# | Title | Priority | Type | AC | Precondition | Key Assertion |
| --- | ----- | -------- | ---- | -- | ------------ | ------------- |
| TC-{n} | {title} | {priority} | {type} | {AC} | {precondition} | {assertion} |

### Acknowledged Risks

(Risks accepted but not addressed — visible forever in the doc)

- **Risk {n}:** {risk statement from the challenge} — accepted {date}

---
```

Also append any new TCs to the Test Cases section of the source doc.

---

## Hard Constraints

- Maximum 12 challenges per run. If you identify more, pick the 12 highest-risk.
- Never auto-accept a challenge. Every disposition requires explicit user response.
- Never rewrite or delete existing doc content. Append only.
- Skip a lens entirely rather than generating a weak challenge to fill the count.
- Use `Edit`, not `Write`, on all existing files.

---

## MCP Tools Required

None. This skill reads local files and uses `AskUserQuestion` for interaction.
All content is derived from the populated doc — no external API calls.
