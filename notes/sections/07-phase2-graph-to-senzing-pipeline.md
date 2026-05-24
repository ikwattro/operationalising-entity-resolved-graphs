# Phase 2 — From Graph Records to Senzing

> **We are here:** `GIN → SZ → GOUT`. Records leave the graph for Senzing; resolved entities come back.

## Narrative

Paco just described the engine and a single round-trip through it. This section is how those round-trips actually happen *from a graph*, continuously, in production. Three things have to be right: the trigger that pushes a record, the mapping from graph shape to Senzing JSON, and the handling of the affected-entities event that comes back.

### Pushing records — CDC versus triggers

Records do not push themselves. Something in the graph input layer (Phase 1) has to notice that a record is ready and emit it to Senzing. Two patterns work in production:

- **Change Data Capture (CDC).** The graph (or its transaction log) emits a stream of change events; a downstream consumer filters for "new or updated `:Record` nodes that have passed alignment" and pushes them to Senzing. This is the right pattern when the customer already has a streaming spine (Kafka, Pulsar, Kinesis) and is comfortable wiring a consumer.
- **Trigger-based.** A Cypher trigger (or equivalent) fires on `:Record` creation and pushes synchronously, or enqueues the push for an async worker. This is the right pattern when the customer's data scale fits, when CDC is not already in the stack, and when we want the push tied tightly to the graph's write path.

Both work. Both are idempotent on Senzing's side because Senzing is idempotent (Section 06). The choice is dictated by the customer's existing stack, not by Senzing.

What both patterns share is the *contract*: a `:Record` in the graph, in a particular state (aligned, dedup-hash computed, ready), produces exactly one push to Senzing per logical change.

### The mapping — graph to Senzing JSON

The graph's exploded representation (Phase 1) has to be flattened back into the feature-oriented JSON shape Senzing expects. The mapping is mechanical but worth being explicit about.

A simplified Cypher to construct the payload — the slide repo will render this as a code block:

```cypher
MATCH (r:Record {record_id: $record_id})-[:FROM]->(src:Source)
OPTIONAL MATCH (r)-[:HAS_NAME]->(n:Name)
OPTIONAL MATCH (r)-[:HAS_DOB]->(d:DOB)
OPTIONAL MATCH (r)-[:HAS_PASSPORT]->(p:Passport)
OPTIONAL MATCH (r)-[:HAS_ADDRESS]->(a:Address)
OPTIONAL MATCH (r)-[:HAS_PHONE]->(ph:Phone)
RETURN {
  DATA_SOURCE:  src.code,
  RECORD_ID:    r.record_id,
  NAME_FULL:    n.value,
  DATE_OF_BIRTH: d.value,
  PASSPORT_NUMBER: p.value,
  PASSPORT_COUNTRY: p.country,
  ADDR_FULL:    a.value,
  PHONE_NUMBER: ph.value
} AS payload
```

The full example in `assets/snippets/07_graph_to_senzing_mapping.cypher` and the resulting JSON in `assets/snippets/07_senzing_input_record.json`. The two key principles:

- **Send what we know, no more.** Empty feature blocks mean *unknown*. Do not invent placeholder strings to fill the schema; Senzing handles missing features cleanly, and inventions create false matches.
- **`DATA_SOURCE` and `RECORD_ID` are not metadata.** Senzing uses them for security, weighting, and addressability. Stable, meaningful values, and never renamed in production.

> [verify with Paco] Exact current field names — `NAMES`/`NAME_FULL`, `ADDRESSES`/`ADDR_FULL`, `IDENTIFIERS` — and whether the listed identifier types (`PASSPORT_NUMBER`, `NATIONAL_ID_NUMBER`, etc.) are the canonical keys.

### What comes back — affected entities

Senzing's most useful output is not "here is the entire resolved entity graph". It is **"these specific entities were affected by the record you just pushed"**. That delta is what we apply to the graph. We never re-read the entity store after every record.

The shape of the response — example in `assets/snippets/07_senzing_affected_entities.json`:

```json
{
  "DATA_SOURCE": "KYC",
  "RECORD_ID": "KYC-902",
  "AFFECTED_ENTITIES": [
    {
      "ENTITY_ID": 1001,
      "MATCH_LEVEL_CODE": "RESOLVED",
      "WHY": { "FEATURES": [
        {"NAME": "PASSPORT", "SCORE": 100, "DECISION": "MATCH"},
        {"NAME": "NAME", "SCORE": 92, "DECISION": "CLOSE"}
      ]},
      "PRIOR_ENTITY_IDS": [1001, 1002]
    },
    {
      "ENTITY_ID": 1002,
      "MATCH_LEVEL_CODE": "RETIRED",
      "MERGED_INTO": 1001
    }
  ]
}
```

The field names above are illustrative; the canonical shape is on Paco's side.

What we do with this on the graph side:

- For each affected entity, find or create the corresponding `:EntityGroup` node, keyed by `ENTITY_ID`.
- Attach the record to the `EntityGroup` via `-[:RESOLVED_TO]->`, with the `MATCH_LEVEL_CODE` and `WHY` carried as edge properties. Explainability stays per-record and queryable.
- For retired entities — `EntityGroup`s that have been absorbed into another — mark them with a `merged_into` pointer and keep them in history. We do not delete them.
- Stamp every change with the triggering record and a timestamp. This is the basis of Phase 4's observability story.

### The graph representation — EntityGroup and the records that hang off it

```
(:Source)
  <-[:FROM]- (:Record)-[:RESOLVED_TO {match_level, why, decided_at}]-> (:EntityGroup {entity_id, last_affected_at})
```

The `EntityGroup` carries the Senzing `entity_id`, the last-affected timestamp, and the resolution metadata. It **does not** carry consolidated record properties — no fused name, no merged address list, no unified phone-number set. The properties stay on the records. The reason is RBAC, and we lean into it hard in this section.

A user's access is scoped by source. If we fused record properties into the `EntityGroup`, a KYC-only analyst would end up seeing attributes derived from wires records they are not entitled to see, and there is no clean way to redact that. **We never fuse records into the `EntityGroup`.** Aggregation happens at query time, RBAC-filtered to the records the user can see. This is the single rule that makes the whole architecture compatible with how the customers in this room actually run access control.

The existence of the `EntityGroup` itself remains visible across sources — an analyst should know there is a resolution group, even if they cannot see all of its contents. What they cannot see is the content from sources outside their scope.

### Putting it together

By the end of this section, the audience has seen:

- One record leaving the graph and turning into a Senzing input JSON (the mapping).
- One affected-entities event coming back and turning into a graph change (the `RESOLVED_TO` edge).
- The `EntityGroup` model that holds resolutions without fusing records.
- The reason the model is shaped that way (RBAC by source).

That is the complete Phase 2 round-trip. Phase 3 is what happens when the second record arrives, and the third, and the thousandth.

## Speaker notes

- CDC versus triggers is the audience's call, not ours. Present them as alternatives, not a recommendation. The engineers in the room will know which one fits their stack.
- The mapping Cypher slide is the one engineers will photograph. Keep it readable on screen, not tiny.
- Spend time on the no-fusion rule. It will surprise some of the room and it is the thing the compliance officers will quote back.
- The "EntityGroup is ours, not Senzing's" naming reminder lands here for the second time in the workshop. Be explicit again.

## Assets

- `assets/snippets/07_graph_to_senzing_mapping.cypher` — Cypher for mapping a `:Record` and its attribute neighbours to a Senzing input JSON.
- `assets/snippets/07_senzing_input_record.json` — example Senzing input.
- `assets/snippets/07_senzing_affected_entities.json` — example affected-entities response.
- `assets/diagrams/07_eg_record_subgraph.mmd` — the `Source ← Record → EntityGroup` subgraph showing how affected entities are stored.

## Open questions

Moved to [`../TODOS.md`](../TODOS.md).
