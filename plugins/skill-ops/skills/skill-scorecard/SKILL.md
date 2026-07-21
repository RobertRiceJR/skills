---
name: skill-scorecard
description: >
    Score and rank the whole skill ecosystem on four axes — Value, Sustainability,
    Maintainability, Maturity — plus a ceiling read for headroom, a per-type weighted
    Standing score, and a recommended disposition (Invest / Maintain / Harden / Simplify /
    Retire). Deep-reads every live skill.md, folds in the live skill-graph census signals,
    emits a self-contained interactive HTML to reference/runs/, appends the run to the
    historical data store, and regenerates the trend dashboard.
    Read-only over the skills; the scoring rubric SSOT is reference/rubric.md.
    Trigger: "score the skills", "skill scorecard", "rank the skills", "skill ecosystem rankings",
    "which skills should we harden/retire/invest in", "skill health dashboard", "/skill-scorecard".
    Do NOT use for the raw reference/coupling census (that is /technical-due-diligence, run TDD-011),
    single-skill blast-radius before an edit (/skill-evolve + npm run skill:impact), or test-suite
    health (/roast-me).
user_invocable: true
argument: '[--date YYYY-MM-DD] [--signals-only] (default: full deep-read of every live skill, today''s date)'
---

# Skill Scorecard

Rank the skill ecosystem so the overhaul has a map: what is valuable, what is fragile, what is
tangled, what has headroom, and — per skill — the one action to take. Every run is a comparable
datapoint in a historical store, and the dashboard shows how the ecosystem moves over time.

This is an **orchestrator**: it regenerates census signals, fans out subagents to deep-read every
skill, scores centrally, emits the deliverable, and updates the history + dashboard. The scoring
contract lives in **`reference/rubric.md`** — read it before every run; it is the single source of
truth for axes, formulas, weights, and dispositions.

> **Portability.** Built for a project (IMA-360) that generates a `_shared/skill-graph.json` census
> via `npm run skill:graph`. **The graph and its `npm run skill:*` tooling are optional signal
> inputs, not requirements:**
> - **Skill discovery** — enumerate skills from wherever the current project keeps them: directories
>   containing a `SKILL.md` under `.claude/skills/`, `~/.claude/skills/`, **and/or `plugins/*/skills/`**
>   (the plugin-marketplace layout this repo itself uses). Exclude `_shared` and `_archive`.
> - **Census signals** — if `_shared/skill-graph.json` (or `npm run skill:graph`) is absent, score on
>   the **intrinsic deep-read only**; mark the signal-derived sub-axes "unavailable (intrinsic-only)"
>   and say so in the report rather than hard-stopping.
> - **`run-counts.seed.json`** — if absent or empty, treat run-frequency as unknown (0); the seed
>   ships empty here and is populated from live usage over time.
> - **Dispatch template / recovery ladder** — use `_shared/agent-dispatch-template.md` /
>   `_shared/agent-recovery-ladder.md` where the project provides them; otherwise construct subagent
>   prompts inline (give each the rubric anchors + skills path) and handle errors inline.

## Non-negotiables

- **Rubric is law.** Apply `reference/rubric.md` exactly so runs are comparable. If you change scoring, change it there first, then mirror the constant into `scripts/score.py`.
- **Standing is health, not importance.** Never present it as "most valuable first." Value is its own axis.
- **Read-only over skills.** Never edit a skill being scored. The only writes are this skill's own `reference/data/`, `reference/runs/`, `dashboard.html`, and the two run logs.
- **Never hardcode the date** — derive it (`date +%F`).
- **Full deep-read each run** (per the chosen design): re-score every live skill from its current `skill.md`. `--signals-only` is an explicit fast path that reuses the last run's read-axes and only refreshes census signals.

## Phase Map

| Phase | Action | Produces |
| --- | --- | --- |
| 0 | Preflight & scope | date, live skill set, last run loaded |
| 1 | Gather census signals | `reference/data/<date>-signals.json` |
| 2 | Deep-read fan-out (full) | `reference/data/<date>-readaxes.json` |
| 3 | Score centrally | `reference/data/<date>-run.json` |
| 4 | Emit deliverable | `reference/runs/<date>-skill-scorecard.html` |
| 5 | Append history + dashboard | `runs.jsonl`, `reference/index.md`, `dashboard.html` |
| 6 | Verify & self-assess | coverage + sanity checks |
| 7 | Skill run-log entry | `runs.<name>.jsonl` |

## Phase 0 — Preflight & scope

1. `date +%F` → `<date>`. Never hardcode it.
2. Refresh the census SSOT: `npm run skill:graph` (regenerates `_shared/skill-graph.json`). If it fails, proceed with the existing graph and note it.
3. Determine the live skill set: every directory containing a `SKILL.md` (case-insensitive) under the current project's skills roots — `.claude/skills/`, `~/.claude/skills/`, and/or `plugins/*/skills/` — excluding `_shared` and `_archive`. This is the scoring scope.
4. Load the previous run for since-last-run deltas: the newest `reference/data/*-run.json` before `<date>` (none on first run).

## Phase 1 — Gather census signals

Run `python3 scripts/gather-signals.py <date>`. It reads `_shared/skill-graph.json` for each project skill's `incoming.files` (blast radius) and `outgoing.skills` (fan-out), and `reference/data/run-counts.seed.json` for ledger run-frequency, emitting `reference/data/<date>-signals.json`.

> Run frequency: the historical counts seeded from TDD-011 live in `run-counts.seed.json`. To refresh from live usage logs, run `npm run skill:runs -- --json` and merge new counts into that seed before this phase.

## Phase 2 — Deep-read fan-out (the scoring read)

Re-score every live skill from its current body. **Read `_shared/agent-dispatch-template.md` first** and fill its sections for each subagent.

- Batch the live skills into groups of ~8 and dispatch **≤ 6 concurrent** `subagent_type: "general-purpose"` agents (omit `isolation` — context isolation is the default; this is a read-only audit, never a worktree).
- Give every subagent the **identical** axis anchors from `reference/rubric.md` (§"The four axes + ceiling"), the intrinsic-scoring instruction, and the skills dir path. Errors → `_shared/agent-recovery-ladder.md`.
- **Return contract** — each subagent returns one block per skill, nothing else:
  ```
  ### <name>
  purpose: <one line>
  type: orchestrator|tool|one-off — <why>
  value: N — <evidence>
  sustainability: N — <external deps that threaten it>
  maintainability: N — <size/complexity/safety-net>
  maturity: N — <evidence>
  ceiling: N — <fuller-buildout sketch>
  ```
- Collect all blocks into `reference/data/<date>-readaxes.json`:
  `{"date","by","method","skills":[{"name","type","vi","si","mi","mat","ci","purpose"}]}`
  (`type` from the subagent's suggestion, reconciled against `reference/rubric.md` §"Type classification").

`--signals-only`: skip this phase; copy the previous run's read-axes to `<date>-readaxes.json` unchanged.

## Phase 3 — Score centrally

`python3 scripts/score.py <date>` joins read-axes + signals, applies the census fold, per-type weights, headroom, and disposition (all per `reference/rubric.md`), and writes `reference/data/<date>-run.json` (`{meta, rows}`). Central scoring guarantees one consistent rater across all skills and runs.

## Phase 4 — Emit the deliverable

`python3 scripts/render-report.py <date>` writes a self-contained interactive report to `reference/runs/<date>-skill-scorecard.html` — three ranked tables (Orchestrators / Tools / One-offs), sortable columns, disposition filter chips, search, Maturity→Ceiling gap bars, and a greppable `<!-- scorecard-meta -->` header. CSS is inlined (no external dependency) per the output-kit portability rule.

## Phase 5 — Append history + regenerate dashboard

1. `python3 scripts/render-dashboard.py` rebuilds `dashboard.html` from **all** `reference/data/*-run.json` — disposition trend, axis drift, per-skill trajectory (sparklines + Δ-vs-prev), and churn.
2. Append one metrics line to `runs.jsonl` (date, total, disp counts, axis averages) — the baseline for the next run's since-last-run delta.
3. Add a row to `reference/index.md` (reverse-chron): `| <date> | <total> | <disp summary> | [report](runs/<date>-skill-scorecard.html) |`.

## Phase 6 — Verify & self-assess

- Coverage: every live skill appears exactly once in `<date>-run.json`; report any skill in the graph but not scored, or scored but no longer live.
- Sanity (consistency with signals): high-blast-radius skills should not score high Maintainability; pure sinks (fan-out 0) should not score low Sustainability; `Harden` only where S ≤ 2; `Maintain` only where no axis is flagged.
- No leftover `__PLACEHOLDER__` tokens in the HTML; row count = live skill count.
- Self-grade the run for the run log: ✅ clean / ⚠️ partial / ❌ rough.

## Phase 7 — Skill run-log entry (final step)

Append one line to `runs.<name>.jsonl` (`<name>` = lowercase first word of `git config user.name`), per `_shared/skill-run-log.md`:
`{"date","by","ticket","quality","well","poorly","improve","model","duration?","run":"reference/runs/<date>-skill-scorecard.html"}`

## MCP Tools Required

**None.** This skill is read-only and local: it reads `skill.md` files, runs npm/python scripts, and writes its own outputs. It uses no MCP servers and never touches the app, a DB, or any external system. Subagents are dispatched via the **Task** tool (general-purpose), not an MCP.

## Scripts

| Script | Role |
| --- | --- |
| `scripts/gather-signals.py <date>` | skill-graph + run-counts → `<date>-signals.json` |
| `scripts/score.py <date>` | read-axes + signals → `<date>-run.json` (the engine; mirrors `reference/rubric.md`) |
| `scripts/render-report.py <date>` | run record → interactive HTML deliverable |
| `scripts/render-dashboard.py` | all run records → `dashboard.html` |
