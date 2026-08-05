# Catching roster abandonment in a week instead of a month

**Run 08-05-2026. Script: `roster_dropoff.py`. Requested by John: "those tenants that are not using daily roster, we need to know sooner. especially if they were using it heavily before."**

## Why the heartbeat model cannot do this

Every heartbeat is **days-since-last-event against a 30-day line**. That makes two completely different customers look identical:

- one who assigned **50 routes a day for months** and stopped last Tuesday
- one who assigns a route every three weeks

Both read "fine" on day 20. **The first one has already left in every sense that matters and we would not know for another eleven days.** This is not a threshold that needs tuning; it is the wrong shape of measurement for a collapse.

## What this measures instead

Routes assigned per week, **against that tenant's own baseline**:

- **Recent window:** last 7 days
- **Baseline:** 60 days, ending 10 days ago so a drop cannot contaminate its own baseline
- **Floor:** a baseline under 5 routes a week is ignored. They were never a roster user, so there is nothing to lose and no new false positive
- **Severity is the volume lost**, not a yes or no. 367 routes a week going to zero is not the same event as 6 going to zero

## What it found: 19 accounts, and 9 nobody would have known about

| | Count |
|---|---|
| Dropping off the daily roster | **19** |
| Of those, an **adoption** problem, drivers still on the books | **14** |
| Of those, **business shrinking**, driver count collapsed too | 5 |
| **Adoption cases still inside the 30-day line**, so currently invisible | **9, $10,259/mo** |

### The adoption list, drivers still on the books

| Account | Was | Now | Drivers | Monthly | Quiet |
|---|---|---|---|---|---|
| **Tala Logistics** | **367/wk** | 0 | 132, -6% | $1,057 | **7 days** |
| **NAFE LLC** | 336/wk | 0 | 86, -2% | $769 | **10 days** |
| **Delivering Delights** | 331/wk | 0 | 129, -1% | $1,199 | **12 days** |
| **Next Phase Logistics** | 230/wk | 0 | 104, -13% | $908 | **8 days** |
| **Upside Delivers** | 228/wk | 0 | 90, -1% | $711 | 18 days |
| **Derby Deliveries** | 150/wk | 0 | 128, **+7%** | $1,071 | 20 days |
| Platinum Transport | 119/wk | 0 | 119 | $929 | 37 days |
| JDW Logistics | 109/wk | 0 | 338 | $2,937 | 22 days |
| TPE Logistics | 79/wk | 0 | 115 | $931 | 51 days |
| **Orad Logistics** | 67/wk | 0 | 112, **+7%** | $922 | **10 days** |
| Leary Logistics | 66/wk | 0 | 125, +5% | $1,070 | 57 days |
| Spears Enterprises | 56/wk | 0 | 111 | $0 | 38 days |
| **Pazzy Logistics** | 46/wk | 0 | 76 | $683 | **7 days** |
| Cargo To You | 21/wk | 0 | 94 | $828 | 54 days |

**Tala Logistics is the case that makes the argument.** 45 to 56 routes assigned every single day through July, then **exactly zero from 07-29 onward.** A cliff, not a taper. It is seven days old, the customer still has 132 drivers on the books, and **the current model classifies it ACTIVE.**

**Derby Deliveries and Orad Logistics are growing their driver count while having stopped rostering entirely.** They are hiring and dispatching somewhere else.

### The five that are NOT a CS problem

| Account | Was | Drivers now | Verdict |
|---|---|---|---|
| GNC Transportation | 279/wk | **1, down 99%** | Business shrinking |
| Globalteq Logistics | 222/wk | **0, down 100%** | Business gone |
| Merica Delivery | 222/wk | **1, down 99%** | Business shrinking |
| Focus Logistics | 130/wk | **0** | Business gone |
| Supreme Delivery | 20/wk | 1 | Business shrinking |

**The cross-reference against the billed driver count is what makes this list usable.** A roster drop only means an adoption problem if the drivers are still there. GNC went from 105 drivers to 1, so calling them about rostering would be tone deaf, and the right action is Matthew confirming or closing the account.

## Verification

| Check | Result |
|---|---|
| **Input** | Read Tala's raw daily series before drawing any conclusion. 16 consecutive days at 45-56 routes, then 6 consecutive days at exactly 0. The drop is abrupt and unambiguous, not an artifact of averaging |
| **Cross-source** | Days-since in the alert match `last_staffed_roster` from the independent signals run exactly: 7, 10, 12, 8, 10. And the detector independently re-found every account already known to be roster-dark (TPE 51d, Leary 57d, Cargo To You 54d, Spears 38d), which is the check working in both directions |
| **Follow-through** | **Ruled out the innocent explanation.** Tenants build rosters days ahead, so an account could look stopped while actually assigning routes for next week. Queried future-dated rosters for the top 10: **0 of 10 had any future route assigned.** Genuine stops, not a planning-horizon artifact |

## Data path, and why it is this one

`Route.byGroupAndTime` looks right and is useless: **`time` is a time of day, `"21:25"`.** There is no group-plus-date index on `Route` at all, and it holds 16,265,269 rows, so scanning per tenant is out.

The route ties to its roster through `routeDailyRosterId`, which **embeds the date**: `2026-08-10daybreak-logistics-94`. `DailyRoster` has `byGroupAndNotesDate` and only 554,716 rows. So: list a tenant's rosters by date, then count the routes on each one carrying a `routeStaffId`.

**Future-dated rosters are excluded**, because tenants plan ahead and counting them would score intent as work done. 36 seconds for all 241 tenants over 90 days.

## What is still open

**This does not yet create tasks.** It produces a JSON file and a printed list. Wiring it into the generator is a separate decision, because it changes call volume: **14 adoption cases against the 3 accounts currently on the RISK list.**

**The 7-day window and the 5-routes-a-week floor are chosen, not derived.** They are defensible: 7 days is the shortest window that survives a customer taking a week off, and the floor is set where a baseline stops being meaningful. But neither is fitted to churn data the way the heartbeat weights were, so **expect to move them once there are logged outcomes.**

**The same approach should work for the other heartbeats.** Messaging volume and VPL volume both have the identical problem: a heavy user going quiet is invisible for 30 days. Rostering was done first because it is what John asked about.
