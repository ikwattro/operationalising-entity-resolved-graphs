# Images Index

Placeholders and missing images in `slides.md`. Every entry below needs a real asset before the deck is presentation-ready. See `SLIDES-TODO.md` for details on each item.

| Slide heading | Placeholder seed | What the real image should show |
|---|---|---|
| "GraphAware + Senzing: two halves" | `ga-senzing-partnership` | Partnership visual — logos side by side or complementary graph↔resolution diagram |
| Phase 1 · "Exploded, not yet resolved" | `phase1-exploded` | Graph subgraph: two Record nodes sharing a Passport node and a DOB node; no EntityGroup present |
| Phase 2 · "Source → Record → EntityGroup" | `entitygroup-subgraph` | Graph schema: Source ←FROM← Records →RESOLVED_TO→ EntityGroup, with edge properties shown |
| Phase 6 · "Hume 3.0 — Advanced Expand demo" | `hume3-smart-er` | Real Hume 3.0 screenshot of Smart ER Advanced Expand from a Person node |

## Architecture "We are here" variants (no placeholder — uses full PNG)

These slides currently show the unmodified `04_master_architecture.png`. Highlighted variants are needed — see `SLIDES-TODO.md` §1 for the full list and suggested file names.

| Slide heading | Region to highlight |
|---|---|
| Phase 1 — Data In | `SRC → DQ → GIN` |
| Phase 2 — Senzing Fundamentals | `GIN → SZ` |
| Phase 2 — Graph→Senzing pipeline | `GIN → SZ → GOUT` |
| OOTB Senzing | inside `SZ` |
| Phase 3 — Living Architecture | `GOUT` (over time) |
| Phase 4 — Explainability | `GOUT → AUDIT` |
| Phase 5 — Trust IDs | `HEUR ⇢ GIN` dotted edge |
| Phase 6 — Consumption | `GOUT → CONS` |
