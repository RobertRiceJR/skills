# TDD Report Components — Catalog & Spec

> Read by Phase 4.1 of `technical-due-diligence/skill.md` when rendering the HTML report.
> **`_shared/output-kit/igs-brand.json` (brand + semantic tokens) and `_shared/output-kit/report.css`
> (component CSS) are the SSOT.** This file is the human-readable spec of what the components mean and
> how to use them — *not* a second copy of the styles (the TDD-021 F-A1 "don't duplicate the SSOT"
> rule; re-inventing tokens is bug-patterns #19). Never put a raw hex in a report — reach for a class.
> Source of the shell = `_shared/output-kit/report-template.html`.

TDD reports **inline** `report.css` into a `<style>` block (self-contained, per `skill.md:232`). Every
class below is therefore available in the emitted file with no external asset. All components are
`var()`-driven, so the opt-in dark theme (`<html data-theme="dark">`) and `@media print` fallbacks work
automatically — except the code card, which is deliberately dark-chrome and carries its own print flip.

---

## SSOT change protocol

To add or change a color:
1. Edit `igs-brand.json` first (the canonical value + a `_use` note).
2. Mirror the value into the matching `--token` in `report.css` `:root` **and** `:root[data-theme="dark"]`.
3. Add the `@media print` fallback if the component is dark-on-dark.
4. Then update this doc's snippet.

The score heatmap (`--s1`–`--s10`) is a rendering concern **owned by `report.css`**, intentionally not
in `igs-brand.json`.

---

## Layout & structural primitives (pre-existing)

- **`.wrap`** — page container (max-width 1080px, centered). Wrap the whole body once.
- **`header.report`** — the hero banner (ink→accent gradient). Children: `.eyebrow`, `h1`, `p.sub`,
  `.meta` (flex chip row). Always the first block.
- **`h2.section`** — uppercase section heading with a bottom rule. One per report section / dimension.
- **`footer.rep`** — centered muted footer. Last block.

```html
<header class="report">
  <p class="eyebrow">Technical Due Diligence · QE · TDD-NNN</p>
  <h1>{scope}</h1>
  <p class="sub">{one-line framing}</p>
  <div class="meta"><span><b>Prepared for:</b> …</span><span><b>Date:</b> …</span><span><b>Scope:</b> …</span></div>
</header>
```

---

## Legend / key cards (pre-existing)

`.legend` grid of `.item`s, each `.k` (label + `.dot` swatch) + `.d` (description). Use for the C/H/M/L
severity key. **Note:** `.k` and `.d` are scoped under `.legend .item` — do not reuse those bare class
names elsewhere.

```html
<div class="legend">
  <div class="item"><div class="k"><span class="dot" style="background:var(--danger)"></span>Critical</div><div class="d">…</div></div>
</div>
```

---

## Tables (pre-existing)

Wrap every `table` in `.tablecard`. `th.num`/`td.num` center numeric columns. Pair with the signal/noise
row treatment (below) for triage tables.

---

## Score heatmap pills + Overall Ranking (pre-existing pill + new usage)

`.score` + `.s1`…`.s10` — a 1-10 heatmap pill (red→green). Owned by `report.css`.

```html
<span class="score s8">8</span>
```

**Overall Ranking (TDD roll-up).** Render the single subsystem score in the header, next to the C/H/M/L
legend, using a `.score sN` pill — `Overall Ranking: <span class="score s4">4</span>`. `N` is produced
by the deterministic band in `skill.md` Phase 3 (a pure function of the finding profile):

| Finding profile          | Score |
| ------------------------ | ----- |
| any Critical             | ≤ 3  (3 isolated · 1–2 as Criticals/Highs pile on) |
| ≥2 High, no Critical     | 4–5   |
| 1 High, no Critical      | 6     |
| Medium/Low only          | 7–9  (7 many Medium · 9 a few Low) |
| no material findings     | 10    |

The score persists as the `Score` column in `reference/index.md`, so rankings trend across runs.

---

## Tier / status cards + Finding-tier ↔ severity (pre-existing)

`.tier` card with a colored left border + `.badge`. Variants `ok / warn / info / muted`. Each TDD
**Finding block** renders as a tier card. Mapping:

| Severity        | tier class | severity lozenge |
| --------------- | ---------- | ---------------- |
| Critical / High | `warn`     | `lozenge danger` |
| Medium          | `info`     | `lozenge validation` (amber) |
| Low             | `muted`    | `lozenge noise` (neutral) |

```html
<div class="tier warn"><h3><span class="badge">Critical</span> {finding title} <span class="lozenge danger">bug</span></h3>
  <p>…</p></div>
```

---

## Callout (pre-existing)

`.callout` with a `.lbl` label. Use for the verdict / bottom-line-up-front block (top-3 concerns,
anchor-linked to their findings).

---

## Lozenges — legacy + severity variants (harvested)

The **one badge component** — do not add a rival `.pill`. Legacy color variants: `green / blue / amber /
gray`. Harvested severity variants map onto the semantic tokens:

| Class                 | Meaning              | Token    |
| --------------------- | -------------------- | -------- |
| `.lozenge.danger` / `.bug` | critical / bug / discard | `--danger` |
| `.lozenge.validation` | validation / caution | `--warning` |
| `.lozenge.auth`       | auth / info          | `--info` |
| `.lozenge.noise` / `.perf` | noise / muted / perf | `--neutral` |

Optional leading dot: `.lozenge .dot` (inherits the text color).

```html
<span class="lozenge danger"><span class="dot"></span>bug</span>
<span class="lozenge noise">noise</span>
```

**When:** state/severity tags in tables and finding headers. **When not:** a 1-10 ranking — use `.score`.

---

## Signal/noise rows (harvested)

Triage-table row treatment. `tr.noise td` / `li.noise` = dimmed + strikethrough. `tr.signal td` /
`li.signal` = inset accent stripe (`box-shadow`, so it survives `border-collapse`).

```html
<tr class="noise"><td>POST /graphql · 499</td><td>217</td><td>navigation noise</td></tr>
<tr class="signal"><td>checkForDuplicateParties · 200</td><td>4</td><td>masked resolver error</td></tr>
```

**When:** any "keep vs discard" evidence table. **When not:** decorative emphasis — use a lozenge.

---

## Numbered process spine (harvested)

Vertical numbered steps with an auto-incrementing node + connector line (CSS counter — no manual
numbers). Use `.spine` on a `<ol>`/`<ul>`.

```html
<ol class="spine">
  <li><b>Sweep</b> — bucket failing requests by op + resultCode.</li>
  <li><b>Drill</b> — pull the operation_Id.</li>
  <li><b>Join</b> — resolve the exception.</li>
</ol>
```

**When:** a real ordered process/pipeline where sequence carries meaning. **When not:** an unordered list.

---

## Decision gate (harvested)

Two-branch fork. `.gate` grid of `.branch.discard` (danger top-border) / `.branch.promote` (success
top-border). Collapses to one column on mobile.

```html
<div class="gate">
  <div class="branch discard"><h4>Discard</h4><p>fast 499 = navigation noise.</p></div>
  <div class="branch promote"><h4>Investigate</h4><p>op + 200 + success==false = real bug.</p></div>
</div>
```

**When:** a binary classification / triage gate. **When not:** more than two outcomes — use a table.

---

## Code / terminal card (harvested)

Terminal-chrome wrapper around a `<pre>` with light syntax tinting. **Upgrades the bare `<pre>`** TDD
uses for quoted evidence code. Intentionally **dark-chrome in both themes** (like the header gradient);
the `@media print` block flips it to light so it never prints dark-on-dark. Syntax classes are scoped
`.codecard pre .k/.s/.v/.c` (keyword / string / var / comment) — never use them bare (`.k` collides with
`.legend .item .k`; `.s*` with the heatmap).

```html
<div class="codecard">
  <div class="bar"><span class="dot r"></span><span class="dot y"></span><span class="dot g"></span><span class="cap">KQL</span></div>
  <pre><span class="k">requests</span> | <span class="k">where</span> name <span class="k">contains</span> <span class="s">"graphql"</span> <span class="c">// sweep</span></pre>
</div>
```

**When:** quoting a command, query, or evidence code block. **When not:** a single inline token — use `code`.

---

## Note: `component-gallery.html`

`reference/component-gallery.html` renders every component above (light + dark + print) as the living
proof. It is a **reference artifact, NOT a TDD run** — it has no `TDD-NNN`, no `<!-- tdd-meta -->` block,
and no row in `reference/index.md`. Do not register it.
