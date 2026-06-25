# Adept Delivery Solutions LLC — Pre-Import Notes

**Generated:** 2026-05-28
**Source files (customer-provided):**

- `AssociateData.csv` — Amazon AMZL Associates export (master roster)
- `Hera Staff Import.csv` — ADP HRIS export
- `VehiclesData.xlsx` — Amazon DSP vehicle export

**Output files (Google Drive `Imports/Tenants/Adept Delivery Solutions LLC/`):**

- `Adept Delivery Solutions LLC - Staff.csv`
- `Adept Delivery Solutions LLC - Vehicles.csv`

All conversion findings have been resolved with the operator before these files were saved. The resolutions are recorded below alongside each finding so the import team has full context.

---

## Staff — high-level

- **AMZL rows:** 160 (113 Active, 47 Inactive)
- **ADP rows (raw):** 113 (no dedup needed — no duplicate emails in this export)
- **Output rows:** 160 (AMZL is master; every AMZL row becomes a Hera Staff row)
- **DOB populated:** 0 (blanked per operator decision — customer not tracking DOB)
- **Gender populated:** 0 (ADP export does not include `Gender for Compliance Reporting` column)
- **Validation:** All checks passed.

---

## Staff — resolutions

### 1. DOB tracking — RESOLVED (blank the column)
**Finding:** DOB populated for 104 drivers from ADP. Template marks DOB as optional and only to collect if customer actively tracks it.
**Decision:** Blank the DOB column for all rows. Adept is not tracking DOB in Hera.

### 2. HRIS-only people (9) — RESOLVED (skip per locked rule)
**Finding:** 9 people in ADP but not in AMZL. Per the locked join rule they aren't drivers per Amazon's roster, so they're skipped.
**Decision:** Confirmed — AMZL is the source of truth. Skip all 9. Listed below for reference only.

| Name | Personal Email | Phone |
|---|---|---|
| Adrian Enriquez | aenriquez@adeptdsda.com | 7274037994 |
| Angel Rodriguez | angelrod@adeptdsda.com | 8134958309 |
| Ivana Blanco | adept@amngtpro.com | 8134003406 |
| Jorge Rivera Henao | jrivera@adeptdsda.com | 7812681497 |
| Lester Martinez Munoz | lemartinez@adeptdsda.com | 7865666751 |
| Management Profile | aopz@lastmilesupport.com | 6505144995 |
| Rafael Chavez Martinez | rafaelc@adeptdsda.com | 4079849216 |
| Ricardo Rodriguez Espinosa | ricardore@adeptdsda.com | 7868229265 |
| Valter Domingos Da Silva | v.domingos@adeptdsda.com | 6562125457 |

### 3. AMZL-only drivers (35) — RESOLVED (import all as-is)
**Finding:** 35 AMZL rows had no ADP match. They import with parsed First/Last from AMZL, AMZL email, blank Hire Date, blank DOB. 11 Active, 24 Inactive.
**Decision:** Follow the locked rule — AMZL is master, import all. Hire Date stays blank on these rows; customer can backfill in Hera if desired.

**Active AMZL-only (11):** Elinor Evans, Gjergj Rrogomi, Jenny Valladares, Jeremy Jackson, Jurgen Ndreu, Maikel Cancio, Manuel Sanchez, Sandra Cepeda, Torrance Townsend, Tyler Johnson, Yilber Preciado.

**Inactive AMZL-only (24):** Abdiel Cruz, Alejandro Garcia, Amanda Hernandez, Andrew Pascual, Anthony Jordan, Antwoin Mccuin, Ashley Roberts, Breana OBrien, Bryan Biggs, Burshonna Lockwood, Daniel Cruz, Daniel Bushey, Daniel Runyon, David Holmes, Dominic Carrasco, Dominick Gianino, Donivan Green, Emilio Libera, Giordany Proenza, Henry Nunez, JACOB BUTLER, jakira thomas, Jonathan Garcia, Joseph Turcios, Kamiya Randall, Keenon Grafton, Keithon Flintroy, keven paulino, Kirill Marshalov, Ladarious Jackson, Leonardo Apaulaza, Luis Ayala, Lyndsey Watson, Malachi Walker, Neil Blalock, Nekaisia Robinson, Nykisha Macon, Rayfredo Garcia, Sandra Vega, Tajmiere Dowe, Tyler Waller, Wilmer Navarroojeda, Yully Calderereo.

### 4. Email mismatches (3) — RESOLVED (ADP wins, locked default)
**Finding:** 3 drivers had different emails in ADP vs AMZL.
**Decision:** Apply locked default — ADP (HRIS) wins. Drivers will receive Hera communications at their ADP personal email.

| Driver | Email in Hera (ADP) | AMZL email (not used) |
|---|---|---|
| Alan Sheehan | sheehan.m.alan@gmail.com | a.sheehan.aopz@gmail.com |
| Jacob Torres | jacob.torres@adeptds.com | jacob.torres2@adeptds.com |
| Milagro Lobo Lobo | Milagrolobo514@gmail.com | mlobo@adeptdsda.com |

### 5. Phone-only match (1) — RESOLVED (accepted)
**Finding:** Angel De la Rosa matched ADP↔AMZL by phone only. ADP row had a blank Personal Email so name/email match couldn't run.
**Decision:** Accepted — same person. AMZL "Angel Roberto De La Rosa Leiva" and ADP "Angel De la Rosa", both phone (813) 860-1115.

### 6. Blank Authorized To Drive (3 Active drivers) — RESOLVED (leave blank)
**Finding:** Three Active AMZL rows had no qualifications at all.
**Decision:** Leave blank. Customer can add driver authorization in-app post-import; no need to reconfirm before import.

| Driver | TID |
|---|---|
| Alan Sheehan | A3T5QGSI2TBXRJ |
| Caleb Chaviano | A1NO9BJYQKCOUV |
| Elinor Evans | AHHJCBM73Y5IH |

### 7. Inactive bucket — RESOLVED (keep `Inactive - Misc`)
**Finding:** 47 AMZL `INACTIVE` rows land in Hera as `Inactive - Misc`.
**Decision:** Keep the documented default. Customer can re-classify in Hera later if they prefer Terminated, On Leave, etc.

---

## Vehicles — high-level

- **Source rows:** 45
- **Output rows:** 45
- **Status:** 45 Active
- **Vehicle Types:** 38 EDV, 6 Standard Parcel XL, 1 Standard Parcel Large
- **Ownership:** 39 Lease (38 AMAZON_OWNED + 1 AMAZON_RENTAL), 6 Rent (RENTAL)
- **Providers:** 28 Lease Plan (LP), 11 Element, 4 Hertz, 2 Enterprise
- **Validation:** All checks passed.

---

## Vehicles — resolutions

### 8. Unknown State on EDV 38 — RESOLVED (blank the State field)
**Finding:** One vehicle (EDV 38, VIN 7FCEHEB27TN043407, plate 15740A34, Rivian EDV 700 2026) had `registeredState = "UNKO - Unknown"` in the Amazon export.
**Decision:** Blank the State field on import. Customer can update once they confirm the registration state. (Other Adept vehicles register in FL (34), AZ (9), and OR (1) — likely FL based on cluster, but not assumed.)

### 9. Providers — INFORMATIONAL
All four providers (Lease Plan, Element, Hertz, Enterprise) are already in Hera's documented allowed-list. No new provider strings introduced.

### 10. Fields not in the Amazon export — INFORMATIONAL
Mileage, Gas Card (Last 6), Parking Space, Description, and Rent Agreement Number are not provided by Amazon. They import blank. If Adept wants to track any of these in Hera, request the data separately.

---

## No converter/mapping updates required by this run

Conversion ran cleanly against the existing locked converters and mapping docs. No schema drift from Amazon or ADP. No new vendor strings to add. The blank-state behavior on a single UNKO vehicle is handled by a manual post-conversion edit rather than a converter change — too rare to be worth a code path.
