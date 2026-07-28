# Customer Success Health Baseline

**Date:** 2026-07-28
**Source:** live queries against production DynamoDB (AWS `530079012632`, `us-east-2`, profile `hera-readonly`)
**Author:** produced during `/csm:cold-start-interview` setup
**Cached query output:** `data/` in this folder

Every number here came from a live query, not an estimate. Where a figure is derived or carries a caveat, it says so.

---

## 1. Glossary

I used a lot of abbreviations during this analysis. Here is what all of them mean.

### Money

| Term | What it means | Your number |
|---|---|---|
| **ARR** | Annual Recurring Revenue. What one customer pays across a year. Monthly invoice times 12 | Median customer: $668/mo, so $8,014 ARR. Whole book: $2.10M |
| **GRR** | Gross Revenue Retention. Of the money you had at the start of the year from customers you already had, how much you still have. Ignores new customers and ignores upsells. Can never go above 100% | 77.1% |
| **NRR** | Net Revenue Retention. Same thing but it counts upgrades, so it can exceed 100% | Not measurable yet |
| **AR** | Accounts Receivable. Money billed but not yet collected | 3 accounts, $3,053 |

### Roles

| Term | What it means |
|---|---|
| **CS** | Customer Success. The function that keeps customers using the product and paying for it |
| **CSM** | Customer Success Manager. Owns the relationship for a set of customers |
| **CSS** | Customer Success Specialist. Your two team members |
| **AE** | Account Executive. A salesperson. Hera does not have one, which is why expansion signals currently have nowhere to route |

### Process

| Term | What it means |
|---|---|
| **QBR** | Quarterly Business Review. A scheduled meeting where you show a customer the value they received and plan the next quarter. Usually a slide deck |
| **SLA** | Service Level Agreement. A promised response time. "At Risk accounts get worked within 5 business days" is an SLA |
| **Health score** | A rating (Healthy, Developing, At Risk, Critical) computed from signals, used to decide which customers need attention |
| **Churn** | A customer leaving |
| **Whitespace** | Something a customer could buy but has not. Your 221 accounts without HeraAi |
| **Expansion** | Selling more to a customer you already have |

### Statistics

| Term | What it means |
|---|---|
| **p50, p75, p90** | Percentiles. p50 is the middle value, also called the median. p90 means 90 percent of accounts fall below that number |
| **r = 0.535** | Correlation, on a scale from -1 to 1. How strongly two things move together. 0.535 is a moderate positive relationship |
| **Cohort** | A fixed group of accounts tracked over time. Used here to measure retention honestly, by following the same accounts rather than mixing in new ones |

### Hera domain terms, recorded so the config uses them correctly

**DSP** is Delivery Service Partner, your customer. **DA** is Delivery Associate, a driver. Amazon scorecard metrics referenced in the product: FICO, DCR, DC DPMO, DAR, DNR.

---

## 2. What the book actually looks like

| | |
|---|---|
| Total tenant records | 953 |
| Test and temporary accounts (excluded from everything below) | 81 |
| **Active paying accounts** | **253** (243 Bundle, 10 Premium) |
| Trials in flight | 68 |
| Lapsed trials | 54 |
| Churned | 497 |
| **Total ARR, annualized** | **$2,097,712** |
| Median tenure | 40 months paid (p25 26, p75 56, longest 64) |
| Customer type | 100 percent Amazon DSP |
| Sub-type | 802 ZL, 68 XL, 2 Lite |

Your coverage book is **321 accounts**: 253 paying plus 68 trials.

Earlier in the session I estimated 230 accounts per person based on Intercom's 693 company records. That was wrong. Many of those records are archived or test accounts. The real active book is 253.

---

## 3. Why revenue-based tiering does not work for you

Most customer success advice assumes you have a few large customers worth protecting and a long tail worth automating. You do not have that shape.

| Percentile | Monthly invoice | ARR |
|---|---|---|
| p10 | $448 | $5,380 |
| p25 | $543 | $6,510 |
| **p50 (median)** | **$668** | **$8,014** |
| p75 | $831 | $9,973 |
| p90 | $990 | $11,874 |
| p95 | $1,095 | $13,142 |
| Largest | $1,348 | $16,179 |

**Your largest account is 2.0 times your median.** For comparison:

| | Share of your total ARR |
|---|---|
| Top 10 accounts | 7.1 percent |
| Top 20 accounts | 13.1 percent |
| Top 50 accounts | 29.3 percent |

In a typical business-to-business software company, the top 10 percent of accounts carry 40 to 60 percent of revenue. Yours carry about 13 percent.

**What this means practically.** "Give the biggest accounts white-glove treatment" has no financial justification here, because the biggest account is worth $16,179 and the median is worth $8,014. Any tier you built on revenue would contain accounts that behave identically. This is why the health model is built on engagement instead, which is covered in section 7.

---

## 4. Associates under management

| | |
|---|---|
| **Total active drivers across all accounts** | **22,888** |
| Median per account | 89 |
| p25 | 69 |
| p75 | 112 |
| p90 | 138 |
| p95 | 158 |
| Largest | 338 (JDW Logistics) |
| Smallest | 0 (see section 8) |

Driver count varies more than revenue does (3.8 times median versus 2.0 times), but not enough to build tiers on either. **86 percent of your accounts run between 50 and 199 active drivers.**

| Size band | Accounts | Share | ARR | Drivers |
|---|---|---|---|---|
| Under 20 drivers | 22 | 8.7% | $174,494 | 59 |
| 20 to 49 | 9 | 3.6% | $47,986 | 377 |
| 50 to 99 | 125 | 49.4% | $886,858 | 9,664 |
| 100 to 199 | 93 | 36.8% | $941,733 | 11,710 |
| 200 or more | 4 | 1.6% | $46,640 | 1,078 |

Correlation between monthly invoice and active driver count is **r = 0.535**, a moderate positive relationship. Your pricing already tracks operational size to a degree, which is another reason a separate size tier would add little.

---

## 5. Retention, measured properly

I measured this as a cohort: the accounts that were already paying you on 2025-07-28, followed forward. New customers acquired during the year are excluded, because including them hides churn.

| | |
|---|---|
| Cohort on 2025-07-28 | 302 accounts, $2,458,146 ARR |
| Still active on 2026-07-28 | 226 accounts, $1,895,460 |
| Churned during the year | 76 accounts, $562,686 |
| of which: Amazon DSP program closure | 30 accounts, $210,062 |
| of which: addressable | 46 accounts, $352,624 |
| New customers added during the year (excluded) | 26 accounts, $189,824 |

| Measure | Result |
|---|---|
| **Gross retention, all causes** | **77.1 percent** |
| **Gross retention, addressable only** | **85.7 percent** |
| Logo retention (count, not dollars) | 74.8 percent |
| Program-closure drag | 8.5 percent |

**Why the split matters.** 30 of the 76 accounts you lost went out of business or left the Amazon DSP program. Your own records label this "DSP Closed." Nobody on your team could have saved them. If you set a retention target that counts those against your team, they will chase unwinnable accounts and miss the ones they could actually keep.

**Caveat, stated plainly.** This uses each account's current average monthly invoice as its ARR, because the database keeps no historical price snapshots. Any price increases or downgrades inside surviving accounts are invisible to this calculation.

---

## 6. Why customers leave

`accountCanceledReason` is populated on 430 of 497 churned accounts, and `accountCanceledNotes` on 312. This is real loss data, not speculation.

### All 469 paid churns, lifetime

| Reason | Accounts | Share | Can CS prevent it? |
|---|---|---|---|
| **DSP Closed** | 181 | 38.7% | **No.** Customer went out of business |
| **Didn't Fully Utilize or Find Value** | 92 | 19.7% | **Yes** |
| (blank) | 60 | 12.8% | Unknown |
| Cost Savings | 48 | 10.3% | Partly, through value justification |
| Switched to Competitor (all) | 56 | 12.0% | Yes |
| Internal processes, built their own | 9 | 1.9% | Partly |
| Reduced routes, dropped drivers to zero, site closure | 12 | 2.6% | No, business contraction |
| Stopped Using, No Explanation | 6 | 1.3% | Yes |

**About 41 percent of your churn is the Amazon DSP program churning, not Hera. About 45 percent is addressable.**

### The trailing 12 months tell a different story

| Reason | Accounts | ARR lost |
|---|---|---|
| **Switched to competitor (all)** | **20** | **$148,097** |
| Didn't Fully Utilize or Find Value | 10 | $84,226 |
| Cost Savings | 7 | $54,988 |
| Internal processes, built their own | 5 | $37,201 |
| Stopped Using, No Explanation | 3 | $19,218 |
| Pause Subscription | 1 | $8,994 |

**Competitive loss is now your largest addressable bucket.** Lifetime, underutilization dominated at 92 accounts. In the last year, competitor switching cost you more.

### Named competitors, from your own loss records

| Competitor | Lifetime losses | Last 12 months |
|---|---|---|
| DSPworkplace | 23 | 5 |
| LMDmax | 17 | 6 |
| **"Other," unnamed** | **13** | **11 ($82,472)** |
| Manage my DSP | 1 | 2 |
| Lokiteck | 2 | 1 |

**The largest single competitive bucket this year is a competitor nobody recorded the name of.** 11 accounts and $82,472 lost to "Switched to Competitor - Other." That is a gap in your own tracking, and it is worth closing before the next loss.

### When customers leave

| | |
|---|---|
| Median tenure at churn | 18 months |
| p10 | 5 months |
| p25 | 10 months |
| **Churned inside 12 months** | **29 percent (138 of 469)** |

Surviving accounts have a 40-month median tenure. So you either lose an account early or you keep it for years. **Intervention is worth most in the first year.**

---

## 7. How to tell a healthy account from a dying one

### The signal that works: roster horizon

`DailyRoster.notesDate` is the date a roster is built *for*, and customers schedule ahead. So a healthy account's most recent roster date is in the **future**. I measure "roster horizon" as the most recent roster date minus today.

| Band | Rule | Accounts | ARR | Share of ARR |
|---|---|---|---|---|
| **Healthy** | Scheduling today or ahead | 173 | $1,408,907 | 67.2% |
| **Developing** | Stopped 1 to 30 days ago | 35 | $312,373 | 14.9% |
| **At Risk** | Stopped 31 to 90 days ago | 17 | $155,082 | 7.4% |
| **Critical** | Stopped over 90 days ago | 8 | $45,355 | 2.2% |
| **Unclassified** | No roster record (21) or corrupt date (8) | 29 | needs investigation | |

### The signal that fails: logins

This is the most important finding in the whole analysis.

Of the 25 accounts that have not built a roster in 30 or more days, **10 logged in within the last 7 days**, and 4 logged in today. A health score built on login activity, or on seat counts, would rate every one of them healthy.

| Account | Roster stopped | Last login | Active drivers | Monthly |
|---|---|---|---|---|
| Clark Courier Service LLC | 86 days ago | **today** | 155 | $1,095 |
| Last Mile Logistics LLC | 83 days ago | **today** | 140 | $1,031 |
| Express Package System Inc | 82 days ago | **today** | 186 | $877 |
| Motaur Express | 94 days ago | yesterday | 1 | $796 |
| On-demand Logistics Service Llc | 52 days ago | yesterday | 62 | $330 |
| Active Transportation Services LLC | 41 days ago | **today** | 71 | $327 |
| EZ Logistix LLC | 54 days ago | 6 days ago | 95 | $538 |
| PacTrack, Inc | 36 days ago | 6 days ago | 79 | $740 |
| MTSL | 55 days ago | 7 days ago | 42 | $541 |
| Spears Enterprises LLC | 31 days ago | 7 days ago | 115 | $998 |

Those 10 accounts are worth **$87,291 in ARR**.

These customers still log in almost daily. They abandoned the core daily workflow while continuing to use something else in the product. That pattern is invisible to conventional health scoring, and it maps directly onto your single largest addressable churn reason: "Didn't Fully Utilize or Find Value," 92 lifetime losses. Add "Dropped Associates to 0" (3) and "Stopped Using, No Explanation" (6) and that is **101 historical losses to exactly the pattern roster horizon detects.**

For completeness, the reverse case is rare: only 5 accounts are rostering normally but have not logged in for over 14 days. Login recency is not useless, it is just far weaker on its own.

---

## 8. Accounts needing attention right now

### 25 accounts have not built a roster in 30 or more days

**$200,436 in ARR.**

| Account | Roster stopped | Last login | Active drivers | Users | Monthly |
|---|---|---|---|---|---|
| DBE Logistics, Inc. | 445 days ago | 15 days ago | 94 | 4 | $369 |
| Prolific Logistics | 376 days ago | 181 days ago | 1 | 27 | $546 |
| Double Iron Car Care LLC | 292 days ago | 34 days ago | 18 | 5 | $25 |
| Black Nile Logistics | 216 days ago | 12 days ago | 75 | 5 | $526 |
| New Deal Logistics | 207 days ago | 277 days ago | 3 | 10 | $676 |
| Divine Package LLC | 183 days ago | 99 days ago | 43 | 5 | $301 |
| Shandy Holdings | 173 days ago | 180 days ago | 2 | 30 | $539 |
| Motaur Express | 94 days ago | yesterday | 1 | 15 | $796 |
| Clark Courier Service LLC | 86 days ago | today | 155 | 6 | $1,095 |
| Last Mile Logistics LLC | 83 days ago | today | 140 | 9 | $1,031 |
| Express Package System Inc | 82 days ago | today | 186 | 25 | $877 |
| Pure Logistics USA LLC | 58 days ago | 64 days ago | 95 | 7 | $828 |
| Supreme Delivery | 58 days ago | 10 days ago | 1 | 15 | $814 |
| Ursa Logistics LLC | 56 days ago | 12 days ago | 2 | 27 | $590 |
| Your Express Solutions LLC | 55 days ago | 13 days ago | 0 | 24 | $1,203 |
| MTSL | 55 days ago | 7 days ago | 42 | 8 | $541 |
| Probyn Inc | 55 days ago | 55 days ago | 41 | 21 | $855 |
| EZ Logistix LLC | 54 days ago | 6 days ago | 95 | 16 | $538 |
| On-demand Logistics Service Llc | 52 days ago | yesterday | 62 | 3 | $330 |
| K&K Solomon Logistics | 50 days ago | 50 days ago | 0 | 6 | $840 |
| Infinite Delivery OPS LLC | 45 days ago | 70 days ago | 0 | 7 | $263 |
| Active Transportation Services LLC | 41 days ago | today | 71 | 7 | $327 |
| Bison Peak LLC | 41 days ago | 9 days ago | 121 | 15 | $1,053 |
| PacTrack, Inc | 36 days ago | 6 days ago | 79 | 20 | $740 |
| Spears Enterprises LLC | 31 days ago | 7 days ago | 115 | 4 | $998 |

### 9 accounts have zero active drivers

**$76,815 in ARR.** These accounts are paying you while having no driver in `Active` status.

| Account | Roster | Last login | Users (never logged in) | Monthly |
|---|---|---|---|---|
| Your Express Solutions LLC | 55 days ago | 13 days ago | 24 (1) | $1,203 |
| SkyHook 2 LLC | 11 days ago | 12 days ago | 26 (2) | $1,014 |
| K&K Solomon Logistics | 50 days ago | 50 days ago | 6 (3) | $840 |
| Focus Logistics | 7 days ago | 12 days ago | 9 (2) | $708 |
| DnA Logistics Inc. | no record | 6 days ago | 31 (1) | $704 |
| Globalteq Logisitcs LLC | 10 days ago | 10 days ago | 12 (4) | $667 |
| Deliver2U LLC | 6 days ago | 7 days ago | 10 (3) | $558 |
| Sarkat Logistics, LLC | 7 days ago | 10 days ago | 19 (1) | $445 |
| Infinite Delivery OPS LLC | 45 days ago | 70 days ago | 7 (3) | $263 |

**This was verified, not assumed.** Every driver at these accounts sits in an `Inactive` status. To rule out a status-vocabulary problem I checked a control account: JDW Logistics shows 338 drivers in `Active` against the same status set, so the field is being used consistently and these zeros are real.

**Two of these are rebuilding, not dying.** DnA Logistics has 69 drivers in `Onboarding` status and Globalteq has 2. They are restaffing. The other seven have no onboarding pipeline at all.

**Six of them are an odd case worth a look.** Focus Logistics, Sarkat, SkyHook 2, DnA, Deliver2U, and Globalteq are all rostering within the last 11 days while showing zero active drivers. Building rosters with no active drivers should not really happen. Most likely they stopped maintaining driver status and are rostering against people marked Inactive, which is a data-hygiene and training problem rather than a churn signal. Worth one call to find out which.

### Combined

Removing the 3 accounts that appear on both lists:

**31 unique accounts need attention, worth $249,584 in ARR, which is 11.9 percent of your book.**

---

## 9. Every factor that could feed a health score

This is the section that got cut off in the terminal.

For each factor: what it tells you, where it comes from, and whether it is measured, measurable, or ruled out. "Measurable" means the database has the right index to compute it cheaply per account, roughly 253 fast queries, but I have not run it yet.

### Group A: Are they doing the daily work?

This is what your team can actually influence.

| Factor | What it tells you | Source | Status |
|---|---|---|---|
| **Roster horizon** | Have they scheduled drivers for upcoming days | `DailyRoster`, index `byGroupAndNotesDate` | **Measured.** 173 healthy, 80 lapsed |
| **Messaging volume** | Are they texting and emailing drivers through Hera, or have they gone back to personal phones | `Message`, index `byGroup` = group + createdAt | Measurable |
| **Daily log volume** | Are they recording what happened each day | `DailyLog`, index `byDate` = group + date | Measurable |

### Group B: Are they using what they pay for?

| Factor | What it tells you | Source | Status |
|---|---|---|---|
| **Scorecard upload freshness** | Are they still uploading their weekly Amazon scorecard. This is a weekly ritual, so a gap is a loud signal | `CompanyScoreCard`, index `byGroup` = group + yearWeek | Measurable |
| **Coaching activity** | Are they logging counselings, infractions, and kudos on drivers | `Counseling`, `Infraction`, `Kudo`, all indexed `byGroupAndDate` | Measurable |
| **Feature adoption** | Which optional modules they have turned on | `Tenant` flags | **Measured**, see below |

Feature adoption as it stands today, across 253 active accounts:

| Feature | Accounts using it | Share |
|---|---|---|
| `featureEnabledCounselings` | 233 | 92% |
| `featureEnabledAssociateApp` | 146 | 58% |
| `permissionHeraAi` | **32** | **13%** |
| InventoryManagement, RosterChecklist | ~253 | ~100%, no useful signal |

**HeraAi at 13 percent is your clearest expansion opportunity: 221 accounts have not turned it on.**

### Group C: Is their business shrinking?

You cannot fix these, but you can see them coming, and that matters because 38.7 percent of your churn is customers going out of business.

| Factor | What it tells you | Source | Status |
|---|---|---|---|
| **Route volume trend** | How many delivery routes they run. If Amazon cuts their routes, they are shrinking | `Route`, index `byGroupAndTime` | Measurable |
| **Driver headcount trend** | Are their active drivers growing or falling | `Staff`, index `byGroupStatus` | **Measured** as a snapshot. Trend not yet measured |
| **Driver turnover** | How fast drivers churn inside their operation | `StaffStatus`, index `byGroup` = group + date | Measurable |

### Group D: Are the right people still showing up?

| Factor | What it tells you | Source | Status |
|---|---|---|---|
| **Login recency** | When anyone last logged in | `User`, index `gsi-TenantUsers` | **Measured.** Weak on its own, see section 7 |
| **Active user count** | How many of their people actually use it, versus just having an account | `User` | Partly measured |
| **Never-logged-in seats** | Accounts created but never used, an onboarding gap | `User` | **Measured.** 622 of 3,672 user records, 17 percent, have never logged in once |

### Group E: Commercial

| Factor | What it tells you | Status |
|---|---|---|
| **Discount depth** | Heavily discounted accounts predict your "Cost Savings" churn reason, 10.3 percent of losses | Measurable |
| **Unpaid balance** | Money owed | **Measured.** Only 3 accounts, $3,053 total. Not a meaningful risk signal for you |
| **Tenure** | Months paid. Under 12 months is your danger zone, 29 percent of losses | **Measured** |

### Ruled out

**Overall app activity from the audit log.** `AuditLog` is indexed on group plus `email#createdAt`, so there is no way to range-query by date across all users of an account. Counting it per account would mean reading roughly 27,000 rows per customer. Too expensive to run on a schedule. Recording it here so nobody rediscovers it later and assumes it was overlooked.

---

## 10. Proposed band definitions

### Count red flags, do not weight percentages

Weighted scoring ("usage 40 percent, support 20 percent, engagement 20 percent") is standard advice, but it is hard to explain, hard to tune, and produces a number nobody can reason about. Counting red flags is closer to how you would actually think about an account.

| Band | Rule |
|---|---|
| **Critical** | Roster stopped over 90 days ago, OR zero active drivers, OR 3 or more red factors |
| **At Risk** | Roster stopped 31 to 90 days ago, OR 2 red factors |
| **Developing** | Roster stopped 1 to 30 days ago, OR 1 red factor |
| **Healthy** | No red factors |

Individual factor thresholds are not set yet. They should be set the same way the roster bands were: measure the factor across all 253 accounts, look at where the natural break falls in the distribution, then draw the line. Setting them by intuition first would defeat the point.

### Keep two separate scores

**Health** uses Groups A, B, D, and E. It answers "is there something we can do here."

**Viability** uses Group C on its own. It answers "is this customer's business going to survive."

**Do not blend them.** 38.7 percent of your churn is customers losing their Amazon contract or closing. Folding that into a health score makes the score unactionable and sends a two-person team after accounts nobody can save. Viability exists to forecast revenue and to decide where *not* to spend effort.

### The highest-value thing you are not yet using

You hold every customer's weekly Amazon scorecard in `CompanyScoreCard`, 88,580 records indexed by tenant and week. That means your single largest churn bucket, customers losing their Amazon contract, is **forecastable** even though it is not preventable. No customer success platform you could buy would give you that, because it depends on data only Hera has.

---

## 11. Data quality register

These are traps that produce confidently wrong answers. Two of them caught me during this session.

| Field | Problem | What to do |
|---|---|---|
| `DailyRoster.notesDate` | It is the date a roster is built **for**, scheduled in advance, not a creation timestamp. Healthy accounts have a future date | Never compute "days since last roster." Use horizon: most recent date minus today. **This bug hit me first time through** |
| `User.lastLogin` | Can hold the literal string `NOT_YET_LOGGED`, which sorts above real ISO timestamps because "N" is greater than "2" | Filter it out before any `max()`. **This bug hit me too, and silently dropped 118 of 253 accounts** |
| `firstChurnedDateTime` | Missing on 267 of 497 churned accounts | Use `customerStatus` instead |
| `firstConvertedToPaidDateTime` | Sparsely populated. Using it, I calculated 78 paid churns. The real figure is 468 | Use `totalNumberOfMonthsPaidByTenant > 0` |
| `numberOfSeats` | Absent on 198 of 253 active accounts | Seat-based health or expansion math is not possible |
| `accountType` | Null on 502 of 872. `PARENT` and `CHILD` never populated | Multi-entity rollup does not work despite schema support |
| `featureAccessX` vs `featureEnabledX` | Access is not a superset of enabled. `featureAccessAssociateApp` is 0 on all 253 accounts while `featureEnabledAssociateApp` is 146 | Do not compute "access minus enabled" as an adoption gap. **I asserted this early in the session and it was wrong** |
| `cost*` fields | `costBundle`, `costStandard`, `costPerformance`, `costRostering`, `costStaff`, `costVehicles` are nonzero on all 253 accounts. `costMessaging` is 0 on all | These are price-list fields, not entitlement markers |
| `DailyRoster.notesDate` range | 8 accounts have values far outside any plausible range | Clamp to roughly -2000 to +400 days from today |
| No roster record | 21 active accounts have no `DailyRoster` row at all | Treat as unclassified, not healthy |
| Contract and renewal dates | **No contract, term, renewal, or expiration field exists anywhere on `Tenant`** | Hera is month-to-month. There is no renewal event and no 90/60/30 day runway. Retention is continuous |
| `Invoice.year#month` | Documented in repo `CLAUDE.md`: December is stored as `<next-year>#0` rather than `<year>#12` | Filter on `createdAt` for month-based queries |

---

## 12. What is decided and what is still open

### Decided and written into the plugin config

- Motion is hybrid and segmented, with the segmentation axis being **engagement state, not revenue**
- Health bands set on roster horizon, per section 7
- Team is roughly 1.5 effective account owners, not 3. John covers the full book, CSS 1 is building toward an owned book with a retention bonus, CSS 2 is a detection layer with no book
- CSS 1's retention bonus must exclude Amazon DSP program closures
- Retention targets: **90 percent addressable GRR** for the team, 80 percent all-causes reported to the CEO, HeraAi attach from 13 to 25 percent standing in for an NRR target
- Escalation goes to John as a Zoho task, with the weekly CEO management meeting as the second tier
- Primary value metric is operational time saved, with the explicit caveat that it is **not instrumented**, so no skill may state a time-saved figure as fact

### Still open

1. **Escalation response times.** Stalled because they depend on how many accounts each band contains once the bands are multi-factor
2. **The 9 measurable factors in section 9.** Measure them, look at the distributions, then set thresholds
3. **QBR format.** At 107 accounts per person, month-to-month, with no renewal event, standing per-account QBRs may not be viable at all
4. **The unnamed competitor.** 11 accounts and $82,472 lost this year to "Switched to Competitor - Other." Worth finding out who that is
5. **Outcome catalog.** Marked pending. Probably worth waiting until the time-saved metric has a real proxy

### Config file locations

- `~/.claude/plugins/config/claude-for-customer-success/company-profile.md`
- `~/.claude/plugins/config/claude-for-customer-success/csm/CLAUDE.md`
