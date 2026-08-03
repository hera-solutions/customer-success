# Is roster-dark a real churn signal?

**Run 2026-08-03. Script: `roster_dark_validation.py`. Reproduce with `python3 roster_dark_validation.py`.**

## Question

The health model puts roster-dark accounts whose revenue is not falling into `ADOPTION_RISK`, described as "adoption conversation, never a save play." That framing assumes those customers are not leaving. Is that true?

## Method

Every tenant that had ever paid, churned between 2025-08-03 and 2026-08-03, with a usable `firstChurnedDateTime`. For each one, find the most recent `DailyRoster` containing a route actually assigned to an associate, and compare that date to the churn date.

Eligibility is "ever built a staffed roster" rather than `accountPremiumStatus`, because **entitlement is stripped when an account churns**, so `can_roster` reads False for all churned tenants and cannot be used as a filter.

Rosters dated after the churn date are counted as active, not excluded. `DailyRoster.notesDate` is the date a roster is built **for**, so a future-dated roster was still built before the customer left.

Control group is the surviving paying tenants from `signals-2026-08-03.json`, measured against the run date.

## Result

| Group | Roster-dark 30+ days |
|---|---|
| Churned, at their churn date | **56 of 104, 54%** |
| Surviving, today | **37 of 237, 16%** |

**Lift 3.45x.** 32% of churns had not built a staffed roster for 180 days or more.

### By churn reason

| Reason | Roster-dark at churn | |
|---|---|---|
| **Cost Savings** | **13 of 16, 81%** | Strongest result |
| Stopped Using, No Explanation | 2 of 3, 67% | |
| Didn't Fully Utilize or Find Value | 8 of 13, 62% | Expected |
| Internal Processes in Use | 4 of 7, 57% | |
| Switched to Competitor (Other, LMDmax) | 8 of 16, 50% | |
| Secondary Site Closure | 3 of 8, 38% | |
| DSP Closed | 14 of 33, 42% | **Causality runs backwards** |

## What it means

**"Cost Savings" churn is mostly an adoption failure with a pricing label.** 81% of customers who left to save money had not used the core workflow in over a month. They were not price-sensitive, they were cancelling something they had stopped using, and it was a rational decision. Worth $6,614/mo in the churn data. **The answer is adoption, early. Not a discount.**

**The `ADOPTION_RISK` framing was too relaxed.** On 2026-07-30, Wilx Logistics and Clark Courier Service were the number two and three accounts in that bucket by revenue. Both churned within four days, together $3,084/mo. Then **Platinum Transport Services churned while this script was running**, 36 days roster-dark, $929/mo, reason "Switched to Competitor, Other". It was position 10 on the roster-dark survivor list produced the same afternoon.

Two of those three went to competitors. A customer paying full bundle price while using one part of the product is the easiest account in the book for a competitor to take.

Keep the value framing, because these customers are not complaining. Drop the assumption that there is time.

## Limits, stated plainly

- **This is correlation.** For `DSP Closed` the causality clearly reverses: they stopped rostering because the business ended. That row is separated out and should not be read as predictive.
- **It is not a complete predictor.** 47% of churns were still rostering within 30 days of leaving, so roughly half of churn gives no roster warning at all.
- **The counts move between runs**, because they include churns up to the run date. The first run returned 55 of 103 and the second 56 of 104 twenty minutes later, when Platinum Transport churned. Cite the run date with the number.
- **Control is measured today, churns at their own churn date.** Not a matched cohort. A stricter version would sample survivors at randomised historical dates.

## Next test worth running

Whether **relative decline against each account's own trailing baseline** beats the absolute 30-day threshold. Every signal rejected in the July baseline was absolute, and the graded depth score was rejected specifically because its components fire on 85% of active days and compress. A per-account deviation measure has never been tested and would not compress the same way.
