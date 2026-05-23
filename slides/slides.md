---
marp: true
theme: graphaware
paginate: true
header: '![logo](theme/1@4x-graphaware-logo.png)'
---

<!-- _class: cover -->
<!-- _paginate: false -->

# Operationalising Entity Resolved Graphs
## From raw records to production-grade knowledge graphs

**Paco Nathan · Christophe Willemsen**

---

<!-- _class: cover -->
<!-- _paginate: false -->

# In this presentation...

- Data quality as the foundation of ER
- End-to-end architecture: graphs → Senzing → graphs
- Graph data model for resolved entities
- Advanced resolution patterns with graph heuristics
- Operating ER at scale: updates, redo, real-time
- Consuming ER graphs & lessons learned

---

<!-- _class: cover -->
<!-- _paginate: false -->

# Data Quality for Entity Resolution

---

## What Makes Good Data for ER

- Cleaning and alignment are prerequisites — ER amplifies input quality
- Consistent field semantics across sources (names, dates, IDs)
- High cardinality attributes drive resolution confidence
- Noise tolerance depends on attribute weight tuning

---

<!-- _class: img-right -->

## Globalisation Challenges

<div class="columns">
<div class="col-content">

- Same entity, different scripts: Arabic vs. English names
- Transliteration inconsistencies across sources
- Cultural naming conventions differ (family name order, honorifics)
- Merging across languages requires normalised canonical forms

</div>
<div class="col-img">

![Multilingual entity names example](https://picsum.photos/seed/globalisation/600/800)

</div>
</div>

---

## Geocoding & Calibration

- Street names from one region can falsely geocode to another country
- Validate geocoding results against expected geographic context
- Calibrate confidence thresholds — errors propagate into resolution
- Caribbean street → India match is a signal to distrust, not merge

---

<!-- _class: cover -->
<!-- _paginate: false -->

# Architecture: Graphs → Senzing → Graphs

---

<!-- _class: img-bottom -->

## End-to-End Flow

<div class="hero-wrap">

![Architecture diagram: source graph nodes → record extraction → Senzing → resolved entity output → graph write-back](https://picsum.photos/seed/er-architecture/1200/700)

</div>
<div class="img-caption">

Source records extracted from the graph, resolved by Senzing, written back as resolved entity nodes.

</div>

---

## Pushing Records to Senzing

- Extract node properties as flat records (Senzing input format)
- Push via Senzing SDK / REST API — each record carries a `DATA_SOURCE` tag
- Senzing processes asynchronously; output is a stream of affected entities
- Batch or streaming ingestion — both supported

---

## Resolution Output & Idempotence

- Output: set of **affected entity IDs** after each record push
- Senzing recalculates entity membership on every change
- **Idempotent**: push records in any order → same resolved entities
- Safe to replay; enables at-least-once delivery pipelines

---

<!-- _class: cover -->
<!-- _paginate: false -->

# Graph Data Model

---

<!-- _class: img-left -->

## Storing Resolved Entities

<div class="columns">
<div class="col-img">

![Graph schema showing source nodes linked to ResolvedEntity nodes via BELONGS_TO relationships](https://picsum.photos/seed/er-graph-model/600/800)

</div>
<div class="col-content">

- Transparent overlay — source nodes untouched
- `ResolvedEntity` node generated per Senzing entity
- Source records linked via `BELONGS_TO` relationship
- Resolution metadata stored as relationship properties

</div>
</div>

---

## Source-Level Security Constraints

- Source nodes carry origin labels (e.g., `FBI`, `INTERPOL`, `PUBLIC`)
- Resolved entity visibility filtered by caller's source access
- Graph queries enforce source-level ACLs at traversal time
- Partial views: a caller sees only the sources they're cleared for

---

## EntityGroup Concept

- `EntityGroup` aggregates `ResolvedEntity` nodes at a higher confidence tier
- Handles cases where multiple resolved entities likely refer to the same real-world entity
- Useful for cross-source disambiguation without forcing a hard merge

---

## Trade-offs of This Model

- Query complexity increases — traversal must hop through resolution layer
- Resolved entity count can diverge from source record count unexpectedly
- Security filtering at source level can produce inconsistent entity views per user
- Index and cache strategy must account for the overlay layer

---

<!-- _class: cover -->
<!-- _paginate: false -->

# Advanced Resolution Patterns

---

## Co-occurrence & Community Analysis

- Build co-occurrence graph: edges between entities that appear in shared records
- Run community detection (Louvain, Leiden) over co-occurrence graph
- Communities signal implicit relationships Senzing scoring may miss
- Feed community membership back as resolution hints

---

## Graph Heuristics as a Decision Layer

- Graph topology provides signals orthogonal to attribute similarity
- Degree centrality, shared neighbours, path distance between candidates
- Use heuristic scores to boost or suppress Senzing resolution confidence
- Creates a feedback loop: graph informs ER, ER updates graph

---

## FORCE MERGE & FORCE APART

- **FORCE MERGE**: override resolution — declare two entities identical
  - Triggered when graph evidence is conclusive but attributes are noisy
- **FORCE APART**: prevent resolution — declare two entities distinct
  - Triggered when attribute similarity is high but graph context rules it out
- Both feed back into Senzing as resolver hints and are stored in the graph

---

<!-- _class: cover -->
<!-- _paginate: false -->

# Operating ER at Scale

---

## Near Real-Time Updates

- Record changes trigger re-resolution for the affected entity cluster
- Senzing emits delta: entities gained/lost members since last state
- Graph write-back is scoped to the affected subgraph — not a full rebuild
- Observable near real-time: resolution lag typically sub-second to seconds

---

## Redo Logic

- Redo = Senzing re-evaluates an entity due to conflicting evidence
- Track **redo rate per feature** to identify noisy attributes
- High redo on a feature → candidate for weight reduction or exclusion
- Surfacing redo metrics in the graph enables continuous tuning

---

<!-- _class: cover -->
<!-- _paginate: false -->

# Real World Examples

---

## Example: Cross-Language Resolution

- Arabic-script name + English transliteration → merged into one entity
- Date-of-birth + partial ID cross-validated across three sources
- Graph path through shared associates confirmed the merge
- FORCE APART applied where name collision was coincidental (common surnames)

---

## Example: Address Calibration Failure → Recovery

- Caribbean address geocoded to Indian city — confidence penalised
- Graph context (co-located associates, shared phone prefix) outweighed geocode
- Redo triggered after geocode weight reduced; entities re-merged correctly
- Demonstrates feedback loop: graph heuristic → weight tuning → re-resolution

---

<!-- _class: cover -->
<!-- _paginate: false -->

# Consuming ER Graphs

---

## Querying Resolved Entities

- Traverse from source node → `BELONGS_TO` → `ResolvedEntity`
- Aggregate properties across all source members of an entity
- Filter by source ACL before surfacing results to callers
- Pattern: resolve first, then query the resolved subgraph

---

## Hume 3: New Capabilities

- Native ER overlay visualisation — resolved entities as first-class graph objects
- Source-level security filtering built into the query layer
- Community detection on co-occurrence graphs, surfaced as entity clusters
- Real-time resolution delta feed for live investigation views

---

<!-- _class: cover -->
<!-- _paginate: false -->

# Lessons Learned

---

## What We'd Do Differently

- Start with data quality profiling before tuning resolution weights
- Build geocoding validation early — bad geocodes compound downstream
- Design for idempotency from day one — replay capability is critical
- FORCE MERGE/APART should be auditable; store the rationale in the graph

---

## What Worked Well

- Transparent overlay preserves raw source data — no destructive merges
- Graph heuristics as a second opinion layer improved precision significantly
- Community analysis surfaced relationships invisible to attribute-only ER
- Source-level ACLs in the graph model made multi-tenant deployments clean

---

<!-- _class: cover -->
<!-- _paginate: false -->

# Thank you

**Paco Nathan · Christophe Willemsen**
