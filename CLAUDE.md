# CLAUDE.md — skills-1

Robert's centralized skill marketplace. Skills live here once and install into other repos on this
machine as plugins. User-facing install/usage is in [README.md](README.md); this file is the
operating guide for **working in this repo**.

## What this repo is

A Claude Code **plugin marketplace** (`robert-skills`), not a project with an app. The deliverable is
the skills themselves. Four themed plugins under `plugins/`, each installable independently.

## Non-negotiable conventions

- **Portability contract.** Every skill resolves paths/commands from the **current working
  directory** and **degrades gracefully** when a project-specific anchor (`_shared/*`, a `TODO.md`,
  an `npm run …`, a sibling `/skill`) is absent — it uses the anchor *when present* and skips it
  (saying so) otherwise. **Never** add a hardcoded user path (`C:\Users\<name>\…`), a `../../../`
  escape out of the repo, or a required external command with no fallback. When a skill has a
  project-specific dependency, express it behind a **Portability** note (see `session-review`,
  `roast-me`, `skill-evolve` for the pattern).
- **`_archive/` is append-only; never delete.** Retiring or replacing anything means **moving it to
  `_archive/`**. This is a hard rule from the repo owner.
- **Entry file is `SKILL.md`** (uppercase) for every skill — the plugin convention and what the
  `skill-creator` eval scripts look for.
- **JSON manifests must stay valid** — `.claude-plugin/marketplace.json` and each
  `plugins/*/.claude-plugin/plugin.json`. Validate after edits.

## Layout

```
.claude-plugin/marketplace.json      # lists the 4 plugins (name: robert-skills)
plugins/
  universal-core/  session-review, todo, condense-claude-md, sync-memory, comms-coach,
                   claude-architect  + hooks/ (session-end-stats, memory-inject, log-skill-run, validate-sql)
  qe-toolkit/      roast-me, technical-due-diligence, devils-advocate
  skill-ops/       sync-skills, skill-evolve, skill-scorecard
  eval-judge/      llm-judge (skill-quality judge), skill-creator (Windows-patched harness)
_archive/          moved-not-deleted material (old spec-judge, IMA run artifacts, count baselines)
.claude/           settings.json (committed: enables the 4 plugins) + settings.local.json (gitignored: marketplace path)
```

## Working in here

- **Skills are discoverable locally** via `.claude/settings.json` (enables the plugins) +
  `.claude/settings.local.json` (registers this repo as the marketplace). The `.local` file holds the
  machine-specific absolute path and is gitignored.
- **Editing a skill's description** changes its triggering — re-grade with the evaluator (below)
  rather than eyeballing it.
- **Changing a skill's contract/name** can ripple to sibling references — use `/skill-evolve` (it
  computes blast radius; degrades to a grep-based sweep here since there's no `skill-graph.json`).

## Hooks (universal-core plugin)

Wired in `plugins/universal-core/hooks/hooks.json`:
- `session-end-stats.ps1` — **universal**; writes per-session cost/token stats to
  `~/.claude/session-stats/` on SessionEnd.
- `memory-inject.ps1` / `log-skill-run.ps1` — **dormant**; derive their memory root from
  `CLAUDE_PROJECT_DIR` and only fire on Zephyr/MSSQL/Playwright/Atlassian MCP tools. No-ops until
  those MCP servers exist in a project. (No hardcoded old-project path.)
- `validate-sql.ps1` — warn-only DML/DDL gate on MSSQL MCP calls; harmless where absent.

## Evaluating skills

`eval-judge/llm-judge` grades skill quality on six dimensions (D1 trigger accuracy → D6
self-containment); `dimensions.json` is the SSOT, `skill-quality-rubric.md` the anchors.
- Interactive: `/llm-judge` (sweep) or `/llm-judge <name>`.
- Live D1 (where an `evals/trigger_evals.json` exists), from repo root:
  ```bash
  PYTHONPATH=plugins/eval-judge/skills/skill-creator \
    python -m scripts.run_eval --skill-path <skill> --eval-set <skill>/evals/<file> \
    --runs-per-query 3 --num-workers 6 --timeout 45 --verbose
  ```
- Latest grades: `plugins/eval-judge/skills/llm-judge/runs/`. Scores are **provisional until the
  golden set is calibrated** on the current rubric version.

## Skills with live trigger-eval sets

`roast-me`, `comms-coach`, `session-review`. The rest are graded statically (D1) + interactively
(D2–D6). Seed an `evals/trigger_evals.json` (`[{query, should_trigger}]`) to add a skill to the live
D1 path.
