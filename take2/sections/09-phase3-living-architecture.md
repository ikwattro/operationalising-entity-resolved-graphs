# Phase 3 — A Living Architecture

> **We are here:** `GOUT` over time. The same nodes, the same engine, different conclusions as evidence arrives.

## Narrative

In a demo, ER decides once. In production, it decides continuously, and its decisions change as evidence arrives. A record that landed last week may belong to a different entity today, because a record from a different source corroborated or contradicted it. This is not a bug — it is the correct behaviour of an evidence-driven system — but it has to be visible, controllable, and survivable.

This phase is the engine of change. Section 10 is how we see it; Section 11 is how we shape it.

### Idempotence — the property the whole loop depends on

Paco set this up in Section 06; we lean on it here. **Idempotence** means: if a record carries the same payload, sending it twice (or out of order) yields the same resolution as sending it once. Same engine version, same configuration, same records — same outcome, regardless of order or repetition.

Operationally this is what makes recovery, re-ingestion, and rebuilds safe. We crash mid-batch, we replay. We re-ingest a source, we replay. We rebuild a downstream index, we replay. None of these operations corrupt the graph, *as long as upstream stays clock-independent*. A record's payload has to be a pure function of source-of-truth state — no timestamps in features, no monotonic sequence numbers in identifiers, no last-modified fields creeping into the matching key. Discipline upstream is what keeps the engine's idempotence intact.

One thing worth being precise about: *replay* means re-sending the same `(DATA_SOURCE, RECORD_ID)` payloads. If the source-of-truth state has changed since the original ingest, what we are doing is a new ingest, not a replay — and the outcome will (correctly) differ. Treating "replay" and "re-ingest after upstream change" as the same operation is the most common confusion in recovery procedures.

### Updates and deletes — records change in the source

Source systems do not freeze. A KYC record gets updated with a corrected passport. A registry record gets deleted because the company was wound up. The graph has to reflect that without breaking history.

Two rules:

- **Update = new versioned record, not mutation.** When the source says "this record changed", we land a new immutable record version, link it to the prior version, and push the new one to Senzing. The graph keeps both — the old version is still queryable for history. Senzing receives the updated `(DATA_SOURCE, RECORD_ID)` payload and re-resolves.
- **Delete = soft delete, marked, never erased.** Hard deletion is a one-way door we never take. We mark the record as deleted, with the deletion event and timestamp, and we tell Senzing the record is no longer evidence. Senzing re-resolves accordingly; the graph keeps the record so we can answer "what did the system think a year ago".

> [verify with Paco] The exact Senzing API surface for marking a record deleted and the resulting affected-entities behaviour. The mechanism above describes what we have always wanted to do; we want to align with the canonical shape.

### Three behaviours: growth, merge, split

As records arrive, three things happen at the `EntityGroup` level:

- **Growth.** A new record falls into an existing `EntityGroup`, adding features without changing the entity's identity. The `EntityGroup` keeps its `entity_id`; a new `RESOLVED_TO` edge appears. Most events are growth events.
- **Merge.** A new record carries enough evidence to link two previously separate `EntityGroup`s — typically a strong identifier like a passport. The two collapse into one; the surviving `EntityGroup` inherits the records of both, the absorbed `EntityGroup` is marked `merged_into` the survivor. Existing `RESOLVED_TO` edges rebind to the survivor; the absorbed `EntityGroup` stays in the graph as history.
- **Split.** A new record contradicts a prior grouping — typically a corrected identifier or a registry update that proves two records refer to different real-world entities. The `EntityGroup` fractures; previously-resolved records get reassigned across the resulting `EntityGroup`s. The original `EntityGroup` may remain (with its remaining records) or itself be retired, depending on what the engine decides.

`assets/data/09_update_timeline.csv` shows a worked example: a single `EntityGroup` cluster goes through growth, then a merge triggered by a passport match, then a split when a registry correction contradicts the merge. Same physical pipeline, same Senzing instance, same records — different conclusions at different times. **This is what near real-time actually looks like in production.**

### What we expect to happen, that we plan around

A few patterns from the field, worth setting expectations on:

- **High-specificity identifiers trigger the largest changes.** A new passport number on a record can collapse two `EntityGroup`s or split one — far more than a new address or phone. The redo cascade (Section 10) is dominated by identifier ingestion.
- **Sources behave differently.** A registry feed delivering corrections produces splits; a KYC pipeline delivering new evidence produces growth. The mix shifts depending on the day's ingestion.
- **Stability is a function of evidence, not time.** An `EntityGroup` is "stable under current evidence", not "stable". Saying it is stable without qualification will mislead the room — be precise.

The graph carries the full history of these transitions. Section 10 is how we surface that history to the people who need it.

## Speaker notes

- This is the section regulators in the room lean in on. Be careful about what is automatic, what is observable, and what an analyst can override (Phase 5).
- Walk the timeline CSV row by row on screen. The merge at step 4 and the split at step 6 are the moments to dwell on.
- Avoid the word "stable" without qualification. The phrase is "stable under current evidence".
- Keep this section to 10 minutes — the redo-storm and observability material lives in Phase 4.

## Assets

- `assets/data/09_update_timeline.csv` — 7-step worked example of growth → merge → split for a single `EntityGroup` cluster. Carries the same content as take1's `06_update_timeline.csv`.

## Open questions

Moved to [`../TODOS.md`](../TODOS.md).
