# Amazon Data Pipeline in Hera

How customer data flows from Amazon (and adjacent telematics/HRIS systems) into Hera. Sourced from the published Intercom KB and the onboarding specs already in this repo. Update when Amazon changes a file format, when a Hera importer changes, or when the Hera Amazon Plugin (MQA) replaces a manual import flow.

Related docs:
- [knowledge/onboarding/vehicles-amazon-dsp-mapping.md](../onboarding/vehicles-amazon-dsp-mapping.md), [knowledge/onboarding/staff-import-mapping.md](../onboarding/staff-import-mapping.md): per-column mappings used by the converters.
- [knowledge/intercom-overview.md](../intercom-overview.md): how the KB itself is organized.

## The short version

Hera is the system of record. Amazon's tools are operational. Hera pulls data out of Amazon (and Netradyne, eMentor, ADP/Paycom) and turns it into a long-tail record that supports coaching, counseling, performance ranking, and unemployment-claim defense long after Amazon's own retention windows expire. See [data-ownership-stance.md](../data-ownership-stance.md) for the customer-facing framing.

Three buckets of Amazon data come in:

1. **Onboarding files** (one-time): AMZL Associates export + AMZL Fleet/Vehicles export, joined with HRIS (ADP, Paycom, Uzio) for Staff.
2. **Performance files** (recurring): weekly Scorecard / POD Details from Amazon + daily Netradyne, eMentor, EOC, PPS, CDF-Negative.
3. **Roster file** (daily): an Amazon-style roster spreadsheet imported through Hera's Custom Spreadsheet Importer.

A newer **Hera Amazon Plugin (MQA)** Chrome extension auto-syncs supported AMZL dashboards directly into Hera, removing the manual export and upload for those metrics. Currently in draft KB status.

## 1. Onboarding data (one-time, per tenant)

### AMZL Associates export

- Path in Amazon Logistics: **Administration > Associates > My Associates > Download**.
- If the DSP operates multiple stations, the station must be selected before download.
- Columns Hera cares about per the KB: **TransporterID** and **Qualifications**. (Our internal mapping in [staff-import-mapping.md](../onboarding/staff-import-mapping.md) treats it as a 9-column file and also consumes Name and ID, ID expiration, Personal Phone Number, Work Phone Number, Email, Status.)
- KB instruction to customers: "Do not edit the information in these two columns." Reinforces that we treat AMZL as locked.
- Hera matches associates to AMZL via the TransporterID once imported. This is also how weekly Scorecards get attributed to the right person.

### AMZL Fleet/Vehicles export

- Path: **Administration > Fleet > My Vehicles > Download**.
- Maps directly to the Hera Vehicles import per [vehicles-amazon-dsp-mapping.md](../onboarding/vehicles-amazon-dsp-mapping.md).
- VIN is the dedupe key on import — re-importing the same VIN updates the existing record rather than creating a duplicate.

### HRIS exports

- ADP via "Custom Reports" with a fixed field list (Legal First/Last Name, Personal/Work Email, Home/Work Phone, Personal/Work Mobile, Birth Date, Gender for Compliance Reporting, Hire Date), filtered to Position Status = Active, output as CSV.
- Paycom via "Advanced Report Writer > Employee" (Legal First/Last Name, Employee Status, Primary Phone, Personal Email, Birth Date, Hire Date), filtered to Status = Active, output as CSV.
- Uzio (xlsx) is supported in the internal converter but not yet documented in the KB.
- A newer Paycom path uses a Magic Link + API integration: customer asks Paycom for API access, signs NDA + MSA, gets API SID + Token, then allowlists Hera's IPs (13.59.40.132, 3.136.219.255, 18.216.194.37). Article is draft. This is the direction Hera is heading: API pulls instead of CSV uploads.

### How they get joined

The HRIS file and the AMZL Associates file describe the same humans. Our converter joins them and produces a single Hera Staff row per associate. AMZL wins on TransporterID, qualifications, DL expiration, email, status. HRIS wins on hire date, DOB, gender, hourly status. See the mapping doc for the exact field-by-field rule, including the 2026-06-05 change that made AMZL email the default on conflict.

## 2. Performance data (recurring)

Hera distinguishes Daily vs Weekly. Each goes through its own importer at the top of the screen: **Import > Daily Performance Data** or **Import > Weekly Performance Data**.

A cardinal rule appears everywhere in the KB: **do not edit the file contents or rename the file.** Hera parses by file shape and original Amazon naming.

### Weekly (Wednesdays)

Two files come out of Amazon's **Supplementary Reports** section weekly. Files release Wednesdays and contain the prior week's data.

| File | Source | Hera use |
|---|---|---|
| **Scorecard** | AMZL Supplementary Reports | DSP and DA-level metrics, feeds the Performance Dashboard, generates per-metric Coaching Opportunities / Positive Reinforcement / Associate Issues / Kudos |
| **DA POD Details** (Photo on Delivery) | AMZL Supplementary Reports | Per-DA POD compliance, drives POD-related coaching |
| **Customer Feedback PDF** (deprecated) | Was AMZL Supplementary Reports | Amazon stopped publishing it. Hera now uses CDF Negative daily (see below). Old import path still exists for backfill. |

**Critical timing:** Hera only generates Coaching for the *current* Amazon work week (Sunday through Saturday). Importing Sunday or later means no coaching messages for that week. Best practice is import first thing Wednesday morning.

### Daily

| File | Source | Notes |
|---|---|---|
| **EOC** (Engine Off Compliance) | AMZL Supplementary Reports, filename `EOC_Last_7_Days*` | File dated today contains yesterday's data. Amazon is often up to 2 days behind. Hera will create coaching for files up to 2 days old. Always open the file before importing to confirm Amazon updated it. |
| **eMentor (Mentor Daily)** | eMentor website, TIME FRAME must be set to DAILY | Coaching only generated for previous day's data. |
| **Netradyne** | Netradyne Reports Central > Create Request > Daily, all alert types + DriverStar | Subscribable as daily email; refresh after clicking Request and the report is instantly available. Arrives late in the day after auto-coaching window; Hera prompts to send coaching immediately after import. Skip "unknown associate" rows since Netradyne didn't identify the driver. |
| **PPS Daily Report** (Proper Parking Sequence) | AMZL Supplementary Reports > PPS Daily Report > DA-level CSV export | Default time range is wrong: must set Start 12:00 AM / End 11:59 PM or report is empty. |
| **CDF Negative** (Customer Delivery Feedback) | AMZL Quality Dashboard > Customer Delivery Feedback - Negative > Day or Week | Replaces deprecated weekly Customer Feedback PDF. Either Day or Week version is accepted, both go into Daily Performance Data. |

**Critical timing for Daily files:** Coaching is only generated when the file is yesterday's (or up to 2 days back for EOC). Older files can still be imported to backfill the record but won't trigger coaching messages. Coaching messages are English only; default language is not configurable.

### How performance data turns into Hera output

Once any performance file is imported, Hera:

1. Matches each row to an associate by TransporterID (with a one-time "Match Associates" UI for unrecognized rows — Hera remembers the match after).
2. Compares each metric against configurable thresholds in **Company Settings > Coaching**.
3. Generates **Coaching Opportunities** (for sub-threshold performance) and **Positive Reinforcement** messages (for above-threshold performance). These auto-send at a user-configured time daily. If the file imports after the cutoff, messages don't go out automatically that day; the user can send manually.
4. Generates **Associate Issues** (negative, internal-only) and **Associate Kudos** (positive, internal-only) per metric.
5. Updates each associate's **Hera Score** and **Hera Rank**. This is Hera's holistic ranking, distinct from the Amazon Scorecard rank. Each metric has a customer-tunable Importance slider. Default time window is 15 to 30 days.
6. Surfaces the file in the Performance & Coaching dashboards with a green / yellow / red status icon (green = imported on time; yellow = imported after auto-coaching cutoff so no messages sent; red = not imported).

## 3. Daily Roster import

Customers run their morning rostering through Hera's **Custom Spreadsheet Importer** on the Daily Rostering page (Hera renamed it "Rostering and Checklists"). It accepts any Excel or CSV file from the customer's station rostering process.

Key behaviors:

- Header matching is fuzzy: a column called "DA", "da name", "delivery associate", "associate", "staff", "employee", or "associate name" all map to the same field. Owner doesn't need a Hera-specific template.
- Match is on **TransporterID** if present (preferred) or on **associate name** as fallback.
- Vehicle Name, Device Name, and Associate Status columns must exact-match what's in Hera; everything else is intelligent.
- Importer both **updates** rostered drivers and **adds** unrostered ones in a single pass.
- Defaults set at the associate level (default vehicle, device, parking space) backfill automatically so the spreadsheet only needs route and staging.

There's also a draft KB article on filtering an AMZL roster spreadsheet down to only working drivers before import. It's draft because the recommended path is now the Custom Spreadsheet Importer rather than the AMZL file directly.

## 4. Hera Amazon Plugin (MQA) — the new direction

Draft article. Chrome extension that pulls Amazon Logistics data straight into Hera without manual export and upload.

**Supported dashboards:**

- Safety Daily
- Safety Weekly
- Safety ORCAS
- Quality Daily
- Quality Weekly
- Performance Summary Weekly

**Two modes:**

- **Auto Sync**: pick a location and start date, plugin runs continuously on supported dashboards.
- **Custom Sync**: target a single dashboard for a date range (daily dashboards) or week range (weekly dashboards). Used for backfill or re-sync.

**Sync History** view shows which syncs ran, what was processed, and where gaps are.

Synced data feeds the same Hera surfaces as manually imported files, **plus** powers Hera AI Chat (which can only answer about data that's actually in Hera).

This is the direction the product is going: less manual file shuffling, more automated pulls. CDF Negative and PPS Daily are recent additions to manual imports; expect them to fold into the plugin over time.

## Operational gotchas worth remembering

- **The Amazon work week ends Saturday.** Weekly Scorecards imported Sunday or later produce no coaching messages.
- **EOC is dated for today but contains yesterday's data**, and Amazon is often 2 days behind. The KB explicitly tells customers to open the file before importing to confirm it actually updated.
- **PPS exports empty unless Start/End times are 12:00 AM and 11:59 PM.** The default time range Amazon picks is wrong.
- **Netradyne "unknown associate" rows** should be unchecked before import. That's not a Hera error, it's Netradyne not recognizing the driver.
- **Don't rename the files.** Hera parses them in their original Amazon shape and name.
- **Coaching messages are English only.** No localization yet.
- **Days Amazon doesn't deliver** (New Year, Independence Day, Thanksgiving, Christmas): files can still be imported for the record, but coaching won't generate for those dates.
- **Multiple stations require separate Hera accounts** because Amazon scorecards are per-station and need to stay separated. Email aliasing (`hera+TCO@dsp.com`) is the standard trick.

## Where this all lands inside Hera

Every Amazon-sourced data point eventually shows up in one of these surfaces:

- **Daily Roster** (today's operations, photo logs, messaging)
- **Performance & Coaching** (Automated Coaching tab, Counselings tab, Associate Kudos tab, Recent DSP-Level Metrics dashboard)
- **Tasks & Reports** (EOC Metrics, Netradyne 30d/Week/Yesterday, Associate Issue Trends, Repeat Offenders, Counselings All/Pending, Attendance Statistics, Daily Report)
- **Vehicle Management** (Photo Logs, Maintenance, Damage/Accident records)
- **Associate Management** (Onboarding Tracker, Associate List, individual profile pages with Hera Score)

The downloadable archive of every imported performance file lives at Performance & Coaching > View Weekly Import Report > Imported Performance Data page.
