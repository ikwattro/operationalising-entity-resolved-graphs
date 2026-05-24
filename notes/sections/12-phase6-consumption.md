# Phase 6 — Consumption and Hume 3.0 Smart ER

> **We are here:** `GOUT → CONS`. Everything we have built is now in the hands of the people we built it for.

## Narrative

Resolution is a means, not an end. Nobody opens a regulator's letter and replies "we have a beautifully resolved entity store" — they reply with names, networks, timelines, and the chain of evidence behind them. The work in the previous five phases only pays off if the resolved graph is *usable* by the people who need to act on it.

This phase is shorter than the others on purpose. The consumer surfaces are downstream of the principles; if the principles are right, the consumer surfaces fall out. There is one new thing worth showing in detail — the Hume 3.0 Smart ER capability — and a short look at what comes after.

### Who actually consumes the resolved graph

Four patterns, all of which a well-designed ER graph supports:

- **Investigation workflows.** An analyst starts from a name, a phone, or an alert, and walks the neighbourhood. They need to see the resolved entity, every record that contributed (RBAC-filtered), every relationship at one and two hops, and the `WHY` behind each resolution. Speed matters: investigations are interrupt-driven.
- **Search and lookup.** Risk officers and call-centre staff type a name and want the unified entity, not a list of duplicate records. Search has to be **entity-aware**, not just full-text.
- **Alerting and monitoring.** Watchlist hits, sanctions matches, anomaly detection — fire on the *entity*, not the record. When a new record resolves into a watchlisted entity, the alert fires once, with the record as evidence.
- **Programmatic exploration.** Data scientists project the graph for feature engineering and model training. They need an API that exposes the graph as a graph, RBAC-respecting, not flattened tables.

Each pattern has different latency, freshness, and access requirements. The graph store has to serve all of them from one consistent state — which is why idempotence (Phase 3) and observable updates (Phase 4) are not optional. They are what makes consistent consumption possible.

### Hume 3.0 — Smart ER in Advanced Expand

The new capability we are revealing on stage. In its own words:

> *When data from multiple systems is combined, the same real-world entity often appears more than once. A person, organisation, or location may exist in several datasets, each represented by a separate node in the graph. Rather than merging those records into a single node and losing important context, GraphAware Hume uses entity groups to connect records that likely represent the same real-world entity while preserving their source data. This allows analysts to understand relationships across sources while still maintaining provenance, data separation, and access control.*

That is the architecture from Phases 1-5, in customer-facing language. The model we have been describing — records stay separate, `EntityGroup` is the join, RBAC scopes by source — is the model Hume implements.

What is new in 3.0 is the **analyst experience**:

> *In previous versions of GraphAware Hume, analysts needed to be aware of these entity groups when building queries or performing advanced expands, adding an extra layer of complexity to investigative workflows. In GraphAware Hume 3.0, that complexity has been removed. Analysts can query and explore their data as if they were working with a single entity, without needing to manage the underlying entity resolution logic.*

Translated to what the analyst actually does on screen: an advanced expand from a `Person` node automatically traverses the `RESOLVED_TO` edge to the `EntityGroup`, then back out across every other record the analyst is allowed to see. They click once; the expand shows them the full entity-aware neighbourhood, with provenance, source attribution, and the `WHY` available for every edge.

The principle: **the analyst reasons about entities; the architecture handles records and groups underneath.** The complexity is in the system, not in the user's head.

We will demo this. The demo is 90 seconds — *not* a tour of Hume's full investigation surface. Just the advanced expand from a record into the entity-aware neighbourhood, with one before/after comparison if time permits.

### What we deliberately do not do

Some consumer-side patterns look attractive and cause more pain than they solve. Worth naming:

- **Materialising the resolved graph into a relational warehouse for downstream consumption.** Tempting because the BI team already has SQL. The warehouse becomes stale within minutes of every Senzing affected-entities event, and the BI team quietly builds their own (incorrect, inconsistent) joins on top of the records. If consumers need entity-level joins, expose them through the graph or a graph-aware API.
- **Letting consumer teams write directly against the resolved entity store.** Every team that does becomes a small client of Senzing without knowing it; every tuning change becomes a coordination problem. Mediate through an API layer with a stable contract.
- **Hiding the resolution mechanics behind a "smart match" layer with no evidence trail.** Whenever resolution feels magic to the consumer, an analyst eventually asks why and the team has nothing to show. Keep the mechanics visible — the `WHY` is the difference between explainable and opaque.

The general posture: **the graph is the source of truth, and consumer surfaces are thin layers on top of it.** Anything that copies the graph into a parallel store is a maintenance bet we lose.

### What comes after — future improvements for ER graphs

Quick look-ahead, not a roadmap commitment:

- **Smart ER search.** Search that returns entity-aware results across resolved sources, with the `WHY` surfaced at result time. The advanced-expand improvement in 3.0 is the first step; entity-aware ranking is the next.
- **Better grouping visuals.** Communities, ownership chains, transaction rings — these are graph-native shapes that current visualisations flatten. We want first-class rendering for them.
- **The explicit audit-history layer from Phase 4.** If the room signals strongly, this becomes a roadmap item.

We close on the principle, not the roadmap: **everything in Phase 6 is downstream of getting Phases 1-5 right.** If we have the loop, observability, and a graph decision layer driven by trust IDs, the consumer story is engineering, not philosophy.

## Speaker notes

- This is the closing-down section. Pace lower than Phase 5.
- The Hume 3.0 reveal is the closer-to-closer. Land the capability in customer-facing language *and* tie it back to the architecture from Phase 4.
- The 90-second demo is the only live demo in the whole workshop. Rehearse it cold. If it fails on stage, the static screenshot in `assets/screenshots/12_hume3_smart_er.png` is the fallback — show it without apologising.
- "What we do not do" lands harder than expected. Several teams in the audience will have built one of those patterns already; be gentle but clear.
- End on the principle. Not on the product. The point is the architecture; Hume is one expression of it.

## Assets

- `assets/screenshots/12_hume3_smart_er.png` — Hume 3.0 Advanced Expand screenshot showing entity-aware navigation. To be sourced; see [`../TODOS.md`](../TODOS.md).
- `assets/snippets/12_smart_er_expand_query.cypher` — Cypher behind a Smart ER expand, for technical follow-up after the close. To be added; see [`../TODOS.md`](../TODOS.md).

## Open questions

Moved to [`../TODOS.md`](../TODOS.md).
