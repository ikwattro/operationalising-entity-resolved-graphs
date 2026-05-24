# Operationalising — What Does It Mean?

## Narrative

We chose the word *operationalising* in the title on purpose. The word does the heavy lifting; this section unpacks it.

In a demo, ER decides once. We dedupe a CSV, eyeball the diff, ship. Done. In production, ER decides continuously, and its decisions change as new evidence arrives. A record that landed last week may belong to a different entity today because a record from a different source corroborated or contradicted it. The graph has to stay consistent. Analysts have to be able to explain a merge they made six months ago to a regulator looking at it for the first time today. Downstream systems have to know which entities changed without re-reading everything. None of those things are demos.

Operationalising ER comes down to four properties. We will keep returning to them throughout the workshop:

- **Near real-time.** A record arrives, affected entities come out seconds later, not overnight. The system runs in the same time-base as the business.
- **Idempotent.** Replay the same events in any order and we land on the same graph. Recovery, re-ingestion, and rebuilds are safe operations, not risky ones.
- **Observable.** We can see redo cascades, drift, and feature-level resolution behaviour as they happen. The system tells us what it is doing, not just the result.
- **Explainable.** For every merge and every split, we can point to the features and the graph evidence that drove the decision. Audit is one query away, not a forensic project.

Everything else in the workshop — the phases, the architecture, the trust-ID mechanic in Phase 5 — is in service of those four properties. If the audience leaves remembering nothing else, they should remember the four.

### What operationalising is *not*

Worth ruling out, because the word is heavy and people pour their own meanings into it:

- It is not "running ER in production" in the trivial sense of "we have a server up". A cron job that re-resolves a table every night is in production and is not operationalised.
- It is not "ER with monitoring bolted on". Observability has to be a property of the model, not a layer on the side.
- It is not "the resolved entities are in the database, so the work is done". The hard part starts when the entities have to keep being correct as the world moves.

### How the next two hours map to the four properties

- *Near real-time* is delivered by the architecture in Section 04 and the affected-entities flow in Section 07.
- *Idempotent* is the contract Senzing offers (Section 06) and the discipline we keep upstream (Section 09, Phase 3).
- *Observable* is what Phase 4 (Section 10) is about, end to end.
- *Explainable* threads through everything but lands hardest in Phase 5 (Section 11) where the decision layer has to justify its overrides.

That is the map. We will hold up the architecture diagram next and show the components those properties live in.

## Speaker notes

- The four properties are the spine of the workshop. Say them once here clearly, then forward-reference them at every phase. Audience members who lose the thread can always re-anchor on the four.
- Do not rank the four. They are not "what's most important". They are properties the system must have, and all four have to hold.
- This is the section that makes "operationalising" stop being a word in a title and start being a checklist. Read the four with a beat in between.
- Avoid the word "robust" — it's a vendor-pitch tell. Say what we mean: idempotent, observable, explainable, near real-time.

## Assets

- _none — this section is the four properties stated cleanly. The slide repo will likely render them as a single anchor visual._

## Open questions

Moved to [`../TODOS.md`](../TODOS.md).
