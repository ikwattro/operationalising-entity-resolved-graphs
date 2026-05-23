# Phase 2 — Senzing Fundamentals (Paco's Deep Dive)

> **We are here:** `GIN → SZ`. Records are about to leave the graph and meet the engine. Before we send them, the engine itself — how Senzing actually does its job.

## Narrative

The next 14 minutes are Paco's. The room came to understand how a production ER engine works under the hood, and Paco is the right person to explain it. We are not abstracting; we are explaining. By the end of this section, the audience should know — concretely — how Senzing turns a stream of messy records into a stable, deterministic resolution.

### Why Senzing earns the depth

Before the mechanics, the context. Senzing is a production ER engine running in financial-crime, AML, sanctions screening, and trust-and-safety deployments at significant scale. It is configurable, deterministic given that configuration, idempotent, and has been hardened on real-world data variation for years. The reason we hand resolution to it — and the reason this workshop dedicates the longest single block to its mechanics — is that re-implementing what Senzing already does correctly would be one of the worst architectural bets in the room.

That is the framing for what follows. We are explaining a good engine, not apologising for one.

### What we need the audience to leave this section knowing

Four things, in order:

1. **What Senzing is and what it is for** — a production ER engine for resolving records to real-world entities, used in financial-crime and trust-and-safety at scale.
2. **How the engine actually decides** — the mechanics, end to end: feature extraction, candidate retrieval, feature scoring, and the resolution call. Not a survey; a walk.
3. **The three concepts they will hear for the rest of the workshop** — **record**, **entity**, **entity group** (the latter is our graph-side name; Senzing says *entity*).
4. **What a Senzing-only round-trip looks like** — input JSON in, affected-entities JSON out — without our graph wrapping it.

### Concepts — the three names that have to be stable

We have to nail the vocabulary now so the rest of the workshop reads clean:

- **Record.** A single piece of evidence from one source, identified by `(DATA_SOURCE, RECORD_ID)`. KYC-001 is a record. WIRE-A12 is a record. Records are immutable in our model; if the source updates, that is a new record (or a versioned record), not a mutation. Senzing also calls these records.
- **Entity.** Senzing's concept: the resolved identity. After Senzing processes a set of records, some of them resolve together — they refer to the same real-world person, company, or asset — and each cluster gets an `ENTITY_ID`. The entity is the join point, not the consolidated profile.
- **`EntityGroup`** (graph-side name). When we land Senzing's `ENTITY_ID` in our graph, we put it on a node labelled `EntityGroup`. The label is ours; the identity is Senzing's. We chose `EntityGroup` to avoid overloading the word "entity", which the workshop uses colloquially. **Whenever Paco says "entity", he means the same thing we mean by `EntityGroup`.** Flag this aloud on stage.

### What Paco covers, in order

The spine of the 14 minutes — concrete beats with substance, not a placeholder list. Paco brings the worked examples and the depth.

1. **What problem Senzing solves, in 60 seconds.** The "three records, same person, across systems" story from the intro, now answered: this is what the engine is for.
2. **How Senzing decides — the engine's mechanics, end to end.**
   - **Feature extraction.** Turning a record's raw strings into typed, comparable features — name parts, address components, identifier values, dates, phones. The engine does not match strings; it matches features.
   - **Candidate retrieval.** Finding the small set of existing records the new one *could* match, using indexed features. This is what makes resolution fast at scale — Senzing does not score the new record against every record in the store.
   - **Feature scoring.** Per-feature confidence: how strong is the name match, the address match, the identifier match, the DOB match. Different features carry different specificity and different scores.
   - **The resolution call.** Composing the per-feature scores into one of the outcomes the engine produces — a match into an existing entity, the creation of a new entity, a possible-match flag, or a possibly-related signal. The match level we see in the affected-entities response.
3. **The configuration model.** Data sources, entity types, feature definitions, scoring rules — the engine is configurable, and the configuration is what makes Senzing fit a domain. Financial-crime, trust-and-safety, and customer-data resolution share the same engine but ship with different configurations. Paco shows the shape; we do not need every knob.
4. **What "good data" looks like, from the engine's point of view.** Stable record IDs, explicit data sources, well-formed feature blocks (names, addresses, identifiers, dates, phones), explicit absence over invented placeholders. This is the bridge to Section 07's mapping discussion.
5. **Determinism and idempotence — the contract the rest of the workshop relies on.** Same engine version + same configuration + same records in any order = same resolution. Operationally, this is what makes replay safe in Phase 3.
6. **A live round-trip.** A single record going in (`assets/snippets/06_senzing_input_record.json`), the affected-entities event coming out (`assets/snippets/06_senzing_affected_entities.json`). The cleanest possible view of the engine in action.
7. **The runway.** Where the rest of the workshop uses Senzing: Section 07 — how the graph pushes records in; Phase 3 — behaviour under continuous updates; Phase 5 — the trust-ID mechanism. Paco hands to Christophe.

### Things we want Paco to address explicitly

Worked through during the deep dive:

- **The candidate-retrieval stage** — how Senzing scopes the work to a handful of candidate records rather than scoring against every record in the store. Important because it is what makes the engine fast at scale, and because it is the layer where indexing choices matter.
- **How per-feature scoring composes into the resolution decision** — the relationship between feature scores, match levels, and the final cluster call.
- **The `WHY` payload** — what it contains, how it is computed, how stable it is across engine versions. We attach it to graph edges in Section 07; the audience needs to know what they are attaching.
- **What features Senzing uses out of the box** — names (with cross-cultural handling), addresses (with parsing and geocoding), identifiers (passports, national IDs, tax IDs, registration numbers), phones, dates of birth. This sets up Section 08 (OOTB).
- **How Senzing handles strong identifiers like passports** — high specificity, high redo potential. We come back to this in Phase 3.
- **The force-merge / force-apart / trust-ID surface** — what the API actually exposes. We mention it here; we use it in Phase 5.

### The handoff

When Paco finishes, the audience should know what the engine is, how it decides, and have seen one trip through it. They should *not* yet know how the graph stays in sync with the engine as records arrive continuously — that is the next section. Paco's last line should set Christophe up: "and that is how the engine resolves. Christophe will show you how the graph pushes records into it."

## Speaker notes

- This is the longest single block in the workshop. 14 minutes is generous; do not pad — every minute is content.
- Paco's existing slides for engine internals (if any) are better than anything we would render from outside. We provide the time slot; Paco brings the substance.
- Stay descriptive, not comparative. We are explaining *how Senzing works*, not how it compares to anything else.
- The "configuration model" beat is the easiest one to lose to time pressure. Hold onto it — it is the difference between "we use Senzing" and "we know how to deploy Senzing".

## Assets

- `assets/snippets/06_senzing_input_record.json` — minimal, realistic Senzing input record for a person.
- `assets/snippets/06_senzing_affected_entities.json` — minimal affected-entities response.

## Open questions

Moved to [`../TODOS.md`](../TODOS.md).
