# Phase 4 — Explainability, Observability, and an Audit-History Idea

> **We are here:** `GOUT → AUDIT`. Everything the engine and the graph do has to be inspectable, queryable, and survivable under audit.

## Narrative

Phase 3 made the system move. Phase 4 makes the movement *visible*. Two of the four properties from Section 02 — *observable* and *explainable* — get earned here. Without them, "near real-time ER" is just a fast way to be confidently wrong.

### Explainability — every merge has a justification queryable from the graph

Every `RESOLVED_TO` edge in the graph carries the **`WHY` payload** from Senzing — the features and scores that drove the resolution decision — as edge properties. No analyst should ever have to ask "why is this record on this entity?". The answer is one Cypher query away:

```cypher
MATCH (r:Record {record_id: $record_id})-[rel:RESOLVED_TO]->(eg:EntityGroup)
RETURN rel.match_level, rel.why, rel.decided_at, eg.entity_id
```

The same pattern applies to overrides (Phase 5). When a trust-ID intervention causes a merge or a split, the `WHY` on the new `RESOLVED_TO` edge records the graph signal as the cause, not just the per-feature scores. An investigator chasing "why did these collapse?" gets the per-feature evidence *and* the graph-evidence trail in the same edge. Explainability is per-record, queryable, and durable.

Two design principles separate a usable ER graph from a frustrating one:

- **Show the entity, not the records.** Every UI surface (Phase 6) defaults to the entity view. Records are how the data arrived; the entity is what the human is reasoning about.
- **Show the `WHY` for every resolution.** No mystery merges, ever. Every edge, every membership, every alert carries its evidence as a click-through.

### Observability — the dashboards live in the graph

Operationalising the change behaviour from Phase 3 means watching it. The metrics worth tracking, in production:

- **Redo rate per ingestion batch.** When Senzing receives a record, it can re-evaluate neighbouring records — and if a strong feature lands, the cascade can touch many. Spikes correlate with high-specificity feature ingestion (passport-rich sources coming online). Tracking the rate lets us anticipate load.
- **Affected-entity count distribution.** Most records affect 1–2 entities. The long tail matters: which records affected 50+ entities, and why? Those are the **redo storms** — single records that trigger thousands of downstream re-evaluations. We do not want to suppress them; we want to *see* them.
- **Entity stability over time.** For each `EntityGroup`, how often does its set of resolved records change? Highly unstable `EntityGroup`s are either contested (interesting) or noisy (a config problem).
- **Feature-level resolution behaviour.** Which features are driving merges? Which are driving splits? If one feature dominates, our configuration is probably overweighting it.
- **Source-level behaviour.** Which sources contribute more redo than they should? Often the answer is a source with poor data quality — Section 03 problems surfacing at runtime.

**All of these are graph queries.** We do not need a separate observability stack. Timestamps on every edge change, a small event log of resolutions per `EntityGroup`, and dashboards built on Cypher. Putting observability in the same store as the data means analysts and operators see the same world. The Cypher behind one of the dashboards lives in `assets/snippets/10_redo_rate_dashboard.cypher`.

### Surviving a redo storm

When a storm happens — and it will — what saves us is not preventing it but containing it:

- **Replayable ingestion** (Phase 3). If the storm started because we ingested a broken batch, we can re-ingest the corrected version because Senzing is idempotent. We do not repair the graph by hand.
- **Lineage on every change.** Every resolution change carries the triggering record as a property. Tracing a storm back to its source is one query, not a forensic investigation.
- **Source-level rate control.** The graph input layer (Phase 1) sits between the source and Senzing; it is the right place to throttle a misbehaving source.
- **Hold and review.** For ingestion patterns that historically cause storms (a passport-rich registry feed showing up), we can buffer the batch, ingest a sample, observe the affected-entity distribution, and only then push the rest.

The general posture: redo is good, redo storms are an operational signal, and the response is observability plus replayability, not algorithmic suppression. We do not want Senzing to *not* redo. We want to know when it does, what it touched, and why.

### A hypothetical idea — an explicit audit-history layer

This is a forward-looking idea we are putting on the slide so the room can poke at it. It is not built; it is the architectural question we want to ask the audience.

Today, the graph carries history as a side-effect: timestamps on edges, versioned records, retired `EntityGroup`s left in place with `merged_into` pointers. The audit story works. But it is *implicit* — reconstructing "what did the system think on 2026-04-01 at 14:00?" is a non-trivial query that walks history edges and resolves the state.

The hypothetical: an **explicit audit-history layer** as a first-class part of the model. Concretely:

- An `OverrideDecision` node for every trust-ID intervention (Phase 5), linked to the reviewer, the evidence, and the resulting `EntityGroup` change.
- A `ChangeEvent` node for every affected-entities event, linking the triggering record, the prior state, and the new state. Queryable by time directly.
- A `Snapshot` mechanism that lets us reconstruct "the graph as it was at time T" for any T, without replay.

The trade-off: more storage, more write amplification, more model surface. The win: audit becomes a primitive, not a project. We do not know yet whether the trade is worth it for every customer. The slide invites the audience to tell us where they land.

> Open question for the room: **how much explicit audit history do you actually need, and what would you sacrifice to get it?** The answer shapes our roadmap.

## Speaker notes

- The "dashboards are graph queries" line is the engineering one. Stress it. Most teams build separate metrics stacks and regret it.
- The hypothetical audit layer is *deliberately* presented as a question. Do not pitch it. Ask the room.
- The redo-storm material is operational; do not let it drift into ER theory. Concrete metrics, concrete responses.
- Phase 4 ends on a question to the room. That sets up the audience pause well (if the pause is at the end of Section 08) or seeds Phase 5 (if pause was earlier).

## Assets

- `assets/snippets/10_redo_rate_dashboard.cypher` — example Cypher for redo-rate and affected-entity-count dashboards.
- `assets/diagrams/10_audit_history_hypothetical.mmd` — sketch of the proposed audit-history layer (OverrideDecision, ChangeEvent, Snapshot).

## Open questions

Moved to [`../TODOS.md`](../TODOS.md).
