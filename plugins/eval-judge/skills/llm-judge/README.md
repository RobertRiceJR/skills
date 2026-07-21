# Skill-Quality LLM Judge

A semantic LLM judge that grades the **quality of a Claude Code skill** — does its description
trigger accurately? is its body coherent? is it portable and dead-reference-free? — so a collection
of mixed provenance can be trusted. It **scores; it does not fix.** Remediation stays with
`/skill-evolve`, `/skill-creator`, or a human.

> Retargeted from a Playwright **spec**-quality judge. The spec-version rubric, golden set, and
> calibration stamp are preserved under `_archive/llm-judge-spec-version/`.

## Files

| File | Role |
| --- | --- |
| [`SKILL.md`](SKILL.md) | The invocable judge — the interactive (Claude-as-judge) grading workflow |
| [`dimensions.json`](dimensions.json) | **Criteria SSOT** — the six dimensions, thresholds, weights, votes |
| [`skill-quality-rubric.md`](skill-quality-rubric.md) | Prose: score anchors + the shared grader frame |
| [`golden/labels.jsonl`](golden/labels.jsonl) | Hand-labeled calibration set (skills across a quality spread) |
| [`promptfooconfig.yaml`](promptfooconfig.yaml) | Optional batch harness (echo provider + shared `rubricPrompt`) |
| [`claude-cli-provider.cjs`](claude-cli-provider.cjs) | Keyless promptfoo grader — shells to `claude -p` (subscription auth, no API key) |
| [`empty-mcp.json`](empty-mcp.json) | Empty MCP config → grader runs with no MCP servers (per-call isolation) |
| `judges/dup-drift/` | Secondary judge: duplication-drift between a skill's inline copies and its canonical sources |
| `runs/` | Judge run logs (append-only) |

## The six dimensions

| Dim | Name | Weight | What it asks |
| --- | --- | --- | --- |
| **D1** | Trigger accuracy | 3 (apex, ×3) | Does the `description:` fire for its own requests and stay quiet for siblings'? |
| **D2** | Description clarity / anti-shadowing | 2 | Specific, scoped, non-overlapping with siblings? |
| **D3** | Body coherence & altitude | 2 | Phases match the promise; gates enforced; right altitude? |
| **D4** | Portability | 2 | Resolves from cwd + degrades gracefully; no hardcoded/unguarded deps? |
| **D5** | Reference integrity | 2 | Live sibling/file refs; no `../../../` escapes; no dead handoffs? |
| **D6** | Self-containment | 1 | Runs from its own folder + the target project? |

## Running it

**Interactive (default) — no setup, no API key:**
```
/llm-judge                 # sweep every discoverable skill
/llm-judge roast-me        # grade one skill
```
Claude reads each `SKILL.md` and scores it against the rubric. See [`SKILL.md`](SKILL.md) for the
phase-by-phase workflow.

**Live D1 (trigger accuracy)** — where a skill has `evals/trigger_evals.json`, the judge measures
D1 with the `skill-creator` trigger-eval harness in this same `eval-judge` plugin:
```bash
# from the project root, with the skill discoverable
PYTHONPATH=<path-to>/plugins/eval-judge/skills/skill-creator \
  python -m scripts.run_eval \
    --skill-path plugins/qe-toolkit/skills/roast-me \
    --eval-set   plugins/qe-toolkit/skills/roast-me/evals/trigger_evals.json \
    --runs-per-query 3 --num-workers 6 --timeout 75 --verbose
```
Auth: the grader authenticates via your **active Claude Code session** (no `ANTHROPIC_API_KEY`). In
CI, `export CLAUDE_CODE_OAUTH_TOKEN=...` (from `claude setup-token`) or `ANTHROPIC_API_KEY`.

**Batch (optional, scale path):** the promptfoo config grades composed artifacts through the keyless
`claude-cli-provider.cjs`. Requires `npm i -D promptfoo`. Use only when grading many skills
headlessly; the interactive path is the default.

## Calibration is not optional

LLMs judging code run 52–78% accurate on benchmarks — a cautionary prior. The golden set is how we
learn whether *this* rubric separates strong from weak skills on *these* skills. Hand-label a spread
and require the judge to reproduce the ordering before its scores gate anything.
