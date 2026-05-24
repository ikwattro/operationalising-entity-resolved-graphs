# Running Order — 2-Hour Slot (Take 2)

## Why this file exists

The new outline organises the workshop around **six phases**, with a pre-phase that sets up the components and the map. This file is the running order Christophe and Paco can walk into the room with — minutes per section, transition cues, and where the audience pause goes.

It is not a script. It is a budget.

## The budget

| #   | Section                                                       | Minutes | Cumulative |
| --- | ------------------------------------------------------------- | ------- | ---------- |
| 0   | Opening — welcome, what-this-is-not                           | 3       | 3          |
| 01  | Intro — Who we are, why ER                                    | 5       | 8          |
| 02  | Operationalising — what does it mean?                         | 6       | 14         |
| 03  | The Best ER Is the One You Don't Need                         | 11      | 25         |
| 04  | The Operational Architecture — the map                        | 7       | 32         |
| 05  | Phase 1 — Data In, Exploded, Disconnected                     | 6       | 38         |
| 06  | Phase 2 — Senzing Fundamentals (Paco's deep dive)             | 14      | 52         |
| 07  | Phase 2 — From Graph Records to Senzing                       | 11      | 63         |
| 08  | The Depth of the Engine — What You'd Never Build Yourself     | 6       | 69         |
| —   | **Audience pause** — 3 questions from the floor              | 5       | 74         |
| 09  | Phase 3 — A Living Architecture (growth, merge, split)        | 10      | 84         |
| 10  | Phase 4 — Explainability, Observability, Audit History        | 9       | 93         |
| 11  | Phase 5 — The Graph Decision Layer and Trust IDs              | 13      | 106        |
| 12  | Phase 6 — Consumption and Hume 3.0 Smart ER                   | 7       | 113        |
| —   | **Close + final Q&A from the floor**                          | 7       | 120        |

Total: 120 minutes. ~7 minutes of buffer in the close — that buffer is for the inevitable overrun, not a planned monologue. If we get to minute 113 with the room still engaged, take live questions.

## Speaker swap

Two voices works better than one alternation per section. Suggested split:

- **Christophe** owns the GraphAware / graph-side sections (00, 01, 02, 03, 04, 05, 07, 09, 10, 11, 12) and closes.
- **Paco** owns the Senzing-fundamentals deep dive (06) and the OOTB-Senzing section (08). These are his to lead because the audience will trust the engine description more from him.
- Paco co-anchors the audience pause — questions in this room often go to him.

This is a starting suggestion; Christophe and Paco to confirm.

## The mid-workshop audience pause (slot at minute 69)

A 2-hour workshop without a break is a trust-burner. The 5-minute pause is a deliberate Q&A bridge between the *Senzing-core* half (Phases 1 + 2 + OOTB) and the *operations and decision* half (Phases 3 + 4 + 5 + 6).

- Up to 3 questions from the floor, strict.
- We answer briefly; if a question opens a longer conversation, we park it for the end and continue.
- If no questions come, surface our own: "by show of hands — who is currently running ER in production?" or "who has a graph already?" — calibrates the room before we start Phase 3.

Placement after Section 08 (OOTB) is intentional: by then the audience has seen the loop, the Senzing internals at the appropriate depth, and what the engine does for them out of the box. The pause cements the *what Senzing is* picture before we start layering operations and overrides on top.

## Transitions worth rehearsing

The transitions matter more than the slide bullets. Land each handoff cleanly and the workshop feels one-piece, not fourteen-piece.

- **01 → 02.** "We came here to talk about ER. What we actually want to talk about is *operationalising* it — and the gap between those two words is the next six minutes."
- **02 → 03.** "Operationalising means doing the unglamorous work first. The first piece of unglamorous work is the data we feed the engine."
- **03 → 04.** "We have aligned the data. Before we look at any one component, we need the map — the picture of where each component sits and how they exchange information." — sets up the "we are here" navigation device used through the rest of the workshop.
- **04 → 05.** "We are here." Point at Phase 1 on the map.
- **05 → 06.** "The graph holds the records. The engine resolves them. Time for Paco to tell us what the engine actually does."
- **06 → 07.** "Now we know what Senzing does. Next: how the records actually get from the graph into Senzing, and what comes back."
- **07 → 08.** "Before we leave Phase 2 — there are things Senzing handles for us out of the box that we should not duplicate upstream. Geocoding and globalisation are the two big ones."
- **08 → pause.** "That is what's inside the engine. The next half of the workshop is what we build around it. Three questions before we go on."
- **pause → 09.** Use a clean question as the bridge — "we said Senzing is idempotent. Phase 3 is what that buys us when the data starts moving."
- **09 → 10.** "Living architecture is the engine of change. Phase 4 is how we make that change explainable and observable."
- **10 → 11.** "Phase 4 was about *seeing* what the engine did. Phase 5 is about telling the engine what *we* see that it cannot." — frames the decision layer as the symmetric override.
- **11 → 12.** "Resolution is a means. Phase 6 is what the people we built this for actually do with it."
- **12 → close.** "We have been around the loop. The remainder is your questions."

## The "we are here" map

Section 04 introduces the components and the full architecture as a single diagram. Every subsequent section starts with a "we are here" highlight on that diagram — Phase 1 highlights data-in, Phase 2 highlights the engine and the bridge, Phase 3 highlights the feedback edge, and so on.

This is the single most important pacing device of the new outline. It is how a 120-minute workshop covering six phases stays navigable. The downstream slide repo will need to render the master diagram once and produce a "we are here" variant for each phase.

## What we do not have time for

Good content, explicitly out of the 120-minute budget. Appendix material or follow-up:

- A live coding demo of normalisation (Section 03) — described, not demoed.
- A full field-by-field walk-through of the Senzing input JSON (Section 07).
- A comparison of community-detection algorithms (Section 11).
- An end-to-end live demo of trust-ID-driven force-merge (Section 11) — described with a CSV example instead.
- Long-form Hume 3.0 demo (Section 12) — keep under 90 seconds or use screenshots.

If asked from the floor: "happy to go deeper after — let's stay on the loop for now."

## Open questions

Moved to [`../TODOS.md`](../TODOS.md).
