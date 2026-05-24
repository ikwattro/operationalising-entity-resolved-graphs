# Operationalising Entity Resolved Graphs — Workshop Content

## Project

Joint **Senzing + GraphAware** workshop for the **Bridge meetup, 2026**.

Title: *Operationalising Entity Resolved Graphs*.

Co-presenters:
- **Paco Nathan** ([@ceteri](https://github.com/ceteri)) — Principal Developer Relations Engineer at Senzing. Paco is the source of truth for anything Senzing-internal.
- **Christophe Willemsen** ([@ikwattro](https://github.com/ikwattro)) — CTO at GraphAware.

## What this repo is for

This repo is the **content workspace** for the workshop: speaker notes, section prose, supporting assets, Senzing API examples, and the Marp-based slide deck. We draft content here, one section at a time.

## Layout

```
notes/                                 ACTIVE content — primary source of truth
  sections/                            13 section files (00 → 12)
    00-running-order.md                canonical workshop spine + per-section budget
    01-intro.md … 12-phase6-…          one .md per section, primary unit of work
  assets/
    data/                              illustrative CSVs + min_aml/ (Senzing JSONL)
      min_aml/                         Senzing-formatted JSONL (open-ownership.json,
                                         open-sanctions.json) — used live in sections
                                         06, 07, 08, 09, 11
    diagrams/                          Mermaid sources + rendered PNGs
    snippets/                          Senzing JSON examples, Cypher mappings
  TODOS.md                             central inbox of open questions + missing
                                         assets, grouped by section, owner-tagged

how/                                   Senzing WHY / HOW API examples
  explain_how.py                       renders a HOW response JSON to HTML
  explain_why.py                       renders a WHY response JSON to HTML
  senzing-*.json                       example API responses
  *-report.html                        rendered HTML outputs

mappings/                              Python mapping code: graph records → Senzing JSON
  mapping.py                           base mapping template (used in Hume pipelines)
  mapping_person.py                    person-specific mapping
  mapping_organization.py             org-specific mapping

slides/                                Marp slide deck (self-contained sub-project)
  slides.md                            master slide source
  CLAUDE.md                            slide-specific instructions for Claude
  README.md                            how to build and preview the deck
  Makefile                             build targets (dev, build, pdf)

references/                            external data references (min_aml, prior talks)
screenshots/                           screenshots used in the README and slides
_tmp/                                  gitignored scratch space (only .gitkeep tracked)
CLAUDE.md                              this file
```

## Section file template

Every `notes/sections/*.md` follows this structure. Keep it consistent.

```markdown
# <section title>

> **We are here:** <which region of the master architecture this phase highlights>

## Narrative
<Prose to present. First-person plural ("we"). Pragmatic, concrete.>

## Speaker notes
<Asides, anecdotes, transitions, things to say but not show on screen.>

## Assets
<Bullet list linking to anything under assets/ used by this section.
 e.g. - `assets/data/min_aml/open-sanctions.json` — record NK-… cited inline>

## Open questions
Moved to [`../TODOS.md`](../TODOS.md).
```

**Open questions / TODOs convention.** Per-section "Open questions" blocks have
been **centralised** into `notes/TODOS.md`, grouped by section and tagged by
owner (`Paco` / `Christophe` / `Joint`). The block in each section file is now a
pointer, not a list. When new open questions surface during editing, add them to
`notes/TODOS.md` under the relevant section heading — do not re-populate the
in-section block.

**Inline narrative hedges.** A `> [verify with Paco]` blockquote inside the
narrative body — qualifying a specific claim for the reader — is still allowed
and useful. Those are speaking voice; they stay in place. The TODOs file
captures the same item as a planning task. The two are not duplicates of
each other; they serve different audiences.

## Voice and tone

- **First-person plural for presenter actions** — "we walk through", "we are using the min_aml dataset". Use **"you"** when addressing the audience's own practice — "you pay for poor data quality", "you keep both records", "you hand off to Senzing". The notes are the source for slides; the audience reads "you", not "we".
- **Pragmatic engineer**, not vendor pitch. Concrete examples beat abstractions.
- **Name failure modes openly**. The GraphAware brand is "we say what breaks". Caribbean street geocoding to India, Arabic↔English alignment edge cases, redo storms — these are the stories worth telling.
- **Senzing is a partner, and a great ER engine**. The workshop is explicitly here to explain how it works — Paco leads the deep dive in Section 06. Do *not* describe Senzing as a "black box", "something we operate but do not understand", or anything else that hedges on the explanation. When in doubt about a specific internal, mark `> [verify with Paco]` and let Paco fill in — never substitute a hedge for an explanation.

## Scope discipline

- **Do not invent Senzing behaviour.** If you're unsure how Senzing handles something (redo triggers, idempotence semantics, internal feature weighting), add it to `notes/TODOS.md` under the relevant section, *and* optionally drop a `> [verify with Paco]` blockquote inline at the point in the narrative where the uncertainty bites. Never substitute a hedge for an explanation.
- **Do not over-engineer.** No custom agents, hooks, or build tooling unless Christophe asks. The repo is prose + small assets.
- **Do not touch `slides/` unless Christophe explicitly asks.** The default workspace is `notes/sections/`. Never edit `slides/slides.md` or any file under `slides/` as a side-effect of working on notes content.

## Key references

- **min_aml dataset** — Paco supplied the Senzing-formatted version directly. Lives at `notes/assets/data/min_aml/open-ownership.json` (316 UK beneficial-ownership records) and `notes/assets/data/min_aml/open-sanctions.json` (24 sanctioned-entity records). Each line is one Senzing input record (JSON Lines). See `references/min_aml.md` for the per-record citations used in the sections.
- **Hume 3** — GraphAware's product. Section 12 (Phase 6 — Consumption) reveals the *Smart ER in Advanced Expand* feature; further Hume 3.0 features for the reveal are still on Christophe to confirm (see `notes/TODOS.md`).
- **Running order** — `notes/sections/00-running-order.md` is the canonical workshop spine: per-section minute budget, transition cues, audience-pause placement, speaker-swap suggestion. Update it whenever section content shifts time materially.

## Working with the slides

The `slides/` directory is a self-contained Marp project. See `slides/README.md` for build instructions. The slide content is driven by `slides/slides.md`, which is separate from the `notes/` content workspace.

## Gitignore notes

- `scratch.md` — excluded from git; use it freely for personal scratch notes.
- `_tmp/` — excluded from git; only `.gitkeep` is tracked to preserve the directory.
- `.DS_Store` — excluded.
