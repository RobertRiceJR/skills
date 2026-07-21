# Calibration — 2026-07-05 (recalibrate, user-requested)

**Result: PASS** (window: `--since 2026-06-01`, includes 2026-06-17; sample: 25 most-recent voice-likely
turns; 180 voice-likely in window, split confidence 0.776)

Scored the Phase-2 read (rendered as `.claude/analysis/comms-coach-2026-07-05.html`; windowed voice
aggregates match the full-corpus run: filler 1.38 vs 1.32/100w, hedge 0.69 vs 0.66, tagQ 0.72, directive
1.01 vs 1.0 — June/July voice buckets identical) against `golden/2026-06-17-byhand.md`.

## Recall — all THREE golden habits independently recovered ✓

1. **Tag-question checkpointing** — recovered. `tagQ` 0.72/turn voice-only; 15/25 sample turns carry ≥1.
   Evidence: "it's designed to assist everybody. Right?"; "Can you get ready so we can survive the compact
   in a due diligent way? Does that make sense?"; "How does that sound? in terms of a path forward."
2. **Front-loaded hedging** — recovered. voice `hedge_rate` 0.69/100w. Evidence: "I guess I just want a
   better understanding of how…"; "I'm I'm referring to the actual, uh, I guess I'm referring to the
   reference files, um, more or less."; "I would probably mark this as either a test skip. Yeah. I'd
   probably mark this as a test skip" (hedge on a decision he then makes). The read separates genuine
   uncertainty ("I'm not sure if the process is still running" — keep) from the reflexive kind, per the
   prompt contract.
3. **Directive-mode strength (the asymmetry)** — recovered. voice `directive_per_turn` 1.01; hedging
   vanishes in demands: "Uh, no edits. Just quick comparison."; "I need you to Automate. End to end with
   technical due diligence."

Secondary credit: mid-sentence self-correction surfaced (`selfcorr` 0.96/turn — "I think it's, like, manual
regression or something like that. Yeah. Manual migration. That's what it's called."). Golden pointer #1
(goal-first) re-observed in current evidence: asks still surface at the end of long turns ("Ask me any
questions that can enhance the deliverables" closing a 179-word turn).

## Precision — no fabricated patterns ✓

Every claim traces to a metric in `comms-coach-metrics-2026-07-05.json` or a verbatim sample turn. The new
"due diligence" finding is countable, not impressionistic: 12/25 windowed sample turns contain the token.
No tone/sentiment, persuasiveness, or peer-comparison claims (no data exists for them).

## Anti-flattery — ✓

- ≥1 genuinely unflattering finding: (a) "due diligence" collapsed into a zero-information intensifier
  (12/25 turns); (b) filler climbing with dictation volume (weekly voice 1.49 → 2.02 → 2.09/100w) with
  unreviewed ASR mangles reaching prompts intact ("fit a fish and see", "Qiwi vault" — the latter destroyed
  the turn's key noun); (c) July voice `directive_per_turn` halved (1.13 → 0.51).
- ≥2 real verbatim quotes: six cited in the report's Evidence card.

## Watch items (not gate failures)

- **Split confidence 0.776** (was 0.907 at the 2026-06-17 calibration; voice-likely pool 56 → 180). The
  classifier is sweeping in more casual dictation. Sample inspection shows zero leakage and all habits
  remain recoverable, so the gate holds — but if confidence drops below ~0.7 next run, revisit the
  classifier threshold in `analyze.mjs` before trusting cross-run rate deltas.
- Known residual confirmed live: pasted SQL/proc bodies inside dictated turns (2 sample turns) distort
  `wc`/`filler_rate` for those turns; per-turn rates were not leaned on for those two.
