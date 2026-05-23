# Lessons Learned — The Things We'd Tell Our Past Selves

## Narrative

Most of what we have shown today was learned the hard way. The pipeline we have now is the third or fourth iteration; each previous iteration broke in a specific way that taught us something. The honest closing of the workshop is the short list of things we would have done differently from day one if we had known.

### 1. Data quality discipline is not optional, and buying an ER product does not change that

Every team that hits ER trouble in production has the same story: the discovery phase looked good, the demo looked good, then production exposed the upstream mess. The work in Section 02 — alignment, normalisation, dedup hashes, dictionary enrichment — is what separates an ER deployment that converges from one that thrashes. The temptation is to short-cut it because the ER product "should handle that". It will handle the cases the product was built for. The remaining 20% is where the operational pain lives.

**What we do now:** the data quality assessment is the first deliverable in any engagement, before architecture, before integration. If the quality is not there, we know what we are going to spend the first six months fixing.

### 2. Idempotence is the boring property that makes everything else work

Replays, recoveries, rebuilds, source re-ingestion, downstream index regeneration — all of them depend on Senzing being idempotent and our upstream records being clock-independent. We have been bitten by every flavour of non-idempotent upstream: timestamps in features, monotonically increasing sequence numbers, "last-modified" fields creeping into the matching key. Each time, the symptom was the same — the graph diverged on replay — and the root cause was the same — a record whose payload was not a pure function of source-of-truth state.

**What we do now:** non-idempotent payloads are a CI failure, not a code review comment. We test that any record can be replayed in any order and yields the same affected-entities.

### 3. Observability has to live in the same store as the data

We tried, in an earlier engagement, to run resolution observability on a separate metrics stack. The dashboards were beautiful and answered the wrong questions. Operators could see *that* something had happened but not *which entities*, not *which records*, not *which feature*. Bridging back to the data was a manual investigation every time.

**What we do now:** every resolution change in the graph carries the timestamp, the triggering record, and the contributing features as edge properties. The dashboards are graph queries. There is no separate metrics store; there is the graph, with the right indexes.

### 4. Force-merge through Senzing, never mutate the graph directly

The first time an analyst said "this is obviously the same person, just merge them", we mutated the graph directly and moved on. Within a month, the graph and Senzing had diverged on dozens of entities, downstream consumers were getting inconsistent answers depending on which system they queried, and an audit asked "why did the graph merge these and Senzing not?" — a question we could not answer.

**What we do now:** all merges and splits go through Senzing, even when the trigger is a graph signal. Senzing remains the single source of truth for resolution. The graph never disagrees with Senzing quietly.

### 5. Country-anchor every address before geocoding

The Caribbean-street-to-India geocode in Section 03 was a real lesson. Geocoders return their highest-confidence guess, and that guess is biased by data volume. Without a country anchor, geocoding will pull Trinidadian addresses to India, Lebanese to India, Haitian to France. The downstream consequence is not subtle: addresses become a redo storm trigger because of false matches across continents.

**What we do now:** no address enters the geocoding pipeline without a country code, derived from the source system, the IBAN, the phone prefix, or another in-record signal. Addresses without a country anchor are flagged, not guessed.

### 6. Communities are hypotheses, not verdicts

Communities are seductive. They show the analyst a "ring" of related entities, and the temptation is to act on the ring. The ring may be a shared building, a postbox provider, a transaction hub that everyone in a city uses. We have been wrong about communities enough times to keep them in the *hypothesis* layer of the surface, never the decision layer.

**What we do now:** communities surface as candidates with an analyst review step. Force-merges driven by community membership require a second signal — high-specificity co-occurrence — before they reach Senzing.

### 7. Keep the native script and the provenance — you cannot recover what you throw away

Throwing away Arabic script, Chinese characters, Cyrillic, or even diacritics, because the downstream system "only wants ASCII", is a one-way door. Once gone, the signal cannot be reconstructed; transliteration is lossy. The same principle applies to provenance: the original source system, the timestamp of capture, the operator who entered the record. All of it eventually matters in an investigation, and the records you ingested last year are the ones you cannot improve retroactively.

**What we do now:** raw payloads are immutable and complete. Normalisation produces *additional* columns; it never replaces the original. Disk is cheap. Lost signal is permanent.

### The shape of the discipline

If we were giving a one-line summary: **operationalising ER is not a project, it is a discipline**. It is the discipline of treating data quality as ongoing, treating resolution as evidence-driven and revisable, treating decisions as needing justification, and treating the resolution engine as one component in a system that also has to be observable, explainable, and operable. None of this is exotic engineering. It is the application of the boring practices we already know to a domain that punishes the absence of them harshly.

Thank you for spending the time with us. We are glad to take questions, and we will be around for the rest of the day.

## Speaker notes

- This is the close. Slow down. Read the lessons one by one — they are short on purpose.
- Land the one-line summary as the last thing on screen. If the audience remembers nothing else, they should remember that operationalising ER is a discipline, not a product purchase.
- Keep the thanks brief; do not undermine the close with logistics. Logistics on a final slide, not in the spoken close.

## Assets

- _none — this section is intentionally text-only._

## Open questions

- Whether to attach a one-page "operator's checklist" derived from these lessons as a handout. Useful if the audience expects something to take away physically.
- Whether to credit specific engagements (anonymised) where each lesson originated. Christophe to judge — adds authenticity but may risk identification.
