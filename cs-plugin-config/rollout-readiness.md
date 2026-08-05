# START HERE. Where the CS motion stands and how to resume.

**Last updated 08-05-2026. Read this first in any new session before touching the CS work.**

**Status: NOT LIVE. No customer contact is authorised. Nothing writes to Zoho.**

---

## Resume in one minute

```bash
cd ~/github/customer-success/analysis/tenant-engagement
aws sso login --profile hera-readonly      # only if the token has expired
python3 run_daily.py                        # the whole chain, dry run
```

**Never pass a back-dated `--as-of`.** It silently inflates darkness across the whole book: running 08-04 on 08-05 took ENGAGE from 34 tasks to 102. A guard warns, but do not ignore it.

`run_daily.py` runs five steps in dependency order and prints the two critical alerts first. Everything it produces lands in `data/`, which is gitignored because it holds per-customer detail.

## The four files that hold the thinking

| File | What is in it |
|---|---|
| **`csm/CLAUDE.md`** | The config the plugin actually reads. Health model, the four heartbeats and what they literally measure, the two critical daily signals, task precedence, the outreach lifecycle, ~25 data traps |
| **`csm/task-field-guide.md`** | How to fill in each of the nine task fields, with good and bad examples |
| **`adoption-conversation.md`** | The RISK call script. **DRAFT, unapproved** |
| **`csm/engage-message-templates.md`** | Four live quarterly email drafts, two withdrawn. **DRAFT, unapproved** |

Analysis and findings live in the repo at `~/github/customer-success/analysis/tenant-engagement/`. **Read the `findings-*.md` files before re-deriving anything**; several document traps that produce confidently wrong answers.

There is also a plain-language briefing for Abram and Lizz at `~/github/customer-success/briefings/2026-08-04-cs-motion-abram-lizz.html`, published as a private artifact.

## What the pipeline does today

| Step | Script | Purpose |
|---|---|---|
| 1 | `staff_history.py` | Daily billed driver count per tenant from `InvoiceLineItem.activeStaff`. **Must run first**, it feeds steps 2 and 3 |
| 2 | `driver_cliff.py` | **CRITICAL.** A sustained roster collapsing to unsustainable numbers in days |
| 3 | `usage_signals.py` | The four heartbeats and the tier per tenant |
| 4 | `roster_dropoff.py` | **CRITICAL.** Stopped assigning routes, weighted by how heavily they used to |
| 5 | `generate_tasks.py` | The task plan. **Dry run only, there is no writer** |

**Output on 08-05-2026: 64 tasks.** 1 driver cliff and 18 confirm-or-close to Matthew, 10 roster-stopped, 3 RISK and 32 ENGAGE to John.

---

## THE FOUR THINGS TO DO NEXT, in order

### 1. Put the owner's name and phone on every task

**This blocks the first call and it is a missing join, not missing data.**

The task says "call the owner." Zoho has 20 to 25 contacts per account, overwhelmingly drivers, with no role field. **Dynamo names the owner for 15 of 15 urgent accounts via `Tenant.ownerUserId` but holds no phone. Zoho has the phone. Match on email.** Lands a number for roughly 10 of 15.

See `findings-who-to-call.md` in the repo. **Caveat: `ownerUserId` may point at whoever administers the account rather than the principal**, so verify against the Zoho contact rather than asserting it on a call.

### 2. Messaging drop-off

**Human-sent message is the strongest signal in the book at 6.8 lift, and it has the exact blind spot already fixed for rostering.** A customer sending 500 messages a week who drops to five is invisible for 30 days. Copy the shape of `roster_dropoff.py`; the `Message` table is the source.

### 3. The 30-day cooldown, BEFORE any Zoho writer ships

`COOLDOWN_DAYS = 30` is defined and never referenced. Every critical task already carries an `event_key` such as `cliff:2026-07-29` so a writer can tell the same collapse from a new one, but **nothing enforces it.** Ship a writer first and the queue regenerates every morning, which is most of how it reached 217 overdue tasks.

### 4. VPL fulfilment ratio

The only driver-side signal that exists. A user sending 50 photo-log requests and getting 5 back means the driver relationship is broken. The request weighs 1.3 and the response weighs 4.5, so **the gap between them is where the information is.**

---

## Waiting on other people

| | Owner | Note |
|---|---|---|
| **Turn off the five `Last_Active1` Zoho rules** | **Matthew** | **The only item that actively interferes.** They are still firing: the five most recent tasks in Zoho are all from them, all `Not Started`. Two systems feeding one queue is how it reached 217 |
| Ratify the outcome catalog | Matthew | `provisional-1.0`, barred from customer-facing use until signed off |
| Chase or write off $2,257 | Matthew | PacTrack $1,411, Pure Logistics $846 |
| Does Matthew use the Zoho `Cases` module? | Matthew | `Cases` is permission-denied to the CS connector, so escalations after day 10 may leave no CRM record at all |
| Read the RISK script and the two email drafts | John | They need a read, not a rebuild |
| Define Abram's carve-out book | John | No account may be assigned to him until it exists, because his comp depends on it |
| Tell Lizz her role is written down | John | She has not seen it |
| Decide on the gap-3 replacement email | John | The original was withdrawn for being wrong to seven customers' faces |

---

## Known gaps, ranked, none of them blocking

**Seasonality will break the new detectors.** Amazon peak runs November to December and January collapses. **A 60-day baseline would read January as the entire book falling off a cliff. Backtest against last January before Q4.**

**Support tickets are absent from the model.** Intercom is connected. Five unresolved tickets is a churn risk no usage signal catches, and it is the only place customers complain in their own words.

**No holdout group**, so coverage can be measured but effectiveness cannot.

**The signal weights need re-deriving.** The 3.9 that put roster maintenance in the top four was derived for the old `StaffStatus` version, which turned out to be wrong half the time. The 3-of-4 rule counts signals rather than summing weights so the rule is unaffected, but whether roster maintenance still ranks fourth is unverified.

**Message and driver-count-moved overlap at Jaccard 0.76**, 13 of 15 shared. Those two are substantially redundant, so 3-of-4 may behave closer to 2-of-3. Small sample; fold it into the weight work.

**Onboarding has no config, and on the evidence that is fine for now.** Only **2.2% of churn happens in the first 90 days and 57% happens after two years**, so the motion is correctly aimed at mature accounts. `cs-ops` is also unconfigured.

**Four revenue totals do not reconcile**: $199,177 invoiced for July, $190,594 collected, $193,080 in the CEO deck, $187,274 in the health report. All defensible, all different populations. **Do not quote any of them externally.**

**Do not quote the churn lift figures outside the team.** Survivors are measured today and churns at their churn date, which inflates every magnitude. The ranking survives; the numbers do not.

**The AMP per-member rate is unknown**, so that opportunity cannot be sized. 46 accounts parked on Trial awaiting rollup billing, extension is manual and monthly.

**627 active drivers bill nothing**: MBB 321 deliberate, Outlaw 195 and Spears 111 from credits granted without CS involvement.

**The 35 stopped-scorecard accounts, $28,268/mo**, were superseded by the heartbeat model and never re-homed.

**LogRocket is unauthenticated**, and it is the best adoption diagnostic available since per-company session URLs already sit in Intercom.

**No customer call recordings exist.** Zoom holds only internal meetings, so there is no baseline for what these conversations sound like.

---

## Cleared, and how

| | Evidence |
|---|---|
| Nothing surfaced an at-risk account | Four heartbeats plus two critical daily signals, five task types, precedence order |
| Nowhere to log a call | Seven custom Zoho fields, verified live, every picklist value matching the generator |
| No owner or cadence | Everything to John, Mon-Fri run, business-day ladder, escalation on day 10 |
| Debt vanishing on churn | Confirm-or-close carries the last two invoices and requires a note |
| "18 drivers at $25 is impossible" | It was always correct. Flat monthly fee. 11 accounts are not billed per driver |
| 217 overdue tasks | Closed and audited in `zoho-task-cleanup-2026-08-03.md` |

## Two standing rules that outrank convenience

**Never write, edit or delete a Zoho Note.** Notes are the human narrative. The nine task fields are the structured record.

**Verify any production figure three ways before presenting it: input, cross-source, follow-through.** Running the same query twice is not verification. In this work alone that rule caught a stale revenue figure that had changed a routing decision, a signal that was wrong half the time, a heartbeat that was 94% mislabelled, and a back-dated run that inflated the task list from 53 to 123.
