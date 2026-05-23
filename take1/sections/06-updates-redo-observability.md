# Living with Updates — Redo Logic and Observability

## Narrative

In a demo, ER decides once. In production, it decides continuously, and its decisions change as new evidence arrives. A record that landed last week may belong to a different entity today, because a record from a different source corroborated or contradicted it. This is not a bug to be smoothed over — it is the correct behaviour of an evidence-driven system — but it has to be visible, controllable, and survivable.

(Throughout this section, "entity" refers to a Senzing-resolved identity. In the graph model from Section 05 these are `EntityGroup` nodes; we use "entity" colloquially below to keep the prose readable.)

### Entities in motion

Three things happen as records arrive:

- **Growth** — a new record falls into an existing entity, adding features (a phone number, an address, an identifier) without changing the entity's identity.
- **Merge** — a new record carries enough evidence to link two previously-separate entities. They collapse into one; the surviving entity inherits the records and features of both, the absorbed entity is retired but its history remains queryable.
- **Split** — a new record contradicts a prior grouping (a passport number that conflicts, a registry update that proves two records are different people). The entity fractures; previously-resolved records are reassigned across the resulting entities.

`assets/data/06_update_timeline.csv` shows a worked example: a single entity grows over hours, absorbs another via a passport match, then splits days later when registry data contradicts the merge. The same physical pipeline, the same Senzing instance, the same records — different conclusions at different times. This is what *near real-time* actually looks like.

### Redo — the engine of change

When Senzing receives a record, it does not just resolve that record in isolation. It re-evaluates the records around it. If the new evidence changes the resolution of a neighbouring record, that change propagates. We call this **redo**, and it is what keeps the graph consistent as evidence accumulates.

Redo is the property we *want*. The risk is that it cascades. A single record with a high-specificity feature (a passport, a national ID, a tax number) can touch many records, each of which gets re-evaluated, each of which can in turn touch more. In the worst case, a single ingestion event triggers thousands of downstream re-evaluations — a **redo storm**.

Some features are more redo-prone than others, as a rule of thumb (we will confirm with Paco for the workshop):

- **High-specificity identifiers** — passports, national IDs, tax IDs, KYC numbers. One match is often enough to drive a resolution; one *new* one is enough to drive a redo.
- **Addresses with strong tokens** — full street + postcode + country. Less than passports, but enough to cluster.
- **Phone numbers** — moderately redo-prone, depending on country and shape.
- **Names alone** — rarely trigger redo cascades. Names tokenise into many candidates and resolution rarely turns on names alone.

> [verify with Paco] The actual ranking of redo-triggering features in current Senzing versions, and whether the engine exposes a "redo budget" or rate-limit knob.

### Observability — making the invisible visible

Operationalising redo means watching it. The metrics we care about:

- **Redo rate per ingestion batch.** Spikes correlate with new high-specificity feature ingestion (e.g. a passport-rich source coming online). Tracking this lets us anticipate load.
- **Affected-entity count distribution.** Most records affect 1–2 entities. The long tail matters: which records affected 50+ entities, and why? Those are the redo storms.
- **Entity stability over time.** For each entity, how often does its set of resolved records change? Highly unstable entities are either contested (interesting) or noisy (a config problem).
- **Feature-level resolution behaviour.** Which features are driving merges? Which are driving splits? If one feature dominates, our configuration is probably overweighting it.
- **Source-level resolution behaviour.** Which sources contribute more redo than they should? Often the answer is a source with poor data quality — Section 02 problems showing up at runtime.

All of these are graph queries. We do not need a separate observability stack — we need to *instrument the graph itself*: timestamps on every edge change, a small event log of resolutions per entity, and dashboards built on Cypher (or whatever the graph speaks). Putting the observability in the same store as the data means analysts and operators see the same world.

### Surviving a redo storm

When a storm happens — and it will — what saves us is not preventing it but containing it:

- **Replayable ingestion.** If the storm started because we ingested a broken batch, we can re-ingest the corrected version because Senzing is idempotent. We do not have to repair the graph by hand. One thing worth being precise about: *replay* means re-sending the same `(DATA_SOURCE, RECORD_ID)` payloads. If the source-of-truth state has changed since the original ingest, what we are doing is a new ingest, not a replay — and the outcome will (correctly) differ. Treating "replay" and "re-ingest after upstream change" as the same operation is the most common confusion in recovery procedures.
- **Lineage on every change.** Every resolution change in the graph has the record that triggered it as a property. Tracing a storm back to its source record is one query, not a forensic investigation.
- **Source-level rate control.** We can slow a misbehaving source without taking the pipeline down. The transparent overlay sits between the source and Senzing; it is the right place to throttle.
- **Hold and review.** For ingestion patterns that historically cause storms (a passport-rich registry feed showing up), we can buffer the batch, ingest a sample, observe the affected-entity distribution, and only then push the rest.

The general posture: redo is good, redo storms are an operational signal, and the response is observability plus replayability, not algorithmic suppression. We do not want Senzing to *not* redo. We want to know when it does, what it touched, and why.

## Speaker notes

- The timeline CSV is the right thing to put on screen during this section. Walk the audience through it row by row — the merge at step 4 and the split at step 6 are the moments to dwell on.
- This is the section where regulators and operators in the room will pay closest attention. Be precise about what is automatic, what is observable, and what an analyst can override.
- Avoid the word "stable" without qualification. An entity is stable until new evidence makes it not — that is the whole point. Say "stable under current evidence" if you need a phrase.
- Lineage is the bridge to explainability — set it up here, lean on it in Section 07 where we use graph signals to drive force-merge decisions.

## Assets

- `assets/data/06_update_timeline.csv` — a 7-step worked example of growth → merge → split for a single entity cluster.

## Open questions

- > [verify with Paco] Which Senzing features are the highest redo triggers in current production deployments, and any tunable limits on redo cascade depth.
- > [verify with Paco] Whether Senzing exposes a "why did this record cause N affected entities" diagnostic we can surface in the graph natively.
- Whether to demo a real redo storm in the live segment, or describe one from a past project. A demo is risky live; a story is safer.
