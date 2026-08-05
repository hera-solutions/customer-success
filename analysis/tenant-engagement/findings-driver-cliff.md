# Driver rosters falling off a cliff

**Run 08-05-2026. Script: `driver_cliff.py`. Requested by John as a critical daily signal: "dropping a significant amount of associates to unsustainable numbers, for example having consistently 100+ drivers then dropping to sub 5 in the course of a couple of days or in a single day."**

## Why nothing already built catches this

| Measure | Why it misses a cliff |
|---|---|
| `driver_direction` | Reports 30-day change. A fall from 105 to 1 shows as -99%, so the **size** is visible but nothing says it happened in **one day**. 100 to 2 overnight and 100 to 2 over three months are the same number and completely different events |
| `roster_maintained` | Fires when the count **stops moving**. A cliff is violent movement, so it says nothing until afterwards |
| The four heartbeats | All days-since. Silent for 30 days |
| **The invoice** | **A month behind. See GNC below** |

## The case that proves it: GNC Transportation

Billed driver count, straight from `InvoiceLineItem.activeStaff`:

| Date | Drivers |
|---|---|
| 07-09 to 07-26 | **92 to 100 every single day** |
| **07-27** | **19** — lost 73 in one day |
| 07-29 | 7 |
| 08-03 | **1** |

**The last closed invoice, dated 07-02, still reads 80.5 average drivers and $745.84.** Billing will not reveal this until the September invoice, roughly **37 days after the event**. The daily count showed it on 07-27.

That gap is the entire argument for running this daily.

## What it found

**15 cliff or crash events in the retained window. 8 happened in one day or less. 14 are still under 5 drivers today, so they never recovered.**

| Account | From | To | Days | On | Now |
|---|---|---|---|---|---|
| **GNC Transportation** | 95 | 7 | 6 | **07-29** | 1 |
| Your Express Solutions | 153 | 1 | 6 | 03-17 | 0 |
| Probyn Inc | 126 | 6 | 5 | 04-01 | 41 |
| Motaur Express | 112 | 1 | **1** | 03-04 | 1 |
| Syndicate Logistics | 85 | 2 | 6 | 03-05 | 2 |
| Merica Delivery | 83 | 1 | 6 | 07-14 | 1 |
| Supreme Delivery | 83 | 1 | **1** | 05-31 | 1 |
| Globalteq Logistics | 80 | 0 | **1** | 07-18 | 0 |
| Infinite Delivery OPS | 80 | 0 | **1** | 04-08 | 0 |
| DnA Logistics | 78 | 0 | 4 | 04-24 | 0 |
| Next Level Logistics | 72 | 1 | 4 | 05-01 | 1 |
| Road Runners | 73 | 3 | **1** | 03-23 | 0 |
| Focus Logistics | 66 | 0 | **1** | 07-14 | 0 |
| Shandy Holdings | 58 | 5 | **1** | 01-18 | 2 |
| Envizion Logistics | 39 | 1 | **1** | 07-01 | 1 |

**Probyn Inc appears here as well as on the RISK list.** Its cliff was 04-01, 126 drivers to 6 in five days, and it recovered to 41. That is the collapse already recorded as "peaked at 200 on 11-20-2025, down 80%", now with a date and a duration attached.

## The guard that stops false alarms, and why it exists

**Three events were excluded as artifacts, and two of them would have fired a critical 6am alert about a business that never went anywhere:**

| Account | Read | Reality |
|---|---|---|
| **Cazar Logistics** | 113 to **0 on 07-04**, then 113 the next day | **Independence Day.** The billing job evidently wrote a zero. A one-day hole between two 113s |
| **Elite OnPoint** | 114 to 0 for 16 days from 06-22 | Real zeros, but it is back at **117** now |
| Commute Is Great | 51 to 1 for 3 days | Back at 64 |

So a cliff must **stick**: at least 3 consecutive days down, and the account must not have recovered to half its prior level. **A fall that does not persist is not a cliff, it is a data artifact.**

Across the whole book, zero-runs bounded by 20+ drivers on both sides are rare: **2 tenants, one a single day and one 16 days.** Rare, but both would have been false criticals.

## Verification

| Check | Result |
|---|---|
| **Input** | Read GNC's raw daily series before concluding anything: 18 consecutive days at 92-100, then 19, then 7, then 1. Also read the raw series for all three suspected artifacts, which is how the single-day 07-04 hole was found |
| **Cross-source** | `roster_dropoff.py` independently flagged GNC as `STOPPED` on rostering with cause "business shrinking", from a different table (`DailyRoster` and `Route`) via a different mechanism. Two detectors, one conclusion |
| **Follow-through** | Checked the innocent explanation, that these are billing-feed gaps rather than real collapses. It is true for 3 of 18, which is exactly why the persistence guard now exists. The other 15 held |

## A separate trap found while wiring this up, and it is a dangerous one

**Running the chain with a back-dated `--as-of` silently inflates darkness across the entire book.** Running `--as-of 2026-08-04` on 08-05 took ENGAGE from 34 tasks to **102**, and `document` dark from 34 accounts to **114**.

Nothing was broken. `to_date()` correctly clamps any date **after** `as_of` to None, because several source fields are user-entered and hold typos like `8610-07-17`. So every customer who did something **today** was scored as having done nothing, ever.

**A guard now warns loudly on any back-dated run**, and the warning is flushed so it appears before the child scripts' output rather than buried under it.

## Status and limits

**`run_daily.py` now runs the whole chain in dependency order**, with both critical detectors marked and a failure in either one called out explicitly rather than buried.

**Neither critical detector creates tasks yet.** They print and write JSON.

**The thresholds are chosen, not derived.** 20 drivers as the floor, under 5 as unsustainable, 7 days as fast, 3 days to persist. All defensible and none fitted to churn data the way the heartbeat weights were.

**Same-day detection is limited by the feed.** `InvoiceLineItem` is generated overnight, so the series runs 1 to 3 days behind. A cliff today surfaces tomorrow at the earliest, which is still 35 days sooner than the invoice.
