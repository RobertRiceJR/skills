---
name: sync-skills
description: >
    Skill architecture drift detector. Audits every skill.md file under
    .claude/skills/ and ~/.claude/skills/ against the routing source of truth
    (_shared/skill-architecture.md), the project MEMORY index, and any /<skill>
    cross-references inside skill bodies. Flags description drift, missing
    skills, stale routing entries, and dead orchestrator phase-map references.
    Default mode is report-only — --apply rewrites only the skill-architecture.md
    description entries that drifted (never removes or renames skills). --optimize
    runs the skill-eval triggering loop for skills with an evals/ set and proposes
    improved descriptions (never auto-applies).
user_invocable: true
argument: '[mode]  # optional — empty (full audit) | --apply (rewrite approved description drift) | --optimize (propose better descriptions via skill-eval loop) | --scope=<project|global> to limit to one skills root'
---

# Skill Architecture Drift Sync

Verifies the skills ecosystem matches its routing source of truth. Two-phase:
**audit first → drift report → approval gate → rewrite second.**

Called by `/sync` as part of the umbrella drift audit. Can also be invoked standalone.

> **Portability:** this is a GLOBAL skill — it operates on **the current working directory's**
> project. All project-side paths (`.claude/skills/`, `_shared/skill-architecture.md`, `MEMORY.md`,
> the `_shared/skill-eval/` and `_shared/skill-creator-patches/` harness paths) are resolved
> relative to cwd. If the current project has no `_shared/skill-architecture.md`, degrade to a
> disk-only audit (enumerate skills, scan cross-references) and skip the routing-drift checks —
> do not hard-stop. The global tree (`~/.claude/skills/`) is always audited.

> **Impact-ranking (optional, project-agnostic):** if the current project provides a generated
> `_shared/skill-graph.json` (a skill dependency graph — incoming/outgoing reference counts per
> skill), use its per-skill incoming-file counts to RANK the drift report by blast radius
> (Critical ≥10 referencing files · High 5–9 · Medium 2–4 · Low 1) so the highest-coupling drift
> surfaces first. If absent, rank by raw cross-reference count as before. Never require it.

---

## When to use this skill

- After renaming, deleting, or adding a skill — confirm the routing doc and MEMORY index reflect it.
- Before a docs cleanup pass — surface stale references first.
- As Phase 1 of a `/sync` run.
- Quarterly hygiene check.

**Do NOT use this skill for:**

- Generating new skills — that's a manual authoring task.
- Editing skill content beyond the `description:` frontmatter — `--apply` only touches routing entries, and `--optimize` only *proposes* description changes (you apply them by hand).
- Removing deprecated skills — flagged for review, never auto-deleted (deprecation is a deliberate human call).

---

## Step 1 — Parse Mode

| Argument                | Mode                                                                  |
| ----------------------- | --------------------------------------------------------------------- |
| _(empty)_               | Full audit across project + global skills, report only                |
| `--scope=project`       | Audit only `.claude/skills/` (this repo)                              |
| `--scope=global`        | Audit only `~/.claude/skills/`                                        |
| `--apply`               | Apply the most recent drift report (must come second)                 |
| `--optimize`            | Run the skill-eval triggering loop for skills with an `evals/` set; propose better descriptions (report-only; never auto-applies). Additive — does not replace the audit. |

`--apply` requires a drift report in the same session. If no report is in context, refuse and ask for an audit run first.

`--optimize` is independent of `--apply` — it runs the triggering loop (Step 10) and is the only mode that proposes changes to a `skill.md` `description:` (proposals only; applying is a separate human-approved edit). It spends real `claude -p` calls, so it is not part of the default audit or of `/sync`.

---

## Step 2 — Enumerate Skills On Disk

Use Glob to find every skill.md:

```
Glob: .claude/skills/*/SKILL.md           (project — classic layout)
Glob: plugins/*/skills/*/SKILL.md          (project — plugin-marketplace layout)
Glob: ~/.claude/skills/*/SKILL.md          (global / user)
```

For each match, Read the frontmatter only (lines 1–30 is sufficient) and extract:

- `name:` field
- `description:` field (collapse to single line for comparison)
- `user_invocable:` field (true / false / missing)
- `description:` **character length** (collapsed-whitespace form) — the harness truncates each `available_skills`
  entry at ~1024 chars, so an over-length description silently loses its tail (typically the last triggers). See
  `_shared/knowledge/reference/bug-patterns.md` #53.
- Path on disk

Build an in-memory table: `name → {path, description, scope}`.

Skip `_shared/`, `_meta/`, and any directory without a `skill.md`. Subdirectory skills (e.g. `playwright-workflow/`) count; loose markdown files do not.

---

## Step 3 — Parse the Routing Source of Truth

Read the current project's routing source of truth — `.claude/skills/_shared/skill-architecture.md`
(resolved relative to cwd) — in full. If it does not exist, skip Steps 3–4's routing comparison and
note "no routing doc in this project — disk-only audit" in the report. Extract two views:

1. **Decision tree entries** (the `├─ /<skill>` lines in the "Which Skill Do I Use?" tree near the top). Each line names a skill and gives a one-line summary.
2. **Section-level entries** (later in the file — orchestrator phase maps, skill-by-skill tables, deprecation notes).

Build a second table: `name → {one_line_summary, mentioned_in_sections}`.

Also read `MEMORY.md` at the project memory path and extract every memory entry — the goal is to find references to skill names so we can spot stale memory pointers later.

---

## Step 4 — Compute Drift

For each skill on disk and each skill referenced in the routing doc, classify:

| Category                      | Definition                                                                           |
| ----------------------------- | ------------------------------------------------------------------------------------ |
| **Match**                     | Skill on disk AND in routing doc AND description aligns with routing summary         |
| **Missing from routing**      | Skill exists on disk but never named in skill-architecture.md                        |
| **Orphan in routing**         | Skill named in skill-architecture.md but skill.md file does not exist                |
| **Description drift**         | Both present, but skill.md `description:` summary disagrees with routing tree summary |
| **Stale cross-reference**     | A skill.md body references `/other-skill` that does not exist on disk                |
| **MEMORY entry mismatch**     | MEMORY.md mentions a skill name no longer on disk                                    |
| **Deprecation candidate**     | Skill marked "deprecated" in routing doc but skill.md still present and user_invocable |
| **Over-length description**   | `description:` (collapsed) exceeds 1024 chars → tail truncated in `available_skills`, dropping trailing triggers (bug-patterns #53) |

**Description alignment** is a fuzzy check, not a string equality. Two summaries align if their first 12–15 words cover the same intent (input → action → output). Wording differences ≠ drift; substantive intent differences = drift. When in doubt, flag as drift and let the user decide.

---

## Step 5 — Cross-Reference Scan

For every skill.md found in Step 2, Grep its body for `/<skill-name>` patterns:

```
Grep: pattern="/[a-z][a-z0-9-]+" path=<skill.md path> output_mode=content
```

For each match: confirm the referenced name exists in the disk-table from Step 2. If not, record a stale-cross-reference finding with: source skill, target name, line number.

Ignore common slash patterns that are not skill refs: file paths (`/usr/`, `/var/`), URL paths (`/graphql`), date formats (`5/27`), pluralized words (`s/he`). Heuristic: a candidate is a skill ref if it appears in body prose (not inside a code block) and the segment is kebab-case.

---

## Step 6 — Report Drift

Output the report in this shape. Skip categories with zero findings.

```
## Skill Architecture Drift Report — <YYYY-MM-DD>

### Missing from routing (N)
- /<skill-name> — exists at <path>, never named in skill-architecture.md

### Orphan in routing (N)
- /<skill-name> — referenced in skill-architecture.md line <n>, no skill.md found

### Description drift (N)
- /<skill-name>:
    routing says:   "<one_line_summary from routing doc>"
    skill.md says:  "<description from frontmatter>"
    intent diff:    <one-line characterization of the disagreement>

### Stale cross-references (N)
- /<source-skill> → references /<missing-target> (line <n>)

### MEMORY entry mismatches (N)
- MEMORY.md line <n>: mentions /<missing-skill>

### Deprecation candidates (N)
- /<skill-name> — marked deprecated in routing but still user_invocable

### Over-length descriptions (N)
- /<skill-name> — description is <chars> chars (>1024); tail truncated in available_skills (bug-patterns #53). Trim to ≤1024 keeping discrimination anchors, then re-validate triggering (skill-creator run_eval, deploy-then-measure).

---

### Summary
- Skills on disk:           N (M project, K global)
- Skills in routing:        N
- Total drift findings:     N
- Apply-eligible findings:  N  (description drift only)
- Review-required findings: N  (missing/orphan/deprecation/stale-refs require human judgment)
```

If no drift detected: report `## No skill architecture drift — N skills audited <date>` and stop. Do not run Step 7+.

---

## Step 7 — Approval Gate

After the report, stop and state:

> Review the drift above. Description-drift entries are apply-eligible — run `/sync-skills --apply` to rewrite the routing tree summaries to match the skill.md descriptions, or name specific skills to update (e.g., "apply /three-amigos and /ready-for-playwright only"). All other categories require human review — re-run after addressing.

Do not touch skill-architecture.md until the user responds.

---

## Step 8 — Apply Approved Updates

For each approved description-drift finding:

1. **Locate** the routing tree line in skill-architecture.md (line number from the report).
2. **Rewrite the one-line summary only** to align with the skill.md frontmatter description. Keep the `├─` prefix, skill name, and indentation intact. Compress the description's first 1–2 sentences into a single line ≤ 100 chars.
3. **Bump the file header** — update the `Last updated:` line at the top of skill-architecture.md with today's date and a one-line "Drift sync: N descriptions refreshed" suffix.

Apply does NOT:

- Add a routing entry for a "Missing from routing" finding — that requires a deliberate placement decision in the tree.
- Remove an "Orphan in routing" entry — could be an in-flight migration; user judgment required.
- Touch any skill.md file. skill.md is the source of truth for descriptions; the routing doc is what gets synced toward it.

---

## Step 9 — Verify the Apply

1. **Re-read** each rewritten line and confirm it now matches the source skill.md description.
2. **Grep skill-architecture.md** for the old summary text — confirm no leftover references.
3. **Confirm header date** was bumped.

Report verification as:

```
## Verification
- Routing entries rewritten: N
- Stale references in skill-architecture.md: <count, with line numbers>
- Header date bumped: PASS / FAIL
```

---

## Step 10 — Optimize Mode (optional, `--optimize`)

`--optimize` is a separate, additive flow — it does not replace the drift audit. It targets
*triggering accuracy*: whether each skill's `description:` actually causes the model to fire it.
The eval harness is the `eval-judge` plugin's `skill-creator` scripts (`run_eval.py`, `run_loop.py`);
its `README.md` documents eval-set format, invocation, and caveats. If the current project provides
no such harness, report the optimize step as unavailable and skip it — don't hard-stop.

1. **Find eligible skills.** From the Step 2 disk table, keep only skills that have an
   `evals/trigger_evals.json` file. List skills without one as "not optimizable (no eval set)" and
   skip them — do not invent eval sets here (that's a deliberate authoring task).
2. **Pre-flight.** The `skill-creator` scripts in the `eval-judge` plugin already carry the
   Windows-portability patches; no re-apply step is needed here.
3. **Run the loop** for each eligible skill via `skill-creator`'s `run_loop.py`
   (`--holdout 0.4`, `--model claude-opus-4-8`).
4. **Collect proposals.** From each loop's JSON output capture `original_description`,
   `best_description`, and `best_score`.
5. **Report** — only skills where the proposal beat the original:

   ```
   ### Description optimization proposals (N)
   - /<skill> — test score <orig>→<best>
       current:  "<original_description>"
       proposed: "<best_description>"
   ```
6. **Approval gate.** Stop. Proposals are NOT applied. State: "These are proposals from the
   triggering loop. To accept one, I'll edit that skill's `skill.md` `description:` frontmatter —
   name the skills to apply." Applying is a direct, human-approved `skill.md` edit — the one case
   where this skill touches `skill.md`, and only on explicit instruction.

Optimize mode honors the same safety contract as `--apply`: report-first, explicit per-skill
approval, no blind writes.

---

## Output Format Summary

| Phase                  | Output                                                                          |
| ---------------------- | ------------------------------------------------------------------------------- |
| Step 6 — drift report  | `## Skill Architecture Drift Report — <date>` + per-category sections + summary |
| Step 7 — approval gate | One-line prompt; stop                                                           |
| Step 8 — apply         | Per-entry one-liner: `✓ /<skill> — routing summary refreshed`                   |
| Step 9 — verify        | Verification block; follow-ups (if any) as a separate list                      |
| Step 10 — optimize     | `### Description optimization proposals` + per-skill current/proposed; approval gate; stop |

---

## Failure Modes

| Symptom                                                | Likely cause                                        | Action                                                                                              |
| ------------------------------------------------------ | --------------------------------------------------- | --------------------------------------------------------------------------------------------------- |
| Hundreds of "Missing from routing" findings            | skill-architecture.md is partial / informal index   | Don't flood the report — cap "Missing from routing" at 20 entries and note the truncation.          |
| Every skill flagged as description drift               | Fuzzy match heuristic is too strict                 | Relax to first-8-words intent comparison; rerun.                                                    |
| `--apply` invoked without a prior drift report         | Out-of-order invocation                             | Refuse and ask for an audit run first.                                                              |
| skill-architecture.md not found                        | cwd has no routing doc (or wrong working dir)       | Degrade to a disk-only audit (enumerate skills + cross-ref scan); note it in the report. Never synthesize a routing doc. |
| MEMORY.md not found                                    | Fresh project, no auto-memory yet                   | Skip the MEMORY mismatch check; note in report.                                                     |

---

## Called By

- `/sync` (umbrella drift audit) — Phase 1 fan-out
- Standalone — manual invocation
