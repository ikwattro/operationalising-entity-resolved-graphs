"""Convert icij-london Senzing JSONL to CSV (persons, organizations, relationships)."""

import csv
import json
from pathlib import Path

HERE = Path(__file__).parent
SOURCE = HERE.parent / "icij-london.jsonl"
OUT = HERE / "csv"
OUT.mkdir(exist_ok=True)

PERSON_FIELDS = [
    "record_id", "data_source", "icij_source", "node_type",
    "primary_name",
    "countries",
    "address", "address_type",
    "group_associations",
    "notes",
]

ORG_FIELDS = [
    "record_id", "data_source", "icij_source", "node_type",
    "primary_name",
    "jurisdiction", "status", "incorporated", "inactivated", "struck_off", "company_type",
    "countries",
    "address", "address_type",
    "notes",
]

REL_FIELDS = [
    "anchor_record_id", "anchor_domain",
    "pointer_record_id", "pointer_domain",
    "relationship_role", "rel_type", "from_date", "thru_date",
]


def classify_rel(role) -> str:
    if not role:
        return ""
    r = role.lower().strip()
    if any(r.startswith(p) for p in ("shareholder", "beneficial owner", "beneficialowner",
                                      "ultimate beneficial owner", "person of significant control",
                                      "nominee shareholder")):
        return "OWNERSHIP"
    if any(kw in r for kw in ("director", "president", "chairman", "secretary",
                               "treasurer", "chief executive", "chief financial",
                               "managing director", "vice-president", "vice president",
                               "vice chairman")):
        return "DIRECTOR"
    if any(kw in r for kw in ("trustee", "settlor", "protector", "co-trustee")):
        return "TRUST"
    if any(kw in r for kw in ("address", "registered office", "registered at",
                               "registration address", "postal")):
        return "ADDRESS"
    if r == "intermediary of":
        return "INTERMEDIARY"
    if any(kw in r for kw in ("representative", "signatory", "attorney",
                               "judicial", "legal", "advisor")):
        return "REPRESENTATIVE"
    if any(kw in r for kw in ("same name", "same id", "similar name", "linked to",
                               "related party", "connected to")):
        return "LINK"
    return ""


def first_address(addresses):
    if not addresses:
        return "", ""
    a = addresses[0]
    return a.get("ADDR_FULL", ""), a.get("ADDR_TYPE", "")


def extract_person(rec):
    countries = ";".join(
        c["COUNTRY_OF_ASSOCIATION"]
        for c in rec.get("COUNTRIES", [])
        if c.get("COUNTRY_OF_ASSOCIATION")
    )
    addr_full, addr_type = first_address(rec.get("ADDRESSES", []))
    groups = ";".join(
        g["GROUP_ASSOCIATION_ORG_NAME"]
        for g in rec.get("GROUP_ASSOCATIONS", [])
        if g.get("GROUP_ASSOCIATION_ORG_NAME")
    )
    return {
        "record_id": rec["RECORD_ID"],
        "data_source": rec["DATA_SOURCE"],
        "icij_source": rec.get("ICIJ_SOURCE", ""),
        "node_type": rec.get("NODE_TYPE", ""),
        "primary_name": rec.get("PRIMARY_NAME_FULL", ""),
        "countries": countries,
        "address": addr_full,
        "address_type": addr_type,
        "group_associations": groups,
        "notes": rec.get("NOTES", ""),
    }


def extract_org(rec):
    countries = ";".join(
        c["COUNTRY_OF_ASSOCIATION"]
        for c in rec.get("COUNTRIES", [])
        if c.get("COUNTRY_OF_ASSOCIATION")
    )
    addr_full, addr_type = first_address(rec.get("ADDRESSES", []))
    return {
        "record_id": rec["RECORD_ID"],
        "data_source": rec["DATA_SOURCE"],
        "icij_source": rec.get("ICIJ_SOURCE", ""),
        "node_type": rec.get("NODE_TYPE", ""),
        "primary_name": rec.get("PRIMARY_NAME_ORG", ""),
        "jurisdiction": rec.get("Jurisdiction", ""),
        "status": rec.get("Status", ""),
        "incorporated": rec.get("INCORPORATED", ""),
        "inactivated": rec.get("INACTIVATED", ""),
        "struck_off": rec.get("STRUCK_OFF", ""),
        "company_type": rec.get("COMPANY_TYPE", ""),
        "countries": countries,
        "address": addr_full,
        "address_type": addr_type,
        "notes": rec.get("NOTES", ""),
    }


def extract_relationships(rec):
    anchor_key = str(rec.get("REL_ANCHOR_KEY", rec["RECORD_ID"]))
    anchor_domain = rec.get("REL_ANCHOR_DOMAIN", rec["DATA_SOURCE"])
    rows = []
    for r in rec.get("RELATIONSHIPS", []):
        if "REL_POINTER_KEY" not in r:
            continue
        role = r.get("REL_POINTER_ROLE", "")
        rows.append({
            "anchor_record_id": anchor_key,
            "anchor_domain": anchor_domain,
            "pointer_record_id": str(r["REL_POINTER_KEY"]),
            "pointer_domain": r.get("REL_POINTER_DOMAIN", ""),
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

with SOURCE.open() as f:
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
            key = (row["anchor_record_id"], row["pointer_record_id"],
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
