# How Customers Use Hera

A working map of how a DSP owner or dispatcher actually uses Hera day-to-day, based on the published Intercom KB. Pair this with [amazon-data-pipeline.md](amazon-data-pipeline.md), which covers how data gets *into* Hera. This file covers what they *do* with it.

## The product in one sentence

Hera is the DSP operating system. The Daily Roster is the heart of the product. Everything else (vehicle photos, counselings, coaching, reports) hangs off the roster or off the performance data Hera pulls in from Amazon.

## Initial setup (Quick-Start)

Order matters, and the KB explicitly warns customers not to import performance data until the first four steps are done:

1. **Log in and set an admin password.** First account is admin; more users added later.
2. **Import Associates.** Download the CSV template, fill it, upload. Min fields: Status, First/Last Name, TransporterID (this is how Hera matches to Amazon), Email, Phone, Hire Date, DOB, Authorized to Drive (semicolon-separated vehicle types).
3. **Import Vehicles.** Same pattern. VIN is the dedupe key.
4. **Import Devices** (the "Rabbits" / company phones).
5. **Edit Company Settings.** Important early choices: automated coaching send time, photo log requirements, Hera Rank metric weights.
6. **Import performance data**, going back as far as 2020 if they want history.

The KB hammers one rule across every import: do not edit column headers, do not delete columns.

## Daily operations (the morning routine)

### Daily Roster (renamed "Rostering and Checklists")

Central daily surface. Replaces a manual roster spreadsheet and the dispatcher hand-texting drivers their assignments.

**Building the roster:**
- Import a custom spreadsheet from the station (any column naming; Hera does fuzzy header matching). Matches on TransporterID preferred, name as fallback. Updates already-rostered drivers and adds new ones in one pass.
- Or roster a single associate manually (useful for late additions).
- Defaults set per associate (default vehicle, device, parking) auto-fill so the imported spreadsheet only needs route and staging.

**Top of the page:**
- **Stand-up Announcements**: broadcasted to rostered DAs when the user clicks send. Supports attachments. Used for daily safety tips, route changes.
- **Manager Notes** and **Fleet Notes**: internal, not sent to DAs.

**Roster Status pills** (color-coded, customizable):
- Default options: Rostered, On Time, Late With Call, Late No Call, VTO, Called Out Excused, Called Out Not Excused, No Show No Call.
- Inactive statuses (VTO, Called Out, No Show) trigger pop-ups offering to create an Associate Issue, a Counseling, or replace with a Standby. This is how a missed shift turns into a paper trail in one click.
- Custom statuses can be added directly from the Daily Roster.
- Once an associate is replaced with a Standby, status changes are restricted to other Inactive statuses until the replacement is removed.
- Full **Roster Status Change Log** per DA via the row action menu.

**Adding to the roster:**
- Helpers, Rescuers, Standby Drivers all supported.
- Standbys live in their own table below the Daily Roster.

**Sending the roster:**
- Single send pushes assignments to all (or selected) rostered DAs. Goes out per each DA's communication preferences.
- Three channels (Daily Roster has explicit checkboxes for each):
  - **SMS to personal phone** (default; DA can opt out via STOP).
  - **SMS to assigned company device** (newer; only available from Daily Roster surfaces).
  - **Email** (with unsubscribe link).
- Inactive DAs (Call Out, No Show, VTO) won't receive messages for that day.

**Why customers actually care about Daily Roster:**
The KB calls out the secondary benefit: it's a paper trail. If a vehicle ticket arrives in the mail two months later, Hera can recall on demand who was using which vehicle and device that day. Same logic for vehicle damage attribution and unemployment defenses.

### Vehicle Photo Logs

The KB describes vehicle damage as "one of the most expensive, costly items for a DSP." Photo logs are the daily damage-accountability ritual. Customers value this feature highly.

**How it works:**
- From Daily Roster, dispatcher sends a unique photo log link to all (or selected) rostered DAs via SMS + email. Or `+Photo Log` button under any single vehicle.
- DA opens the link on their phone (no app, no login). Required photo categories default to Front, Back, Left, Right, Odometer. Customizable per send or globally via Custom Lists > Vehicle Photo Log Requirements.
- DA taps "Tap to Open Camera." By default they can only use the camera, not pick from library; this can be flipped in Company Settings.
- Multiple photos per category allowed; no cap.
- Each upload is timestamped and attributed to the DA.
- Most recent photo logs for the same vehicle are shown alongside, making it easy to spot day-over-day differences.

**Where photo logs surface back:**
- Counter under each vehicle on Daily Roster increases as DAs upload.
- Yellow triangle warning if a sent link has zero photos.
- Full history under Vehicle Management > Vehicle Details > Vehicle History.
- Tasks & Reports > Daily Report > filter to Vehicle Photo Logs to audit completion.

Can also be set as a Roster Checklist item, in which case completion shows in the Checklist drawer.

### Roster Checklists

Send a structured checklist to each rostered DA (e.g., uniform, badge, walk-around) along with or separately from the roster blast. Items can include Vehicle Photo Logs. DA submits via the link, results auto-refresh in the dispatcher view. Once items are saved by the DA they can't be edited.

## Performance management (the disciplinary surface)

This is where the recurring imports from Amazon, Netradyne, and eMentor turn into customer action.

### Performance & Coaching page

Two dashboards: **Weekly Imported Data** and **Daily Imported Data**, each with green / yellow / red icons per file:

- **Green check**: file imported on time, coaching will go out on schedule.
- **Yellow check**: file imported after the auto-coaching cutoff; messages won't auto-send for this period.
- **Red triangle**: file not yet imported.

This dashboard is the dispatcher's "what do I owe today" view.

### Automated Coaching tab

Shows generated Coaching Opportunities (sub-threshold metrics) and Positive Reinforcement messages (above-threshold metrics) for each associate, generated from the imported files.

- Edit each message before send.
- Auto-sends daily at the time set in Company Settings. Default recommendation: send to "Associates Rostered Today" only.
- Send Now button per associate, or bulk send.
- English only, not configurable.

### Associate Issues and Kudos

- **Issues** are negative records. Hera auto-creates them when imported performance shows a Poor or Fair score on any tracked metric. Customers can also create them manually for things Amazon doesn't track (Did Not RTS, Left Trash in Van, etc.).
- **Kudos** are the positive equivalent.
- Both are internal: never sent to the DA, only visible to Hera users.
- Both feed Hera Score / Hera Rank with customer-adjustable importance.
- Custom types live in Custom Lists. Default attendance issues (Called Out, Late No Call) are baked in.
- A special issue type called **Amazon Violation/Defect** is for tracking Amazon-issued DPMOs and appeals. The KB explicitly tells customers to paste the appeal text into Hera since Amazon removes appeals from view after submission.

### Counselings (the formal write-up)

The disciplinary paper trail. Used for unemployment defense, separation decisions, and legal protection.

**Creation paths:**
- Manual via Create > Counseling.
- Auto-prompted from Daily Roster when a DA gets an Inactive status.
- Auto-prompted from Vehicle Damage records (with toggle for "at fault" attribution).
- Auto-prompted from Amazon Violation/Defect Associate Issues.

**On the form:**
- Counseling Type (custom list with reusable templates per type).
- Counseling Severity (custom list, color-coded, customer-defined). Can't edit or delete a severity that's already in use.
- Linked Associate Issue (optional).
- Attached images/documents with per-file "Show to Associate" toggle.
- Schedule-to-send (only at creation time) or send immediately.

**DA experience:**
- Receives SMS + email with a link.
- Reviews the form, optionally sees attached images (documents currently show filename only).
- Signs digitally, or rejects.

**Where they show up:**
- Performance & Coaching > Counselings tab, filterable by Status, Type, Date of Occurrence, Sent Date.
- An "Other Counselings" pill on every counseling form shows the DA's prior counselings while building a new one.
- Downloadable as individual PDFs or as a zip of every counseling for one DA from the Associate Profile.
- Delete is permission-gated (Performance & Coaching: Delete Counselings) and irreversible.

### Hera Score / Hera Rank

Hera's holistic ranking, distinct from the Amazon Scorecard rank.

- Calculated over a customer-set window (Hera recommends 15-30 days; longer windows produce less score movement).
- Each metric (Weekly and Daily) has an Importance slider in Company Settings > Coaching.
- Negative inputs: poor metric performance, Associate Issues.
- Positive inputs: strong metric performance, Associate Kudos.
- Surfaced on the Associate Management Dashboard (top 10 / bottom 10) and on each associate's profile.

KB's framing on why this matters: a DA can be #1 on the Amazon Scorecard and get fired the next day for everything Amazon doesn't see (van damage, callouts, insubordination, missing uniform). The Hera Rank captures that fuller picture.

## Messaging

### Hera Messenger

Two-way SMS with each DA. Works like a phone messaging app inside Hera.

- Single phone number per company (visible in Company Details).
- Users with permission can see all conversations; the DA can't tell which Hera user replied unless told.
- KB suggests customers tell drivers to save the Hera number as the company name and use it for call-outs (so the call-out is recorded).
- Set up like an app on your phone via the "2-way Hera texting on your cell phone" article.

### Group sends

- From Daily Roster: send to all rostered, selected, filtered, or all with a particular Label.
- From Associate List: same, with status filter prefiltering.
- All group sends are individual messages, not group chats. DAs don't see each other.
- Pulling specific DAs across pages is supported; the count chip shows running selection.
- Warnings if Inactive DAs are in the selection.

### Communication preferences

Per DA, tracked on the profile and visible on the Associate Management Dashboard "opted out" card:
- Email Off
- SMS Off
- Both Off
- SMS On But No Phone (opted in, no number on file — flag for cleanup)

DA controls SMS via START/STOP to the Hera number. DA controls email via the unsubscribe link in every Hera email.

### SMS best-practice rules

Not Hera rules, global SMS carrier rules:
- Full URLs only, no shorteners.
- Natural language and standard spelling. Limited emoji/slang.
- 250 characters or fewer per message.
- No references to illegal substances, including telling DAs THC/Cannabis isn't a disqualifier. That alone can get the carrier line filtered.

## Vehicle Management

Beyond photo logs:

- **Vehicle List**: filter by status, search by VIN/plate/make/model. Action menu per vehicle for status change, odometer reading, profile view.
- **Vehicle Details**: edit specs, maintenance, accident records.
- **Maintenance Reminders**: pick services from a custom list (or add new), set date/mileage trigger.
- **Maintenance Records**: with locations as a custom list, attach receipts and photos.
- **Accident Records**: OSHA-format form, video/photo/scan attachments, optionally creates Counseling + Issue if a DA is at fault.
- **Vehicle Damage**: lighter form for non-accident damage, same Counseling/Issue spawn option.
- **Bulk Updates**: change status, device, parking, vehicle type, odometer for many vehicles inline. Active vehicles only.

## Onboarding Tracker

Distinct from "Import Associates." This is the pipeline for candidates pre-hire:

- Onboarding tab in Associate Management.
- Tracks Onboarding Status, Background Check Status, Drug Test Status.
- Filter by any of those.
- Bulk-message subset (e.g., everyone who failed drug test).
- Add candidates manually or via import.

Failed candidates should be marked **Inactive - Failed Onboarding** so they don't count toward billing. Onboarding status is also non-billable. See [billing-overview.md](../billing-overview.md) for the billing logic.

## Associate Statuses (and the billing tie)

Customers don't always realize statuses drive billing. The KB calls this out explicitly: Hera bills only **Active** associates.

| Status | Billable | Use case |
|---|---|---|
| Active | Yes | Currently working |
| Inactive - Terminated | No | Fully offboarded |
| Inactive - Medical Leave | No | Out for injury/illness |
| Inactive - Personal Time/Vacation | No | PTO, short-term leave |
| Inactive - Misc | No | Anything else (KB asks for a reason in the change) |
| Onboarding | No | Candidate in process |
| Inactive - Failed Onboarding | No | Candidate didn't make it |

Three places to change status: Associate List row action menu, Associate profile status badge, Bulk Updates table. Each prompts for an optional reason.

KB explicitly tells customers to sync these to Amazon, ADP, and Paycom updates. Most billing surprises come from missed status changes.

## Reports (the auditable surface)

All under **Tasks & Reports**, search-friendly, mostly CSV-exportable. By category:

**Daily Rostering**
- Daily Report (every roster activity for a date, filterable by activity type)
- Attendance Statistics (per-DA count of each Roster Status, sortable)
- Daily Roster Standbys
- Rescuers / Rescued counts
- Total Fantastics / Fantastic Streaks

**Performance & Coaching**
- EOC Metrics (per-DA %, with up/down/flat indicator vs prior)
- Netradyne Alerts (Last 30 Days / This Week / Yesterday)
- Associate Issues (All / Last 90 Days)
- 30-Day Associate Issue Trends (with variance vs prior 30 days)
- Associate Issue Trends Graph (timeseries by issue type)
- 30-Day Repeat Offenders
- Counselings (All / Pending Signature)
- Associate Kudos

**Vehicles**
- Vehicle Maintenance Reminders / Records
- Expiring License Plates
- Incident/Accident Records

**Associates**
- Birthdays for Active Associates
- Expiring Driver's Licenses
- Issued Uniforms
- Injury Records

Plus the export buttons on Daily Roster, Vehicle List, and Associate List themselves. All exports notify via the bell icon when ready.

## Custom Lists (the configurability layer)

Most of the dropdowns in Hera are Custom Lists, editable in Company Settings > Custom Lists. Key ones:

- Counseling Type (with reusable templates)
- Counseling Severity (color-coded)
- Associate Issue Type
- Associate Kudo Type
- Vehicle Photo Log Required Photos
- Roster Status Options
- Maintenance Service Types
- Maintenance Locations

A custom value can't be deleted if it's been used historically (Hera shows "Used For" count). This protects the audit trail.

## Account-level features worth knowing

### User permissions

- "Full Admin Access" grants everything. Toggle it off to expose granular per-feature permissions.
- Document access (Associate Management: Associate Documents) is per-user. Used to lock sensitive documents to a subset of admins.
- Delete Counselings is its own permission since deletes are irreversible.

### Sensitive HR data

KB position: Hera is on AWS S3 with encryption at rest and in transit, but it's not SOC 2/SOC 3 audited. Customers are told not to store SSNs, government IDs, or PHI in Hera; use their HRIS (ADP, Paycom) for that. See [data-ownership-stance.md](../data-ownership-stance.md) for the broader retention story.

### Shared logins

KB has a dedicated article telling customers not to use shared dispatch logins. Accountability, traceability, and security argument.

### Multi-station

Separate Hera account per station, because Amazon scorecards are per-station. Email aliasing (`hera+TCO@dsp.com`) is the standard workaround for getting both accounts under one inbox.

### Hera AI Chat

Newer feature (draft KB). Answers questions about data stored in Hera. Only works on data that's actually been synced in, which is why the Amazon Plugin matters: more synced data = more useful AI Chat.

## The pattern under all of this

Every customer-facing surface in Hera is built on the same loop:

1. Data comes in (manual import, Amazon Plugin auto-sync, or Hera-generated from daily activity).
2. Hera enriches it (matches to associates, evaluates against thresholds, generates Issues / Kudos / Coaching / Counseling prompts).
3. The customer acts (sends roster, sends photo log link, reviews coaching, signs counseling).
4. The customer audits (reports, exports, downloads).
5. The record persists (long after Amazon's own retention would have cleared it).

That last point is the value proposition. Amazon collects much of the same data, but doesn't keep it accessible past about a year. Hera is the keeper of record for the DSP's operational history. Every workflow in the KB ladders back to that.
