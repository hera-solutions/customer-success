# Customer Success Health Baseline

**Revision 4, 2026-07-29.** Revisions 1 to 3 published 2026-07-28.
**Source:** live queries against production DynamoDB (AWS `530079012632`, `us-east-2`, profile `hera-readonly`)
**Cached query output:** `data/`

---

## 0. Revision history

| Measure | Rev 1 | Rev 2 | Rev 3 | **Rev 4** |
|---|---|---|---|---|
| Price per associate | unknown | $7.83 | $9.00 | **$9.00, verified** |
| Total ARR | $2,097,712 | $1,987,326 | $2,341,619 | **$2,341,619** |
| GRR addressable | 85.7% | 77.2% | **95.0%** | 95.0% |
| Customers | 253 | 253 | 253 | **246** (253 tenants) |
| Primary health signal | roster horizon | associate trend | associate trend | **two axes, see section 2** |

**What each revision got wrong.** Rev 1 used `Tenant.averageMonthlyInvoiceTotal`, a lifetime average. Rev 2 used `Invoice.invoiceTotal` from invoices that were all status `Pending`, meaning partial months still accruing, which manufactured a fake book-wide decline. Rev 3 fixed the money by using closed invoices and verifying against line items.

**What revision 4 adds.** John supplied the $9 price, the arrears billing cycle, the fact that customers control Inactive status and lag on it, and the specific health factors he cares about. That produced: a two-axis model replacing the single band, the discovery that rostering depth does **not** predict revenue decline, a customer-level rollup of multi-site tenants, the under-10 associate rule, an audit of every account against the $9 list price, and the 67 trials scored for the first time.

---

## 1. Glossary

| Term | Meaning |
|---|---|
| **ARR** | Annual Recurring Revenue. What a customer pays across a year |
| **GRR** | Gross Revenue Retention. Of the revenue you had a year ago from existing customers, how much remains. Never above 100% |
| **NRR** | Net Revenue Retention. Same, but counts upgrades, so it can exceed 100% |
| **CSM / CSS** | Customer Success Manager / Specialist |
| **AE** | Account Executive, a salesperson. Hera has none |
| **SLA** | Service Level Agreement, a promised response time |
| **Whitespace** | Something a customer could buy but has not |
| **p50, p90** | Percentiles. p50 is the median. p90 means 90% of accounts fall below it |
| **Cohort** | A fixed group of accounts followed over time, so new customers do not mask churn |
| **DSP / DA** | Delivery Service Partner (your customer) / Delivery Associate (a driver) |

---

## 2. The model: two axes, not one band

Revisions 1 to 3 tried to produce a single health band. That was wrong, and the pilot in section 7 proves it: **product engagement does not predict revenue decline.** The most deeply engaged account in the pilot was losing 15% of its associates, and the lowest-scoring account was growing 20%.

So two independent axes:

**Revenue direction** answers "how much will they pay." Measured from associate count across the last four closed invoices, because billing is $9 per active associate.

**Engagement** answers "will they stay at all." A binary abandonment test: no roster containing a staffed route in 30 days **and** fewer than 5 messages per associate.

|  | Engaged | Abandoned |
|---|---|---|
| **Associates growing** | Healthy | **Adoption risk** |
| **Associates flat** | Stable | **Adoption risk** |
| **Associates declining** | Business contraction | **Critical** |

### Where your book sits, at customer level

253 tenants roll up to **246 customers**, because 7 customers run secondary sites (permanent and temporary) that appear as separate tenants.

| Quadrant | Customers | ARR | Share |
|---|---|---|---|
| Healthy: growing, engaged | 123 | $1,322,684 | 56.5% |
| Stable, engaged | 51 | $467,538 | 20.0% |
| Business contraction: declining, engaged | 31 | $266,224 | 11.4% |
| **Adoption risk** | **18** | **$169,661** | **7.2%** |
| **Critical** | **19** | **$82,942** | **3.5%** |
| Not entitled to rostering (assessed separately) | 4 | $32,570 | 1.4% |

**Adoption risk is worth more than twice Critical, and nobody has ever looked at it.**

**Business contraction is not a CS failure.** Those 31 customers use the product properly and are losing associates because their own operation is shrinking. Chasing them wastes effort. Forecast them instead.

---

## 3. Adoption risk: paying more every month, not using it

| Account | Associates | Monthly | Last staffed roster | Msgs/assoc | Assoc change |
|---|---|---|---|---|---|
| Express Package System Inc | 195 | $1,750 | 83d | 0.9 | +25% |
| Wilx Logistics | 179 | $1,613 | none in 14 | 0.5 | +24% |
| Distant Winds Logistics | 154 | $1,386 | 130d | 0.8 | +27% |
| Bison Peak LLC \| DHI2 | 128 | $1,149 | none in 14 | 3.9 | +2% |
| Bison Peak LLC | 126 | $1,137 | none in 14 | 3.9 | +12% |
| Spears Enterprises LLC | 124 | $1,120 | 32d | 0.0 | +7% |
| TPE Logistics Solutions Inc | 111 | $900 | 45d | 0.3 | +12% |
| Pure Logistics USA LLC | 95 | $855 | 59d | 0.0 | +54% |
| RPM Delivery Service | 94 | $845 | none in 14 | 2.2 | +7% |
| Frontline Logistics | 92 | $828 | none in 14 | 3.8 | +2% |
| Black Nile Logistics | 87 | $787 | none in 14 | 3.1 | +20% |
| Flash Hub Delivery | 76 | $686 | none in 14 | 0.2 | +9% |
| Krowned Solutions LLC | 68 | $608 | 78d | 4.9 | +1928% |
| On-demand Logistics Service Llc | 67 | $400 | none in 14 | 0.2 | +8% |
| Double Iron Car Care LLC | 18 | $25 | none in 14 | 0.0 | +29% |
| New Deal Logistics | 3 | $27 | 208d | 0.0 | +0% |
| Shandy Holdings | 2 | $18 | none in 14 | 0.0 | +0% |
| Prolific Logistics | 1 | $4 | none in 14 | 0.0 | +0% |
| K&K Solomon Logistics | 0 | $0 | none in 14 | 0.0 | n/a |

**19 tenants, 18 customers, $169,661 ARR, 1,621 associates.**

The top three are the story. Express Package System has grown 25% to 195 associates and pays $1,750 a month, and has not built a staffed roster in 83 days or sent meaningful messages. Wilx and Distant Winds are the same shape. These are your best-paying non-users, and each is a renewal that dies quietly the first time somebody asks what they are paying for.

Both Bison Peak tenants are here, so at customer level that is one $27,428 relationship, not two small ones.

---

## 4. Critical: declining and abandoned

| Account | Associates | Monthly | Last staffed roster | Msgs/assoc | Assoc change | Under 10 for |
|---|---|---|---|---|---|---|
| DC1 Transport | 137 | $1,234 | none in 14 | 3.1 | -6% | - |
| SkyHook 2 LLC | 115 | $1,035 | 60d | 2.4 | -8% | **23d** |
| SURF Logistics | 114 | $927 | 78d | 0.8 | -11% | - |
| Platinum Transport Services | 114 | $920 | 31d | 0.6 | -8% | - |
| PacTrack, Inc | 79 | $711 | 52d | 0.1 | -6% | - |
| Envizion Logistics LLC | 68 | $562 | 104d | 0.0 | -26% | **28d** |
| MTSL | 45 | $405 | none in 14 | 0.1 | -20% | - |
| Probyn Inc | 41 | $369 | 82d | 0.0 | -66% | - |
| Road Runners Enterprises | 3 | $27 | 129d | 0.0 | -95% | **89d** |
| Syndicate Logistics LLC | 2 | $18 | none in 14 | 0.0 | -84% | **89d** |
| Motaur Express | 1 | $9 | 171d | 0.0 | -91% | **89d** |
| Supreme Delivery | 1 | $9 | 60d | 0.0 | -99% | **59d** |
| Ursa Logistics LLC | 2 | $9 | 94d | 0.0 | -99% | **85d** |
| Your Express Solutions LLC | 0 | $0 | none in 14 | 0.0 | -100% | **89d** |
| DnA Logistics Inc. | 0 | $0 | none in 14 | 0.0 | -100% | **89d** |
| Outlaw Logistics | 185 | $0 | none in 14 | 0.3 | -36% | - |
| Next Level Logistics | 1 | $-1 | none in 14 | 0.0 | -99% | **89d** |

**17 tenants, $74,806 ARR. But only $55,640 is genuinely still at risk.** The remaining $19,166 has already stopped, because those accounts are already below 10 associates and their next invoice will be near zero. See section 5.

**Work the top eight.** Below Probyn Inc the accounts are already collapsed to single digits and are administrative cleanup, not saves.

---

## 5. Under 10 active associates, and revenue that has already stopped

Your rule: fewer than 10 active associates means they are probably leaving. `InvoiceLineItem` carries a daily `activeStaff` count, so this is directly measurable. 89 days of daily history captured per account.

| Account | Peak in window | Now | Days under 10 | Last closed invoice |
|---|---|---|---|---|
| Ursa Logistics LLC | 151 | 2 | 85 | $9 |
| SkyHook 2 LLC | 125 | 0 | 23 | **$1,035** |
| Deliver2U LLC | 122 | 0 | 7 | **$671** |
| Globalteq Logisitcs LLC | 106 | 0 | 11 | **$900** |
| Envizion Logistics LLC | 96 | 1 | 28 | **$562** |
| Merica Delivery Service | 93 | 5 | 15 | **$681** |
| Supreme Delivery | 84 | 1 | 59 | $9 |
| Focus Logistics | 71 | 0 | 15 | **$610** |
| Sarkat Logistics, LLC | 67 | 0 | 7 | $0 comped |
| Road Runners, New Deal, Syndicate, Shandy, Next Level, Motaur, Prolific, K&K Solomon, Your Express, Infinite Delivery, DnA | 0 to 3 | 0 to 3 | 89 | under $30 |

**20 tenants currently under 10 associates.**

**The important number: 6 accounts billed over $100 on their last closed invoice and are now under 10 associates.** SkyHook 2, Globalteq, Merica Delivery, Deliver2U, Focus Logistics, and Envizion. That is **$53,510 of annualized ARR that has already stopped.** Their next invoice will be near zero. Any figure in this document that uses the last closed invoice overstates these six.

**On the consecutive-day question.** All 20 have been under 10 for at least 7 straight days, so a sustained-day requirement does not delay any real alert. But three accounts had a single-day dip under 10 and recovered: Cazar Logistics (peak 134, now 106), Elite OnPoint (peak 116, now 116), and 2Twenty Logistics (peak 115, now 97). **A 3-consecutive-day rule prevents those three false positives at no cost.** Recommend keeping it.

---

## 6. Empty roster shells

Some accounts create roster records and put nothing in them. Somebody opens the tool and does nothing with it.

**133 of 253 tenants have at least one empty roster in 30 days, so a raw count is meaningless.** The ratio is the signal.

| Account | Empty / total | Associates | Monthly | Msgs/assoc |
|---|---|---|---|---|
| Lucky 7 Logistics | 3/3 | 122 | $1,095 | 9.3 |
| SkyHook 2 LLC | 5/5 | 115 | $1,035 | 2.4 |
| Derby Deliveries | 7/10 | 114 | $1,024 | 4.5 |
| JPZ Logistics LLC | 3/3 | 107 | $969 | 8.8 |
| Cargo To You | 4/4 | 102 | $924 | 6.0 |
| Platinum Transport Services | 9/9 | 114 | $920 | 0.6 |
| TPE Logistics Solutions Inc | 4/4 | 111 | $900 | 0.3 |
| Orad Logistics Inc | 9/12 | 99 | $891 | 2.1 |
| RPM Delivery Service | 7/7 | 94 | $845 | 2.2 |
| Infinity Logistics Solutions | 7/8 | 85 | $692 | 17.5 |
| Focus Logistics | 6/8 | 68 | $610 | 1.8 |
| Krowned Solutions LLC | 6/6 | 68 | $608 | 4.9 |
| Outlaw Logistics | 6/7 | 185 | $0 | 0.3 |
| Next Level Logistics | 3/3 | 1 | $-1 | 0.0 |

**14 tenants, $126,127 ARR.** Half are not flagged by any other test, so this catches accounts the quadrants miss. Lucky 7, Derby, JPZ, Cargo To You, Orad, and Infinity Logistics appear here and nowhere else.

---

## 7. What was tested and rejected

Recording this so nobody rebuilds it.

### Rostering depth does not predict revenue decline

Built the weighted daily score John specified: route assigned to associate (1), vehicle assigned (1), attendance via roster status (2), photo log (1), roster checklist (1), stand-up sent (1), general note (1), fleet note (1). Max 9 per day. Piloted on 20 accounts across a 30-day window.

| | Healthy comparators (3) | Declining accounts (15) |
|---|---|---|
| Average daily score | 5.21 | 4.30 |
| Range | 4.0 to 6.0 | 0.0 to 7.6 |

**6 of 15 declining accounts scored above the healthy average.** The highest score in the pilot was Proactive Logistics Home at 7.6, losing 15%. The lowest healthy account was Pure Deliver at 4.0, growing 20%.

The graded score is still useful for ranking adoption-coaching targets. It is not a churn predictor.

**Component firing rates compress it.** Route-to-associate fires on 89% of active days, roster status 82%, vehicle 79%. Those carry 4 of 9 points, so any account that rosters at all starts near 4. The discriminating actions are rare: photo logs 46%, stand-up 28%, general notes 24%, fleet notes 18%, checklist 11%.

### Roster horizon was the wrong metric

Rev 1 measured whether accounts planned rosters ahead. That rewards an account that bulk-builds a week and never returns, which is close to the opposite of daily engagement. It also **missed 10 accounts that were losing revenue**, including Envizion (down 99%, rostered 27 days ago) and Next Level (down 99%, rostered 15 days ago).

### The associates-to-routes ratio is context, not a signal

John's rule of thumb is 1.75x to 2x associates per route, with 1:1 being rare and worth flagging, and no upper bound because of part-timers. In the pilot only 2 of 17 fell below 1.75x, at 1.65x and 1.72x, and neither was near 1:1. Meanwhile it cannot distinguish part-timers from incomplete route entry: Whiterecon showed 23x and Outlaw 1295x, which is clearly missing route data, but the two healthiest large accounts also sat high at 5.4x and 5.5x. Dropped from scoring by decision, kept as account context.

### Messaging threshold, derived not invented

Messages per associate over 30 days across all 253 tenants:

| p10 | p25 | p50 | p75 | p90 | max |
|---|---|---|---|---|---|
| 0.3 | 9.6 | 35.9 | 66.0 | 104.2 | 645 |

34 tenants are under 1.0, 49 are under 5.0, then it jumps to 9.6 at p25. **Under 5 per associate per 30 days** sits in genuine empty space rather than on a slope.

Messaging does not predict decline either. Proactive Logistics has 218 messages per associate, the highest in the pilot, while losing 15%. It is an abandonment detector, same as rostering.

---

## 8. The 67 trials, scored for the first time

Excluding two internal accounts (Hera Deliveries at 3,617 associates, AI Testing at 317).

| | Trials | Associates | Pipeline at $9 |
|---|---|---|---|
| **Engaged** (staffed roster in 30d or 5+ msgs/assoc) | **26** | 2,525 | **$272,700** |
| **Not engaged** | **41** | 4,169 | **$450,252** |

**The non-engaged trials hold more potential revenue than the engaged ones.** Largest: Mako Delivery Service (283 associates, last staffed roster 279 days ago), Amazing Customer Experience Logistics (266, none), Alchemy Logistics (224, none), Deva Logistics (233, 43 days), Out-A-Time Logistics (205, 136 days), Business Logistics Solutions (178, none).

The engaged ones look genuinely active: Lovett Logistix (152 associates, rostered today, 77.8 msgs/assoc), Steady Pace (123, yesterday, 69.4), Zipzone (83, today, 144.4), Pride Delivery (178, yesterday, 50.6).

**Nobody is working this.** 8 trials have zero active associates and 33 have never had a staffed roster in their 14 most recent. At $9 against a median 89 associates, one converted trial is worth about $9,600 a year.

---

## 9. Billing

**$9.00 per active associate per month, charged as $0.30 per associate per day, billed one month in arrears.** July usage invoices on August 1 after the July invoice closes.

Verified from `InvoiceLineItem`, which holds one row per calendar day with that day's `activeStaff` and `bundleCost: 9`. Express Package System, June day 26: `activeStaff` 203, `bundleCostExt` 60.9, exactly 203 x 0.30. Closed invoices on that account bill $8.963 to $9.042 per associate.

**Only `status = 'Active'` associates bill.** The customer controls that status and lags on it, and Hera sends cleanup reminders twice a month, mid-month and a week before close.

### Module price list

| Module | Per associate |
|---|---|
| **Bundle** | **$9** |
| Standard | $2 |
| Performance | $3 |
| Rostering | $1 |
| Staff | $3 |
| Vehicles | $1 |
| Sum a la carte | $10 |

Legacy accounts still on module pricing pay the sum of their modules, which is why some bill exactly $5, $6, or $7.

### Audit against the $9 list

180 of 249 tenants pay full $9. The $222,393 annual gap breaks down as:

| Bucket | Tenants | $/yr | Status |
|---|---|---|---|
| Labeled discount programs | 47 | $140,250 | Intentional |
| Legacy module pricing | 9 | $29,283 | Grandfathered, working as configured |
| Discount baked into base rate | 7 | $43,105 | Intentional, but not auditable via `discountPercent` |
| **Unexplained** | **3** | **$17,029** | **Needs resolution** |

Discount programs: Customer Service $34,345 (3 accounts), Internal $32,511 (MBB, comped for internal support), Veteran $26,625 (20), DeliverRe $14,670 (14), Overpayment $12,608, plus First Responder, CA wildfire, Customer Retention and Discretionary.

### Billing anomalies to resolve

| Account | Associates | Billing | Issue |
|---|---|---|---|
| **Philosophe LLC** | 72.9 | $0 | On `bundle`, no discount label, no recorded reason. **$7,877/yr** |
| **Integrated Logistics Solutions LLC** | 62.2 | $0 | Same. **$6,713/yr** |
| **Crucial Mile Logistics LLC** | 175.0 | $7.839/assoc | `accountPremiumStatus` is `['None']`, no modules recorded at all. **$2,439/yr** |
| Elite OnPoint Delivery Service | 75.5 | $9.30/assoc | Above list, no label. Needs research |
| Envizion Logistics LLC | 68.4 | $9.13/assoc | Above list, carries a DeliverRe label |
| Active Transportation, LBM Last Mile, SURF \| HEW4 | | $8.40 to $8.75 | Bundle, slightly under, no label. $1,012/yr combined |

**Intentionally comped, confirmed:** MBB Delivery (301 associates, provides internal support to Hera). Four others carry labels: Home Stretch, KJ Logistics, Cazar, Double Iron.

**A structural note:** because discounts can live either in `discountPercent` or in the base rate, any future pricing report must check both. Reading `discountPercent` alone would miss $43,105.

---

## 10. The four accounts not entitled to rostering

These are on legacy module pricing without the rostering module, so they physically cannot roster. Scored instead on what they do have: coaching and scorecard import.

| Account | Associates | Monthly | Scorecards ever | Last scorecard | Counselings 30d | Infractions 30d | Kudos 30d | Verdict |
|---|---|---|---|---|---|---|---|---|
| **DBE Logistics, Inc.** | 91.4 | $457 | 245 | **2026 wk 29** | 0 | **224** | **2,386** | **Heavily engaged** |
| Deliver2U LLC | 112.0 | $671 | 89 | 2023 wk 04 | 66 | 0 | 0 | Partly engaged |
| EZ Logistix LLC | 92.2 | $460 | 98 | 2024 wk 09 | 18 | 0 | 0 | Partly engaged |
| Crucial Mile Logistics LLC | 175.0 | $1,372 | 216 | 2025 wk 32 | 0 | 0 | 0 | Abandoned |
| Divine Package LLC | 43.0 | $215 | 220 | 2025 wk 19 | 0 | 0 | 0 | Abandoned |
| Infinite Delivery OPS LLC | 0.0 | $0 | 334 | 2026 wk 14 | 0 | 0 | 0 | Dead |

**DBE Logistics is one of your most engaged customers and I nearly mislabeled it abandoned.** Current scorecard, 224 infractions and 2,386 kudos logged in 30 days. It scores zero on rostering because it does not have rostering. It pays $5.00 per associate on legacy module pricing.

**That makes DBE the clearest upsell in the book.** A customer demonstrably getting value from coaching, paying $5, missing rostering and messaging entirely. Moving them to bundle at $9 is a value conversation, not a price increase.

Crucial Mile is the opposite: 175 associates, $1,372 a month, no modules recorded, last scorecard nearly a year old, zero coaching activity. Abandoned on everything, and also one of the billing anomalies.

---

## 11. Retention

Cohort method: the 305 tenants already paying in June 2025, followed to June 2026 using closed invoices at both ends. New customers excluded.

| | Amount | Tenants |
|---|---|---|
| Cohort ARR, June 2025 | **$2,430,676** | 305 |
| Lost, Amazon DSP program closure | -$243,393 | 34 |
| Lost, addressable churn | -$362,697 | 47 |
| **Change inside surviving accounts** | **+$254,260** | 224 (**+13.9%**) |
| **ARR, June 2026** | **$2,078,846** | 224 |

| Measure | Result |
|---|---|
| GRR, all causes | **85.5%** |
| **GRR, addressable** | **95.0%** |
| Program-closure drag | 10.0% |

**Surviving customers expanded 13.9% with no sales motion**, because billing follows headcount and they hired.

**The 90% addressable GRR target set during setup is already exceeded by $110,292.** It needs replacing. Options: 96 to 97% addressable GRR, a target on all-causes GRR (85.5% today), or a target on the trial funnel, which is entirely unworked and holds $722,952 of potential.

**Churn dating caveat:** Matthew or Liz mark accounts churned manually and charge usage to that point, sometimes writing off the balance. So cohort membership dates are approximate.

---

## 12. Why customers leave

`accountCanceledReason` populated on 430 of 497 churned tenants.

| Reason | Lifetime | Share | Preventable? |
|---|---|---|---|
| **DSP Closed** | 181 | 38.7% | **No.** Went out of business |
| Didn't Fully Utilize or Find Value | 92 | 19.7% | **Yes** |
| (blank) | 60 | 12.8% | Unknown |
| Switched to Competitor | 56 | 12.0% | Yes |
| Cost Savings | 48 | 10.3% | Partly |
| Internal processes | 9 | 1.9% | Partly |
| Route reduction, site closure, dropped to zero | 12 | 2.6% | No |
| Stopped Using, No Explanation | 6 | 1.3% | Yes |

**Trailing 12 months, competitive loss is the largest addressable bucket** at 20 accounts and $148,097, ahead of underutilization at 10 accounts and $84,226.

| Competitor | Lifetime | Last 12 months |
|---|---|---|
| DSPworkplace | 23 | 5 |
| LMDmax | 17 | 6 |
| **"Other", unnamed** | **13** | **11 ($82,472)** |
| Manage my DSP | 1 | 2 |
| Lokiteck | 2 | 1 |

**Your largest single competitive loss this year is to a competitor nobody recorded the name of.**

**Timing:** median tenure at churn 18 months, p10 5 months. **29% churned inside 12 months** against a 40-month median for survivors.

---

## 13. Data quality register

| Field | Problem | What to do |
|---|---|---|
| **`Invoice.status = 'Pending'`** | The in-progress month, still accruing | Filter to closed invoices for revenue. **Caused every rev 2 error** |
| **`Tenant.averageMonthlyInvoiceTotal`** | Lifetime average, not current | Use the latest closed `Invoice.invoiceTotal`. **Caused every rev 1 error** |
| **`StaffStatus` status fields** | Fields are `currentStatus` and `previousStatus`, not `status` | Projecting `status` returns nothing and looks like "no data exists." **I first concluded zero cleanups across 30 accounts** |
| **Associate status is customer-controlled** | Only `Active` bills, and customers lag on marking people Inactive | Always check `StaffStatus` for a bulk cleanup before reading a decline as churn |
| **`Route.byGroupAndTime`** | `time` is a clock time like `18:30`, not a date. `Route` has no date field | Reach routes via `DailyRoster` then `gsi-RouteDailyRoster` |
| **Rostering entitlement** | Accounts without `bundle` or `rostering` cannot roster | Check `accountPremiumStatus` before flagging non-rostering. **This produced 6 false positives** |
| **Empty roster shells are normal** | 133 of 253 tenants have at least one in 30 days | Use the empty-to-total ratio, never the count |
| **Multi-site tenants** | 7 customers appear as 14 tenants via `\| STATION` suffixes. `parentAccountId` is never populated | Roll up by name before counting customers |
| `DailyRoster.notesDate` | The date a roster is built **for**, scheduled ahead | Never compute "days since." 8 tenants also have implausible values, clamp the range |
| `User.lastLogin` | Can hold the literal string `NOT_YET_LOGGED`, which sorts above real timestamps | Filter before any `max()`. Silently dropped 118 of 253 |
| `InvoiceLineItem.month` | Often absent, and inconsistent when present | Use `date` only |
| `Invoice.year#month` | Per repo `CLAUDE.md`: December stored as `<next-year>#0` | Filter on `createdAt` |
| `firstChurnedDateTime` | Missing on 267 of 497 churned | Use `customerStatus` |
| `firstConvertedToPaidDateTime` | Sparse | Use `totalNumberOfMonthsPaidByTenant > 0` |
| `numberOfSeats` | Absent on 198 of 253 | Irrelevant, billing is per associate |
| `accountType` | Null on 502 of 872, `PARENT` / `CHILD` never used | Multi-entity rollup does not work |
| `featureAccessX` vs `featureEnabledX` | Access is not a superset of enabled | Do not compute a gap between them |
| Contract dates | **No contract, term, renewal, or expiration field exists** | Month-to-month, no renewal event |
| `Payment Error` status | Stripe failed (NSF, blocked, expired card), customer must act | An involuntary-churn signal, not noise |
| Internal accounts | Hera Deliveries (3,617 associates) and AI Testing (317) are not customers | Exclude from all trial and book figures |

---

## 14. Open

### Awaiting John

1. **Seasonality.** Peak-season detail to come. Every threshold here comes from a mid-summer window, so a July decline cannot yet be separated from a seasonal trough. This is the one input that could move numbers.
2. **Routing and ownership per quadrant.** Config currently sends At Risk and Critical to John as a Zoho task. There are now five states, and Adoption Risk plausibly belongs with CSS 1 as an adoption conversation rather than with John as a save. Who owns the empty-shell list is also unassigned.
3. **Response times.** Now answerable, since the queues are small: 17 Critical, 19 Adoption Risk, 14 empty-shell, 20 under-10.
4. **Billing anomalies.** Philosophe, Integrated Logistics, and Crucial Mile pending the conversation with Matthew. Elite OnPoint and Envizion billing above list need research.

### Still unmeasured

5. **Phantom billing exposure.** How many currently-Active associates across the book have not worked in months. Measurable against `Route`. This is what a customer would discover.
6. **Is $9 above or below market?** Competitive loss is the largest addressable bucket and "Cost Savings" adds 10.3%, but what DSPworkplace and LMDmax charge is unknown.
7. **Associate decline versus Amazon route cuts.** Separates unfixable viability from an operational problem Hera's coaching tools address.
8. **The unnamed competitor.** $82,472 lost this year. The answer is likely in the 312 `accountCanceledNotes` records.
9. **Support signal.** Intercom holds conversations and sentiment per company. Never pulled.
10. **No intervention log.** Nothing records what was tried or whether it worked, so none of these thresholds can be calibrated against outcomes yet.

### Config locations

- `~/.claude/plugins/config/claude-for-customer-success/company-profile.md`
- `~/.claude/plugins/config/claude-for-customer-success/csm/CLAUDE.md`
