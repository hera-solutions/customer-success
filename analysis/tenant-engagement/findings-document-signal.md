# The "driver paperwork" heartbeat is 94% vehicle photos

**Run 08-05-2026. Script: `document_breakdown.py`. Raised by John: "for the paperwork heartbeat, I want to know what that actually includes, because I think combining multiple actions for a simple upload might throw off the numbers."**

He was right, and the problem is bigger than the label.

## What the signal actually was

`document` is the newest `uploadDate` on the `Document` table. `Document` is **one table holding every file in the product, 20,277,037 rows.** Nothing in the signal distinguished what kind of file.

Measured over 90 days across all 241 paying tenants, 1,117,102 rows:

| What it is | Rows | Share |
|---|---|---|
| **Daily-log vehicle photos** | 1,054,085 | **94.4%** |
| Counseling images | 52,042 | 4.7% |
| **Filed against a person (real driver paperwork)** | **4,204** | **0.4%** |
| Incident evidence | 2,659 | 0.2% |
| Vehicle document | 1,627 | 0.1% |
| Maintenance document | 1,100 | 0.1% |
| Injury evidence | 810 | 0.1% |
| Unlinked upload | 569 | 0.1% |
| Infraction evidence | 5 | 0.0% |
| Filed into a folder | 1 | 0.0% |

**Actual paperwork is 0.7% of the signal by volume.** A heartbeat labelled "driver paperwork uploaded", carrying the second-highest churn weight in the model at 4.5, was overwhelmingly measuring **the daily vehicle check**.

Subtype comes from which foreign key is set: `documentDailyLogId` for a photo log, `documentImageCounselingId` for coaching evidence, `documentStaffId` for a document filed against a person. Checked in priority order, because a row can carry more than one.

## Why this matters beyond the wrong word

**A daily vehicle photo is taken during the driver's pre-trip check. Filing a licence is an office job.** Different action, different person, different meaning, and in Hera's terms one is a **staff** interaction and the other is a **user** action. Rolling them into one date makes the signal unreadable: a CSM told "no driver paperwork uploaded in 51 days" would open the call on the wrong subject.

## Real paperwork cannot be a heartbeat

| Definition | Tenants dark at 30 days, of 241 |
|---|---|
| Any document, the old rule | **34** |
| Real paperwork only | **164** |
| Tenants that change side | **130** |

**164 of 241 accounts have filed nothing against a person in 30 days, so absence is normal rather than exceptional.** That fails the prevalence rule already in the config: a signal firing on a minority is an expansion conversation, never a risk flag. Real paperwork belongs in the **optional / engagement** tier alongside compliance and HR at 34.9%.

## But the heartbeat is NOT redundant, which was the other worry

The concern was that photo logs hang off `DailyLog`, which hangs off the roster flow, so the document heartbeat might be a restatement of the rostering heartbeat. **It is not.**

| Pair | Both dark | Union | Jaccard |
|---|---|---|---|
| **message** and **driver count moved** | 13 | 17 | **0.76** |
| message and document | 15 | 34 | 0.44 |
| message and roster built | 15 | 41 | 0.37 |
| roster built and driver count moved | 15 | 41 | 0.37 |
| document and driver count moved | 13 | 36 | 0.36 |
| **document and roster built** | 19 | 56 | **0.34** |

Only 56% of document-dark accounts are also roster-dark, and 46% the other way. **Document and rostering are largely distinct populations, so the 3-of-4 rule is not double-counting there.**

**The pair that IS substantially redundant is message and driver-count-moved at 0.76.** Thirteen of the fifteen message-dark accounts also have a frozen driver count. On a sample of fifteen that is not conclusive, but it means the 3-of-4 rule may behave closer to 2-of-3 than intended. **Fold this into the weight re-derivation, which is already outstanding for the roster signal.**

## What changed

**The signal is kept and relabelled**, from `no driver paperwork uploaded` to `no vehicle photo log or file upload`. It earns its place on independence, not on the label it had.

**Real paperwork is now measured separately** as `staff_file` in `document-breakdown-<date>.json`, available as an engagement signal.

## The ENGAGE gap-2 email survives, but its date was wrong

The "you stopped uploading driver paperwork" email goes to 13 accounts. Checked against the breakdown:

- **All 13 genuinely have filed nothing against a person in 90 days.** The claim is true.
- **But 5 of them were flagged by their photo log lapsing, not paperwork**: FKG 39 days, Blue Heron 78, OneLove 49, KJ 32. The date the email would have quoted is the date of their last **vehicle photo**.
- So for those five the premise "you stopped" is wrong. They never started on paperwork. **They belong in the "never used it" variant, not "used it and stopped."**

**Fix: derive never-versus-lapsed from `staff_file`, and never quote a date that came from the combined signal.** This is the same class of error that got gap 3 withdrawn, caught before sending this time.

## A separate bug found on the way

Every script selected its input with `sorted(glob.glob("<prefix>-*.json"))[-1]`. **`data/usage-clamped.json` sorts after `usage-2026-08-04.json` and is a bare list rather than a dict**, so the glob silently picked a leftover working file from an earlier experiment. `document_breakdown.py` crashed on it. The same fallback in `generate_tasks.py` would have loaded it without complaining on any day the dated file was missing.

Now routed through `lib_hera.newest_dated()`, which matches `<prefix>-YYYY-MM-DD.json` only and raises if there is none.

## Verification

| Check | Result |
|---|---|
| **Input** | Read raw rows before classifying. The first tenant inspected had 21,666 of 22,696 rows carrying `documentDailyLogId` and an S3 key under `photo-log-images/<group>/vehicles/`, confirming what the field means before any aggregate was computed |
| **Cross-source** | Key-prefix classification and foreign-key classification agree: 96.8% `photo-log-images` by prefix across the 25 largest tenants, 94.4% `documentDailyLogId` by foreign key across all 241. Two independent routes to the same conclusion |
| **Follow-through** | Tested the innocent explanation, that the signal might be a legitimate proxy for rostering. It is not: Jaccard 0.34, so the signal stays |
