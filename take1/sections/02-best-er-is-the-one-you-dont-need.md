# The Best ER Is the One You Don't Need

## Narrative

Buying an ER product does not let us skip data engineering. It just changes which problems we hand off and which we keep. Data quality and the boring discipline of alignment, normalisation, and enrichment are not optional — they are the work that makes ER cheap, fast, and explainable. Skip them, and we pay later in redo storms, low-confidence merges, and analyst review queues.

The pattern is simple. Before a single record reaches Senzing, we do the work nobody finds glamorous:

- **Format alignment** — case, whitespace, punctuation, diacritics. `Jose María García`, `jose maria garcia`, `J.M. Garcia` should not be three different strings to the rest of the pipeline.
- **Prefix and suffix expansion** — strip and standardise `Dr.`, `Mr.`, `Jr.`, generational markers, honorifics. Keep them in a separate column if we need them; do not let them pollute the matching key.
- **Company suffix alignment** — `GmbH`, `G.m.b.H.`, `gmbh` collapse to one canonical form. Same for `Ltd` / `Limited`, `Corp` / `Corporation` / `Corp.`, `Inc` / `Incorporated`. Split the legal form off from the core name and keep both — the core name is what actually matches; the legal form is metadata.
- **Dictionary enrichment** — country codes to ISO3 (`Germany` → `DEU`, `U.A.E.` → `ARE`), nickname expansion (`Bob` ↔ `Robert`), date formats to ISO 8601. Each of these is a tiny lookup, and together they eliminate a large fraction of the variation that ER would otherwise have to absorb.

Once the data is aligned, something useful falls out for free: we can hash the stable, normalised columns and get a deduplication key. It is not entity resolution — we are not making decisions about whether two records refer to the same real-world entity — but it collapses obvious duplicates before they ever reach Senzing. Fewer records in means fewer features to evaluate, fewer redos, lower cost, and a cleaner signal for the resolution that actually requires judgement.

The slogan we want the audience to remember: **the best ER is the one we did not need to run, because we did the work upstream**. Everything we still reach for ER for is then a genuinely hard call, which is exactly the work we want Senzing doing.

## Normalisation walk-through

The two example datasets (`assets/data/02_persons_*.csv`, `assets/data/02_companies_*.csv`) carry the original columns alongside the normalised ones, so the before/after is visible on a single row. The `dedup_hash` column is a SHA-256 of the stable normalised fields, truncated to 16 hex characters for readability — identical hash means the records collapse to the same dedup key.

**Persons** — the rules applied:

- `full_name` → `name_norm`: lowercase, strip diacritics (`García` → `garcia`), drop punctuation (`.`, `-`), collapse internal whitespace, remove honorifics (`Dr.`, `Mr.`) and generational suffixes (`Jr.`, `Sr.`), expand nicknames against a dictionary (`Bob` → `robert`), expand abbreviated given names where unambiguous within the source (`M.` → `mohammed`, `J.M.` → `jose maria`).
- `dob` → `dob_norm`: parse heterogeneous formats (`1982-03-14`, `14/03/1982`, `Mar 14 1982`) and emit ISO 8601 `YYYY-MM-DD`. Locale ambiguity (US `MM/DD` vs EU `DD/MM`) resolved via the `source` system's known convention.
- `country` → `country_iso3`: lookup against a country dictionary, map every variant (`AE`, `United Arab Emirates`, `U.A.E.`, `SG`, `Singapore`, `US`, `USA`, `ES`, `Spain`, `ESP`) to ISO 3166-1 alpha-3.
- `dedup_hash` = SHA-256(`name_norm` + `|` + `dob_norm` + `|` + `country_iso3`)[:16]. The three Al-Rashid records, two Sarah Chen records, two Robert/Bob Smith records, and three Jose María García records collapse to four distinct hashes.

**Companies** — the rules applied:

- `legal_name` → `name_core` + `legal_form`: split the legal form off the end of the name. Recognise variants of `GmbH` (`G.m.b.H.`, `GMBH`), `Ltd` / `Limited`, `Corp` / `Corporation` / `Corp.` / `Inc.` / `Incorporated`, map each to a canonical form (`gmbh`, `ltd`, `corp`). Lowercase the `name_core`, normalise `&` to `and`, collapse whitespace.
- `country` → `country_iso3`: same ISO 3166-1 alpha-3 mapping as for persons.
- `reg_number` → `reg_number_norm`: strip whitespace and hyphens, uppercase. `HRB12345`, `HRB 12345`, `HRB-12345` all become `HRB12345`.
- `dedup_hash` = SHA-256(`name_core` + `|` + `legal_form` + `|` + `country_iso3` + `|` + `reg_number_norm`)[:16]. The three Acme Industries records, two Bright Future records, three Apex records, and two Smith & Sons records collapse to four distinct hashes. Smith & Sons has no detectable legal form in the source data, so that field is empty — and that is fine, because the registration number carries the load.

Note what the hash deliberately does *not* include: the source system, the original formatting, honorifics, or anything else that varies for non-identity reasons. Only the stable, normalised, identity-bearing fields go into the key. This is what makes the same physical entity collide across sources, and what keeps unrelated entities apart.

## Speaker notes

- This is the section where some of the audience will expect us to talk about Senzing. We deliberately do not. The point is that ER does not absolve us of data engineering — it depends on it.
- The German GmbH example lands well with European audiences. For US-heavy crowds, lean on `Corp` / `Corporation` / `Inc.` variations.
- The hash-as-free-dedup trick is worth pausing on. It is the cheapest win in the whole pipeline and most teams skip it.
- Avoid going down the rabbit hole of *how* to normalise (libraries, regexes, address parsers). That belongs in the appendix or a follow-up. Here we are establishing the principle.
- Good transition into the next section: "the normalisation rules above are the easy 80%. The remaining 20% is where the cross-cultural and geocoding edge cases live, and that is the next section."

## Assets

- `assets/data/02_persons_raw.csv` — 10 person records with realistic variation (case, titles, nicknames, diacritics, date and country formats).
- `assets/data/02_persons_normalized.csv` — the same 10 records after alignment; identical `dedup_hash` for records that collapse to the same entity.
- `assets/data/02_companies_raw.csv` — 10 company records covering `GmbH` variants, `Ltd` / `Limited`, `Corp` / `Corporation`, and `& / and`.
- `assets/data/02_companies_normalized.csv` — same records after suffix splitting and core-name normalisation, with `dedup_hash` showing the collapses.

## Open questions

- Do we want a live demo of the normalisation step, or is the before/after CSV enough? A 30-second Python snippet would land the point harder, but eats time.
- Should we name the libraries we use in practice (e.g. `cleanco`, `nameparser`, `libpostal`), or stay tool-agnostic? Naming them helps engineers in the room; staying agnostic keeps the message vendor-neutral.
- > [verify with Paco] Does Senzing prefer pre-normalised input, or does it have its own normalisation that we should *not* duplicate upstream? We do not want to fight its internal cleaning.
