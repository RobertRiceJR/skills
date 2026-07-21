---
name: condense-claude-md
description: >
    Analyzes a CLAUDE.md file, classifies each section as load-bearing / reference-only /
    duplicate / outdated, proposes a condensation strategy with per-section actions
    (KEEP / COMPRESS / MOVE+LINK / DROP), and executes approved changes. Produces a
    before/after metrics report. Default target: project CLAUDE.md.
user_invocable: true
argument: '[path to CLAUDE.md] (optional — defaults to project root CLAUDE.md)'
---

> **Portability:** GLOBAL skill — operates on the current project's CLAUDE.md (or any path passed
> as the argument). If the current project has `.claude/skills/_shared/skill-architecture.md`, read it
> first to load the orchestrator/sub-skill routing table (it informs DUPLICATE/DROP calls); if absent,
> skip that step. All `_shared/…` overlap-source and report paths below are project-relative and
> degrade gracefully when they don't exist.

# condense-claude-md

Audits a CLAUDE.md for token bloat, classifies every section, proposes a condensation
strategy, and — after explicit approval — executes surgical edits. Read-only until the
user approves Phase 3. Produces a report under the project's `.claude/skills/_shared/tickets/`
when that directory exists; otherwise writes it next to the target CLAUDE.md.

---

## Phase 0 — Bootstrap

1. **Resolve target file:**
    - If argument provided → use that path verbatim
    - Otherwise → default to `{project-root}/CLAUDE.md`
2. Read the file; compute baseline metrics:
    - Lines: count of newlines
    - Chars: raw character count
    - Estimated tokens: `chars / 4` (rough approximation)
3. **Verify overlap sources exist** (Glob or Read to confirm):
    - `.claude/skills/_shared/skill-architecture.md`
    - `.claude/skills/_shared/ima-360-reference.md`
    - Note any that are missing — they affect DROP/MOVE decisions downstream
4. Print:
    ```
    Analyzing: {resolved path}
    Baseline:  {lines} lines / {chars} chars / ~{tokens} tokens
    Overlap sources: skill-architecture.md ✓/✗  |  ima-360-reference.md ✓/✗
    ```

---

## Phase 1 — Section Audit

1. Parse the file into sections by `##` headers. Record: header text, start line, end line,
   line count (header + body).
2. For each section assign **one** classification:

    | Classification   | Criteria                                                                                                    |
    | ---------------- | ----------------------------------------------------------------------------------------------------------- |
    | **LOAD_BEARING** | Must be read before any skill invocation — conventions, critical patterns, env URLs, MCP servers, git rules |
    | **REFERENCE**    | Useful but only looked up occasionally; not needed on every invocation                                      |
    | **DUPLICATE**    | Same content exists authoritatively in a named shared file                                                  |
    | **OUTDATED**     | Stale, superseded, or rendered redundant by a shared file that is more complete                             |

3. For DUPLICATE / OUTDATED sections: record the authoritative source path.
4. Output audit table:

```
| Section                        | Lines | Classification | Overlap Source                               |
|--------------------------------|-------|----------------|----------------------------------------------|
| Repo Identity                  | 10    | LOAD_BEARING   | —                                            |
| What This Repo Does            | 10    | LOAD_BEARING   | —                                            |
| Key Commands                   | 21    | LOAD_BEARING   | —                                            |
| Directory Structure            | 59    | DUPLICATE      | _shared/ima-360-reference.md §Repo Structure |
| Import Aliases                 | 27    | REFERENCE      | _shared/ima-360-reference.md §Key Helpers    |
| Waiter Pattern                 | 16    | LOAD_BEARING   | —                                            |
| GraphQL Fixture & API Patterns | 52    | REFERENCE      | _shared/ima-360-reference.md (partial)       |
| Spec File Placement Reference  | 23    | REFERENCE      | _shared/skill-architecture.md (partial)      |
| Test Environments              | 10    | LOAD_BEARING   | —                                            |
| MCP Servers                    | 16    | LOAD_BEARING   | —                                            |
| Auth Storage                   | 9     | REFERENCE      | —                                            |
| Known Conventions              | 15    | LOAD_BEARING   | —                                            |
| Skills Ecosystem               | 58    | DUPLICATE      | _shared/skill-architecture.md (authoritative)|
| GraphQL Types Maintenance      | 16    | REFERENCE      | —                                            |
| Git Workflow                   | 8     | LOAD_BEARING   | —                                            |
```

> **Note:** The table above reflects the IMA 360 project CLAUDE.md as of 2026-05-19.
> For a different CLAUDE.md, re-classify from scratch — do not copy this table.

---

## Phase 2 — Condensation Strategy

Assign **one action** to each section using these rules:

| Rule                                                              | Action                                             |
| ----------------------------------------------------------------- | -------------------------------------------------- |
| LOAD_BEARING → always                                             | `KEEP` — never drop or move a load-bearing section |
| DUPLICATE, authoritative source confirmed present                 | `DROP`                                             |
| DUPLICATE, source present but partial overlap                     | `COMPRESS` — keep the delta content only           |
| REFERENCE, verbose (code blocks, long tables, prose examples)     | `COMPRESS`                                         |
| REFERENCE, full content already in a shared file                  | `MOVE+LINK`                                        |
| REFERENCE, short + standalone (≤ 8 lines, not in any shared file) | `KEEP`                                             |
| OUTDATED                                                          | `DROP`                                             |

**Action definitions:**

- **`KEEP`** — no change
- **`COMPRESS`** — retain the `##` header; rewrite body to essential rules only (≤ 8 lines target); strip code examples that are already in shared files
- **`MOVE+LINK`** — append full content to the destination shared file (if not already there); replace the section body in CLAUDE.md with a single-line pointer
- **`DROP`** — remove header + body entirely from CLAUDE.md; authoritative copy is already indexed

For each action compute estimated line savings (lines removed from CLAUDE.md after change).

Output strategy table:

```
| Section                        | Action      | Est. Savings | Notes                                         |
|--------------------------------|-------------|--------------|-----------------------------------------------|
| Repo Identity                  | KEEP        | 0            | Orientation — always needed                   |
| What This Repo Does            | KEEP        | 0            | Orientation — always needed                   |
| Key Commands                   | KEEP        | 0            | Load-bearing                                  |
| Directory Structure            | DROP        | −59          | Fully in ima-360-reference.md §Repo Structure   |
| Import Aliases                 | COMPRESS    | −19          | Keep rule + tsconfig note; cut full alias list  |
| Waiter Pattern                 | KEEP        | 0            | Load-bearing — critical ordering rule           |
| GraphQL Fixture & API Patterns | COMPRESS    | −44          | Keep fixture import + one request pattern only  |
| Spec File Placement Reference  | COMPRESS    | −15          | Keep table; cut prose paragraph above it        |
| Test Environments              | KEEP        | 0            | Load-bearing                                    |
| MCP Servers                    | KEEP        | 0            | Load-bearing                                    |
| Auth Storage                   | KEEP        | 0            | Short, standalone, not duplicated               |
| Known Conventions              | KEEP        | 0            | Load-bearing                                    |
| Skills Ecosystem               | DROP        | −58          | skill-architecture.md is authoritative          |
| GraphQL Types Maintenance      | COMPRESS    | −8           | Keep 2-line rule; cut manual-patch example      |
| Git Workflow                   | KEEP        | 0            | Load-bearing                                  |
```

Then print projected totals:

```
Before: {N} lines / ~{T} tokens
After:  {N2} lines / ~{T2} tokens
Savings: −{ΔN} lines / ~−{ΔT} tokens ({pct}% reduction)
```

---

## Phase 3 — Approval Gate (HARD STOP)

Present the Phase 1 audit table and Phase 2 strategy table together.

Then print:

> "Ready to execute? This will edit `{resolved path}`.
> Adjust any action above or confirm with **yes** to proceed."

**Do not read, write, or modify any file until the user explicitly confirms.**

If the user adjusts an action (e.g., changes DROP → COMPRESS for a section), update the
strategy table and re-compute projected totals before asking again.

---

## Phase 4 — Execute

Process sections **in document order** (top to bottom). For each:

### DROP

1. Remove the `##` header and its entire body from CLAUDE.md
2. If the section contained content NOT confirmed in the overlap source, log a warning:
   `⚠ Dropped "{section}" — verify content exists in {source}`

### COMPRESS

1. Keep the `##` header unchanged
2. Rewrite the body: keep the behavioral rule / "why"; remove code blocks already in
   shared files, remove duplicate tables, remove prose examples
3. Target: ≤ 8 lines of body text per section
4. When referencing a shared file for the full detail, add a one-liner at the bottom of
   the compressed section:
   `> Full reference: \`.claude/skills/\_shared/{file}.md\``

### MOVE+LINK

1. Read the destination shared file
2. If the section's content is not already present, append it under an appropriate header
3. Replace the entire section body in CLAUDE.md with:
   `> See \`.claude/skills/\_shared/{file}.md\` — {section name}.`
4. Keep the `##` header

### KEEP

No changes.

After processing all sections, recompute actual metrics: lines, chars, tokens.

---

## Phase 5 — Verify + Report

1. **Print actual metrics:**

    ```
    Before: {N_before} lines / ~{T_before} tokens
    After:  {N_after} lines / ~{T_after} tokens
    Saved:  −{ΔN} lines / ~−{ΔT} tokens ({pct}% reduction)
    ```

2. **Show git diff** of CLAUDE.md (and any modified shared files).

3. **Write report** to `.claude/skills/_shared/tickets/condense-claude-md-{YYYY-MM-DD}.md` if that
   directory exists in the current project; otherwise write `condense-claude-md-{YYYY-MM-DD}.md`
   next to the target CLAUDE.md:

```markdown
# CLAUDE.md Condensation Report — {YYYY-MM-DD}

**Target:** {resolved path}
**Skill:** condense-claude-md

## Metrics

| Metric | Before | After | Saved          |
| ------ | ------ | ----- | -------------- |
| Lines  | {N}    | {N2}  | −{ΔN} ({pct}%) |
| Tokens | ~{T}   | ~{T2} | ~−{ΔT}         |

## Changes Applied

| Section | Action | Lines Saved |
| ------- | ------ | ----------- |

{rows — one per non-KEEP section}

## Warnings

{list any ⚠ warnings from Phase 4, or "None"}
```

4. Ask:

> "Want to commit this? `git diff` is shown above. Run `git add CLAUDE.md` and confirm."

**Do not commit automatically.**

---

## Notes

- This skill is safe to re-run. Re-running on an already-condensed file will produce a
  short audit with mostly KEEP actions — that's the expected steady-state result.
- For the **global CLAUDE.md** (`~/.claude/CLAUDE.md`): pass the full path as the argument.
  The overlap-source check will report missing project shared files as expected; adjust
  DROP/COMPRESS decisions accordingly since shared files don't apply.
- If a new shared file is created after a MOVE+LINK, add it to the overlap source list
  at the top of Phase 0 for future runs.
- **COMPRESS forward-pointer rule:** every COMPRESS section that references a shared file
  for the full detail must end with `> Full reference: .claude/skills/_shared/{file}.md`.
  Without it, the compressed section is a dead end — the reader cannot find the long form.
