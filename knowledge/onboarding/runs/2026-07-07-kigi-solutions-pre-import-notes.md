# KiGi Solutions — Pre-Import Notes

**Generated:** 2026-07-07
**Source files (customer-provided):**

- `AssociateData-6` — Amazon AMZL Associates export (master roster)
- `20260706132244_Advanced_Report_Writer_b3adb317.csv` — Paycom HRIS export ("Advanced Report Writer")
- `VehiclesData.xlsx` — Amazon DSP vehicle export

**Output files (Google Drive `Imports/Tenants/KiGi Solutions/`):**

- `KiGi Solutions - Staff.csv`
- `KiGi Solutions - Vehicles.csv`

This is the first Hera import for a customer whose HRIS is **Paycom**. Two things came out of it that now apply to every future import:

1. **Paycom is a locked HRIS format** — the converter now supports Paycom Advanced Report Writer exports alongside Uzio and ADP. Mapping is documented in [staff-import-mapping.md](../staff-import-mapping.md#paycom--advanced-report-writer-locked).
2. **The AMZL-wins email rule is now baked into the converter** — up to this run the 2026-06-05 rule change lived only in the docs and required a post-conversion manual override (as noted at the bottom of the Precise pre-import notes). The converter has been updated so no manual patching is needed anymore.

---

## Staff — high-level

- **AMZL rows:** 35 (all Active — no Inactive drivers in the AMZL export)
- **Paycom rows (raw / deduped):** 38 / 38
- **Output rows:** 35 (AMZL is master; every AMZL row becomes a Hera Staff row)
- **Matched HRIS↔AMZL:** 31 (name 29, email 1, phone 1)
- **AMZL-only imported:** 4 (Hire Date + DOB stay blank)
- **HRIS-only skipped:** 7 (not on the AMZL roster — see resolution 2)
- **Email populated:** 35 of 35
- **DOB populated:** 31 of 35 (only AMZL-only rows have blank DOB)
- **Gender populated:** 0 of 35 (Paycom Advanced Report Writer template does not include gender)
- **Validation:** All checks passed.

---

## Staff — resolutions

### 1. Paycom format newly supported — INFORMATIONAL

**Finding:** The HRIS export is Paycom, which the docs previously listed as TBD.
**Decision:** Added a Paycom loader to the converter and locked the mapping. Column set matched the expected Paycom schema exactly, so the mapping went straight from spec to locked without any surprises. Names arrive ALL CAPS from Paycom and are title-cased on load (with Mc / Mac / hyphen handling for names like `MCCORMACK` → `McCormack`, `NELSON-LILLARD` → `Nelson-Lillard`). Spot-checked in the output — all names look correct.

### 2. HRIS-only people (7) — RESOLVED (skip per locked rule)

**Finding:** 7 people appear in Paycom but not in AMZL. Per the locked join rule they aren't drivers on Amazon's roster, so they're skipped.
**Decision:** Skip all 7. Listed below for reference.

| Name | Hire Date | Personal Email | Phone |
|---|---|---|---|
| Kikelomo Olukoya | 06/01/2026 | princesskike@icloud.com | (217) 974-1311 |
| Jamarcus English | 06/04/2026 | jamarcuse01@gmail.com | (312) 636-5158 |
| Ashley Lewis | 06/02/2026 | ashleylewis9723@att.net | (217) 799-0815 |
| Lucas Fawbush | 06/04/2026 | LFawbush91@outlook.com | (217) 685-1684 |
| Kaylee Jones | 06/04/2026 | kayleejo030805@gmail.com | (217) 305-8278 |
| Jarrett Kerkes | 06/04/2026 | kerkesjarett@outlook.com | (217) 766-2935 |
| Mayowa Olukoya | 06/15/2026 | mayo.olukoya@gmail.com | (316) 213-0502 |

Note for KiGi: all 7 have June 2026 hire dates and may simply not be on AMZL yet. If any of them are active drivers who should be, send us their AMZL Transporter IDs and we can add them.

### 3. Kikelomo Olukoya DOB — FLAG FOR KIGI

**Finding:** Kikelomo Olukoya's Paycom DOB is `08/21/2008` and Hire Date is `06/01/2026`, which would make her 17 at hire. She is HRIS-only and does not import into Hera on this pass, so it doesn't affect the file we're loading. But it's worth flagging to KiGi so they can verify the DOB on their end.
**Decision:** No action required for this import. Send KiGi a note to double-check their Paycom record.

### 4. AMZL-only drivers (4) — RESOLVED (import all as-is)

**Finding:** 4 AMZL rows had no Paycom match. All 4 are Active. They import with parsed First/Last from AMZL, AMZL email, AMZL phone, blank Hire Date, blank DOB. All 4 have valid driver qualifications.
**Decision:** Follow the locked rule — import all. Hire Date stays blank; KiGi can backfill in Hera if they want.

| Driver | TID | AMZL Email | Notes |
|---|---|---|---|
| Julio Fabela | A12QEFMADWTHDM | julio.fabela-kigi@outlook.com | CDV + Standard Parcel |
| Justin Randle | A1K3OA775SRAT | justin.randle.kigi@gmail.com | Standard Parcel |
| KiMaya Young | AETYD3R9V98RY | kimaya.young.kigi@gmail.com | Standard Parcel |
| Maddux Pumphrey | A12UEF8LOI96EQ | maddux.pumphrey.kigi@gmail.com | Standard Parcel |

**Flag for KiGi:** These 4 are on AMZL but not in Paycom. Confirm they're actually employed (not stale AMZL records), and if they are, get them into Paycom so Hire Date and DOB get filled in on the next sync.

### 5. Email mismatches (24) — RESOLVED (AMZL email wins by rule)

**Finding:** 24 of the 31 matched drivers have different emails in Paycom vs AMZL. AMZL emails follow KiGi's `<firstname>.<lastname>-kigi@outlook.com` / `-kigi@proton.me` / `.kigi@gmail.com` company-issued patterns; Paycom holds personal addresses.
**Decision:** AMZL wins — this is now the built-in default in the converter. No manual patching needed for future runs.

| Driver | Hera Email (AMZL) | Personal email on file (Paycom, not imported) |
|---|---|---|
| Aishia Mitchell | aishia.mitchell-kigi@proton.me | mitchellaishia2@gmail.com |
| Aliya Wright | aliyawright-kigi@outlook.com | aliyawright10@gmail.com |
| Alize Tibbs-Goodwin | alize.tibbsgoodwin-kigi@outlook.com | amtg17@yahoo.com |
| Andrew Brown | andrew.brownkigi@outlook.com | andrewjbrown3244@gmail.com |
| Austin Radmaker | austin.radmaker.kigi@gmail.com | austinradmaker1@yahoo.com |
| Breonna Gardner | breonna.gardner-kigi@proton.me | Gardnerbre9@gmail.com |
| Connor McCormack | connor.mccormack-kigi@outlook.com | connormccormack00@gmail.com |
| David Rodriguez | david.rodriguez.kigi@gmail.com | drodriguez3138@gmail.com |
| Devin Hathaway | devhathaway91@outlook.com | Devhath91@gmail.com |
| Guillermo Espinosa Arzeta | guillermo.espinosa-kigi@outlook.com | gaespinosa02@gmail.com |
| Jalen Lee | jalen.lee.kigi@gmail.com | jmac2349@gmail.com |
| Jose Cortez | cortejose556@outlook.com | cortejose556@gmail.com |
| Joseph Kern | jkern.cygz@gmail.com | jkern7414@gmail.com |
| Justin Hornickel | justin.hornickel.kigi@gmail.com | justhornick@gmail.com |
| Kaelyn Shaffer | kaelynshaffer17@gmail.com | kaelynshaffer@yahoo.com |
| Kassandra Gower | kassandra.gower-kigi@proton.me | lesanjruh@yahoo.com |
| Kayla Jordan | kayla.jordan-kigi@outlook.com | kaylajordan96@icloud.com |
| Marshaun Turner | marshaun.turner.kigi@gmail.com | marshaunturner95@gmail.com |
| Nylajah Thatch | nylajah.thatch-kigi@proton.me | nylajahbailey@yahoo.com |
| Parker Claypool | claypoolpwil4@gmail.com | parkerclaypool90@gmail.com |
| Raimone Allen | raimone.allen-kigi@proton.me | tee81054@gmail.com |
| Toiniyah Craig | toiniyah.craig-kigi@outlook.com | teewopster12@gmail.com |
| Tyler Tolbert | tyler.tolbert-kigi@outlook.com | tylertolbert259@gmail.com |
| Auzhay Nelson-Lillard | auzhay.lillard-kigi@outlook.com | — (matched by email; AMZL email `auzhay.lillard-kigi@outlook.com` is identical to Paycom `auzhay.lillard-kigi@outlook.com`, no mismatch to flag) |

### 6. Phone-only match — Alize Tibbs-Goodwin — RESOLVED (accepted)

**Finding:** Alize matched Paycom ↔ AMZL by phone only. AMZL has her as `Alize  Monique Tibbs Goodwin` (Monique middle name + space-separated last name → name key parses as `alize goodwin`). Paycom has `ALIZE TIBBS-GOODWIN` (hyphenated → key `alize tibbs-goodwin`). Emails also differ. Phone `(872) 444-0227` matched on both sides.
**Decision:** Accepted — same person. DL expiration, DOB, hire date, and driver auth all carry through from the correct source per the mapping rules.

### 7. Email-based match — Auzhay Nelson-Lillard — INFORMATIONAL

**Finding:** Auzhay matched by email rather than name because AMZL spells the surname `Nelson lillard` (space, lowercase L) and Paycom spells it `NELSON-LILLARD`. Both emails are `auzhay.lillard-kigi@outlook.com`, so the match is unambiguous.
**Decision:** Accepted. Hera output uses the Paycom (title-cased) spelling `Nelson-Lillard`.

### 8. Andrew Brown DL expiration — FLAG FOR KIGI

**Finding:** Andrew Brown's DL Expiration from AMZL is `06/21/2026` — expired 16 days before this import.
**Decision:** Import the expired date as-is. Ask KiGi to renew Andrew's license in AMZL and re-sync, or update the expiration directly in Hera.

Also worth watching:

- Jose Cortez — expires `08/24/2026` (about 7 weeks out).
- Joseph Kern — expires `03/06/2027`.

Nothing else in the roster is inside the 90-day-out window.

### 9. Julio Fabela — no work phone (AMZL only had personal) — INFORMATIONAL

**Finding:** Julio Fabela's AMZL row lists a personal phone but no work phone. Since AMZL personal was populated, the converter used it without falling back. No pre-import flag beyond mentioning it for transparency.
**Decision:** No action.

### 10. Inactive bucket — N/A this run

**Finding:** Every AMZL row for KiGi is `ACTIVE`. No `Inactive - Misc` rows in the output.
**Decision:** N/A.

---

## Vehicles — high-level

- **Source rows:** 16
- **Output rows:** 16
- **Status:** All 16 Active (all AMZL `ACTIVE + OPERATIONAL`)
- **Ownership:** All 16 Rent (no Amazon-owned, no self-owned)
- **Vehicle Types:** 13 Standard Parcel XL, 1 Standard Parcel Large, 2 Standard Parcel Small (no Rivians, no CDVs, no box trucks)
- **Makes:** Ram 7, GMC 4, Mercedes-Benz 2, Freightliner 1, Ford 1, Chevrolet 1
- **Providers:** Ryder 6, U-Haul 6, Budget 4
- **States:** AZ 6, IL 5, OK 4, WI 1
- **Validation:** All checks passed.

---

## Vehicles — resolutions

### 11. All 16 vehicles have blank Vehicle Name — RESOLVED (import blank)

**Finding:** Amazon didn't provide `vehicleName` on any of the 16 rows. Hera accepts this and drivers still get to work — Vehicle Name is a nice-to-have for the DSP's own labeling (unit number, etc.).
**Decision:** Import blank. Ask KiGi if they use internal unit numbers; if yes, they can add them in Hera post-import or send us a list.

### 12. Ryder is a new provider (6 rentals) — RESOLVED (add to allowed list)

**Finding:** 6 vehicles came from Amazon with `vehicleProvider = "Ryder"`. Ryder is not in Hera's currently-documented allowed Company list. Same class of finding as U-Haul and Kingbee in earlier imports.
**Decision:** Import as `Ryder` (matches U-Haul/Kingbee handling). Hera will add Ryder to the allowed list. Mapping doc updated so future imports don't re-flag this.

VINs for reference: W2Y4DCHY5MT058349, W1Y5DBHY2NT088146, 3C6LRVDG1RE155059, 3C6LRVDG1RE155093, 3C6LRVDG5RE104888, W1Y4KCHY2PT130387.

### 13. 3 vehicles used serviceTier fallback — INFORMATIONAL

**Finding:** 3 rentals had no Amazon `serviceType` and were categorized via `serviceTier = EXTRA_LARGE_CARGO_VAN` → Hera `Standard Parcel XL`.
**Decision:** No action — categorization is unambiguous from serviceTier.

VINs: 3C6LRVDG7SE537263, 3C6LRVDGXRE132606, 3C6MRVJG0PE554809 (all Ram ProMaster).

### 14. 12 rentals with no License Plate Expiration — INFORMATIONAL

**Finding:** Amazon's export doesn't capture registration expiry on the Ryder (6) or U-Haul (6) rentals. All 4 Budget rentals do have expiry (all `10/31/2026`). Hera template marks the field required, but this is a known limitation of the Amazon source.
**Decision:** Import blank. KiGi can fill in expirations as they become known.

### 15. Rental End Dates all in July–October 2026 — FLAG FOR KIGI

**Finding:** All 16 rentals have `ownershipEndDate` in the next 4 months. 10 of them expire within 12 days of today (2026-07-07):

| Vehicle | Plate | Provider | End Date |
|---|---|---|---|
| Ram ProMaster (3MD894) | 3MD894 | Budget | 07/08/2026 |
| Ram ProMaster (3MD916) | 3MD916 | Budget | 07/08/2026 |
| Ram ProMaster (3MH003) | 3MH003 | Budget | 07/08/2026 |
| Ram ProMaster (3JT669) | 3JT669 | Budget | 07/11/2026 |
| GMC Savana (AJ40279) | AJ40279 | U-Haul | 07/17/2026 |
| GMC Savana (AL08354) | AL08354 | U-Haul | 07/17/2026 |
| GMC Savana (AG62250) | AG62250 | U-Haul | 07/17/2026 |
| Chevrolet Express (AN35194) | AN35194 | U-Haul | 07/17/2026 |
| Ford Transit (AN66459) | AN66459 | U-Haul | 07/18/2026 |
| GMC Savana (AJ40914) | AJ40914 | U-Haul | 07/18/2026 |

**Decision:** Import the dates as-is. Confirm with KiGi that these are the actual rental terms and they intend to either renew or turn over. If any of these vehicles are being returned before onboarding lands, KiGi can mark them Inactive in Hera post-import.

### 16. Fields not in the Amazon export — INFORMATIONAL

Gas Card (Last 6), Mileage, Parking Space, Description, and Rent Agreement Number are not provided by Amazon. They import blank. If KiGi wants to track any of these in Hera, the data needs to be supplied separately.

---

## Mapping doc updates from this run

Three commitments were locked in during this import:

1. [staff-import-mapping.md](../staff-import-mapping.md) — Paycom Advanced Report Writer added as a fully-locked HRIS format (previously TBD). Includes column structure, mapping table, and the ALL-CAPS-name title-case handling.
2. [staff-amazon-dsp-convert.py](../staff-amazon-dsp-convert.py) — Paycom loader + smart title-caser added. AMZL-wins email rule finally baked in (previously required a manual post-conversion patch — see the bottom of the Precise pre-import notes for the follow-up commitment). Auto-detect now identifies Paycom by header sniffing.
3. [vehicles-amazon-dsp-mapping.md](../vehicles-amazon-dsp-mapping.md) + [vehicles-amazon-dsp-convert.py](../vehicles-amazon-dsp-convert.py) — Ryder added to the provider list (same treatment as U-Haul and Kingbee: recognized, imported, not in Hera's documented allowed list yet).

No other converter or mapping changes came out of this run.
