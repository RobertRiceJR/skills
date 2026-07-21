---
name: claude-architect
description: >
    The centerpiece capability ledger for Claude-architecture work. Tracks this repo's
    standing against the 30 task statements of the Anthropic Claude Certified Architect –
    Foundations (CCA-F) spine — one self-updating reference file per statement, each holding
    the current verdict (BUILT/PARTIAL/GAP) + evidence (what we have) and a decomposed
    build-on checklist + work-log (what we need to do). Reports where we stand, picks the
    single highest-impact next gap, and hands off to the right skill/spike — it does NOT
    implement the work itself. After a bit of work lands, it records the change so context
    survives across sessions. Seeded from the CCA-F audit at
    .claude/analysis/cca-f-capability-audit.html.
    Trigger phrases: "claude architect", "capability ledger", "where do we stand on the cert",
    "cca-f status", "what's the next architecture gap", "architecture backlog",
    "update the architect ledger", "/claude-architect".
user_invocable: true
argument: "[ <statement code e.g. 1.2> | next | status | update <code> | reaudit <code> ]  (no arg = status)"
---

# Claude Architect — Capability Ledger

## Overview

This skill is the **living, self-updating ledger** of how far this repo has come toward
implementing what a Claude Certified Architect is expected to know. Its knowledge base is the
**30-statement CCA-F spine** (5 weighted domains), one reference file per statement. Each file
expands from a single index line into **what we have** (verdict + cited evidence) and **what we
need to do** (decomposed sub-tasks + a dated work-log), so gaps get closed a bit at a time
without losing context.

**This skill is a ledger + router, not an executor.** It reports status, selects the next
highest-leverage move, and hands off to the skill/spike/file that should do the work. It only
writes to its own `knowledge-base/` (status flips, checked sub-tasks, log entries).

> **Portability / provenance.** The `knowledge-base/` is a **personal cert ledger** — its evidence
> citations reference the specific project it was seeded from (an IMA-360 Playwright repo: paths,
> `npm run` commands, `_shared/` files, an IGS email). That is the historical record of where the
> evidence *was*, not a runtime dependency — the skill only reads/writes files under its own
> `knowledge-base/` and never dereferences those cited paths. As new work lands in other repos, add
> fresh evidence lines; the old citations stay as provenance.

> **Provenance / NTK:** The 30 statements are a *distributable paraphrase*. NEVER paste verbatim
> exam text or sample questions into any KB file. The CCA-F exam guide is Confidential /
> Need-to-Know and must never be ingested. Architecture rationale + the original snapshot:
> `.claude/analysis/cca-f-capability-audit.html`.

---

## Knowledge base (read at the start of every run)

The KB lives in the `knowledge-base/` subdirectory **alongside this skill file** — resolve it
relative to this `SKILL.md`, never by an absolute path.

- `00-index.md` — **THE index.** Status legend · domain roll-up · the 30-line spine table
  (one line per statement → status + next action + file link) · the impact-ranked backlog.
- `d1-agentic-orchestration/` … `d5-context-reliability/` — the per-statement dossiers
  (`<code>-<title>.md`), 7 / 5 / 6 / 6 / 6 files.
- `99-session-log.md` — dated cross-statement progress log (the context-preservation spine).

Every dossier follows one schema: `# <code> · <title>` + a `> **Domain/Status/Source**`
blockquote header, then `## What the exam expects`, `## What we have`, `## Depth gap`,
`## What we need to do` (checkbox sub-tasks + a `Next action:` line), optional `## Prep flag`,
and `## Work log`.

---

## Backlog ranking (the one formula)

Impact = **domain weight (%) × severity**, where severity = GAP 2 · PARTIAL 1 · BUILT 0.
Domain weights: **D1 27 · D2 18 · D3 20 · D4 20 · D5 15.** Higher impact = higher priority.
The current top of stack is maintained in `00-index.md`.

---

## Phases

### Phase 0 — Load
Read `00-index.md`. If the argument is a statement code (`1.2`) or `update/reaudit <code>`, also
read that dossier file. Resolve the file path from the index's spine table.

### Phase 1 — Status  (default — no arg, or `status`)
Lead with the **Readiness scorecard** headline (current weighted readiness % · B/P/G · GAPs left ·
delta vs the previous time-series row), then the domain roll-up and the top 3–5 of the impact-ranked
backlog. One screen. End with: "Run `/claude-architect next` to start the top item, or
`/claude-architect <code>` to drill in."

### Phase 2 — Drill  (`<code>`)
Print that statement's dossier: verdict + confidence, **What we have** (evidence), **Depth gap**,
the open sub-tasks, and the single **Next action**. Do not implement.

### Phase 3 — Next  (`next`)
Pick the highest-impact OPEN item (not BUILT-with-no-open-subtasks) from the backlog. State the
next bit and **hand off** to its routed target — e.g.:
- `1.1` → live smoke (`ant auth login` → `npm run smoke` in `~/.claude/spikes/agentic-loop-stop-reason/`) → BUILT
- `3.3` → `/skill-creator` + config (`paths:`-scoped rule)
- `4.5` → Batches-API spike + `scripts/llm-judge`
- `1.7` → extend `.claude/skills/resume/`
- `5.3` → net-new shared error-context schema + `.claude/workflows/deep-research.js`

Offer to launch that handoff. The skill itself recommends + routes; the user (or the routed
skill) does the implementation.

### Phase 4 — Record  (`update <code>`)  — the "Learn" discipline
After a bit of work lands, update the dossier: flip `Status` in the header if a verdict changed,
check the completed sub-task(s), and append a dated `## Work log` line (what changed + the
artifact). Then refresh that statement's line in `00-index.md` (status + next action) and append
a `99-session-log.md` entry: `YYYY-MM-DD · <code> · <what advanced> · <new status>`.
**A verdict may only be flipped to BUILT if the dossier cites a real artifact** (the audit's
evidence rule — no uncited BUILT).

**If the verdict changed, also update the Readiness scorecard in `00-index.md`** (the before/after
instrument): change the affected domain's `B/P/G` + the Total in BOTH the Domain roll-up and the
Scorecard table (they must stay equal), recompute that domain's `creditsᵈ÷nᵈ` and weighted
contribution, refresh the Total readiness, and **append one Time-series row**
(`Date · B/P/G · readiness · GAPs left · what changed`). Readiness
`R = Σ_domain [ domain% × (creditsᵈ÷nᵈ) ]` with credit BUILT 1.0 / PARTIAL 0.5 / GAP 0.0, rounded to
one decimal. Sanity-check: the five weighted contributions must sum to the Total.

### Phase 5 — Re-audit  (`reaudit <code>`, optional)
Lightweight single-statement re-verification: re-check the cited artifacts still exist and the
depth gap against the current tree, then confirm/deny a PARTIAL→BUILT promotion before Phase 4
flips it. Reuse the audit methodology (targeted grep/glob + ≤30-line reads). Do not re-run the
whole 30-statement sweep here.

---

## Conventions
- Self-contained: this skill duplicates the context it needs rather than cross-importing, per
  repo skill convention (CLAUDE.md may not be loaded when it runs).
- Only writes inside `knowledge-base/`. All implementation happens in the routed target.
- Keep the index and the dossiers consistent: the `00-index.md` Status cell for a statement must
  always match that dossier's header `Status`.
