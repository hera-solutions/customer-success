# Fleet module added as an upside-only health tier

## 1. Date, time, and scope

2026-07-30. Continuation of the 2026-07-28 session. Two things happened: the health
model gained a second tier for signals that measure value captured rather than risk,
and the open questions were moved out of chat into a tracked file with stable IDs.

## 2. What changed

### New: `analysis/OPEN-QUESTIONS.md`

The canonical open-questions list, IDs A1 through G1. Created because the A/B/C/D/E
lettering used in conversation existed nowhere in the repo and would not have survived
the session. Five A-block items had never been written down at all: A3 retention
target, A4 expansion routing, A5 legal routing, A7 success plan format, A8 renewal
conversation style.

Supersedes the 16 numbered items in section 7 of the 2026-07-28 log.

### Modified: `analysis/tenant-engagement/three_signals.py`

Collects fleet signals per tenant into an `upside` dict. Entitlement-gated: 7 of 248
paying tenants lack the vehicles module and are excluded rather than counted as absent.

### Modified: `analysis/tenant-engagement/classify.py`

Carries `upside` through untouched, renders the value-opportunities report section, and
adds `verify_upside_isolation()`.

### Modified: `analysis/tenant-engagement/README.md`, `analysis/cs-health-weekly/skill/SKILL.md`

Document the tier, the two field traps, and how to report it without causing alarm.

### Commits

- `1ffdb92` five files, 309 insertions, fleet upside tier
- Second commit: this log plus `analysis/OPEN-QUESTIONS.md`

## 3. Decisions made

**Fleet is upside-only, not scored.** John's decision, in his words: "upside only for
fleet." The reason is information content, not caution. 168 of 241 entitled tenants
(70%) log neither an odometer reading in 30 days nor a maintenance record in 90. A
signal that fires on 70% of the book cannot triage. It describes one company-level
product adoption gap, not 168 individual problems. Promote to scored only when a
majority are using it, so absence becomes the exception. Recorded as F3.

**Accidents and incidents count as value captured, not risk.** A tenant logging
incidents is using Hera for compliance and getting more from it, not doing worse.

**Inventory and document signing paused.** Recorded as F1 and F2.

**The isolation is structural, not a convention.** `r["upside"]` is assigned after every
scored signal and the bucket logic never reads it. `verify_upside_isolation()` classifies
the same synthetic tenant twice, once with every upside signal maxed and once at zero,
and asserts the bucket is identical. If someone later wires an upside signal into the
bucket logic, that test fails. The live run is the second proof: buckets came out
byte-identical to the pre-fleet run.

## 4. Technical details

### Fleet event storage

`Accident` is the polymorphic vehicle-history table despite the name. Its own
description says "Used for Accidents, Vehicle Damage, Maintenance, and Odometer
Readings." Production distribution: Odometer Reading 22,274, Maintenance 2,000,
Vehicle Damage 291, Accident 155, Incident 140.

### Indexes used

| Table | Index | Key |
|---|---|---|
| `Accident` | `byGroupByHistoryType` | group + `vehicleHistoryType#accidentDate` |
| `Vehicle` | `byGroup` | group + id |
| `Vehicle` | `byGroupAndLastOdometerReadingDate` | group + `lastOdometerReadingDate` |
| `VehicleMaintenanceReminder` | `byGroupByStatus` | group + `status#dueBySort` |

### Measured result, 241 entitled tenants

| Signal | Tenants | Share |
|---|---|---|
| No odometer reading in 30d | 218 | 90% |
| No maintenance record in 90d | 173 | 72% |
| Neither | 168 | 70% |
| Has open maintenance reminders | 103 | 43% |
| Logged an incident or damage in 90d | 79 | 33% |

$131,156/mo comes from the 168 using nothing, carrying 22,734 vehicles between them.

## 5. Things that almost went wrong

### Maintenance reminders read as 51% adoption and were not

`VehicleMaintenanceReminder` has no `createdAt` index, so a `byGroup` count is
lifetime-ever and reaches back to 2022. It was counting reminders somebody completed
three years ago as current usage. HRH Delivery read 923 reminders against 214 vehicles.

Caught because 51% was implausible next to 10% odometer usage. Verified the records are
genuinely user-created (real `userId`, specific services like "Oil Change", creation
dates spread across years rather than clustered on one provisioning day), so the table
was fine and the query was wrong. Switched to open `Pending` reminders via
`byGroupByStatus`: 43%, and HRH at 237.

**The general lesson:** a lifetime-ever count sitting in a table of 30 and 90 day
metrics looks like a rate and is not one. Check the index before trusting the number.

### I wrote a tenant count off a flag that is a global default

The first version of the report said how many tenants have inventory management enabled.
`featureEnabledInventoryManagement` and `featureAccessInventoryManagement` are both
`true` on 949 of 954 tenant rows, including long-churned ones. It is a global default,
not a purchase record, so the count meant nothing. Caught by checking the distribution
across the whole table before publishing rather than after.

This is the second time a `featureEnabled*` / `featureAccess*` field has looked like an
adoption model and not been one. **Treat every flag on `Tenant` as suspect until checked
against the full table.**

### A stale key survived a code change

Renaming `inventory_entitled` out of the code left the old key in the already-written
data file. Re-ran collection rather than hand-editing the data, which would have left a
file no code produces. The run is about two minutes, so this is always the right call.

## 6. Open items

See [`analysis/OPEN-QUESTIONS.md`](../../analysis/OPEN-QUESTIONS.md). Nothing was
answered this session. A4 got sharper: fleet upside alone identifies $131,156/mo of
untapped value with nowhere to route it, because there is no AE.

## 7. Context that matters later

**The upside tier is a pattern, not a one-off for fleet.** Any signal whose absence is
the norm belongs here. The test to apply is not "is this important" but "would flagging
its absence tell me which accounts to work today." Fleet fails that test at 70%
non-adoption while still being the largest value story in the book. Both things are
true, and the two-tier structure is what lets the report say both without the second
one drowning the first.

**Reporting order matters for this section.** A table showing 70% of customers using
nothing reads like an emergency. The skill now instructs putting it last, saying out
loud that it cannot lower a band, leading with the aggregate rather than a per-account
list, and naming the reference customers who do use it, since those are what sell fleet
to everyone else. Elevated Delivery Service logged 1,728 odometer readings and 216
maintenance records in the window.

**Committed straight to `main`.** A feature branch was created first by mistake and
fast-forwarded back. This repo's `CLAUDE.md` is explicit that John works directly on
`main` with auto-commit and push, and that PRs are the exception rather than the default.
