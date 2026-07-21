# Robert's Voice Card — team-update register

> **Source:** distilled from `/comms-coach` Layer 1 (`analyze.mjs`) + the voice-likely sample, run
> 2026-06-22 (56 voice-likely turns, split confidence 0.90). This is the **directive subset** of his
> logged voice, not the whole fingerprint.
> **Regenerate when:** a fresh `/comms-coach` run shows his directive habits shifting (re-derive the
> KEEP/DROP table from the new `comms-coach-sample-<date>.json`). Don't hand-edit the metrics — re-run.
> **Consumed by:** `/dsu --team-update` (and pasteable into any session that drafts an outward update).

---

## The core principle

The voice `/comms-coach` measures is his **dictation-to-Claude** voice — a *think-aloud* register
(voice-only: filler 0.5/100w, hedge 0.39/100w, tag-Q 0.89/turn, self-correction 1.02/turn, TTR 0.639,
~370 words/turn with the ask at the **end**). That register is wrong for a written update.

His **team-update voice is the directive 20%** of that fingerprint — `directive_per_turn 0.98`, the mode
where the hedging vanishes and he gets crisp. Extract that; discard the exploratory scaffolding.

**One rule above all:** state the verdict first. His real ask reliably surfaces last when he talks; in
writing, invert it — headline up top, detail below, ask explicit.

---

## KEEP — his real strengths (use these)

| Trait | Why it works | Verbatim exemplar (his words) |
|---|---|---|
| Lead with a verdict | confident, no warm-up | *"Yes. That's exactly what I'm looking for."* · *"This is great. This is exactly what I wanted."* |
| Crisp imperatives | unambiguous next step | *"Publish it to Confluence. Let me know when you're done."* · *"Put this into an HTML."* |
| Plain, vivid framing | readable, memorable | *"a horrible square of pain exercise"* · *"I'm a big seniority guy"* |
| Concrete, sequential detail | the work is legible | *"I run my test in bulk… I rerun last failed. And I decreased the worker count."* |
| Enumerate | scannable | numbers things naturally — *"1. What apps… 2. Will you be picking up…"* |
| State the rationale | "why this matters" lands | *"And why am I thinking about this? It's because this is what we do on our day to day."* |

## DROP — dictation scaffolding (edit out before sending)

| Trait | Metric (voice) | Verbatim example to kill |
|---|---|---|
| Front-loaded hedging | 0.39/100w (W25 spike 1.53) | *"I'm not sure how I'm not sure how to make it great"* · *"I feel like I had an epiphany"* |
| Tag-question checkpointing | 0.89/turn | *"Right?"* · *"Does that make sense?"* → make it a period |
| Filler | 0.5/100w | *"um, uh, you know, yada yada yada"* |
| Mid-sentence self-correction | 1.02/turn | *"laptop, I guess"* — pick the word, delete the wobble |
| Repetition | TTR 0.639 | *"I'm not sure how I'm not sure how"* — say it once |
| Ask-at-the-end arc | ~370 words/turn | move the ask to the **top** |

**The "but" swap (his own insight, 2026-06-17):** he hedges partly to avoid the word *but* (*"I know X,
but I don't know Y"*). In writing, swap to **and** — *"I know X, **and** I don't yet know Y"* — or split
into two sentences. Both clauses stand; no front-loaded doubt.

---

## The skeleton (same every time = consistent + readable)

```
Headline   — the verdict, one line. What's true now.
What changed — 2–4 bullets, past tense, concrete.
Why it matters — impact / risk / decision (skip if obvious).
Next       — what happens next, who owns it.
Asks       — explicit, singular. Empty is fine — say "no asks."
```

---

## Two variants

### EXEC — leadership-facing
- Headline = outcome or risk, not activity ("Regression suite is green on INT" not "I ran tests").
- Lead with impact and decisions-needed. Cut rationale unless a decision hinges on it.
- Short declaratives. Zero tag-questions, zero hedge.
- One explicit ask, or "no asks." Confident — *"best by margin"*, not "I think maybe."

### PEER — teammate-facing
- Keep the **rationale** ("why I'm doing this") — it's a genuine strength and peers want the reasoning.
- Keep plain metaphors (*"square of pain"*) — they land with the team.
- Warmer, but still no filler / hedge / self-correction. One light checkpoint max, as a *statement*
  ("Shout if that breaks your flow"), never *"Right?"*.
- Enumerate the steps when describing a process.

---

## Self-edit pass (run on any draft)

1. Is the **verdict in the first line**? If the point is at the bottom, move it up.
2. Delete every *um / uh / you know / yada yada* and every *I feel like / I guess / I'm not sure* that
   isn't **genuine** uncertainty. (Real unknowns stay — label them as open questions.)
3. Convert every *"Right?" / "Does that make sense?"* to a period.
4. Any *but*-hedge → *and*-swap or split.
5. Each sentence one idea; kill the mid-sentence corrections.
6. Is the **ask explicit and at the top**? If there's no ask, say so.
