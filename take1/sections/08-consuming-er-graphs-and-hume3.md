# Consuming ER Graphs — Downstream and Hume 3

## Narrative

Resolution is a means, not an end. Nobody opens a regulator's letter and replies "we have a beautifully resolved entity store" — they reply with names, networks, timelines, and the chain of evidence that supports them. The work in the rest of this workshop only pays off if the resolved graph is *usable* by the people who need to act on it.

### The four shapes of consumption

In practice we see four downstream consumption patterns, and a well-designed ER graph supports all of them:

- **Investigation workflows.** An analyst starts with a name, a phone number, or an alert, and walks the neighbourhood. They need to see the resolved entity, every record that contributed, every relationship at one and two hops, and the `WHY` behind each resolution. Speed matters — investigation work is interrupt-driven and analysts will not wait 30 seconds for a graph traversal.
- **Search and lookup.** Risk officers and call-centre staff want to type a name and see the unified entity, not a list of duplicate records. The graph's job is to power a search index that returns *entities*, not records — which means search has to be entity-aware, not just full-text.
- **Alerting and monitoring.** Watchlist hits, sanctions matches, transaction anomalies — these all want to fire on the *entity*, not the record. When a new record resolves into a watchlisted entity, the alert fires once, against the entity, with the record as evidence. When an entity changes membership (a force-merge, a force-apart), downstream consumers need to know.
- **Programmatic exploration.** Data scientists and ML teams want to project the graph for feature engineering, train models against resolved entities, run path queries for risk scoring. They need an API that exposes the graph as a graph, not flattened tables, and that respects the source-level security from Section 05.

Each pattern has different latency, freshness, and access requirements. The graph store has to serve all of them from one consistent state — which is why idempotence (Section 04) and observable updates (Section 06) are not optional: they are what makes consistent consumption possible.

### What "resolution-aware" actually means in a consumer

Two design principles separate a usable ER graph from a frustrating one:

- **Show the entity, not the records.** Every UI surface defaults to the entity view. Records are how the data arrived; the entity is what the human is reasoning about. Drilling into records is a deliberate action, not the default.
- **Show the `WHY` for every resolution.** No analyst should ever have to ask "why is this here?". Every edge, every membership, every alert carries the contributing evidence as a click-through. This is what Section 01 meant by *explainable*.

Get those two right and the rest of the consumer surface is engineering, not philosophy.

### Hume 3 — what we are revealing

GraphAware's investigation platform Hume has, in version 3, introduced new capabilities specifically aimed at ER-graph consumption. The detail of which features and how they work will be filled in by Christophe — this is the reveal moment in the workshop.

> [Christophe to fill] — the specific Hume 3 ER features to demo or discuss, in the order they should appear in the deck.

The framing we want: Hume 3 is not the point of the workshop. It is one expression of the principles we have been describing — entity-first surfaces, explainable resolution, source-aware visibility, observable updates. If the audience leaves understanding the principles, they can apply them whether or not they use Hume.

### What we deliberately do not do

Some patterns look attractive but cause more pain than they solve. Worth naming:

- **Materialising the resolved graph into a relational warehouse for downstream consumption.** Tempting because the BI team already has SQL. The problem is that the warehouse becomes stale within minutes of every Senzing affected-entities event, and the BI team will quietly build their own (incorrect, inconsistent) joins on top of the records to compensate. If consumers need entity-level joins, expose them through the graph or a graph-aware API, not by flattening upstream.
- **Letting consumer teams write directly against the resolved entity store.** Every team that does this becomes a small client of Senzing without knowing it, and every Senzing tuning change becomes a coordination problem. Mediate through an API layer that exposes entities at a stable contract.
- **Hiding the resolution mechanics behind a "smart match" layer.** Whenever we have wrapped resolution into something that feels magic to the consumer, an analyst has eventually asked why and we have had nothing to show them. Keep the mechanics visible.

The general posture: the graph is the source of truth, and the consumer surfaces are thin layers on top of it. Anything that copies the graph into a parallel store is a maintenance bet we lose.

## Speaker notes

- This section flips the perspective from operator to consumer. Pace down a notch; let the audience see why everything previous was worth the trouble.
- Hume 3 reveal is the closer-to-closer. Build into it with the principles, then hand to the demo (if we run one live) or the screenshots.
- The "what we deliberately do not do" subsection lands harder than it looks. Several teams in the audience will have already done the warehouse-materialisation thing. Be gentle but clear about why it does not scale.

## Assets

- TODO: Hume 3 screenshots, once Christophe has confirmed which features are in the reveal.
- TODO: a small "entity-first UI" mockup or screenshot — could be Hume, could be a sketch.

## Open questions

- > [Christophe to fill] Which exact Hume 3 ER features we are showcasing, and in what order. Confirm release timing against the Bridge meetup date.
- Do we want a 2-minute live demo here, or static screenshots? Live demo is higher impact but adds risk to the run-through.
- Do we mention any non-Hume consumer tooling we have integrated with (Linkurious, Neo4j Bloom, custom UIs)? Useful if there are non-Hume users in the room.
