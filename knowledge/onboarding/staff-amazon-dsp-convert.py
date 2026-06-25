#!/usr/bin/env python3
"""
Convert paired DSP onboarding files into the Hera Staff import CSV.

Inputs:
  - AMZL Associates export (csv) — the master roster
  - HRIS export — supports Uzio (xlsx) and ADP (csv).
    Format is auto-detected from extension + headers, or forced with
    --hris-format {uzio,adp}.

Mapping rules are documented in staff-import-mapping.md. Keep both files
in sync if Amazon, an HRIS vendor, or Hera changes their schema.

Rules:
- AMZL is the master roster. Every active+inactive AMZL row goes into the
  output. HRIS-only employees are skipped (they aren't drivers).
- For each AMZL row, try to find an HRIS match: name (first+last, drop
  middles and suffixes) -> email -> phone. Manual overrides via
  --merge "AMZL_TID=HRIS_PERSONAL_EMAIL".
- Matched rows pull First/Last from HRIS, Email from HRIS, Hire Date
  from HRIS. Email mismatches between HRIS and AMZL are flagged but HRIS
  wins.
- Unmatched AMZL rows pull First/Last by parsing 'Name and ID' (first
  token + last token after dropping suffixes); Email and Phone come from
  AMZL; Hire Date stays blank.
- Phone preference: AMZL Personal > AMZL Work > HRIS personal mobile > HRIS home/landline.
- Authorized To Drive: AMZL Qualifications mapped to Hera vehicle types,
  deduped, joined with '; '.
- DOB: pulled from HRIS when the HRIS provides it (ADP yes, Uzio no).
  Flag in pre-import notes — customer should confirm they want DOB tracked.
- Gender: pulled from HRIS when present and non-blank.
- Pronouns, Gas Card PIN, MVR, Hourly Status: blank.

Usage:
    python3 staff-amazon-dsp-convert.py \\
        --amzl   /path/to/AssociateData.csv \\
        --hris   /path/to/EmployeeRoster.xlsx     # or ADP .csv
        --output /path/to/<Company> - Staff.csv
"""

import argparse
import csv
import re
import sys
from collections import Counter
from datetime import datetime
from pathlib import Path

try:
    import openpyxl
except ImportError:
    sys.exit("openpyxl is required: pip install openpyxl")


HERA_HEADERS = [
    "Status", "First Name", "Last Name", "Hera Display Name", "Nickname",
    "Transporter ID", "Email", "Phone", "Hire Date", "Gender", "Pronouns",
    "DOB", "Gas Card PIN", "Authorized To Drive", "DL Expiration",
    "Motor Vehicle Report", "Hourly Status",
]

SUFFIXES = {"jr", "jr.", "sr", "sr.", "ii", "iii", "iv", "v"}

STANDARD_PARCEL_FULL = [
    "Standard Parcel Small",
    "Standard Parcel",
    "Standard Parcel Large",
    "Standard Parcel XL",
]

QUAL_MAP = {
    "CDV": ["Custom Delivery Van"],
    "EDV": ["EDV"],
    "Standard Parcel": STANDARD_PARCEL_FULL,
    "Step Van": ["10,000lbs Van"],
    "AMXL_STANDARD_PARCEL": STANDARD_PARCEL_FULL,
    "AMXL_CDV": ["Custom Delivery Van"],
    "AMXL_BOX_TRUCK": ["10,000lbs Van"],
    "AMXL_CNO_BOX_TRUCK": ["10,000lbs Van"],
}
QUAL_EXCLUDE = {
    "AMZL_HELPER", "AMXL_HELPER",
    "AMXL_CNO_VAN_LARGE_SINGLE_DA", "AMXL_LIFTGATE",
    "DOT",
}


def norm_name(n):
    if not n:
        return ""
    return re.sub(r"\s+", " ", str(n).lower().strip())


def first_last_key(full_name):
    tokens = [t for t in norm_name(full_name).split() if t not in SUFFIXES]
    if not tokens:
        return ""
    if len(tokens) == 1:
        return tokens[0]
    return f"{tokens[0]} {tokens[-1]}"


def parse_amzl_name(full_name):
    """Return (first, last) for an AMZL-only row. Drops middles and suffixes."""
    if not full_name:
        return "", ""
    tokens = [t for t in re.sub(r"\s+", " ", full_name).strip().split() if t.lower() not in SUFFIXES]
    if not tokens:
        return "", ""
    if len(tokens) == 1:
        return tokens[0], ""
    return tokens[0], tokens[-1]


def norm_email(e):
    return str(e).strip().lower() if e else ""


def norm_phone(p):
    if p is None or p == "":
        return ""
    if isinstance(p, float):
        try:
            p = str(int(p))
        except (ValueError, OverflowError):
            p = str(p)
    digits = re.sub(r"\D", "", str(p))
    return digits[-10:] if len(digits) >= 10 else ""


def quals_to_auth(q):
    if not q:
        return ""
    out = []
    for item in [x.strip() for x in q.split(",")]:
        if not item or item in QUAL_EXCLUDE:
            continue
        for v in QUAL_MAP.get(item, []):
            if v not in out:
                out.append(v)
    return "; ".join(out)


def to_mdy(d):
    """Normalize a date to MM/DD/YYYY. Accepts datetime, 'YYYY-MM-DD', or already-MDY strings."""
    if not d:
        return ""
    if isinstance(d, datetime):
        return d.strftime("%m/%d/%Y")
    s = str(d).strip()
    for fmt in ("%Y-%m-%d", "%m/%d/%Y", "%m/%d/%y"):
        try:
            return datetime.strptime(s, fmt).strftime("%m/%d/%Y")
        except ValueError:
            continue
    return s


def load_amzl(path):
    with open(path, newline="", encoding="utf-8-sig") as f:
        rows = list(csv.DictReader(f))
    for a in rows:
        a["_name_key"] = first_last_key(a["Name and ID"])
        a["_email_key"] = norm_email(a["Email"])
        a["_p_personal"] = norm_phone(a.get("Personal Phone Number"))
        a["_p_work"] = norm_phone(a.get("Work Phone Number"))
        a["_phones"] = {p for p in [a["_p_personal"], a["_p_work"]] if p}
    return rows


# ----- HRIS loaders ----------------------------------------------------------

def _hris_record(first, last_full, personal_email, hire, phone_primary, phone_secondary, dob, gender):
    """Common HRIS row shape consumed by the merge step."""
    return {
        "_first": (first or "").strip(),
        "_last_full": (last_full or "").strip(),
        "_name_key": first_last_key(f"{(first or '').strip()} {(last_full or '').strip()}"),
        "_email_key": norm_email(personal_email),
        "Personal Email": (personal_email or "").strip(),
        "Hire Date": hire,
        "_phone": norm_phone(phone_primary) or norm_phone(phone_secondary),
        "_phone_secondary": norm_phone(phone_secondary),
        "DOB": dob or "",
        "Gender": (gender or "").strip(),
    }


def load_uzio(path):
    wb = openpyxl.load_workbook(path, data_only=True)
    ws = wb["HR Report"]
    all_rows = list(ws.iter_rows(values_only=True))
    headers = all_rows[1]
    rows = []
    for r in all_rows[2:]:
        rec = dict(zip(headers, r))
        last = (rec.get("Last Name") or "").strip()
        suffix = (rec.get("Suffix") or "").strip()
        first = (rec.get("First Name") or "").strip()
        last_full = f"{last} {suffix}".strip() if suffix else last
        rows.append(_hris_record(
            first=first,
            last_full=last_full,
            personal_email=rec.get("Personal Email"),
            hire=to_mdy(rec.get("Date of Hire")),
            phone_primary=rec.get("Phone"),
            phone_secondary=None,
            dob="",       # Uzio Birthday lacks the year — leave blank
            gender="",    # Uzio doesn't carry Gender
        ))
    return rows


# ADP column names (the canonical export Hera receives).
ADP_HEADERS_EXPECTED = {
    "Legal First Name",
    "Legal Last Name",
    "Personal Contact: Personal Email",
}


def load_adp(path):
    """Read an ADP staff export CSV. Dedupe on Personal Email (case-insensitive).

    For duplicate emails, merge by taking the first occurrence's values and
    backfilling any blank fields from later occurrences. Common case: ADP
    returns two rows per person that differ only in Home Phone.
    """
    with open(path, newline="", encoding="utf-8-sig") as f:
        raw = list(csv.DictReader(f))

    by_email = {}
    order = []
    for r in raw:
        key = norm_email(r.get("Personal Contact: Personal Email"))
        if not key:
            # No email — fall back to a name+DOB key so unkeyed rows still dedupe.
            key = f"__nameonly::{norm_name(r.get('Legal First Name'))}|{norm_name(r.get('Legal Last Name'))}|{r.get('Birth Date','')}"
        if key not in by_email:
            by_email[key] = dict(r)
            order.append(key)
        else:
            kept = by_email[key]
            for col, val in r.items():
                if not kept.get(col) and val:
                    kept[col] = val

    rows = []
    for k in order:
        r = by_email[k]
        rows.append(_hris_record(
            first=r.get("Legal First Name"),
            last_full=r.get("Legal Last Name"),
            personal_email=r.get("Personal Contact: Personal Email"),
            hire=to_mdy(r.get("Hire Date")),
            phone_primary=r.get("Personal Contact: Personal Mobile"),
            phone_secondary=r.get("Home Phone"),
            dob=to_mdy(r.get("Birth Date")),
            gender=r.get("Gender for Compliance Reporting"),
        ))
    return rows


def detect_hris_format(path, forced):
    if forced:
        return forced
    suffix = path.suffix.lower()
    if suffix in (".xlsx", ".xlsm"):
        return "uzio"
    if suffix == ".csv":
        # Sniff the header row for ADP markers.
        with open(path, newline="", encoding="utf-8-sig") as f:
            reader = csv.reader(f)
            try:
                headers = set(next(reader))
            except StopIteration:
                headers = set()
        if ADP_HEADERS_EXPECTED.issubset(headers):
            return "adp"
        sys.exit(
            f"Cannot auto-detect HRIS format for {path}. "
            "Pass --hris-format adp|uzio to force."
        )
    sys.exit(f"Unsupported HRIS file type: {suffix}. Use .csv (ADP) or .xlsx (Uzio).")


def load_hris(path: Path, fmt: str):
    if fmt == "uzio":
        return load_uzio(path)
    if fmt == "adp":
        return load_adp(path)
    sys.exit(f"Unknown HRIS format: {fmt}")


# ----- Match + build --------------------------------------------------------

def match_hris(amzl_row, hris_by_name, hris_by_email, hris_by_phone, manual_overrides):
    tid = amzl_row["TransporterID"]
    if tid in manual_overrides:
        return manual_overrides[tid], "manual"
    if amzl_row["_name_key"] and amzl_row["_name_key"] in hris_by_name:
        return hris_by_name[amzl_row["_name_key"]], "name"
    if amzl_row["_email_key"] and amzl_row["_email_key"] in hris_by_email:
        return hris_by_email[amzl_row["_email_key"]], "email"
    for p in amzl_row["_phones"]:
        cands = hris_by_phone.get(p, [])
        if len(cands) == 1:
            return cands[0], "phone"
    return None, None


def build(amzl_path, hris_path, hris_format, output_path, manual_pairs):
    amzl = load_amzl(amzl_path)
    hris = load_hris(hris_path, hris_format)

    manual_overrides = {}
    for pair in manual_pairs:
        tid, ident = pair.split("=", 1)
        ident = ident.strip().lower()
        match = next((u for u in hris if u["_email_key"] == ident), None)
        if match:
            manual_overrides[tid.strip()] = match
        else:
            print(f"WARNING: manual merge pair '{pair}' did not resolve to an HRIS row.", file=sys.stderr)

    hris_by_name = {u["_name_key"]: u for u in hris if u["_name_key"]}
    hris_by_email = {u["_email_key"]: u for u in hris if u["_email_key"]}
    hris_by_phone = {}
    for u in hris:
        if u["_phone"]:
            hris_by_phone.setdefault(u["_phone"], []).append(u)
        if u.get("_phone_secondary"):
            hris_by_phone.setdefault(u["_phone_secondary"], []).append(u)

    output_rows = []
    flags = []
    used_hris_keys = set()
    dob_populated = 0
    gender_populated = 0

    for a in amzl:
        u, method = match_hris(a, hris_by_name, hris_by_email, hris_by_phone, manual_overrides)

        if u:
            used_hris_keys.add(u["_name_key"])
            first = u["_first"]
            last = u["_last_full"]
            email = u["Personal Email"]
            hire = u["Hire Date"]
            dob = u.get("DOB", "")
            gender = u.get("Gender", "")
            if u["_email_key"] and a["_email_key"] and u["_email_key"] != a["_email_key"]:
                flags.append(f"EMAIL_MISMATCH: {first} {last} | HRIS={u['Personal Email']} | AMZL={a['Email']}")
        else:
            first, last = parse_amzl_name(a["Name and ID"])
            email = a["Email"]
            hire = ""
            dob = ""
            gender = ""
            flags.append(f"AMZL_ONLY: {first} {last} (TID={a['TransporterID']}) — no HRIS match; parsed name from AMZL")

        if method == "manual":
            amzl_first, amzl_last = parse_amzl_name(a["Name and ID"])
            first = amzl_first or first
            last = amzl_last or last
            flags.append(f"MANUAL_MERGE: AMZL '{a['Name and ID']}' <- HRIS '{u['_first']} {u['_last_full']}' — using AMZL First/Last")

        display = f"{first} {last}".strip()

        if a["_p_personal"]:
            phone = a["_p_personal"]
        elif a["_p_work"]:
            phone = a["_p_work"]
            flags.append(f"PHONE_FALLBACK_to_AMZL_WORK: {display} (AMZL Personal blank)")
        elif u and u["_phone"]:
            phone = u["_phone"]
            flags.append(f"PHONE_FALLBACK_to_HRIS: {display} (AMZL had no phone)")
        elif u and u.get("_phone_secondary"):
            phone = u["_phone_secondary"]
            flags.append(f"PHONE_FALLBACK_to_HRIS_SECONDARY: {display} (AMZL + HRIS primary blank, using HRIS landline/home)")
        else:
            phone = ""
            flags.append(f"NO_PHONE: {display}")

        if a["Status"] == "ACTIVE":
            status = "Active"
        else:
            status = "Inactive - Misc"
            flags.append(f"STATUS_INACTIVE_in_AMZL: {display} -> Hera Status='Inactive - Misc'")

        auth = quals_to_auth(a["Qualifications"])
        if not auth:
            flags.append(f"NO_DRIVE_AUTH: {display} (Qualifications={a['Qualifications']!r})")

        if method == "email":
            flags.append(f"MATCHED_BY_EMAIL: {display} (HRIS name '{u['_first']} {u['_last_full']}' vs AMZL '{a['Name and ID']}')")
        elif method == "phone":
            flags.append(f"MATCHED_BY_PHONE: {display} — review (name and email did not match)")

        if dob:
            dob_populated += 1
        if gender:
            gender_populated += 1

        output_rows.append([
            status, first, last, "", "",
            a["TransporterID"], email, phone, hire,
            gender, "", dob, "",
            auth, to_mdy(a["ID expiration"]), "", "",
        ])

    hris_only = [u for u in hris if u["_name_key"] not in used_hris_keys]

    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(HERA_HEADERS)
        w.writerows(output_rows)

    summary = {
        "hris_format": hris_format,
        "amzl_rows": len(amzl),
        "hris_rows": len(hris),
        "hris_only_count": len(hris_only),
        "dob_populated": dob_populated,
        "gender_populated": gender_populated,
    }
    return output_rows, flags, hris_only, summary


def validate(output_rows):
    """Hard validation: only conditions that should block the import.

    Blank Authorized To Drive and blank DL Expiration are reported in the
    per-row flags above, but not treated as hard fails — AMZL occasionally
    has driver rows with no qualifications (helpers, office staff who got
    AMZL accounts, etc.) and the customer resolves these case-by-case.
    """
    issues = []
    tids = [r[5] for r in output_rows]
    tid_dupes = [t for t, c in Counter(tids).items() if c > 1]
    if tid_dupes:
        issues.append(f"DUPLICATE Transporter IDs (block import): {tid_dupes}")
    required = {0: "Status", 1: "First Name", 2: "Last Name", 5: "Transporter ID"}
    for ci, name in required.items():
        blanks = [i + 2 for i, r in enumerate(output_rows) if not r[ci]]
        if blanks:
            issues.append(f"Blank {name} in rows: {blanks}")
    return issues


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--amzl", required=True, type=Path)
    p.add_argument("--hris", required=True, type=Path)
    p.add_argument("--hris-format", choices=["uzio", "adp"], default=None,
                   help="Force HRIS format. Default: auto-detect by file extension + headers.")
    p.add_argument("--output", required=True, type=Path)
    p.add_argument("--merge", action="append", default=[],
                   help='Manual merge override: "AMZL_TID=hris_personal_email"')
    args = p.parse_args()

    fmt = detect_hris_format(args.hris, args.hris_format)
    output_rows, flags, hris_only, summary = build(args.amzl, args.hris, fmt, args.output, args.merge)

    print(f"HRIS format: {summary['hris_format']}")
    print(f"AMZL rows: {summary['amzl_rows']}  HRIS rows (deduped): {summary['hris_rows']}")
    print(f"Wrote {len(output_rows)} rows to {args.output}")
    print(f"DOB populated for {summary['dob_populated']} rows; Gender populated for {summary['gender_populated']} rows.")
    print()
    print(f"HRIS-only rows (skipped — not in AMZL): {summary['hris_only_count']}")
    for u in hris_only:
        print(f"  {u['_first']} {u['_last_full']} | email={u['Personal Email']} | phone={u['_phone']}")
    print()
    print("Flags:")
    for f in flags:
        print(f"  {f}")
    issues = validate(output_rows)
    print()
    print("Validation:")
    if issues:
        for i in issues:
            print(f"  [!] {i}")
        sys.exit(1)
    else:
        print("  All checks passed.")


if __name__ == "__main__":
    main()
