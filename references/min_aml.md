# min_aml — canonical example dataset

- **Upstream source**: https://github.com/DerwenAI/min_aml
- **What it is**: a minimal AML (anti-money-laundering) subset built from the OO/OS (OpenOwnership / OpenSanctions) data, curated by Derwen.ai.
- **Why we use it**: it is small, public, redactable, and exhibits the realistic ER pain points we want to showcase — multi-script name aliases, address parsing across countries, identifier variants, beneficial-ownership chains worth resolving.

## In-repo location (take2)

Paco supplied the **Senzing-formatted** version of the dataset, already shaped for direct push to the engine. It lives at:

- `take2/assets/data/min_aml/open-sanctions.json` — 24 sanctioned-entity records (PERSON and ORGANIZATION). The capabilities-demo dataset.
- `take2/assets/data/min_aml/open-ownership.json` — 316 UK beneficial-ownership records (PERSON and ORGANIZATION). Larger; carries the relationship graph for shareholding / directorships / voting rights.

Each line is one Senzing input record (JSON Lines). Fields include `DATA_SOURCE`, `RECORD_ID`, `RECORD_TYPE`, `NAMES` (with `NAME_TYPE`, `NAME_FULL`, `NAME_ORG`), `ADDRESSES` (with `ADDR_FULL` and optionally `ADDR_LINE1` / `ADDR_CITY` / `ADDR_COUNTRY` / `ADDR_POSTAL_CODE`), `IDENTIFIERS` (with `PASSPORT_NUMBER`, `NATIONAL_ID_NUMBER`, `TAX_ID_NUMBER`, `OTHER_ID_*`), `COUNTRIES`, `DATES`, `RELATIONSHIPS`, and source links.

## Where it appears in the take2 workshop

- **Section 06** (Phase 2 — Senzing Fundamentals) — Paco's live round-trip uses one of these records as the example input. Section 06's `06_senzing_input_record.json` / `06_senzing_affected_entities.json` are illustrative snippets; the real records in this dataset are what we push at scale.
- **Section 07** (Phase 2 — Graph → Senzing Pipeline) — the mapping discussion is "from our graph's exploded representation back to *this* JSON shape".
- **Section 08** (OOTB Senzing — Geocoding and Globalisation) — *primary capabilities showcase*. Key records cited:
  - `NK-dNNN56A4ApVfUFvfzniLCF` (Firuza Nazimovna Kerimova) — 13 alias variants across Latin, Cyrillic (Russian and Ukrainian), and Japanese scripts. The headline evidence that Senzing handles multi-script name resolution natively.
  - `NK-auyPsLrBzRoxjCRWgjBvas` (Wandle Holdings Limited) — Cyprus business address in Greek script, plus two variants of the same Cyprus registration number (`C188266` and `HE188266`).
  - `10442160967680700142` (Helena Verbeek, open-ownership) — Edinburgh address with `ADDR_COUNTRY: NL` — the upstream-data-quality issue we still own.
- **Section 09** (Phase 3 — Living Architecture) — candidate source for the growth → merge → split timeline once we pick a specific entity to follow.
- **Section 11** (Phase 5 — Graph Decision Layer and Trust IDs) — the Kerimova family records (Firuza, Amina, Gulnara, all sharing the same Moscow address with `Family` and `Owned or Controlled By` relationships in `RELATIONSHIPS`) are a natural anchor for the trust-ID examples.

## Notes

- Paco supplied this version. Confirm with him before republishing snippets outside the workshop deliverables.
- Records are real and in some cases involve named sanctioned individuals — handle on stage with the same care as any open-source watchlist data. Citing the OFAC source URL alongside the record is the right discipline.
- The dataset is line-delimited JSON (JSON Lines, not a JSON array). Tooling should treat it accordingly.
