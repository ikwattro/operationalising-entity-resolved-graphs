# Storing Resolved Entities — RBAC and Trade-Offs

## Narrative

The model in 05a is shaped by one constraint above all others: a user's access to data is scoped by source, and the graph has to respect that without leaking. This section is the *why* and the *consequences* of that shape.

### Why records stay separate — the RBAC constraint

The single most important property of this model is the one that does *not* exist on the diagram: **we never fuse records into the `EntityGroup`**. There is no consolidated name on the `EntityGroup`, no unified address list, no merged phone-number set. The `EntityGroup` carries the resolution identity (`entity_id`) and nothing more.

The reason is RBAC. In the world we live in, a user's access is scoped by source. A KYC-only analyst is entitled to see KYC records, not wires. If we fused records into the `EntityGroup`, the fused properties would contain attributes derived from sources the analyst is not entitled to see — a name spelling, an address, a phone number — and there is no clean way to redact that. Fusion mixes provenance; RBAC depends on provenance being preserved.

By keeping records separate and attached to their source, the RBAC filter applies cleanly at the record level. A KYC-only analyst traversing from a `:Person` they can see, through the `RESOLVED_TO` edge to an `EntityGroup`, then back out through `RESOLVED_TO` edges, sees only the records from sources they have access to. The `EntityGroup` may have other records attached for other sources — those are not visible. Crucially, the *existence* of the `EntityGroup` itself remains visible, which is correct: an analyst should know there is a resolution group, even if they cannot see all of it. What they cannot see is the content from sources outside their scope.

The downstream consequence: every query that returns a "view" of a person aggregates from the visible records at query time. The aggregation is RBAC-filtered automatically because it is record-driven. There is no second redaction step.

One question this model leaves open and Section 07b picks up: what happens when an *override* — a force-merge or force-apart proposal — spans sources a single user cannot see? Briefly: the signal that generates the candidate runs under a compliance lens that sees across sources, but the decision respects the reviewer's RBAC scope and escalates when the scope is insufficient. Full mechanics in Section 07b.

### What this means for "viewing an entity"

When an analyst opens an `EntityGroup`, they do not see a single canonical record. They see a list of records they are allowed to see, with each record's source, captured payload, and contribution to the resolution. The UI's job is to make this readable — to surface the strongest evidence, group records by source, and indicate when content is hidden because of RBAC ("3 records from 2 sources you do not have access to").

This is the right model for investigation. It preserves the audit trail (every record is its own node), it preserves provenance (every record links to its source), and it preserves the regulator's question ("what evidence drove this resolution?") — every record contributing to the `EntityGroup` is enumerable.

### The problems this model introduces

We do not pretend it is free of trade-offs. The honest list:

- **No cheap "give me everything we know about Ahmad Hassan" query.** A consumer cannot just read the `EntityGroup` node and get a consolidated record. The consumer has to traverse records, aggregate, and respect RBAC. We mitigate with an API layer that does this consistently and caches per-user views.
- **Identity drift in `EntityGroup`s.** Senzing can change its mind. A record that resolved to `EntityGroup` 1001 yesterday may resolve to a freshly-created `EntityGroup` 1042 today (a split), or `EntityGroup` 1001 may be absorbed into `EntityGroup` 0042 (a merge). The graph has to track those transitions without losing history. `EntityGroup` nodes are versioned and historical `RESOLVED_TO` edges remain queryable.
- **Cross-source RBAC paradoxes.** Different users see different shapes of the same `EntityGroup`. Reconciling "analyst X says the entity has two records, auditor Y says four" requires care. We mitigate with a `compliance` lens that sees everything, used only for audit.
- **Community noise on the co-occurrence graph.** Two `EntityGroup`s sharing an address may be flatmates, an office building, or a postbox shell company. Without filtering, communities will be dominated by trivial co-occurrences. We weight edges by signal strength (frequency, exclusivity, type) before running detection.

### Communities on the co-occurrence graph

Once the co-occurrence layer between `EntityGroup`s exists, community detection (Louvain, Leiden) surfaces clusters that pure resolution misses: networks of shell companies that share directors but never co-resolve, families of accounts that share addresses across jurisdictions, transaction rings that share counterparties. These are not resolutions — none of these `EntityGroup`s *are* each other — they are *related*, and the analyst's job is to decide what that means.

The value is in surfacing patterns; the danger is in believing them too quickly. Communities are a hypothesis layer, not a verdict.

## Speaker notes

- The "we never fuse" rule is the line we want them to remember. Land it deliberately. It is also the line regulators in the audience will care about most — linger.
- Some audience members will expect a consolidated entity profile node and will be uncomfortable with the records-stay-separate model. The justification is RBAC, not graph aesthetics. Lead with the constraint, not the design.
- Communities-as-hypothesis: set this up here so it pays off in Section 07a, where we corroborate community signal with high-specificity co-occurrence before any force-merge instruction goes to Senzing.

## Assets

- _none — this section reuses the diagram from 05a._

## Open questions

- > [verify with Paco] How Senzing communicates identity transitions (entity split, entity merge) — is it always via affected-entities, or are there explicit transition events with from/to `entity_id`s we can record on the `EntityGroup` lineage?
