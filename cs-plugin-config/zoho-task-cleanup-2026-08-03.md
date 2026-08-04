# Zoho task queue cleanup, 2026-08-03

Authorised by the user. **217 overdue tasks owned by John Goldman (`5936992000000469001`) set to `Completed`.** Nothing was deleted, so every record is recoverable by reverting Status.

Queue state before: 217 overdue, oldest due 2025-08-01, across 95 distinct deals.

| Subject | Count |
|---|---|
| Comprehensive Follow Up - Schedule Comprehensive Training | 107 |
| Check In 2 - Schedule Comprehensive | 92 |
| At Risk (Needs Attention) Day 5 SMS to Whole Team | 6 |
| Escalation to CEO - Day 14 Reach out Blast | 4 |
| Churn Risk (Critical) Day 10 Call | 4 |
| At Risk (Escalation) Day 7 Call | 4 |

## Why these were closed, not worked

The 199 onboarding automation tasks (Check In 2, Comprehensive Follow Up) have no completion path, fire duplicates, and target junk deals. The 18 risk-ladder tasks belong to four accounts, three of which are churned or internal.

**Closing them is a data-hygiene action, not a claim the work was done.** The underlying automation is unchanged and will keep generating tasks until the workflow is fixed. See `csm/CLAUDE.md`, escalation matrix, open repair on `Last_Active1`.

## Requires action despite being closed

**Supreme Delivery DHO3** (deal `5936992000047178466`, Active Subscriber, Bundle) ran the full at-risk ladder in June 2026 and none of it was actioned. These four tasks were the only record:

- `5936992000078506305` due 2026-06-08 -- At Risk (Needs Attention) Day 5 SMS to Whole Team
- `5936992000078664161` due 2026-06-09 -- At Risk (Escalation) Day 7 Call
- `5936992000079010228` due 2026-06-12 -- Churn Risk (Critical) Day 10 Call
- `5936992000079271183` due 2026-06-16 -- Escalation to CEO - Day 14 Reach out Blast

**That escalation is still unresolved.** The record now lives here rather than in the queue.

## Full list of closed task IDs

| Task ID | Due | Subject | Account |
|---|---|---|---|
| `5936992000045379309` | 2025-08-01 | Check In 2 - Schedule Comprehensive | DELETE ME 1 |
| `5936992000045379313` | 2025-08-04 | Comprehensive Follow Up - Schedule Comprehensive Training | DELETE ME 1 |
| `5936992000049266539` | 2025-08-04 | At Risk (Needs Attention) Day 5 SMS to Whole Team | Hepburn Deliveries - Deal |
| `5936992000054275002` | 2025-10-11 | Check In 2 - Schedule Comprehensive | Blue Leaf Logistics LLC - Deal |
| `5936992000054275003` | 2025-10-14 | Comprehensive Follow Up - Schedule Comprehensive Training | Blue Leaf Logistics LLC - Deal |
| `5936992000054641337` | 2025-10-16 | Check In 2 - Schedule Comprehensive | Arisa Logistics - Deal |
| `5936992000054670263` | 2025-10-16 | Check In 2 - Schedule Comprehensive | Linden Logistics LLC - Deal |
| `5936992000054691330` | 2025-10-16 | Check In 2 - Schedule Comprehensive | Ridgeline Express Logistics Group, LLC - Deal |
| `5936992000054592366` | 2025-10-17 | Check In 2 - Schedule Comprehensive | ROM Logistics, LLC - Deal |
| `5936992000054639355` | 2025-10-17 | Check In 2 - Schedule Comprehensive | Steady Pace Logistics LLC - Deal |
| `5936992000054641338` | 2025-10-19 | Comprehensive Follow Up - Schedule Comprehensive Training | Arisa Logistics - Deal |
| `5936992000054670264` | 2025-10-19 | Comprehensive Follow Up - Schedule Comprehensive Training | Linden Logistics LLC - Deal |
| `5936992000054592367` | 2025-10-20 | Comprehensive Follow Up - Schedule Comprehensive Training | ROM Logistics, LLC - Deal |
| `5936992000054639356` | 2025-10-20 | Comprehensive Follow Up - Schedule Comprehensive Training | Steady Pace Logistics LLC - Deal |
| `5936992000062595002` | 2025-11-16 | Check In 2 - Schedule Comprehensive | CV Delivery Service | WNC8 - Deal |
| `5936992000062595003` | 2025-11-19 | Comprehensive Follow Up - Schedule Comprehensive Training | CV Delivery Service | WNC8 - Deal |
| `5936992000057902683` | 2025-11-23 | Comprehensive Follow Up - Schedule Comprehensive Training | Penn Express Delivery LLC - Deal |
| `5936992000063291316` | 2025-11-23 | Check In 2 - Schedule Comprehensive | CNS Logistics LLC | WNG1 - Deal |
| `5936992000058343576` | 2025-11-26 | Check In 2 - Schedule Comprehensive | All Wrights Reserved - Deal |
| `5936992000063291317` | 2025-11-26 | Comprehensive Follow Up - Schedule Comprehensive Training | CNS Logistics LLC | WNG1 - Deal |
| `5936992000058343577` | 2025-11-29 | Comprehensive Follow Up - Schedule Comprehensive Training | All Wrights Reserved - Deal |
| `5936992000060977003` | 2025-12-20 | Comprehensive Follow Up - Schedule Comprehensive Training | OneLove Logistics - Deal |
| `5936992000061726035` | 2025-12-24 | Check In 2 - Schedule Comprehensive | New Legacy Logistics LLC - Deal |
| `5936992000078985022` | 2025-12-24 | Check In 2 - Schedule Comprehensive | New Legacy Logistics LLC - Deal |
| `5936992000063645387` | 2025-12-25 | At Risk (Needs Attention) Day 5 SMS to Whole Team | CNS Logistics LLC | WNG1 - Deal |
| `5936992000061726036` | 2025-12-27 | Comprehensive Follow Up - Schedule Comprehensive Training | New Legacy Logistics LLC - Deal |
| `5936992000078985023` | 2025-12-27 | Comprehensive Follow Up - Schedule Comprehensive Training | New Legacy Logistics LLC - Deal |
| `5936992000063737705` | 2025-12-29 | At Risk (Needs Attention) Day 5 SMS to Whole Team | Hepburn Deliveries - Deal |
| `5936992000063754276` | 2025-12-29 | At Risk (Escalation) Day 7 Call | CNS Logistics LLC | WNG1 - Deal |
| `5936992000064074003` | 2025-12-30 | Churn Risk (Critical) Day 10 Call | CNS Logistics LLC | WNG1 - Deal |
| `5936992000064268887` | 2026-01-05 | Escalation to CEO - Day 14 Reach out Blast | CNS Logistics LLC | WNG1 - Deal |
| `5936992000076032005` | 2026-01-15 | Check In 2 - Schedule Comprehensive | Hawks Logistics LLC - Deal |
| `5936992000076032006` | 2026-01-18 | Comprehensive Follow Up - Schedule Comprehensive Training | Hawks Logistics LLC - Deal |
| `5936992000078841002` | 2026-01-28 | Check In 2 - Schedule Comprehensive | DELETE Inventory Management Test - Deal |
| `5936992000078841003` | 2026-01-31 | Comprehensive Follow Up - Schedule Comprehensive Training | DELETE Inventory Management Test - Deal |
| `5936992000065401003` | 2026-02-02 | Comprehensive Follow Up - Schedule Comprehensive Training | Epic Logistics LLC | DJX3 - Deal |
| `5936992000075983172` | 2026-02-04 | Check In 2 - Schedule Comprehensive | Amazing Customer Experience Logistics LLC - Deal |
| `5936992000075983447` | 2026-02-04 | Check In 2 - Schedule Comprehensive | MKL Logistics & Transportation LLC - Deal |
| `5936992000075983468` | 2026-02-04 | Check In 2 - Schedule Comprehensive | Integrity Global Logistics LLC - Deal |
| `5936992000075999153` | 2026-02-04 | Check In 2 - Schedule Comprehensive | Sparkle Logistics LLC - Deal |
| `5936992000076011081` | 2026-02-04 | Check In 2 - Schedule Comprehensive | 2X Logistics LLC - Deal |
| `5936992000076013175` | 2026-02-04 | Check In 2 - Schedule Comprehensive | Riman Logistics LLC - Deal |
| `5936992000076022171` | 2026-02-04 | Check In 2 - Schedule Comprehensive | Deva Logistics LLC - Deal |
| `5936992000076044264` | 2026-02-04 | Check In 2 - Schedule Comprehensive | Out-A-Time Logistics LLC - Deal |
| `5936992000076051122` | 2026-02-04 | Check In 2 - Schedule Comprehensive | ROM Logistics, LLC - Deal |
| `5936992000076034173` | 2026-02-05 | Check In 2 - Schedule Comprehensive | Tailwind Delivery LLC - Deal |
| `5936992000075983173` | 2026-02-07 | Comprehensive Follow Up - Schedule Comprehensive Training | Amazing Customer Experience Logistics LLC - Deal |
| `5936992000075983448` | 2026-02-07 | Comprehensive Follow Up - Schedule Comprehensive Training | MKL Logistics & Transportation LLC - Deal |
| `5936992000075983469` | 2026-02-07 | Comprehensive Follow Up - Schedule Comprehensive Training | Integrity Global Logistics LLC - Deal |
| `5936992000075999154` | 2026-02-07 | Comprehensive Follow Up - Schedule Comprehensive Training | Sparkle Logistics LLC - Deal |
| `5936992000076011082` | 2026-02-07 | Comprehensive Follow Up - Schedule Comprehensive Training | 2X Logistics LLC - Deal |
| `5936992000076013176` | 2026-02-07 | Comprehensive Follow Up - Schedule Comprehensive Training | Riman Logistics LLC - Deal |
| `5936992000076022172` | 2026-02-07 | Comprehensive Follow Up - Schedule Comprehensive Training | Deva Logistics LLC - Deal |
| `5936992000076044265` | 2026-02-07 | Comprehensive Follow Up - Schedule Comprehensive Training | Out-A-Time Logistics LLC - Deal |
| `5936992000076051123` | 2026-02-07 | Comprehensive Follow Up - Schedule Comprehensive Training | ROM Logistics, LLC - Deal |
| `5936992000076034174` | 2026-02-08 | Comprehensive Follow Up - Schedule Comprehensive Training | Tailwind Delivery LLC - Deal |
| `5936992000066712792` | 2026-02-12 | Check In 2 - Schedule Comprehensive | Final Mile Logistics LLC - Deal |
| `5936992000066749883` | 2026-02-12 | Check In 2 - Schedule Comprehensive | SEI Logistics LLC - Deal |
| `5936992000068458333` | 2026-02-13 | At Risk (Needs Attention) Day 5 SMS to Whole Team | CNS Logistics LLC | WNG1 - Deal |
| `5936992000066712793` | 2026-02-15 | Comprehensive Follow Up - Schedule Comprehensive Training | Final Mile Logistics LLC - Deal |
| `5936992000066749884` | 2026-02-15 | Comprehensive Follow Up - Schedule Comprehensive Training | SEI Logistics LLC - Deal |
| `5936992000068442953` | 2026-02-16 | At Risk (Escalation) Day 7 Call | CNS Logistics LLC | WNG1 - Deal |
| `5936992000068903003` | 2026-02-18 | Churn Risk (Critical) Day 10 Call | CNS Logistics LLC | WNG1 - Deal |
| `5936992000069251685` | 2026-02-23 | Escalation to CEO - Day 14 Reach out Blast | CNS Logistics LLC | WNG1 - Deal |
| `5936992000075939428` | 2026-02-25 | Check In 2 - Schedule Comprehensive | MJ Logistics LLC - Deal |
| `5936992000075962312` | 2026-02-25 | Check In 2 - Schedule Comprehensive | MJ Logistics LLC - Deal |
| `5936992000075939429` | 2026-02-28 | Comprehensive Follow Up - Schedule Comprehensive Training | MJ Logistics LLC - Deal |
| `5936992000075962313` | 2026-02-28 | Comprehensive Follow Up - Schedule Comprehensive Training | MJ Logistics LLC - Deal |
| `5936992000068025376` | 2026-03-01 | Check In 2 - Schedule Comprehensive | Hepburn Transportation - Deal |
| `5936992000068025377` | 2026-03-04 | Comprehensive Follow Up - Schedule Comprehensive Training | Hepburn Transportation - Deal |
| `5936992000075975139` | 2026-03-13 | Check In 2 - Schedule Comprehensive | LBM Last Mile Logistics LLC - Deal |
| `5936992000069498003` | 2026-03-14 | Comprehensive Follow Up - Schedule Comprehensive Training | Double D Delivers LLC | DAS8 - Deal |
| `5936992000069942002` | 2026-03-14 | Check In 2 - Schedule Comprehensive | LTW Logistics LLC - Deal |
| `5936992000069678003` | 2026-03-16 | Comprehensive Follow Up - Schedule Comprehensive Training | G92 Logistics LLC | DWA7 - Deal |
| `5936992000069802031` | 2026-03-16 | Comprehensive Follow Up - Schedule Comprehensive Training | LBM Last MIle Logistics LLC - Deal |
| `5936992000069839013` | 2026-03-16 | Comprehensive Follow Up - Schedule Comprehensive Training | Safe Ship Logistics LLC - Deal |
| `5936992000075975140` | 2026-03-16 | Comprehensive Follow Up - Schedule Comprehensive Training | LBM Last Mile Logistics LLC - Deal |
| `5936992000069942003` | 2026-03-17 | Comprehensive Follow Up - Schedule Comprehensive Training | LTW Logistics LLC - Deal |
| `5936992000069688002` | 2026-03-20 | Check In 2 - Schedule Comprehensive | Sweetwater Logistics Services LLC - Deal |
| `5936992000069504029` | 2026-03-25 | Check In 2 - Schedule Comprehensive | Lelit Logistics LLC - Deal |
| `5936992000070175002` | 2026-03-25 | Check In 2 - Schedule Comprehensive | Alley Cat Delivery LLC - Deal |
| `5936992000070599745` | 2026-03-25 | Comprehensive Follow Up - Schedule Comprehensive Training | Balanced Logistics Brokerage LLC - Deal |
| `5936992000070843003` | 2026-03-25 | Check In 2 - Schedule Comprehensive | Crimson Transport - Deal |
| `5936992000069504030` | 2026-03-28 | Comprehensive Follow Up - Schedule Comprehensive Training | Lelit Logistics LLC - Deal |
| `5936992000070175003` | 2026-03-28 | Comprehensive Follow Up - Schedule Comprehensive Training | Alley Cat Delivery LLC - Deal |
| `5936992000070843004` | 2026-03-28 | Comprehensive Follow Up - Schedule Comprehensive Training | Crimson Transport - Deal |
| `5936992000071283002` | 2026-03-28 | Check In 2 - Schedule Comprehensive | OTW Delivery LLC - Deal |
| `5936992000073391609` | 2026-04-01 | Check In 2 - Schedule Comprehensive | MJ Logistics LLC - Deal |
| `5936992000076011016` | 2026-04-01 | Check In 2 - Schedule Comprehensive | Triple Four Logistics LLC - Deal |
| `5936992000076022079` | 2026-04-01 | Check In 2 - Schedule Comprehensive | Giddy Up Logistics - Deal |
| `5936992000079058020` | 2026-04-01 | Check In 2 - Schedule Comprehensive | Triple Four Logistics LLC - Deal |
| `5936992000076009211` | 2026-04-02 | Check In 2 - Schedule Comprehensive | Black Steel Logistics LLC - Deal |
| `5936992000069200004` | 2026-04-03 | Comprehensive Follow Up - Schedule Comprehensive Training | Xcel Logistics LLC - Deal |
| `5936992000071646036` | 2026-04-03 | Comprehensive Follow Up - Schedule Comprehensive Training | Black Steel Logistics LLC - Deal |
| `5936992000069396003` | 2026-04-04 | Comprehensive Follow Up - Schedule Comprehensive Training | Giddy Up Logistics - Deal |
| `5936992000069930004` | 2026-04-04 | Comprehensive Follow Up - Schedule Comprehensive Training | MJ Logistics LLC - Deal |
| `5936992000069951003` | 2026-04-04 | Comprehensive Follow Up - Schedule Comprehensive Training | Upside Delivers - Deal |
| `5936992000071795003` | 2026-04-04 | Comprehensive Follow Up - Schedule Comprehensive Training | Triple Four Logistics LLC - Deal |
| `5936992000073391610` | 2026-04-04 | Comprehensive Follow Up - Schedule Comprehensive Training | MJ Logistics LLC - Deal |
| `5936992000076011017` | 2026-04-04 | Comprehensive Follow Up - Schedule Comprehensive Training | Triple Four Logistics LLC - Deal |
| `5936992000076022080` | 2026-04-04 | Comprehensive Follow Up - Schedule Comprehensive Training | Giddy Up Logistics - Deal |
| `5936992000079058021` | 2026-04-04 | Comprehensive Follow Up - Schedule Comprehensive Training | Triple Four Logistics LLC - Deal |
| `5936992000076009212` | 2026-04-05 | Comprehensive Follow Up - Schedule Comprehensive Training | Black Steel Logistics LLC - Deal |
| `5936992000075955131` | 2026-04-09 | Check In 2 - Schedule Comprehensive | Sweetwater Logistics Services LLC - Deal |
| `5936992000072683594` | 2026-04-11 | Check In 2 - Schedule Comprehensive | Primetime Logistics LLC | DJE3 - Deal |
| `5936992000076051222` | 2026-04-11 | Check In 2 - Schedule Comprehensive | Primetime Logistics LLC | DJE3 - Deal |
| `5936992000075955132` | 2026-04-12 | Comprehensive Follow Up - Schedule Comprehensive Training | Sweetwater Logistics Services LLC - Deal |
| `5936992000076051223` | 2026-04-14 | Comprehensive Follow Up - Schedule Comprehensive Training | Primetime Logistics LLC | DJE3 - Deal |
| `5936992000076051101` | 2026-04-15 | Check In 2 - Schedule Comprehensive | Safe Ship Logistics LLC - Deal |
| `5936992000075950273` | 2026-04-16 | Check In 2 - Schedule Comprehensive | Krowned Solutions LLC - Deal |
| `5936992000076022276` | 2026-04-16 | Check In 2 - Schedule Comprehensive | Dino Delivery LLC - Deal |
| `5936992000076036180` | 2026-04-17 | Check In 2 - Schedule Comprehensive | Pierce One Logistics | DAT9 - Deal |
| `5936992000076051102` | 2026-04-18 | Comprehensive Follow Up - Schedule Comprehensive Training | Safe Ship Logistics LLC - Deal |
| `5936992000075950274` | 2026-04-19 | Comprehensive Follow Up - Schedule Comprehensive Training | Krowned Solutions LLC - Deal |
| `5936992000076022277` | 2026-04-19 | Comprehensive Follow Up - Schedule Comprehensive Training | Dino Delivery LLC - Deal |
| `5936992000076036181` | 2026-04-20 | Comprehensive Follow Up - Schedule Comprehensive Training | Pierce One Logistics | DAT9 - Deal |
| `5936992000075955298` | 2026-05-04 | Comprehensive Follow Up - Schedule Comprehensive Training | StrawHat Logistics LLC - Deal |
| `5936992000075962376` | 2026-05-04 | Comprehensive Follow Up - Schedule Comprehensive Training | SURF Logistics | HEW4 - Deal |
| `5936992000074595124` | 2026-05-05 | Check In 2 - Schedule Comprehensive | LBM Last Mile Logistics LLC - Deal |
| `5936992000072600002` | 2026-05-07 | Check In 2 - Schedule Comprehensive | Hawks Logistics LLC - Deal |
| `5936992000075942083` | 2026-05-07 | Check In 2 - Schedule Comprehensive | Element Logistics LLC | DKO9 - Deal |
| `5936992000075942166` | 2026-05-07 | Comprehensive Follow Up - Schedule Comprehensive Training | CAX Operations LLC - Deal |
| `5936992000075949184` | 2026-05-07 | Check In 2 - Schedule Comprehensive | Total Package Logistics - Deal |
| `5936992000075949349` | 2026-05-07 | Check In 2 - Schedule Comprehensive | Lumana LLC - Deal |
| `5936992000075949414` | 2026-05-07 | Check In 2 - Schedule Comprehensive | Swift Pace Logistics LLC - Deal |
| `5936992000075950011` | 2026-05-07 | Check In 2 - Schedule Comprehensive | CPAC Logistics LLC - Deal |
| `5936992000075950035` | 2026-05-07 | Check In 2 - Schedule Comprehensive | Steady Pace Logistics LLC - Deal |
| `5936992000075950172` | 2026-05-07 | Check In 2 - Schedule Comprehensive | Pride Delivery Services LLC - Deal |
| `5936992000075950283` | 2026-05-07 | Check In 2 - Schedule Comprehensive | Timmer Group LLC - Deal |
| `5936992000075955110` | 2026-05-07 | Check In 2 - Schedule Comprehensive | Arisa Logistics - Deal |
| `5936992000075955171` | 2026-05-07 | Check In 2 - Schedule Comprehensive | Ridgeline Express Logistics Group, LLC - Deal |
| `5936992000075955390` | 2026-05-07 | Check In 2 - Schedule Comprehensive | ZFT Logistics LLC - Deal |
| `5936992000075961181` | 2026-05-07 | Check In 2 - Schedule Comprehensive | Nova Routes LLC | DBK1 - Deal |
| `5936992000075961257` | 2026-05-07 | Check In 2 - Schedule Comprehensive | Deal Logistics LLC - Deal |
| `5936992000075962280` | 2026-05-07 | Check In 2 - Schedule Comprehensive | ROR Delivery Inc - Deal |
| `5936992000075977106` | 2026-05-07 | Check In 2 - Schedule Comprehensive | Fortun Logistics, LLC - Deal |
| `5936992000075979038` | 2026-05-07 | Check In 2 - Schedule Comprehensive | Ridgeline Express Logistics Group, LLC | HKX1 - Deal |
| `5936992000075983338` | 2026-05-07 | Check In 2 - Schedule Comprehensive | Gamma Ray Express LLC - Deal |
| `5936992000076009038` | 2026-05-07 | Check In 2 - Schedule Comprehensive | Mako Delivery Service Inc. - Deal |
| `5936992000076011214` | 2026-05-07 | Check In 2 - Schedule Comprehensive | Force 10 Logistics, LLC - Deal |
| `5936992000076011235` | 2026-05-07 | Check In 2 - Schedule Comprehensive | Gold Star Logistics LLC | DLT2 - Deal |
| `5936992000076013065` | 2026-05-07 | Check In 2 - Schedule Comprehensive | Linden Logistics LLC - Deal |
| `5936992000076018166` | 2026-05-07 | Check In 2 - Schedule Comprehensive | Zipzone Logistics LLC - Deal |
| `5936992000076022125` | 2026-05-07 | Check In 2 - Schedule Comprehensive | 5L3R Logistics LLC - Deal |
| `5936992000076022255` | 2026-05-07 | Check In 2 - Schedule Comprehensive | Miracle Mile DSP LLC - Deal |
| `5936992000076034119` | 2026-05-07 | Check In 2 - Schedule Comprehensive | Lovett Logistix LLC - Deal |
| `5936992000076036289` | 2026-05-07 | Check In 2 - Schedule Comprehensive | Alchemy Logistics Services LLC - Deal |
| `5936992000076038147` | 2026-05-07 | Check In 2 - Schedule Comprehensive | Gold Link Logistics LLC - Deal |
| `5936992000076043248` | 2026-05-07 | Check In 2 - Schedule Comprehensive | Nova Routes LLC | DBK4 - Deal |
| `5936992000076044310` | 2026-05-07 | Check In 2 - Schedule Comprehensive | AMLO Logistics - Deal |
| `5936992000076046002` | 2026-05-07 | Check In 2 - Schedule Comprehensive | Austral Logistics LLC - Deal |
| `5936992000076046162` | 2026-05-07 | Check In 2 - Schedule Comprehensive | Palm Beach Delivers LLC - Deal |
| `5936992000076046197` | 2026-05-07 | Check In 2 - Schedule Comprehensive | LCDC Logistics, LLC - Deal |
| `5936992000076046320` | 2026-05-07 | Check In 2 - Schedule Comprehensive | Last Mile DSP LLC - Deal |
| `5936992000076051179` | 2026-05-07 | Check In 2 - Schedule Comprehensive | Gold Star Logistics LLC | DRT3 - Deal |
| `5936992000072600003` | 2026-05-10 | Comprehensive Follow Up - Schedule Comprehensive Training | Hawks Logistics LLC - Deal |
| `5936992000075942084` | 2026-05-10 | Comprehensive Follow Up - Schedule Comprehensive Training | Element Logistics LLC | DKO9 - Deal |
| `5936992000075949185` | 2026-05-10 | Comprehensive Follow Up - Schedule Comprehensive Training | Total Package Logistics - Deal |
| `5936992000075949350` | 2026-05-10 | Comprehensive Follow Up - Schedule Comprehensive Training | Lumana LLC - Deal |
| `5936992000075949415` | 2026-05-10 | Comprehensive Follow Up - Schedule Comprehensive Training | Swift Pace Logistics LLC - Deal |
| `5936992000075950012` | 2026-05-10 | Comprehensive Follow Up - Schedule Comprehensive Training | CPAC Logistics LLC - Deal |
| `5936992000075950036` | 2026-05-10 | Comprehensive Follow Up - Schedule Comprehensive Training | Steady Pace Logistics LLC - Deal |
| `5936992000075950173` | 2026-05-10 | Comprehensive Follow Up - Schedule Comprehensive Training | Pride Delivery Services LLC - Deal |
| `5936992000075950284` | 2026-05-10 | Comprehensive Follow Up - Schedule Comprehensive Training | Timmer Group LLC - Deal |
| `5936992000075955111` | 2026-05-10 | Comprehensive Follow Up - Schedule Comprehensive Training | Arisa Logistics - Deal |
| `5936992000075955172` | 2026-05-10 | Comprehensive Follow Up - Schedule Comprehensive Training | Ridgeline Express Logistics Group, LLC - Deal |
| `5936992000075955391` | 2026-05-10 | Comprehensive Follow Up - Schedule Comprehensive Training | ZFT Logistics LLC - Deal |
| `5936992000075961182` | 2026-05-10 | Comprehensive Follow Up - Schedule Comprehensive Training | Nova Routes LLC | DBK1 - Deal |
| `5936992000075961258` | 2026-05-10 | Comprehensive Follow Up - Schedule Comprehensive Training | Deal Logistics LLC - Deal |
| `5936992000075962281` | 2026-05-10 | Comprehensive Follow Up - Schedule Comprehensive Training | ROR Delivery Inc - Deal |
| `5936992000075977107` | 2026-05-10 | Comprehensive Follow Up - Schedule Comprehensive Training | Fortun Logistics, LLC - Deal |
| `5936992000075979039` | 2026-05-10 | Comprehensive Follow Up - Schedule Comprehensive Training | Ridgeline Express Logistics Group, LLC | HKX1 - Deal |
| `5936992000075983339` | 2026-05-10 | Comprehensive Follow Up - Schedule Comprehensive Training | Gamma Ray Express LLC - Deal |
| `5936992000076009039` | 2026-05-10 | Comprehensive Follow Up - Schedule Comprehensive Training | Mako Delivery Service Inc. - Deal |
| `5936992000076011215` | 2026-05-10 | Comprehensive Follow Up - Schedule Comprehensive Training | Force 10 Logistics, LLC - Deal |
| `5936992000076011236` | 2026-05-10 | Comprehensive Follow Up - Schedule Comprehensive Training | Gold Star Logistics LLC | DLT2 - Deal |
| `5936992000076013066` | 2026-05-10 | Comprehensive Follow Up - Schedule Comprehensive Training | Linden Logistics LLC - Deal |
| `5936992000076018167` | 2026-05-10 | Comprehensive Follow Up - Schedule Comprehensive Training | Zipzone Logistics LLC - Deal |
| `5936992000076022126` | 2026-05-10 | Comprehensive Follow Up - Schedule Comprehensive Training | 5L3R Logistics LLC - Deal |
| `5936992000076022256` | 2026-05-10 | Comprehensive Follow Up - Schedule Comprehensive Training | Miracle Mile DSP LLC - Deal |
| `5936992000076034120` | 2026-05-10 | Comprehensive Follow Up - Schedule Comprehensive Training | Lovett Logistix LLC - Deal |
| `5936992000076036290` | 2026-05-10 | Comprehensive Follow Up - Schedule Comprehensive Training | Alchemy Logistics Services LLC - Deal |
| `5936992000076038148` | 2026-05-10 | Comprehensive Follow Up - Schedule Comprehensive Training | Gold Link Logistics LLC - Deal |
| `5936992000076043249` | 2026-05-10 | Comprehensive Follow Up - Schedule Comprehensive Training | Nova Routes LLC | DBK4 - Deal |
| `5936992000076044311` | 2026-05-10 | Comprehensive Follow Up - Schedule Comprehensive Training | AMLO Logistics - Deal |
| `5936992000076046003` | 2026-05-10 | Comprehensive Follow Up - Schedule Comprehensive Training | Austral Logistics LLC - Deal |
| `5936992000076046163` | 2026-05-10 | Comprehensive Follow Up - Schedule Comprehensive Training | Palm Beach Delivers LLC - Deal |
| `5936992000076046198` | 2026-05-10 | Comprehensive Follow Up - Schedule Comprehensive Training | LCDC Logistics, LLC - Deal |
| `5936992000076046321` | 2026-05-10 | Comprehensive Follow Up - Schedule Comprehensive Training | Last Mile DSP LLC - Deal |
| `5936992000076051180` | 2026-05-10 | Comprehensive Follow Up - Schedule Comprehensive Training | Gold Star Logistics LLC | DRT3 - Deal |
| `5936992000075983003` | 2026-05-18 | Comprehensive Follow Up - Schedule Comprehensive Training | RTD Routes LLC - Deal |
| `5936992000076243003` | 2026-05-24 | Comprehensive Follow Up - Schedule Comprehensive Training | Triple Four Logistics LLC - Deal |
| `5936992000076251118` | 2026-05-25 | Comprehensive Follow Up - Schedule Comprehensive Training | G Squared Logistics - Deal |
| `5936992000076539613` | 2026-05-27 | Check In 2 - Schedule Comprehensive | Fletcher Logistics LLC - Deal |
| `5936992000076539614` | 2026-05-30 | Comprehensive Follow Up - Schedule Comprehensive Training | Fletcher Logistics LLC - Deal |
| `5936992000078025187` | 2026-06-01 | At Risk (Needs Attention) Day 5 SMS to Whole Team | AI Testing - Deal |
| `5936992000078058498` | 2026-06-01 | At Risk (Escalation) Day 7 Call | AI Testing - Deal |
| `5936992000078242206` | 2026-06-04 | Churn Risk (Critical) Day 10 Call | AI Testing - Deal |
| `5936992000077457002` | 2026-06-06 | Check In 2 - Schedule Comprehensive | New Legacy Logistics LLC - Deal |
| `5936992000078454453` | 2026-06-08 | Escalation to CEO - Day 14 Reach out Blast | AI Testing - Deal |
| `5936992000078506305` | 2026-06-08 | At Risk (Needs Attention) Day 5 SMS to Whole Team | Supreme Delivery DHO3 - Deal |
| `5936992000077457003` | 2026-06-09 | Comprehensive Follow Up - Schedule Comprehensive Training | New Legacy Logistics LLC - Deal |
| `5936992000078664161` | 2026-06-09 | At Risk (Escalation) Day 7 Call | Supreme Delivery DHO3 - Deal |
| `5936992000077784002` | 2026-06-11 | Check In 2 - Schedule Comprehensive | SACB Logistics - Deal |
| `5936992000079010228` | 2026-06-12 | Churn Risk (Critical) Day 10 Call | Supreme Delivery DHO3 - Deal |
| `5936992000077784003` | 2026-06-14 | Comprehensive Follow Up - Schedule Comprehensive Training | SACB Logistics - Deal |
| `5936992000079271183` | 2026-06-16 | Escalation to CEO - Day 14 Reach out Blast | Supreme Delivery DHO3 - Deal |
| `5936992000078044567` | 2026-06-17 | Check In 2 - Schedule Comprehensive | Philosophe LLC - Deal |
| `5936992000078044568` | 2026-06-20 | Comprehensive Follow Up - Schedule Comprehensive Training | Philosophe LLC - Deal |
| `5936992000082491002` | 2026-06-28 | Check In 2 - Schedule Comprehensive | R&H Logistics - Deal |
| `5936992000082491003` | 2026-07-01 | Comprehensive Follow Up - Schedule Comprehensive Training | R&H Logistics - Deal |
| `5936992000080483004` | 2026-07-17 | Check In 2 - Schedule Comprehensive | Athenyx Logistics - Deal |
| `5936992000076038035` | 2026-07-20 | Check In 2 - Schedule Comprehensive | Paranos Delivery Inc - Deal |
| `5936992000080483005` | 2026-07-20 | Comprehensive Follow Up - Schedule Comprehensive Training | Athenyx Logistics - Deal |
| `5936992000076038036` | 2026-07-23 | Comprehensive Follow Up - Schedule Comprehensive Training | Paranos Delivery Inc - Deal |
| `5936992000080835466` | 2026-07-25 | Check In 2 - Schedule Comprehensive | KiGi Solutions Inc - Deal |
| `5936992000080835467` | 2026-07-28 | Comprehensive Follow Up - Schedule Comprehensive Training | KiGi Solutions Inc - Deal |
