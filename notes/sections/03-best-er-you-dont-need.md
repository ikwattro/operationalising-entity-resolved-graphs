# The Best ER Is the One You Don't Need

## Narrative

Buying an ER product does not let you skip data engineering. It just changes which problems you hand off and which you keep. Data quality and the boring discipline of alignment, normalisation, and enrichment are not optional — they are the work that makes ER cheap, fast, and explainable. Skip them, and you pay later — in missed connections, degraded analytics, and intelligence work that fails not because the analyst was wrong but because the data was.

But there is a harder version of this point. Sometimes, if you know your data and your fields carry enough discriminating power, good DQ is the whole answer. You normalise correctly, the duplicates collapse on a hash, and Senzing has nothing to add that you have not already resolved yourself. No ER engine needed.

That is what the title means. **The best ER is the one you did not need to run** — not because you bought good tooling, but because you understood your data and did the work. Everything you still reach for ER for after that is a genuinely hard problem, which is exactly where you want Senzing.

### Raw data — what it looks like before we touch it

We are using the [min_aml](https://github.com/DerwenAI/min_aml) subset throughout the workshop — a small, public, redactable AML dataset built from OpenOwnership and OpenSanctions. It has the variation we need to show the techniques and the failure modes.

The `assets/data/03_persons_raw.csv` snapshot below is what real source data looks like. Same physical people, very different strings:

```
KYC-001  | Dr. Mohammed Al-Rashid | 1982-03-14   | United Arab Emirates
WIRE-A12 | Muhammad Al Rashid     | 14/03/1982   | U.A.E.
REG-2090 | M. Rashid              | Mar 14 1982  | AE
KYC-002  | Sarah Chen             | 1990-07-22   | Singapore
WIRE-B07 | Bob Smith              | 11/02/1975   | USA
KYC-003  | Robert Smith Jr.       | 1975-11-02   | US
REG-2091 | José María García      | 1988-01-30   | Spain
KYC-004  | Jose Maria Garcia      | 30/01/1988   | ES
```

To a human, these collapse to four people. To a string-matching engine, they are eight strings sharing very few characters in common positions. To Senzing, they are eight records about which a resolution decision will have to be made. The cheaper we can make that decision, the better the system runs.

### The techniques

Before a single record reaches Senzing, you do the work nobody finds glamorous:

- **Format alignment.** Case, whitespace, punctuation, diacritics. `Jose María García`, `jose maria garcia`, `J.M. Garcia` should not be three different strings to the rest of the pipeline.
- **Prefix and suffix expansion.** Strip and standardise `Dr.`, `Mr.`, `Jr.`, generational markers, honorifics. Keep them in a separate column if you need them; do not let them pollute the matching key.
- **Company-suffix alignment.** `GmbH`, `G.m.b.H.`, `gmbh` collapse to one canonical form. Same for `Ltd` / `Limited`, `Corp` / `Corporation` / `Corp.`. Split the legal form off from the core name; the core name is what actually matches, the legal form is metadata.
- **Dictionary enrichment.** Country codes to ISO 3166-1 alpha-3 (`Germany` → `DEU`, `U.A.E.` → `ARE`), nickname expansion (`Bob` ↔ `Robert`), date formats to ISO 8601. Each of these is a tiny lookup; together they eliminate a large fraction of the variation Senzing would otherwise have to absorb.

### After — the dedup hash that falls out for free

Once the data is aligned, something useful falls out: you can hash the stable, normalised columns and get a **deduplication key**. It is not entity resolution — you are not making decisions about whether two records refer to the same real-world entity — but it collapses obvious duplicates before they ever reach Senzing.

`assets/data/03_persons_normalised.csv` shows the same records after alignment. The `dedup_hash` is a SHA-256 of `name_norm | dob_norm | country_iso3`, truncated to 16 hex chars for readability:

```
KYC-001  | mohammed al rashid | 1982-03-14 | ARE | 38d2f8ef964b7af1
WIRE-A12 | mohammed al rashid | 1982-03-14 | ARE | 38d2f8ef964b7af1
REG-2090 | mohammed al rashid | 1982-03-14 | ARE | 38d2f8ef964b7af1
KYC-002  | sarah chen         | 1990-07-22 | SGP | 419788d799247f30
WIRE-B07 | robert smith       | 1975-11-02 | USA | 21a2e7f090ad2cb7
KYC-003  | robert smith       | 1975-11-02 | USA | 21a2e7f090ad2cb7
REG-2091 | jose maria garcia  | 1988-01-30 | ESP | 616dcf313c6c0d86
KYC-004  | jose maria garcia  | 1988-01-30 | ESP | 616dcf313c6c0d86
```

Eight records, four hashes. The duplicates collapse for free. Fewer records into Senzing means fewer features to evaluate, fewer redos, lower cost, and a cleaner signal for the resolution that actually requires judgement.

What the hash deliberately does *not* include: the source system, the original formatting, honorifics, or anything else that varies for non-identity reasons. Only the stable, normalised, identity-bearing fields go into the key. That is what makes the same physical entity collide across sources, and what keeps unrelated entities apart.

### Sometimes the hash is enough — and that is the point

This is where the section title earns its name. If your data has enough discriminating fields and you normalise them correctly, the dedup hash solves the problem entirely. There is nothing Senzing will add.

Take `firstname`, `lastname`, `age`, `possibleYearsOfBirth`, `race`, `gender`. Normalise all of them correctly. Two records about the same person hash to the same value. That is deduplication. You did not need ER.

This is not a failure mode or a corner case — it is the goal. It happens when you know your data well enough to know that the variation you are seeing is formatting noise, not genuine ambiguity. The hash collapses it. Senzing is for the cases that remain: incomplete evidence, records from sources that share no common key, ambiguity that no normalisation step can resolve.

**Know your data.** Understand what fields you have, what they mean, and how much discriminating power they carry. That is what determines whether you need ER at all — and if you do, it determines how much of the work you can finish before Senzing ever sees a record.

Either way, always pass the cleanest possible data downstream. If you need Senzing, you get better resolution, fewer redos, and a cleaner signal. If you do not, you have already done the job.

### What you do not throw away

Two records collapsing to the same hash does not mean you delete one of them. You keep both. The hash is a *signal* — "these look like duplicates" — and the records themselves remain separately addressable in the graph, with their provenance intact. Section 05 (Phase 1) is about exactly how the graph holds the raw record and the alignment side-by-side without losing either.

This is the most important habit in the whole workshop: **disk is cheap, lost signal is permanent**. Normalisation produces *additional* columns; it never replaces the original.

## Speaker notes

- Some of the audience will expect us to talk about Senzing here. We deliberately do not. The point is that ER does not absolve you of data engineering — it depends on it.
- The hash-as-free-dedup trick is worth pausing on. Most teams skip it.
- The German GmbH example lands well with European audiences; the US `Corp` / `Corporation` / `Inc.` variations work better with North American crowds. Pick whichever the room is.
- Avoid going down the rabbit hole of *how* to normalise (libraries, regexes, address parsers). That belongs in the appendix. Here we establish the principle.
- The "you do not throw away the original" beat is the bridge to Phase 1.

## Assets

- `assets/data/03_persons_raw.csv` — raw person records (carried from take1).
- `assets/data/03_persons_normalised.csv` — same records after alignment, with `dedup_hash` showing the collapses.
- `assets/data/03_companies_raw.csv`, `assets/data/03_companies_normalised.csv` — same treatment for companies (carried from take1).

## Open questions

Moved to [`../TODOS.md`](../TODOS.md).
