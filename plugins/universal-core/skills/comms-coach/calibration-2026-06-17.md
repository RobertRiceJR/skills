# Calibration — 2026-06-17

**Result: PASS** (window: full corpus, includes 2026-06-17; sample: 25 most-recent voice-likely turns)

Scored a Layer 2 read against `golden/2026-06-17-byhand.md`.

## Recall — all THREE golden habits independently recovered ✓
1. **Tag-question checkpointing** — recovered. Evidence: the "don't agree" turn carries `tagQ=6`
   ("…best by margin. Right? … Does that make sense?"); the "one skill for all domains" turn `tagQ=5`.
2. **Front-loaded hedging** — recovered. Evidence: "I feel like domains was a easy way of classifying things
   of the past"; `hedge_rate` 0.58–1.90 on the dictated turns.
3. **Directive-mode strength** — recovered. Evidence: "I don't want you to agree with me just to agree";
   "not just best by a little bit, but best by margin."

## Precision — no fabricated patterns ✓
Every claim traces to a sample turn or a metric in `comms-coach-metrics-2026-06-17.json`. No invented tics.

## Anti-flattery — ✓
- Unflattering finding present: filler/hedge **rise** as dictation rises (May 0.07 → June 0.16 /100w); the
  opening monologue was partly re-recorded (redundancy); hedging undercuts points he has evidence for.
- ≥2 verbatim quotes cited (above).

## Notes
- ~~Trend buckets aggregate all turns → filler/hedge diluted by typed turns~~ **RESOLVED 2026-06-17:**
  `analyze.mjs` now emits voice-only buckets (`voiceOverall`/`byMonthVoice`/`byWeekVoice`); Phase 2/3 trend
  the voice-only rates and keep all-turns `voice_share` only as the dictation-volume signal.
- `splitConfidence` 0.889 — 183 turns sit within ±1 of the voice/typed boundary; acceptable for v1.

Gate satisfied → Layer 2 is trusted to emit reports until `--recalibrate`.

## Independent re-grade — 2026-06-17 (closes the self-graded gap)

The original PASS above was self-graded (author == grader). Re-graded by an **independent subagent** given
only the golden file, the report, and the sample/metrics JSON, instructed to be skeptical:

- **RECALL: PASS** — all three golden habits recovered (+ secondary self-correction).
- **PRECISION: PASS** — every Evidence quote located in `sample.json` (minor stutter/ellipsis smoothing, no
  fabrication); every headline number matched `voiceOverall`/`byMonthVoice` exactly.
- **ANTI-FLATTERY: PASS** — 3 unflattering findings + 3 real verbatim quotes.
- **OVERALL: PASS.**

## Extraction-contamination fix (same day)

Re-running during the touch-up pass exposed a Pattern-37 contaminant: harness-injected user-role turns
(skill-invocation bodies "Base directory for this skill:", context-compaction summaries "This session is
being continued…", `<ide_opened_file>`/`<task-notification>` spans) were being counted as human turns —
inflating `avg_words` to ~734 and leaking into the voice-likely set. `analyze.mjs` now excludes them
(`clean()` + two predicate guards). Voice-likely settled at 37, `avg_words` 490. Known residual: a couple of
pasted prompt templates still count (genuinely user-authored; they shift word-count, not per-word rates).
