# Customer Success Health Baseline

**Revision 2, 2026-07-28.** Revision 1 published earlier the same day.
**Source:** live queries against production DynamoDB (AWS `530079012632`, `us-east-2`, profile `hera-readonly`)
**Cached query output:** `data/` in this folder

Every number here came from a live query. Where a figure is derived or carries a caveat, it says so.

---

## 0. What changed in revision 2

John pointed out that **only ACTIVE associates count for billing**, and that associate figures should only ever be read that way. Chasing that down turned out to be the most consequential correction of the whole analysis, because it led to the `Invoice` table, which I had not opened in revision 1.

### The discovery

`Invoice` carries a field called **`averageActiveDriverCount`**, alongside `variableTotal` and `flatMonthlyBillingAmount`. Billing is a per-active-driver charge. That means the field I used for every revenue figure in revision 1, `Tenant.averageMonthlyInvoiceTotal`, is a **lifetime average**, and for any account that has grown or shrunk it reports what they used to pay rather than what they pay now.

### Numbers that changed

| Figure | Revision 1 | Revision 2 | Why |
|---|---|---|---|
| Total ARR | $2,097,712 | **$1,987,326** | Latest actual invoice, not lifetime average. 5.3% overstated |
| ARR at stake, at-risk accounts | $249,584 | **$141,271** | **43% overstated** |
| Accounts at genuine churn risk | 31 | **12** | 7 of the 31 are growing, 10 are flat |
| GRR, all causes | 77.1% | **70.3%** | Real invoices, and survivor shrinkage is now visible |
| GRR, addressable | 85.7% | **77.2%** | My earlier formula was wrong, see section 6 |
| Cost of reaching 90% addressable GRR | ~$105,000/yr | **$295,734/yr** | Follows from the corrected baseline |
| Rate per active driver | not known | **$7.83/month** | New |
| Survivor shrinkage | "invisible to this calculation" | **-$134,889 (-7.0%)** | Now measured |

### Conclusions that changed

1. **Driver-count trend replaces roster horizon as the primary health signal.** Driver count *is* the revenue. It comes from `Invoice`, updates monthly, and is available for 251 of 253 accounts.
2. **Roster lapse does not mean churn risk.** Seven accounts flagged in revision 1 are growing their driver count and their bill while ignoring the roster feature. One has not rostered in 445 days and is still growing. Those are feature-adoption gaps, and treating them as churn risk would waste effort.
3. **Shrinkage inside surviving accounts is a separate problem from churn**, worth $134,889 a year, and revision 1 could not see it at all.
4. **The 90% retention target is far more aggressive than it looked** when set against a 77.2% baseline instead of 85.7%.

### What did not change

Book composition (253 active accounts), the homogeneity finding, the churn-reason analysis, the roster-versus-login divergence as a real phenomenon, and the data quality register. Sections carrying material changes are marked **[REVISED]**.

---

## 1. Glossary

### Money

| Term | What it means | Your number |
|---|---|---|
| **ARR** | Annual Recurring Revenue. What one customer pays across a year | Median customer: $649/mo, so about $7,800 ARR. Whole book: $1.99M |
| **GRR** | Gross Revenue Retention. Of the money you had at the start of the year from customers you already had, how much you still have. Ignores new customers and upsells. Never above 100% | 70.3% |
| **NRR** | Net Revenue Retention. Same but it counts upgrades, so it can exceed 100% | Not set as a target, see section 14 |
| **Run rate** | What you are billing right now, projected forward a year. Different from what you billed on average historically | |
| **Contraction / shrinkage** | An existing customer paying you less than before, without leaving | -$134,889 this year |
| **AR** | Accounts Receivable. Money billed but not collected | 3 accounts, $3,053 |

### Roles

| Term | What it means |
|---|---|
| **CS** | Customer Success. The function that keeps customers using the product and paying |
| **CSM** | Customer Success Manager. Owns the relationship for a set of customers |
| **CSS** | Customer Success Specialist. Your two team members |
| **AE** | Account Executive. A salesperson. Hera does not have one, which is why expansion signals have nowhere to route |

### Process

| Term | What it means |
|---|---|
| **QBR** | Quarterly Business Review. A scheduled meeting where you show a customer the value they received and plan the next quarter |
| **SLA** | Service Level Agreement. A promised response time |
| **Health score** | A rating (Healthy, Developing, At Risk, Critical) computed from signals, to decide who needs attention |
| **Churn** | A customer leaving |
| **Whitespace** | Something a customer could buy but has not. Your 221 accounts without HeraAi |
| **Expansion** | Selling more to a customer you already have |

### Statistics

| Term | What it means |
|---|---|
| **p50, p75, p90** | Percentiles. p50 is the middle value, the median. p90 means 90 percent of accounts fall below it |
| **r = 0.963** | Correlation, from -1 to 1. How strongly two things move together. 0.963 is near-lockstep |
| **Cohort** | A fixed group of accounts followed over time, so new customers do not mask churn |

### Hera domain terms

**DSP** is Delivery Service Partner, your customer. **DA** is Delivery Associate, a driver. Amazon scorecard metrics in the product: FICO, DCR, DC DPMO, DAR, DNR.

---

## 2. How billing actually works (new in revision 2)

This section did not exist in revision 1 and it reframes everything after it.

| | |
|---|---|
| Correlation, `averageActiveDriverCount` to `invoiceTotal` | **r = 0.963** |
| Accounts with a variable, per-driver component | 242 of 243 |
| Accounts with any flat monthly fee | **4** of 243 |
| Rate per active driver per month | p25 $7.56, **median $7.83**, p75 $7.84 |
| Invoice records available | 25,773, going back years |
| Age of the most recent invoice | median 26 days, maximum 26 days for every account |

**Your revenue is active drivers times about $7.83 a month.** Only active drivers count, which is what John flagged, and the billing system already works that way: the four accounts with zero active drivers are billing $0.

### Three things follow from this

**Driver count is not a usage metric, it is the invoice.** A customer losing 20 drivers has already reduced your revenue by about $156 a month. There is no lag and no renewal event where you could intervene, because Hera is month-to-month (see section 12).

**`Invoice` is a monthly time series of driver count per account.** This is the single most useful dataset for health scoring and I missed it in revision 1.

**You have almost no pricing lever inside an account.** Revenue per driver is fixed at about $7.83 and only 4 accounts have a flat fee. So Hera grows when your customers hire drivers, and shrinks when they do not. The only way to increase revenue per driver is to sell something that is not priced per driver, and HeraAi sits at 13 percent adoption.

### Reconciliation note

Point-in-time `Staff` count gives 22,888 active drivers. Summing `averageActiveDriverCount` across the latest invoices gives about 21,150. The difference is expected: the invoice figure is a monthly average and the Staff count is a snapshot on 2026-07-28. Use the invoice figure for revenue and the Staff figure for operational size.

---

## 3. What the book looks like **[REVISED]**

| | |
|---|---|
| Total tenant records | 953 |
| Test and temporary (excluded throughout) | 81 |
| **Active paying accounts** | **253** (243 Bundle, 10 Premium) |
| Trials in flight | 68 |
| Lapsed trials | 54 |
| Churned | 497 |
| **Total ARR, from latest actual invoices** | **$1,987,326** |
| (Revision 1 figure, lifetime averages) | ($2,097,712, 5.3% high) |
| Median tenure | 40 months paid (p25 26, p75 56, longest 64) |
| Customer type | 100 percent Amazon DSP |
| Sub-type | 802 ZL, 68 XL, 2 Lite |

Coverage book is **321 accounts**: 253 paying plus 68 trials.

---

## 4. Why revenue-based tiering does not work for you

Most customer success advice assumes a few large customers worth protecting and a long tail worth automating. You do not have that shape.

| Percentile | Monthly invoice | ARR |
|---|---|---|
| p10 | $448 | $5,380 |
| p25 | $543 | $6,510 |
| **p50 (median)** | **$668** | **$8,014** |
| p75 | $831 | $9,973 |
| p90 | $990 | $11,874 |
| Largest | $1,348 | $16,179 |

*(Percentiles above are from the lifetime-average field. Directionally correct; the shape is what matters here, not the exact cents.)*

**Your largest account is 2.0 times your median.**

| | Share of total ARR |
|---|---|
| Top 10 accounts | 7.1% |
| Top 20 accounts | 13.1% |
| Top 50 accounts | 29.3% |

In a typical business-to-business software company the top 10 percent of accounts carry 40 to 60 percent of revenue. Yours carry about 13 percent. Any tier built on revenue would contain accounts that behave identically. That is why health is built on engagement and revenue direction instead.

---

## 5. Associates, counting only ACTIVE status **[REVISED]**

Only `status = 'Active'` associates are counted anywhere in this document, because that is the billing basis.

| | |
|---|---|
| **Total active drivers** | **22,888** |
| Median per account | 89 |
| p25 / p75 | 69 / 112 |
| p90 / p95 | 138 / 158 |
| Largest | 338 (JDW Logistics) |
| Smallest | 0 (see section 9) |

Driver count varies more than revenue (3.8 times median versus 2.0), but **86 percent of accounts run between 50 and 199 active drivers**, so this is not a tiering variable either.

| Size band | Accounts | Share | Drivers |
|---|---|---|---|
| Under 20 | 22 | 8.7% | 59 |
| 20 to 49 | 9 | 3.6% | 377 |
| 50 to 99 | 125 | 49.4% | 9,664 |
| 100 to 199 | 93 | 36.8% | 11,710 |
| 200 or more | 4 | 1.6% | 1,078 |

**Status vocabulary, for reference.** `Active`, `Onboarding`, `Inactive - Terminated`, `Inactive - Misc`, `Inactive - Medical Leave`, `Inactive - Personal Time/Vacation`, `Inactive - Failed Onboarding`. Only `Active` bills. `Onboarding` is worth watching separately as a leading indicator of driver growth.

---

## 6. Retention, recomputed from real invoices **[HEAVILY REVISED]**

Measured as a cohort: the 302 accounts already paying on 2025-07-28, followed forward. New customers acquired during the year are excluded. Revision 1 used lifetime-average ARR for this, which hid one entire loss category.

### Full decomposition

| | Amount | Accounts |
|---|---|---|
| Cohort ARR at 2025-07-28 | **$2,530,140** | 302 |
| Lost, Amazon DSP program closure | -$225,236 | 30 |
| Lost, addressable churn | -$391,335 | 46 |
| **Shrinkage inside surviving accounts** | **-$134,889** | 226 |
| **ARR today from that cohort** | **$1,778,680** | 226 |

Surviving accounts shrank **7.0 percent** in revenue. Revision 1 stated this was "invisible to this calculation." It is now measured, and it is the third-largest loss category.

### Retention, and a correction to my formula

| Measure | Result |
|---|---|
| **GRR, all causes** | **70.3%** |
| **GRR, addressable (correct)** | **77.2%** |
| GRR, addressable (revision 1 method) | 84.5%, **wrong** |
| Program-closure drag | 8.9% |

**Why revision 1 was wrong.** I computed addressable GRR as (start minus addressable churn) divided by start. That subtracts churn but silently treats survivor shrinkage as if it never happened, and it leaves program-closed accounts in the denominator. The correct calculation removes program closures from **both** sides, then measures what remains:

```
addressable base = $2,530,140 - $225,236 = $2,304,904
addressable GRR  = $1,778,680 / $2,304,904 = 77.2%
```

### Loss as a share of what your team could influence

| | Share of addressable base | Amount |
|---|---|---|
| Addressable churn | 17.0% | $391,335 |
| Survivor shrinkage | 5.9% | $134,889 |
| **Total** | **22.8%** | **$526,224** |

### What the target actually costs

| Target | Annual recovery required |
|---|---|
| 80% addressable GRR | $65,243 |
| 85% | $180,488 |
| **90% (currently set)** | **$295,734** |

Revision 1 described the 90% target as worth about $105,000 against an 85.7% baseline. Against the corrected 77.2% baseline it requires recovering **$295,734 a year**, which is a 12.8 point improvement. **That target should probably be revisited.** 85% is already a substantial ask.

---

## 7. Why customers leave

Unchanged from revision 1. `accountCanceledReason` is populated on 430 of 497 churned accounts and `accountCanceledNotes` on 312.

### All 469 paid churns, lifetime

| Reason | Accounts | Share | Preventable by CS? |
|---|---|---|---|
| **DSP Closed** | 181 | 38.7% | **No.** Went out of business |
| **Didn't Fully Utilize or Find Value** | 92 | 19.7% | **Yes** |
| (blank) | 60 | 12.8% | Unknown |
| Cost Savings | 48 | 10.3% | Partly |
| Switched to Competitor (all) | 56 | 12.0% | Yes |
| Internal processes, built their own | 9 | 1.9% | Partly |
| Reduced routes, dropped drivers to zero, site closure | 12 | 2.6% | No |
| Stopped Using, No Explanation | 6 | 1.3% | Yes |

About 41 percent of churn is the Amazon DSP program churning rather than Hera. About 45 percent is addressable.

### Trailing 12 months tells a different story

| Reason | Accounts | ARR lost |
|---|---|---|
| **Switched to competitor (all)** | **20** | **$148,097** |
| Didn't Fully Utilize or Find Value | 10 | $84,226 |
| Cost Savings | 7 | $54,988 |
| Internal processes | 5 | $37,201 |
| Stopped Using, No Explanation | 3 | $19,218 |
| Pause Subscription | 1 | $8,994 |

**Competitive loss is now your largest addressable bucket.**

### Named competitors, from your own records

| Competitor | Lifetime | Last 12 months |
|---|---|---|
| DSPworkplace | 23 | 5 |
| LMDmax | 17 | 6 |
| **"Other", unnamed** | **13** | **11 ($82,472)** |
| Manage my DSP | 1 | 2 |
| Lokiteck | 2 | 1 |

**Your largest single competitive loss this year is to a competitor nobody recorded the name of.** 11 accounts, $82,472.

### When customers leave

Median tenure at churn is 18 months (p10 5, p25 10). **29 percent churned inside 12 months.** Survivors have a 40-month median. You lose accounts early or keep them for years, so intervention is worth most in year one.

---

## 8. How to tell a healthy account from a dying one **[HEAVILY REVISED]**

### Primary signal: driver-count trend

This replaces roster horizon as the primary signal. It comes from consecutive `Invoice` records and it is the revenue itself.

Across all 251 accounts with a computable trend, comparing the earliest and latest of the last four invoices:

| Direction | Accounts | Run-rate change, annualized |
|---|---|---|
| Growing more than 10% | 90 | +$78,428 |
| Stable, within 10% | 122 | -$156,134 |
| Shrinking 10 to 25% | 26 | -$51,682 |
| Shrinking 25 to 50% | 4 | -$11,760 |
| Collapsing more than 50% | 8 | -$59,310 |
| **Net** | **251** | **-$193,298** |

**Do not act on that net figure yet.** It comes from only 2 to 4 invoice months in mid-summer. Amazon delivery volume is seasonal, so this could be a normal summer trough or a real contraction. Separating the two requires a year-over-year comparison, which `Invoice` can support with 25,773 records. See section 13, item 1.

Note also that "stable" accounts still moved $156,134 in run rate. On a base of 22,888 drivers, a 5 percent wobble is real money.

### Secondary signal: roster horizon

`DailyRoster.notesDate` is the date a roster is built *for*, and customers schedule ahead, so a healthy account's most recent roster date is in the **future**. Roster horizon is that date minus today.

| Band | Rule | Accounts |
|---|---|---|
| Scheduling today or ahead | horizon >= 0 | 173 |
| Stopped 1 to 30 days ago | -1 to -30 | 35 |
| Stopped 31 to 90 days ago | -31 to -90 | 17 |
| Stopped over 90 days ago | < -90 | 8 |
| No roster record or corrupt date | | 29 |

**What roster horizon actually measures is feature adoption, not churn risk.** That is the significant reinterpretation in revision 2, and section 9 shows why.

### Login recency: still the weakest signal

Of the 25 accounts lapsed 30 or more days on rostering, **10 logged in within the last 7 days** and 4 logged in the same day. A login-based or seat-based health score would rate all 10 healthy.

| Account | Roster stopped | Last login | Drivers |
|---|---|---|---|
| Clark Courier Service LLC | 86 days ago | **today** | 153 |
| Last Mile Logistics LLC | 83 days ago | **today** | 135 |
| Express Package System Inc | 82 days ago | **today** | 198 |
| Motaur Express | 94 days ago | yesterday | 1 |
| Active Transportation Services LLC | 41 days ago | **today** | 68 |

The reverse case is rare: only 5 accounts roster normally but have not logged in for over 14 days.

---

## 9. Accounts needing attention **[HEAVILY REVISED]**

Revision 1 listed 31 accounts and $249,584 in ARR. Splitting those same 31 by whether their driver count, and therefore their revenue, is actually moving changes the picture completely.

| Group | Accounts | Current ARR |
|---|---|---|
| **Shrinking drivers, real churn risk** | **12** | **$34,516** |
| Flat | 10 | $54,894 |
| **Growing drivers, adoption gap only** | **7** | **$51,861** |
| No trend available, already at $0 | 2 | $0 |
| Total | 31 | $141,271 |

### The real churn list: 12 accounts, $34,516 ARR

| Account | Roster stopped | Drivers now | Change | % | Monthly |
|---|---|---|---|---|---|
| Infinite Delivery OPS LLC | 45d | 0 | -18 | -100% | $0 |
| DnA Logistics Inc. | none | 0 | -59 | -100% | $0 |
| Supreme Delivery | 58d | 1 | -83 | -99% | $8 |
| Ursa Logistics LLC | 56d | 2 | -151 | -99% | $8 |
| SkyHook 2 LLC | 11d | 21 | -104 | -83% | $172 |
| Focus Logistics | 7d | 31 | -29 | -49% | $249 |
| Globalteq Logisitcs LLC | 10d | 47 | -28 | -38% | $381 |
| Deliver2U LLC | 6d | 81 | -27 | -25% | $439 |
| Sarkat Logistics, LLC | 7d | 48 | -9 | -16% | $352 |
| Active Transportation Services LLC | 41d | 68 | -12 | -15% | $531 |
| EZ Logistix LLC | 54d | 91 | -8 | -8% | $396 |
| MTSL | 55d | 44 | -4 | -8% | $341 |

Four of these are effectively gone already, billing $0 or $8. Ursa Logistics lost **151 drivers**, from 153 down to 2. SkyHook 2 lost 104. Those are business events, not engagement problems, and worth understanding before they repeat.

Note that six of these accounts rostered within the last 11 days. **They are engaged and shrinking at the same time**, which is exactly why roster horizon alone would have missed them.

### Growing, not at risk: 7 accounts, $51,861 ARR

These were flagged in revision 1. They should not have been.

| Account | Roster stopped | Drivers now | Change | % | Monthly |
|---|---|---|---|---|---|
| **Express Package System Inc** | 82d | 198 | **+35** | **+21%** | **$1,556** |
| Bison Peak LLC | 41d | 123 | +22 | +21% | $929 |
| Probyn Inc | 55d | 40 | +14 | +55% | $309 |
| Pure Logistics USA LLC | 58d | 95 | +12 | +14% | $735 |
| On-demand Logistics Service Llc | 52d | 69 | +11 | +19% | $361 |
| **DBE Logistics, Inc.** | **445d** | 93 | +5 | +5% | $406 |
| Double Iron Car Care LLC | 292d | 17 | +3 | +24% | $25 |

Express Package System has grown 21 percent and now bills $1,556 a month, against an $877 lifetime average, while not touching the roster in 82 days. DBE Logistics has not rostered in **445 days** and is still growing. These accounts use Hera for staff records and billing but not for rostering. **The correct play is a feature-adoption conversation, not a save.**

### Flat: 10 accounts, $54,894 ARR

| Account | Roster stopped | Drivers now | Change | Monthly |
|---|---|---|---|---|
| Clark Courier Service LLC | 86d | 153 | -6 (-4%) | $1,176 |
| Last Mile Logistics LLC | 83d | 135 | -4 (-3%) | $1,057 |
| Spears Enterprises LLC | 31d | 112 | +0 | $874 |
| PacTrack, Inc | 36d | 79 | -2 (-2%) | $619 |
| Black Nile Logistics | 216d | 77 | +1 (+1%) | $604 |
| Divine Package LLC | 183d | 43 | +0 | $193 |
| New Deal Logistics | 207d | 3 | +0 | $24 |
| Shandy Holdings | 173d | 2 | +0 | $16 |
| Motaur Express | 94d | 1 | +0 | $8 |
| Prolific Logistics | 376d | 1 | +0 | $4 |

The bottom four have already collapsed to 1 to 3 drivers and are billing under $25 a month. They are dormant shells, not accounts to save. The top three are large, stable, and simply not using the roster.

### Zero active drivers: 9 accounts

Verified, not assumed. Every associate at these accounts sits in an `Inactive` status. Control check: JDW Logistics shows 338 in `Active` against the same status set, so the field is used consistently.

Of these, **4 already bill $0**: K&K Solomon Logistics, Your Express Solutions, Infinite Delivery OPS, and DnA Logistics. Billing has already caught up. They are revenue-churned while still marked `Active` in `customerStatus`.

**Two are rebuilding, not dying.** DnA Logistics has 69 associates in `Onboarding` status and Globalteq has 2. They are restaffing.

---

## 10. Every factor that could feed a health score **[REVISED]**

For each factor: what it tells you, where it comes from, and whether it is measured, measurable, or ruled out. "Measurable" means the database has the right index to compute it cheaply per account, roughly 253 fast queries, but it has not been run.

### Group A: Revenue and operational scale (new priority in revision 2)

| Factor | What it tells you | Source | Status |
|---|---|---|---|
| **Active driver count** | The billing basis. This is the revenue | `Invoice.averageActiveDriverCount` | **Measured** |
| **Driver-count trend** | **Primary health signal.** Revenue direction | Consecutive `Invoice` records, `byGroup` = group + createdAt | **Measured**, 251 of 253 |
| **Onboarding pipeline** | Associates in `Onboarding` status, a leading indicator of driver growth | `Staff`, index `byGroupStatus` | Partly measured |
| Year-over-year driver change | Separates seasonal dips from real decline | `Invoice`, 25,773 records | **Not yet measured. Highest priority** |

### Group B: Are they doing the daily work?

| Factor | What it tells you | Source | Status |
|---|---|---|---|
| **Roster horizon** | Whether they use the rostering feature. **Adoption, not churn risk** | `DailyRoster`, index `byGroupAndNotesDate` | **Measured** |
| Messaging volume | Are they messaging drivers through Hera or back on personal phones | `Message`, index `byGroup` = group + createdAt | Measurable |
| Daily log volume | Are they recording what happened each day | `DailyLog`, index `byDate` = group + date | Measurable |

### Group C: Are they using what they pay for?

| Factor | What it tells you | Source | Status |
|---|---|---|---|
| Scorecard upload freshness | Still uploading the weekly Amazon scorecard. A weekly ritual, so a gap is loud | `CompanyScoreCard`, index `byGroup` = group + yearWeek | Measurable |
| Coaching activity | Logging counselings, infractions, kudos | `Counseling`, `Infraction`, `Kudo`, all `byGroupAndDate` | Measurable |
| Feature adoption | Which optional modules are on | `Tenant` flags | **Measured** |

Feature adoption across 253 active accounts:

| Feature | Using it | Share |
|---|---|---|
| `featureEnabledCounselings` | 233 | 92% |
| `featureEnabledAssociateApp` | 146 | 58% |
| `permissionHeraAi` | **32** | **13%** |
| InventoryManagement, RosterChecklist | ~253 | ~100%, no signal |

**HeraAi at 13 percent is your clearest expansion opportunity**, and per section 2 it is one of the only ways to raise revenue per driver.

### Group D: Is their business shrinking? (viability, not fixable by CS)

| Factor | What it tells you | Source | Status |
|---|---|---|---|
| **Route volume trend** | Whether Amazon is cutting their routes | `Route`, index `byGroupAndTime` | Measurable. **See section 13, item 5** |
| Driver turnover | How fast drivers churn inside their operation | `StaffStatus`, index `byGroup` = group + date | Measurable |
| Amazon scorecard tier and trend | Whether Amazon may terminate them | `CompanyScoreCard`, 88,580 records | Measurable |

### Group E: Are the right people showing up?

| Factor | What it tells you | Source | Status |
|---|---|---|---|
| Login recency | When anyone last logged in. **Weak on its own** | `User`, index `gsi-TenantUsers` | **Measured** |
| Active user count | How many of their people actually use it | `User` | Partly measured |
| Never-logged-in seats | An onboarding gap | `User` | **Measured.** 622 of 3,672 records, 17% |

### Group F: Commercial

| Factor | What it tells you | Status |
|---|---|---|
| Discount depth | Predicts the "Cost Savings" churn reason, 10.3% of losses | Measurable |
| Unpaid balance | Money owed | **Measured.** 3 accounts, $3,053. Not a meaningful signal for you |
| Tenure | Under 12 months is the danger zone, 29% of losses | **Measured** |
| Support volume and sentiment | Standard health input | **Not pulled.** Intercom connector works. See section 13, item 8 |

### Ruled out

**Overall app activity from the audit log.** `AuditLog` is indexed on group plus `email#createdAt`, so there is no date range query across all users of an account. Counting it per account means reading roughly 27,000 rows per customer. Too expensive to schedule. Recorded here so nobody assumes it was overlooked.

---

## 11. Proposed band definitions **[REVISED]**

### Count red flags, do not weight percentages

Weighted scoring is standard advice but hard to explain, hard to tune, and produces a number nobody can reason about. Counting red flags is closer to how you would actually think about an account.

### Two separate scores, and the split moved

**Health** answers "is there something we can do here."
**Viability** answers "is this customer's business going to survive."

Revision 2 moves driver-count trend to the top of Health, because it is the revenue, and demotes roster horizon to an adoption signal.

| Band | Proposed rule |
|---|---|
| **Critical** | Drivers down more than 50%, OR zero active drivers, OR 3+ red factors |
| **At Risk** | Drivers down 10 to 50%, OR 2 red factors |
| **Developing** | Drivers down 5 to 10%, OR 1 red factor |
| **Healthy** | Drivers flat or growing, no red factors |
| **Adoption gap** (new) | Drivers flat or growing, but a core feature unused. **Not a risk band.** Route to an adoption conversation, not a save |

That last band is new and it exists because of the 7 growing accounts in section 9.

**The driver-trend thresholds above are placeholders.** They cannot be finalized until the seasonality question in section 13 is answered, because a 10 percent summer decline may be normal. Do not treat them as set.

**Do not blend Health and Viability.** 38.7 percent of your churn is customers losing their Amazon contract or closing. Folding that into a health score makes it unactionable and sends a small team after accounts nobody can save.

---

## 12. Data quality register **[REVISED]**

Traps that produce confidently wrong answers. Three of them caught me during this analysis.

| Field | Problem | What to do |
|---|---|---|
| **`Tenant.averageMonthlyInvoiceTotal`** | A **lifetime average**, not current billing. Overstated total ARR by 5.3% and at-risk ARR by 43% | Use the latest `Invoice.invoiceTotal`. **This produced every wrong number in revision 1** |
| `DailyRoster.notesDate` | The date a roster is built **for**, scheduled ahead, not a creation timestamp. Healthy accounts have a future date | Never compute "days since last roster." Use horizon: latest date minus today. **Caught me first time through** |
| `User.lastLogin` | Can hold the literal string `NOT_YET_LOGGED`, which sorts above real ISO timestamps because "N" > "2" | Filter before any `max()`. **Silently dropped 118 of 253 accounts** |
| Associate status | Only `status = 'Active'` bills. Total staff records include years of terminations, up to 2,102 on one account | Always filter to `Active` for anything billing or size related |
| `firstChurnedDateTime` | Missing on 267 of 497 churned accounts | Use `customerStatus` |
| `firstConvertedToPaidDateTime` | Sparse. Using it I calculated 78 paid churns. The real figure is 468 | Use `totalNumberOfMonthsPaidByTenant > 0` |
| `numberOfSeats` | Absent on 198 of 253 active accounts | Seat-based math is not possible. Irrelevant anyway, since billing is per driver |
| `accountType` | Null on 502 of 872. `PARENT` and `CHILD` never populated | Multi-entity rollup does not work despite schema support |
| `featureAccessX` vs `featureEnabledX` | Access is not a superset of enabled. `featureAccessAssociateApp` is 0 on all 253 while `featureEnabledAssociateApp` is 146 | Do not compute "access minus enabled" as an adoption gap. **I asserted this early and it was wrong** |
| `cost*` fields | Nonzero on all 253 accounts. `costMessaging` is 0 on all | Price-list fields, not entitlement markers |
| `DailyRoster.notesDate` range | 8 accounts have values far outside any plausible range | Clamp to roughly -2000 to +400 days |
| No roster record | 21 active accounts have no `DailyRoster` row | Unclassified, not healthy |
| Contract and renewal dates | **No contract, term, renewal, or expiration field exists on `Tenant`** | Hera is month-to-month. No renewal event, no 90/60/30 runway. Retention is continuous, and a driver loss hits revenue immediately |
| `Invoice.year#month` | Documented in repo `CLAUDE.md`: December stored as `<next-year>#0` | Filter on `createdAt`, not `year#month` |

---

## 13. What we have not uncovered (new in revision 2)

Ordered by how much each would change the plan.

**1. Seasonality, and it undermines every threshold here.** Everything was measured on a single snapshot on 2026-07-28, and the driver trends span only 2 to 4 months of mid-summer. If Amazon volume dips in summer and peaks in Q4, a July driver decline is normal and the "shrinking" bucket is partly noise. `Invoice` holds 25,773 records going back years, so year-over-year is computable. **Do this before finalizing any threshold.**

**2. How "DSP Closed" actually gets recorded.** The entire target structure, the addressable/program split, and CSS 1's retention bonus all rest on that one field. Who fills it in, and how do they know the DSP closed rather than just left? If it is an assumption made at cancellation, 38.7 percent is softer than it has been treated.

**3. Is Amazon growing or culling the DSP program?** That external fact drives 38.7 percent of churn and appears nowhere in the database. Regional consolidation would produce churn nobody can prevent, which should be forecast rather than staffed against.

**4. Is $7.83 per driver above or below market?** Competitive switching is the largest addressable loss at $148,097 and "Cost Savings" adds 10.3 percent. What DSPworkplace and LMDmax charge is unknown. That single fact determines whether this is a pricing problem or a value-communication problem.

**5. Driver decline versus route cuts.** When an account loses drivers, is Amazon cutting their routes (viability, unfixable) or is the customer failing to retain drivers (operational, and something Hera's coaching tools directly address)? `Route` has `byGroupAndTime`, so this is measurable, and it separates "forecast the loss" from "sell them the fix." Ursa Logistics losing 151 drivers is the case to test it on.

**6. The 68 trials, entirely unexamined.** Nothing has been measured about trial-to-paid conversion, and 54 have already lapsed. At $7.83 per driver against a median 89 drivers, one converted trial is worth roughly $8,400 a year. This may be a larger lever than saving the 12 shrinking accounts, which together hold $34,516.

**7. Onboarding, given 29 percent of churn happens in year one.** The onboarding plugin is installed but never configured. Early churn is the biggest addressable pattern and onboarding quality drives it, and none of that process is in the data.

**8. Support signal.** Intercom holds conversation history and sentiment per company and none of it was pulled. The connector is verified working.

**9. Nobody records what worked.** There is no log of interventions and outcomes, so it is not yet knowable whether calling a lapsed account saves it. Worth starting now, because in six months it turns this model from a guess into something calibrated.

**One strategic observation.** Because revenue equals drivers times a fixed rate, Hera grows only when customers hire drivers. There is no pricing lever inside an account except modules, and HeraAi is at 13 percent. So the NRR problem is not a missing sales process, it is that revenue is a pass-through on a headcount base Hera does not control. That reframes expansion from "sell more seats" to "sell things that are not priced per driver."

---

## 14. What is decided and what is open **[REVISED]**

### Decided and written into the plugin config

- Motion is hybrid and segmented, with the axis being **engagement state, not revenue**
- Team is roughly 1.5 effective account owners, not 3. John covers the full book, CSS 1 is building toward an owned book with a retention bonus, CSS 2 is a detection layer with no book
- CSS 1's retention bonus must exclude Amazon DSP program closures
- Escalation goes to John as a Zoho task, with the weekly CEO management meeting as second tier
- Primary value metric is operational time saved, with the explicit caveat that it is **not instrumented**, so no skill may state a time-saved figure as fact

### Needs revisiting because of revision 2

- **The 90% addressable GRR target.** Set against a baseline I reported as 85.7%. The real baseline is 77.2%, so 90% now requires recovering $295,734 a year. 85% requires $180,488. Recommend revisiting.
- **The health model's primary signal.** Config records roster horizon as primary. It should be driver-count trend, with roster horizon demoted to an adoption signal.
- **Escalation response times**, still unset, and now they depend on the driver-trend bands rather than the roster bands.

### Still open

1. Seasonality (section 13, item 1). Blocks every threshold
2. Escalation response times
3. QBR format. At 107 accounts per person, month-to-month, with no renewal event, standing per-account QBRs may not be viable
4. The unnamed competitor: $82,472 lost this year to "Switched to Competitor - Other"
5. Outcome catalog, marked pending. Probably wait until the time-saved metric has a real proxy

### Config file locations

- `~/.claude/plugins/config/claude-for-customer-success/company-profile.md`
- `~/.claude/plugins/config/claude-for-customer-success/csm/CLAUDE.md`
