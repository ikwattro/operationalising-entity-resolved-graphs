# Phase 1 — Data In, Exploded, Disconnected

> **We are here:** `SRC → DQ → GIN`. Data arrives, gets cleaned, lands in the graph.

## Narrative

Phase 1 is the part most teams underestimate. Records arrive from source systems, get aligned, and land in the graph **exploded** into nodes and relationships — and at this stage, **disconnected**: no entity has been resolved yet, no `EntityGroup` has been created. The graph holds knowledge about records, not resolutions. Resolution is Phase 2's job.

There are three properties this phase has to deliver, and they shape everything else:

- **Cleaned, but not destructively.** The alignment from Section 03 has run. Normalised columns sit beside the original raw payload; we keep both.
- **Exploded.** Each record is pulled apart so its attributes are independently addressable in the graph. Names, identifiers, addresses, phones, dates — each becomes a node, each linked back to the record it came from.
- **Disconnected.** No `EntityGroup` exists yet. The records mention the same phone number, but the graph does not yet say they are the same person. That call belongs to Senzing.

### Cleaning does not have to be in Hume

The alignment step (Section 03) can happen wherever the customer's data pipeline already runs — dbt, Spark, Flink, a bespoke ETL service, or the warehouse. We do not insist on Hume / Neo4j as the home of normalisation. What we insist on is that, by the time data lands in the graph input layer, the records carry both the raw and the normalised payloads, and the dedup hash is computed.

The graph input layer is the *first place where ER becomes possible*, not the first place where data has to be touched.

### What "exploded" looks like

A record `KYC-001: Mohammed Al-Rashid, 1982-03-14, AE, passport P12345678` becomes, in the graph, something like:

```
(:Source {code: "KYC"})
  <-[:FROM]- (:Record:Person {record_id: "KYC-001",
                              raw_payload: {...},
                              normalised_payload: {...},
                              dedup_hash: "38d2f8ef964b7af1",
                              ingested_at: ...})
              -[:HAS_NAME]-> (:Name {value: "mohammed al rashid"})
              -[:HAS_DOB]->  (:DOB  {value: "1982-03-14"})
              -[:HAS_PASSPORT]-> (:Passport {value: "P12345678",
                                             country: "ARE"})
              -[:HAS_COUNTRY]-> (:Country {iso3: "ARE"})
```

The same attribute nodes are *shared* across records when the value matches. The next record to arrive carrying passport `P12345678` will attach to the same `:Passport` node. This is what makes the graph queryable *before* resolution: we can ask "how many records share this passport?" without having asked Senzing yet.

`assets/diagrams/05_phase1_exploded.mmd` shows the explosion pattern with two records sharing some attributes and not others. The slide repo will render it as a small subgraph; we walk it on stage.

### And yet, disconnected

What is deliberately *missing* from this picture: any `EntityGroup`, any `RESOLVED_TO`, any claim that two records refer to the same real-world entity. Two records may sit on the same `:Passport` node, and the graph notices that as a *structural* fact — but the graph does not yet declare them to be the same person. That declaration is Senzing's call, made in Phase 2 with all the engine's feature scoring behind it, not a shortcut taken in Phase 1 because two strings happened to match.

The reason matters. The minute Phase 1 starts making resolution decisions on its own, the architecture loses the property that *Senzing is the source of truth for resolution*. The graph would quietly disagree with the engine, and downstream consumers would have no idea which decision to trust. We do not do that. Phase 1 prepares; Phase 2 decides.

### What we get for free at the end of Phase 1

By the end of Phase 1, even before any ER has run, the graph already does useful work:

- **Source-volume reporting.** "How many KYC records do we have today? How many wires?"
- **Attribute reachability.** "How many records carry a passport? An address? A phone?"
- **Naive co-occurrence.** "Which addresses are mentioned by more than ten records?" — useful for finding postbox shells or shared buildings before Senzing has touched any of it.
- **Dedup-hash audit.** "Which raw records collapsed to the same hash, and which sources are involved?"

These are the kinds of dashboards we can stand up before the resolution engine is even connected. They make Phase 1 itself a deliverable, not just a setup step.

## Speaker notes

- The "exploded" diagram is the visual to land. Walk one record onto the screen, then a second sharing one attribute, and show the graph's structural fact appearing.
- "Disconnected" is the line that will surprise some audience members — they expect Phase 1 to do the resolution. Make the distinction sharp: structural facts (shared `:Passport` node) versus resolution decisions (`EntityGroup`).
- The "cleaning does not have to be in Hume" beat is for the customers in the room who already have a data platform. We are not asking them to rebuild it.
- This is also the moment to flag that the graph's first useful queries arrive before ER does. It reframes the project — value in week one, not week twelve.

## Assets

- `assets/diagrams/05_phase1_exploded.mmd` — sample exploded subgraph: two records sharing a passport node, not yet resolved.
- `assets/data/03_persons_normalised.csv` — reuse from Section 03; this is the input to Phase 1.

## Open questions

Moved to [`../TODOS.md`](../TODOS.md).
