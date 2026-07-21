---
name: skill-evolve
description: >
    Blast-radius-aware skill improvement orchestrator for a Claude Code skill ecosystem. Use when
    changing an existing skill in a way that could ripple downstream — renaming it, changing its
    argument/contract, re-optimizing its description/trigger, restructuring its body, or
    deprecating/deleting it. Computes the blast radius and a file-level propagation checklist BEFORE
    the edit (from the skill dependency graph), wraps the Anthropic skill-creator for description
    optimization with anti-shadowing, and VERIFIES nothing broke after (ref integrity + duplication
    drift + type-check). This is the safe way to "make a skill better as the models improve" without
    manually tracking every dependent file. Per-area gates, sync-style. Triggers: "evolve this skill",
    "improve this skill safely", "rename this skill", "what breaks if I change this skill",
    "blast radius of this skill", "/skill-evolve". For a one-off blast-radius lookup with no edit,
    run `npm run skill:impact` directly; for creating a NEW skill use /skill-creator.
user_invocable: true
argument: '<skill-name> --change <rename|contract|description|content|deprecate|delete> [--apply] (e.g., zephyr-reporter --change rename)'
---

# Skill-Evolve — blast-radius-aware skill improvement

> **Portability.** This skill was built for a project (IMA-360) that ships a skill-tooling chain —
> `npm run skill:graph | skill:refs | skill:impact | skill:templates:check`, a generated
> `_shared/skill-graph.json`, and `_shared/scripts/*`. **That tool-chain is the reference
> implementation, not a hard requirement.** When the current project provides it, use it. When it
> does not (the common case), degrade to the manual equivalent below and **never hard-stop on a
> missing `npm run skill:*` command:**
> - **Blast radius / impact** (replaces `skill:graph` + `skill:impact`): grep the skills tree and
>   docs for the target's references — `grep -rn "/<name>" .claude/skills plugins CLAUDE.md MEMORY.md`
>   (and its `name:`/folder) — and treat the count of referencing **files** as the severity
>   (Critical ≥10 · High 5–9 · Medium 2–4 · Low 1).
> - **Ref integrity** (replaces `skill:refs`): after any edit, re-grep for now-dangling `/<name>`
>   references; zero dangling = clean.
> - **Eval-set build + dup-drift judge** (replaces `_shared/scripts/build-eval-set.mjs` /
>   `scripts/llm-judge/*`): use the `eval-judge` plugin's `skill-creator` scripts and `llm-judge`
>   if available; otherwise skip that optional gate and say so in the report.
> - `_shared/skill-architecture.md`, `CLAUDE.md`, and `MEMORY.md` propagation steps apply **only
>   where the project has those files** — skip the absent ones, don't fake them.

The skill ecosystem is **orchestrators calling leaf workers**, wired by `/name` delegations, `_shared/`
references, `_index.yml` routing, frontmatter contracts, and **duplicated context blocks** (skills copy
shared context instead of importing it). Changing one skill can silently strand any of those edges.
This orchestrator makes a change **safe**: it reads the dependency graph, shows the blast radius +
a propagation checklist, helps make the change, propagates the mechanical updates behind a gate, and
verifies the tree is still consistent.

It never edits a skill silently and never cascades — every apply step is gated, mirroring `/sync`.

**Data layer (all read-only except where noted):**

- `npm run skill:graph` — regenerate `_shared/skill-graph.json` (the dependency-graph SSOT; codifies the reference census).
- `npm run skill:refs` — integrity gate (dangling `/name`, broken `_shared/` paths, name/folder mismatch).
- `npm run skill:templates:check` — template-fidelity gate (stale fixture spelling / embedded API test body / hard-wait anti-pattern in skill docs, per `bug-patterns.md` #19). Advisory.
- `npm run skill:impact -- --skill <X> --change <type>` — blast radius + per-change-type propagation checklist.
- `node .claude/skills/_shared/scripts/build-eval-set.mjs --skill <X>` — `/skill-creator` eval set with sibling anti-shadow negatives.
- duplication-drift judge on the skill's inline copies vs canonical `_shared/` sources. **Keyless default:** `node scripts/llm-judge/run-dup-sweep.ts --emit-pairs --skill <X>` → grade the emitted pairs via subagents (DD1 ×3 / DD2 / DD3 from `dimensions.json`), flag mean DD1 < floor. (`npm run judge:dup-sweep` is the promptfoo/keyed alternative.) See `judges/dup-drift/README.md` § Keyless grading.

---

## Phase 0 — Preflight (baseline must be clean)

1. `npm run skill:graph` — regenerate the graph so impact reflects current disk.
2. `npm run skill:refs` — the tree must be **clean (0 blocking)** before you change anything.
   - If it reports broken refs, STOP and surface them: you'd be evolving on top of existing drift.
     Fix or get sign-off first. (Advisories are fine — they're historical/planned/runtime.)
3. Confirm the target is a real skill (`skill:impact` errors with near-name suggestions if not).

## Phase 1 — Impact (the gate)

Run `npm run skill:impact -- --skill <X> --change <type>` and present its output verbatim:

- the **severity** (Critical ≥10 referencing files · High 5–9 · Medium 2–4 · Low 1),
- the **referencing-file list** (the blast radius), and
- the **propagation checklist** for the chosen change type.

**GATE.** Show the user the blast radius and the plan. Do not proceed to edits without a go-ahead
(or `--apply`, which is a standing go-ahead for THIS run only — still gate each apply area in P3).

## Phase 2 — Improve

Branch on `--change`:

- **description** — re-optimize the trigger string with anti-shadowing:
  1. `node .claude/skills/_shared/scripts/build-eval-set.mjs --skill <X> --out <scratchpad>/<X>.eval.json`
     (negatives are drawn from sibling skills so the optimizer can't broaden into their triggers).
     If it warns the should_trigger set is thin, ADD natural-language queries that should route to `/<X>` before optimizing.
  2. Invoke `/skill-creator` in optimize mode against that eval set; apply the returned `best_description` to the frontmatter.
- **content / structure** — make the body edits. Then run the duplication-drift judge to catch any
  inline duplicated block that now contradicts its canonical `_shared/` source (score-only; you fix).
  Keyless: `node scripts/llm-judge/run-dup-sweep.ts --emit-pairs --skill <X>` → grade each emitted pair
  via a subagent per dimension (frame from `promptfooconfig.yaml`, criteria from `dimensions.json`),
  flag mean DD1 < floor. (`npm run judge:dup-sweep` is the keyed/promptfoo alternative.)
- **contract** — change `argument:`; the P1 checklist already lists the callers that pass positional args (and the `--phase` caveat for `/context-load`).
- **rename / deprecate / delete** — no body edit here; the change IS the propagation in P3.

## Phase 3 — Propagate (per-area gate, never cascade)

Work the P1 checklist. Apply mechanical updates **one area at a time, gating each** (mirror `/sync` Phase 3):

1. The referencing files (update / repoint / remove the `/<X>` ref in each listed file).
2. `_shared/skill-architecture.md` routing tables (decision tree + sub-skill/standalone tables).
3. `CLAUDE.md` (project + global) skill lists.
4. `MEMORY.md` pointers (not graph-scanned — check by hand).
5. For **rename**: rename the folder and frontmatter `name:`. For **deprecate**: add a deprecation note
   so the integrity gate treats incoming refs as advisory (historical-marker line). For **delete**:
   every incoming ref must be repointed/removed first.

## Phase 4 — Verify (prove the tree is still consistent)

1. `npm run skill:graph` — regenerate; eyeball the incoming-count delta for the changed skill and its referrers.
2. `npm run skill:refs` — must be **clean (0 blocking)**. Any new dangling ref = an incomplete propagation; go back to P3.
3. `npm run skill:templates:check` — no newly-introduced template-fidelity advisories (stale fixture spelling / embedded test body / hard wait) from this edit. Advisory — investigate any new hit, don't auto-ignore.
4. duplication-drift check on `<X>` (keyless: `run-dup-sweep.ts --emit-pairs --skill <X>` → subagent-grade) — no newly-flagged stale inline copies (PROVISIONAL until the dup judge is calibrated).
5. `npm run type-check` — scripts/config still compile.
6. Report: what changed, what is now consistent, and anything that still needs human judgment.

---

## Relationship to other skills

- **`/skill-creator`** (global) optimizes ONE skill's description in isolation and is blind to the
  ecosystem — this orchestrator wraps it with the eval-set anti-shadowing + the before/after blast-radius guard.
- **`/sync`** delegates its "skill-graph & duplication-drift" apply area here.
- **`/sync-skills`** consumes the same `skill-graph.json` for impact-ranked drift reporting.
- For creating a brand-new skill, use `/skill-creator`. For a read-only blast-radius lookup, run `npm run skill:impact` directly.

> Self-contained by the duplication rule: this body restates the contract it needs. Canonical sources —
> `_shared/skill-architecture.md` (routing), `_shared/skill-graph.json` (generated dependency SSOT),
> `.claude/skills/_shared/scripts/` (the data-layer scripts), `scripts/llm-judge/run-dup-sweep.ts` (dup judge).
