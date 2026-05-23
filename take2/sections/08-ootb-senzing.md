# What Is OOTB in Senzing — Geocoding and Globalisation

> **We are here:** still inside `SZ`, looking at what the engine already does for us before we do anything ourselves.

## Narrative

A pattern we see in projects: a team prepares to operationalise ER, reads up on the failure modes of cross-cultural name matching and address geocoding, and proposes a six-month upstream project to solve them. Sometimes that is the right call. Often it is not, because **Senzing already handles a lot of it out of the box**, and what we build upstream collides with what the engine is doing.

This section is about drawing the line, with **real records**. We use the `min_aml` dataset Paco provided (`assets/data/min_aml/open-ownership.json` and `open-sanctions.json`) — the same data we are pushing into the engine for the rest of the workshop — to show what Senzing handles natively and where we still need to help.

### What Senzing handles natively, with the receipts

#### Multi-script and cross-cultural name handling

The record `NK-dNNN56A4ApVfUFvfzniLCF` in `open-sanctions.json` is **Firuza Nazimovna Kerimova**, an OFAC-sanctioned individual. The same `RECORD_ID` carries 13 `NAME_TYPE: ALIAS` variants:

- **Latin transliterations:** `Firuza Nazimovna Kerimova`, `FIRUZA NAZIMOVNA KERIMOVA`, `KERIMOVA, Firuza Nazimovna`, `Firuza Kerimova`, `Kerimova Firuza`.
- **Married-name variants:** `Firuza Nazimovna Khanbalaeva`, `Firuza Kerimova (Khanbalaeva)`.
- **Russian Cyrillic:** `Керимова Фируза Назимовна`.
- **Ukrainian Cyrillic:** `Керімова Фіруза Назимівна`.
- **Alternate transliteration system:** `Kerimova Firuza Nazymivna` (Ukrainian-style romanisation of the Russian name).
- **Japanese katakana:** `フィルザ・ケリモウ゛ァ(ハンバラエウ゛ァ)` and `フィルザ・ケリモウ゛ァ` (with the married-name variant in brackets).

This is one person, one `RECORD_ID`, thirteen strings, four scripts. Senzing handles this natively — we send all of them in a single record's `NAMES` array, and the engine knows how to compare a `NAME_FULL` in Latin script against a `NAME_FULL` in Cyrillic or katakana when another record arrives.

The corollary: we do *not* pick one canonical spelling upstream and drop the others. The minute we collapse those thirteen variants to "Kerimova, Firuza", we lose the signal Senzing needed to match an incoming record from a Cyrillic-source system.

#### Address handling in non-Latin script

Record `NK-auyPsLrBzRoxjCRWgjBvas` (`WANDLE HOLDINGS LIMITED`) carries a Cyprus business address in **Greek script**:

```
DEANA BEACH APTS, BLOCK A, Flat 212, Προμαχών Ελευθερίας, 33,
'Άγιος Αθανάσιος, 4103, Λεμεσός, Κύπρος
```

with `ADDR_TYPE: BUSINESS`, `REGISTRATION_COUNTRY: cy`. Latin building-name + Greek street name + Greek city (Λεμεσός = Limassol) + Greek country (Κύπρος = Cyprus). Senzing accepts and matches against the Greek script directly.

#### Address parsing — same place, four shapes

The same Firuza Kerimova record has **four variants of the same Moscow address**:

```
1.  MOSCOW, RUS, 123430
2.  Apt. 270, Build. 31, Pyatnitskoe Shosse, 123430 Moscow
3.  Apt 270, Build. 31, Pyatnitskoe Shosse, Moscow, 123430
4.  ADDR_LINE1:    Apt 270, Build. 31, Pyatnitskoe Shosse
    ADDR_CITY:     Moscow
    ADDR_COUNTRY:  ru
    ADDR_POSTAL_CODE: 123430
```

Variant 1 is country-and-postcode only. Variants 2 and 3 are full-address strings with the components in different orders and slightly different punctuation. Variant 4 is the same address pre-parsed into structured fields. Senzing handles all four shapes — `ADDR_FULL` for the unstructured ones, the component fields when we have them. We do not have to normalise these four shapes into one before pushing.

#### Identifier normalisation — same ID, two formats

The Cyprus company `WANDLE HOLDINGS LIMITED` carries two `NATIONAL_ID_NUMBER` entries: `C188266` and `HE188266`. These are the same Cyprus registration number — the `HE` prefix (Cyprus's "Limited Company" prefix, *Etaireia Periorismenis Efthynis*) is sometimes included in the record and sometimes stripped. Senzing matches across these variants without us having to choose one.

The same shape shows up in the Russian records: `PASSPORT_NUMBER: 724348524` appears twice in Firuza's `IDENTIFIERS` array — once bare, once with `PASSPORT_COUNTRY: ru`. Senzing accepts both forms.

#### Cross-cultural conventions

Russian patronymics (`Nazimovna`, `Suleymanovna`) appear in the primary name and in many aliases. UK records have full postcodes (`WC2B 5DG`, `BR1 4EL`). Danish records carry Danish national IDs without a `NATIONAL_ID_TYPE` set. Each of these follows a convention the engine knows; none of them needs upstream rewriting.

### Where we still need to help — the cases Senzing cannot solve alone

OOTB is generous, not magical. There are failure modes the engine cannot fix because the missing information lives *outside* the record. Two real examples from the dataset:

#### Country mismatch in the source record

`open-ownership.json` contains the record `10442160967680700142` for **Helena Antoinette Marie Verbeek**:

```
ADDR_FULL:    28 Charlotte Square, Edinburgh, EH2 4ET
ADDR_COUNTRY: NL
NATIONALITY:  GB
```

The address is unambiguously in Edinburgh (Scotland, UK — `EH2 4ET` is a valid Edinburgh postcode). The country code says Netherlands. The nationality says Great Britain. This is a real data-quality issue *in the source*, and Senzing cannot reconcile it — only the upstream system can. If we let this through unchecked, downstream queries that filter by country will quietly misroute Helena.

The lesson: **country has to be consistent with the address before the record lands in Senzing**. The transparent overlay from Section 04 is where we catch and either correct or quarantine these.

#### Native script when the source dropped it

The Kerimova record only carries Cyrillic and Japanese aliases because the OFAC source preserved them. If the upstream system that captured the record had stripped to ASCII (as many KYC systems do), those aliases would be irrecoverable. Senzing would still match across the Latin variants — but never against a future Cyrillic-source record. The signal is gone.

The lesson: **when we have native script, we keep it. We never normalise to ASCII upstream.** Disk is cheap; lost signal is permanent.

#### Source-system context

For addresses without a country anchor, the geocoder will pull the most-indexed match — and the most-indexed match is almost always the wrong country if our data is from a smaller jurisdiction. In the `min_aml` dataset every address carries `ADDR_COUNTRY` because the source systems were careful. In customer data that is often not the case. **Country has to be in the record before Senzing geocodes it.** The country comes from the source system, the IBAN, the phone country prefix, or in-record context — never from the geocoder's guess.

### The honest message

If we leave the audience with one line from this section: **do not duplicate Senzing's work upstream**. The cross-cultural name handling, the multi-script address parsing, the identifier normalisation, the address-variant matching — Senzing already does it. The `Firuza Kerimova` record is the proof. The remaining work upstream is small, context-shaped, and unambiguous: country anchors, native-script preservation, source attribution. That is where engineering effort belongs.

## Speaker notes

- Open this section by pulling up the Kerimova record on screen — the thirteen aliases across four scripts is the most viscerally convincing single piece of evidence in the whole workshop that the engine earns its keep.
- The Cyrus Greek-script address is the second-strongest visual. Show it; the room will not forget it.
- Helena Verbeek's NL-vs-Edinburgh inconsistency is the line that lands the "what we still own" argument. Slow down on it.
- Paco co-anchors this section — he confirms what Senzing handles natively in the current version. We provide the framing and the receipts; Paco signs off.
- Avoid implying Senzing is *perfect*. The honest framing is "much more than you'd expect, but with a clear edge where you still need to help".

## Assets

- `assets/data/min_aml/open-sanctions.json` — 24 sanctioned-entity records (the canonical capabilities demo). Key records cited in this section: `NK-dNNN56A4ApVfUFvfzniLCF` (Firuza Kerimova, multi-script), `NK-auyPsLrBzRoxjCRWgjBvas` (Wandle Holdings, Greek-script Cyprus address).
- `assets/data/min_aml/open-ownership.json` — 316 UK beneficial-ownership records. Key record cited: `10442160967680700142` (Helena Verbeek, country-mismatch case).
- `references/min_aml.md` — pointer to the source and licensing notes.

## Open questions

Moved to [`../TODOS.md`](../TODOS.md).
