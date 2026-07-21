# Claude Architect — Capability Ledger Index

This directory is the self-updating knowledge base for the `claude-architect` skill: the
**30-statement CCA-F spine**, one reference file per statement. Read this index + the relevant
dossier(s) at the start of each run. Update both whenever a bit of work lands (skill Phase 4).

> **Source:** CCA-F capability audit, 2026-06-29 — `.claude/analysis/cca-f-capability-audit.html`
> **Last reviewed:** 2026-06-30 (1.1 GAP→PARTIAL — stop_reason-loop spike built; live smoke pending)
> **NTK:** Statements are a distributable paraphrase. Never store verbatim exam text; never ingest the exam PDF.

**Status legend:** `BUILT` = citable artifact does the thing · `PARTIAL` = present but below the bar ·
`GAP` = no evidence found.
**Backlog formula:** impact = domain weight (%) × severity (GAP 2 · PARTIAL 1 · BUILT 0).

---

## Domain roll-up

| Domain | Weight | BUILT | PARTIAL | GAP |
| ------ | ------ | ----- | ------- | --- |
| D1 · Agentic Architecture & Orchestration | 27% | 5 | 2 | 0 |
| D2 · Tool Design & MCP Integration        | 18% | 2 | 3 | 0 |
| D3 · Claude Code Config & Workflows       | 20% | 3 | 2 | 1 |
| D4 · Prompt Engineering & Structured Output | 20% | 5 | 0 | 1 |
| D5 · Context Management & Reliability     | 15% | 4 | 2 | 0 |
| **Total** | **100%** | **19** | **9** | **2** |

---

## Readiness scorecard

A single weighted score for the whole spine, recomputed on every `/claude-architect update` (Phase 4).
It measures **capability coverage** — an evidence-gated proxy — **not** production impact. A flipped
statement only proves "it mattered" once it graduates and moves a real outcome metric (see each dossier's
Depth gap / Build-on). Guard against gaming: the evidence rule (no uncited BUILT) + discriminating gates
(e.g. 1.1's live smoke) mean a status that can't fail doesn't count.

_Derived HTML snapshots under `.claude/analysis/` (audit · executive report · 1.1 deep-dive · spike findings) are **point-in-time**; this scorecard is the readiness SSOT._

**Formula (auditable):** credit `c` = BUILT 1.0 · PARTIAL 0.5 · GAP 0.0. Per-statement weight
`w = domain% ÷ statements-in-domain`. Readiness `R = Σ(w·c) = Σ_domain [ domain% × (creditsᵈ ÷ nᵈ) ]`.
The B/P/G below MUST equal the Domain roll-up above (invariant).

| Domain | Weight | B / P / G | Domain achieved (creditsᵈ ÷ nᵈ) | Weighted contribution |
| ------ | ------ | --------- | ------------------------------- | --------------------- |
| D1 | 27% | 5 / 2 / 0 | 6.0 / 7 = 85.7% | 23.14 |
| D2 | 18% | 2 / 3 / 0 | 3.5 / 5 = 70.0% | 12.60 |
| D3 | 20% | 3 / 2 / 1 | 4.0 / 6 = 66.7% | 13.33 |
| D4 | 20% | 5 / 0 / 1 | 5.0 / 6 = 83.3% | 16.67 |
| D5 | 15% | 4 / 2 / 0 | 5.0 / 6 = 83.3% | 12.50 |
| **Total** | **100%** | **19 / 9 / 2** | — | **78.2%** |

### Readiness time series (append-only — newest last)

| Date | B / P / G | Readiness | GAPs left | What changed |
| ---- | --------- | --------- | --------- | ------------ |
| 2026-06-29 | 19 / 8 / 3 | 76.3% | 3 | Baseline — seeded from the CCA-F audit |
| 2026-06-30 | 19 / 9 / 2 | 78.2% | 2 | 1.1 GAP→PARTIAL — stop_reason-loop spike built (live smoke pending) |

_Next expected move: 1.1 PARTIAL→BUILT on a green live smoke → **80.2%** (19/9/2 → 20/8/2)._

---

## The spine (one line per statement)

### D1 · Agentic Architecture & Orchestration — 27%
| Code | Title | Status | Conf | Next action | File |
| ---- | ----- | ------ | ---- | ----------- | ---- |
| 1.1 | Agentic loop control via stop_reason | PARTIAL | High | Loop proven live via `claude -p` ✓; BUILT needs IGS Anthropic API access (IT-gated) → SDK smoke | `d1-agentic-orchestration/1.1-stop-reason-loop.md` |
| 1.2 | Coordinator–subagent orchestration | BUILT | High | Prototype complexity-based dynamic routing in deep-research.js | `d1-agentic-orchestration/1.2-coordinator-subagent-orchestration.md` |
| 1.3 | Subagent spawning & context passing | BUILT | High | Promote agent-dispatch-template into ≥1 production skill | `d1-agentic-orchestration/1.3-subagent-spawning-context-passing.md` |
| 1.4 | Multi-step workflow enforcement | BUILT | High | (meets bar) optional machine-checkable gate assertion | `d1-agentic-orchestration/1.4-multi-step-workflow-enforcement.md` |
| 1.5 | Agent SDK hooks | BUILT | High | Add a PostToolUse transform hook example | `d1-agentic-orchestration/1.5-agent-sdk-hooks.md` |
| 1.6 | Task decomposition | BUILT | High | Add adaptive re-plan-on-dry to deep-research | `d1-agentic-orchestration/1.6-task-decomposition.md` |
| 1.7 | Session state, resumption & forking | PARTIAL | Med | Extend /resume with fork_session + fresh-summary check | `d1-agentic-orchestration/1.7-session-state-resumption-forking.md` |

### D2 · Tool Design & MCP Integration — 18%
| Code | Title | Status | Conf | Next action | File |
| ---- | ----- | ------ | ---- | ----------- | ---- |
| 2.1 | Tool interface design | BUILT | High | (meets bar) | `d2-tool-mcp/2.1-tool-interface-design.md` |
| 2.2 | Structured MCP error responses | PARTIAL | High | Wrap one tool path in an {isError,errorCategory,isRetryable} envelope | `d2-tool-mcp/2.2-structured-mcp-error-responses.md` |
| 2.3 | Tool distribution & tool_choice | PARTIAL | High | Spike a forced/any tool_choice call | `d2-tool-mcp/2.3-tool-distribution-tool-choice.md` |
| 2.4 | MCP server integration & scoping | BUILT | High | Add ${ENV} expansion + one MCP resource read to .mcp.json | `d2-tool-mcp/2.4-mcp-server-integration-scoping.md` |
| 2.5 | Built-in tool selection | PARTIAL | Med | Write a built-in tool selection matrix | `d2-tool-mcp/2.5-built-in-tool-selection.md` |

### D3 · Claude Code Configuration & Workflows — 20%
| Code | Title | Status | Conf | Next action | File |
| ---- | ----- | ------ | ---- | ----------- | ---- |
| 3.1 | CLAUDE.md hierarchy & modular org | PARTIAL | High | Convert reference tables to @import + add a .claude/rules/ file | `d3-config-workflows/3.1-claudemd-hierarchy-modular-org.md` |
| 3.2 | Custom slash commands & skills (frontmatter) | PARTIAL | High | Add allowed-tools + argument-hint to high-traffic skills | `d3-config-workflows/3.2-custom-slash-commands-skills.md` |
| 3.3 | Path-specific rules | GAP | High | Add a paths:-scoped auto-loading rule | `d3-config-workflows/3.3-path-specific-rules.md` |
| 3.4 | Plan mode vs direct execution | BUILT | High | (meets bar) | `d3-config-workflows/3.4-plan-mode-vs-direct-execution.md` |
| 3.5 | Iterative refinement | BUILT | High | (meets bar) | `d3-config-workflows/3.5-iterative-refinement.md` |
| 3.6 | Claude Code in CI/CD | BUILT | High | Add a claude -p --output-format json gate step to .azpl | `d3-config-workflows/3.6-claude-code-in-cicd.md` |

### D4 · Prompt Engineering & Structured Output — 20%
| Code | Title | Status | Conf | Next action | File |
| ---- | ----- | ------ | ---- | ----------- | ---- |
| 4.1 | Explicit-criteria prompts | BUILT | High | (meets bar) | `d4-prompt-structured-output/4.1-explicit-criteria-prompts.md` |
| 4.2 | Few-shot prompting | BUILT | High | (meets bar) | `d4-prompt-structured-output/4.2-few-shot-prompting.md` |
| 4.3 | Structured output via tool_use + JSON schema | BUILT | High | Adopt --json-schema (or forced tool_use) in a claude -p path | `d4-prompt-structured-output/4.3-structured-output-json-schema.md` |
| 4.4 | Validation / retry / feedback loops | BUILT | High | (meets bar) | `d4-prompt-structured-output/4.4-validation-retry-feedback-loops.md` |
| 4.5 | Message Batches API strategy | GAP | High | Spike Batches API for the spec-quality sweep | `d4-prompt-structured-output/4.5-message-batches-api.md` |
| 4.6 | Multi-instance & multi-pass review | BUILT | High | (meets bar) | `d4-prompt-structured-output/4.6-multi-instance-multi-pass-review.md` |

### D5 · Context Management & Reliability — 15%
| Code | Title | Status | Conf | Next action | File |
| ---- | ----- | ------ | ---- | ----------- | ---- |
| 5.1 | Context preservation across long interactions | BUILT | High | Trim verbose MCP output before persisting to ticket.md | `d5-context-reliability/5.1-context-preservation.md` |
| 5.2 | Escalation & ambiguity resolution | PARTIAL | High | Encode escalation gates as in-skill steps | `d5-context-reliability/5.2-escalation-ambiguity-resolution.md` |
| 5.3 | Error propagation across agents | PARTIAL | Med | Define a shared structured error-context schema | `d5-context-reliability/5.3-error-propagation-across-agents.md` |
| 5.4 | Context mgmt in large-codebase exploration | BUILT | High | (meets bar) optional /compact triggers | `d5-context-reliability/5.4-context-mgmt-large-codebase.md` |
| 5.5 | Human review & confidence calibration | BUILT | High | Stratified prod-output sampling + grow golden set | `d5-context-reliability/5.5-human-review-confidence-calibration.md` |
| 5.6 | Provenance & multi-source synthesis | BUILT | High | (meets bar) | `d5-context-reliability/5.6-provenance-multi-source-synthesis.md` |

---

## Build backlog — ranked by impact (weight × severity)

The single highest-leverage move is on top. Open items only (BUILT-at-bar excluded).

| # | Code | Title | Status | Impact | Smallest next step | Effort | Handoff |
| - | ---- | ----- | ------ | ------ | ------------------ | ------ | ------- |
| 1 | 3.3 | Path-specific rules | GAP | 40 (20×2) | add a `paths:`-scoped rule/skill auto-loading for a glob (e.g. src/tests/**) | S | /skill-creator + config |
| 2 | 4.5 | Message Batches API strategy | GAP | 40 (20×2) | route the spec-quality / dup sweeps through the Batches API (custom_id, 24h, 50%) | M | spike + scripts/llm-judge |
| 3 | 1.1 | Agentic loop control via stop_reason | PARTIAL | 27 (27×1) | `claude -p` loop smoke ✓ done; BUILT needs IGS Anthropic API access (IT-gated) → SDK smoke | S | IT provisioning + ~/.claude/spikes/agentic-loop-stop-reason/ |
| 4 | 1.7 | Session state, resumption & forking | PARTIAL | 27 (27×1) | extend /resume to use --resume / fork_session + a fresh-vs-stale summary check | M | .claude/skills/resume/ |
| 5 | 3.1 | CLAUDE.md hierarchy & modular org | PARTIAL | 20 (20×1) | @import the big reference tables + add a `.claude/rules/` file | S | CLAUDE.md + .claude/rules/ |
| 6 | 3.2 | Custom slash commands & skills | PARTIAL | 20 (20×1) | add `allowed-tools` + `argument-hint` (+ `context: fork`) to high-traffic skills | S | skill SKILL.md files |
| 7 | 2.2 | Structured MCP error responses | PARTIAL | 18 (18×1) | wrap one tool path in a structured {isError,errorCategory,isRetryable} envelope | M | net-new wrapper / fixtures |
| 8 | 2.3 | Tool distribution & tool_choice | PARTIAL | 18 (18×1) | a claude -p / SDK example invoking tool_choice (forced + any) | S | spike |
| 9 | 2.5 | Built-in tool selection | PARTIAL | 18 (18×1) | a Read/Write/Edit/Bash/Grep/Glob selection matrix | S | _shared/templates/code/patterns-quickref.md |
| 10 | 5.2 | Escalation & ambiguity resolution | PARTIAL | 15 (15×1) | encode escalation criteria (3-fail gate, approval gate) as explicit in-skill steps | S | skill bodies |
| 11 | 5.3 | Error propagation across agents | PARTIAL | 15 (15×1) | a shared structured error-context schema + coordinator recovery policy | M | net-new + deep-research.js |

> BUILT-at-bar statements (no open backlog item): 1.4, 2.1, 3.4, 3.5, 4.1, 4.2, 4.4, 4.6, 5.4, 5.6.
> BUILT-with-hardening items (below the cut line, optional): 1.2, 1.3, 1.5, 1.6, 2.4, 3.6, 4.3, 5.1, 5.5.
