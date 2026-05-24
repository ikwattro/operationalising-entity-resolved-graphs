# The Depth of the Engine — What You'd Never Build Yourself

> **We are here:** still inside `SZ`. Paco lifts the hood.

## Narrative

Before we move to Phase 3, we stop on a question the room will be quietly asking: why not build this ourselves?

The answer is not "it's hard." The answer is: **you don't know how hard it is until you've seen what's inside**. Senzing is the product of years of focused engineering and domain knowledge from people who have done nothing else. The capabilities below are not configuration options — they are decisions that had to be made, researched, tested against real data at scale, and maintained across every language, jurisdiction, and data quality level on earth. Teams that have tried to build their own ER engine and had the right people have still ended up spending more money than they would have buying Senzing — and most teams do not have the right people.

This section is Paco's to lead. We provide the data; Paco shows what the engine actually does with it.

### What the engine actually does — with the receipts

#### Multi-script and cross-cultural name matching

Record `NK-dNNN56A4ApVfUFvfzniLCF` in `open-sanctions.json` is **Firuza Nazimovna Kerimova**, one sanctioned individual. Her record carries 13 name variants across four scripts:

- Latin transliterations: `Firuza Nazimovna Kerimova`, `FIRUZA NAZIMOVNA KERIMOVA`, `KERIMOVA, Firuza Nazimovna`, `Firuza Kerimova`, `Kerimova Firuza`.
- Married-name variants: `Firuza Nazimovna Khanbalaeva`, `Firuza Kerimova (Khanbalaeva)`.
- Russian Cyrillic: `Керимова Фируза Назимовна`.
- Ukrainian Cyrillic: `Керімова Фіруза Назимівна`.
- Alternate transliteration: `Kerimova Firuza Nazymivna` (Ukrainian-style romanisation of the Russian name).
- Japanese katakana: `フィルザ・ケリモウ゛ァ(ハンバラエウ゛ァ)` and `フィルザ・ケリモウ゛ァ`.

One person, one `RECORD_ID`, thirteen strings, four scripts. We send all of them in the `NAMES` array and the engine compares across scripts when a new record arrives — whether it is Latin, Cyrillic, or katakana. We did not implement that. We did not configure that. It is in the engine.

The corollary: we do not collapse the thirteen variants to one canonical spelling upstream. The signal we discard is gone permanently.

#### Address handling in non-Latin script

Record `NK-auyPsLrBzRoxjCRWgjBvas` (`WANDLE HOLDINGS LIMITED`) carries a Cyprus business address in Greek script:

```
DEANA BEACH APTS, BLOCK A, Flat 212, Προμαχών Ελευθερίας, 33,
'Άγιος Αθανάσιος, 4103, Λεμεσός, Κύπρος
```

Latin building name, Greek street name, Greek city (Λεμεσός = Limassol), Greek country. The engine accepts and matches against this directly. No transliteration step upstream.

#### Address variants — same place, four shapes

Firuza Kerimova's same Moscow address appears four times in her record:

```
1.  MOSCOW, RUS, 123430
2.  Apt. 270, Build. 31, Pyatnitskoe Shosse, 123430 Moscow
3.  Apt 270, Build. 31, Pyatnitskoe Shosse, Moscow, 123430
4.  ADDR_LINE1: Apt 270, Build. 31, Pyatnitskoe Shosse
    ADDR_CITY: Moscow
    ADDR_COUNTRY: ru
    ADDR_POSTAL_CODE: 123430
```

Country-and-postcode only. Full free-text string in two component orders. Structured fields. All four resolve to the same place. We did not write a normaliser for this. We do not need to.

#### Identifier normalisation

`WANDLE HOLDINGS LIMITED` carries `C188266` and `HE188266` — the same Cyprus company registration, with and without the legal-type prefix. The engine matches across them. Russian passport `724348524` appears twice — once bare, once with `PASSPORT_COUNTRY: ru`. The engine handles both forms.

#### Cross-cultural conventions

Russian patronymics (`Nazimovna`, `Suleymanovna`) in both primary names and aliases. UK postcodes (`WC2B 5DG`, `BR1 4EL`). Danish national IDs without a type set. Each of these follows a convention the engine was built to know. None of them required upstream rewriting on our part.

### The thin layer we still own

The engine cannot fix what was never in the record. Two real cases from the dataset:

**Country mismatch in the source.** `open-ownership.json` record `10442160967680700142`, Helena Antoinette Marie Verbeek: address `28 Charlotte Square, Edinburgh, EH2 4ET`, country code `NL`, nationality `GB`. The address is in Edinburgh. The country says Netherlands. That is a source-data error. Senzing will process what it receives. We catch this upstream — or we accept that Helena will misroute in any country-filtered query.

**Native script stripped by the source.** The Kerimova record carries Cyrillic and Japanese because the OFAC source preserved them. If an upstream KYC system normalised to ASCII before we saw the record, those aliases are gone. Senzing matches across the Latin variants — but it will never match a future Cyrillic-source record. The signal is not recoverable. **When we have native script, we keep it. We never normalise to ASCII upstream.**

These two cases define the boundary. Everything else — the script handling, the address parsing, the identifier variants, the cultural conventions — the engine has already solved. Our job upstream is country anchors, native-script preservation, and clean source attribution. Nothing more.

### The build-vs-buy line

This is not an advertisement. It is an accounting problem. If you try to build what the Kerimova record demonstrates — multi-script comparison, address-variant matching, identifier-form normalisation, cross-cultural patronymic handling — across every script and jurisdiction your data touches, you are building a research project. The teams that have done it and had genuinely strong people have still spent more than the licence cost. Most teams do not have the people. Either way, you are not building a product faster than Senzing has iterated on one.

Buy the engine. Own the thin layer. That is the correct split.

## Speaker notes

- Paco leads. His job is to show the room things they would not have thought of. The Kerimova record is the opener — pull it up on screen, read the four scripts out loud, and let it land.
- The Greek-script Cyprus address is the second strongest visual. Show it without translating it first.
- The build-vs-buy section is deliberately blunt. Do not soften it. The audience in this room is evaluating exactly this question.
- Paco should feel free to go further than the receipts listed here — if there are internal capabilities of the engine that are not visible in this data but are equally surprising, this is the slot for them.
- The "thin layer we own" beats are ours to deliver: Helena Verbeek's country mismatch and the ASCII-strip failure mode are both GraphAware-side observations about what the upstream has to get right.

## Assets

- `assets/data/min_aml/open-sanctions.json` — key records: `NK-dNNN56A4ApVfUFvfzniLCF` (Firuza Kerimova, multi-script), `NK-auyPsLrBzRoxjCRWgjBvas` (Wandle Holdings, Greek-script address).
- `assets/data/min_aml/open-ownership.json` — key record: `10442160967680700142` (Helena Verbeek, country-mismatch case).
- `references/min_aml.md` — source and licensing notes.

## Open questions

Moved to [`../TODOS.md`](../TODOS.md).
