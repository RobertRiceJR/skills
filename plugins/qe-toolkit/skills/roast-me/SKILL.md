---
name: roast-me
description: >
    Roasts the health of a Playwright test suite (tuned for IMA-360-style suites, runs against
    any). Runs git + grep scripts to surface flake-prone hard waits (waitForTimeout), skipped/fixme
    tests, leaked focus (.only), churn hotspots (specs you keep re-fixing),
    god POMs/specs, suppressed type/lint errors, stray console.logs, stale
    TODOs, alias/import drift, forbidden flake patterns (pressSequentially on
    address fields), and test-to-page coverage drift. Scores each finding for
    evidence quality and severity, drops the weak ones, and returns a
    prioritized report with a single highest-leverage fix. Default tone is
    blunt developer roast.
    Run manually with /roast-me. Optional arg scopes to one area (a path segment such as a
    feature/module name).
    Trigger: "roast me", "roast the suite", "roast the tests", "suite health check", "test debt audit",
    "what's rotting in the test suite", "/roast-me"
user_invocable: true
argument: '[area] (optional — a path segment to scope to, e.g. a feature/module name. Default: whole suite.)'
---

# Suite Roast

Roast the health of the Playwright test suite (`src/`). Find the rot, cite the
evidence, rank by what will bite in CI, and name the one fix worth doing today.
This is the QE-flavored cousin of a generic repo health-check: the signals are tuned to
test debt — flakiness, leaked focus, skipped coverage, god files, suite
conventions — not generic code smell.

> **Scope boundary.** This skill owns **test-suite** health (`src/`). It does
> not roast whole-repo concerns (dependency/codegen freshness, the
> `.claude/skills` ecosystem, root-level cruft). If asked for a
> repo-wide audit, say so and stay in your lane — don't half-cover it.

## Context

**Gather first — run these via the Bash tool, not inline `!`…`` execution.**
These signals used to be embedded as inline `!`…`` command-substitutions the
harness auto-runs at skill load. That form is dead-on-arrival on Windows /
PowerShell hosts: the permission gate static-analyzes each command, and the
churn command's `$(…)` substitution can't be statically analyzed, which aborts
the *entire skill* before any signal runs. So run the block below with the
**Bash tool** (POSIX is available even on Windows) as your first action. The
commands are independent — batch them across a few Bash calls for speed.

Each signal is git-tracked-only (no `node_modules`, `playwright-report`, or
`test-results`). If a command returns nothing or errors, skip that signal and
note "no data" — never invent counts.

```bash
# CODE-token signals (1,2,3,7,9,10) go through a comment-aware grep `grep-code.mjs`
# (strips // and /* */ before matching) so a commented-out `.only(` / `waitForTimeout`
# no longer false-flags. Signals #6 (@ts directives) and #8 (TODO/FIXME) DELIBERATELY stay on raw
# grep — they target COMMENT content by design; comment-stripping them would zero them out.
#
# PORTABILITY: grep-code.mjs is a project-specific helper. If the current project ships one, use it;
# otherwise fall back to raw `grep -nE` (the comment-aware pass is a nicety, not a requirement — the
# Self-Assessment step already drops comment/string false positives). Both take `<pattern> <files...>`,
# so $GREP is drop-in for xargs. Auto-detect:
GC="$(ls .claude/skills/_shared/scripts/grep-code.mjs _shared/scripts/grep-code.mjs 2>/dev/null | head -1)"
if [ -n "$GC" ]; then GREP="node $GC"; else GREP="grep -nE"; fi   # code-token signals use $GREP

# 1. Hard waits (flake factory)
git ls-files 'src/**/*.ts' | xargs $GREP 'waitForTimeout' 2>/dev/null | head -40

# 2. Skipped / fixme tests (silent coverage holes)
git ls-files 'src/**/*.ts' | xargs $GREP 'test\.(skip|fixme)|test\.describe\.skip|describe\.skip' 2>/dev/null | head -40

# 3. Leaked focus — .only (CRITICAL: disables the rest of the suite in CI)
git ls-files 'src/**/*.ts' | xargs $GREP '\.only\(' 2>/dev/null | head -20

# 4. Churn hotspots (specs/POMs re-fixed most in 6mo → flaky candidates;
#    resolves origin/master so it works on a feature branch with no local commits)
ref=$(git rev-parse -q --verify origin/master || git rev-parse -q --verify master || echo HEAD); git log --pretty=format: --name-only --since="6 months ago" "$ref" -- 'src/**/*.ts' 2>/dev/null | grep -v '^$' | sort | uniq -c | sort -rn | head -12

# 5. Largest files (god specs / god POMs)
git ls-files 'src/**/*.ts' | xargs wc -l 2>/dev/null | grep -vE ' total$' | sort -rn | head -10

# 6. Suppressed signals (@ts-ignore / @ts-expect-error / eslint-disable) — RAW grep on purpose:
#    these are directive COMMENTS, so the match must see comment content.
git ls-files 'src/**/*.ts' | xargs grep -nE '@ts-ignore|@ts-expect-error|eslint-disable' 2>/dev/null | head -20

# 7. Stray console.log/debug left in tests
git ls-files 'src/tests/**/*.ts' | xargs $GREP 'console\.(log|debug)' 2>/dev/null | head -20

# 8. Stale TODO/FIXME/HACK in source — RAW grep on purpose: these markers live in comments,
#    so the match must see comment content (comment-stripping would zero this signal out).
git ls-files 'src/**/*.ts' | xargs grep -nE 'TODO|FIXME|HACK|WORKAROUND' 2>/dev/null | head -25

# 9. Alias/import drift (non-spec POMs/utils/fixtures using relative ../../ instead of
#    tsconfig aliases — spec files excluded; the waiters.types relative import is sanctioned)
git ls-files 'src/**/*.ts' | grep -vE '\.spec\.ts$' | xargs $GREP "from '\.\./\.\./" 2>/dev/null | head -20

# 10. Forbidden flake pattern (pressSequentially breaks Google Places autocomplete under
#     the config's --disable-http2; address fields must be filled manually — MUST be 0)
git ls-files 'src/**/*.ts' | xargs $GREP 'pressSequentially' 2>/dev/null | head -10

# 11. Coverage shape (specs vs page objects)
echo "e2e specs:"; git ls-files 'src/tests/**/*.e2e.spec.ts' | wc -l; echo "api specs:"; git ls-files 'src/tests/**/*.api.spec.ts' | wc -l; echo "page objects:"; git ls-files 'src/pages/**/*.ts' | wc -l; echo "specs by area:"; git ls-files 'src/tests/**/*.spec.ts' | sed -E 's#src/tests/(e2e|api)/([^/]+)/.*#\1/\2#' | sort | uniq -c | sort -rn
```

> **Run with the Bash tool, not PowerShell.** These are POSIX pipelines
> (`grep`/`xargs`/`node`/`sed` + `$(…)` substitution) — the Bash tool runs them fine on
> this Windows host; do not translate them to PowerShell. The code-token signals
> (1,2,3,7,9,10) pipe through `grep-code.mjs` so commented-out code no longer false-flags;
> #6 and #8 stay on raw `grep` because they target comment content. Interpretation notes:
> signal #3 (`.only`) and #10 (`pressSequentially`) are the two CRITICALs and
> must each be **0** — never skip them. For #9, the `waiters.types` relative
> imports are sanctioned (see CLAUDE.md) and are NOT drift — exclude them.

If an `[area]` argument was passed, filter every finding to files whose path
contains that segment (e.g. `party` → `src/**/party/**`). Otherwise roast the
whole suite.

## Constraints

- Never be vague — every finding cites a specific file (and line/count) as evidence.
- Every finding includes: what's wrong, evidence, severity, fix.
- A bare count is not a finding — name the worst offenders by file.
- Prefer script output over assumptions. If the repo contradicts prior knowledge, trust the repo.
- Never recommend "rewrite the suite" — suggest the incremental, highest-leverage cut.
- Never flag lint/formatting style — that's eslint's job. Flag *suppressed* lint (eslint-disable), not formatting.
- A `waitForTimeout` is presumed-guilty: hard waits are the #1 flake source. Don't soften them.
- `.only` is always CRITICAL if present — it silently green-checks a CI run that ran one test.
- `pressSequentially` is CRITICAL if present — it's a known breakage on this config, not a style nit.
- Alias drift is a real finding only for **non-spec** files; the `waiters.types` relative import in e2e specs is sanctioned (see CLAUDE.md) — don't flag it.
- Maximum 8 findings, ordered by severity. Quality over inventory.
- Only make findings backed by observed evidence from the Context scripts.
- Don't double-count: a god spec full of hard waits is one finding (the worst dimension), not three.

## Workflow

Work these phases internally before presenting. Internal phasing lets you drop
weak findings so the user sees only what earns its place.

1. **Gather.** Read all Context script output. If an `[area]` arg was passed, filter now. Then (via the Bash tool) read the last line of `runs.jsonl` in this skill's folder if it exists — that's the previous baseline for the Since-last-roast comparison. If the file is absent, this is the first roast on record.
2. **Categorize & score.** Bucket findings (flakiness, coverage holes, complexity/churn, conventions, hygiene). Run Self-Assessment on each. Drop or flag anything below the evidence bar.
3. **Prioritize.** Rank by CI impact, not by how easy the finding was to spot. Build the recommendations. Run the Constraints checklist before presenting.

Present one complete report. Only stop for input if more than half the findings
score below 7 on evidence quality and you genuinely can't tell signal from noise.

## Self-Assessment

Rate each finding before presenting:
- **Evidence quality (1-10)** — backed by script output, or inference?
- **Severity accuracy (1-10)** — will this actually bite (flake, false green, merge pain), or could it be intentional?
- **Actionability (1-10)** — can Robert fix it today?

Drop or flag-as-"needs investigation" any finding below 6 on evidence quality.
Show the three scores on each finding so the reasoning is visible.

> Watch for grep false positives before scoring: a `SELECT ... FROM` or a
> `TODO` inside a `//` comment is documentation, not debt. If a hit is in a
> comment or a string literal rather than live code, it does not earn a finding.

## Scoring Guide (suite health, out of 10)

- 9-10: Lean and stable. Negligible flake surface, no leaked focus, coverage tracks growth.
- 7-8: Healthy with some debt. A handful of hard waits / skips to clean up.
- 5-6: Meaningful debt. Flake surface is real; skipped coverage is accumulating.
- 3-4: Systemic. Hard waits everywhere, skips rotting, god files concentrating risk.
- 1-2: On fire. Leaked `.only`, forbidden patterns shipped, double-digit skips, churn hotspots no one trusts.

## Output

Default to **ROAST mode** — blunt, specific, funny if it lands, never cruel about
people. Roast the code, not the coder. If the user says "for my manager" or
"for the team," switch to a measured assessment that frames findings as CI cost
(flaky-run minutes, false greens, onboarding friction).

Structure:
1. **One-line verdict** + overall score /10. Make it sting a little.
2. **Since last roast** — only if a baseline exists (last line of `runs.jsonl`). One
   line of deltas on the headline counts and score, each marked ▼ better / ▲ worse /
   = flat (debt going *down* is ▼ and good): e.g. `Since 2026-06-04 — hard waits
   36→28 ▼, skips 59→61 ▲, alias drift 20→14 ▼, score –→7`. If there's no baseline,
   say "first roast on record — this run sets the benchmark," and move on.
3. **Top findings** (max 8), each with: issue, evidence (file + count/line), severity, fix, and the three confidence scores.
4. **Confidence summary** — how many findings were high-confidence vs flagged.
5. **One thing the suite does well** — credit where due (e.g. zero `.only`, clean POM separation, `pressSequentially` count of 0).
6. **Highest-leverage fix** — the single change that buys the most stability. One sentence.

**Example finding (roast mode):**
**Issue:** Hard waits are carrying your flakiness on their back
**Evidence:** 36 `waitForTimeout` calls across `src/tests/`; worst concentration in `party/` specs
**Severity:** High
**Confidence:** Evidence 9/10, Severity 9/10, Actionability 7/10
**Fix:** Replace the top 5 offenders with web-first assertions (`expect(locator).toBeVisible()`) or the waiter pattern (`getResponsePromise` before the action, `waitForResponseSuccess` after). Start with the party specs — they're also your #1 churn hotspot, so the flake and the re-fixes are the same wound.

## Snapshot (persist for next time)

**Always run this as the final step** — it's what makes the Since-last-roast
comparison work. Via the Bash tool, append exactly one JSON line to `runs.jsonl`
in this skill's folder, using the real counts from the Context signals
(append-only, one line per run; the next roast reads the last line as its baseline):

```
{"date":"<YYYY-MM-DD>","branch":"<git branch>","area":"<area|whole suite>","score":<n>,"counts":{"hard_waits":N,"skips_fixme":N,"only":N,"suppressed":N,"console_logs":N,"todos":N,"alias_drift":N,"press_sequentially":N},"top_hotspots":["file:count","file:count","file:count"]}
```

If a prior `runs.jsonl` line exists, your next run compares against it; otherwise this run sets the benchmark.

## Triggering Evals

A triggering eval set lives at `evals/trigger_evals.json` (positives = real roast
phrasings; negatives = requests that should route to a sibling skill or a repo-wide audit).
`/sync-skills --optimize` (or the `eval-judge` plugin's `skill-creator` scripts directly) can run
it to grade whether this `description:` fires when it should and stays quiet when it shouldn't.

---

## Skill Run Log Entry (Final Step)

> Per-skill usage log — append one JSON line to this skill's own `runs.<name>.jsonl` (where a
> project ships a `_shared/skill-run-log.md` spec, follow it).
> **Skip this if you were invoked as a sub-step of another skill’s run** — the parent skill logs;
> only record when this skill ran as a standalone unit of work.

Resolve the contributor: `git config user.name` (first word, lowercased → `<name>`; fallback: the name
segment of `git rev-parse --abbrev-ref HEAD`). Append ONE valid single-line JSON
object to `runs.<name>.jsonl` in this skill's folder (create if absent). **Append only — never edit prior lines.**

```json
{"date":"YYYY-MM-DD","by":"Robert|Jess","ticket":"CI-#### | scope | local","quality":"✅|⚠️|❌","well":"≤15 words","poorly":"≤15 words (— if none)","improve":"≤30 words","model":"claude-opus-4-8","duration":"~Nm","run":"optional artifact ref"}
```

Quality: ✅ clean · ⚠️ partial / needed correction · ❌ rough / abandoned.
