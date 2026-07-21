---
name: todo
description: >
    Manage the repo's canonical task list at repo-root `TODO.md`. Default (no argument)
    reads the file and surfaces In Progress first, then a compact digest of open items by
    section. Also adds new items to the right section, checks off / archives done items to
    Recently Completed (strikethrough audit trail), and bumps the Last triage date. This is
    THE answer to "check the todo" / "what's on my todo" / "add to the todo" / "mark X done".
    Lightweight and self-contained — no MCP, no orchestrator, reads/writes one file.
user_invocable: true
argument: '"" (view) | "add <text> [to <section>]" | "done <match> [— <ref>]" | "triage"'
---

# /todo — Repo Task List

GLOBAL skill — the canonical task list lives at the **current repo's root**: `TODO.md`.
Resolve its path dynamically: use the git toplevel of the current working directory
(`git rev-parse --show-toplevel`) and look for `TODO.md` there; if there's no git root, fall back
to `TODO.md` in cwd. Do **not** hardcode a project path.

This is the single answer when the user says "check the todo." Do not invent another location,
do not use the ephemeral `TodoWrite` tool for this, and do not conflate it with any MEMORY.md
"Active Work" section (that's session memory; this is the durable backlog).

## File shape (read it, don't impose it)

**Always match whatever `##` headers the target `TODO.md` actually has** — never silently drop,
rename, or reorder one, and never force a fixed section set. A representative layout (from one
project; treat as illustrative only):

```
# <Project> TODO
_Last triage: YYYY-MM-DD_

## In Progress
## Open — <theme>          ← zero or more themed "Open" buckets, project-specific
## Future / Research
## Recently Completed (last ~2 weeks)
```

If the file doesn't exist yet and the user adds an item, create it with a minimal
`# TODO` + `## In Progress` + `## Recently Completed` skeleton.

- Open items: `- **<Title>** — <body, wrapped>`. Rich detail goes in 4-space-indented
  sub-bullets under the item (match the style of existing entries in the file).
- Completed items: `- ~~**<Title>**~~ — <ref>` (PR #, commit sha, or memory pointer).
  Strikethrough is the audit trail — never delete a completed item during a normal `done`.

## Routing — read the argument

| Argument                          | Mode                          |
| --------------------------------- | ----------------------------- |
| _(empty)_, `view`, `show`, `list` | **VIEW** (default)            |
| `add <text> [to <section>]`       | **ADD**                       |
| `done <match> [— <ref>]`          | **DONE** (check off)          |
| `triage`                          | **TRIAGE**                    |

Be autonomous — do not ask "should I proceed?" between steps. Ask only when ADD section
inference is genuinely ambiguous, or when DONE matches zero / multiple items.

---

## VIEW (default)

1. Read `TODO.md`.
2. Output a **compact digest**, not the whole file:
   - **In Progress** — every item's full title + a one-line gist (this is what matters most).
   - For each `Open — *` section: the count and a bare title list (no bodies).
   - **Future / Research** — count only, titles on request.
   - Footer: `Last triage: <date>` and total open count.
3. Offer: "Say `/todo <section>` to expand a section, or `/todo add …` / `/todo done …`."

Keep it scannable. The point is a fast answer, not a file dump.

---

## ADD

1. Parse the new item text. First read the file's **actual** `##` headers, then determine the target:
   - Explicit `to <section>` wins (fuzzy-match to a real `##` header).
   - Else infer by matching the item's theme to the **existing** section names — pick the section
     whose title/topic best fits (e.g. an item about "research/explore/investigate" → a
     Future/Research-style section; something actively being worked → an In Progress-style section;
     a themed item → the matching `Open — <theme>` bucket if one exists).
   - If no existing section fits, default to the most general open section (In Progress if nothing
     better), and mention that no themed bucket matched.
   - If inference is a coin-flip between two sections, ask which one (one question).
2. Append `- **<Title>** — <body>` under the chosen section, matching surrounding style.
   Derive a short bold title from the text if the user didn't give one.
3. State which section it landed in. Done.

---

## DONE (check off)

1. Fuzzy-match `<match>` against open-item titles/bodies across all sections.
   - 0 matches → report, list nearest titles, stop.
   - >1 match → list them, ask which (one question).
2. Move the matched bullet to **Recently Completed**:
   - Wrap its title in `~~ ~~`, collapse multi-line bodies to a single trailing clause.
   - Append `— <ref>` if the user supplied a PR/commit/memory pointer.
   - Drop it into the most fitting Completed sub-group if subheadings exist
     (Skills shipped / Infrastructure / Migrations / …), else just under the section header.
3. Remove the original bullet (and its sub-bullets) from its open section.
4. Confirm: "Moved **<Title>** → Recently Completed."

---

## TRIAGE

1. Bump `_Last triage:_` to today's date.
2. Report: open count per section, and items in **Future / Research** untouched for a long
   time (candidates to promote or cut).
3. **Recently Completed** older than ~2 weeks: list them and ask before pruning — these are
   the audit trail. Prune only on explicit yes.
4. Summarize what changed.

---

## After any write

- No type-check needed (markdown only).
- Do not commit — show the user the change; they commit on their own cadence
  (`git diff TODO.md`).
