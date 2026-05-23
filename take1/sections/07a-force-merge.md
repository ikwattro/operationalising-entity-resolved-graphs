# Graph Heuristics — Force Merge

## Narrative

Senzing makes resolution decisions from the features in each record. The graph sees something Senzing does not: the *neighbourhood* of those records. Two `EntityGroup`s that share four addresses, two phone numbers, and nine counterparties are almost certainly the same person, even if Senzing's per-feature scoring kept them apart. (We use "entity" and `EntityGroup` interchangeably below — see Section 05a for the naming.)

This is the reinforcement edge in the architecture — the dotted arrow from graph heuristics back to Senzing in Section 04a's diagram. It is what closes the loop, and it is where GraphAware + Senzing is more than the sum of the parts. This section covers the *force-merge* half of the override path; force-apart is in 07b.

### The two graph signals we lean on

- **Co-occurrence weight.** For any two entities, the count of shared neighbours by type — same addresses, same phones, same counterparties in shared transactions, same beneficial-ownership chains. Weighted by the specificity of each shared feature (a shared rare passport number is worth more than a shared common address). This is the *load-bearing* signal.
- **Community membership.** Entities in the same detected community are structurally close; entities in different communities are structurally distant. We treat community membership as a **prior**, never as a decision input on its own — its job is to raise or lower the threshold the co-occurrence signal has to clear, not to drive a decision. A pair of entities in the same community needs less co-occurrence to be merge-worthy than a pair in different communities, but no community signal alone ever produces an override.

Neither signal alone is decisive. Co-occurrence carries the decision; community shapes the threshold. Together, with provenance for every contributing edge, they form the basis of an override.

### Force merge — when the graph says "these are the same"

When two entities sit at `POSSIBLY_RELATED` in Senzing's output but the graph shows dense, high-specificity co-occurrence, and that co-occurrence sits within a shared community (the prior), we have a candidate for **force merge**. The mechanics:

1. The graph heuristics layer computes the signal — co-occurrence weight above the threshold for the relevant community-prior, no contradicting features.
2. We do *not* mutate the graph directly. We send a force-merge instruction back to Senzing, naming the two entities and the evidence.
3. Senzing applies the merge, emits affected-entities, the graph updates as it would for any other resolution change — with the difference that the `WHY` on the resolution edge records the graph signal as the cause, not just the per-feature scores.

The reason we route through Senzing rather than overlaying the merge in the graph: it keeps the resolution authoritative in one place. The graph never quietly disagrees with Senzing. Either Senzing has merged the entities, or it has not. If it has not, we have either accepted that or asked it to change its mind.

### A real-world force-merge shape

Two `Ahmad Hassan` entities, both at `POSSIBLY_RELATED` in Senzing because the name and DOB matched but the addresses and identifiers diverged across sources. The graph showed four shared addresses (one a residential building, three a sequence of business addresses across years), two shared phone numbers, and nine shared counterparties — including two unusual ones that appear in fewer than 100 entities across the entire graph. Same community. Force-merge issued, accepted by Senzing, affected-entities propagated.

The principle: this is not the graph quietly disagreeing with the engine. It is the graph telling the engine what the engine cannot see, in a form the engine can act on. The pipeline goes back through the same process — push, resolve, affected entities, graph update — with the override expressed as additional input rather than a parallel decision.

`assets/data/07_force_merge_example.csv` shows the candidate-row shape used by the heuristics layer; the same CSV also carries the force-apart row used in 07b.

## Speaker notes

- This is the section that earns the workshop's title. *Operationalising* ER means closing this loop. Without it, we have a pipeline; with it, we have a system.
- The Ahmad Hassan shape is a placeholder for a story Christophe can fill in with a real (anonymised) engagement example. The structure of the story is what matters: situation Senzing saw, signal the graph added, override, outcome.
- Stress the "do not mutate the graph directly" rule. It is counter-intuitive — engineers often want to "fix" the graph in place — and it is the most common architectural mistake we see.

## Assets

- `assets/data/07_force_merge_example.csv` — four entities illustrating force-merge (dense overlap) and force-apart (disjoint communities) candidate flows. Force-merge rows used here; force-apart row used in 07b.
- TODO: before/after subgraph visualisation for the force-merge shape — the downstream slide repo to render, ideally from the CSV.

## Open questions

- > [verify with Paco] The Senzing API surface for force-merge — exact endpoint, payload shape, how the override appears in subsequent `WHY` outputs.
- > [verify with Paco] Whether Senzing has any built-in graph-feedback hook we should use rather than building our own.
- Thresholds: what co-occurrence weight and community-agreement values should we cite as defaults? We can either say "calibrate per deployment" (honest) or give a starting point (more actionable). Christophe to decide.
- Which engagement is redactable enough to use as the force-merge story on stage. Christophe to source.
