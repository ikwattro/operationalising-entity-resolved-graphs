# Operationalising ER Graphs — Why Now

## Narrative

A criminal opens an account as "Mohammed Al-Rashid" in our KYC system, another as "M. Rashid" in our wire transfer system, and registers a shell company under a third spelling in our corporate registry feed. Three records, three systems, zero connections between them. That gap *is* the business model — fraud, AML, sanctions evasion all live in the space between disconnected datasets.

Entity Resolution closes that gap. But one-shot ER — dedupe a CSV, eyeball the diff, ship — is a demo. Operationalising ER is a different problem.

In production, records arrive continuously. Entities form, split, and merge as new evidence lands. Downstream systems need to know *which entities changed* and *why*. An analyst has to defend a merge decision in front of a regulator months after it happened.

That is what we mean by **operationalising**, and it comes down to four properties we will keep returning to throughout the workshop:

- **Near real-time** — a record arrives, affected entities come out seconds later, not overnight.
- **Idempotent** — replay the same events in any order and we land on the same graph.
- **Observable** — we can see redo storms, drift, and feature-level resolution behaviour as they happen.
- **Explainable** — for every merge and every split, we can point to the features that drove the decision.

The rest of the workshop is how we build a system with those properties. The shape is not the obvious one: data does not go straight into Senzing. It lands in the graph first, flows into Senzing for resolution, comes back into the graph as resolved entities — and then the graph itself feeds decisions back to Senzing, using graph features (communities, co-occurrence, network signals) to reinforce or challenge resolutions. That loop is what turns ER from a one-way pipeline into a system that gets sharper over time.

## Speaker notes

- Open cold with the three-records story. Do not start with "today we'll talk about..." — start with the criminal.
- The "demo vs production" distinction is the whole reason this workshop exists. Land it hard. Most ER content stops at the demo.
- Four properties = the spine of the workshop. Forward-reference them when they come up later (e.g. when we cover redo logic, point back to *observable*).
- Christophe's anecdote slot — a real disconnected-data-missed-risk moment if there's one shareable.
- Set the tone here: we will name things that break later (geocoding to India, Arabic↔English alignment). Audience should expect candour, not a pitch.

## Assets

- None yet. Possible later: a simple 3-records-3-systems visual for the opener.

## Open questions

- Is there a published, non-sensitive real-world example we can use for the opener instead of a constructed one?
- Do we want to name-check a specific regulator / regime (FinCEN, FCA, EU AMLA) or stay jurisdiction-neutral?
