# Operationalising Entity Resolved Graphs — Workshop Content

## Project

Joint **Senzing + GraphAware** workshop for the **Bridge meetup, 2026**.

Title: *Operationalising Entity Resolved Graphs*.

Co-presenters: Christophe Willemsen (GraphAware CTO) and Paco (Senzing). Paco is the source of truth for anything Senzing-internal.

## What this repo is for

This repo is the **content workspace** for the workshop. We draft prose, speaker notes, and supporting assets here, one section at a time. Slides are generated **elsewhere** by a separate repo/agent that consumes the Markdown produced here.

Out of scope for this repo:
- Slide layouts, decks, visual designs.
- Image rendering (diagrams stay as Mermaid or ASCII; the slide repo handles rendering).

## Layout

```
take1/                                 frozen previous iteration — do NOT edit
  sections/                            13 section files from the pre-phase outline
  assets/                              supporting assets for take1

take2/                                 ACTIVE iteration — current source of truth
  sections/                            13 phase-based section files (00 → 12)
    00-running-order.md                canonical workshop spine + per-section budget
    01-intro.md … 12-phase6-…          one .md per section, primary unit of work
  assets/
    data/                              illustrative CSVs + min_aml/ (real Paco data)
      min_aml/                         Senzing-formatted JSONL (open-ownership.json,
                                         open-sanctions.json) — used live in Sections
                                         06, 07, 08, 09, 11
    diagrams/                          Mermaid sources + rendered PNGs
    snippets/                          Senzing JSON examples, Cypher mappings
  TODOS.md                             central inbox of open questions + missing
                                         assets, grouped by section, owner-tagged

references/                            external pointers (min_aml, prior talks)
scratch.md                             original outline + updated outline — read-only
CLAUDE.md                              this file
```

**Versioning convention:** the workshop has been iterated more than once. Older
iterations land in `takeN/` directories and are preserved as references; the
highest-numbered `takeN/` is the active source of truth. Today that is `take2/`.
Do not edit older takes. If a new iteration is needed, create `take3/` and copy
forward — never overwrite history.

## Section file template

Every `take2/sections/*.md` follows this structure. Keep it consistent so the downstream slide agent has a predictable shape.

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
been **centralised** into `take2/TODOS.md`, grouped by section and tagged by
owner (`Paco` / `Christophe` / `Joint`). The block in each section file is now a
pointer, not a list. When new open questions surface during editing, add them to
`take2/TODOS.md` under the relevant section heading — do not re-populate the
in-section block.

**Inline narrative hedges.** A `> [verify with Paco]` blockquote inside the
narrative body — qualifying a specific claim for the reader — is still allowed
and useful. Those are speaking voice; they stay in place. The TODOs file
captures the same item as a planning task. The two are not duplicates of
each other; they serve different audiences.

## Voice and tone

- **First-person plural** — "we push records to Senzing", not "you push records".
- **Pragmatic engineer**, not vendor pitch. Concrete examples beat abstractions.
- **Name failure modes openly**. The GraphAware brand is "we say what breaks". Caribbean street geocoding to India, Arabic↔English alignment edge cases, redo storms — these are the stories worth telling.
- **Senzing is a partner, and a great ER engine**. The workshop is explicitly here to explain how it works — Paco leads the deep dive in Section 06. Do *not* describe Senzing as a "black box", "something we operate but do not understand", or anything else that hedges on the explanation. When in doubt about a specific internal, mark `> [verify with Paco]` and let Paco fill in — never substitute a hedge for an explanation.

## Scope discipline

- **Do not invent Senzing behaviour.** If you're unsure how Senzing handles something (redo triggers, idempotence semantics, internal feature weighting), add it to `take2/TODOS.md` under the relevant section, *and* optionally drop a `> [verify with Paco]` blockquote inline at the point in the narrative where the uncertainty bites. Never substitute a hedge for an explanation.
- **Do not propose slide structure or visual design.** That's the downstream repo's job.
- **Do not over-engineer.** No custom agents, hooks, or build tooling unless Christophe asks. The repo is prose + small assets.

## Key references

- **min_aml dataset** — Paco supplied the Senzing-formatted version directly. Lives at `take2/assets/data/min_aml/open-ownership.json` (316 UK beneficial-ownership records) and `take2/assets/data/min_aml/open-sanctions.json` (24 sanctioned-entity records). Each line is one Senzing input record (JSON Lines). See `references/min_aml.md` for the per-record citations used in the sections.
- **Hume 3** — GraphAware's product. Section 12 (Phase 6 — Consumption) reveals the *Smart ER in Advanced Expand* feature; further Hume 3.0 features for the reveal are still on Christophe to confirm (see `take2/TODOS.md`).
- **Running order** — `take2/sections/00-running-order.md` is the canonical workshop spine: per-section minute budget, transition cues, audience-pause placement, speaker-swap suggestion. Update it whenever section content shifts time materially.
