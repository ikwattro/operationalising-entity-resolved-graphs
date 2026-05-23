# Architecture — The Senzing Contract

## Narrative

The previous section described the shape of the loop. This section is about the contract along its right-hand side: what we send into Senzing, what we get back, and what properties we rely on. The discipline here is what makes the rest of the workshop possible — observability (Section 06), overrides (Section 07), and consumer surfaces (Section 08) all depend on this contract holding.

### Pushing records to Senzing

The transport between the overlay and Senzing is intentionally left undecided here — in production we have used Kafka topics, polling sweepers, and direct synchronous calls, and the choice is shaped by the customer's existing infrastructure rather than by Senzing. What matters for the rest of the workshop is the contract: a record leaves the overlay, lands in Senzing, and triggers an affected-entities event that flows back. The shape of that contract is what we describe below.

Senzing wants records as JSON, with a `DATA_SOURCE`, a `RECORD_ID` stable within that source, and feature blocks for names, addresses, dates of birth, phone numbers, identifiers, and so on. The shape is intentionally flat and feature-oriented — we are not pushing graph structure; we are pushing the evidence that lets Senzing decide whether records resolve.

See `assets/snippets/04_senzing_input_record.json` for a minimal but realistic example.

A few things worth being explicit about:

- **`DATA_SOURCE` is not metadata for show.** Senzing uses it for source-level behaviour (security, weighting, conflict resolution). Pick stable, meaningful codes and never rename them in production.
- **`RECORD_ID` is the addressability handle.** Subsequent updates, deletes, and force-merge instructions reference `(DATA_SOURCE, RECORD_ID)`. If the source system's primary key is unstable, we generate a stable surrogate upstream and keep the original as a feature.
- **We send what we know, no more.** Empty feature blocks are not "unknown" — they are explicit absence. Do not invent placeholders to fill the schema; Senzing handles missing features cleanly and inventions create false matches.

### Senzing magic — treated as a black box

Inside Senzing, records get tokenised into features, features get scored, scoring drives resolution. We do not reverse-engineer the internals here, deliberately. Two reasons: it is not our system to explain on stage, and treating it as a black box keeps our integration honest. If our architecture only works because we know Senzing's internal heuristics, we have built something brittle.

What we rely on from Senzing, as contractual surface:

- **Deterministic resolution for a given engine version, configuration, and set of inputs.** The determinism holds within a version; upgrades and configuration changes can legitimately change resolutions. Treat it as deterministic across replays, not across upgrades.
- **Idempotence** — replaying the same `(DATA_SOURCE, RECORD_ID)` payloads in any order lands on the same entity graph. Put plainly: if a record carries the same payload, sending it twice (or out of order) yields the same resolution as sending it once. This is what makes recovery, re-ingestion, and rebuilds safe operations rather than risky ones.
- **Affected-entities notification** — when a record changes a resolution, Senzing tells us which entities are affected.

### Affected entities — the output we actually consume

Senzing's most useful output is not "here is your resolved entity graph" — it is **"these specific entities were affected by the record you just pushed"**. That delta is what we propagate into the graph, and it is what makes the system real-time. We do not re-read the whole entity store after every record; we apply the affected-entities delta.

See `assets/snippets/04_senzing_affected_entities.json` for the shape. The key fields (names below are illustrative — we will align with current Senzing terminology before the workshop, see open questions):

- `ENTITY_ID` — Senzing's internal identifier for the resolved entity. In the graph (Section 05a) this lands on an `EntityGroup` node as the `entity_id` property. **Forward reference:** we use `EntityGroup` as the graph-side label for what Senzing calls an *Entity*; the full model is in Section 05a. For now, think of `EntityGroup` as the join point that the resolved records hang off.
- `MATCH_LEVEL_CODE` — illustrative values like `RESOLVED`, `POSSIBLE_MATCH`, `POSSIBLY_RELATED`. Each gets a different code path in our graph (e.g. `RESOLVED_TO` versus `RELATED_TO` edges).
- `WHY` — the features and scores that drove the decision. We attach this to the `RESOLVED_TO` edge from the record to the `EntityGroup`, so explainability stays per-record and queryable.

> [verify with Paco] Exact field names and the full enum of `MATCH_LEVEL_CODE` values, plus how identity transitions (split, merge into) are signalled in the response. The snippet uses names we have seen in practice but the canonical shape needs Paco's review before the workshop.

### Idempotence — the property the whole loop depends on

Idempotence is what lets us replay events freely. We crash mid-batch, we replay. We re-ingest a source, we replay. We rebuild a downstream index, we replay. As long as Senzing is idempotent, none of these operations corrupt the graph.

We rely on this aggressively. It is also the property most teams quietly break by sending non-idempotent records (timestamps embedded in features, sequence numbers in identifiers, anything that varies between replays of the "same" record). Discipline upstream: a record's payload is a pure function of its source-of-truth state, with no clock-dependent fields.

## Speaker notes

- When showing the input JSON, do not get into the schema reference. The point is the shape, not the spec.
- Stress idempotence. It is the boring property that makes everything else work, and most teams underweight it until they hit their first replay incident.
- "Affected entities, not full entity store" is the line that explains *how* the system can be near real-time. Land it deliberately.

## Assets

- `assets/snippets/04_senzing_input_record.json` — minimal realistic Senzing input record for a person.
- `assets/snippets/04_senzing_affected_entities.json` — minimal realistic affected-entities response.

## Open questions

- > [verify with Paco] Exact current field names for the input payload — `RECORD_TYPE`, `NAMES`/`NAME_FULL`, `ADDRESSES`/`ADDR_FULL`, `IDENTIFIERS`. We want the snippet to be copy-pasteable.
- > [verify with Paco] The complete set of `MATCH_LEVEL_CODE` values we should be ready to handle, and whether `WHY` is included by default or requires a flag.
