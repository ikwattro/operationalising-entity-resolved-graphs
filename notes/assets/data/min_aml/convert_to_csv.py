"""Convert min_aml Senzing JSONL files to CSV (persons, organizations, relationships)."""

import csv
import json
from pathlib import Path

HERE = Path(__file__).parent
OUT = HERE / "csv"
OUT.mkdir(exist_ok=True)

SOURCES = [HERE / "open-ownership.json", HERE / "open-sanctions.json"]

PERSON_FIELDS = [
    "record_id", "data_source", "primary_name", "aliases", "gender",
    "date_of_birth", "nationality", "citizenship",
    "address", "address_country",
    "national_id_number", "national_id_type", "passport_number", "tax_id_number",
    "risk_topics", "url", "statement_date",
]

ORG_FIELDS = [
    "record_id", "data_source", "primary_name", "aliases",
    "registration_date", "registration_countries", "dissolution_date",
    "address", "address_country",
    "national_id_number", "national_id_type",
    "risk_topics", "url", "statement_date",
]

REL_FIELDS = [
    "from_record_id", "from_data_source",
    "to_record_id", "to_data_source",
    "relationship_role", "rel_type", "from_date", "thru_date",
]

def classify_rel(role: str) -> str:
    r = role.lower()
    if any(r.startswith(p) for p in ("shareholding", "voting_rights")) \
            or "ownership of shares" in r \
            or r in ("rights_to_surplus_assets_on_dissolution", "учрфл", "учрюлрос",
                     "owned or controlled by", "controlled by",
                     "appointment_of_board", "other_influence_or_control"):
        return "INFLUENCE"
    if r in ("directorship", "occupancy"):
        return "DIRECTOR"
    if r == "family":
        return "FAMILY"
    if "customer" in r or "contract" in r:
        return "CUSTOMER"
    return ""


def first(items, key, default=""):
    for item in items:
        v = item.get(key)
        if v:
            return v
    return default


def extract_person(rec):
    names = rec.get("NAMES", [])
    primary = (
        rec.get("PRIMARY_NAME_FULL")
        or first([n for n in names if n.get("NAME_TYPE") == "PRIMARY"], "NAME_FULL")
    )
    aliases = ";".join(
        n["NAME_FULL"] for n in names
        if n.get("NAME_TYPE") == "ALIAS" and n.get("NAME_FULL")
    )

    dob = rec.get("DATE_OF_BIRTH") or first(rec.get("DATES", []), "DATE_OF_BIRTH")

    attrs = rec.get("ATTRIBUTES", [])
    countries = rec.get("COUNTRIES", [])
    nationality = first(attrs, "NATIONALITY") or first(
        [c for c in countries if "NATIONALITY" in c], "NATIONALITY"
    )
    citizenship = first([c for c in countries if "CITIZENSHIP" in c], "CITIZENSHIP")

    addresses = rec.get("ADDRESSES", [])
    address = first(addresses, "ADDR_FULL")
    address_country = first(addresses, "ADDR_COUNTRY")

    identifiers = rec.get("IDENTIFIERS", [])
    nat_id = first([i for i in identifiers if "NATIONAL_ID_NUMBER" in i], "NATIONAL_ID_NUMBER")
    nat_id_type = first([i for i in identifiers if "NATIONAL_ID_NUMBER" in i], "NATIONAL_ID_TYPE")
    passport = first([i for i in identifiers if "PASSPORT_NUMBER" in i], "PASSPORT_NUMBER")
    tax_id = first([i for i in identifiers if "TAX_ID_NUMBER" in i], "TAX_ID_NUMBER")

    risks = ";".join(r["TOPIC"] for r in rec.get("RISKS", []) if r.get("TOPIC"))

    links = rec.get("LINKS", [])
    url = rec.get("URL") or next(
        (list(lnk.values())[0] for lnk in links if "OpenOwnership Register" in lnk),
        ""
    )

    return {
        "record_id": rec["RECORD_ID"],
        "data_source": rec["DATA_SOURCE"],
        "primary_name": primary,
        "aliases": aliases,
        "gender": rec.get("GENDER", ""),
        "date_of_birth": dob,
        "nationality": nationality,
        "citizenship": citizenship,
        "address": address,
        "address_country": address_country,
        "national_id_number": nat_id,
        "national_id_type": nat_id_type,
        "passport_number": passport,
        "tax_id_number": tax_id,
        "risk_topics": risks,
        "url": url,
        "statement_date": rec.get("statementDate") or rec.get("LAST_CHANGE", ""),
    }


def extract_org(rec):
    names = rec.get("NAMES", [])
    # OO orgs: NAMES[].PRIMARY_NAME_ORG; OS orgs: NAMES[NAME_TYPE=PRIMARY].NAME_ORG
    primary = (
        first([n for n in names if "PRIMARY_NAME_ORG" in n], "PRIMARY_NAME_ORG")
        or first([n for n in names if n.get("NAME_TYPE") == "PRIMARY"], "NAME_ORG")
    )
    aliases = ";".join(
        n["NAME_ORG"] for n in names
        if n.get("NAME_TYPE") == "ALIAS" and n.get("NAME_ORG")
    )

    reg_date = rec.get("REGISTRATION_DATE") or first(
        [d for d in rec.get("DATES", []) if "REGISTRATION_DATE" in d], "REGISTRATION_DATE"
    )
    reg_countries = (
        rec.get("REGISTRATION_COUNTRY")
        or ";".join(
            c["REGISTRATION_COUNTRY"]
            for c in rec.get("COUNTRIES", [])
            if c.get("REGISTRATION_COUNTRY")
        )
    )

    addresses = rec.get("ADDRESSES", [])
    address = first(addresses, "ADDR_FULL")
    address_country = first(addresses, "ADDR_COUNTRY")

    identifiers = rec.get("IDENTIFIERS", [])
    nat_id = first([i for i in identifiers if "NATIONAL_ID_NUMBER" in i], "NATIONAL_ID_NUMBER")
    nat_id_type = (
        first([i for i in identifiers if "NATIONAL_ID_NUMBER" in i], "NATIONAL_ID_TYPE")
        or first([i for i in identifiers if "NATIONAL_ID_NUMBER" in i], "OTHER_ID_TYPE")
    )

    risks = ";".join(r["TOPIC"] for r in rec.get("RISKS", []) if r.get("TOPIC"))

    links = rec.get("LINKS", [])
    url = rec.get("URL") or next(
        (list(lnk.values())[0] for lnk in links if "OpenCorporates" in lnk),
        ""
    )

    return {
        "record_id": rec["RECORD_ID"],
        "data_source": rec["DATA_SOURCE"],
        "primary_name": primary,
        "aliases": aliases,
        "registration_date": reg_date,
        "registration_countries": reg_countries,
        "dissolution_date": rec.get("dissolutionDate", ""),
        "address": address,
        "address_country": address_country,
        "national_id_number": nat_id,
        "national_id_type": nat_id_type,
        "risk_topics": risks,
        "url": url,
        "statement_date": rec.get("statementDate") or rec.get("LAST_CHANGE", ""),
    }


def extract_relationships(rec):
    rels = rec.get("RELATIONSHIPS", [])
    # Find the anchor key for this record (may appear as a dedicated anchor entry)
    anchor_key = None
    anchor_domain = None
    for r in rels:
        if "REL_ANCHOR_KEY" in r and "REL_POINTER_KEY" not in r:
            anchor_key = r["REL_ANCHOR_KEY"]
            anchor_domain = r.get("REL_ANCHOR_DOMAIN", rec["DATA_SOURCE"])
            break

    rows = []
    for r in rels:
        if "REL_POINTER_KEY" not in r:
            continue
        from_key = r.get("REL_ANCHOR_KEY") or anchor_key or rec["RECORD_ID"]
        from_ds = r.get("REL_ANCHOR_DOMAIN") or anchor_domain or rec["DATA_SOURCE"]
        role = r.get("REL_POINTER_ROLE", "")
        # POINTER is the entity holding the role; ANCHOR is the entity it holds the role in.
        # Direction: POINTER → ANCHOR (e.g. person OWNS org, not org OWNS person).
        rows.append({
            "from_record_id": r["REL_POINTER_KEY"],
            "from_data_source": r.get("REL_POINTER_DOMAIN", ""),
            "to_record_id": from_key,
            "to_data_source": from_ds,
            "relationship_role": role,
            "rel_type": classify_rel(role),
            "from_date": r.get("REL_POINTER_FROM_DATE", ""),
            "thru_date": r.get("REL_POINTER_THRU_DATE", ""),
        })
    return rows


persons = []
orgs = []
relationships = []
_seen_rels = set()

for src in SOURCES:
    with src.open() as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            rec = json.loads(line)
            rtype = rec.get("RECORD_TYPE", "").upper()
            if rtype == "PERSON":
                persons.append(extract_person(rec))
            elif rtype == "ORGANIZATION":
                orgs.append(extract_org(rec))
            for row in extract_relationships(rec):
                key = (row["from_record_id"], row["to_record_id"],
                       row["relationship_role"], row["from_date"])
                if key not in _seen_rels:
                    _seen_rels.add(key)
                    relationships.append(row)


def write_csv(path, fields, rows):
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)
    print(f"  {path.name}: {len(rows)} rows")


print(f"Writing CSVs to {OUT}/")
write_csv(OUT / "persons.csv", PERSON_FIELDS, persons)
write_csv(OUT / "organizations.csv", ORG_FIELDS, orgs)
write_csv(OUT / "relationships.csv", REL_FIELDS, relationships)
