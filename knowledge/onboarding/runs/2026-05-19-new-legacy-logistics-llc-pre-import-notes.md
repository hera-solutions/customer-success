# New Legacy Logistics LLC — Pre-Import Notes

**Generated:** 2026-05-19
**Source files (customer-provided):**

- `AssociateData (10).csv` — Amazon AMZL Associates export (master roster)
- `Hera Staff Report.csv` — ADP HRIS export
- `VehiclesData (3).xlsx` — Amazon DSP vehicle export

**Output files (this folder):**

- `New Legacy Logistics LLC - Staff.csv`
- `New Legacy Logistics LLC - Vehicles.csv`

All conversion findings have been resolved with the operator before these files were saved. The resolutions are recorded below alongside each finding so the import team has full context.

---

## Staff — high-level

- **AMZL rows:** 145 (123 Active, 22 Inactive)
- **ADP rows after dedup:** 138 (raw 155, 17 duplicates removed — ADP returned the same person twice for 16 emails, differing only in Home Phone)
- **Output rows:** 145 (AMZL is master; every AMZL row becomes a Hera Staff row)
- **DOB populated:** 125 / 145
- **Gender populated:** 0 (ADP `Gender for Compliance Reporting` blank for every row)
- **Validation:** All checks passed.

---

## Staff — resolutions

### 1. DOB tracking — RESOLVED (keep populated)
**Finding:** DOB populated for 125 drivers from ADP. Per Hera template, DOB is optional and only collected if the customer actively tracks it.
**Decision:** Keep DOB populated in the import. 125 drivers will have DOB on their Hera profile.

### 2. Blank Authorized To Drive (3 drivers) — RESOLVED (leave blank)
**Finding:** Three AMZL rows had no qualifications at all (Kayla McCormick — Inactive, Rebecca Hoover — Active, Shayla Ward — Active). Authorized To Drive is empty for them.
**Decision:** Leave Authorized To Drive blank for all three. They will import with an empty driver-authorization list and can be updated in-app if needed. The converter no longer treats this as a hard validation fail.

### 3. AMZL-only drivers (20) — RESOLVED (import all as-is)
**Finding:** 20 AMZL rows have no ADP match. They import with parsed First/Last from AMZL, AMZL email, blank Hire Date, blank DOB. Three are Active (Brian Dowdy, LaQuonn Mayes, Terrell Gardner); 17 are Inactive.
**Decision:** Follow the locked rule — AMZL is master, import all 20. Hire Date and DOB stay blank on these rows; customer can backfill in Hera if desired.

### 4. ADP-only people (13) — RESOLVED (skip per doc)
**Finding:** 13 people in ADP but not in AMZL. Per the locked join rule they aren't drivers per Amazon's roster, so they're skipped.
**Decision:** Confirmed — leave them out of the Hera Staff import. Listed below for reference only.

| Name | Personal Email | Phone |
|---|---|---|
| Alexandria Riley | arileynlwz@gmail.com | 6623211260 |
| Andre Avery | averynwlz@gmail.com | 6625540880 |
| Austin Young | nwlzyoung@gmail.com | 6625965633 |
| Christopher Bernier | berniernwlz@gmail.com | 6627601410 |
| Daniel Bishop | bishopnwlz@gmail.com | 6625388848 |
| Diana Delgado | delgadonwlz@gmail.com | 8328655323 |
| Jordan Kimble | jordankimble22@icloud.com | 6627903666 |
| Joshua Decanter | nwlzjoshua@gmail.com | 6625388842 |
| Kendra Rodriguez | kendranwlz@gmail.com | 2819875160 |
| Kylieanna Zepernick | kylienwlz@gmail.com | 6624913710 |
| Tamara Richardson | tamararnwlz@gmail.com | 7318033609 |
| Victoria Allen | victorianwlz@gmail.com | 6627508673 |
| Zachary Barnett | barnettnwlz@gmail.com | 6627062201 |

### 5. Email mismatches (11) — RESOLVED (ADP wins)
**Finding:** 11 drivers had different emails in ADP vs AMZL.
**Decision:** Apply the locked default — ADP (HRIS) wins. Drivers will receive Hera communications at their ADP personal email.

| Driver | Email in Hera (ADP) | AMZL email (not used) |
|---|---|---|
| Altonio Kennedy | altoniokennedy99@icloud.com | altonionwlz@gmail.com |
| Azalee Staples | azaleestaples7@gmail.com | azaleenwlz@gmail.com |
| David Wilson | frankie.wlsn@icloud.com | nwlzwilson@gmail.com |
| Destoni Fields | Destonifields2121@gmail.com | nwlzfields@gmail.com |
| Ethan Farley | ethanfarley483@gmail.com | nwlzethan@gmail.com |
| Giovanni Locastro | giolocastro95@gmail.com | locastronwlz@gmail.com |
| Khalil McGlaun | kamcglaun@gmail.com | nwlzkhalil@gmail.com |
| Precious Barton | Preciousbarton09@gmail.com | moenwlz@gmail.com |
| Ramoun Shumpert | Shumpertramoun@gmail.com | nwlzramoun@gmail.com |
| Skylar Medcalf | medcalfskylar2001@icloud.com | medcalfnwlz@gmail.com |
| Taisha Hendrix | Tdhendrix24@gmail.com | taishanwlz@gmail.com |

### 6. Name spelling differences — RESOLVED (use AMZL spelling)
**Finding:** Two drivers had slightly different names between AMZL and ADP.
**Decision:** Use AMZL spelling for both (overridden via `--merge` flags so the output matches AMZL).

| Hera (AMZL spelling, used) | ADP (not used) |
|---|---|
| Giovanni Washington | Giovanni Washinton |
| JJ McAlister | JJ McAllister |

### 7. Inactive bucket — RESOLVED (keep `Inactive - Misc`)
**Finding:** 22 AMZL `INACTIVE` rows land in Hera as `Inactive - Misc`.
**Decision:** Keep the documented default. Customer can re-classify in Hera later if they prefer Terminated, On Leave, etc.

---

## Vehicles — high-level

- **Source rows:** 75
- **Output rows:** 75
- **Validation:** All checks passed.

---

## Vehicles — resolutions

### 8. Box trucks → 10,000lbs Van — RESOLVED (confirmed)
**Finding:** 2 box trucks (Hino L6, Freightliner M2 106) come through Amazon as `Box Truck Parcel (Large)` / `BOX_TRUCK_LARGE`. Hera's closest taxonomy match is `10,000lbs Van`.
**Decision:** Confirmed — map both to `10,000lbs Van`. Locked into the vehicles mapping doc for future runs.

### 9. Vehicle Type fallback (5 vehicles) — INFORMATIONAL
For these rows `serviceType` was blank, so the converter mapped from `serviceTier`. Same end result, flagging so the import team knows we categorized on the customer's behalf:

| Row | VIN | serviceTier → Hera Vehicle Type |
|---|---|---|
| 15 | 1FTBR1C87SKB06331 | LARGE_CARGO_VAN → Standard Parcel Large |
| 30 | 1FTBR1C87SKA88316 | LARGE_CARGO_VAN → Standard Parcel Large |
| 34 | 1FTBR1C89SKA88253 | LARGE_CARGO_VAN → Standard Parcel Large |
| 46 | 1FTBR1C89SKA56922 | LARGE_CARGO_VAN → Standard Parcel Large |
| 68 | 1FTBR1C86SKB05574 | LARGE_CARGO_VAN → Standard Parcel Large |

### 10. New providers — INFORMATIONAL
- **Kingbee** (9 vehicles) — not in Hera's documented allowed-list. Passes through as `Kingbee` in the import; Hera engineering should add it to the picker. Does not block the import.
- **Zeeba** (25 vehicles) and **Merchants Fleet** (17 vehicles, source `MERCHANTS`) — already in Hera's allowed list.

### 11. Fields not in the Amazon export — INFORMATIONAL
Mileage, Gas Card (Last 6), Parking Space, Description, and Rent Agreement Number are not provided by Amazon. They import blank. If New Legacy wants to track any of these in Hera, request the data separately.

---

## Converter / mapping updates locked in by this run

These changes are committed to the repo so the next customer with similar data converts cleanly:

- **Staff converter** now supports ADP CSVs (auto-detected by extension + headers), dedupes ADP duplicate-email rows, and excludes the `DOT` qualification (analogous to LIFTGATE — certification, not a vehicle type).
- **Staff mapping doc** has a full LOCKED ADP section.
- **Staff validator** no longer hard-fails on blank Authorized To Drive / blank DL Expiration — they remain flags but don't block the import.
- **Vehicles converter / mapping** locks in: `ownershipType=LEASE → Lease`, `Box Truck Parcel (Large)` / `BOX_TRUCK_LARGE → 10,000lbs Van`, and providers `MERCHANTS → Merchants Fleet`, `Zeeba`, `Kingbee` (passthrough).
