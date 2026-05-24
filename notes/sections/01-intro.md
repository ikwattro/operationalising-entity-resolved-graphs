# Intro — Who We Are, Why ER

## Narrative

This is a joint workshop. **GraphAware** builds graph-powered investigation software — Hume — and works with customers to operationalise large connected-data systems. **Senzing** builds the entity resolution engine the financial-crime and trust-and-safety worlds reach for first. We are not competitors; we are two halves of the same picture, and the next two hours are about how those halves fit together in production.

Christophe is GraphAware's CTO. Paco is from Senzing. We have, between us, spent enough years operationalising entity-resolved graphs to know what breaks, what scales, and what the audience in this room is probably about to bump into. We are going to tell you those things straight.

### Why ER, and why now

Entity Resolution is the act of deciding that the same real-world person, company, or asset is sitting behind multiple records in different systems. A criminal opens an account as "Mohammed Al-Rashid" in our KYC system, transfers money as "M. Rashid" through our wire system, and registers a shell company under a third spelling in our corporate registry feed. Three records, three systems, zero connections between them. That gap *is* the business model — fraud, AML evasion, sanctions evasion, modern-slavery networks, ad fraud, account-takeover rings — all of it lives in the space between disconnected datasets.

ER closes that gap. But one-shot ER — dedupe a CSV, eyeball the diff, ship — is a demo. **Operationalising** ER is a different problem, and that distinction is what the next two hours are about.

### What this workshop is not

To save us all time on expectation calibration:

- **Not a vendor pitch.** Neither GraphAware nor Senzing is selling from this stage. We will name our products when relevant and not otherwise.
- **Not a product walkthrough.** We run most of this live in Hume because that is where the patterns are most visible. The focus is the methodology.
- **Not a fix-everything-from-the-stage talk.** We will name failure modes openly.

What this workshop *is*, on the other hand, very much includes a proper walk through how Senzing works. Paco takes the audience through the engine's mechanics in Section 06 — feature extraction, scoring, the resolution decision, the configuration model. Senzing is a great ER engine and the people in this room deserve to leave understanding how it actually does its job, not just what it does for them.

The rest of the time, we are going to walk the loop end-to-end, in six phases, with a map you can navigate.

## Speaker notes

- Open cold with the three-records story. Do not start with "today we'll talk about…". Start with the criminal.
- Read "we are not competitors; we are two halves of the same picture" out loud — it sets the tone for Paco's deep dive in Section 06 and the joint-presentation feel of the whole hour.
- Christophe: introduce Paco with a real credential, not "from Senzing". Paco: same favour back.
- Hard time discipline: this is 5 minutes. The clock starts the second the room sits down.

## Assets

- _none — this section is intentionally spoken._

## Open questions

Moved to [`../TODOS.md`](../TODOS.md).
