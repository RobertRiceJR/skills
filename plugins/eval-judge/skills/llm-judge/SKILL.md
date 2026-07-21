---
name: llm-judge
description: >
    Semantic skill-quality judge. Grades a Claude Code skill (or sweeps every skill in the
    current project) against six dimensions — D1 trigger accuracy, D2 description clarity /
    anti-shadowing, D3 body coherence & altitude, D4 portability, D5 reference integrity, D6
    self-containment — and returns per-dimension scores, a weighted confidence, and a triage
    flag for the weak ones. It SCORES; it does not fix — remediation stays with /skill-evolve,
    /skill-creator, or a human. Trigger accuracy (D1) is measured live via the skill-creator
    trigger-eval harness when a skill has evals/trigger_evals.json; otherwise it is judged
    statically from the description.
    Trigger: "judge this skill", "grade this skill", "score skill quality", "evaluate my skills",
    "which skills are weak", "skill quality report", "/llm-judge".
    Do NOT use to score Playwright specs or test suites (that was the previous target — see
    _archive/llm-judge-spec-version), to rank the ecosystem by health (/skill-scorecard), or to
    edit a skill (/skill-evolve, /skill-creator).
user_invocable: true
argument: '[skill-name | path | all] (default: all skills discoverable in the current project)'
---

# LLM Judge — Skill-Quality Evaluator

A semantic judge that grades the **quality of a skill** so a mixed-provenance collection can be
trusted. It **scores; it does not fix.** The criteria SSOT is [`dimensions.json`](dimensions.json);
the score anchors + shared grader frame are in [`skill-quality-rubric.md`](skill-quality-rubric.md).

> **Portability.** Fully project-agnostic — it grades whatever skills the current project exposes,
> from wherever they live (`.claude/skills/`, `~/.claude/skills/`, or `plugins/*/skills/`). The only
> optional dependency is the trigger-eval harness (the `skill-creator` scripts in this same
> `eval-judge` plugin); when it's unavailable, D1 degrades to a static read of the description.

---

## Two grading paths

1. **Interactive (default).** Claude *is* the judge. For each target skill, read its `SKILL.md`
   (and the supporting files a dimension needs), then score each dimension against the rubric
   using the shared grader frame. No external tooling required — works on any machine, no API key.
2. **Batch (optional).** For grading many skills headlessly, the promptfoo harness
   ([`promptfooconfig.yaml`](promptfooconfig.yaml) + [`claude-cli-provider.cjs`](claude-cli-provider.cjs),
   a keyless `claude -p` grader) can score composed artifacts. This is the scale path; the
   interactive path is the default and is what the phases below describe.

---

## Phase 0 — Scope

Resolve the target set from the argument:
- a **skill name** or **path** → that one skill.
- **`all`** or no argument → every directory containing a `SKILL.md` (case-insensitive) under the
  project's skills roots: `.claude/skills/*/`, `~/.claude/skills/*/`, and `plugins/*/skills/*/`.
  Exclude `_shared`, `_archive`, and non-skill folders.

State the resolved set and count before grading.

## Phase 1 — Gather, per skill

For each target skill, read:
- its `SKILL.md` (frontmatter + body) — always;
- `evals/trigger_evals.json` if present (enables the live D1 path);
- the specific supporting file a dimension needs (e.g. a `scripts/` file for D6, a referenced
  `_shared/` path for D5) — only when the dimension turns on it.

## Phase 2 — Score each dimension (D1–D6)

Apply [`skill-quality-rubric.md`](skill-quality-rubric.md) anchors, one dimension at a time, using
the shared grader frame (skeptical, score-only, full 0.0–1.0 scale). For each dimension emit
`{reason, score, pass}` where `pass = score ≥ threshold` (thresholds in `dimensions.json`).

**D1 — trigger accuracy** is the apex (voted ×3, weight 3):
- **If the skill has `evals/trigger_evals.json`** and the `skill-creator` harness is available, run
  the live trigger eval and use its pass rate as D1 (see the command below). This is the honest
  measure.
- **Otherwise** judge D1 statically from the description (trigger phrases present? boundary against
  siblings present?).

Live D1 command (run from the project root so the deployed skill is discoverable; MCP disabled):
```bash
# PYTHONPATH points at the skill-creator plugin dir; run from repo root.
python -m scripts.run_eval \
  --skill-path <path-to-skill> \
  --eval-set   <path-to-skill>/evals/trigger_evals.json \
  --runs-per-query 3 --num-workers 6 --timeout 75 --verbose
```
The `skill-creator` scripts carry the Windows-portability patches; no re-apply step is needed.

## Phase 3 — Roll up & flag

Per skill, compute the weighted confidence (weights in `dimensions.json`; D1 as the voted-×3 apex).
**Flag** any skill whose D1 or overall confidence falls below the `flag` floors — that is a triage
signal ("fix this first"), not the verdict. The honest per-dimension scores are the verdict.

## Phase 4 — Report

Output one table (sweep) or one block (single skill):

```
## Skill-Quality Judge — <date>

| Skill | D1 trig | D2 desc | D3 body | D4 port | D5 refs | D6 self | Conf | Flag |
| ----- | ------- | ------- | ------- | ------- | ------- | ------- | ---- | ---- |
| roast-me | 0.85 | 0.8 | 0.85 | 0.80 | 0.75 | 0.9 | 0.83 |  |
| skill-evolve | 0.75 | 0.8 | 0.85 | 0.70 | 0.65 | 0.7 | 0.74 | ⚑ |

**Weakest dimension across the set:** D5 reference integrity (mean 0.7).
**Flagged for triage:** skill-evolve (D5 dead sibling refs).
**One-line verdict per flagged skill**, each pointing at the specific weakness.
```

For a single skill, expand each dimension's one-sentence `reason`.

## Phase 5 — Record (optional)

If asked to persist, append the run to `runs/first-pass-<date>.md` in this skill's folder (the run
log; append-only). Do not edit any graded skill — this judge is read-only over its targets.

---

## What this skill does NOT do

- It does not fix skills. Report the scores; remediation is `/skill-evolve` or `/skill-creator`.
- It does not rank the ecosystem by health/importance — that's `/skill-scorecard`.
- It does not grade Playwright specs. That was the previous target; the spec-version rubric,
  golden set, and calibration stamp are preserved under `_archive/llm-judge-spec-version/`.
- It does not penalize clearly-labeled historical-provenance notes as dead references (D5).
