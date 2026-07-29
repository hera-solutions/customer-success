# Customer Success Health Baseline

**Revision 3, 2026-07-29.** Revisions 1 and 2 were published 2026-07-28.
**Source:** live queries against production DynamoDB (AWS `530079012632`, `us-east-2`, profile `hera-readonly`)
**Cached query output:** `data/` in this folder

---

## 0. Revision history, and what to trust

### Read this first

Revisions 1 and 2 both got the money wrong, in opposite directions, for the same underlying reason: **I used a revenue field without first verifying what it measured.** Revision 3 is verified against invoice line items, which is the ground truth.

| Measure | Rev 1 | Rev 2 | **Rev 3 (verified)** |
|---|---|---|---|
| Price per associate | not known | $7.83 | **$9.00/month, $0.30/day** |
| Total ARR | $2,097,712 | $1,987,326 | **$2,341,619** |
| GRR, all causes | 77.1% | 70.3% | **85.5%** |
| GRR, addressable | 85.7% | 77.2% | **95.0%** |
| Change inside surviving accounts | not measurable | -7.0% | **+13.9%** |
| Book direction | not measured | -$193,298/yr | **+$160,133/yr** |
| Largest account vs median ARR | 2.0x | 2.0x | **3.8x** |
| Accounts at real revenue risk | 31 | 12 | **15** |

### What caused each error

**Revision 1** used `Tenant.averageMonthlyInvoiceTotal`. That is a **lifetime average**, so for any account that grew or shrank it reports what they used to pay.

**Revision 2** used `Invoice.invoiceTotal` from the most recent invoice. But **every one of those invoices had status `Pending`**, meaning an in-progress month still accruing. Comparing a 26-day partial month against full months made every account look like it was losing revenue, which manufactured the "-$193,298 book decline" and the "-7.0% survivor shrinkage." Both were artifacts.

**Revision 3** uses the most recent **closed** invoice (`status != 'Pending'`, median 57 days old, the June cycle), and confirms the rate against `InvoiceLineItem` records.

### How the pricing is now verified

`InvoiceLineItem` holds **one row per day** with that day's `activeStaff` count and `bundleCost: 9`. Example, from Express Package System's June invoice: on day 26, `activeStaff` was 203 and `bundleCostExt` was 60.9, which is exactly 203 x 9 / 30. Closed invoices across that account show $8.963, $8.987, $8.999, $8.991, $9.042 per associate. Across the book, 179 of 240 accounts bill within 5 cents of $9.00.

**John's $0.30/day framing is literally how the system bills.**

### Conclusions that changed in revision 3

1. **You are already past the 90% addressable GRR target**, at 95.0%. Revision 2 said you were at 77.2% and needed $295,734 a year to reach it. That was wrong.
2. **The book is growing**, +1,483 associates and +$160,133 a year in run rate.
3. **Surviving accounts expanded 13.9%.** They hire more drivers, and your revenue follows automatically.
4. **13 of 30 declining accounts are roster cleanups, not lost business.** See section 3.
5. **The homogeneity finding is weaker than stated.** The largest account is 3.8x the median, not 2.0x, and the largest is $34,596 ARR, not $16,179.

### Conclusions from earlier revisions that still hold

Roster horizon measures feature adoption rather than churn risk. Login recency is a weak signal. The churn-reason analysis in section 7. The addressable versus program-closure split. The data quality register.

---

## 1. Glossary

### Money

| Term | Meaning | Your number |
|---|---|---|
| **ARR** | Annual Recurring Revenue. What a customer pays across a year | Median $9,108. Book: $2.34M |
| **GRR** | Gross Revenue Retention. Of the revenue you had a year ago from customers you already had, how much remains. Ignores new customers and upsells. Never above 100% | 85.5% |
| **NRR** | Net Revenue Retention. Same, but counts upgrades, so it can exceed 100% | Not formally measured, but survivors grew 13.9% |
| **Run rate** | What you bill right now, projected forward | |
| **Contraction / expansion** | An existing customer paying less, or more, without leaving | +13.9% this year |

### Roles

| Term | Meaning |
|---|---|
| **CS** | Customer Success. Keeping customers using the product and paying |
| **CSM** | Customer Success Manager. Owns relationships for a set of customers |
| **CSS** | Customer Success Specialist. Your two team members |
| **AE** | Account Executive. A salesperson. Hera has none, so expansion signals have nowhere to route |

### Process

| Term | Meaning |
|---|---|
| **QBR** | Quarterly Business Review. A scheduled meeting showing a customer the value they received |
| **SLA** | Service Level Agreement. A promised response time |
| **Health score** | A rating computed from signals, to decide who needs attention |
| **Whitespace** | Something a customer could buy but has not. Your 221 accounts without HeraAi |

### Statistics

| Term | Meaning |
|---|---|
| **p50, p75, p90** | Percentiles. p50 is the median. p90 means 90 percent of accounts fall below it |
| **r = 0.963** | Correlation, -1 to 1. How tightly two things move together. 0.963 is near lockstep |
| **Cohort** | A fixed group of accounts followed over time, so new customers do not mask churn |

### Hera domain

**DSP** is Delivery Service Partner, your customer. **DA** or associate is a driver. Amazon scorecard metrics: FICO, DCR, DC DPMO, DAR, DNR.

---

## 2. How billing works (verified)

**$9.00 per ACTIVE associate per month, charged as $0.30 per associate per day.**

Only `status = 'Active'` associates bill. `Onboarding` and every `Inactive - *` status do not. Every associate figure in this document counts Active only.

### Verified structure

| | |
|---|---|
| `InvoiceLineItem` granularity | one row per day |
| Daily charge | `activeStaff` x `bundleCost` / 30 |
| `bundleCost` | **9** |
| Correlation, associate count to invoice total | **r = 0.963** |
| Accounts with a per-associate variable component | 242 of 243 |
| Accounts with any flat monthly fee | **4** |
| Accounts billing within 5c of $9.00 | 179 of 240 |
| Accounts discounted below $8.50 | **58** |
| Effective realized rate across the book | **$8.22** |

### Module price list, from the line items

| Module | Monthly per associate |
|---|---|
| **Bundle** (what almost everyone is on) | **$9** |
| Standard | $2 |
| Performance | $3 |
| Rostering | $1 |
| Staff | $3 |
| Vehicles | $1 |
| Sum if bought separately | $10 |

Bundle at $9 is a 10 percent discount against $10 a la carte.

### Three consequences

**Associate count is not a usage metric, it is the invoice.** A customer losing 20 associates has already cut your revenue by $180 a month. There is no renewal event to intervene at, because Hera is month-to-month (section 12).

**`Invoice` is a monthly time series of associate count per account.** 25,773 records. This is the most useful dataset for health scoring, and revisions 1 and 2 both missed it.

**You have almost no pricing lever inside an account.** The rate is fixed and only 4 accounts carry a flat fee, so Hera grows when customers hire and shrinks when they do not. The only way to lift revenue per associate is to sell something not priced per associate, and HeraAi sits at 13 percent adoption.

### 8 accounts bill $0 despite having associates

| Associates | Account |
|---|---|
| **301** | MBB Delivery, LLC |
| 185 | Outlaw Logistics |
| 125 | Cazar Logistics LLC |
| 117 | Straightaway Delivery LLC |
| 91 | Red Stick Logistics & Transportation |
| 73 | Philosophe LLC |
| 62 | Integrated Logistics Solutions |
| 60 | Sarkat Logistics, LLC |

1,014 associates, 4.3 percent of your billed base, representing **$109,498 a year** of foregone billing. All show status `Paid` at $0, so these look deliberately comped rather than broken. **MBB Delivery is your second-largest account by associate count and pays nothing.** Worth confirming each is intentional.

---

## 3. Roster hygiene, and why it distorts the risk list (new in revision 3)

John's point: **the customer decides when an associate moves to Inactive, and it does not always happen when it should.** Hera leaves that responsibility with the tenant.

That has a direct measurable consequence, and it reclassifies a third of my risk list.

### Bulk cleanups are detectable

`StaffStatus` records every transition with `previousStatus` and `currentStatus`. A customer who lets the roster go stale and then tidies it produces a spike: many `Active` to `Inactive` transitions on a single day. Genuine attrition spreads out over months.

Of the 30 accounts whose associate count fell 10 percent or more:

| Pattern | Accounts | ARR |
|---|---|---|
| **Roster cleanup**, a data-hygiene correction | **13** | $16,562 |
| **Real attrition**, gradual loss | **15** | $113,844 |
| Mixed | 2 | $14,137 |

**1,109 associates were moved to Inactive on a single day across those 13 accounts**, ending $119,772 a year of billing.

### Cleanup, not churn: 13 accounts

| Account | Associates now | Change | Monthly | Biggest single day inactive |
|---|---|---|---|---|
| Your Express Solutions LLC | 0 | -100% | $0 | **152 on 2026-03-17** |
| Infinite Delivery OPS LLC | 0 | -100% | $0 | 80 on 2026-04-09 |
| DnA Logistics Inc. | 0 | -100% | $0 | 74 on 2026-04-24 |
| Next Level Logistics | 1 | -99% | $0 | 69 on 2026-05-01 |
| Supreme Delivery | 1 | -99% | $9 | 82 on 2026-05-31 |
| Ursa Logistics LLC | 2 | -99% | $9 | **150 on 2026-05-05** |
| Motaur Express | 1 | -91% | $9 | **112 on 2026-03-04** |
| Syndicate Logistics LLC | 2 | -84% | $18 | 82 on 2026-03-06 |
| Probyn Inc | 41 | -66% | $369 | 106 on 2026-04-01 |
| **Outlaw Logistics** | **185** | -36% | $0 (comped) | 98 on 2026-03-30 |
| Red Stick Logistics & Transportation | 91 | -31% | $0 (comped) | 36 on 2026-03-13 |
| Envizion Logistics LLC | 68 | -26% | $562 | 57 on 2026-06-17 |
| MTSL | 45 | -20% | $405 | 11 on 2026-04-09 |

Peak transitions per minute run 4 to 12, so these are people working through the interface over an hour or two, not API bulk loads. Someone sat down and cleaned up.

Note that Outlaw Logistics still has 185 associates and Red Stick has 91. **They are not dying, they corrected their data.**

### Real attrition: 15 accounts, $113,844 ARR

This is the list that deserves attention.

| Account | Associates now | Change | Monthly | Roster last built |
|---|---|---|---|---|
| Road Runners Enterprises | 3 | -95% | $27 | 192 days ago |
| D4 Delivery Solutions - MMRO | 32 | -28% | $261 | yesterday |
| CamCash Logistics | 67 | -20% | $548 | today |
| Whiterecon Logistics | 110 | -20% | $796 | today |
| S&S Shipping LLC | 65 | -18% | $582 | today |
| Broward Delivery | 73 | -17% | $654 | 343 days ago |
| RBHJAX Consulting | 53 | -16% | $478 | 29 days ago |
| Add Logistics, LLC | 87 | -15% | $787 | 65 days ago |
| Proactive Logistics Home Inc | 109 | -15% | $985 | 277 days ago |
| AngryByrd Logistics | 101 | -14% | $910 | today |
| Unbound-Holdings | 72 | -13% | $649 | today |
| Angel Transportation | 101 | -13% | $905 | 131 days ago |
| Milestone Delivery Inc | 49 | -12% | $442 | today |
| SURF Logistics | 114 | -11% | $927 | 18 days ago |
| Commute Is Great Logistics | 60 | -11% | $534 | today |

**Seven of these built a roster today.** They are actively engaged and quietly shrinking. No roster-based, login-based, or engagement-based signal would surface any of them.

### The uncomfortable part

Because billing follows Active status and the customer controls that status, **an account that has not cleaned up is paying for associates who already left.** Before its cleanup, Ursa Logistics was billing for roughly 150 associates it no longer employed, about $1,350 a month.

Three things follow, and they are business decisions rather than analysis:

1. **Proactively helping customers tidy their roster reduces your revenue.** A "let's clean up your roster" play is good service that costs money. That tension should be decided deliberately.
2. **A customer who works this out independently has a refund conversation, not a renewal conversation.** "Cost Savings" is already 10.3 percent of your churn, 48 accounts.
3. **Associate-count decline is ambiguous as a signal** until you check whether it was a cleanup. That check is cheap: one `StaffStatus` query per account.

### Still unmeasured, and it is the top follow-up

**How much phantom billing is happening right now.** The 13 cleanups are accounts that already corrected. The open question is how many currently-Active associates across the other 240 accounts have not worked in months. Testable by cross-referencing Active associates against recent `Route` assignments. That number is your exposure, and knowing it is better than a customer finding it first.

---

## 4. What the book looks like **[REVISED]**

| | |
|---|---|
| Total tenant records | 953 |
| Test and temporary (excluded) | 81 |
| **Active paying accounts** | **253** |
| Trials in flight | 68 |
| Lapsed trials | 54 |
| Churned | 497 |
| **ARR, last closed invoice** | **$2,341,619** |
| ARR, `Paid` invoices only | $2,271,770 |
| **Billed active associates** | **23,734** |
| Effective rate | $8.22 per associate |
| Median tenure | 40 months paid |
| Customer type | 100 percent Amazon DSP (802 ZL, 68 XL, 2 Lite) |

Coverage book is **321 accounts**: 253 paying plus 68 trials.

**Data freshness note.** The most recent closed invoice is the June cycle, 57 days old for every account. July is still accruing as `Pending`. So "current" here means June. Do not use `Pending` invoices for revenue.

---

## 5. Account size distribution **[REVISED]**

From closed invoices, which changes the shape from what revisions 1 and 2 reported.

| Percentile | Monthly | ARR |
|---|---|---|
| p10 | $457 | $5,482 |
| p25 | $606 | $7,267 |
| **p50** | **$759** | **$9,108** |
| p75 | $1,012 | $12,143 |
| p90 | $1,234 | $14,803 |
| p95 | $1,471 | $17,651 |
| **max** | **$2,883** | **$34,596** |

**Largest account is 3.8x the median**, not the 2.0x I reported twice.

| | Share of ARR |
|---|---|
| Top 10 accounts | 8.9% |
| Top 20 accounts | 16.0% |
| Top 50 accounts | 33.9% |

**The conclusion still holds but is weaker than I stated.** In most business-to-business software the largest account is 50 to 100 times the median, and the top decile carries 40 to 60 percent of revenue. At 3.8x and 16 percent for the top 20, revenue tiering would still produce buckets that behave similarly. But this is not as flat as "2.0x" implied, and if you enter a market with different economics, re-check it rather than assuming.

### Associates per account

| | |
|---|---|
| Total active | 23,734 billed (Staff snapshot: 22,888) |
| Median per account | 89 |
| p25 / p75 | 69 / 112 |
| p90 / p95 | 138 / 158 |
| Largest | 338 (JDW Logistics) |

86 percent of accounts run between 50 and 199 active associates. The two totals differ because the invoice figure is a monthly average and the Staff figure is a point-in-time snapshot. Use invoice for revenue, Staff for operational size.

---

## 6. Retention **[HEAVILY REVISED]**

Cohort method: the 305 accounts already paying in June 2025, followed to June 2026, using closed invoices at both ends. New customers acquired during the year are excluded.

| | Amount | Accounts |
|---|---|---|
| Cohort ARR, June 2025 | **$2,430,676** | 305 (24,786 associates) |
| Lost, Amazon DSP program closure | -$243,393 | 34 |
| Lost, addressable churn | -$362,697 | 47 |
| **Change inside surviving accounts** | **+$254,260** | 224 (**+13.9%**) |
| **ARR, June 2026** | **$2,078,846** | 224 (21,003 associates) |

| Measure | Result |
|---|---|
| **GRR, all causes** | **85.5%** |
| **GRR, addressable** | **95.0%** |
| Program-closure drag | 10.0% |

```
addressable base = $2,430,676 - $243,393 = $2,187,283
addressable GRR  = $2,078,846 / $2,187,283 = 95.0%
```

### Your surviving customers expand on their own

Surviving accounts grew **13.9 percent**, worth $254,260. Because billing follows headcount, that expansion happened without a sales motion. It is the single healthiest fact in this analysis, and revision 2 reported it as a 7.0 percent decline.

### The target needs rethinking

| Target | Gap from 95.0% |
|---|---|
| 85% addressable GRR | already exceeded by $219,656 |
| 90% addressable GRR | already exceeded by $110,292 |
| 95% addressable GRR | met, within $928 |

**The 90 percent target set during setup is already achieved.** Recommend replacing it with something that still has room: 96 to 97 percent addressable GRR, or a target on all-causes GRR (85.5 percent today), or a target on the trial funnel, which is entirely unmeasured.

---

## 7. Why customers leave

Unchanged from earlier revisions. `accountCanceledReason` populated on 430 of 497 churned accounts, `accountCanceledNotes` on 312.

### Lifetime, 469 paid churns

| Reason | Accounts | Share | Preventable by CS? |
|---|---|---|---|
| **DSP Closed** | 181 | 38.7% | **No.** Went out of business |
| **Didn't Fully Utilize or Find Value** | 92 | 19.7% | **Yes** |
| (blank) | 60 | 12.8% | Unknown |
| Cost Savings | 48 | 10.3% | Partly |
| Switched to Competitor | 56 | 12.0% | Yes |
| Internal processes | 9 | 1.9% | Partly |
| Route reduction, site closure, dropped to zero | 12 | 2.6% | No |
| Stopped Using, No Explanation | 6 | 1.3% | Yes |

About 41 percent is the Amazon DSP program churning, not Hera. About 45 percent is addressable.

### Trailing 12 months

| Reason | Accounts | ARR lost |
|---|---|---|
| **Switched to competitor** | **20** | **$148,097** |
| Didn't Fully Utilize or Find Value | 10 | $84,226 |
| Cost Savings | 7 | $54,988 |
| Internal processes | 5 | $37,201 |
| Stopped Using, No Explanation | 3 | $19,218 |

**Competitive loss is now your largest addressable bucket.**

### Competitors, from your own records

| Competitor | Lifetime | Last 12 months |
|---|---|---|
| DSPworkplace | 23 | 5 |
| LMDmax | 17 | 6 |
| **"Other", unnamed** | **13** | **11 ($82,472)** |
| Manage my DSP | 1 | 2 |
| Lokiteck | 2 | 1 |

**Your largest single competitive loss this year is to a competitor nobody recorded.**

### Timing

Median tenure at churn 18 months (p10 5, p25 10). **29 percent churned inside 12 months** against a 40-month median for survivors.

---

## 8. Health signals, ranked **[HEAVILY REVISED]**

### Primary: associate-count trend, cleanup-adjusted

Associate count is the revenue, so its direction is the health signal. But per section 3 it must be checked against `StaffStatus` for bulk cleanups first, or you will chase 13 accounts that simply tidied their data.

Whole book, last four closed invoices:

| Direction | Accounts | Associate change | Run-rate change |
|---|---|---|---|
| Growing more than 10% | **98** | +2,415 | **+$260,873/yr** |
| Stable | 123 | +183 | +$19,773/yr |
| Down 10 to 25% | 16 | -232 | -$25,050/yr |
| Down 25 to 50% | 4 | -181 | -$19,529/yr |
| Down more than 50% | 10 | -703 | -$75,934/yr |
| **Net** | **251** | **+1,483** | **+$160,133/yr** |

**98 accounts growing against 30 declining, and 13 of those 30 are cleanups.** The book is healthy.

### Secondary: roster horizon (feature adoption, not risk)

| Band | Accounts |
|---|---|
| Scheduling today or ahead | 173 |
| Stopped 1 to 30 days ago | 35 |
| Stopped 31 to 90 days ago | 17 |
| Stopped over 90 days ago | 8 |
| No record or corrupt date | 29 |

**Roster horizon missed 10 of the accounts that were actually losing revenue**, including Envizion Logistics (down 99 percent, rostered 27 days ago) and Next Level Logistics (down 99 percent, rostered 15 days ago). Seven of the 15 real-attrition accounts built a roster today. Treat roster horizon as an adoption metric, never as the primary risk signal.

### Weakest: login recency

Of the 25 accounts lapsed 30 or more days on rostering, 10 logged in within 7 days and 4 logged in the same day.

---

## 9. Factor menu **[REVISED]**

"Measurable" means the right index exists to compute it cheaply per account, roughly 253 fast queries, but it has not been run.

### Group A: Revenue and scale (primary)

| Factor | Source | Status |
|---|---|---|
| **Active associate count** | `Invoice.averageActiveDriverCount` | **Measured** |
| **Associate trend** | consecutive closed `Invoice` records | **Measured**, 251 of 253 |
| **Bulk cleanup detection** | `StaffStatus`, `byGroup` = group + date, fields `previousStatus` / `currentStatus` | **Measured** for the 30 declining accounts |
| Onboarding pipeline | `Staff`, `byGroupStatus`, status `Onboarding` | Partly measured |
| Year-over-year seasonality | `Invoice`, 25,773 records | **Not measured. Still the top gap** |
| **Phantom-billing exposure** | Active associates vs recent `Route` assignments | **Not measured. New top priority** |

### Group B: Daily workflow

| Factor | Source | Status |
|---|---|---|
| Roster horizon | `DailyRoster`, `byGroupAndNotesDate` | **Measured.** Adoption, not risk |
| Messaging volume | `Message`, `byGroup` = group + createdAt | Measurable |
| Daily log volume | `DailyLog`, `byDate` = group + date | Measurable |

### Group C: Paid-for features

| Factor | Source | Status |
|---|---|---|
| Scorecard upload freshness | `CompanyScoreCard`, `byGroup` = group + yearWeek | Measurable |
| Coaching activity | `Counseling`, `Infraction`, `Kudo`, all `byGroupAndDate` | Measurable |
| Feature adoption | `Tenant` flags | **Measured** |

| Feature | Using it | Share |
|---|---|---|
| `featureEnabledCounselings` | 233 | 92% |
| `featureEnabledAssociateApp` | 146 | 58% |
| `permissionHeraAi` | **32** | **13%** |

HeraAi is your clearest expansion opportunity and, per section 2, one of the only ways to raise revenue per associate.

### Group D: Viability (not CS-fixable)

| Factor | Source | Status |
|---|---|---|
| Route volume trend | `Route`, `byGroupAndTime` | Measurable |
| Associate turnover | `StaffStatus`, `byGroup` | Measurable |
| Amazon scorecard tier | `CompanyScoreCard`, 88,580 records | Measurable |

### Group E: People

| Factor | Source | Status |
|---|---|---|
| Login recency | `User`, `gsi-TenantUsers` | **Measured.** Weak |
| Never-logged-in seats | `User` | **Measured.** 622 of 3,672, 17% |

### Group F: Commercial

| Factor | Status |
|---|---|
| **Discount depth** | **Measured.** 58 accounts below $8.50/associate. Predicts "Cost Savings" churn |
| **Comped accounts** | **Measured.** 8 accounts, 1,014 associates, $109,498/yr foregone |
| Unpaid balance | **Measured.** 3 accounts, $3,053. Not a meaningful signal |
| Tenure | **Measured.** Under 12 months is the danger zone |
| Support volume and sentiment | **Not pulled.** Intercom connector works |

### Ruled out

**Audit-log activity.** `AuditLog` is indexed on group plus `email#createdAt`, so there is no date range query across all users. Roughly 27,000 rows per account. Too expensive to schedule.

---

## 10. Proposed band definitions **[REVISED]**

| Band | Rule |
|---|---|
| **Critical** | Associates down more than 50% **after ruling out a cleanup**, or zero associates, or 3+ red factors |
| **At Risk** | Associates down 10 to 50% after ruling out a cleanup, or 2 red factors |
| **Developing** | Associates down 5 to 10%, or 1 red factor |
| **Healthy** | Associates flat or growing, no red factors |
| **Adoption gap** | Growing or flat, but a core feature unused. **Not a risk band.** Route to an adoption conversation |
| **Data hygiene** | Decline explained by a bulk `StaffStatus` cleanup. **Not a risk band.** Billing corrected itself |

The last two bands exist because of real accounts that would otherwise be mishandled.

**The cleanup check is mandatory before assigning a risk band.** One `StaffStatus` query per account, filtering `previousStatus = 'Active'` and `currentStatus` starting with `Inactive`, then testing whether one day holds 40 percent or more of the transitions.

**Thresholds remain provisional** until the seasonality question is answered. A 10 percent summer decline may be normal.

**Keep Health and Viability separate.** 38.7 percent of churn is customers losing their Amazon contract. Blending that in makes the score unactionable.

---

## 11. Data quality register **[REVISED]**

| Field | Problem | What to do |
|---|---|---|
| **`Invoice.status = 'Pending'`** | The current in-progress month, still accruing. Comparing it against closed months makes every account look like it is shrinking | **Filter to closed invoices for any revenue figure. This produced every wrong number in revision 2** |
| **`Tenant.averageMonthlyInvoiceTotal`** | A lifetime average, not current billing | Use the latest closed `Invoice.invoiceTotal`. **Produced every wrong number in revision 1** |
| **`StaffStatus` status field** | The field is `currentStatus` and `previousStatus`, **not** `status` | Projecting `status` returns nothing and looks like "no transitions exist." **Caught me: I first concluded zero cleanups across 30 accounts** |
| **Associate status** | Only `Active` bills. **The customer controls it and often lags** | Always filter to `Active`. Always check for bulk cleanups before reading a decline as churn |
| `DailyRoster.notesDate` | The date a roster is built **for**, scheduled ahead, not a creation time. Healthy accounts have a future date | Use horizon: latest date minus today, never "days since" |
| `User.lastLogin` | Can hold the literal string `NOT_YET_LOGGED`, which sorts above real timestamps | Filter before any `max()`. Silently dropped 118 of 253 accounts |
| `InvoiceLineItem.month` | Zero-indexed. June appears as `month: '5'` | Do not read it as a calendar month |
| `Invoice.year#month` | Per repo `CLAUDE.md`: December stored as `<next-year>#0` | Filter on `createdAt` |
| Zero-value invoices | 8 accounts show `Paid` at $0 with associates present | Comped accounts. Exclude from rate calculations, include in ARR at $0 |
| `firstChurnedDateTime` | Missing on 267 of 497 churned | Use `customerStatus` |
| `firstConvertedToPaidDateTime` | Sparse | Use `totalNumberOfMonthsPaidByTenant > 0` |
| `numberOfSeats` | Absent on 198 of 253 | Irrelevant anyway, billing is per associate |
| `accountType` | Null on 502 of 872, `PARENT` / `CHILD` never used | Multi-entity rollup does not work |
| `featureAccessX` vs `featureEnabledX` | Access is not a superset of enabled | Do not compute a gap between them |
| `cost*` on `Tenant` | Nonzero on all 253 | Price-list fields, not entitlement |
| `DailyRoster.notesDate` range | 8 accounts have implausible values | Clamp to roughly -2000 to +400 days |
| No roster record | 21 active accounts have none | Unclassified, not healthy |
| Contract dates | **No contract, term, renewal, or expiration field exists** | Month-to-month. No renewal event. Associate loss hits revenue immediately |

---

## 12. What we still have not uncovered

**1. Phantom billing exposure, right now.** New top priority, from section 3. How many currently-Active associates have not been on a route in months? That is what customers will discover, and it is measurable via `Route`.

**2. Seasonality.** Every threshold comes from a snapshot with four months of trend. `Invoice` holds 25,773 records going back years, so year-over-year is computable. Less alarming now that the book is growing, but still needed before finalizing thresholds.

**3. How "DSP Closed" gets recorded.** The addressable split and CSS 1's bonus rest on this one field. Who fills it in, and how do they know?

**4. Is Amazon growing or culling the DSP program?** Drives 38.7 percent of churn, appears nowhere in the data.

**5. Is $9 per associate above or below market?** Competitive switching is your largest addressable loss at $148,097 and "Cost Savings" adds 10.3 percent. What DSPworkplace and LMDmax charge is unknown, and it determines whether this is a pricing problem or a value-communication problem.

**6. Associate decline versus route cuts.** Is Amazon cutting routes (viability, unfixable) or is the customer failing to retain drivers (operational, and something Hera's coaching tools address)? `Route` has `byGroupAndTime`. This separates "forecast the loss" from "sell them the fix."

**7. The 68 trials, entirely unexamined.** 54 have already lapsed. At $9 against a median 89 associates, one converted trial is worth about $9,600 a year. Probably a bigger lever than the 15 real-attrition accounts, which hold $113,844 total.

**8. Onboarding, given 29 percent of churn is in year one.** The onboarding plugin is installed but unconfigured.

**9. Support signal.** Intercom holds conversations and sentiment per company. Not pulled.

**10. Nobody records what worked.** No intervention-and-outcome log, so it is not knowable whether calling a shrinking account helps.

**11. Are the 8 comped accounts intentional?** $109,498 a year, including your second-largest account by associate count.

**Strategic observation.** Revenue equals associates times a fixed rate, so Hera grows when customers hire. That is working: survivors expanded 13.9 percent with no sales motion. The flip side is that you have no pricing lever inside an account except modules, and HeraAi is at 13 percent. Expansion here means selling things not priced per associate.

---

## 13. Decided, and open **[REVISED]**

### Decided and in the plugin config

- Motion is hybrid and segmented, on **engagement state, not revenue**
- Roughly 1.5 effective account owners, not 3. John covers the book, CSS 1 is building toward an owned book with a retention bonus, CSS 2 is a detection layer with no book
- CSS 1's retention bonus must exclude Amazon DSP program closures
- Escalation goes to John as a Zoho task, second tier is the weekly CEO meeting
- Primary value metric is operational time saved, **not instrumented**, so no skill may state a time-saved figure as fact

### Needs changing because of revision 3

- **The 90% addressable GRR target is already met** at 95.0%. Replace it
- **Primary health signal** should be associate-count trend with a mandatory cleanup check, not roster horizon
- **Escalation response times**, still unset, now depend on the associate-trend bands

### Open

1. Phantom billing exposure (section 12, item 1)
2. Seasonality
3. Escalation response times
4. QBR format. Month-to-month with no renewal event, at 107 accounts per person, may not support standing per-account QBRs
5. The unnamed competitor, $82,472 this year
6. Whether the 8 comped accounts are intentional
7. Outcome catalog, pending

### Config locations

- `~/.claude/plugins/config/claude-for-customer-success/company-profile.md`
- `~/.claude/plugins/config/claude-for-customer-success/csm/CLAUDE.md`
