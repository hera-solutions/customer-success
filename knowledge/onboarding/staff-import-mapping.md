# Staff Import Mapping (HRIS + AMZL Associates → Hera Staff)

Reusable spec for converting a customer's onboarding **Staff** data into the Hera Staff import template. Unlike Vehicles, Staff requires a **join of two source files**:

1. The customer's HRIS export (ADP or Paycom — see [Gather Your Onboarding Data](https://support.hera.app/en/articles/10139790-gather-your-onboarding-data)).
2. The customer's Amazon Logistics Associates export (Administration > Associates > My Associates > Download).

Both files cover the same set of people. We match them and merge the fields into one Hera Staff row per associate.

Related docs:
- [import-templates.md](import-templates.md) — canonical Hera template definitions and global rules (date format, etc.).
- [vehicles-amazon-dsp-mapping.md](vehicles-amazon-dsp-mapping.md) — Hera vehicle type taxonomy reused below.

---

## Source 1: AMZL Associates export (LOCKED)

Filename pattern (typical): `AssociateData (N).csv`. Column structure is consistent across DSP customers — Amazon controls the export schema.

### Column structure

| # | Column | Format | Notes |
|---|---|---|---|
| 1 | `Name and ID` | Full legal name | Some rows have double-spaces between name parts. Normalize to single space on read. |
| 2 | `TransporterID` | Amazon ID, e.g., `A39DX7EJYCK2DZ` | Unique per associate. **This is the strongest UID on the AMZL side.** |
| 3 | `Position` | `Helper, Driver` (or `Driver, Helper`) | Not used. Drop. |
| 4 | `Qualifications` | Comma-separated list | Mapped to Hera vehicle types — see table below. |
| 5 | `ID expiration` | `YYYY-MM-DD` | Driver's License expiration. Convert to `MM/DD/YYYY`. |
| 6 | `Personal Phone Number` | 10-digit unformatted | Primary phone source. |
| 7 | `Work Phone Number` | E.164 with `+1` | Fallback when Personal is blank. |
| 8 | `Email` | Standard email | Used to cross-check the HRIS email — see Email rule below. |
| 9 | `Status` | `ACTIVE` / `INACTIVE` | `ACTIVE` → `Active`; `INACTIVE` → `Inactive - Misc` (flag in pre-import notes). |

### Mapping to Hera Staff fields (AMZL side)

| AMZL column | Hera Staff field | Transform |
|---|---|---|
| `Name and ID` | First Name | Split on whitespace after normalizing doubles → first token |
| `Name and ID` | Last Name | Split on whitespace after normalizing doubles → last token |
| `TransporterID` | Transporter ID | direct |
| `Qualifications` | Authorized To Drive | Map each qualification per table below; dedupe; **join with `;` (semicolon)** |
| `ID expiration` | DL Expiration | `YYYY-MM-DD` → `MM/DD/YYYY` |
| `Personal Phone Number` | Phone | Use as primary; fall back to `Work Phone Number` if blank |
| `Status` | Status | `ACTIVE` → `Active`; `INACTIVE` → `Inactive - Misc` (flag) |

### Qualifications → Hera Vehicle Types

`Authorized To Drive` ends up as a semicolon-separated list of Hera vehicle types after applying this map and deduping:

| AMZL Qualification | Hera Vehicle Type(s) |
|---|---|
| `AMZL_HELPER` | *(exclude — helper, not a driver qual)* |
| `AMXL_HELPER` | *(exclude — helper, not a driver qual)* |
| `CDV` | Custom Delivery Van |
| `EDV` | EDV |
| `Standard Parcel` | **Standard Parcel Small; Standard Parcel; Standard Parcel Large; Standard Parcel XL** |
| `Step Van` | 10,000lbs Van |
| `AMXL_STANDARD_PARCEL` | **Standard Parcel Small; Standard Parcel; Standard Parcel Large; Standard Parcel XL** |
| `AMXL_CDV` | Custom Delivery Van |
| `AMXL_BOX_TRUCK` | 10,000lbs Van |
| `AMXL_CNO_BOX_TRUCK` | 10,000lbs Van |
| `AMXL_CNO_VAN_LARGE_SINGLE_DA` | *(exclude)* |
| `AMXL_LIFTGATE` | *(exclude — liftgate certification, not a vehicle type)* |
| `DOT` | *(exclude — DOT certification, not a vehicle type)* |

**Standard Parcel expansion rule:** Anyone qualified for Standard Parcel (`Standard Parcel` or `AMXL_STANDARD_PARCEL`) is treated as authorized to drive all four Standard Parcel sizes (Small, regular, Large, XL).

Example: `AMZL_HELPER, CDV, Standard Parcel , EDV` → `Custom Delivery Van; Standard Parcel Small; Standard Parcel; Standard Parcel Large; Standard Parcel XL; EDV`.

### Hera Staff fields the AMZL file does NOT provide

These have to come from the HRIS side (or stay blank):
- Hera Display Name
- Nickname
- Hire Date
- Gender
- Pronouns
- DOB
- Gas Card PIN
- Motor Vehicle Report
- Hourly Status

### AMZL Email vs HRIS Email rule

**AMZL email is the source of truth for the Hera `Email` field.** DSPs typically issue company-style emails (e.g., `<lastname><firstinitial>plgt@gmail.com`) and use them for AMZL ops — drivers actually check those addresses during shifts. The HRIS personal email is often a private address the driver doesn't monitor at work.

Rules:
- AMZL email populated → use it for Hera `Email`.
- AMZL email blank, HRIS personal email populated → fall back to HRIS personal.
- Both blank → Hera `Email` is blank; flag the driver in pre-import notes.
- Mismatches between AMZL and HRIS personal are noted in pre-import notes for transparency, but no per-driver decision is required — AMZL wins by default.

(Process change committed 2026-06-05 during the Precise Logistical Services import. Earlier locked rule said HRIS wins; that's no longer the default.)

---

## Source 2: HRIS export

Hera accepts HRIS exports from three systems: **ADP, Paycom, and Uzio**. The converter currently supports ADP (csv) and Uzio (xlsx); Paycom is still TBD. Format is auto-detected by file extension and header sniffing, or can be forced with `--hris-format`.

### Uzio — Employee Roster (LOCKED)

Filename pattern (typical): `Employee Roster.xlsx`. Single sheet, named `HR Report`.

**Header structure — two rows:**

| Row | Purpose |
|---|---|
| Row 1 | Section grouping labels: `Personal`, `Job`, `Home Address`. **Ignore on parse.** |
| Row 2 | Actual column names. |
| Row 3+ | Data. |

Personal Email and Phone are grouped under "Home Address" in the Uzio file — a Uzio quirk. They are personal contact fields, not address fields.

**Column structure:**

| # | Column | Type / Format | Notes |
|---|---|---|---|
| 1 | First Name | text | Strip whitespace. |
| 2 | Last Name | text | If `Suffix` is populated, append: `<Last Name> <Suffix>` (e.g., `Smith II`). |
| 3 | Suffix | text | Usually blank. When present (`II`, `Jr`, `Sr`, etc.), append to Last Name and then drop. |
| 4 | Birthday | text | **Month + day only, no year.** A few rows get auto-converted to Excel datetimes with a bogus current year — treat the same. |
| 5 | Date of Hire | datetime | Convert to `MM/DD/YYYY`. |
| 6 | Personal Email | text | Used for Hera `Email`. |
| 7 | Phone | text or float | Some rows arrive as floats (Excel autoconversion). Convert `7576769408.0` → `7576769408` (int → str). |

**Mapping to Hera Staff fields (Uzio side):**

| Uzio column | Hera Staff field | Transform |
|---|---|---|
| First Name | First Name | strip whitespace |
| Last Name + Suffix | Last Name | concat with space if Suffix present |
| Date of Hire | Hire Date | datetime → `MM/DD/YYYY` |
| Personal Email | Email | direct |
| Phone | Phone | normalize: float → int → str |
| *(constant)* | Status | `Active` for all Uzio-sourced rows (Uzio export does not include status; assume the report lists active employees only) |
| *(blank)* | DOB | left blank — Uzio Birthday lacks the year |
| *(blank)* | Gender | left blank — Uzio HR Report does not include this |

**Pre-import flags Uzio always produces:**

- Every employee has blank DOB. Note in pre-import summary.
- Every employee has blank Gender. Note in pre-import summary.
- Any employee whose Birthday cell arrived as a datetime (Excel autoconversion) — list separately so it can be sanity-checked later.

### ADP — Hera Staff Report (LOCKED)

Filename pattern (typical): `Hera Staff Report.csv`. CSV with a single header row. Dates arrive already formatted as `MM/DD/YYYY`.

**Column structure:**

| # | Column | Format | Notes |
|---|---|---|---|
| 1 | `Legal First Name` | text | |
| 2 | `Legal Last Name` | text | ADP returns the legal last name in one field — no separate Suffix column to merge. |
| 3 | `Personal Contact: Personal Email` | email | Source of truth for the Hera `Email` field. |
| 4 | `Work Contact: Work Email` | email | Not used for import. Sometimes blank. |
| 5 | `Home Phone` | `(NNN) NNN-NNNN` | Secondary phone fallback. |
| 6 | `Work Contact: Work Phone` | `(NNN) NNN-NNNN` | Not used. |
| 7 | `Personal Contact: Personal Mobile` | `(NNN) NNN-NNNN` | Primary HRIS phone. |
| 8 | `Birth Date` | `MM/DD/YYYY` | Pulled into Hera `DOB`. |
| 9 | `Gender for Compliance Reporting` | text or blank | Pulled into Hera `Gender` when populated. Frequently blank. |
| 10 | `Hire Date` | `MM/DD/YYYY` | Pulled into Hera `Hire Date`. |

**Mapping to Hera Staff fields (ADP side):**

| ADP column | Hera Staff field | Transform |
|---|---|---|
| `Legal First Name` | First Name | strip whitespace |
| `Legal Last Name` | Last Name | strip whitespace |
| `Personal Contact: Personal Email` | Email | direct |
| `Personal Contact: Personal Mobile` | Phone (HRIS primary) | normalize to 10 digits |
| `Home Phone` | Phone (HRIS secondary) | normalize to 10 digits |
| `Hire Date` | Hire Date | passes through; already `MM/DD/YYYY` |
| `Birth Date` | DOB | passes through; already `MM/DD/YYYY` — see PII note |
| `Gender for Compliance Reporting` | Gender | direct if non-blank |
| *(none)* | Status | Driven by AMZL only (`ACTIVE`→`Active`, `INACTIVE`→`Inactive - Misc`) |

**ADP dedup rule:** ADP exports often list the same person twice, differing only in `Home Phone`. The converter dedupes on lowercased `Personal Contact: Personal Email`. For duplicates, the first occurrence wins and any blank fields are backfilled from later occurrences.

**Pre-import flags ADP commonly produces:**

- DOB populated for most employees. Carry the values through — DOB is included whenever ADP provides it. (Process change 2026-06-05: no longer blanked by default.)
- `Gender for Compliance Reporting` carried through when populated. Blank rows stay blank. (Process change 2026-06-05: no longer blanked by default.)
- Phone falls back to ADP `Home Phone` when AMZL has no phone and ADP `Personal Mobile` is also blank.

### Paycom — Advanced Report Writer (LOCKED)

Filename pattern (typical): `YYYYMMDDHHMMSS_Advanced_Report_Writer_<hash>.csv`. CSV with a single header row. Dates arrive already formatted as `MM/DD/YYYY`. Names arrive in **ALL CAPS**.

**Column structure:**

| # | Column | Format | Notes |
|---|---|---|---|
| 1 | `Legal_Firstname` | text (all caps) | Title-case on load. |
| 2 | `Legal_Lastname` | text (all caps) | Title-case on load. `Mc`/`Mac` prefixes and hyphenated names are handled by the converter's smart title-caser. Edge cases (e.g., unusual prefixes) can be corrected in Hera post-import. |
| 3 | `Employee_Status` | `Active` / (other) | Not used — status is driven by AMZL. |
| 4 | `Primary_Phone` | 11-digit E.164-ish string, e.g., `12179741311` | Normalized to last 10 digits. |
| 5 | `Personal_Email` | email | Source of truth for HRIS-side Email (AMZL still wins by the AMZL-vs-HRIS email rule above). |
| 6 | `Birth_Date_(MM/DD/YYYY)` | `MM/DD/YYYY` | Pulled into Hera `DOB`. Watch for driver DOBs that imply age under 18 at hire — flag in pre-import. |
| 7 | `Hire_Date` | `MM/DD/YYYY` | Pulled into Hera `Hire Date`. |

**Mapping to Hera Staff fields (Paycom side):**

| Paycom column | Hera Staff field | Transform |
|---|---|---|
| `Legal_Firstname` | First Name | `title_case_name()` |
| `Legal_Lastname` | Last Name | `title_case_name()` |
| `Personal_Email` | Email | direct |
| `Primary_Phone` | Phone (HRIS primary) | normalize to 10 digits |
| `Hire_Date` | Hire Date | passes through; already `MM/DD/YYYY` |
| `Birth_Date_(MM/DD/YYYY)` | DOB | passes through; already `MM/DD/YYYY` |
| *(not in export)* | Gender | left blank — this Paycom template does not include Gender |
| *(none)* | Status | Driven by AMZL only (`ACTIVE`→`Active`, `INACTIVE`→`Inactive - Misc`) |

**Pre-import flags Paycom commonly produces:**

- All names arrive as ALL CAPS. Converter title-cases automatically. Spot-check `Mc`, `Mac`, `O'`, and hyphenated surnames in the output.
- DOB populated for all rows. Carry through per the DOB-always-through rule (2026-06-05 process change).
- Gender always blank — this template does not include gender.
- Driver DOBs implying age under 18 at Hire Date should be flagged for customer confirmation.

---

## Join logic (HRIS ↔ AMZL) — LOCKED

**AMZL is the master roster.** Every AMZL row (active or inactive) becomes a Hera Staff row. HRIS data is layered on top when a match exists.

### Inclusion rules

| Source presence | Imported? | Hera Status |
|---|---|---|
| In AMZL + in HRIS | Yes | `Active` or `Inactive` based on AMZL status |
| In AMZL only | Yes — "import as much as possible" | Based on AMZL status; First/Last parsed from AMZL `Name and ID` (first + last token, suffixes dropped); Hire Date stays blank |
| In HRIS only | **Skip** | Not a driver per the Amazon roster |

### Match algorithm

For each AMZL row, try in order:

1. **Name** — `first_last_key(AMZL.Name and ID)` vs `first_last_key(Uzio.First Name + " " + Uzio.Last Name)`. `first_last_key` lowercases, collapses whitespace, drops middle names and suffixes, then joins first token + last token.
2. **Email** — `AMZL.Email` (lowercased) vs `Uzio.Personal Email` (lowercased).
3. **Phone** — last 10 digits of either AMZL phone vs last 10 digits of Uzio phone. Phone match is only used when name and email both miss, and only when exactly one Uzio row has that phone (multi-candidate phone matches are skipped and flagged).
4. **Manual override** — `--merge AMZL_TID=uzio_personal_email` for cases where automated matching fails but the operator has confirmed the two records are the same person (e.g., name on AMZL is the legal name but Uzio has a nickname/initial form).

### Field source-of-truth rules (for matched rows)

| Hera field | Source |
|---|---|
| Status | AMZL (`ACTIVE` → `Active`, `INACTIVE` → `Inactive` and flag) |
| First Name / Last Name | Uzio (with Suffix appended to Last Name) |
| Hera Display Name | **Left blank** — Hera generates this in-app. |
| Transporter ID | AMZL |
| Email | **AMZL** (company-issued). Fall back to HRIS personal if AMZL blank. Mismatches noted but AMZL wins by default. |
| Phone | AMZL Personal > AMZL Work (flag fallback) > Uzio (flag fallback) |
| Hire Date | Uzio |
| Authorized To Drive | AMZL Qualifications mapped |
| DL Expiration | AMZL `ID expiration`, MM/DD/YYYY |
| Gender | HRIS when populated — **always carry through, do not blank**. ADP yes when populated; Uzio no. |
| DOB | HRIS when populated — **always carry through, do not blank**. ADP yes; Uzio no (Uzio Birthday lacks the year). |
| Pronouns / Gas Card PIN / MVR / Hourly Status | blank |

### Manual merge overrides

When two records are clearly the same person but normal matching can't connect them (e.g., AMZL has legal name `Susie Kandi Hall`, Uzio has nickname-style `S Kandi`), use the `--merge` CLI argument:

```
--merge "AMZL_TID=uzio_personal_email"
```

The override binds the AMZL row (by Transporter ID) to the Uzio row (looked up by Personal Email). When this fires:

- Uzio email and Hire Date are still pulled in (per source-of-truth rules above).
- First/Last/Display Name are taken from the **AMZL parsed name** (the override is generally used because AMZL has the more complete legal name).

---

## Pre-import validation checklist (Staff)

Run every time before handing the converted file to the customer or to the import tool:

1. **Row count** — Hera output row count equals AMZL row count (every AMZL row imports). HRIS-only rows are skipped and listed separately.
2. **Transporter ID uniqueness** — no duplicates across rows.
3. **Required fields populated** — Status, First Name, Last Name, Transporter ID, Authorized To Drive, DL Expiration. Hire Date is allowed to be blank for AMZL-only rows.
4. **Date format** — all dates `MM/DD/YYYY`.
5. **Email mismatch flags** — list every matched associate whose AMZL email differs from their HRIS personal email (AMZL wins in the output by default; HRIS personal noted alongside for reference).
6. **Status flags** — list every associate set to `Inactive` (from AMZL `INACTIVE`).
7. **Phone fallback flags** — list every associate whose Phone fell back to AMZL Work or to Uzio.
8. **Blank Authorized To Drive** — list every associate whose Qualifications produced no Hera vehicle types after exclusions (e.g., helper-only).
9. **AMZL-only rows** — list every AMZL row that had no HRIS match (these still import, but with blank Hire Date and parsed name from AMZL).

## Conversion script

A reusable converter is checked in at [staff-amazon-dsp-convert.py](staff-amazon-dsp-convert.py). Usage:

```bash
python3 knowledge/onboarding/staff-amazon-dsp-convert.py \
  --amzl   "/path/to/AssociateData.csv" \
  --hris   "/path/to/Employee Roster.xlsx"           # Uzio xlsx, or ADP "Hera Staff Report.csv"
  --hris-format adp                                  # optional; auto-detected from extension + headers
  --output "/Users/johnjm/Library/CloudStorage/GoogleDrive-john@hera_app/Shared drives/Imports/Tenants/<Company Name>/<Company Name> - Staff.csv" \
  --merge  "AMZL_TID=hris_personal_email"            # optional, repeatable
```

The script prints per-row flags (email mismatches, Inactive rows, phone fallbacks, AMZL-only rows, manual merges) and exits non-zero on any validation failure (duplicate TIDs, missing required fields).
