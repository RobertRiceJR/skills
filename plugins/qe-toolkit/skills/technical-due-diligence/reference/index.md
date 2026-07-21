# Technical Due Diligence — Run Registry

Human index of every `/technical-due-diligence` run. **Reverse-chronological — newest first.**
Each run's full report is a self-contained HTML file (IGS-brand output-kit) in [`runs/`](runs/); the **Report** cell links to it.

- **Run ID** is sequential and stable (`TDD-001` = oldest). Assigned at Phase 0; never reuse.
- **Verdict** is the one-line, ≤15-word top-acquirer-concern summary. Keep it scannable.
- **C/H/M/L** = Critical / High / Medium / Low finding counts (matches the report frontmatter `severity`).
- **Score** = Overall Ranking (1-10, 10 = clean) — the deterministic band on the C/H/M/L profile
  (`skill.md` Phase 3 step 5). Rendered as a `.score` heatmap pill in the report header; matches the
  report frontmatter `ranking`.
- **Jira** = `CI-####` refs if any, else `—`.

> **SQL-layer overhaul (2026-06-25):** TDD-015–018 are a four-part review of `src/utils/sql` split by sub-area (client/facade · config · queries · types). See the [cross-area roll-up](runs/2026-06-25-sql-layer-rollup.html) for the unified, ranked punch-list across all four (synthesis page — not a registry row).

| Date | Run ID | Scope | Verdict (≤15 words) | C/H/M/L | Score | Jira | Report |
| ---- | ------ | ----- | ------------------- | ------- | ----- | ---- | ------ |
| 2026-07-06 | TDD-032 | package.json — dependency & devDependency audit + CI install strategy | 4 devDeps deletable; can't --omit=dev the test pipeline (runner is a devDep); dashboard leg can + promptfoo→optional | 0/0/4/3 | 7 | — | [report](runs/2026-07-06-package-json-deps.html) |
| 2026-07-03 | TDD-031 | igs-production-investigation vs prod-support (comparative skill audit + harvest map) | IGS C+ — flagship KQL file is a byte-dup, methodology excellent; prod-support B+ — signatures 3% backfilled; 8-item harvest | 1/2/9/6 | 3 / 6 | — | [report](runs/2026-07-03-prod-support-skills-comparative.html) |
| 2026-07-02 | TDD-030 | src/utils/sql — architecture + routing stats + timing (10-run history, live plan caches) + enhancement plan | Hottest finder ships 10k rows to pick 1 (67 server execs); 12–40s query family unobserved; Industrial SQL fragmented + health-check-blind | 0/3/8/7 | 4 | CI-7868, CI-7761, CI-7513 | [report](runs/2026-07-02-sql-query-architecture.html) |
| 2026-07-02 | TDD-029 | Deal-sheet LF/WIP 3-path harvest (TDD-024 R1 WIP-half close) — WIP templates vs Live witnesses | LF ships only in Electric WIP (hedge workbench); gas WIPs ≈ Live; 2 margin-math defect candidates | 0/2/3/3 | 5 | CI-7513, CI-7733 | [report](runs/2026-07-02-deal-sheet-lf-wip-harvest.html) |
| 2026-07-02 | TDD-028 | mssql-industrial-int — 3 long-running sessions (405 billing proc; 383/340 DemandForecasting SSIS extracts) + RAD-burst TRIAGE | CPU-starved by a recurring (CI-7868) RAD account-feed burst — self-resolved when it drained; billing proc 100×+ degraded/overlapping w/ swallowed failures; RAD volume flat so 06-27 root cause unpinned (Query Store OFF) | 1/2/3/2 | 2 | — | [report](runs/2026-07-02-industrial-int-long-running-sessions.html) |
| 2026-07-01 | TDD-027 | src/utils/sql/queries — WITH (NOLOCK) decision (166 read-only finders) | No — RCSI is ON on all 4 DBs, so NOLOCK is a pure downgrade (dirty reads, Error 601), zero concurrency gain | 0/1/3/2 | 6 | — | [report](runs/2026-07-01-sql-queries-nolock.html) |
| 2026-07-01 | TDD-026 | dealsheet-excel-upgrade (IGS.CIBatch Excel-2024 upgrade — probes + run-log; + deal-scrape hub relevance) | Not the scraper source; run-log shows a Critical silent margin-corruption (scrape recalc `#NAME?`→0) + fix live on the wrong box; large deal-scrape harvest | 1/2/4/3 | 2 | CI-7806, CI-7513, CI-7734, ITOPS-6107 | [report](runs/2026-07-01-dealsheet-excel-upgrade-cibatch.html) |
| 2026-07-01 | TDD-025 | hedge_reconciliation.py — Supply→IMA.Hedges backfill (+ deal-sheet-debug hub relevance) | One-off backfill, not a pipeline: non-txn delete+insert + false idempotency (confirmed live); reference-only for the hub, bypasses the scrape/HedgeKey path | 2/5/4/3 | 1 | LFA-1, CI-7513, CONTRACT-954 | [report](runs/2026-07-01-hedge-reconciliation-pipeline.html) |
| 2026-06-26 | TDD-024 | deal-sheet-debug KB completeness + enrichment roadmap (Confluence pipeline + LFA-1 hedges) | KB documents 1 of 6 paths; blind to upstream pipeline + LFA hedges; mis-defines DNT — +Confluence-sweep addendum extends roadmap to R13, adopts deal-scrape split | 2/6/5/2 | 1 | LFA-1, CI-7733, CI-7513 | [report](runs/2026-06-26-deal-sheet-debug-kb-enrichment.html) |
| 2026-06-26 | TDD-023 | QE ecosystem volume co-located inside a developer/app repo (agent-steering risk) | Real risk, fully containable: OVERRIDE-framed eager floor + test-facts-as-app-truth; cheapest fix is don't co-locate | 1/3/4/1 | 2 | — | [report](runs/2026-06-26-qe-ecosystem-volume-in-dev-repo.html) |
| 2026-06-26 | TDD-022 | QE→developer context-bleed boundary (skill-sharing risk-mitigation) | Platform isolated by construction; real gaps are the unenforced boundary + global init-qe-repo | 0/2/3/1 | 5 | — | [report](runs/2026-06-26-qe-dev-context-bleed.html) |
| 2026-06-26 | TDD-021 | /align-pom Phase-5 self-grading judge (skill.md + conformance-rubric.md) | Architecture right; "deterministic" greps are comment-blind + reuse can't see prefix-overlap; validator unvalidated | 0/4/4/3 | 4 | — | [report](runs/2026-06-26-align-pom-judge.html) |
| 2026-06-25 | TDD-020 | prod-support v1 triage operating model (skill + bug-template + poller/headless) | Boundary solid + dedup proven live; novel branch unproven; autonomous dedup can silently drop | 0/2/5/2 | 5 | CI-7863, CI-7871 | [report](runs/2026-06-25-prod-support-v1.html) |
| 2026-06-25 | TDD-019 | Proposed remediation of src/utils/api.utils.ts (review of recommended changes) | Waiter already closed the gap; ship logging+doc, de-scope the duplicate errors[] guard | 0/0/2/3 | 8 | — | [report](runs/2026-06-25-api-utils-remediation.html) |
| 2026-06-25 | TDD-018 | src/types/sql — SQL result types (+ inline facade types) | Hand-written casts, no generation; one type declares fields its query never returns | 0/0/3/3 | 8 | — | [report](runs/2026-06-25-sql-types.html) |
| 2026-06-25 | TDD-017 | src/utils/sql/queries — 6 query modules (~2,726 LOC) | String params interpolated (not bound) into live-DB SQL; CI filter copy-pasted ~80× | 0/1/5/4 | 6 | — | [report](runs/2026-06-25-sql-queries.html) |
| 2026-06-25 | TDD-016 | src/utils/sql — config (sql.config + sql.industrial.config + context routing) | Industrial "config" is half a finder layer; trustServerCertificate blanket-true; copy-pasted config | 0/0/4/4 | 7 | — | [report](runs/2026-06-25-sql-config.html) |
| 2026-06-25 | TDD-015 | src/utils/sql — client + facade (sql.client.ts + sql.db.ts) | New pool per finder call, never closed; ~100-finder god facade; inconsistent empty-result contract | 0/1/5/3 | 6 | — | [report](runs/2026-06-25-sql-client-facade.html) |
| 2026-06-25 | TDD-014 | waiters.ts response-wait primitive (+ logger.ts) — best-practice + Winston logging | Lightweight & fit-for-purpose; "success" only checks HTTP 200 (GraphQL errors pass); failures unlogged | 0/1/7/4 | 6 | — | [report](runs/2026-06-25-waiters-util.html) |
| 2026-06-24 | TDD-013 | Swarm Testing (Groce-style fuzzing) methodology fit for this suite + app | No — no oracle, destructive shared data, budget 3–4 orders too small; query-layer PBT is the real move | 2/2/1/0 | 1 | — | [report](runs/2026-06-24-swarm-testing-methodology-fit.html) |
| 2026-06-24 | TDD-012 | Feature-flag / env-gating strategy for the suite | No env axis in selection; only env-gate is a phantom; skip+per-env JSON is lightest correct | 0/3/4/4 | 4 | — | [report](runs/2026-06-24-feature-flag-env-gating.html) |
| 2026-06-24 | TDD-011 | Skills ecosystem — reference-count census (62 skills) | Zero ghost skills; coupling concentrates in ~8 orchestrators; clean orchestrator/worker layering | 0/0/0/2 | 9 | — | [report](runs/2026-06-24-skills-ecosystem-references.html) |
| 2026-06-24 | TDD-010 | Deal Sheet hedge-tab API tests (CI-7735) | Clean tests, near-zero feature coverage; hedge financials verified by nothing executed | 1/2/3/2 | 2 | CI-7735 | [report](runs/2026-06-24-deal-sheet-hedge-tab-ci-7735.html) |
| 2026-06-24 | TDD-009 | Navigation utilities — navigate.ts + site-navigator.ts (modernization TDD) | Two navigation SSOTs already drifting; waits flaky-by-design; standardize on a shared least-resistant-path core | 0/4/6/3 | 4 | — | [report](runs/2026-06-24-navigation-utils.html) |
| 2026-06-23 | TDD-008 | IMA 360 search-index propagation — 5 proposed indexing fixes (three-amigos × TDD) | CI-7863 needs an architecture call; 3 of 5 fixes don't match main; CI-7864 mis-scoped | 0/3/2/0 | 4 | CI-7868, CI-7869, CI-7862, CI-7863, CI-7864 | [report](runs/2026-06-23-ima-search-index-fixes.html) |
| 2026-06-23 | TDD-007 | Orchestrator TC-creation data + navigation setup slice (/three-amigos, /ready-for-testing, /sql-data) | Reuse façade (sqlDB.*) invisible to /sql-data → bespoke SQL + over-precision manufactures the user gate | 0/3/4/1 | 4 | — | [report](runs/2026-06-23-orchestrator-tc-data-nav-setup.html) |
| 2026-06-20 | TDD-006 | Igs.Crm.Query.Web (CRM GraphQL gateway) — Auth0-regression + subsystem audit | App-layer auth fails open (header-trust + any-origin CORS); 5 of 7 "Auth0" bugs are pre-existing | 3/15/16/5 | 1 | CI-7843 | [report](runs/2026-06-20-crm-query-web-auth0-regression.html) |
| 2026-06-19 | TDD-005 | GraphQL App Insights (INT) × suite coverage | getCurrentUserTeam (top error) untested; failures masked as 200; +post-release regression F11 (COH) | 0/5/4/2 | 4 | — | [report](runs/2026-06-19-graphql-appinsights-coverage.html) |
| 2026-06-19 | TDD-004 | src/data mutations + queries (GraphQL op packaging) | Documented "load-bearing" duplicate is dead; 2 mutations misfiled in queries/; fragment ×3 | 0/3/5/5 | 4 | — | [report](runs/2026-06-19-data-mutations-queries-packaging.html) |
| 2026-06-16 | TDD-003 | CRM IMA search indexer (Igs.Crm.Ima.Search) | Indexer code trace: 2 confirmed bugs (1 high, 1 med), 3 refuted | 0/1/1/0 | 6 | — | [report](runs/2026-06-16-elastic-drift-indexer-defects.html) |
| 2026-06-15 | TDD-002 | Suite minus party (GraphQL vs Playwright) | Account merge untested; 4 @authorize-gated mutations' authz entirely untested | 5/7/~28/~22 | 1 | CI-7764 | [report](runs/2026-06-15-coverage-gap-scan-whole-suite-no-party.html) |
| 2026-06-15 | TDD-001 | Party subsystem (GraphQL vs Playwright) | Party write paths covered; gaps cluster in merge-preview/duplicate-detection read flow | 0/4/7/3 | 4 | CI-7633, CI-7760, CI-7707 | [report](runs/2026-06-15-coverage-gap-scan-party.html) |

> **Backfill provenance (2026-06-18):** TDD-001…003 were re-filed verbatim from `.claude/analysis/`
> (`/coverage-gap-scan` + `/elastic-drift` outputs) — originals left in place; copied byte-for-byte,
> so these `.html` files carry **no embedded `tdd-meta` comment** (that's emitted only by native runs).
> Flags: TDD-002 M/L counts are approximate in the source (`~`); TDD-003's tally counts **confirmed**
> findings only (3 additional candidates were adversarially refuted). Verdicts/severities extracted
> from each report, not inferred.

> **Score column backfill (2026-07-03):** the `Score` column was added when the Overall Ranking landed;
> every existing row's score was derived mechanically by applying the `skill.md` Phase 3 band to its
> already-recorded C/H/M/L tally (not re-judged). New runs set it at Phase 3.
