# Skill Eval & Triggering Harness — IMA 360 workflow

A thin project wrapper over the **skill-creator** activation-eval scripts. It answers one
question per skill: *does this skill's `description:` cause the model to trigger it for the
queries that should, and stay quiet for the queries that shouldn't?* — and, in loop mode,
*proposes a better description* when it doesn't.

This doc is the IMA-360 operating manual. The scripts themselves live in the managed
marketplace plugin; the Windows-portability patches that make them run here live in
[`../skill-creator-patches/`](../skill-creator-patches/README.md) (read that first).

---

## What lives where

| Thing | Location |
| --- | --- |
| Eval scripts (`run_eval.py`, `run_loop.py`, `improve_description.py`) | `~/.claude/plugins/marketplaces/anthropic-agent-skills/skills/skill-creator/scripts/` |
| Durable Windows patches (re-apply source) | `.claude/skills/_shared/skill-creator-patches/` |
| Per-skill eval sets | `.claude/skills/<skill>/evals/trigger_evals.json` |
| Pilot suites (this pass) | `three-amigos`, `ready-for-testing`, `ready-for-playwright` |

---

## Pre-flight (every time, before any eval run)

A marketplace refresh / plugin reinstall **reverts** the Windows patches. Re-apply them first
(PowerShell):

```powershell
$SC   = "$env:USERPROFILE\.claude\plugins\marketplaces\anthropic-agent-skills\skills\skill-creator\scripts"
$HERE = ".claude\skills\_shared\skill-creator-patches"
Copy-Item "$HERE\claude_proc.py","$HERE\run_eval.py","$HERE\improve_description.py","$HERE\utils.py" $SC -Force
python -m py_compile "$SC\run_eval.py" "$SC\run_loop.py" "$SC\improve_description.py"
```

If `py_compile` is clean, the harness is ready. (The bash equivalent is in the patches README.)

---

## Eval-set format

A flat JSON array. Each item needs exactly two fields; extra keys are ignored. **No top-level
metadata object** — the loader iterates the array and reads `item["query"]` / `item["should_trigger"]`.

```json
[
  { "query": "natural-language user request, NO slash command", "should_trigger": true },
  { "query": "a request that should route to a SIBLING skill instead", "should_trigger": false }
]
```

Seeding rules that make a good set:
- **Positives** = real phrasings of this skill's job (mine the skill's own `description:` trigger phrases).
- **Negatives** = phrasings that should route to an *adjacent* skill. The harness only checks whether
  *this* skill fired, so a negative that correctly fires a sibling counts as a pass. The most valuable
  negatives sit on lifecycle boundaries (e.g. for `three-amigos`: "the PR merged, derive TCs" → that's
  `ready-for-testing`).
- Aim for ~10 queries, roughly balanced. The loop's default `--holdout 0.4` stratifies by
  `should_trigger`, so keep ≥3 of each class or the train split starves.

---

## Mode 1 — Eval only (does the current description trigger correctly?)

Run from the **repo root** (so `find_project_root` finds `.claude/` and the deployed skill is
discoverable). PowerShell:

```powershell
$env:PYTHONPATH = "$env:USERPROFILE\.claude\plugins\marketplaces\anthropic-agent-skills\skills\skill-creator"
python -m scripts.run_eval `
  --skill-path .claude\skills\three-amigos `
  --eval-set   .claude\skills\three-amigos\evals\trigger_evals.json `
  --runs-per-query 3 --num-workers 6 --timeout 75 --verbose
```

Output: JSON to stdout with per-query `pass` + a `summary { total, passed, failed }`. `--verbose`
prints a `[PASS]/[FAIL] rate=2/3 expected=true: <query>` line per query to stderr.

## Mode 2 — Optimize loop (propose a better description)

Same invocation with `run_loop` + a required `--model`. It evals, asks the model to improve the
description from the failures, re-evals on a held-out test split, and reports the best description
found. It opens a live HTML report in the browser.

```powershell
$env:PYTHONPATH = "$env:USERPROFILE\.claude\plugins\marketplaces\anthropic-agent-skills\skills\skill-creator"
python -m scripts.run_loop `
  --skill-path .claude\skills\three-amigos `
  --eval-set   .claude\skills\three-amigos\evals\trigger_evals.json `
  --model claude-opus-4-8 --max-iterations 5 --holdout 0.4 `
  --runs-per-query 3 --num-workers 6 --timeout 75 --verbose
```

Output JSON carries `original_description`, `best_description`, `best_score` (test-split), and the
full per-iteration `history`. **The loop never writes the skill** — it proposes. Applying the
`best_description` to the skill's `skill.md` frontmatter is a separate, human-approved edit.

---

## Caveats (read before trusting a result)

- **In-project isolation is imperfect.** Because the run happens inside this repo, the *real*
  deployed skill of the same name is discoverable, so a `--description` override is not perfectly
  isolated — the harness measures the **deployed** description. For an honest A/B of a *proposed*
  description, temporarily move the real skill out of discovery, or accept that Mode 2's in-loop
  scores reflect the proposal competing against its own deployed twin.
- **Windows file casing.** The scripts check for `SKILL.md`; project skills are `skill.md`. The
  Windows case-insensitive filesystem resolves this automatically — no rename needed. On a
  case-sensitive FS this would fail.
- **MCP is disabled during runs** (`--mcp-config <empty> --strict-mcp-config`, baked into the
  patches). The eval needs only the Skill tool, and booting the MCP fleet was the original
  zero-output-timeout blocker. Don't remove it.
- **`run_loop` requires `--model`** (no default); `run_eval` defaults to the user's configured model.
- **Cost.** Each query × `runs-per-query` × iterations is a real `claude -p` call. A 10-query set at
  3 runs × 5 iterations ≈ 150 calls. Keep pilot sets small.

---

## How `/sync-skills --optimize` uses this

`/sync-skills` (report-only by default) can call Mode 2 for any skill that has an
`evals/trigger_evals.json`. It surfaces the proposed `best_description` in the drift report as a
**suggestion**, gated behind the same explicit-approval contract as `--apply` — it never rewrites a
`skill.md` description on its own. Skills without an eval set are skipped with a note. See
`_shared/skill-architecture.md` § Skill Eval & Triggering.
