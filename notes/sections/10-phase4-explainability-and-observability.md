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

### Redos and redo storms — Paco [live]

> **[Paco owns this block — leave blank for the session.]**
>
> Cover:
> - What a redo is: the internal Senzing mechanism that re-evaluates affected records when new evidence arrives.
> - When redos trigger: which events cause a cascade and why.
> - A worked example on screen — ideally with the min_aml dataset or a small synthetic set showing a redo cascade step by step.
> - How the engine handles the cascade internally — scoping, ordering, termination.
> - Redo storms: when a single record triggers a large cascade, what that looks like operationally, and how Senzing surfaces it.

### Observability — the dashboards live in the graph

Operationalising the change behaviour from Phase 3 means watching it. The metrics worth tracking, in production:

- **Redo rate per ingestion batch.** Spikes correlate with high-specificity feature ingestion (passport-rich sources coming online). Tracking the rate lets us anticipate load.
- **Affected-entity count distribution.** Most records affect 1–2 entities. The long tail — records that affected 50+ entities — are the redo storms Paco covered above. We do not want to suppress them; we want to *see* them.
- **Entity stability over time.** For each `EntityGroup`, how often does its set of resolved records change? Highly unstable `EntityGroup`s are either contested (interesting) or noisy (a config problem).
- **Feature-level resolution behaviour.** Which features are driving merges? Which are driving splits? If one feature dominates, our configuration is probably overweighting it.
- **Source-level behaviour.** Which sources contribute more redo than they should? Often the answer is a source with poor data quality — Section 03 problems surfacing at runtime.

**All of these are graph queries.** We do not need a separate observability stack. Timestamps on every edge change, a small event log of resolutions per `EntityGroup`, and dashboards built on Cypher. Putting observability in the same store as the data means analysts and operators see the same world. The Cypher behind one of the dashboards lives in `assets/snippets/10_redo_rate_dashboard.cypher`.


## Speaker notes

- Paco leads the redo/redo-storm block. Christophe hands over at the start of that subsection and picks back up at Observability.
- The "dashboards are graph queries" line is the engineering one. Stress it. Most teams build separate metrics stacks and regret it.
- Phase 4 ends on observability — leave the room with the concrete picture of metrics-as-graph-queries before moving to Phase 5.

## Assets

- `assets/snippets/10_redo_rate_dashboard.cypher` — example Cypher for redo-rate and affected-entity-count dashboards.

## Open questions

Moved to [`../TODOS.md`](../TODOS.md).
