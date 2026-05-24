# Phase 1 — Data In, Exploded, Disconnected

> **We are here:** `SRC → DQ → GIN`. Data arrives, gets cleaned, lands in the graph.

## Narrative

Phase 1 is the part most teams underestimate. Records arrive from source systems, get aligned, and land in the graph **exploded** into nodes and relationships — and at this stage, **disconnected**: no entity has been resolved yet, no `EntityGroup` has been created. The graph holds knowledge about records, not resolutions. Resolution is Phase 2's job.

There are three properties this phase has to deliver, and they shape everything else:

- **Cleaned, but not destructively.** The alignment from Section 03 has run. Normalised columns sit beside the original raw payload; we keep both.
- **Exploded.** Each record is pulled apart. Scalar attributes — name, date of birth, nationality — sit as properties on the Record node. Structured identifiers that can be shared across records — passports, addresses, phone numbers — become their own nodes, linked back to the record.
- **Disconnected.** No `EntityGroup` exists yet. The records mention the same phone number, but the graph does not yet say they are the same person. That call belongs to Senzing.

### Cleaning does not have to be in Hume

The alignment step (Section 03) can happen wherever the customer's data pipeline already runs — dbt, Spark, Flink, a bespoke ETL service, or the warehouse. We do not insist on Hume / Neo4j as the home of normalisation. What we insist on is that, by the time data lands in the graph input layer, the records carry both the raw and the normalised payloads, and the dedup hash is computed.

The graph input layer is the *first place where ER becomes possible*, not the first place where data has to be touched.

### What "exploded" looks like

A record `KYC-001: Mohammed Al-Rashid, 1982-03-14, AE, passport P12345678` becomes, in the graph, something like:

```
(:Source {code: "KYC"})
  <-[:FROM]- (:Record:Person {record_id: "KYC-001",
                              name: "mohammed al rashid",
                              date_of_birth: "1982-03-14",
                              nationality: "ARE",
                              raw_payload: {...},
                              normalised_payload: {...},
                              dedup_hash: "38d2f8ef964b7af1",
                              ingested_at: ...})
              -[:HAS_PASSPORT]-> (:Passport {number: "P12345678",
                                             country: "ARE"})
```

Scalar attributes that belong unambiguously to the record — name, date of birth, nationality — sit as properties on the node itself. Identifiers and structured attributes that can be *shared across records* — passports, addresses, phone numbers — become their own nodes. The next record to arrive carrying passport `P12345678` will attach to the same `:Passport` node. This is what makes the graph queryable *before* resolution: we can ask "how many records carry this passport number?" without having asked Senzing yet.

`assets/diagrams/05_phase1_exploded.mmd` shows the explosion pattern with two records sharing some attributes and not others. The slide repo will render it as a small subgraph; we walk it on stage.

### And yet, disconnected

What is deliberately *missing* from this picture: any `EntityGroup`, any `RESOLVED_TO`, any claim that two records refer to the same real-world entity. Two records may sit on the same `:Passport` node, and the graph notices that as a *structural* fact — but the graph does not yet declare them to be the same person. That declaration is Senzing's call, made in Phase 2 with all the engine's feature scoring behind it, not a shortcut taken in Phase 1 because two strings happened to match.

`screenshots/min_aml_not_resolved.png` shows this directly with the min_aml dataset. Open Ownership (OO) and Open Sanctions (OS) records have both landed in the graph. You can see two disconnected clusters. The top cluster contains *Gold Wynn UK Holdings Limited* (reg `12524623`) and a person *Jeffrey Weinzweig* (DOB `1962-08-01`, Buffalo). The bottom cluster contains *GOLD WYNN UK HOLDINGS LIMITED* (same reg `12524623`) and *Jeffrey Mark Weinzweig* (same DOB, same address). Same company, same person — different source, different name string, different cluster. No edge between them. The graph holds the structural facts; it does not yet have the resolution. That is Phase 1 done correctly.

The reason matters. The minute Phase 1 starts making resolution decisions on its own, the architecture loses the property that *Senzing is the source of truth for resolution*. The graph would quietly disagree with the engine, and downstream consumers would have no idea which decision to trust. We do not do that. Phase 1 prepares; Phase 2 decides.

### What you have at the end of Phase 1

A graph. Disconnected. Data cleaned if you did the work in Section 03. Records sitting in the input layer, waiting for Senzing. That is it. Phase 2 starts here.

## Speaker notes

- The "exploded" diagram is the visual to land. Walk one record onto the screen, then a second sharing one attribute, and show the graph's structural fact appearing.
- "Disconnected" is the line that will surprise some audience members — they expect Phase 1 to do the resolution. Make the distinction sharp: structural facts (shared `:Passport` node) versus resolution decisions (`EntityGroup`).
- The "cleaning does not have to be in Hume" beat is for the customers in the room who already have a data platform. We are not asking them to rebuild it.

## Assets

- `assets/diagrams/05_phase1_exploded.mmd` — sample exploded subgraph: two records sharing a passport node, not yet resolved.
- `assets/data/03_persons_normalised.csv` — reuse from Section 03; this is the input to Phase 1.
- `screenshots/min_aml_not_resolved.png` — live Hume screenshot: OO and OS records in two disconnected clusters, Gold Wynn UK Holdings (reg 12524623) and Jeffrey Weinzweig appearing in both, no resolution yet.

## Open questions

Moved to [`../TODOS.md`](../TODOS.md).
