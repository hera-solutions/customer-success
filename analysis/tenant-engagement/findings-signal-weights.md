# Weighting usage signals by churn, and why the result is a starting point rather than a model

**Run 08-04-2026. Scripts: `usage_signals.py`, `signal_weights.py`. Weights: `signal-weights.json`.**

> **This is a CALIBRATION STARTING POINT. Do not quote the lift figures outside the team.** The limitations section is not boilerplate; two of the items in it are serious enough to change the conclusions.

## What was being decided

Which usage signals indicate a customer is at risk, and how much each should count. The weights had to come from evidence rather than judgment, so they are derived from churn.

## Method

For each of the 111 paid churns in the 12 months to 08-04-2026, measure days-since-each-signal **at that account's churn date**. Compare against the 241 surviving paying tenants measured today. The lift, share of churns dark divided by share of survivors dark at a 30-day threshold, is the weight.

Addressable churns only, n=66. `DSP Closed`, `Secondary Site Closure`, `Reduced Route Count` and `Dropped Associates to 0` are excluded because causality reverses: those customers stopped using Hera because the business ended.

Future-dated values are clamped away. Several of these fields are **user-entered event dates, not system timestamps**, and some are typos: `TextractJob` has held `8610-07-17`, `Accident` `2030-09-09`, `Counseling` `2027-05-31`. A future date is not evidence of recent activity. Before clamping, a single counseling dated 08-31-2026 made Your Express Solutions read as active 27 days in the future when its real last activity was 85 days earlier.

## The weights

| Signal | Addressable churns dark | Survivors dark | Lift = weight |
|---|---|---|---|
| **Human-sent message** | 42.4% | **6.2%** | **6.8** |
| **Document upload** | 63.6% | 14.1% | **4.5** |
| **Staffed roster** | 72.7% | 17.0% | **4.3** |
| **Associate status change** | 48.5% | 12.4% | **3.9** |
| Infraction | 62.1% | 21.2% | 2.9 |
| Counseling | 66.7% | 23.2% | 2.9 |
| Kudo | 66.7% | 24.5% | 2.7 |
| Textract / scorecard OCR | 56.1% | 22.8% | 2.5 |
| Scorecard | 71.2% | 29.9% | 2.4 |
| Attachment | 75.8% | 34.4% | 2.2 |
| Vehicle history | 90.9% | 68.5% | 1.3 |
| Daily log | 77.3% | 58.5% | 1.3 |
| **Odometer** | 100% | **91.3%** | **1.1, weight 0** |

**Messaging is the strongest signal in the book.** Only 6.2% of surviving customers have gone 30 days without a human-sent message. It is the most reliable heartbeat, and it was nearly omitted because the churn dataset did not carry it.

**Document upload beating rostering was not expected** and deserves independent confirmation before it drives anything customer-facing.

**Odometer is confirmed worthless as a risk signal**, 100% of churns and 91.3% of survivors both dark. That independently reproduces the existing fleet upside-only rule from a different direction.

## The rule

The top four signals, weight 3.9 and above, are the **heartbeats**: human-sent message, document upload, staffed roster, associate status change.

**RISK = dark for 30 days on 3 or more of the 4 heartbeats.**

| Rule | Catches | False positives | Lift | Accounts | DBE test |
|---|---|---|---|---|---|
| Additive score of all weights ≥ 15 | 65.2% | 14.5% | 4.49 | 35 | **FAIL** |
| Dark on ≥1 heartbeat | 83.3% | 26.6% | 3.14 | 64 | **FAIL** |
| Dark on ≥2 heartbeats | 65.2% | 10.8% | 6.04 | 26 | **FAIL** |
| **Dark on ≥3 heartbeats** | **48.5%** | **6.6%** | **7.30** | **16** | **pass** |
| Dark on all 4 | 30.3% | 5.8% | 5.22 | 14 | pass |

**3-of-4 was chosen for correctness, not optimality. 2-of-4 has materially better recall, 65.2% against 48.5%.** What rules it out is that it flags DBE Logistics, which is dark on document upload and rostering while active on messaging, scorecard, infractions and kudos within three days. DBE must never read as at-risk. It is not ignored: it lands in the ENGAGE tier, where the conversation is about its two gaps rather than its survival.

**The additive score was abandoned because it counted absence without accounting for presence.** DBE is dark on six signals and active on six others, scored 16.5, and got called at-risk.

## Output tiers, 08-04-2026

| Tier | Accounts | Rule |
|---|---|---|
| **RISK** | **16** | Dark on 3+ heartbeats |
| **ENGAGE** | **48** | Active overall, dark on 1 or 2 heartbeats |
| ACTIVE | 177 | No heartbeat dark |

**Two independent validations in the RISK list.** Spears Enterprises tops it at $1,120/mo, and was separately identified from billing as having received a 100% discount labelled "Non Usage." Two unrelated routes reached the same account. Platinum Transport also appears, and churned to a competitor on 08-03-2026, one day after the signal snapshot.

## Limitations, and two are serious

**1. The comparison is structurally biased and it inflates every lift figure.** Survivors are measured today, churns at their own churn date. A surviving customer's most recent activity is recent by definition. **Fixing this needs per-signal history so survivors can be sampled at randomised historical dates.** Only the latest date per signal was pulled, so it cannot be reconstructed from the cached data. **The ranking survives the bias because it affects all thirteen signals in the same direction. The magnitudes do not.**

**2. The rule was selected from six variants on 66 events, after seeing the results.** The gap between 48.5% and 65.2% is 32 events versus 43. That could flip with a different twelve-month window. This is model selection on a sample too small to distinguish the candidates reliably.

**3. Correlation, not causation.** Nothing here establishes that going dark causes churn rather than accompanying it.

**4. 30 days is inherited, not derived.** It matches the existing abandonment threshold so the two are comparable, but no separate distribution work justifies it for these signals.

## What would settle it

Sixty-four logged conversations. The six adoption-conversation fields in Zoho capture outcome per account, so one quarter of real calls will discriminate between 2-of-4 and 3-of-4 far better than further retrospective fitting on this dataset.

Do the matched-cohort test before any lift figure is used outside the team.
