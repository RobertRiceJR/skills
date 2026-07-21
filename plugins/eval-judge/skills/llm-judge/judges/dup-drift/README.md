# Duplication-Drift Judge

> **Status: preserved reference implementation — not runnable standalone here.** This is the
> IMA-origin secondary judge. It requires the `run-dup-sweep` orchestration harness (which lived in
> the old project's `scripts/llm-judge/` and is **not** shipped in this marketplace) and a project
> that follows the `_shared/` canonical-source + inline-copy convention. Its golden set is IMA QE
> domain data, kept as worked examples of the drift concept. The **primary, runnable** judge is the
> parent skill-quality judge in [`../../`](../../SKILL.md); use that. Rebuild the harness (or port it
> to grep-based shingle containment) before relying on this one.

Detects the one drift class nothing else checks: the **self-containment invariant** — skills
duplicate `_shared/` context instead of importing it, and those inline copies go stale when the
canonical source changes.

## How it works

1. **Markerless candidate discovery** (`run-dup-sweep.ts`, no LLM): for each skill, compare its body
   against the canonical docs it cites (`sharedRefs` in `skill-graph.json`) plus a small CORE set,
   using 8-word-shingle **containment**. Pairs ≥ `--threshold` (default 0.12) become candidates.
   Paraphrased/terser copies score low on purpose — 0.12 surfaces real structural copies without
   flooding the judge.
2. **Judge** (promptfoo `echo` + the rubric here): each `(canonical block, inline copy)` pair is
   scored on DD1 factual-consistency (apex, ×3 votes), DD2 currency, DD3 carry-forward-risk.
   HIGH = still in sync; LOW = stale/contradictory. Terser is fine; only contradictions/stale claims
   lose points. **Score-only — never edits a skill.**

## Grader auth

The sweep/calibrate steps call Anthropic via promptfoo, so they need credentials at runtime
(`apiKeyRequired: false` only skips promptfoo's *startup* check — the grading call still needs a key).
Inside an active Claude Code session that carries Anthropic creds it works keyless; **in a bare
terminal `export ANTHROPIC_API_KEY=...` (PowerShell: `$env:ANTHROPIC_API_KEY="…"`) for the run.**
Same requirement as the spec-quality judge. Discovery (`--list` / `--dry`) is keyless.

## Keyless grading (Agent-dispatch — no API key, the default in this env)

The promptfoo path needs an Anthropic key. The **keyless** path mirrors `/spec-review`: the Node script
does the keyless mechanical parts (candidate discovery, pair emission, gate math) and the **Claude Code
session grades via subagents** — no key, no promptfoo. This is what `/skill-evolve` and `/sync` use here.

**Sweep (flag stale copies):**
1. `node scripts/llm-judge/run-dup-sweep.ts --emit-pairs [--skill X]` → JSON `{mode, flagFloorDD1, pairs:[{id, canonical, inline, …}]}`.
2. For each pair, the session dispatches a subagent per dimension (DD1 ×3, DD2, DD3) with the grader
   frame from `promptfooconfig.yaml` + that dimension's `criteria` from `dimensions.json`, returning
   `{score, reason}` only. Average DD1's three votes.
3. Flag any pair whose mean DD1 < `flagFloorDD1`. Report; never auto-edit a skill.

**Calibrate (trust gate, keyless):**
1. `node scripts/llm-judge/run-dup-sweep.ts --emit-pairs --golden` → the 16 labelled pairs (with `humanScore`).
2. The session grades each **blind to `humanScore`**, computes overall MAE vs the labels.
3. `node scripts/llm-judge/run-dup-sweep.ts --stamp --mae <computed> --grader <model>` writes
   `calibration-stamp.json` (PASS if MAE ≤ 0.25) — same gate the promptfoo path produces.
   ⚠ Caveat: the seed labels were written by Claude, so a keyless PASS measures grader-vs-those-labels,
   not grader-vs-Robert — have Robert spot-check a few `humanScore`s for full independence.

## Commands

```
npm run judge:dup-sweep                              # full sweep via promptfoo (needs ANTHROPIC_API_KEY)
node scripts/llm-judge/run-dup-sweep.ts --emit-pairs  # KEYLESS feed for session/subagent grading
node scripts/llm-judge/run-dup-sweep.ts --list       # candidate pairs only, NO LLM
node scripts/llm-judge/run-dup-sweep.ts --skill X    # one skill (used by /skill-evolve content checks)
node scripts/llm-judge/run-dup-sweep.ts --dry        # write cases, skip the eval
npm run judge:dup-calibrate                          # golden-set MAE on Opus → calibration-stamp.json (the /sync gate)
```

## Files

- `dimensions.json` — DD1/DD2/DD3 rubric SSOT.
- `promptfooconfig.yaml` — doc-reviewer grader frame (NOT the Playwright one).
- `golden/labels.jsonl` — human-labelled pairs `{id, canonical, inline, dimension, humanScore}`.
  **Seeded with 3 illustrative rows — expand to 10–14 (in-sync · terser-OK · stale) before trusting.**
- `calibration-stamp.json` *(generated, committed)* — MAE gate + rubric hash; `/sync` flags staleness.
- `generated-cases.json`, `results/` *(generated, gitignored)*.

## Status

**PROVISIONAL until calibrated.** Run `npm run judge:dup-calibrate` after expanding the golden set;
the sweep prints a PROVISIONAL banner until a `calibration-stamp.json` with gate PASS exists.
