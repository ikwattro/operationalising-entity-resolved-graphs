# SLIDES-TODO — Manual Input Needed

Generated alongside `slides.md`. Every item below is a placeholder or open decision that requires human input before the deck is presentation-ready.

---

## 1. "We are here" — per-phase architecture highlights

`slides.md` uses `../slides/assets/diagrams/04_master_architecture.png` (the full master diagram) for every "We are here" slide, with a caption naming the phase.

**What is needed:** highlighted variants of the master architecture diagram — one per phase, with the relevant region visually emphasised (bold border, colour wash, or dimmed-out background nodes).

| Slide heading | Region to highlight | Needed file |
|---|---|---|
| Phase 1 — Data In | `SRC → DQ → GIN` | `slides/assets/diagrams/04_arch_phase1.png` |
| Phase 2 — Senzing Fundamentals | `GIN → SZ` | `slides/assets/diagrams/04_arch_phase2a.png` |
| Phase 2 — Graph→Senzing pipeline | `GIN → SZ → GOUT` | `slides/assets/diagrams/04_arch_phase2b.png` |
| OOTB Senzing | inside `SZ` | `slides/assets/diagrams/04_arch_ootb.png` |
| Phase 3 — Living Architecture | `GOUT` (over time) | `slides/assets/diagrams/04_arch_phase3.png` |
| Phase 4 — Explainability | `GOUT → AUDIT` | `slides/assets/diagrams/04_arch_phase4.png` |
| Phase 5 — Trust IDs | `HEUR ⇢ GIN` dotted edge | `slides/assets/diagrams/04_arch_phase5.png` |
| Phase 6 — Consumption | `GOUT → CONS` | `slides/assets/diagrams/04_arch_phase6.png` |

Mermaid source for the master architecture is at `slides/assets/diagrams/04_master_architecture.mmd`. The simplest approach is to use `mermaid-js` theming/classDef to highlight nodes per variant, then render to PNG.

---

## 2. Phase 1 exploded subgraph diagram

**Slide:** "Exploded, not yet resolved" — uses a picsum placeholder.

**What is needed:** a graph diagram showing two `:Record` nodes sharing a `:Passport` node and a `:DOB` node, but **no** `EntityGroup` connecting them.

Mermaid source reference: `slides/assets/diagrams/05_phase1_exploded.mmd` (not yet created — needs to be authored and rendered).

Suggested content:
```
graph LR
  R1[Record KYC-001] --> P[Passport P12345678]
  R1 --> D[DOB 1982-03-14]
  R2[Record WIRE-A12] --> P
  R2 --> D
  style R1 fill:#96D2FF
  style R2 fill:#96D2FF
  style P fill:#CF99FF
  style D fill:#CF99FF
```

**Target file:** `slides/assets/diagrams/05_phase1_exploded.png`
**Slide path to update:** the `img-left` slide with the picsum seed `phase1-exploded`

---

## 3. Source → Record → EntityGroup subgraph diagram

**Slide:** "Source → Record → EntityGroup" — uses a picsum placeholder.

**What is needed:** a graph diagram showing the `EntityGroup` model: one `:Source` node, two or three `:Record` nodes each with a `[:RESOLVED_TO]` edge to one `:EntityGroup`, and each `Record` with a `[:FROM]` edge to the `Source`.

Mermaid source reference: `slides/assets/diagrams/07_eg_record_subgraph.mmd` (not yet created).

Suggested content:
```
graph LR
  SRC[(Source KYC)] --> R1[Record KYC-001]
  SRC --> R2[Record KYC-002]
  R3[Record WIRE-A12] --> SRC2[(Source WIRES)]
  R1 -->|RESOLVED_TO| EG[EntityGroup 1001]
  R2 -->|RESOLVED_TO| EG
  R3 -->|RESOLVED_TO| EG
```

**Target file:** `slides/assets/diagrams/07_eg_record_subgraph.png`
**Slide path to update:** the `img-left` slide with seed `entitygroup-subgraph`

---

## 4. Audit history hypothetical diagram

**Referenced in:** Section 10 narrative and `take2/TODOS.md`.
**Not yet in slides** (described in prose only — no image slide currently).

If a diagram slide is added for the audit-history hypothetical, the Mermaid source would live at `slides/assets/diagrams/10_audit_history_hypothetical.mmd` (not yet created).

Suggested content sketch:
```
graph LR
  REC[Record update] --> CE[ChangeEvent]
  CE --> EG1[EntityGroup — prior state]
  CE --> EG2[EntityGroup — new state]
  OD[OverrideDecision] --> CE
  OD --> REV[Reviewer jdoe]
  SNAP[Snapshot T=2026-04-01] --> EG1
```

---

## 5. Hume 3.0 Smart ER screenshot

**Slide:** "Hume 3.0 — Advanced Expand demo" — uses a picsum placeholder (`seed/hume3-smart-er`).

**What is needed:** a real screenshot or screen recording of the Hume 3.0 Advanced Expand with Smart ER enabled, showing entity-aware neighbourhood navigation from a `Person` node.

- **Source:** Christophe / GraphAware product team
- **Referenced in:** `take2/TODOS.md` under Section 12
- **Target file:** `slides/assets/screenshots/12_hume3_smart_er.png`
- **Slide path to update:** the `img-bottom` slide with seed `hume3-smart-er`

A before/after comparison (standard expand vs. Smart ER expand) would be even stronger if the screen real-estate allows.

---

## 6. Section 06 — Paco's own Senzing internals slides

Section 06 (Senzing Fundamentals) runs 14 minutes and is Paco's block.

`slides.md` provides:
- The three-concept vocabulary slide (Record / Entity / EntityGroup)
- The four-step engine mechanics slide (feature extraction → candidate retrieval → feature scoring → resolution call)
- The configuration model slide
- The input record round-trip slide (JSON from `take2/assets/snippets/06_senzing_input_record.json`)
- The affected-entities round-trip slide (JSON from `take2/assets/snippets/06_senzing_affected_entities.json`)
- The determinism and idempotence slide

**Paco may want to substitute or supplement these with his own Senzing-internal diagrams** — particularly for feature extraction internals, the candidate-retrieval index, and the scoring composition. These slides are structurally complete but may benefit from Paco's own visuals.

**Action:** Paco to review Section 06 slides and provide any supplementary materials.

---

## 7. GraphAware + Senzing "partnership" image

**Slide:** "GraphAware + Senzing: two halves" — uses a picsum placeholder (`seed/ga-senzing-partnership`).

**What is needed:** a clean visual representing the two companies as complementary — could be:
- Official logos side by side with a connecting element
- A simple "graph ↔ resolution" dumbbell diagram
- Something on-brand for a joint presentation slide

This is not critical for the first rehearsal but should be replaced before a public showing.

---

## 8. Updated images-index.md

The `images-index.md` file currently tracks 3 entries from the previous iteration of `slides.md`. It should be updated to reflect all placeholders in the new slide deck.

**Updated index:**

| Slide | Placeholder seed | Description |
|---|---|---|
| "GraphAware + Senzing: two halves" | `ga-senzing-partnership` | Partnership visual — two logos or complementary diagram |
| Phase 1 "Exploded, not yet resolved" | `phase1-exploded` | Subgraph: two Records sharing Passport and DOB nodes, no EntityGroup |
| Phase 2 "Source → Record → EntityGroup" | `entitygroup-subgraph` | Graph schema: Source → Records → EntityGroup via RESOLVED_TO |
| Phase 6 "Hume 3.0 Advanced Expand demo" | `hume3-smart-er` | Real Hume 3.0 screenshot — entity-aware neighbourhood from Person node |

Plus the 8 "We are here" architecture variants in item 1 above.

---

## 9. Snippets not yet in assets

Referenced in section narratives but not yet present in `take2/assets/snippets/`:

| File | Used in | Status |
|---|---|---|
| `07_graph_to_senzing_mapping.cypher` | Section 07 slide | Not yet present — Cypher is shown inline on the slide as-is |
| `10_redo_rate_dashboard.cypher` | Section 10 | Not in slides (described in prose); add as a code slide if desired |
| `12_smart_er_expand_query.cypher` | Section 12 closing | Not in slides; could be a "technical follow-up" appendix slide |

---

## Priority order for a first rehearsal

1. **Hume 3.0 screenshot** (§5 above) — the reveal needs a real image
2. **Phase 1 exploded subgraph** (§2) — walked on stage, needs a real diagram
3. **EntityGroup subgraph** (§3) — engineers will photograph this slide
4. **Paco's Section 06 review** (§6) — confirm the engine-mechanics slides are accurate
5. **"We are here" highlighted variants** (§1) — important for pacing, can be done post-rehearsal
