# Globalisation and Geocoding — Where Naive ER Falls Apart

## Narrative

Two failure modes hit harder than any other in real-world ER, and they have nothing to do with the matching algorithm. They sit upstream, in assumptions baked into our data: how names should look, and where addresses should be. If we treat names as Western strings and addresses as globally unique, we will silently merge unrelated people and miss real matches.

### Names across cultures

Names are not strings. They are conventions, and the conventions differ by culture, language, and the system that captured the record. A few patterns we see constantly:

- **Arabic transliteration variance.** `Mohammed`, `Muhammad`, `Mohamed`, `Mohammad`, `Mohd` — five spellings of the same Arabic name, one underlying entity. The native-script `محمد` is identical; the Latinisation is whatever the data-entry clerk preferred. Same for `Al-Rashid` / `Al Rashid` / `Alrashid`.
- **Chinese name order and romanisation.** `Xi Jinping` (pinyin, family-first), `Jinping Xi` (Western reorder), `Hsi Chin-ping` (Wade-Giles, Taiwan-era romanisation). Three strings, one person. The CJK script `习近平` is the only stable anchor.
- **Spanish double surnames.** `Maria Garcia Lopez` (paternal then maternal) versus `Maria Garcia` (maternal dropped in a non-Spanish system). Treating the maternal surname as optional is correct; treating it as a distinguishing token is a merge failure waiting to happen.
- **Russian patronymics.** `Ivan Petrovich Sidorov` in a Russian source, `Ivan Sidorov` in a Western wire. The patronymic carries identity information in one system and is invisible in another.
- **Korean hyphenation.** `Park Ji-sung` versus `Jisung Park`. Family-name-first plus hyphenated given name versus romanised given-first. Identical entity, two strings that share almost no characters in common positions.

What we do about it: never collapse cross-cultural variants into a single normalised string by force. Keep the native script when we have it (it is the most stable anchor). Use transliteration libraries that know the source language. And tell Senzing what the script and language are when we push records — Senzing has feature handling for this, and we want it to do the work rather than pre-flattening signal that it could have used.

### Geocoding: the Caribbean–India problem

Addresses look like they should be globally unique. They are not. A street name in Port of Spain may be a more famous street name in Mumbai. A geocoder asked to resolve `Frederick Street` without a country anchor will return the Indian match because the Indian data volume dominates the index. This is not a bug in the geocoder — it is correctly returning its highest-confidence guess given the input — but it is a failure of how we ask the question.

The same problem in different forms:

- **Generic street names** (`Frederick Street`, `Main Street`, `Independence Square`) match many countries; whichever has the most data wins.
- **Colonial-era street names** (`Rue Saint-Honoré` in Paris and in Port-au-Prince) collide between metropole and former colony; the metropole almost always wins on data volume.
- **Famous landmarks** (`Marine Drive`) match the most-indexed place (Mumbai) and lose the smaller candidates (Beirut, plenty of others).

What we do about it:

- **Anchor every address to a country before geocoding**, ideally before that record ever reaches the geocoder. The country comes from the source system, the originating IBAN, the phone prefix, or the record's other context — not from the geocoder's guess.
- **Calibrate for known systematic errors.** If we know our pipeline geocodes Trinidadian addresses to India when the country token is missing, we instrument that path and either flag it or drop the geocode result entirely as untrustworthy.
- **Plausibility checks downstream.** A person with a Trinidadian phone number, a Trinidadian source system, and a geocoded-to-India address is more likely a geocoding failure than a person who genuinely moved continents. The graph view makes this kind of inconsistency easy to surface.

The shared lesson: globalisation breaks the implicit assumption that strings carry their context. They do not — context lives in the source system, the script, the country code, the originating channel. The job upstream of ER is to put the context back in before Senzing sees the record.

## Speaker notes

- This section is where we promised candour. Tell the stories straight: the Caribbean→India geocode hit us in a real project, and the redo storms that came out of it taught us to country-anchor everything.
- The audience will include people who have only worked with Western datasets. Linger on the Chinese and Korean examples — they are the ones that produce the most "wait, really?" moments.
- Avoid implying that Senzing handles all this transparently. It has good defaults, but it works far better when we feed it well-prepared, context-rich input.
- The native-script columns in the CSV are intentionally present even when the record was captured in Latin. The point: if we ever *had* the native script, we should have kept it; throwing it away upstream loses irrecoverable signal.

## Assets

- `assets/data/03_names_cross_cultural.csv` — 12 records covering Arabic, Chinese, Spanish, Russian, Korean conventions, with native-script anchors where applicable.
- `assets/data/03_addresses_geocoding.csv` — 10 records showing geocoding failures (Trinidad→India, Lebanon→India, Haiti→France) and the country-and-city anchors that fix them.

## Open questions

- Do we have a real, anonymisable Caribbean→India geocoding war story we can tell on stage? It would land harder than a constructed example.
- > [verify with Paco] How Senzing handles native script versus transliteration when both are present in a record. We want to recommend "send both" but only if Senzing will use them.
- Should we mention specific transliteration libraries (`unidecode`, `arabic_transliterate`, ICU)? Useful for engineers in the room but vendor-leaning.
