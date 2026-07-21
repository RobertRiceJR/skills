# robert-skills — a local Claude Code skill marketplace

A centralized, portable home for Robert's Claude Code skills. The skills live here once and install
into **any repo on this machine** as plugins. Every skill resolves paths and commands from the
**current working directory** and degrades gracefully when a project-specific anchor is absent — so
`session-review` works everywhere, and `roast-me` runs against whatever repo you point it at.

## The four plugins

| Plugin | Install where | Skills |
| --- | --- | --- |
| **universal-core** | everywhere | `session-review`, `todo`, `condense-claude-md`, `sync-memory`, `comms-coach`, `claude-architect` (+ the session-stats hook) |
| **qe-toolkit** | QE / Playwright repos | `roast-me`, `technical-due-diligence`, `devils-advocate` |
| **skill-ops** | repos where you curate a skill ecosystem | `sync-skills`, `skill-evolve`, `skill-scorecard` |
| **eval-judge** | wherever you author/grade skills | `llm-judge` (skill-quality evaluator), `skill-creator` (create/optimize skills, Windows-patched) |

## Install into another repo

```
# one-time: register this repo as a marketplace
/plugin marketplace add C:\Users\terri\Repos\skills-1

# then install whichever plugins that repo needs
/plugin install universal-core@robert-skills
/plugin install qe-toolkit@robert-skills        # only in QE/Playwright repos
```

Installed skills are invoked like any other — `/session-review`, `/roast-me`, `/llm-judge`, … — and
run against the repo you're in.

> Developing **in this repo**: the marketplace is registered via `.claude/settings.local.json`
> (gitignored, machine-specific) and the four plugins are enabled via committed `.claude/settings.json`,
> so all skills are discoverable here without a manual install step.

## The portability contract

Every skill obeys one rule: **resolve from the current project; if an anchor isn't there, degrade —
never hard-stop.** A skill that wants a project's `_shared/skill-architecture.md`, a `TODO.md`, an
`npm run type-check`, or a sibling `/skill` uses it *when present* and skips it (saying so) when not.
Skills carry a **Portability** note where this matters. Nothing references the old project in a way
that breaks: no hardcoded user paths, no `../../../` escapes out of the repo, no required `npm run`
with no fallback.

## Evaluating skills

The `eval-judge` plugin grades skill quality on six dimensions (D1 trigger accuracy → D6
self-containment). Run `/llm-judge` to sweep every discoverable skill, or `/llm-judge <name>` for
one. Trigger accuracy is measured live via the `skill-creator` harness where a skill ships an
`evals/trigger_evals.json`. See [plugins/eval-judge/skills/llm-judge/README.md](plugins/eval-judge/skills/llm-judge/README.md)
and the latest run in [plugins/eval-judge/skills/llm-judge/runs/](plugins/eval-judge/skills/llm-judge/runs/).

## `_archive/` — nothing is deleted

Retired or old-project-specific material is **moved to [`_archive/`](_archive/)**, never deleted:
the previous spec-quality version of the judge, IMA-360 run artifacts, superseded hooks, and count
baselines. If something looks missing, it's in `_archive/`.

## Layout

```
.claude-plugin/marketplace.json   # lists the 4 plugins
plugins/<bucket>/
  .claude-plugin/plugin.json
  skills/<skill>/SKILL.md          # every skill's entry file is SKILL.md
  hooks/                           # universal-core only
_archive/                          # moved-not-deleted material
CLAUDE.md                          # operating guide for working in this repo
```
