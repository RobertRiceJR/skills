# skill-creator harness — patched mirror (cross-platform / Windows)

These are **git-tracked mirrors** of four files from the `skill-creator` plugin's `scripts/`
directory, patched to make the activation-eval harness run on Windows (and any MCP-heavy repo).

**Why this exists:** `skill-creator` is installed from the managed marketplace
`~/.claude/plugins/marketplaces/anthropic-agent-skills/` — a git clone of
`https://github.com/anthropics/skills.git`. The patches are applied **in place** in that
installed copy, but a plugin update / marketplace refresh (git pull / reinstall) **reverts
them**. These mirrors are the durable copy; re-apply after any reinstall.

**Installed location (target of re-apply):**
`~/.claude/plugins/marketplaces/anthropic-agent-skills/skills/skill-creator/scripts/`

## What was patched (all four files, 2026-06-01)

| File | Change |
| --- | --- |
| `claude_proc.py` | **NEW** shared helper. `resolve_claude()` — spawn the real `claude.cmd`/`.exe` launcher via `shutil.which` (a bare `claude` is a shell shim `CreateProcess` can't exec → WinError 2). `empty_mcp_config()` — writes a `{"mcpServers":{}}` temp file so `claude -p` + `--strict-mcp-config` skips booting the project's MCP fleet (that boot latency was why headless runs timed out with zero output). |
| `run_eval.py` | Spawn via `resolve_claude()`; **thread+queue reader** replacing `select.select()` (Unix-only on pipes → WinError 10038); `--mcp-config <empty> --strict-mcp-config`; trigger detection matches the skill's **base name** (the model emits `{"skill":"session-review"}`, not the synthetic unique name — the old check was backwards → all-False); utf-8 I/O (stdout/stderr reconfigure, command-file write, eval-set read). |
| `improve_description.py` | Spawn via `resolve_claude()`; `--mcp-config <empty> --strict-mcp-config`; utf-8 on the `subprocess.run` (its prompt embeds the SKILL.md body), on transcript write + eval/history reads, and stdout/stderr reconfigure. (Uses `subprocess.run` to completion — no `select` path to fix.) |
| `utils.py` | `parse_skill_md` reads `SKILL.md` with `encoding="utf-8"` (Windows cp1252 crashes on em-dashes). |

## Re-apply after a plugin reinstall

```bash
SC=~/.claude/plugins/marketplaces/anthropic-agent-skills/skills/skill-creator/scripts
HERE=.claude/skills/_shared/skill-creator-patches
cp "$HERE"/claude_proc.py "$HERE"/run_eval.py "$HERE"/improve_description.py "$HERE"/utils.py "$SC"/
```

Then sanity-check: `python -m py_compile "$SC"/*.py` and a trivial
`claude.cmd -p "say hi" --mcp-config <empty> --strict-mcp-config` round-trip.

## Run the eval (any skill, from the repo root)

```bash
PYTHONPATH=~/.claude/plugins/marketplaces/anthropic-agent-skills/skills/skill-creator \
  python -m scripts.run_eval --skill-path <skill-dir> --eval-set <eval.json> \
  --runs-per-query 3 --num-workers 6 --timeout 75 --verbose
```

Run from the project root that registers the skill (so the deployed skill is discoverable; the
eval detects the model invoking it by base name). Upstream fix not yet contributed back to
`anthropics/skills`; if/when it is, delete this mirror.
