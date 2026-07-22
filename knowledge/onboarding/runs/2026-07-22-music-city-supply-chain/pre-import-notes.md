# Music City Supply Chain — Pre-Import Notes

**Date:** 2026-07-22
**Prepared by:** John (customer success)
**Source folder:** `Shared drives/Imports/Tenants/Music City Supply Chain`
**Outputs:** `Music City Supply Chain - Staff.csv`, `Music City Supply Chain - Vehicles.csv` (this folder)

## What these source files actually are

This customer did **not** send raw ADP/AMZL/DSP exports. Both files were already filled into
(roughly) the Hera template shape by the customer, then exported to CSV. That means this was a
**cleanup and validation pass**, not the usual mapping conversion. The two source files:

- `Associates - Music City.csv` — 215 staff rows, in the Hera Staff template layout.
- `Vehicles -Music City.csv` — 42 vehicle rows, in the Hera Vehicles template layout.

There is **no Devices file** and **no HRIS export** in the folder. If devices (phones) are in scope
for this customer, we still need that file.

The cleaned output CSVs keep the exact header lines from the source files (those are the live Hera
template headers with the allowed-value annotations), so the importer will still match its columns.
Only the data rows were cleaned. The reusable script is `clean_music_city.py` in this folder.

## Cleanup applied (data only)

- **Excel serial dates → MM/DD/YYYY.** The single biggest issue. Hired Date, DOB, and DL Expiration
  each contained a mix of Excel serial numbers (e.g., `45418`, `28372`, `47370`) and already-formatted
  `MM/DD/YYYY` values in the same column. **190 serial values** were converted (Excel 1900 date system,
  base 1899-12-30). Verified against known rows: Allen David Fitzpatrick hire `45418` → `05/06/2024`,
  DL `47370` → `09/09/2029`; Andre Peete DOB `28372` → `09/04/1977`.
- **Garbage dates blanked.** `0` and `00/01/1900` placeholder values → blank. **48 values** blanked
  across ~24 (all inactive) associates.
- **Phone → 10 digits.** Stripped formatting; `0`/empty → blank.
- **Names trimmed.** Leading spaces and internal double-spaces collapsed (e.g., ` Barbara Morales`
  → `Barbara Morales`, `Jonathan  Edwards` → `Jonathan Edwards`).
- **Authorized to Drive trimmed.** Trailing `;` removed.
- **Vehicle Type trimmed.** `Standard Parcel ` (trailing space) → `Standard Parcel`.
- **Company case-normalized** to the allowed list (`ELEMENT` → `Element`). Values not in the allowed
  list were left as-is and flagged (see below).

## Status taxonomy note (needs confirmation)

The Staff file's Status column uses a more granular taxonomy than what `import-templates.md`
documents. Allowed values in this template's header: `Active`, `Inactive - Misc - Misc`,
`Inactive - Misc - Medical Leave`, `Inactive - Misc - Terminated`,
`Inactive - Misc - Personal Time/Vacation`, `Onboarding`. Every inactive row in the file uses
`Inactive - Misc - Misc`. Our documented convention is the shorter `Inactive - Misc`. **I left the
values as the customer/template has them** rather than rewriting to the documented form. Confirm the
importer accepts `Inactive - Misc - Misc`; if it expects `Inactive - Misc`, this is a one-line change.

## Staff flags (215 rows: 72 Active, 143 Inactive)

1. **Missing Transporter ID — 7 rows (required field).** All inactive. Cesar Cano, Eleeza Jones,
   James Pratt, Kameron Coleman, Morgan Harrison, Terrance Johnson, Tony Hockett. These may fail
   import or import without the Amazon UID. Decision needed: drop them, or import with blank TID.
2. **Same person appears in multiple rows with different Transporter IDs — 14 clusters.** These are
   duplicate/stale Amazon accounts (e.g., Jacquelyne Turner ×5 total across the file, Malcolm
   Townsend ×3, Santiago Mcklean ×3). All are inactive. No duplicate TIDs exist, so they will all
   import as separate staff records unless we prune. Recommend pruning to one record per person
   before import to avoid a cluttered roster, but that is a customer call.
3. **Active with NO Authorized-to-Drive — 2.** Andre Peete and Brian William Fitzpatrick are Active
   but have no vehicle-type qualifications. They will import but won't be assignable to routes.
   Confirm whether they are drivers.
4. **Active with NO DL Expiration — 1.** Andre Peete. DL Expiration is required for drivers.
5. **Blank phone — 74 rows** (almost all inactive). No active driver is missing a phone except where
   noted; the bulk are terminated/stale accounts.
6. **Blank email — 0.** Every row has an email.
7. **Under-18-at-hire — 0.** No age red flags.

## Vehicle flags (42 rows: 33 Active, 9 Inactive - Grounded)

1. **Company not in the allowed list — 5 rows.** Three "Agility" vans list Company `Other`
   (VAN 31, VAN 33, VAN 34) and two owned vans list `LP` (Van 24, Van 26). `LP` is almost certainly
   **Lease Plan** — confirm and I'll map it. `Other` needs a real leasing company or should be blank
   for owned vehicles. I did **not** guess these.
2. **Blank mileage — all 42 rows (required field).** The customer provided no odometer readings.
   Either collect them or confirm the importer accepts blank mileage at onboarding.
3. **Lease/Rent with blank plate expiration — 20 rows.** All the Enterprise/Agility rentals. Normal
   for rentals (plates ride with the rental agreement), but the template marks License Plate
   Expiration required. Confirm blank is acceptable for rented units.
4. **VINs:** all 42 are valid 17-char, **no duplicates**. Plates: **no duplicates**. Clean.
5. **Rent Agreement Number — blank on all rented units.** Not collected. Low priority.

## Recommended next steps

1. Confirm the Status taxonomy question with whoever owns the import tool (blocks nothing, but avoids
   a re-import).
2. Get a decision on the 7 missing-TID rows and the 14 duplicate-person clusters (prune vs. import
   as-is). This is the main thing standing between "clean" and "final."
3. Ask the customer for: vehicle mileage, `LP`/`Other` company clarification, and a Devices file if
   phones are in scope.
4. Once 1–3 are resolved, upload the two cleaned CSVs to the customer's Drive Tenants folder and run
   the import.
