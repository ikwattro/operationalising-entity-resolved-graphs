# Running Order — 2-Hour Slot

## Why this file exists

The 2-hour slot is tight. The drafted sections add up to slightly more than fits, so timing has to be planned, not improvised. This file is the running order Christophe and Paco can walk into the room with — minutes per section, transition cues, and where the audience pause goes.

It is not a script. It is a budget.

## The budget

| #   | Section                                                       | Minutes | Cumulative |
| --- | ------------------------------------------------------------- | ------- | ---------- |
| 0   | Opening — welcome, who-we-are, what-this-is-not               | 4       | 4          |
| 01  | Operationalising ER Graphs — Why Now                          | 7       | 11         |
| 02  | The Best ER Is the One You Don't Need                         | 13      | 24         |
| 03  | Globalisation and Geocoding                                   | 11      | 35         |
| 04a | Architecture — The Loop, End to End                           | 9       | 44         |
| 04b | Architecture — The Senzing Contract                           | 8       | 52         |
| —   | **Audience pause** — 3 questions from the floor, no slides    | 6       | 58         |
| 05a | Storing Resolved Entities — The Graph Model                   | 8       | 66         |
| 05b | Storing Resolved Entities — RBAC and Trade-Offs               | 8       | 74         |
| 06  | Living with Updates — Redo Logic and Observability            | 13      | 87         |
| 07a | Graph Heuristics — Force Merge                                | 8       | 95         |
| 07b | Graph Heuristics — Force Apart and the Override Discipline    | 6       | 101        |
| 08  | Consuming ER Graphs — Downstream and Hume 3                   | 10      | 111        |
| 09  | Lessons Learned                                               | 6       | 117        |
| —   | **Close + Q&A from the floor**                                | 3       | 120        |

Total: 120 minutes. No slack. Anything that overruns has to be pulled from a later section live; the obvious candidates are the second example in Section 03 and the "what we deliberately do not do" subsection in Section 08 — both can be cut to one beat each if we are behind at the halfway mark.

## The mid-workshop audience pause (slot at minute 52)

A 2-hour workshop without a break is a trust-burner. The 6-minute pause at minute 52 is **not a coffee break** — it is a deliberate Q&A bridge between the architecture half and the operations half:

- Up to 3 questions from the floor, strict.
- We answer briefly; if a question opens a longer conversation, we park it for the end and continue.
- If no questions come, we use the slot to surface our own: "by show of hands — who is currently running ER in production?" or similar. Either way the room re-engages before Section 05a.

The reason for placing it after Section 04b and not later: 04a + 04b together are the densest single block. The audience has just absorbed the loop diagram, the input shape, and the contract Senzing offers us. A pause here cements the spine of the workshop before we move into the storage, redo, and override mechanics that depend on it.

## Transitions worth rehearsing

The transitions between sections matter more than the slide bullets. Land each handoff cleanly and the workshop feels one-piece rather than thirteen-piece.

- **01 → 02.** "We said the first property is *near real-time*. None of the four properties are reachable if the data we feed Senzing is dirty." — sets up that data quality is the precondition.
- **02 → 03.** "The rules we just walked through are the easy 80%. The remaining 20% is where the cross-cultural and geocoding edge cases live." — explicit handoff.
- **03 → 04a.** "We have aligned the data and we have not lied to ourselves about the edge cases. Now we look at how it flows." — moves from data to architecture.
- **04a → 04b.** "That is the shape of the loop. The right-hand side — what we send Senzing and what we get back — is the contract we depend on. Let us look at it." — moves from picture to interface.
- **04b → pause.** "That is the contract. The next half of the workshop is about living inside it. Before we go on, three questions from the floor."
- **pause → 05a.** Pick one specific question that ended cleanly and use it as the bridge — "we said earlier the graph never disagrees with Senzing quietly. The next two sections are how we store the agreement and how we keep it RBAC-honest."
- **05a → 05b.** No transition — these are two halves of the same idea. Take questions only after 05b.
- **05b → 06.** "We have a graph that stores resolutions and respects access control. Now we make it survive new evidence." — the model is static; the next section makes it move.
- **06 → 07a.** "Redo is the engine of change driven by the records. The graph itself is the *other* engine of change, and that is what we look at next." — frames force-merge as the symmetric override.
- **07a → 07b.** "Force-merge is the easier direction. The reverse — telling Senzing to split an entity it resolved — is more delicate, and the surrounding discipline of who decides and how is the rest of this section." — earned handoff into the human-in-the-loop subsection.
- **07b → 08.** "Resolution is a means, not an end." — Section 08's own opening line, lift it as the transition.
- **08 → 09.** "Everything we have shown today, we learned the hard way." — set up the lessons as earned, not abstract.

## Speaker swap notes

Co-presenting with two voices works better than alternating per section — the audience loses track. Suggested split:

- **Christophe** opens (00, 01), owns the GraphAware-flavoured sections (05a, 05b, 07a, 07b, 08, 09), and closes.
- **Paco** owns the data-engineering and Senzing-facing sections (02, 03, 04a, 04b, 06).
- The pause at minute 52 is whoever the room engaged with more — read it live.

Final speaker arrangement is for Christophe and Paco to confirm; this is a starting suggestion, not a prescription.

## What we do not have time for

The following are good content but explicitly out of the 120-minute budget. They become appendix material for the deck, or follow-up reading:

- A live coding demo of the normalisation step from Section 02 (estimated 4-6 min, too expensive).
- A walk-through of the Senzing input JSON field by field (Section 04b — we show the shape, not the schema).
- A detailed comparison of community-detection algorithms in Sections 05b / 07a (we cite Louvain/Leiden by name and move on).
- Full Hume 3 demo, if there is one — keep it under 90 seconds or use screenshots.

If asked about any of these from the floor, the answer is "happy to go deeper after — let's stay on the loop for now."

## Open questions

- Whether Christophe wants a 5-minute hard break (water, stretch) instead of the 6-minute Q-bridge. Trade-off: a hard break re-engages bodies but loses momentum; the Q-bridge keeps momentum but tires people who needed to stand up.
- Whether the audience pause should be at minute 52 (after 04b) or minute 74 (after 05b). Currently choosing the earlier one because the architecture pair is the heaviest single block; revisit after dry-run.
- Confirm slot length with the Bridge organisers — we are designing for 120 minutes door-to-door including any intro from the host. If the host eats 5 minutes, Section 08 contracts first.
