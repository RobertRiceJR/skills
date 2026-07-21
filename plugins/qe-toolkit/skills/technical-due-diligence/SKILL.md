---
name: technical-due-diligence
description: >
    Technical due-diligence review of a repo or subsystem as a staff engineer
    reporting to a prospective acquirer — surface every material risk and quality gap,
    evidence-first. Reads actual implementation and traces real call paths (never infers
    from layout or docs); every finding cites file:line + quoted code, ranked
    Critical/High/Medium/Low by blast radius. Seven dimensions: architecture/coupling,
    test gaps, security, error handling, tech debt, dependency health, performance.
    Verdict-first (top-3 acquirer concerns), then the full breakdown; writes a
    self-contained HTML report + registry row.
    Large repos: scope one subsystem per run, or fan out per-dimension subagents.
    Trigger: "technical due diligence", "tech due diligence", "TDD review", "acquirer review",
    "risk and quality audit of this repo", "staff-eng code review".
    Do NOT use for closed-bug coverage gaps (use /bug-gap-analysis), Epic↔TC coverage
    (/gap-analysis), source-vs-suite coverage (/coverage-gap-scan), or single-spec quality
    (/spec-review).
user_invocable: true
argument: '<target repo or subsystem path> [--scope <glob>] [--dimensions a,b,c] [ticket: ID,...] (e.g., "C:\path\to\some-repo" or "src/tests/party --dimensions security,error-handling")'
---

# Technical Due Diligence

## Purpose

Review a repository or subsystem the way a staff engineer would when reporting to a
**prospective acquirer**: assume the seller has incentive to hide risk, and your job is to
find every material risk and quality gap before the deal closes. The deliverable is a
ranked, evidence-first report a non-author could act on.

**Stance:** adversarial but fair. You are not the author's friend and you are not writing a
roadmap — you are pricing risk. A finding only counts if you can prove it from the code.

**Source of truth:** the actual implementation. Filenames, directory layout, READMEs,
comments, and commit messages are *claims*, not evidence. Confirm or refute them by reading
the code and tracing the real call paths.

> **Portability.** Built for a project (IMA-360) that ships a shared **output-kit** and
> **agent-dispatch** template under `.claude/skills/_shared/`. Those are conveniences, not
> requirements — the skill runs against **any repo**:
> - **HTML report** — if `_shared/output-kit/report-template.html` + `report.css` exist, start from
>   them; **otherwise generate a self-contained HTML from scratch** (all CSS inlined, no sibling
>   assets) using this skill's own `reference/report-components.md` catalog. Use a clean neutral
>   theme by default; a brand theme only where the project supplies one.
> - **Subagent dispatch** — if `_shared/agent-dispatch-template.md` / `agent-recovery-ladder.md`
>   exist, follow them; otherwise construct prompts inline (the 9 sections are summarized in the
>   Large-Repo Scoping section) and recover from subagent errors inline. Never hard-stop on a
>   missing `_shared/` file.
> - The negative-routing skills named in the description (`/bug-gap-analysis`, `/gap-analysis`, …)
>   are project-specific — if the current project doesn't have them, simply don't route there.

---

## The Three Non-Negotiable Rules

1. **Evidence-first — read the implementation, trace real call paths.** Never infer a finding
   from a filename, a folder name, a doc, or a test's title. If you claim a function is
   unguarded, you must have read the function and followed its callers. If you claim a path is
   untested, you must have searched the test tree and confirmed nothing exercises it.
2. **Every finding cites `file:line` and quotes the relevant code.** No quote, no finding.
   A finding without a code citation is a hypothesis — either prove it or drop it.
3. **Be exhaustive. Do not stop early or summarize detail away.** The verdict is a summary;
   the body is not. Under-reporting risk is the one failure mode an acquirer cannot tolerate.

> ⚠ **Anti-pattern (auto-reject your own finding):** "The `auth/` directory suggests
> authentication is centralized." That is layout inference. Open the files, trace who calls
> the guard, and report what the code actually does.

---

## Severity — rank by blast radius

Every finding gets exactly one severity. Rank by **blast radius** (how much breaks, and how
badly, if this risk is realized), not by how easy it is to fix.

| Severity     | Blast radius                                                                                                                                              |
| ------------ | -------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Critical** | Data loss/corruption · auth/access bypass · secret exposure · money computed wrong · entire subsystem unrecoverable on failure · no test coverage on a money/auth path |
| **High**     | A core feature breaks for many users · a shared module's change silently breaks unrelated callers · an unhandled failure mode that reaches production · a dependency with a known exploit in the used surface |
| **Medium**   | Degraded behavior with a workaround · coupling that makes change risky but not breaking · partial/weak test coverage on a non-critical path · maintainability tax that compounds |
| **Low**      | Localized smell · cosmetic debt · minor version lag with no known impact · style/consistency gaps                                                         |

**Blast-radius multiplier — bump one level (max Critical) if the finding sits on:** money /
billing / commission paths · auth / permissions / tenancy · data sync / outbound integrations
· anything with no rollback. Note the bump explicitly in the finding (`severity: High → Critical (money path)`).

---

## The Seven Dimensions

Each dimension is its own report section. Cover all seven unless the user scoped a subset via
`--dimensions`. For each finding within a dimension, use the **Finding block** format below.

| # | Dimension                                  | The question it answers                                                                                  |
| - | ------------------------------------------ | ------------------------------------------------------------------------------------------------------- |
| 1 | **Architecture, coupling, boundaries**     | Where are the module boundaries, and where do they leak? What change radiates? Where are the god modules / circular deps / shared mutable state? |
| 2 | **Test coverage, test quality, and gaps**  | What is actually exercised vs. asserted-by-title-only? **Name what is untested** — by file/function/path, not a percentage. Where are no-assertion tests, flaky waits, over-mocking? |
| 3 | **Security surface & trust boundaries**    | Where does untrusted input enter? Where are authz checks (and where are they missing)? Injection, secret handling, SSRF, deserialization, over-broad permissions. |
| 4 | **Error handling & failure modes**         | What happens on failure? Swallowed exceptions, empty catch, unbounded retries, partial-write/no-rollback, missing timeouts, failure that corrupts state. |
| 5 | **Tech debt & maintainability**            | What makes this expensive to change? Duplication, dead code, magic constants, TODO/FIXME debt, inconsistent patterns, missing types, files that are too large to reason about. |
| 6 | **Dependency health & version risk**       | Outdated/abandoned/vulnerable deps, transitive risk, license risk, pinned-but-stale, dependency on a single maintainer, version traps (see repo's known graphql-codegen trap). |
| 7 | **Performance hotspots**                   | N+1 queries, unbounded loops/fetches, sync work on hot paths, missing pagination, allocations in tight loops, missing indexes behind a query. Trace the actual hot path — don't guess. |

### Finding block (the content contract for every finding — rendered as an HTML tier card; see Phase 4.1)

```markdown
#### [{SEVERITY}] {one-line finding title}

- **Evidence:** `path/to/file.ext:NN-MM`
    ```{lang}
    {the actual code, quoted verbatim — enough lines to prove the claim}
    ```
- **Why it matters:** {the concrete failure the acquirer inherits — the blast radius}
- **Call path / reach:** {who calls this, what breaks downstream — only what you traced}
- **Severity rationale:** {High → Critical (money path), etc.}
- **Remediation sketch:** {one line — not a roadmap; just what fixing it would take}
```

If a dimension has zero findings after a genuine pass, write one line:
`No material findings — {what you actually checked, e.g. "traced all 7 resolvers; all inputs validated via X"}`. Do **not** pad.

---

## Phase Map

| Phase | Action                                  | Produces                                                          |
| ----- | --------------------------------------- | ---------------------------------------------------------------- |
| 0     | Scope & Plan                            | Instantiated `reference/dispatch-template.md`; run ID; scope decision |
| 1     | Surface map (read entry points, trace)  | Real call-path inventory; the change-radius map                  |
| 2     | Dimension passes (×7, inline or fan-out) | Finding blocks per dimension                                     |
| 3     | Severity ranking + verdict synthesis    | Ranked findings; the top-3 acquirer verdict                      |
| 4     | Write report + register + log           | `reference/runs/<file>.html` (output-kit); `reference/index.md` row; ledger row |

---

## Phase 0 — Scope & Plan

1. Resolve the target from the argument (a repo path, a subsystem path, or a `--scope` glob).
   If the argument is ambiguous or missing, ask the user for the exact path/glob — do not guess.
2. **Assign the run ID.** Read `reference/index.md`, take the highest existing `TDD-NNN`, add 1
   (first run = `TDD-001`). The ID is sequential and stable — never reuse or renumber.
3. **Capture the date.** Run `git log -1 --format=%cd --date=short` (or `date +%F` via Bash) —
   do not hardcode. Capture any `jira: CI-####` references from the argument.
4. **Size the target** (Glob the scope, count files / approximate LOC). Decide the run shape
   against the **Large-Repo Scoping** rules below.
5. **Instantiate the plan.** Copy `reference/dispatch-template.md`, fill in Scope, dimensions
   in/out of scope, the subagent split (if any), and the run ID/date/Jira stamp. This filled
   plan becomes the **Scope & Plan** section at the top of the run report.

> One heroic "analyze everything in one pass" attempt is forbidden — it silently truncates and
> reads as "covered everything" when it didn't. Scope down or fan out (Phase 2).

---

## Phase 1 — Surface Map

Before any dimension pass, build a factual map of what's actually there — by reading, not by
listing directories.

1. Identify the real **entry points** (HTTP routes, resolvers, CLI commands, exported public
   API, scheduled jobs, message consumers). Read each one's body.
2. **Trace the call paths** from each entry point one to two levels deep — far enough to know
   what each entry point actually touches (DB, network, shared state, other modules).
3. Record the **change-radius map**: which modules are depended on by many others (high blast
   radius), and which are leaves. This drives Architecture (Dim 1) and prioritizes the rest.

Write this map into the report's Phase 1 section. It is evidence the later findings build on.

---

## Phase 2 — Dimension Passes

Run all seven dimensions (or the `--dimensions` subset). For each, produce Finding blocks
with `file:line` + quoted code, severity-ranked.

**Pass discipline per dimension:**

- Start from the Phase 1 surface map — walk the actual code paths the dimension cares about.
- Quote the code. If you can't quote it, you can't claim it.
- Rank each finding by blast radius (severity table above). Apply the multiplier where it fits.
- Don't stop at the first finding in a hot file — exhaust it.

### Inline vs. fan-out

- **Small/medium target** (fits a safe context budget — roughly ≤ ~40 files / one cohesive
  subsystem): run all dimensions inline, in this single context.
- **Large target:** do **not** attempt one pass. Choose one:
    - **(a) One subsystem per run** — scope to a single subsystem, finish it fully, write the
      report, then start a new run for the next subsystem (next sequential TDD-NNN).
    - **(b) Per-dimension subagent fan-out** — dispatch one read-only subagent per dimension,
      each with an explicit return contract, then synthesize. See Large-Repo Scoping below.

---

## Large-Repo Scoping (subagent dispatch)

When fanning out, mirror the read-phase dispatch pattern used by `/three-amigos` and
`/ready-for-testing`.

1. **Read `.claude/skills/_shared/agent-dispatch-template.md`** before constructing any prompt —
   fill its 9 sections. Set `subagent_type: "general-purpose"`, **context isolation (the
   default — omit `isolation`)**.
2. **Do NOT use `isolation: "worktree"`.** TDD is read-only; there are no parallel writes to
   isolate. Per the repo gotcha, worktree forks from `master` (not session HEAD) and sub-agents
   can escape into the main tree — a needless risk for a read-only audit. Keep every subagent
   read-only (return a manifest, write no files).
3. **One subagent per dimension** (or per (dimension × subsystem) for very large repos). Batch
   ≤ 6 concurrent. Each subagent's **return contract** is a list of Finding blocks for its
   dimension only — same format as above, with `file:line` + quoted code mandatory. A subagent
   that returns a finding without a citation has failed its contract; reject and re-dispatch.
4. On any subagent `Status: error`, apply `.claude/skills/_shared/agent-recovery-ladder.md`.
5. **Synthesize in this orchestrator context** — dedup overlapping findings across dimensions,
   re-rank the merged set by blast radius, and build the verdict. Do not let a subagent write
   the verdict; cross-dimension synthesis is the orchestrator's job.

> **No silent caps.** If you scope down (one subsystem, top-N files, a dimension subset),
> say so explicitly in the report's Scope & Plan section and in the index verdict — an
> acquirer must never read a partial audit as a complete one.

---

## Phase 3 — Severity Ranking + Verdict

1. Collect every Finding block across all dimensions into one list.
2. Re-rank globally by blast radius (a Critical in Dim 4 outranks a High in Dim 1).
3. **Build the verdict — the three findings that would most concern an acquirer.** These are
   not necessarily the three Criticals; they are the three that most change the *price or
   go/no-go* of the deal (a Critical money-path bug, a whole untested subsystem, a dependency
   time bomb). One line each, each pointing to its full Finding block below.
4. Tally severities (`critical/high/medium/low` counts) for the frontmatter and index row.
5. **Derive the Overall Ranking (1-10)** — a single subsystem score, a *pure function* of the tally
   (rubric is law; consistent run-to-run and across analysts):

   | Finding profile          | Score |
   | ------------------------ | ----- |
   | any Critical             | ≤ 3  (3 isolated · 1–2 as Criticals/Highs pile on) |
   | ≥2 High, no Critical     | 4–5   |
   | 1 High, no Critical      | 6     |
   | Medium/Low only          | 7–9  (7 many Medium · 9 a few Low) |
   | no material findings     | 10    |

   Carry the score into the `tdd-meta` block, the header pill, and the index `Score` column (Phase 4).

---

## Phase 4 — Output Handling

Every run writes a self-contained **HTML** report **and** registers it. Both, always.

### 4.1 — Write the run report (self-contained HTML)

Build the report as a **standalone** HTML file (openable / shareable / PDF-able with no sibling
assets) — do not leave a dangling `<link>`:

- If the project ships `.claude/skills/_shared/output-kit/report-template.html`, start from it and
  **inline `report.css`** into the `<style>` block. Otherwise build the page from scratch using this
  skill's `reference/report-components.md` catalog, with all CSS inlined.
- Use a clean **neutral** theme by default; apply a brand theme (e.g. an `igs-brand.json` /
  `theme-template.md`) only where the project provides one and the user asks.
- Optional PDF export: see `_shared/output-kit/doc-formats.md` where available.
- **Component vocabulary:** `reference/report-components.md` is the catalog of every available class
  (copy-paste snippets + theme/print notes). In particular: use the **code card** (`.codecard`) instead
  of a bare `<pre>` when quoting evidence code, and **severity lozenges** (`danger`/`validation`/`noise`/…)
  alongside the tier badge. `reference/component-gallery.html` is a reference artifact — **not** a run
  (no `TDD-NNN`, no `tdd-meta`, no `index.md` row).

Path: `reference/runs/YYYY-MM-DD-<scope-slug>.html`
`<scope-slug>` = the scope kebab-cased (e.g. `querygateway`, `party-subsystem`, `e2e-party-grid`).

**Embed machine-readable metadata** as an HTML comment immediately after `<!DOCTYPE html>` —
same keys the registry reads. Keep it greppable; never skip it:

```html
<!DOCTYPE html>
<!-- tdd-meta
run_id: TDD-NNN
date: YYYY-MM-DD
scope: <subsystem or repo>
jira: [CI-XXXX, ...]
severity: { critical: N, high: N, medium: N, low: N }
ranking: N
status: complete
-->
```

Then render, mapping onto the kit's sections, **in this order** (verdict-first):

1. **Header** (`header.report`) — eyebrow `Technical Due Diligence · QE`; headline = the scope;
   sub = one-line framing; meta row = Prepared for (acquirer/audience) · Date · Scope. Render the
   C/H/M/L tally as the legend/key cards, and the **Overall Ranking** (Phase 3 step 5) in the meta row
   as a `.score sN` heatmap pill (e.g. `Overall Ranking: <span class="score s4">4</span>`).
2. **Verdict** (`callout`) — the top-3 acquirer concerns, one line each, each anchor-linked to its
   finding below. Bottom-line-up-front — this comes before the detail.
3. **Scope & Plan** — the instantiated `dispatch-template.md` (target, globs in/out, dimensions
   in/out, subagent split if any, run ID/date/Jira). State any scope-down explicitly.
4. **Phase 1 — Surface Map** — entry points + traced call paths + change-radius map.
5. **Dimension-by-dimension breakdown** — one `h2.section` per dimension; render each Finding
   block as a `tier` card (severity → class: Critical/High `warn`, Medium `info`, Low `muted`)
   with the severity `badge`, the `file:line` evidence, the quoted code in `<pre>`, why-it-matters,
   call path, and remediation. Highest severity first. Cover all seven (or the scoped subset; note
   which were out of scope).

### 4.2 — Append the index row

The registry stays markdown (scannable/editable). Append (or insert to keep
**reverse-chronological, newest first**) one row to `reference/index.md`:

```markdown
| {YYYY-MM-DD} | TDD-NNN | {scope} | {verdict — ≤15 words, one line} | {C}/{H}/{M}/{L} | {CI-#### or —} | [report](runs/YYYY-MM-DD-<scope-slug>.html) |
```

Keep the verdict cell to a single scannable line; the Report cell links to the `.html` file.

### 4.3 — Skill run log (see final section)

---

## MCP Tools Required

This skill is **read-only and local** — its core (read code, trace paths, write the report)
uses no MCP tools. Optional, load via `ToolSearch` only if the user asks for them:

| Tool                                                 | When                                                       |
| ---------------------------------------------------- | --------------------------------------------------------- |
| `mcp__azure-devops__repo_get_file_content` / `search_code` | Target is an ADO repo not cloned locally; read files remotely |
| `mcp__claude_ai_Atlassian__getJiraIssue`             | A `jira: CI-####` ref was passed — pull context for the Scope section |

Never run the app, never write to a DB, never mutate the target. A due-diligence review
observes; it does not touch.

---

## Skill Run Log Entry (Final Step)

> **PILOT (2026-06-24):** this skill logs to the new **per-skill usage log** (spec:
> `_shared/skill-run-log.md`) instead of the central `skill-ledger-*.md`. The roll-up
> `_shared/scripts/skill-runs-rollup.mjs` reproduces the cross-skill ledger view on demand.

Resolve the contributor: run `git config user.name` (first word → `Robert`/`Jess`; fallback: the
name segment of `git rev-parse --abbrev-ref HEAD`); lowercase → `<name>`. Append ONE valid
single-line JSON object to `.claude/skills/technical-due-diligence/runs.<name>.jsonl` (create if
absent). **Append only — never edit prior lines.**

```json
{"date":"YYYY-MM-DD","by":"Robert|Jess","ticket":"TDD-### | scope | CI-####","quality":"✅|⚠️|❌","well":"≤15 words","poorly":"≤15 words (— if none)","improve":"≤30 words","model":"claude-opus-4-8","duration":"~Nm","run":"reference/runs/<file>.html"}
```

**Quality self-assessment (the `quality` field):**

- ✅ Clean — all in-scope dimensions covered, every finding cited + quoted + ranked, report written + indexed
- ⚠️ Partial — scope reduced mid-run, a dimension left incomplete, or some findings uncited (flag which)
- ❌ Rough — abandoned before the report was written, or findings could not be evidenced
