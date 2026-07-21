---
name: sync-memory
description: >
    MEMORY.md pointer health audit. Walks every link in the project MEMORY.md
    index, resolves it against the filesystem, and flags dead links plus orphan
    memory files (on disk but not indexed). Handles both absolute and relative
    paths — the ../../../../spikes/INDEX.md pattern is fragile and a known drift
    surface. Default mode is report-only; --apply removes confirmed-dead pointers
    and offers to add confirmed-orphan files to the index. Prompts per item.
user_invocable: true
argument: '[mode]  # optional — empty (full audit) | --apply (act on the most recent report)'
---

# MEMORY.md Pointer Health Sync

Validates the integrity of the project auto-memory index. Two-phase:
**audit first → drift report → approval gate → fix second.**

Called by `/sync` as part of the umbrella drift audit. Can also be invoked standalone.

---

## When to use this skill

- After reorganizing the `memory/` directory (renaming files or subfolders).
- When a memory file shows up in Glob results that you don't recognize from MEMORY.md.
- As Phase 1 of a `/sync` run.
- After major Claude Code upgrades that change the memory path format.

**Do NOT use this skill for:**

- Authoring new memories — that's a manual write task.
- Reorganizing memory content — this skill checks link integrity, not the contents.
- Validating CLAUDE.md links — those live elsewhere; use `/condense-claude-md` for CLAUDE.md hygiene.

---

## Step 1 — Parse Mode

| Argument    | Mode                                              |
| ----------- | ------------------------------------------------- |
| _(empty)_   | Audit all MEMORY.md links + scan for orphans      |
| `--apply`   | Act on the most recent report (must come second)  |

`--apply` requires a drift report in the same session. If no report is in context, refuse and ask for an audit run first.

---

## Step 2 — Locate MEMORY.md

This is a GLOBAL skill — derive the auto-memory path from the **current working directory**, never a
hardcoded project. Claude Code stores per-project memory at
`~/.claude/projects/<encoded-cwd>/memory/MEMORY.md`, where `<encoded-cwd>` is the absolute cwd with the
drive letter lowercased and every `:` `\` `/` `_` replaced by `-`
(e.g. `C:\Users\me\IGS_360\my_repo` → `c--Users-me-IGS-360-my-repo`).

1. Compute `<encoded-cwd>` from the absolute cwd and try
   `~/.claude/projects/<encoded-cwd>/memory/MEMORY.md` first.
2. **Fallback** (if that exact path isn't found — the encoding rule can drift across Claude Code
   versions): Glob `**/MEMORY.md` under `~/.claude/projects/`, prefer the directory whose name contains
   the cwd's basename; if several match, pick the most recently updated.
3. If still none found, stop with `No project MEMORY.md found — nothing to audit`.

The memory root is the directory containing MEMORY.md. Remember it as `MEM_ROOT`.

---

## Step 3 — Extract Links

Walk MEMORY.md line by line. For every `[Title](path)` pattern in markdown bullets, capture:

- `title` — the link text (e.g., "General Preferences")
- `raw_path` — the path inside parens (e.g., `general.md` or `../../../../spikes/INDEX.md`)
- `section` — the most recent `##` heading above the line
- `line_no` — line number in MEMORY.md

Skip:

- Links inside code blocks
- External URLs (`http://`, `https://`)
- Anchors-only links (`#section-name`)

---

## Step 4 — Resolve Every Link

For each captured link, compute the resolved absolute path:

| Pattern                  | Resolution                                                            |
| ------------------------ | --------------------------------------------------------------------- |
| `file.md`                | `MEM_ROOT/file.md`                                                    |
| `subdir/file.md`         | `MEM_ROOT/subdir/file.md`                                             |
| `../path`                | Resolved relative to MEM_ROOT, normalized                             |
| `C:/...` or `/abs/...`   | Absolute path used as-is                                              |

Test existence with a Read (catching not-found errors) or Glob. Mark each link:

- **OK** — file exists at resolved path.
- **DEAD** — file does not exist; capture the resolved path attempted.
- **AMBIGUOUS** — relative path traverses outside `MEM_ROOT` AND target does not exist; could be intentional (cross-project pointer) or broken. Flag separately.

---

## Step 5 — Find Orphans

Glob every `.md` file under `MEM_ROOT` (recursive):

```
Glob: <MEM_ROOT>/**/*.md
```

Exclude MEMORY.md itself.

For each found file, check whether its path appears in the link table from Step 3 (either by exact path or by basename match against a `[Title](relative-path)` link).

Files not referenced anywhere in MEMORY.md = **orphans**.

Note: it's legitimate for some subdirectories (e.g. nested topic folders) to be indexed only via a "see also" link, not directly. If MEMORY.md links to a parent INDEX.md and the orphan lives in that subtree, treat it as **soft-orphan** (mention but don't recommend deletion).

---

## Step 6 — Report Drift

```
## MEMORY.md Pointer Health Report — <YYYY-MM-DD>

### Dead links (N)
| Line | Section | Title | Resolved path attempted |
| ---- | ------- | ----- | ----------------------- |
| 14   | Domain  | Foo   | <MEM_ROOT>/domain/foo.md (NOT FOUND) |

### Ambiguous relative links (N)
| Line | Title | Raw path | Notes |
| ---- | ----- | -------- | ----- |
| 47   | Spike | ../../../../spikes/INDEX.md | Traverses outside MEM_ROOT; target not found |

### Orphan files (N)
- <MEM_ROOT>/domain/orphan1.md  (not referenced in MEMORY.md)
- <MEM_ROOT>/tools/orphan2.md   (not referenced in MEMORY.md)

### Soft-orphans (N)
- <MEM_ROOT>/some-subtree/file.md  (parent dir indexed via INDEX.md)

---

### Summary
- Links checked:       N
- Dead links:          N
- Ambiguous links:     N
- Files on disk:       N
- Hard orphans:        N
- Soft orphans:        N
```

If no findings: report `## MEMORY.md is clean — N links and N files verified <date>` and stop.

---

## Step 7 — Approval Gate

After the report, stop and state:

> Review the report above. Run `/sync-memory --apply` to walk each finding interactively, or name specific findings to act on. Apply mode prompts for each: remove dead pointer, add orphan to index, leave alone.

Do not touch MEMORY.md until the user responds.

---

## Step 8 — Apply Approved Fixes

Walk each finding from the report. For each, prompt the user with three options:

| Finding type        | Prompt                                                              | Yes action                                                                                                          |
| ------------------- | ------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------- |
| Dead link           | `Remove dead pointer "<title>" at line <n>?`                        | Edit MEMORY.md — delete the bullet line. If the section becomes empty, leave it; do not delete section headers.     |
| Ambiguous link      | `Update or remove ambiguous link "<title>" at line <n>?`            | Prompt for a new path or removal; apply via Edit.                                                                   |
| Hard orphan         | `Add "<basename>" to MEMORY.md under section <suggested-section>?`  | Read the orphan file's first heading or title; insert a new bullet at the end of the suggested section.             |
| Soft orphan         | (Skipped by default — only acted on if user explicitly names them)  | Same as hard orphan.                                                                                                |

For each action taken, log: `✓ <action> — <line/file>`.

Suggest section assignment for orphans by matching the file's parent directory name against MEMORY.md section headings (e.g. file in `tools/` → `## Tool Quirks`).

---

## Step 9 — Verify

After applying, re-read MEMORY.md and:

1. Confirm every previously-dead link is now gone.
2. Confirm every newly-added orphan has a bullet in the index.
3. Re-Glob the memory tree and recompute the orphan count.

Report:

```
## Verification
- Dead links removed:   N
- Orphans added:        N
- Remaining orphans:    N
- MEMORY.md line count: <before> → <after>
```

---

## Output Format Summary

| Phase                  | Output                                                                       |
| ---------------------- | ---------------------------------------------------------------------------- |
| Step 6 — drift report  | `## MEMORY.md Pointer Health Report — <date>` + per-category tables + summary |
| Step 7 — approval gate | One-line prompt; stop                                                        |
| Step 8 — apply         | Per-finding one-liner: `✓ <action>`                                          |
| Step 9 — verify        | Verification block                                                           |

---

## Failure Modes

| Symptom                                          | Likely cause                                      | Action                                                                                                       |
| ------------------------------------------------ | ------------------------------------------------- | ------------------------------------------------------------------------------------------------------------ |
| MEMORY.md not found at the documented path       | Project hash changed, or fresh setup              | Glob for `**/MEMORY.md` under `~/.claude/projects/`; if multiple, pick most-recently-updated and warn.       |
| Every link reports DEAD                          | Working directory wrong, or MEM_ROOT misresolved  | Stop. Re-confirm MEM_ROOT before continuing.                                                                 |
| Hundreds of orphan findings                      | A bulk dump landed in memory/ without indexing    | Cap orphan report at 30 entries; tell user to consider a bulk re-organize before applying one-by-one.        |
| Relative link traverses 5+ levels (`../../../../`) | User-level resource intentionally outside project | Treat as **ambiguous**, not dead, even if target exists — it's a fragile pattern worth surfacing regardless. |

---

## Called By

- `/sync` (umbrella drift audit) — Phase 1 fan-out
- Standalone — manual invocation
