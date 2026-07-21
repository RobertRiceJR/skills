# Skill Scorecard — Scoring Rubric (SSOT)

> **Source:** Operationalized from the TDD-011 reference census + the 2026-06-24 deep-read scoring run.
> **Owns:** the canonical axis anchors, census-fold formulas, per-type weights, and disposition logic.
> **Read by:** `/skill-scorecard` Phase 2 (subagent prompt) and `scripts/score.py`. Change scoring HERE, then mirror any constant into `scripts/score.py` (the one duplicated thing — keep them in lockstep; bug-patterns #19).

This is the single definition of how a skill is scored. Every run applies it identically so runs are comparable over time.

## The four axes + ceiling (deep-read, scored 1–5)

Subagents score these **intrinsically** (judge the skill on its own merits; do NOT factor in how often it is called — that arrives as a census signal and is folded in centrally).

| Axis | Question | 1 | 3 | 5 |
| --- | --- | --- | --- | --- |
| **value** (`vi`) | What is it worth when it runs? | novelty / marginal | useful, moderate time-save | mission-critical, gates releases, painful to lose |
| **sustainability** (`si`) | Will it keep working if nobody touches it? | brittle (DOM selectors, multiple 3rd-party APIs, fast schema drift) | a couple of changing systems / one API or schema | depends only on stable internal docs/templates |
| **maintainability** (`mi`) | Cost/safety to change it on purpose? | sprawling/tangled, many phases, no safety net | moderate size/complexity | small, single-responsibility, clear, has eval/safety-net |
| **maturity** (`mat`) | How complete/polished is it TODAY? | experimental/stub | works with rough edges | production-grade, battle-tested |
| **ceiling** (`ci`) | How high could its value realistically go? | already near its natural limit / inherently narrow | modest upside | could become far more capable/central |

**Headroom** = `ceiling − maturity` (clamped ≥ 0). It answers "what's the ceiling, and are we there?" — a long headroom = unrealized upside. Headroom is derived, not scored.

## Census fold (applied centrally in `score.py`)

Final axes blend the intrinsic deep-read score with objective signals from `_shared/skill-graph.json` (incoming blast-radius `in`, outgoing fan-out `out`) and ledger run-frequency (`runs`). All sub-signals are bucketed to 1–5 so ±1–3 differences in raw counts don't move the score.

```
reach(in)  = 5:>=20  4:12-19  3:6-11  2:3-5  1:<=2          # blast radius -> Value up
usage(runs)= 5:>=25  4:10-24  3:3-9   2:1-2  1:0  (None=excluded)
outf(out)  = 1:>=10  2:7-9    3:4-6   4:1-3  5:0             # fan-out -> Sustainability down
ripple(in) = 1:>=20  2:12-19  3:6-11  4:3-5  5:<=2           # blast radius -> Maintainability down

Value          = round( 0.5*vi + 0.3*reach + 0.2*usage )      # if runs known
               = round( 0.625*vi + 0.375*reach )              # if no runs logged
Sustainability = round( 0.7*si + 0.3*outf )
Maintainability= round( 0.7*mi + 0.3*ripple )
Maturity       = mat        (unchanged)
Ceiling        = ci         (unchanged)
```
Rounding is **half-up** (`int(x+0.5)`), not banker's rounding — a score of exactly 2.5 becomes 3.

## Per-type composite (Standing, 0–100)

Same axes, weighted by type because "value" means different things for a conductor vs a worker vs a niche helper.

| Type | Value | Sustainability | Maintainability | Maturity |
| --- | --- | --- | --- | --- |
| **Orchestrators** (O) | 40% | 25% | 20% | 15% |
| **Tools** (T) | 35% | 30% | 20% | 15% |
| **One-offs** (X) | 35% | 20% | 25% | 20% |

`Standing = (wV·V + wS·S + wM·Maint + wMat·Maturity) / 5 × 100`. **Standing is a health score, not an importance ranking** — a load-bearing skill that is fragile and tangled scores lower than a humble clean one. Sort by Value for pure importance.

## Disposition (priority cascade — protect value first, then grow)

```
V <= 2                                  -> Retire/Review   (low value — does it still earn its place?)
S <= 2                                  -> Harden          (valuable but fragile; covers fragile+tangled)
M <= 2                                  -> Simplify        (valuable but hard/risky to change)
headroom >= 2  OR (ceiling>=5 & mat<=4) -> Invest          (solid, with real runway)
otherwise                               -> Maintain        (healthy — leave it alone)
```
A Harden-flagged skill with a high ceiling is an Invest candidate **after** it is stabilized.

## Type classification

A skill is one of three types. Classify by role, not raw reference count:

- **Orchestrator** — a user-facing workflow conductor that drives a multi-phase process, typically delegating to sub-skills, or an autonomous multi-phase engine.
- **Tool** — a reusable building block (reporter, analyzer, loader, linter, diagnostic, data helper), called by orchestrators or run standalone.
- **One-off** — niche, episodic, personal, or novelty; not part of the repeatable core system.

Current assignment (reviewable each run — override in `<date>-readaxes.json`):
- **Orchestrators (13):** three-amigos, ready-for-testing, ready-for-qa, ready-for-playwright, playwright-workflow, api-test-workflow, prod-support, prod-support-poller, sync, confluence-test-plan, technical-due-diligence, skill-evolve, fix-loop.
- **One-offs (5):** auth0-regression, deal-sheet-debug, manual-migration, comms-coach, roast-me.
- **Tools (38):** everything else.

> Portability across AI platforms is intentionally **excluded** (Claude-specific is fine, per Robert 2026-06-24).
