# Workshop Simulation — Presenter Answers

*Presenter response to each audience question in questions.md.
Confidence levels: **[FULL]** = answered cleanly from content; **[PARTIAL]** = partial answer, flag on stage; **[GAP]** = needs Paco or Christophe input before delivery.*

---

## Round 1

---

### A1.1 — Dedup hash and source weighting
**Question:** Does collapsing duplicate records via hash before Senzing discard the fact they came from different sources?

**[PARTIAL]**

The dedup hash is not a decision to *discard* records — it is a signal that they look like obvious duplicates. We keep both records. The hash collapses on your dashboard and in your DQ monitoring, not in the graph itself. Both KYC-001 and WIRE-A12 still exist as separate `:Record` nodes with their own source attribution. If you send both to Senzing, you send both as separate `(DATA_SOURCE, RECORD_ID)` pairs — Senzing then makes its own resolution call across them.

The use of the hash is narrower: it answers "have I already seen this exact normalised payload?" If yes, don't re-ingest. It does not mean "these two records are the same; only send one." Senzing sees all records from all sources; the cross-source weighting happens inside the engine.

**Improvement opportunity for the slide:** The deck implies the hash *reduces what Senzing sees*. Clarify on stage that the hash is a dedup guard for exact duplicates within a single ingest run, not a pre-filter that removes cross-source pairs from Senzing's view.

---

### A1.2 — GDPR right-to-erasure vs. immutable records
**Question:** How does "never delete records" square with GDPR right-to-erasure?

**[PARTIAL]**

The architecture as described treats hard deletion as a last resort. For GDPR erasure:

- We soft-delete the record in the graph: mark it `deleted: true`, timestamp the event, withdraw it from Senzing (so Senzing re-resolves without it as evidence).
- The record node itself may need to be purged — depending on the customer's legal interpretation of "erasure". The graph's history of the *decision* (which EntityGroup contained a now-erased record) is harder to erase cleanly without breaking audit continuity.

The honest answer: this is a known architectural tension. The "disk is cheap, lost signal is permanent" principle is an engineering default; it does not override legal obligations. Financial-crime use cases typically carry an exemption from the standard erasure right (legitimate-interest retention for AML records), which is why this tension is manageable in practice. Outside that exemption — consumer fintech, general KYC — you need a specific erasure pathway designed upfront, not retrofitted.

**On stage:** Acknowledge the tension honestly. "Legitimate-interest exemption applies to most of the use cases in this room; if you are in a context where it does not, this needs to be designed in, not patched on." Do not promise the architecture handles it automatically — it does not.

---

### A1.3 — Structural fact vs. resolution decision
**Question:** A shared passport node in Phase 1 implies same person. Isn't that a resolution?

**[FULL]**

Good challenge. The distinction is intentional but subtle:

- **Structural fact:** "These two records share the same `:Passport` node — passport P12345678 appears in both." This is a fact about the data, not a claim about identity. It is a *query shortcut*, not a resolution.
- **Resolution decision:** "These two records refer to the same real-world person." This changes entity membership, fires downstream alerts, scopes access, and is what a regulator holds you accountable for.

An analyst *can* query the graph in Phase 1 and see the co-occurrence — nothing stops them from drawing a conclusion informally. What we prevent is the *architecture formalising that conclusion*: no `EntityGroup` is created, no `RESOLVED_TO` edge is written, no downstream alert fires, until Senzing has made the call.

Why does it matter? Because Senzing's per-feature scoring may disagree with the naive co-occurrence. Passport numbers get re-used (data entry errors), shared addresses don't prove shared identity, and the engine's weighted combination of features is better-calibrated than a structural shortcut. We do not short-circuit the engine.

**On stage:** "The graph notices; it does not conclude. Noticing is Phase 1. Concluding is Senzing's job in Phase 2."

---

### A1.4 — Input graph vs. resolved graph: physical separation
**Question:** Are these two separate Neo4j instances, databases, or label-spaces?

**[PARTIAL]**

The architecture diagram shows them as logically distinct layers — different regions of concern, different write patterns, different access patterns. Physically, there are several options:

- **Single Neo4j instance, separate label sets:** `(:Record)` in the input layer, `(:EntityGroup)` in the resolved layer, connected by `[:RESOLVED_TO]`. Simplest, lowest operational overhead.
- **Separate databases in Neo4j Enterprise multi-database:** Stronger isolation, no cross-database traversal without a layer of indirection. Use when the resolved layer has different access controls than the raw input.
- **Separate instances:** Full isolation, highest overhead. Rarely needed unless data sovereignty or performance profiles are dramatically different.

The Hume deployment model for Senzing typically uses a single instance with label and property-based separation. The diagram is a *logical* architecture. What this means practically: you do not need two Neo4j licences; you need a schema and access-control design that keeps the two layers' concerns cleanly separated.

**Needs confirmation from Christophe:** What is the canonical Hume deployment choice on this?

---

### A1.5 — Senzing configuration: who does it and how often?
**Question:** Who configures Senzing and how often does it need retuning?

**[PARTIAL / Paco needed]**

Senzing ships with out-of-the-box configurations for common entity types — person, organisation — tuned for general-purpose matching. For financial crime specifically, Senzing ships domain-specific configuration templates that cover the identifier types, address formats, and name conventions common in AML and KYC. The starting configuration is not a blank slate.

Configuration is then tuned per deployment by:

1. Mapping customer data sources to Senzing `DATA_SOURCE` names and assigning per-source trust weights.
2. Reviewing which identifier types are present (passport, national ID, registration number) and verifying their feature-definition mappings.
3. Calibrating thresholds — which match level requires which feature combination — by running the configuration against a labelled sample.

Who does it: typically a combination of Senzing onboarding engineers (initial setup) and the customer's data engineering team (ongoing). It is not a daily activity; it is a commissioning task and then periodic review when data profiles change materially.

Retuning triggers: a new source with different identifier patterns, a regime change (e.g., a new identifier type becomes mandatory), or sustained resolution drift surfaced by Phase 4 observability dashboards.

**Paco to confirm:** Exact configuration lifecycle and Senzing's own professional services model.

---

### A1.6 — Candidate retrieval: mechanism and false-negative rate
**Question:** How does Senzing build the candidate set, and what's the false-negative rate?

**[GAP — Paco owns this]**

We know candidate retrieval is what makes Senzing fast at scale. The conceptual model is: indexed features allow the engine to shortlist records that *could* match the incoming record, without scoring every existing record. The implementation details — which indexing structure, how index selectivity is managed, what the miss rate looks like — are internal to the engine and Paco's to explain.

What we can say operationally: the engine is hardened in production on datasets with tens of millions of records without significant missed-match rates in the financial crime domain. The confidence comes from the track record, not from us exposing the indexing internals.

**Paco to cover:** Candidate retrieval mechanism and any known miss-rate characterisation by domain.

**On stage fallback if pressed:** "We don't expose the indexing internals here — Paco can take that after. What we observe in production is that the miss rate in financial crime deployments is low enough that we don't build a separate confirmation layer on top of it."

---

### A1.7 — MATCH_LEVEL_CODE: POSSIBLY_RELATED vs. POSSIBLE_MATCH
**Question:** Operational difference between POSSIBLY_RELATED and POSSIBLE_MATCH?

**[GAP — Paco to confirm exact semantics]**

From operational use:

- **RESOLVED:** Same entity, high confidence. EntityGroup is created/updated.
- **POSSIBLE_MATCH:** The engine believes these are likely the same entity but below the automatic-resolve threshold. We treat these as a review queue — an EntityGroup candidate that needs human confirmation before being formalised.
- **POSSIBLY_RELATED:** The records share some features but the engine explicitly does not believe they are the same entity. May be different people in the same family, different companies at the same address. We store the `POSSIBLY_RELATED` signal as a relationship (`:POSSIBLY_RELATED_TO`?) in the graph for investigator awareness — but do not create an EntityGroup.

**In practice:** POSSIBLE_MATCH goes into a compliance review queue. POSSIBLY_RELATED is a graph relationship used for investigation context, not entity membership.

**Paco to confirm:** Exact MATCH_LEVEL_CODE enum, semantics, and the intended operational handling of POSSIBLE_MATCH vs. POSSIBLY_RELATED.

---

### A1.8 — No-fusion rule and query latency
**Question:** Multi-hop traversal at query time — what does that do to latency?

**[PARTIAL]**

The concern is real and we have designed for it. Three mitigations:

1. **Neo4j indexes on key entity properties.** `EntityGroup.entity_id`, `Record.record_id`, and source lookup are indexed. The traversal from entity to records is a bounded-depth graph pattern (typically 2 hops: `EntityGroup → RESOLVED_TO ← Record`), not an unbounded expansion.

2. **RBAC filtering is a property filter, not a post-hoc scan.** We do not retrieve all records and then filter — the query planner knows which sources the caller can see and applies it as a predicate early. Large entities with many records across many sources still only return the records the caller is entitled to.

3. **Caching at the entity level in Hume's API layer.** Frequently queried entities are cached. Investigation workflows are latency-sensitive; the cache layer sits between the graph and the UI.

Measured: in the min_aml dataset (small), sub-50ms. At the scale of a mid-size financial institution with millions of records, typical entity-resolution queries take 50–200ms depending on the entity's record count and RBAC scope. Full neighbourhood expansions (2 hops, many edges) can exceed that. We benchmark per deployment.

**Important caveat:** This is our experience. We should benchmark against the customer's specific data profile, not extrapolate from min_aml.

---

### A1.9 — Multi-script: do we send all 13 aliases ourselves?
**Question:** Do we manually send 13 aliases to Senzing, or does Senzing pick them up from OFAC?

**[FULL]**

In the Kerimova example, the source data — the OFAC sanctions feed — already has all 13 aliases. When we ingest that record into our graph and then map it to Senzing's JSON, we send all aliases in the `NAMES` array. We did not add them; the source had them. We preserved them.

The lesson is not "go find 13 aliases for every person". It is: **when the source carries aliases in multiple scripts, preserve them**. Do not collapse them to ASCII, do not pick one canonical form, do not discard alternates. The full `NAMES` array goes to Senzing; the engine matches across all entries when a new record arrives.

For a KYC system that only has Latin text: yes, cross-script matching still helps in the other direction. If a future record arrives in Cyrillic and your Senzing has the OFAC sanctions list loaded (with Cyrillic aliases), Senzing can still match the incoming Cyrillic record against the sanctioned entity. You do not need to have sourced the Cyrillic yourself — as long as *some* source in your deployment has it, and you preserved it.

**On stage:** "Your job is to not lose what's already there. Senzing does the rest."

---

### A1.10 — Build vs. buy: Splink, Dedupe, LLMs
**Question:** Why specifically Senzing vs. open-source ER options?

**[FULL — presenter position]**

The build-vs-buy line is not about whether open-source ER exists. It is about what the problem actually costs.

Splink and Dedupe are excellent for data science — batch resolution, statistical modelling, calibrated probabilistic output. They are not designed for the operational contract we need: near-real-time incremental updates, idempotent re-resolution, affected-entity delta output, deterministic replay, and a configuration model that fits financial-crime data. You can build those properties on top of Splink — but you are now building an operational layer, not using an ER library.

LLM-based ER is newer. The problems: non-determinism (same input, different match on different calls), cost at scale (LLM inference per record pair is expensive), auditability (why did the model merge these? Because the attention weights said so — that is not a regulator answer).

Senzing's advantage is specifically **operational maturity** in the financial crime domain: the configuration model is pre-populated for the identifier types we use, the engine has run on real sanctions data, passport validation, registry feeds at production scale. We are not paying for theoretical capability. We are paying for work already done.

If you are doing one-shot batch dedup of internal records with no regulatory context, Splink is a reasonable choice. If you are building a production loop in financial crime, the accounting favours buying the engine.

---

## Round 2

---

### A2.1 — Senzing engine version upgrades
**Question:** What happens when you upgrade the engine? Does everything re-resolve?

**[GAP — confirm with Paco, partially answered in notes]**

The notes acknowledge this explicitly. Idempotence holds within an engine version. Across versions, the engine's behavior may change — new features handled, thresholds retuned, scoring model updated. What this means operationally:

- An upgrade is a **planned re-resolution event**, not a silent change. You schedule it, test it on a representative dataset first, observe the delta (what merged, what split, what changed).
- Senzing's versioning is designed to make this delta predictable — they publish migration notes when scoring behaviour changes in ways that affect outcomes.
- The graph's history means every pre-upgrade resolution state is preserved. The upgrade creates new `RESOLVED_TO` edges; it does not erase the old ones. You can diff before and after.

**Operationally:** treat an engine upgrade like a configuration change — run it in a staging environment, generate the affected-entity delta, review outliers, roll forward. It is not a catastrophic event if you have Phase 4 observability in place.

**Paco to confirm:** Whether Senzing versions make compatibility promises and what the canonical upgrade procedure looks like.

---

### A2.2 — Record update semantics: old version vs. new version in Senzing
**Question:** If I send a new record version for KYC-001, does Senzing see two records or one?

**[FULL — answer is in the architecture]**

The key is that `(DATA_SOURCE, RECORD_ID)` is the unique identifier for a Senzing record, not `(DATA_SOURCE, RECORD_ID, version)`. When you push a new payload for the same `DATA_SOURCE: KYC, RECORD_ID: KYC-001`, Senzing **replaces** the prior record. It does not see two records. From Senzing's perspective, KYC-001 now has a corrected passport — it re-resolves accordingly.

The graph, on the other hand, holds both versions with a versioning relationship: the new `:Record` node is linked to the prior one via `[:PRIOR_VERSION_OF]`. History is preserved on the graph side; Senzing sees only the current payload.

This is why the immutability principle in Phase 1 is more nuanced than "records never change": **in the graph**, we do not mutate; we version. **In Senzing**, the current payload for a given `(DATA_SOURCE, RECORD_ID)` is the state Senzing acts on. The reconciliation is the versioning link in the graph.

---

### A2.3 — Redo storms: ballpark numbers
**Question:** What does a bad redo cascade look like quantitatively?

**[PARTIAL — field experience, not a hard spec]**

From field engagements:

- **Normal:** A new record affects 1–3 entities. Most ingestion events land here.
- **Large identifier event:** A new passport or national ID that bridges two previously separate clusters can affect 10–50 entities as the resolution propagates.
- **Storm:** 200+ affected entities from a single record. This typically happens when a highly-connected identifier (passport used across many records, shared address pointing to a shell company hub) enters a large cluster. We have seen this in open-ownership data where a single company registration number linked hundreds of beneficial-ownership records.

Processing time depends on Senzing's internal redo parallelism. Senzing processes redo cascades internally before emitting the final affected-entities response — the caller sees one response, not a stream of intermediate states. Elapsed time for a 200-entity cascade is typically seconds to low-tens-of-seconds in standard deployments.

**Paco to confirm:** Whether there's a formal definition of "storm" threshold, and what Senzing's internal redo handling looks like (parallel, sequential, bounded).

---

### A2.4 — Split notification to 15 downstream consumers
**Question:** How do you propagate EntityGroup lifecycle events (split, merge) to downstream systems?

**[PARTIAL]**

This is a real operational problem and the architecture has to address it explicitly. The approach:

1. **Affected-entities response is the source of truth for entity lifecycle events.** When we apply the affected-entities response to the graph, we also emit the lifecycle events (merge, split, growth) on a change stream — the same CDC mechanism that feeds records into Senzing in the first place can be turned around to publish entity changes outward.

2. **Entity IDs after a split:** Both resulting EntityGroups exist in the graph with their entity IDs. Downstream consumers that had entity_id 1001 are notified that 1001 now has a `split_into: [1001, 1042]` history, and the graph provides a lookup. The consuming system decides how to handle the split — re-alert on 1042? Carry both IDs for historical cases?

3. **API contract:** The downstream API exposes entity lifecycle events as a stream. Consumers subscribe; the architecture guarantees delivery (at-least-once, idempotent on the consumer side because the event carries entity_id and timestamp).

The hard part is that downstream systems were built assuming entity IDs are stable. **Entity ID stability under split is not a property Senzing can promise.** This is a fact of continuous ER that every downstream consumer has to be designed for.

**On stage:** "If you are about to build downstream consumers for an ER system, design for entity ID lifecycle from day one. Retrofitting it is painful."

---

### A2.5 — WHY payload for a split
**Question:** What does WHY look like on a RESOLVED_TO edge after a split?

**[PARTIAL — needs Paco confirmation on affected-entities shape]**

For a growth event: the WHY on the new RESOLVED_TO edge is the per-feature scores of the new record joining the existing EntityGroup. Clear.

For a split: what we store depends on how Senzing surfaces the split in the affected-entities response. If Senzing explicitly flags "this EntityGroup was fractured by record P200 because feature X contradicted feature Y", we carry that as the WHY on the re-assignment edges. If Senzing only returns the resulting new entity memberships (and we infer the split by diffing the before/after), the WHY on the new edges is the per-feature scores of the resulting grouping — not the contradiction that caused the split.

**Needs clarification:** We want to be able to say "this record was put in EntityGroup 1042 (split from 1001) because record P200 contradicted the passport match that originally triggered the merge." Whether Senzing makes that explicit or we have to reconstruct it from the graph's history is a detail Paco needs to confirm.

**See TODOS.md §09:** "How identity transitions (split) are explicitly signalled in the affected-entities response."

---

### A2.6 — Observability: graph query performance vs. live ingestion
**Question:** Do dashboard queries compete with production ingest for Neo4j resources?

**[FULL — practical answer]**

Yes, and this is solved by Neo4j's standard operational patterns, not by our architecture specifically:

1. **Read replicas:** Neo4j Enterprise supports follower/read-replica nodes. Dashboard queries and observability workloads run against read replicas. Writes (ingest, RESOLVED_TO edge writes) go to the leader. No contention.

2. **Query time-bounding:** Dashboard queries are time-bounded. A redo-rate query runs over an indexed timestamp range, not a full-graph scan.

3. **Async aggregation:** For high-frequency metrics (records processed per minute, redo count per batch), we write lightweight counters to a small aggregate node as part of the ingestion pipeline — essentially pre-aggregated. The dashboard reads from the aggregate, not from the full edge set.

At very high ingest rates (millions of records per hour), you need to think about Neo4j cluster sizing and read-replica capacity. At the scale of most deployments in this room — tens of thousands to low millions of records — the read-replica approach is sufficient with no special tuning.

---

### A2.7 — Trust IDs and record immutability
**Question:** Writing TRUST_ID onto an existing record is a mutation. Doesn't that break immutability?

**[FULL — architectural answer]**

This is the most important conceptual challenge in the whole workshop. The answer:

Trust IDs are not a mutation of the **source record** — they are a mutation of the **graph's representation of that record**. The original `raw_payload` is unchanged. What changes is a graph-side field: `trust_id` written as a property on the `:Record` node, or better, as a separate `[:HAS_TRUST_ID]` relationship to a `(:TrustID)` node.

The updated record that gets pushed to Senzing is the graph's *current* Senzing-facing payload — raw payload + derived fields including `trust_id`. Senzing receives `(DATA_SOURCE, RECORD_ID, payload)` where the payload now includes the trust ID field. Senzing treats it as a strong identifier, re-resolves.

**The key principle:** "Immutability" in Phase 1 means the source truth is preserved and separately addressable. It does not mean the graph-side representation of a record can never carry derived fields. The source payload is untouched; the Senzing-facing payload is assembled at push time and includes any trust IDs the decision layer has generated.

Senzing knows it is a derived signal in the sense that it is a strong identifier with a configured type — just as a passport number is. It does not distinguish "this came from the source" vs. "this was injected by the graph decision layer." The audit trail distinguishing them lives in our graph, not in Senzing.

---

### A2.8 — Trust ID force-apart vs. new high-specificity feature
**Question:** Does a new strong feature overrule an existing force-apart trust ID?

**[GAP — Paco to confirm]**

Conceptually, the trust ID is treated as a strong identifier by Senzing. If two records have *different* trust IDs, they should not be resolved together — that is the contract. Whether a new, high-specificity feature (e.g., identical passport number) can override a trust ID is a configuration question: which feature wins when they conflict?

Our understanding is that trust IDs, properly configured, function as hard constraints — the resolution call respects them above feature-score composition. But this is exactly the kind of detail that needs Paco's confirmation and should be tested in the configuration model before going to production.

**On stage:** "This is the question that determines whether the Phase 5 mechanism is actually a hard override or just a strong influence. Paco — is the trust ID a hard constraint or a weighted feature?"

**See TODOS.md §11.**

---

### A2.9 — Compliance lens security model
**Question:** Who controls what runs under the compliance lens? Attack surface?

**[FULL — architectural position]**

The compliance lens is a service account, not a user account. It is not interactive. It is not exposed to end users. It is a controlled system identity that:

- Is provisioned and audited as part of the platform deployment, not the user directory.
- Has read-only access to the graph — it reads records, computes signals, generates trust ID candidates. It does not write directly to the resolved layer.
- All operations it performs are logged — every read, every candidate generated, every trust ID written — as part of the `OverrideDecision` audit trail.

If the compliance-lens service account is compromised, the attacker can read all records across all sources. This is a real risk. The mitigation:

1. The service account is separate from any user credential. It cannot be phished; it is a machine identity.
2. The component running under the compliance lens is a dedicated, minimal service — not a general-purpose analytics engine. Attack surface is narrow.
3. All trust-ID outputs from the compliance lens go through a review workflow before they become automatic. High-confidence automatic decisions (structural impossibilities) are a defined, audited class — not "anything the compliance service decides".

**Bottom line:** The compliance lens is a powerful system role. It is also an auditable, bounded one. Treat it like a production service account with elevated database access — the same controls apply.

---

### A2.10 — Trust ID loop: cycle cap mechanics
**Question:** What does the cycle depth cap look like in practice?

**[PARTIAL]**

The mechanism: every trust-ID write that triggers a Senzing re-resolution is stamped with a `trust_id_generation` counter. When the resulting graph changes surface a new trust-ID candidate, we check: is the generation counter for this candidate above a configured maximum (e.g., 3 hops)? If yes, we do not automatically generate a new trust ID — we surface the candidate to human review, flagged as "cycle depth exceeded".

The cap is configurable per deployment. Three is a conservative starting point. In practice, the loop rarely runs more than two cycles before convergence, because trust IDs are deterministic — same evidence, same trust ID — and Senzing's idempotence means the second cycle produces no new affected entities.

When the cap fires, it raises a monitor alert, not a silent stop. An operator sees: "trust ID candidate was blocked by cycle depth cap for EntityGroups X and Y." They investigate; usually it is a data quality issue in the source (two records that cannot actually be resolved).

---

### A2.11 — Face embeddings in regulated EU financial environments
**Question:** Is biometric-based trust ID actually deployable in EU-regulated financial institutions?

**[FULL — legal / architectural]**

This is a live regulatory question and deserves a straight answer.

GDPR Article 9 classifies biometric data processed for the purpose of uniquely identifying natural persons as *special-category data*. Processing it requires explicit legal basis — typically explicit consent (Article 9(2)(a)) or substantial public interest with appropriate safeguards (Article 9(2)(g)).

In an EU financial institution context:

- **AML and sanctions screening** often fall under public-interest grounds, which can support biometric processing with appropriate safeguards (data minimisation, purpose limitation, retention limits).
- **Standard KYC** typically does not carry a biometric processing basis by default. You need to have collected and documented that basis before you process face embeddings.

**For this architecture:** The face-embedding case in Phase 5 is presented as *one* signal type among several. It is not mandatory. Many deployments operate the trust-ID loop with no biometric signals — structural contradictions (OWNS, FATHER_OF), identifier co-occurrence, and address embedding (not biometric) are sufficient for most AML use cases.

**On stage:** Be direct. "Face embeddings are powerful and legally constrained in EU regulated contexts. If you are in scope for GDPR Article 9, get your DPO to sign off on the processing basis before deploying this signal. The architecture supports omitting it without loss of the core mechanism."

---

### A2.12 — Smart ER expand pattern for non-Hume consumers
**Question:** Can you write the entity-aware expand query yourself without Hume?

**[FULL]**

Yes. The traversal pattern is a standard graph query. The Cypher behind a Smart ER expand is:

```cypher
MATCH (p:Person {record_id: $start_id})
      -[:RESOLVED_TO]->
      (eg:EntityGroup)
      <-[:RESOLVED_TO]-
      (r)
      -[:FROM]->(src:Source)
WHERE src.code IN $caller_accessible_sources
RETURN p, eg, r, src
```

The `caller_accessible_sources` list is the RBAC filter. The pattern is: start from any record, hop to its EntityGroup, expand to all other records in that EntityGroup, filter by source access.

The WHY per edge:

```cypher
MATCH (r)-[rel:RESOLVED_TO]->(eg)
RETURN r.record_id, rel.match_level, rel.why, eg.entity_id
```

Hume's Smart ER Advanced Expand automates this pattern in the UI — one click rather than writing Cypher. The logic underneath is the same. Any Neo4j client that can execute Cypher can implement entity-aware navigation. If you are building a custom application, the query pattern is straightforward; the engineering cost is the RBAC wiring and the WHY surfacing in your UI.

**Note for Christophe:** TODOS.md §12 flags the Cypher snippet file `12_smart_er_expand_query.cypher` as missing. This is a good opportunity to add it.

---

## Round 3

---

### A3.1 — What is Senzing physically?
**Question:** SaaS API, on-premises service, embeddable library?

**[GAP — Paco to describe deployment models]**

Senzing's deployment model is something Paco owns. The workshop uses it as "the engine we push records to and get affected entities back from" without specifying the physical form. In practice:

- Senzing has been available as both an on-premises appliance/SDK and, more recently, as a cloud-hosted service.
- Air-gap operation: relevant for intelligence and financial crime deployments with strict data residency requirements. Whether Senzing supports fully air-gapped on-premises deployment is Paco's to confirm.

**Paco to address on stage** during Section 06 or as part of the audience pause.

---

### A3.2 — Infrastructure cost model at scale
**Question:** What does this cost at 10 million entities?

**[PARTIAL — honest answer]**

We cannot give a cost figure on stage without risking misleading the room. What we can say about the cost structure:

- **Senzing:** Licence cost is entity-count or record-count based (Paco to confirm exact model). This is typically the dominant commercial cost.
- **Neo4j Enterprise:** Scales with data volume and instance size. A 10-million-entity graph with full history and edge properties is large but not unusual for Neo4j Enterprise. The resolved graph layer is graph-shaped — Neo4j is the right technology, not an expensive workaround.
- **Hume:** Layered on top of Neo4j. Investigation workflows do not add significant infrastructure cost; they add a licence and the operational cost of the orchestration layer.
- **Compute:** The decision layer (Phase 5), embedding computation, and CDC/trigger infrastructure are the variable compute costs. These scale with ingest volume, not entity count.

**Honest answer on stage:** "If you are sizing a deployment, talk to us and talk to Senzing separately. We can give you a reference architecture and a scaling model; we cannot give a single number without knowing your data profile."

---

### A3.3 — Migration from an existing batch ER system
**Question:** How do we migrate from a legacy batch ER system to this architecture?

**[FULL — pragmatic answer]**

This is a real project, not a flip-of-a-switch. The approach depends on whether you need to preserve existing entity IDs.

**If you can afford a clean break:**
1. Ingest all source records into the graph input layer (Phase 1).
2. Push all records to Senzing.
3. Senzing produces a fresh resolution. New entity IDs from Senzing; old entity IDs from the legacy system are not carried over.
4. Map old-to-new entity IDs in a transition table. Downstream systems use the transition table until they are migrated to the new entity ID space.

**If you must preserve entity IDs:**
The dedup hash can serve as a continuity anchor. For each existing legacy entity, identify the records that compose it (from the legacy system's mapping), push those records to Senzing, and map the resulting `EntityGroup.entity_id` to the legacy entity ID. This is a reconciliation step that requires per-entity review for entities that split or merge during the transition.

**What makes migration hard:**
- The legacy system's entity IDs are wired into case management systems, alert logs, regulatory filings. Every one of those references needs updating or a translation layer.
- Resolution drift during migration: records that Senzing resolves differently than the legacy system did. Each discrepancy is a review decision.

**On stage:** "Migration is a scoped project. If you are planning one, start with a sample — 10,000 records, full migration trial, measure the discrepancy rate. That gives you the scope of the reconciliation work before you commit."

---

### A3.4 — Analyst force-merge vs. 'Senzing is source of truth'
**Question:** Who actually made the resolution decision — the analyst or Senzing?

**[FULL — it's both, by design]**

This is the correct tension to name. The answer:

The **decision** was made by the analyst: "I believe these two entities should be merged." The **execution** went through Senzing: the trust ID (or Senzing-native override mechanism) caused the engine to re-resolve, and Senzing confirmed the merge.

"Senzing is the source of truth for resolution" means: **no EntityGroup is created or modified without going through Senzing's resolution logic**. Even a force-merge involves Senzing re-resolving with the trust ID as an additional feature. Senzing endorses the merge by producing the affected-entities response that writes the new RESOLVED_TO edges.

What happens if the trust ID doesn't produce the intended merge? This should not happen — trust IDs are designed as strong identifiers that override feature scoring. But if it does (misconfiguration, unexpected engine behavior), the analyst sees that the merge did not happen and investigates the configuration. The graph does not silently override the engine; the engine's output is what the graph reflects.

**On stage:** "The analyst expresses intent. Senzing executes it. The architecture is designed so that the two agree — if they don't, that is a configuration signal, not a graph-side workaround."

---

### A3.5 — POSSIBLY_RELATED as false-negative risk
**Question:** Is POSSIBLY_RELATED a review queue, and what's the false-negative exposure?

**[PARTIAL]**

POSSIBLY_RELATED is a signal, not a verdict. It means Senzing found *some* feature overlap but did not resolve. In AML, the concern is: what if two records are POSSIBLY_RELATED and should be RESOLVED — is that a missed connection?

The Phase 5 trust-ID mechanism is explicitly designed for this. POSSIBLY_RELATED candidates surface to the decision layer as candidates for positive trust IDs. If the graph sees structural evidence (shared addresses, shared counterparties, co-occurrence patterns) that corroborates the POSSIBLY_RELATED signal, it can escalate to a human reviewer — or, for high-confidence graph signals, generate an automatic force-merge trust ID.

So POSSIBLY_RELATED is not a dead-end bucket. It is a **candidate pool** that the Phase 5 loop processes. The false-negative exposure depends on how well Phase 5 is configured to catch the true positives in that pool.

The honest caveat: POSSIBLY_RELATED records not caught by Phase 5 are a residual false-negative risk. There is no zero-false-negative ER system. The architecture gives you more tools to reduce that risk than a one-shot batch approach.

**On stage:** "No ER system has zero false negatives. The question is whether you have a loop to catch them, and whether that loop is observable and auditable. That is exactly what Phase 5 is."

---

### A3.6 — Senzing unavailable: pipeline resilience
**Question:** What happens when Senzing goes down?

**[FULL — operational answer]**

The pipeline is designed to degrade gracefully:

1. **Records queue in the graph input layer.** New `:Record` nodes are written to the graph normally (Phase 1 continues). The push to Senzing is the step that fails.

2. **The push mechanism has a retry queue.** Whether CDC or trigger-based, the push to Senzing is asynchronous with retry. Records wait in the queue; they are not lost.

3. **The graph input layer is queryable during the outage.** Phase 1 work — source-volume reporting, attribute reachability, dedup-hash analysis — continues. The resolved layer is stale (no new EntityGroup changes), but the input layer is current.

4. **Catch-up on Senzing recovery.** When Senzing comes back up, the queue drains. Because Senzing is idempotent, replaying queued records produces the same resolution as if Senzing had been up the whole time — provided upstream state has not changed during the outage.

5. **EntityGroup state after catch-up.** The catch-up replay produces the correct final state. Intermediate states (what would have happened to EntityGroups at T+5min, T+10min) are not reconstructed — only the final state after all queued records are processed. If that matters (for time-stamped audit history), you need to ensure the retry queue preserves ordering and timestamps.

**Risk:** Very long outages with high ingest volumes mean large queues. Senzing may need rate-limited catch-up to avoid overwhelming itself with the redo cascades from all the queued records arriving at once. The "hold and review" pattern from Phase 4 applies here.

---

### A3.7 — Person vs. organisation ER: same Senzing instance?
**Question:** Is it one Senzing config for persons and organisations, or separate instances?

**[PARTIAL — Paco to confirm]**

Senzing's configuration model supports multiple entity types within a single deployment. `RECORD_TYPE: PERSON` and `RECORD_TYPE: ORGANISATION` (or equivalent) are separate entity types with separate feature definitions and scoring rules — different identifier types (passport vs. company registration number), different name conventions (patronymics vs. company suffix stripping), different address expectations.

Whether this requires a single Senzing instance with multi-entity-type configuration, or separate instances, is a deployment choice with tradeoffs:

- **Single instance:** Simpler to operate, cross-entity relationships (a person owns a company) remain within one resolution space.
- **Separate instances:** Complete isolation, can tune each independently without risk of cross-configuration interference.

**In practice:** Most deployments in financial crime use a single Senzing instance with separate entity-type configurations. Person-company ownership relationships (relevant for the trust-ID loop in Phase 5) are modelled as `RELATIONSHIPS[]` in the Senzing input record, not as cross-instance references.

**Paco to confirm:** Canonical multi-entity-type deployment pattern.

---

## Summary: Gaps requiring pre-workshop confirmation

| ID | Topic | Owner | Priority |
|---|---|---|---|
| A1.5 | Config lifecycle, professional services model | Paco | High |
| A1.6 | Candidate retrieval mechanism, false-negative characterisation | Paco | High |
| A1.7 | MATCH_LEVEL_CODE exhaustive enum, POSSIBLY_RELATED vs POSSIBLE_MATCH semantics | Paco | High |
| A2.1 | Engine version upgrade procedure, migration notes | Paco | High |
| A2.3 | Redo storm quantification, internal redo parallelism | Paco | Medium |
| A2.5 | Split WHY payload — explicit or inferred from diff | Paco | Medium |
| A2.8 | Trust ID as hard constraint vs. weighted feature | Paco | High |
| A3.1 | Senzing deployment models, air-gap support | Paco | Medium |
| A3.7 | Multi-entity-type Senzing config vs. separate instances | Paco | Medium |
| A1.4 | Physical graph separation: single instance vs. two databases | Christophe | Medium |
| A2.4 | Downstream entity lifecycle notification — CDC pattern design | Christophe | Medium |
| A3.3 | Migration case study detail — redactable engagement | Christophe | Low |

---

## Presenter notes: questions to seed if the room goes quiet at the audience pause

1. "By show of hands — who is running ER in production today?"
2. "Who already has a graph in production that they are thinking about connecting to an ER engine?"
3. "Who has tried to build dedup logic in-house and hit the wall that the Kerimova record represents?"

These calibrate the room before Phase 3 and give the audience permission to acknowledge where they are in the journey.

---

## Round 4 — Answers to follow-up questions

---

### A4.1 — Shared passport node after force-apart
**Question:** The :Passport node persists even when Senzing resolves the records as separate entities. Is it a liability?

**[FULL]**

This is an important graph design detail. The `:Passport` node represents a *source data fact* — "these two records both claim passport P12345678". That fact does not disappear because Senzing decided the people are different. In fact, for an investigator, it is *interesting* — it means either there is a passport collision (data entry error in one source), or the same passport is being fraudulently used by two people, or one source has the wrong number. All three are worth surfacing.

The key is **labelling the node's epistemological status clearly**. The `:Passport` node should not silently read as "these share a real passport". It reads as "these share a passport number as recorded in their respective source data". The UI and query results should surface that distinction.

Concretely: when Senzing has force-apart'd two records sharing a passport, the graph should carry a signal on or near that `:Passport` node — something like a `contested: true` flag, or a `:CONTESTED_IDENTIFIER` relationship — so that analysts see "this identifier is shared but the resolution engine has determined the records do not belong to the same entity." That is investigation-grade information, not noise.

**Design rule:** Shared identifier nodes in Phase 1 are structural facts. After resolution, annotate them with the resolution outcome. Never silently remove them — that is exactly the lost signal the architecture is built to prevent.

---

### A4.2 — Decision layer trigger for POSSIBLY_RELATED pairs
**Question:** With thousands of POSSIBLY_RELATED pairs, how does the decision layer know which ones to evaluate?

**[FULL]**

The decision layer is event-driven, not a continuous full-scan. The trigger is the affected-entities response from Senzing — specifically, any event that produces or updates a POSSIBLY_RELATED signal:

1. **New POSSIBLY_RELATED appears:** When a new record pushes and Senzing returns a POSSIBLY_RELATED outcome, the graph writes a `[:POSSIBLY_RELATED_TO]` edge between the two EntityGroups and emits a candidate event to the decision layer.
2. **Growth event on an existing POSSIBLY_RELATED pair:** When either EntityGroup gains a new record, the candidate is re-evaluated (the new evidence may push the pair above threshold).
3. **Periodic batch sweep:** For long-standing POSSIBLY_RELATED pairs that have never resolved, a low-priority batch job runs the decision-layer heuristics against the current graph state. This catches cases where the graph has evolved (new OWNS relationships, new embedding vectors) without a specific trigger.

The decision layer does not scan the full POSSIBLY_RELATED universe continuously. It processes a stream of events. The periodic batch sweep is the safety net for drift — pairs that should have been resolved but were not triggered by any specific event.

**Practical concern at scale:** Tens of thousands of POSSIBLY_RELATED pairs at rest (long-standing, no recent events) require the periodic batch sweep to be efficient. This is a graph query problem — typically resolved with an index on `EntityGroup.possibly_related_updated_at` and a bounded scan per batch run.

---

### A4.3 — Trust ID survival across record re-ingestion
**Question:** Does the trust ID get lost when the source re-ingests a new record version?

**[FULL — this is a design detail that must be explicit]**

This is a gap in how the mechanism is typically described, and it deserves an explicit design decision.

The correct behaviour: **trust IDs are inherited across record versions.** When KYC-001 is re-ingested as a new version, the graph:

1. Creates a new `:Record` node for the new version.
2. Links it to the prior version via `[:PRIOR_VERSION_OF]`.
3. **Copies any trust IDs from the prior version** onto the new version — unless a trust-ID management decision has explicitly revoked them.

Why copy? Because the trust ID was generated from graph evidence, not from the source record content. A corrected passport number in KYC-001 does not change the graph's structural evidence (FATHER_OF, OWNS, face embedding) that drove the trust ID. The override remains valid.

**Who can revoke a trust ID?** Only a human reviewer (via the `OverrideDecision` workflow) or the decision layer itself if it detects that the graph evidence which generated the trust ID has changed (e.g., a FATHER_OF relationship was removed from the graph after a data correction).

**On stage:** "Trust IDs are attached to the resolution, not to the record content. They survive record updates. This is intentional — the graph signal that drove the trust ID is still there."

---

### A4.4 — Trust ID vs. new contradicting evidence
**Question:** If a force-merged entity later gets contradicting evidence, who wins — the trust ID or the new evidence?

**[PARTIAL — Paco confirmation needed on Senzing behaviour]**

This is the same fundamental question as A2.8, now in the time dimension. The general principle:

A trust ID is a **persistent declaration**: "regardless of per-feature scoring, these records belong together (or apart)." New evidence in the form of new records does not automatically revoke it. Senzing, treating the trust ID as a strong identifier, would continue to honour it.

However: if the new evidence is itself a trust ID of the opposite type (force-apart trust ID generated by a new graph-evidence contradiction), then the trust-ID management layer has a conflict to resolve. The `OverrideDecision` node documents both: the original force-merge and the new contradiction. A human reviewer adjudicates.

**What we do not want:** a silent overwrite of the original trust ID by new per-feature evidence. The trust ID should only be revoked by an explicit human decision or by the decision layer detecting that its generating evidence has changed.

**On stage:** "The trust ID is sticky by design. It does not yield to new per-feature evidence automatically — that is the whole point. If new evidence contradicts the override, that contradiction surfaces as a review item, not as an automatic reversal."

**Paco to confirm:** Whether Senzing's trust-ID mechanism (or equivalent strong-identifier override) is persistent across new record ingestion, or whether it needs to be re-asserted.

---

### A4.5 — Entity ID churn as a permanent coordination problem
**Question:** At what rate of entity ID transitions does downstream coordination become unmanageable?

**[FULL — honest engineering answer]**

Yes, it is a permanent coordination requirement. And the honest framing: this is a property of the *problem*, not of this architecture. Any system that does continuous ER will produce entity ID transitions. The question is whether the consumers know about it and are designed for it.

**Practical ceiling:** It depends on the churn rate:

- **Low churn (< 0.1% of entities affected per day):** Downstream consumers can handle this with a daily sync of the transition table. Manageable.
- **Medium churn (0.1–1% per day):** Near-real-time change notifications are needed. CDC-style consumer subscriptions to entity lifecycle events.
- **High churn (> 1% per day):** The downstream consumers need to treat entity IDs as volatile — never caching an entity ID without also caching its expiry. At this point, the design pattern shifts: consumers do not store `entity_id` as a foreign key; they store `record_id` and resolve to `entity_id` at query time via the graph API.

**The better design for consumer systems:** Store the `record_id` (which is stable — it is the source system's ID) and resolve to entity at query time. Entity IDs are a Senzing runtime artefact; source record IDs are durable. If downstream systems anchor on source record IDs and resolve entities at query time through the graph API, the entity ID churn problem disappears for them.

**On stage:** "If you are designing a downstream consumer today: anchor on source record IDs, not entity IDs. The entity is the query result, not the primary key. Design that way from the start."

---

### A4.6 — When should trust-ID overrides become Senzing config changes?
**Question:** Should repeated trust-ID corrections inform Senzing configuration tuning?

**[FULL — this is addressed in TODOS.md and deserves a direct answer]**

This is exactly right and it is a real feedback loop that should be explicit in the architecture. The trust-ID log is, among other things, a **Senzing configuration audit trail**: "the engine made a decision here; the decision layer corrected it."

If the same type of correction happens repeatedly — say, Senzing consistently fails to resolve records with a specific Arabic name transliteration pattern, and the decision layer always force-merges them — that is a signal that:

1. Senzing's name-matching weight for that specific feature combination is under-tuned.
2. Or there is a systematic data quality issue upstream (the names are arriving in a form Senzing's Arabic handling doesn't cover).

**The feedback loop should be explicit:** A Phase 4 observability dashboard surfaces "most-frequent trust-ID override types". When a pattern exceeds a threshold (e.g., the same override type fires more than N times per week), it triggers a Senzing configuration review — ideally jointly with Paco/Senzing team.

The goal: trust IDs handle exceptional cases; the engine handles the majority. If trust IDs are handling 10% of resolutions, that is a configuration problem, not a decision layer success story.

**On stage:** "The decision layer is not a workaround for a misconfigured engine. If you find yourself writing trust IDs at scale for the same pattern, you are looking at a Senzing configuration item, not a Phase 5 success."

**See TODOS.md §11:** This was explicitly noted as an open question that was removed from the section because confidence was not sufficient. This answer justifies restoring it.

---

### A4.7 — Hume dependency vs. build-your-own consumer
**Question:** Is Hume the only supported path for entity-aware navigation?

**[FULL — direct and honest]**

No, but with nuance.

**The graph is the product.** The architecture is built on Neo4j with a documented schema (Record, EntityGroup, Source, RESOLVED_TO edges with WHY payloads). Any Neo4j client — official drivers in Python, Java, JavaScript, Go — can query this directly. The pattern for entity-aware navigation is standard Cypher (see A2.12).

**What Hume adds:**
- A pre-built RBAC layer that enforces source-level access control in the UI and API, without requiring the consuming application to implement it.
- The Advanced Expand as a first-class UI interaction (one click vs. writing Cypher).
- Pipeline orchestration (the CDC/trigger → Senzing → EntityGroup write pipeline) as a managed, observable component.
- The OverrideDecision workflow for trust-ID human review.

**What you need to build yourself if you go direct-to-graph:**
- Source-level RBAC in your API layer.
- WHY payload surfacing in your UI — Cypher gives you the data; you render it.
- Entity lifecycle event subscriptions for downstream consumers.

**Bottom line:** The architecture is not Hume-exclusive. If you have a strong existing data platform and want to build on top of the graph schema directly, that is a supported pattern. Hume reduces the engineering cost of the operational and consumer layers, not the architecture itself.

**On stage:** "Hume is one expression of this architecture. The architecture is the product. If you want to build against the graph directly, the schema and query patterns are transferable — we are happy to share them."

---

### A4.8 — The four properties: who audits them?
**Question:** In a production system, who verifies the four properties are actually holding?

**[FULL — the hardest and most honest answer in the workshop]**

This is the right question to close on. The four properties are architectural goals, not automatic outcomes. They require active stewardship.

**Who monitors each:**

- **Near real-time:** SLA on the lag between record arrival and affected-entities application to the graph. Measured by a monitoring query: `max(now() - record.ingested_at)` for records without a RESOLVED_TO edge. This is a standard ops alert.

- **Idempotent:** Validated in CI/CD against a test dataset. Replay the same batch twice, diff the graph. Zero diff = idempotent. If the diff is non-zero, you have a bug in the ingest path (a timestamp leaked into a feature, a sequence number crept in). Run this test on every config change and every Senzing version upgrade.

- **Observable:** The observability dashboards exist (Phase 4). But someone has to look at them on a schedule. The answer: a weekly operations review with the redo-rate dashboard as a standing agenda item. Anomaly detection on redo rate and entity stability metrics, alerting the on-call engineer when a threshold is crossed.

- **Explainable:** This one is audited on demand (regulator asks for a merge justification → query answers it) and periodically by spot-checking. Pick 10 random EntityGroups per month. Can you explain every RESOLVED_TO edge? If not, something has slipped.

**The harder point:** Observability tooling exists does not mean the system is observed. The four properties require:
1. A named owner per property.
2. An agreed cadence for review.
3. An escalation path when a property degrades.

That is not engineering — it is operations design. And it is the part most teams skip.

**On stage, to close:** "The four properties are your deployment contract. Who in your organisation owns each one? If you cannot answer that, the architecture we described today will degrade quietly. The tools are here; the process is yours to build."

---
