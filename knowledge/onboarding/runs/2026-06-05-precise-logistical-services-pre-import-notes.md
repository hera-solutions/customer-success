# Precise Logistical Services — Pre-Import Notes

**Generated:** 2026-06-05
**Source files (customer-provided):**

- `AssociateData (4).csv` — Amazon AMZL Associates export (master roster)
- `Hera Staff Import.csv` — ADP HRIS export
- `VehiclesData (2).xlsx` — Amazon DSP vehicle export

**Output files (Google Drive `Imports/Tenants/Precise Logistical Services/`):**

- `Precise Logistical Services - Staff.csv`
- `Precise Logistical Services - Vehicles.csv`

All conversion findings were resolved with the operator before these files were saved. Resolutions are recorded below alongside each finding so the import team has full context.

This run also introduced **two process changes** to the staff import rules. They are now reflected in [staff-import-mapping.md](../staff-import-mapping.md) and apply to every future DSP import:

1. **DOB and Gender** — always carry HRIS values through to Hera when populated. No longer blanked by default.
2. **Email mismatches** — AMZL (company-issued) email wins by default. HRIS personal email is informational. (Previously: HRIS won.)

---

## Staff — high-level

- **AMZL rows:** 122 (94 Active, 28 Inactive)
- **ADP rows (raw):** 138; deduped to 138 (no duplicate-email collisions, though several people appear twice with different phone variants)
- **Output rows:** 122 (AMZL is master; every AMZL row becomes a Hera Staff row)
- **Email populated:** 122 of 122 (after AMZL backfills — see resolutions 5 and 6 below)
- **DOB populated:** 115 of 122 (carried through from ADP per new rule)
- **Gender populated:** 108 of 122 (carried through from ADP per new rule)
- **Validation:** All checks passed.

---

## Staff — resolutions

### 1. DOB tracking — RESOLVED (carry HRIS values through)
**Finding:** DOB populated for 115 of 122 drivers from ADP.
**Decision:** Carry the values through. Process change: DOB is no longer blanked by default. If HRIS provides it, Hera gets it.

### 2. Gender tracking — RESOLVED (carry HRIS values through)
**Finding:** Gender populated for 108 of 122 drivers from ADP.
**Decision:** Carry the values through. Same process change as DOB.

### 3. HRIS-only people (23) — RESOLVED (skip per locked rule)
**Finding:** 23 people appear in ADP but not in AMZL. Per the locked join rule they aren't drivers per Amazon's roster, so they're skipped.
**Decision:** Skip all 23. Listed below for reference.

| Name | Hire Date | Personal Email | Phone |
|---|---|---|---|
| Irvin Bowdoin | 08/04/2019 | ifrankbowdoin@gmail.com | (843) 425-3495 |
| Drayton Siegling | 04/13/2020 | draytonsplgt@gmail.com | (843) 725-8467 |
| James Howell | 07/24/2020 | jhowellplgt@yahoo.com | (843) 327-0493 |
| Camille Bowdoin | 09/27/2020 | CSBowdoin@gmail.com | (843) 494-9080 |
| Samuel Wheeler | 05/10/2021 | samwheeler29@gmail.com | (864) 723-0355 |
| Monica Hamlet | 04/19/2024 | hamletmplgt@gmail.com | (854) 212-9874 |
| Mitchell Rose | 11/11/2024 | brandonrose650@gmail.com | (843) 478-8326 |
| Alejandra Castillo Boza | 03/13/2025 | acastilloplgt@gmail.com | (843) 704-7359 |
| Issiah Byrd | 05/15/2025 | byrdiplgt@gmail.com | (864) 275-2848 |
| Kayla Clark | 05/26/2025 | clarkkplgt@gmail.com | (410) 231-1317 |
| Kevin Bryant | 07/14/2025 | kevinbplgt@gmail.com | (843) 653-7067 |
| Mickeil Murray | 09/03/2025 | mickeilmplgt@gmail.com | (854) 212-1866 |
| Kenia De Oliveira | 09/18/2025 | kdeoliveiraplgt@gmail.com | (843) 990-0814 |
| Tykeia Howell | 11/01/2025 | howelltplgt@gmail.com | (203) 572-4544 |
| Reginald Smalls | 11/05/2025 | smallsrplgt@gmail.com | (843) 384-3562 |
| Ethan Ros | 11/12/2025 | ethanrplgt@yahoo.com | (603) 219-1520 |
| Cameron Waltz | 01/26/2026 | waltzcplgt@gmail.com | (472) 248-4978 |
| Benjamin German | 03/17/2026 | germanbplgt@gmail.com | (843) 637-5242 |
| Chynah Judge | 04/01/2026 | judgecplgt@gmail.com | (854) 274-5721 |
| Frederick Carn II | 05/06/2026 | carnfplgt@yahoo.com | (843) 613-1643 |
| Jessica Garrett | 05/21/2026 | garrettjplgt@yahoo.com | (843) 499-1848 |
| Michael Windham | 05/25/2026 | windhammplgt@gmail.com | (843) 303-8368 |
| Ricardo De La Rosa Aranda | 05/26/2026 | ricardorplgt@gmail.com | (854) 210-7140 |

Note for Precise: about a third of these have May–June 2026 hire dates and may simply not be on AMZL yet. If any are active drivers we missed, send the AMZL Transporter ID and they can be added.

### 4. AMZL-only drivers (7) — RESOLVED (import all as-is)
**Finding:** 7 AMZL rows had no ADP match. All 7 are INACTIVE. They import with parsed First/Last from AMZL, AMZL email, AMZL phone, blank Hire Date, blank DOB.
**Decision:** Follow the locked rule — import all. Hire Date stays blank; Precise can backfill in Hera if desired.

| Driver | TID | Notes |
|---|---|---|
| Abigail Wood | A1FBGVMN0NQED3 | Helper-only (no drive auth) |
| Darius Hanna | A1JAEA0WW3XSM5 | |
| Justin Dueno | AUA11XUQC3MQY | |
| Nikolas Mirabella | A1XEBBBAGELPTG | Helper-only (no drive auth) |
| Samuel Hymas | A8EKBV8A6YNCQ | |
| Sebastien Boyle | A2QWK95I4NLD5G | Helper-only (no drive auth) |
| Trevor Kubis | A1I3AF2UET97S3 | |

### 5. Email mismatches (13) — RESOLVED (AMZL email wins — new default)
**Finding:** 13 drivers had different emails in ADP vs AMZL. AMZL emails follow Precise's `<lastname><firstinitial>plgt@gmail.com` company-issued pattern; ADP holds the drivers' personal emails.
**Decision:** Use AMZL emails for Hera. This is a permanent rule change for all future DSP imports — DSPs typically use their company-issued addresses for ops comms, and drivers actually check those at work.

| Driver | Hera Email (AMZL) | Personal email on file (ADP, not imported) |
|---|---|---|
| Asia Cunningham | asiacplgt@yahoo.com | cunninghamaplgt@gmail.com |
| Cedrick Stewart | cstewartplgt@gmail.com | cedricksplgt@gmail.com |
| Christopher DeWitt | christopherdplgt@gmail.com | dewittcplgt@gmail.com |
| Jasmyn Schoolfield | jschoolfieldplgt@gmail.com | jasmyn.schoolfield@gmail.com |
| John Bowdoin | bowdoinjplgt@gmail.com | jbowdoin44@gmail.com |
| Junuh Waller | wallerjplgt@yahoo.com | wallerjplgt@gmail.com |
| Keydrick Jenkins | kjenkinsplgt@gmail.com | keyjenk@yahoo.com |
| Nigeria Baqi | nbaqiplgt@gmail.com | Nigeriabaqi@gmail.com |
| Pablo Rodrigues Santos | psantosplgt@gmail.com | pablitousa2023@gmail.com |
| Samantha Haakinson | shaakinsonplgt@gmail.com | s.haakinson79@gmail.com |
| Stacy Weaver | sweaverplgt@gmail.com | stacyWPLGT@gmail.com |
| Wynton Holmes | holmeswplgt@gmail.com | wynton_h@yahoo.com |
| Zakwon Gregg | greggkplgt@gmail.com | zgregg35@gmail.com |

### 6. Blank ADP email — AMZL backfill (3) — RESOLVED
**Finding:** 3 drivers matched ADP but had blank ADP Personal Email. AMZL had values for all three. Without backfill, two active drivers would have arrived in Hera with no email.
**Decision:** Backfill from AMZL email. Aligns with the new AMZL-wins rule.

| Driver | Status | Hera Email (from AMZL) |
|---|---|---|
| Allen Chandler | Inactive | allencplgt@outlook.com |
| Edward Washington | Active | ewashingtonplgt@gmail.com |
| Vitalii Khvorostinin | Active | vitaliikplgt@yahoo.com |

### 7. Phone-only match (1) — RESOLVED (accepted)
**Finding:** Pablo Rodrigues Santos matched ADP↔AMZL by phone only. AMZL has him as "Pablo RodriguesSantos" (no space) with email `psantosplgt@gmail.com`; ADP has "Pablo Rodrigues Santos" with email `pablitousa2023@gmail.com`. Phone (854) 500-2087 matched.
**Decision:** Accepted — same person.

### 8. Name override — Maurice Chisolm — RESOLVED
**Finding:** AMZL row shows "maurice Chisolm" (lowercase first letter). ADP row shows "Eric Chisolm". They matched by shared email `ericcplgt@gmail.com`. The legal first name appears to be Maurice (likely goes by Eric).
**Decision:** Use AMZL name — `Maurice Chisolm` in Hera (first letter title-cased).

### 9. Blank Authorized To Drive (6 helper-only) — RESOLVED (leave blank)
**Finding:** Six AMZL rows are AMZL_HELPER only — no driver qualifications. Only one is currently Active.
**Decision:** Leave Authorized To Drive blank. Precise can add driver authorization in-app if any of them transition to driving.

| Driver | Status |
|---|---|
| Abigail Wood | Inactive |
| **Addison Carson** | **Active** |
| Andrea Moniz | Inactive |
| Mandi Bunnell | Inactive |
| Nikolas Mirabella | Inactive |
| Sebastien Boyle | Inactive |

**Flag for Precise:** Confirm Addison Carson is helper-only and not also driving. If she's also a driver, add the qualification on AMZL and re-run the import or update her directly in Hera.

### 10. Inactive bucket (28) — RESOLVED (keep `Inactive - Misc`)
**Finding:** 28 AMZL `INACTIVE` rows land in Hera as `Inactive - Misc`.
**Decision:** Keep the documented default. Precise can re-classify in Hera later if they prefer Terminated, On Leave, etc.

### 11. Name variations matched cleanly by email (8) — INFORMATIONAL
ADP and AMZL had different spellings/formats of the same legal name; the email match resolved them. Hera output uses the ADP spelling (HRIS wins on First/Last per locked rule). Listed for transparency:

- Alishya Neal-Turner (ADP) / Alishya Nealturner (AMZL)
- A'Miyah Temple / AMiyah Temple
- A'Myah Temple / Amyah Lenae Temple
- Borman Sanchez Alfaro / Borman Alexander Sanchez
- Quadre' Stuckey / Quadre Tavon Stuckey
- Sa'miah Eddings Zieglar / Sa Miiah Sai Yuniq Eddings Zieglar
- Samari Hamilton-Smith / Samari Le Hamilton Smith

---

## Vehicles — high-level

- **Source rows:** 68
- **Output rows:** 68
- **Status:** 44 Active, 24 Inactive - Grounded
- **Vehicle Types:** 49 Standard Parcel XL, 18 Standard Parcel Large, 1 Custom Delivery Van (16ft)
- **Ownership:** 40 Rent, 28 Lease (Amazon-owned)
- **Providers (after blanking "Other"):** 28 Element, 21 Merchants Fleet, 19 blank
- **States:** SC 45, FL 15, NJ 6, ME 2
- **Validation:** All checks passed.

---

## Vehicles — resolutions

### 12. Company = "Other" on 19 rentals — RESOLVED (blank the column)
**Finding:** 19 rental vehicles came from Amazon with `vehicleProvider = "Other"` — Amazon didn't capture the rental company. The raw `type` field hinted at rental codes (`Rental`, `Rental (H123)`, `Rental (PLGT01)`, `Rental (42101)`) but those don't map deterministically to Hera's allowed Company list.
**Decision:** Blank the Company column on all 19. Precise can fill in the actual provider in Hera once the data lands. All 19 rows still have full VIN, plate, ownership = Rent, and other identifying info.

VINs (for Precise's reference when filling in): 3C6MRVHG1PE575268, W1Y40CHY8MT056586, W1Y4KBHYXST213956, W1W40CHY3MT052440, W1Y70BGY3NT112833, W1Y70BGY3NT113498, W1Y70BGYXNT113980, 1FTYE1C8XPKB71364, W1Y4KBHY0ST215585, W1Y70BGY3NT114663, W1Y4KBHY5ST214951, W1Y4KBHY3ST214382, W1Y70BGY0NT115169, W1Y70BGY2NT107333, W1Y4KBHY8ST213809, W1Y70BGY1NT115939, W1Y70BGY3PT128940, W1Y70BGY0PT127698, W1Y4KBHYXST213648.

### 13. OTHER Make/Model — H12 L (C) — RESOLVED (leave blank)
**Finding:** One vehicle (H12 L (C), VIN W1Y70BGY0PT127698, plate V0429RL, 2023 model year, Large Cargo Van tier, SC, Rent) has Make = `OTHER` and Model = `OTHER` in Amazon's export. The VIN prefix W1Y identifies Mercedes-Benz, but Amazon hasn't filled in the make or model.
**Decision:** Blank Make and Model in Hera. Precise can fill in the correct values once the data lands. Vehicle Type (Standard Parcel Large) is still populated from the LARGE_CARGO_VAN serviceTier.

### 14. Two vehicles used serviceTier fallback — INFORMATIONAL
Two rentals had no Amazon `serviceType` and were categorized via `serviceTier = LARGE_CARGO_VAN` → Hera `Standard Parcel Large`. Same vehicles as above:

- H08 L (C) — VIN W1Y70BGY3NT113498
- H12 L (C) — VIN W1Y70BGY0PT127698 (also the OTHER Make/Model row)

### 15. 28 rentals with no License Plate Expiration — INFORMATIONAL
Amazon's export doesn't capture registration expiry on most rentals. All 28 are Rent ownership. Hera template marks the field required, but this is a known limitation of the Amazon source. Precise can fill in expirations as they become known.

### 16. Fields not in the Amazon export — INFORMATIONAL
Gas Card (Last 6), Mileage, Parking Space, Description, and Rent Agreement Number are not provided by Amazon. They import blank. If Precise wants to track any of these in Hera, the data needs to be supplied separately.

---

## Mapping doc updates from this run

Two process commitments were locked in during this import:

1. [staff-import-mapping.md](../staff-import-mapping.md) — Email rule rewritten so AMZL wins by default; DOB and Gender language updated to "always carry HRIS values through, do not blank".

No converter code changes were needed. The email override and Chisolm name override were applied as a one-time post-conversion patch for this run; a follow-up should update the converter so the new email rule is built in.
