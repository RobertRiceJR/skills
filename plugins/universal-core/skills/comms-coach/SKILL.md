---
name: comms-coach
description: >
  Analyzes Robert's own Claude Code communication style from this project's session transcripts and produces a
  dated, evidence-based coaching report — quantified linguistic trends plus a calibrated qualitative read with
  1–2 structure pointers. Use when he wants feedback on how he talks to Claude, his voice/dictation patterns,
  whether his habits are improving over time, or a "communication style report." Trigger phrases: "analyze my
  communication style", "comms coach", "how am I structuring my sentences", "how do I structure my sentences
  when I talk to claude", "feedback on my voice messages", "am I getting better at dictation", "/comms-coach".
  NOT for code review (/roast-me), cost/usage (/codeburn), or stand-ups (/dsu).
user_invocable: true
argument: '(optional) a focus area or date range to scope the coaching report; omit for the full session surface'
---

# comms-coach

Two-layer self-coaching tool over Robert's **own** session transcripts for THIS project. Layer 1 is a
deterministic, zero-model trend engine; Layer 2 is a calibrated LLM coaching read. Output is a self-contained
dated HTML report. Read-only against transcripts; writes only inside this skill folder and `.claude/analysis/`.

**Privacy:** mines only genuine human turns (his words). Tool results, system-reminders, and slash-command
machinery are filtered out by `analyze.mjs`. Nothing leaves the machine.

## Data source

- Session transcripts: `~/.claude/projects/<this-project>/*.jsonl`, auto-resolved by matching the `cwd` field
  to the current repo (no hardcoded path). Top-level files only — `subagents/` excluded.
- `analyze.mjs` is dependency-free Node. The verified genuine-human-turn predicate, metric definitions, and the
  voice classifier all live in that file — read it before changing any metric.
- **Injection exclusions (Pattern 37):** the `user` role is overloaded — beyond tool results it carries
  harness-injected content that is NOT human speech. The predicate/`clean()` drop: skill-invocation bodies
  (`Base directory for this skill:`), context-compaction summaries (`This session is being continued…`),
  and `<ide_opened_file>`/`<task-notification>`/`<system-reminder>`/`<ide_selection>` spans. Sanity gate:
  if voice-likely `avg_words` jumps implausibly (≫ ~500) or a voice turn opens with one of those markers, a
  new injection type is leaking — add an exclusion. Known residual: pasted prompt templates count as turns
  (user-authored, distort word-count not per-word rates).

---

## Phase 0 — Layer 1 (always run first)

```bash
node .claude/skills/comms-coach/analyze.mjs            # full history
node .claude/skills/comms-coach/analyze.mjs --since 2026-06-01   # window
```

Emits to `.claude/analysis/`: `comms-coach-metrics-<date>.json` (overall + per-month/week buckets with
deltas, voice-likely share, split confidence) and `comms-coach-sample-<date>.json` (≈25 most-recent
voice-likely cleaned turns — Layer 2's evidence). Appends one line to `runs.jsonl`. Read both emitted files
plus the stdout summary before proceeding.

**Sanity gates before trusting the run:** genuine turns ≈ 1–5% of total lines; sample turns are real messages
with **zero** tool-result/reminder leakage; voice-likely turns score ≥ 2. If any fails, stop — the parser
drifted (see the `parentUuid` foot-gun documented in `analyze.mjs`).

## Phase 1 — Calibration gate (first run, or `--recalibrate`)

Layer 2's read is NOT trusted until it passes calibration against the human baseline
`golden/2026-06-17-byhand.md`. Run this once; record the result.

1. Run Layer 1 over a window that **includes 2026-06-17** (`--since 2026-06-01`).
2. Produce the Phase-2 coaching read on that window.
3. Score it against the golden rubric:
   - **Recall** — independently surfaces all THREE golden habits (tag-question checkpointing; front-loaded
     hedging; directive-mode strength).
   - **Precision** — asserts no pattern absent from the evidence.
   - **Anti-flattery** — includes ≥1 genuinely unflattering finding AND cites ≥2 verbatim quotes.
4. Write `calibration-<date>.md` with PASS/FAIL + per-check notes. On **FAIL**, tune the Phase-2 prompt below
   and re-run. Do **not** emit a trusted report until a PASS is recorded.

If a prior `calibration-*.md` with PASS exists and `--recalibrate` was not passed, skip to Phase 2.

## Phase 2 — Coaching read (Layer 2)

Read `comms-coach-metrics-<date>.json` + `comms-coach-sample-<date>.json`. Produce, grounded ONLY in that
evidence:

- **Profile** — his current linguistic fingerprint from the voice-likely sample + `voiceOverall` (the
  voice-only aggregate). Name habits; back each with a metric and ≥1 verbatim quote (e.g. "tag-question
  checkpointing — `tagQ` 5–6 per long turn: 'best by margin. Right?'").
- **Strengths** — what's working, **every item tied to a metric or quote** (e.g. directive clarity ←
  `directive_per_turn`; reasoning depth ← `avg_words`; lexical range ← `mean_ttr`). An unbacked strength is
  flattery — omit it or label it explicitly "observed, not measured." Do NOT invent tone/sentiment,
  persuasiveness, or peer comparison (no acoustic data, no benchmark corpus exist).
- **Opportunities** — the weaknesses, framed honestly. Lead with the **1–2 highest-leverage** pointers, then
  growth areas, **each with a concrete target** so the next run measures progress: filler < 0.3/100w,
  hedge < 0.15/100w, ask in the first third of the turn. This section carries the rubric's required
  ≥1 unflattering finding.
- **Delta narrative** — use **voice-only** buckets (`byMonthVoice[].deltas`) for the rate trend (filler/hedge/
  tagQ) — the all-turns `byMonth` rates are diluted by typed commands and should NOT be trended. Use all-turns
  `byMonth[].voice_share` only for the separate "how much he's dictating" signal. Also delta against the last
  `runs.jsonl` line: "filler 1.2 → 0.9 /100w, ▼." If only one voice bucket exists, say "baseline — no trend yet."

**Prompt rules (the calibrated contract — keep in sync with the golden rubric):**
- Cite ≥2 real verbatim quotes from the sample. No invented examples.
- Include ≥1 unflattering finding. A read that is all praise is a FAIL — he explicitly wants honest pushback
  over agreement ("I don't want you to agree with me just to agree").
- Distinguish genuine uncertainty from reflexive hedging — never tell him to "be more confident" flatly.
- Terse. Verdicts, not surveys. Match the house voice in `user_communication_style.md`.

## Phase 3 — Render the report

Write a self-contained dark-theme HTML to `.claude/analysis/comms-coach-<date>.html` using the skeleton below
(mirrors the `.claude/analysis/` house style). Open-in-browser, paste-able. Then report the one-line headline
+ the two pointers in-session.

```html
<!DOCTYPE html><html lang="en"><head>
<meta charset="utf-8"/><meta name="viewport" content="width=device-width,initial-scale=1"/>
<meta name="date" content="<DATE>"/><meta name="type" content="comms-coach"/>
<title>comms-coach — <DATE></title>
<style>
:root{--bg:#0f1419;--card:#1a2129;--ink:#e6edf3;--muted:#9fb0c0;--accent:#4db8ff;--good:#3fb950;--warn:#d29922;--bad:#f85149}
*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--ink);font:15px/1.5 Inter,Segoe UI,Arial,sans-serif}
.wrap{max-width:860px;margin:2rem auto;padding:0 1rem}h1{font-size:20px}h2{font-size:15px;margin:1.5rem 0 .4rem;color:var(--accent)}
.card{background:var(--card);border-radius:10px;padding:1rem 1.25rem;margin:.75rem 0}
table{width:100%;border-collapse:collapse;font-size:13px}th,td{text-align:left;padding:.35rem .5rem;border-bottom:1px solid #243} 
.muted{color:var(--muted)}.up{color:var(--bad)}.down{color:var(--good)}blockquote{border-left:3px solid var(--accent);margin:.5rem 0;padding:.25rem .75rem;color:var(--muted)}
</style></head><body><div class="wrap">
<h1>comms-coach — <DATE></h1>
<p class="muted">Project corpus · <N> voice-likely turns · split confidence <CONF></p>
<div class="card"><h2>Profile</h2>...</div>
<div class="card"><h2>Strengths</h2>...evidence-backed only; green tag...</div>
<div class="card"><h2>Opportunities</h2>...the 1–2 pointers + growth areas, each with a → target; warn tag...</div>
<div class="card"><h2>Trend</h2><table>...byMonthVoice (voice-only) rates with delta arrows; add a separate row/line for all-turns voice_share = how much he's dictating...</table></div>
<div class="card"><h2>Evidence</h2><blockquote>...quotes...</blockquote></div>
</div></body></html>
```

## Files

| Path | Role |
|---|---|
| `analyze.mjs` | Layer 1 engine (predicate, metrics, classifier, buckets). Dep-free Node. |
| `golden/2026-06-17-byhand.md` | Calibration baseline + rubric. |
| `calibration-<date>.md` | Calibration result (written Phase 1). |
| `evals/trigger_evals.json` | `/sync-skills --optimize` trigger set. |
| `runs.jsonl` | Append-one-line-per-run ledger (delta source). |
| `.claude/analysis/comms-coach-*.{json,html}` | Run outputs. |

## Roadmap

- Promote to a parameterized **global** skill (corpus = any project, resolved from cwd) once the project pilot
  proves out — currently project-scoped per the build decision (a global skill must not hardcode the IMA corpus).

---

## Skill Run Log Entry (Final Step)

> Per-skill usage log — append one JSON line to this skill's own `runs.<name>.jsonl` (the
> per-skill-log convention; where a project ships a `_shared/skill-run-log.md` spec, follow it).
> **Skip this if you were invoked as a sub-step of another skill’s run** — the parent skill logs;
> only record when this skill ran as a standalone unit of work.

Resolve the contributor: `git config user.name` (first word → `Robert`/`Jess`; fallback: the name
segment of `git rev-parse --abbrev-ref HEAD`); lowercase → `<name>`. Append ONE valid single-line JSON
object to `.claude/skills/comms-coach/runs.<name>.jsonl` (create if absent). **Append only — never edit prior lines.**

```json
{"date":"YYYY-MM-DD","by":"Robert|Jess","ticket":"CI-#### | scope | local","quality":"✅|⚠️|❌","well":"≤15 words","poorly":"≤15 words (— if none)","improve":"≤30 words","model":"claude-opus-4-8","duration":"~Nm","run":"optional artifact ref"}
```

Quality: ✅ clean · ⚠️ partial / needed correction · ❌ rough / abandoned.
