# Workshop TODOs (take2)

Open questions, external dependencies, and missing assets — moved out of the section files so there is one inbox to triage. If a TODO causes a content edit, update the relevant `take2/sections/NN-*.md` and remove (or check off) the item here.

Owner tags:

- **Paco** — Senzing-internals confirmation.
- **Christophe** — content decisions, examples to source, or Hume-side detail.
- **Joint** — workshop logistics or decisions Christophe and Paco share.

Note: the section files still carry **inline narrative hedges** of the form `> [verify with Paco]` where a specific claim needs qualifying for the reader. Those stay in place; they are the speaking voice, not the planning inbox. The items below are the actionable list.

---

## Section 00 — Running Order

- [ ] **Joint:** Pause placement — minute 69 (current, after Senzing core) vs end of Section 04 (after the map). Currently leaning later; revisit after dry-run.
- [ ] **Paco:** Whether you bring your own slides for Section 06 as well as words — we should not rebuild Senzing-internals slides if you already have a set you use.
- [ ] **Christophe:** Whether to credit specific engagements (anonymised) in Phase 5 examples.
- [ ] **Christophe + Paco:** Whether to swap Paco onto Section 04 (the map) as well, since it crosses both companies' surfaces.

## Section 01 — Intro

- [ ] **Christophe:** Whether to open with a real (redactable) disconnected-data-missed-risk story instead of the constructed Al-Rashid opener. Real lands harder.
- [ ] **Joint:** Whether to name-check specific regimes (FinCEN, FCA, EU AMLA) or stay jurisdiction-neutral. Read the room composition.

## Section 02 — Operationalising

- [ ] **Christophe:** Whether to add a fifth property — *secure by source* (RBAC) — or fold into *explainable*. Currently folded; Phase 4 revisits if the audience pushes.
- [ ] **Christophe:** Whether to reframe *idempotent* as *replayable* for non-engineering audiences. Currently keeping the engineering term and defining it on first use (Section 06).

## Section 03 — Best ER You Don't Need

- [ ] **Paco:** Does Senzing prefer pre-normalised input, or does it have its own normalisation we should *not* duplicate? We want to recommend "send raw + normalised" but only if Senzing uses what we send sensibly.
- [ ] **Joint:** Whether to live-demo a normalisation pass with a Python snippet (3-4 min, lands harder) or rely on before/after CSV (safer).
- [ ] **Joint:** Whether to name libraries on stage (`cleanco`, `nameparser`, `libpostal`). Helps engineers in the room; less vendor-neutral.

## Section 04 — Operational Architecture

- [ ] **Joint:** Whether to render six "we are here" diagram variants up front, or one master with highlight overlays. Slide-repo decision.
- [ ] **Joint:** Whether `AUDIT` is a separate box on the master diagram or folded into `GOUT`. Currently separate so Phase 4 has a region to highlight.
- [ ] **Christophe:** Whether to label `HEUR` as "graph decision layer" or "trust-ID generator". Currently "decision layer" — frames the role, not the mechanism.

## Section 05 — Phase 1: Data In

- [ ] **Christophe:** Whether to call the explosion pattern "feature graph" (engineering-precise) or "exploded record" (everyday). Currently using "exploded".
- [ ] **Christophe:** Whether to share `:Name` nodes across records or keep names as record properties only. Currently *not* sharing name nodes — sharing creates spurious co-occurrence (every "John Smith" linking together). Worth being explicit about on stage.
- [ ] **Christophe:** Whether to introduce `:OverrideDecision` / `:Hint` nodes here so Phase 5 has somewhere to land. Currently saved for Phase 5.

## Section 06 — Phase 2: Senzing Fundamentals (Paco)

- [ ] **Paco:** Whether you want to bring your own slides for the engine deep dive, or have us render from the section's spine. Either way, this is your deep dive — we want internals on stage, not a survey.
- [ ] **Paco:** Confirm the canonical names for the engine's stages on stage — *feature extraction*, *candidate retrieval*, *feature scoring*, *resolution* — and align with current Senzing terminology.
- [ ] **Paco:** Confirm concept names — *entity*, *resolution*, *match level*, *affected entities* — match current Senzing docs.
- [ ] **Paco:** Shape of the configuration-model walk-through — by entity type, by feature, or by example. We are going deep; you pick the shape that lands best in 14 minutes.
- [ ] **Paco:** Whether to include the determinism-across-upgrade-boundary caveat here or in Section 07. Currently here, because the audience asks immediately.

## Section 07 — Phase 2: Graph → Senzing Pipeline

- [ ] **Paco:** Exact current field names for the input payload — `NAMES`/`NAME_FULL`, `ADDRESSES`/`ADDR_FULL`, `IDENTIFIERS`, and identifier sub-keys (`PASSPORT_NUMBER`, `NATIONAL_ID_NUMBER`, etc.). We want the snippet copy-pasteable.
- [ ] **Paco:** Whether `MATCH_LEVEL_CODE` values are stable across versions. We encode them in graph edge properties; renames would matter.
- [ ] **Paco:** Whether the affected-entities response includes identity transitions (split, merge into) explicitly, or whether we infer them by diffing entity membership.
- [ ] **Joint:** Whether to recommend CDC over triggers as the workshop default. Currently neutral; engineers in the room may have a preference we want to read live.
- [ ] **Joint:** Whether to introduce the `MATCH_LEVEL_CODE` enum exhaustively or by sample. Currently by sample.

## Section 08 — OOTB Senzing

- [ ] **Paco:** Authoritative list of OOTB capabilities in the current Senzing version — names, addresses, identifiers, dates — including granularity (e.g. does name handling cover Russian patronymics by default, or only with explicit configuration?).
- [ ] **Paco:** How Senzing actually decides geocoding when no country anchor is in the record. The workshop currently says "garbage in, geocoded-elsewhere out"; we want the engine's actual behaviour.
- [ ] **Christophe:** Whether to demo a side-by-side — same record with/without country anchor, showing the resolution difference. Higher impact, eats time.
- [ ] **Christophe:** Whether to mention that pre-flattening upstream is a *common* mistake even among teams using Senzing — gentle warning vs implicit point.

## Section 09 — Phase 3: Living Architecture

- [ ] **Paco:** Exact API surface for record deletes — soft delete on the record vs. signalling absence of evidence. Clear story needed for stage.
- [ ] **Paco:** How identity transitions (merge into, split into) are explicitly signalled in the affected-entities response. We infer some today; canonical signalling preferred.
- [ ] **Christophe:** Whether to demo a live growth → merge → split timeline against a sample dataset, or describe one. Demo = higher impact, higher risk.

## Section 10 — Phase 4: Explainability & Observability

- [ ] **Paco:** Which features in current Senzing versions are the highest redo triggers in production, and whether the engine exposes a "redo budget" / rate-limit knob.
- [ ] **Paco:** Whether Senzing exposes a "why did this record cause N affected entities" diagnostic we can surface directly in the graph.
- [ ] **Christophe:** Whether to commit to building the explicit audit-history layer as a Hume roadmap item, or leave it as a community question. Revisit if the room responds strongly.
- [ ] **Christophe:** Whether to demo a real redo storm in the live segment, or describe one from a past project.

## Section 11 — Phase 5: Graph Decision Layer + Trust IDs

- [ ] **Paco:** How exactly to configure Senzing so a `TRUST_ID` feature on a record drives merge/split behaviour. We want canonical configuration on stage.
- [ ] **Paco:** Whether Senzing has a built-in "trust ID" concept, or whether we are using a generic strong-identifier feature for the purpose. The mechanism works either way; the language on stage depends on which.
- [ ] **Christophe:** Thresholds for the automatic categories (face-embedding similarity, co-occurrence weight). Currently "calibrate per deployment". A starting point would be more actionable.
- [ ] **Paco:** Whether the trust-ID log (pattern of overrides correcting the same engine behaviour repeatedly) is a meaningful signal for Senzing config tuning in practice — and if so, how. Removed a "feedback drift" risk bullet from the section because we were not confident enough to state it. Either Paco confirms and we restore it, or it stays out.
- [ ] **Christophe:** Which engagements / examples are redactable enough to show on stage. The `OWNS` and `FATHER_OF` examples should ideally be real.
- [ ] **Christophe:** Whether to introduce an `:OverrideDecision` node in the graph model now, or treat it as part of the audit-history hypothetical from Section 10.

## Section 12 — Phase 6: Consumption & Hume 3.0

- [ ] **Christophe:** Which exact Hume 3.0 features beyond *Smart ER in Advanced Expand* are in scope for the reveal. Currently planned: lead with Smart ER, mention the next two improvements lightly.
- [ ] **Christophe:** Whether the 90-second demo runs live or as a recorded clip. Live = higher impact, recorded = safer.
- [ ] **Christophe:** Whether to credit a specific engagement (anonymised) where Smart ER was first used in production. Adds authenticity but risks identification.
- [ ] **Christophe:** Whether to mention non-Hume consumer tooling (Linkurious, Neo4j Bloom, custom UIs). Useful if non-Hume users in the room.

---

## Missing assets

Tracked separately because these are sourcing tasks, not decisions.

- [ ] **Christophe — Section 12:** Hume 3.0 Advanced Expand screenshot showing entity-aware navigation. Target path: `take2/assets/screenshots/12_hume3_smart_er.png`.
- [ ] **Christophe — Section 12:** Cypher behind a Smart ER expand, for the technical follow-up after the close. Target path: `take2/assets/snippets/12_smart_er_expand_query.cypher`.
- [ ] **Joint — Sections 05 / 07 / 10:** Mermaid diagrams referenced in section text but not yet split out as `.mmd` files: `05_phase1_exploded.mmd`, `07_eg_record_subgraph.mmd`, `10_audit_history_hypothetical.mmd`. Inline Mermaid in the section files is sufficient for now; pull them out only if the slide repo asks.
- [ ] **Joint — Section 07:** `07_graph_to_senzing_mapping.cypher` — the Cypher mapping snippet inlined in the section text. Pull out as a standalone file if the slide repo prefers external snippets.
- [ ] **Joint — Section 10:** `10_redo_rate_dashboard.cypher` — example Cypher for the redo-rate dashboard. Inlined description in section; standalone file optional.
