# Hera Outcome & Value Catalog

**Version:** provisional-1.0
**Generated:** 2026-07-30
**Ratified:** not yet. Requires review with the CEO at the weekly management meeting before any entry is used in customer-facing material.

---

## What this is, and how much to trust it

A shared vocabulary of the outcomes a Hera customer is trying to reach, so that adoption conversations, success plans, and value statements all describe value the same way instead of improvising each time.

**Every outcome below is inferred, not evidenced.** Read this before using it:

| Input | What it gave us | Quality |
|---|---|---|
| Product schema (`schema.graphql`, 3,902 lines) | The real capability surface, 90+ entity types | Strong. This is what the product actually does |
| Coaching threshold fields on `Tenant` | The Amazon scorecard metrics Hera coaches against, with Hera's own default thresholds | Strong |
| Health model (two axes) | Which behaviours correlate with retention | Medium. Tested on a 20-account pilot |
| `accountCanceledReason`, 559 churned tenants | Why accounts left, by category | Medium. A taxonomy, not customer language |
| `accountCanceledNotes` | Almost nothing usable | **Weak.** ~10 distinct internal labels, median 64 characters. Not customer voice |
| Customer interviews | Nothing. None have been done | **Absent** |

**No customer has confirmed that any of these is an outcome they care about.** The outcome statements are written in operator language because that is the correct form for a catalog, not because an operator said them.

**Validation path, agreed 2026-07-30:** the 62 monthly adoption conversations (adoption risk plus stopped scorecards) are the instrument. Each conversation tests whether the outcomes below match what that customer is actually trying to achieve, and collects the attributed quotes the value metric now depends on. Promote entries from `inferred` to `evidenced` as customers confirm them, and record who said it. Target v1.0 ratification after one quarter.

## Rules that bind every entry

- **Never state a time-saved figure.** Time saved is the benefit customers care about and is not computable from product data. Quote a customer and attribute it, or say nothing. See `csm/CLAUDE.md`, "CS methodology."
- **Cite the evidence column, not the outcome.** "Zero rosters built in 83 days" is the finding. "Not getting value" is a label on it.
- **Check entitlement first.** Accounts without `bundle` or `rostering` in `accountPremiumStatus` physically cannot roster. Flagging them for non-rostering is a false positive.
- **AMP accounts have no billing signal.** Score them on engagement only. See `../amp-cohort.md`.
- **HeraAi is excluded from all measurement by user decision.** It does not appear in this catalog and must not be added as an outcome or an attach metric.

---

## Job 1: Get tomorrow's routes staffed without working until 9pm

The core daily job. Every DSP owner does this every single day, and it is the reason most accounts sign up.

### O-1.1 Tomorrow's roster is built and staffed before the end of today

| | |
|---|---|
| **Outcome** | I know every route is covered before I leave, and I am not texting people at 9pm to fill gaps |
| **Delivered by** | `DailyRoster`, `Route`, `RouteStatus` |
| **Evidence** | Roster exists for the target date with staffed routes. `[measurable today]` |
| **Value signal** | Rosters built per week, and how far ahead the latest one reaches |
| **Stage** | Onboarding milestone, then continuous |
| **Trap** | `DailyRoster.notesDate` is the date a roster is built **for**, scheduled ahead. Never compute "days since." Roster horizon was tested as a churn signal and rejected: it rewards bulk-building a week and never returning |

### O-1.2 A same-day callout does not become an uncovered route

| | |
|---|---|
| **Outcome** | When someone calls out at 5am I can find a replacement and reassign the route in minutes, from my phone |
| **Delivered by** | `ReplaceByRoute`, `RouteStaffRescuer`, `StaffStatus` |
| **Evidence** | Replacement and rescuer records against a roster. `[measurable today, not yet instrumented in any report]` |
| **Value signal** | Replacements executed in Hera versus routes left unstaffed |
| **Stage** | Continuous. Usually the moment the product proves itself |
| **Note** | This is the highest-emotion moment in the operator's week and nothing currently measures it. Strong candidate for the first thing to instrument |

### O-1.3 The van is roadworthy and the driver has what they need before they leave the lot

| | |
|---|---|
| **Outcome** | Nobody rolls out without a checked vehicle, a device, and the day's brief |
| **Delivered by** | `RosterChecklist` and its task/item/subject tables, `Device`, `SubscribedDevices` |
| **Evidence** | Checklist completion rates per roster. `[measurable today]` |
| **Value signal** | Percentage of rosters with a completed checklist |
| **Stage** | Onboarding milestone |
| **Trap** | Empty roster shells are normal, 133 of 253 tenants have one. Use the ratio of empty to total, never the count |

---

## Job 2: Survive the Amazon scorecard

Hera coaches against Amazon's actual metrics, with per-tenant thresholds already configured on `Tenant`. This is the outcome area where Hera is closest to the customer's own performance review, and it is where 35 accounts have already gone quiet.

### O-2.1 I walk into the Amazon review knowing what my score is and why

| | |
|---|---|
| **Outcome** | No surprises in the weekly scorecard conversation. I know which drivers moved the number before Amazon tells me |
| **Delivered by** | `CompanyScoreCard`, `StaffScoreCard`, `EocScore` |
| **Evidence** | Scorecard imported within the last two weeks. `[measurable today]` |
| **Value signal** | Scorecard import recency and continuity |
| **Stage** | Continuous |
| **Why it matters** | **35 accounts worth $28,268 a month have stopped importing scorecards.** They still message drivers, so half the product has already been replaced for them. This is the single largest instance of an outcome quietly lapsing |

### O-2.2 My tier does not slip because I found out too late

| | |
|---|---|
| **Outcome** | I see a driver trending the wrong way while I can still coach them, not after the tier drops |
| **Delivered by** | Per-tenant coaching thresholds on `Tenant`: DAR (default 77), FICO (kudo at 825), speeding events, harsh braking and cornering rates, following distance, seatbelt compliance, distraction, U-turns, traffic light and sign/signal violations, PPS breaches and compliance percent, SWC, SSE, low impact, delivered-to-wrong-address, DA professionalism, daily compliance rate, overall and consecutive tier rating |
| **Evidence** | Threshold configuration plus coaching records generated against it. `[measurable today]` |
| **Value signal** | Coaching actions triggered by threshold breach, and whether anyone acted on them |
| **Stage** | Continuous |
| **Note** | The thresholds are Hera defaults on most accounts. A customer who has tuned their own thresholds is a deeply adopted customer and that is worth detecting |
| **Boundary, do not cross it** | Tier and score belong here, as outcomes the **customer** cares about. They are **banned from our risk model**, because Amazon can cancel a DSP for any reason and their performance therefore says nothing about whether they survive. Decision 2026-08-03. What counts as a Hera signal is **whether they upload the scorecard at all**, which measures adoption. See `csm/CLAUDE.md`, "Amazon scorecard: the upload is the signal, the score is not" |

### O-2.3 Delivery quality problems get caught at the photo, not at the complaint

| | |
|---|---|
| **Outcome** | I catch bad deliveries from the evidence rather than from an Amazon escalation |
| **Delivered by** | `PodQuality`, `PodQualitySummary`, `ProperParkingSequence` and summary, `CxFeedbackSummary`, `StaffCxFeedback`, `StaffNetradyneAlert` |
| **Evidence** | POD and parking summaries populated, Netradyne alerts flowing. `[measurable today, unverified]` |
| **Value signal** | Volume of quality records reviewed per period |
| **Stage** | Post-onboarding depth |
| **Note** | I have not confirmed these tables are populated in production. Check before promising this outcome to anyone |

---

## Job 3: Coach and document drivers so a termination holds up

The compliance and defensibility job. Unglamorous, and the reason some accounts stay for years.

### O-3.1 Every corrective conversation is documented, dated, and defensible

| | |
|---|---|
| **Outcome** | If I have to let someone go, I can show a written record of every warning, and it will hold up |
| **Delivered by** | `Counseling`, `Infraction`, `CoachingHistory`, `CoachingRecords`, `CounselingStatus` |
| **Evidence** | Counselings and infractions logged per period. `[measurable today]` |
| **Value signal** | Counselings logged. **One of the four components of the primary value metric** |
| **Stage** | Continuous |
| **Why it matters** | Sits outside the health model, so it adds independent evidence rather than restating the health band. Prefer it when the point is value. DBE Logistics logged 224 infractions and 2,386 kudos in 30 days on $5 legacy pricing with no rostering module: that profile is an upsell, not a risk |

### O-3.2 Good work gets recognised, not just bad work punished

| | |
|---|---|
| **Outcome** | My drivers hear from me when they do well, and it is on record |
| **Delivered by** | `Kudo`, `StaffMentor` |
| **Evidence** | Kudos logged, mentor relationships assigned. `[measurable today]` |
| **Value signal** | Kudo to infraction ratio. A heavily lopsided ratio in either direction is worth a conversation |
| **Stage** | Post-onboarding depth |

### O-3.3 Hiring paperwork and compliance records are in one place and current

| | |
|---|---|
| **Outcome** | When Amazon or an insurer asks for a drug test, physical, or licence, I can produce it without digging through email |
| **Delivered by** | `OnBoard`, `Document`, `Attachment`, `DrugTest`, `Physical`, `Uniform`, `Injury`, `TextractJob` |
| **Evidence** | Document and compliance record counts per account. `[partially measurable]` |
| **Value signal** | Documents stored, onboarding records completed |
| **Stage** | Onboarding milestone |
| **Trap** | **Document signing is not measurable.** It has no field on `Tenant` at all. Inventory management is also not measurable: it lives in the Athena app with no table in this DynamoDB account, and `featureEnabledInventoryManagement` is `true` on 949 of 954 tenant rows including long-churned ones, so it is a global default rather than a record of who bought it |

---

## Job 4: Reach the whole team at once

### O-4.1 I tell forty drivers something once, and I know who read it

| | |
|---|---|
| **Outcome** | I send one message instead of forty texts, and I can prove who saw it |
| **Delivered by** | `Message`, `MessageTemplate`, `RecurringMessages`, `PendingMessage`, `MessageReadStatus`, `MessageReader`, `Telnyx`, `ShortenUrl` |
| **Evidence** | Message volume and read status per account. `[measurable today]` |
| **Value signal** | Messenger volume. **One of the four components of the primary value metric** |
| **Stage** | Onboarding milestone, usually the first thing that sticks |
| **Trap** | `Message` is 65.7M rows. Query per group via `byGroup`, never scan. Also this signal is already Axis 2 of the health model, so citing it as value restates the health band rather than adding to it |

### O-4.2 Routine communication happens without me remembering to send it

| | |
|---|---|
| **Outcome** | The recurring reminders go out whether or not I am having a bad week |
| **Delivered by** | `RecurringMessages`, `SchedulerTask`, coaching automation |
| **Evidence** | Automated messages sent per period. `[measurable today]` |
| **Value signal** | Automated coaching messages sent. **One of the four components of the primary value metric** |
| **Stage** | Post-onboarding depth |
| **Note** | Outside the health model, so it carries independent weight. The strongest available proxy for work that did not happen by hand |

### O-4.3 My drivers actually use it

| | |
|---|---|
| **Outcome** | It is not just me in the system. My team engages with it |
| **Delivered by** | Driver-side app usage, `MessageReadStatus`, `Staff` engagement |
| **Evidence** | **Not currently measured at the driver level.** `[gap]` |
| **Value signal** | None instrumented |
| **Stage** | Continuous |
| **Why this entry exists** | A repeated churn note reads "team not using it / drivers not engaging with the platform." Manager adoption and driver adoption are different things, and the health model only sees tenant-level activity. **An account where the owner builds rosters daily but the drivers ignore the app reads as healthy until it cancels.** This is a known blind spot and the highest-value thing on the instrumentation backlog |

---

## Job 5: Keep the fleet legal, running, and accounted for

### O-5.1 Maintenance happens before the breakdown

| | |
|---|---|
| **Outcome** | I know which vans are due for service before one strands a driver mid-route |
| **Delivered by** | `Vehicle`, `VehicleHistory`, `VehicleMaintenanceReminder`, `VehicleStatus` |
| **Evidence** | Maintenance records and open reminders. `[measurable today]` |
| **Value signal** | Open (`Pending`) reminders and maintenance records in the last 90 days |
| **Stage** | Post-onboarding depth |
| **Traps** | Count open reminders via `byGroupByStatus`, never a plain `byGroup` count: there is no `createdAt` index, so `byGroup` is lifetime-ever and reaches back to 2022, which put HRH Delivery at 923 instead of 237. Vehicle history lives in the `Accident` table despite the name, indexed `byGroupByHistoryType` |

### O-5.2 Damage and incidents are recorded when they happen, with evidence

| | |
|---|---|
| **Outcome** | When a van comes back damaged I have photos and a record, not an argument |
| **Delivered by** | `Accident`, `VehicleHistory`, vehicle photo logs, `Injury` |
| **Evidence** | Incident and damage records in the last 90 days. `[measurable today]` |
| **Value signal** | Incidents and damage logged. **Counts as value captured, never as risk.** A tenant logging incidents is using Hera for compliance and getting more from it, not doing worse |
| **Stage** | Post-onboarding depth |

### O-5.3 The whole fleet is worth attention, and almost nobody is giving it any

| | |
|---|---|
| **Outcome** | (aspirational, mostly unrealised) |
| **Evidence** | **168 of 248 paying tenants use no fleet features at all while carrying 22,734 vehicles between them, and they pay $131,156 a month** |
| **Value signal** | **Upside-only. This can never lower a health band** |
| **Why** | A signal that fires on 70% of customers cannot triage. 90% have logged no odometer reading in 30 days, 72% no maintenance record in 90 days. This is one company-level product conversation, not 168 individual account problems |
| **Promotion rule** | Move fleet to the scored tier only when a majority are using it, so that absence becomes the exception |

---

## Job 6: Run the operation from one place

### O-6.1 The day's problems are written down where the next shift can see them

| | |
|---|---|
| **Outcome** | What happened today is recorded, so tomorrow's supervisor is not starting blind |
| **Delivered by** | `DailyLog`, `DailyLogHistory`, `Note`, `Task`, `StaffMention`, `VehicleMention`, fleet notes, stand-ups |
| **Evidence** | Daily log and note volume. `[measurable today]` |
| **Value signal** | Notes and logs per operating day |
| **Stage** | Post-onboarding depth |
| **Note** | Appears in the rejected graded rostering-depth score, whose top components fire on ~85% of active days and therefore compress. Useful for ranking adoption-coaching targets, not for churn prediction |

---

## The partial-value profile, and what to do with it

A repeated churn note reads: *"Only using specific features (coaching, performance, etc.) and doesn't need the full package."*

These customers **did** reach an outcome, from Job 2 or Job 3, and left because they were paying bundle pricing for it. That is a packaging problem wearing a churn label, and it is worth roughly $10,941 a month of the addressable loss.

**How to handle an account matching this profile:**

1. Do not run a save play. They are not failing to get value, they are getting a subset of it.
2. Confirm which job they actually care about, then measure the outcome for that job only. Do not score them on rostering they never wanted.
3. Route the pricing question to the CEO. There is no CS lever here, and legacy module pricing already exists ($9 bundle, standard $2, performance $3, rostering $1, staff $3, vehicles $1), so a partial-value customer may simply belong on it.
4. DBE Logistics is the reference case: zero rostering, 224 infractions and 2,386 kudos in 30 days, current scorecard, $5 legacy pricing. Read that as an upsell, not a risk.

---

## Instrumentation backlog, ranked

Ordered by how much a CS conversation would improve if it existed.

1. **Driver-side engagement** (O-4.3). The health model's largest blind spot, and named directly in churn notes.
2. **Same-day replacement and rescue volume** (O-1.2). The highest-emotion moment in the operator's week, currently unmeasured.
3. **Threshold tuning as an adoption depth signal** (O-2.2). Distinguishes a configured account from a default one.
4. **POD and parking quality population check** (O-2.3). Confirm the tables carry data before promising the outcome.
5. **Inventory management and document signing** (O-3.3). Needs RDS or the Athena API. Both are intended to become scored eventually.

---

## Changelog

- **provisional-1.0, 2026-07-30.** First generation. Basis: product schema, coaching threshold configuration, health model, churn reason taxonomy, two usable churn-note signals. No customer validation. HeraAi excluded by user decision. Trial-funnel and time-saved framings deliberately absent.
