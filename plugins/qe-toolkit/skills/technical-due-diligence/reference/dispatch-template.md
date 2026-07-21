# TDD Dispatch Template — per-run plan

Fill-in spec instantiated once per `/technical-due-diligence` run (Phase 0). The completed
copy becomes the **Scope & Plan** section at the top of the run report in `runs/`.

This is the run *plan*. It is **not** the subagent prompt — when fanning out (Phase 2), the
actual subagent prompts are built from `.claude/skills/_shared/agent-dispatch-template.md`
(the 9-section format). This file decides *what* to dispatch; that file decides *how*.

Replace every `<FILL IN>`. Delete the guidance in _italics_ once filled.

---

## Scope

- **Run ID:** TDD-<NNN>  _(Phase 0: highest in index.md + 1; first run = TDD-001)_
- **Date:** <YYYY-MM-DD>  _(Phase 0: from `git log -1 --format=%cd --date=short` — never hardcode)_
- **Jira:** [<CI-####>, ...]  _(or `—`)_
- **Target:** <repo name / subsystem name>
- **Root path:** `<absolute path>`  _(e.g. `C:\path\to\some-repo`)_
- **File globs in scope:** `<glob(s)>`  _(e.g. `src/**/*.ts`, `Resolvers/**/*.cs`)_
- **File globs excluded:** `<glob(s) or none>`  _(e.g. `**/*.generated.ts`, `**/node_modules/**`, `**/*.test.ts` if tests are assessed separately)_
- **Approx size:** <N files / ~N LOC>  _(Phase 0 sizing — drives the run shape below)_

## Dimensions

| # | Dimension                                  | In scope? | Note (why out, if out) |
| - | ------------------------------------------ | --------- | ---------------------- |
| 1 | Architecture, coupling, boundaries         | <Y/N>     |                        |
| 2 | Test coverage, test quality, and gaps      | <Y/N>     |                        |
| 3 | Security surface & trust boundaries        | <Y/N>     |                        |
| 4 | Error handling & failure modes             | <Y/N>     |                        |
| 5 | Tech debt & maintainability                | <Y/N>     |                        |
| 6 | Dependency health & version risk           | <Y/N>     |                        |
| 7 | Performance hotspots                       | <Y/N>     |                        |

_Default: all seven in scope. Mark a dimension out only when the user passed `--dimensions`._

## Run shape

- [ ] **Inline** — small/medium target, all in-scope dimensions in this single context.
- [ ] **One subsystem per run** — large repo; this run covers `<subsystem>` only; remaining
      subsystems get their own sequential TDD-NNN runs (list them: `<...>`).
- [ ] **Per-dimension subagent fan-out** — large target; dispatch read-only subagents.

### Subagent split (only if fan-out)

_One subagent per dimension (or per (dimension × subsystem) for very large repos). Batch ≤ 6.
`subagent_type: general-purpose`, context isolation (omit `isolation`). **Never `worktree`** —
read-only audit. Build each prompt from `_shared/agent-dispatch-template.md`._

| Subagent | Dimension(s) | Path / glob slice | Return contract |
| -------- | ------------ | ----------------- | --------------- |
| A | <e.g. 3 Security> | `<glob>` | Finding blocks for Security only — every finding has `file:line` + quoted code, severity by blast radius. No file writes; return a manifest. |
| B | <...> | `<...>` | <...> |

_Synthesis (dedup across dimensions, global re-rank, verdict) stays in the orchestrator —
never delegated to a subagent._

## Acceptance check (before writing the report)

- [ ] Every finding cites `file:line` and quotes the code (rule 2). Uncited → dropped or proven.
- [ ] No finding rests on a filename/layout/doc inference (rule 1).
- [ ] Every in-scope dimension was genuinely walked (a "no findings" line names what was checked).
- [ ] Any scope-down is stated explicitly in Scope & Plan **and** in the index verdict (no silent caps).
- [ ] Verdict = the 3 findings that most move the deal's price/go-no-go, each linking its block.
