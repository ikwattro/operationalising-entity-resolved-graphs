# Graph Heuristics — Force Apart and the Override Discipline

## Narrative

07a covered force-merge — the graph telling Senzing two entities should be one. This section covers the symmetric and more delicate case: force-apart, the graph telling Senzing one entity should be two. It then covers the surrounding discipline that makes either override safe: who runs the candidate generation, who is allowed to decide, what audit artifact the decision produces, and what the risks are.

### Force apart — when the graph says "these are different"

Senzing has resolved records into one entity. The graph shows the records sit in disjoint communities, share no neighbours, and one of them carries a strong identifier the others contradict. The instinct is to split, but the discipline is to slow down — false splits damage trust faster than false merges.

The mechanics:

1. Surface the candidate to a named human role — typically a **compliance investigator** or **KYC operations reviewer** depending on the customer's org chart — not directly to Senzing. Force-apart is closer to a human-in-the-loop decision than force-merge, and treating it as automation creates legal and reputational exposure.
2. The reviewer sees the evidence Senzing used to merge, the contradicting graph evidence, and produces a **justification artifact** (a case-file entry or its equivalent) recording who they are, what they decided, and why. The artifact lives in the same store as the resolution change — typically an `OverrideDecision` node linked to both the originating `EntityGroup` and the reviewer's identity — so the audit trail is queryable in the graph, not in a separate ticketing system.
3. The reviewer issues the force-apart. Senzing applies the split, emits the new entity IDs, the graph updates. The original entity remains in history, and the `OverrideDecision` stays attached to the lineage.

### A real-world force-apart shape

A single entity `Sergey Volkov` that Senzing resolved from three records: one KYC, two wires. The graph showed the wires records' counterparties sat in a different community from the KYC record's. A passport number on the new wires record contradicted the KYC record's passport. Force-apart surfaced to the reviewer, applied after review. Senzing emitted two distinct entities; the graph re-linked the new wires record to the freshly-created entity, with the `OverrideDecision` node carrying the reviewer's name and the contradicting passport as the justification.

### Overrides and access control

A question that comes up consistently: how does the override path interact with the source-level RBAC from Section 05b? If a force-merge candidate spans two sources, and the user proposing the override only has access to one of them, can they even see the candidate? If they can't, who initiates the override?

The answer in practice is a deliberate split of two roles:

- **Candidate generation runs under a `compliance` lens** — the same elevated lens used for audit. The graph heuristics layer that generates force-merge and force-apart candidates needs to see across sources to evaluate the signal honestly. Restricting it to one user's RBAC scope would silently bias the candidate set toward over-represented sources.
- **Candidate review respects standard RBAC**, with a clear escalation path. A reviewer who can see only one of the two sources sees the candidate redacted: "this `EntityGroup` may merge with another `EntityGroup` that you do not have access to". They cannot decide alone. The override is escalated to a reviewer who holds the union of the two scopes, typically a senior compliance investigator or a paired-review workflow with a second signatory.

The general posture: the *signal* runs across sources because that is where signal lives, but the *decision* respects the RBAC scope of the people accountable for it. We never quietly use compliance-lens data to drive an override that a single user could not legitimately see end-to-end.

### Why this loop is worth the complexity

It is tempting to ask: if the graph has this signal, why not let the graph be the source of truth? The answer is that Senzing brings things the graph cannot:

- A scoring engine tuned across many customers and many years.
- An idempotent, observable resolution layer that downstream consumers can trust.
- A consistent identity for entities across replays and rebuilds.

Replacing it with a graph algorithm would lose all of that. Augmenting it with one keeps it and adds context. The reinforcement loop is the place where domain context (graph structure, business rules, analyst judgment) re-enters a resolution pipeline that would otherwise only see features.

### The risks worth naming

- **Overconfidence in communities.** A community is a hypothesis. Driving force-merges off community membership alone, without high-specificity co-occurrence, will create false merges that are then painful to unwind. The threshold matters.
- **Feedback drift.** If the graph keeps telling Senzing to merge entities Senzing originally separated, and we never go back and tune Senzing's configuration, the system becomes dependent on the override. Periodically, the force-merge log is itself a signal for Senzing config tuning.
- **Audit complexity.** Every force-merge and force-apart needs a justification on the record. The `WHY` payload is not optional — it is what an investigator or regulator will ask for first.
- **Loops.** Force-merge changes the graph, which changes the signals, which could re-trigger an override. Idempotence helps — the same signal in the same shape produces the same instruction — but we still cap the cycle depth as a safety.

## Speaker notes

- Force-apart is the slide where regulators lean in. Cover the human-in-the-loop framing carefully and name the role.
- The "overrides and access control" subsection is the one a compliance officer in the audience will quote back. Slow down here.
- The risks list is short on purpose — read each one slowly, do not editorialise.

## Assets

- `assets/data/07_force_merge_example.csv` — shared with 07a; the force-apart row is the one referenced here.
- TODO: before/after subgraph visualisation for the force-apart shape — the downstream slide repo to render, ideally from the CSV.

## Open questions

- > [verify with Paco] The Senzing API surface for force-apart — exact endpoint, payload shape, how the override appears in subsequent `WHY` outputs.
- Whether to add an `OverrideDecision` node to the graph model in Section 05a to make the override audit trail explicit, or keep it as a per-section concept only mentioned here. Currently the model in 05a does not show this node — we are forward-referencing it implicitly.
- Which engagement is redactable enough to use as the force-apart story on stage. Christophe to source.
