# Shared Company Profile
*Written by /csm:cold-start-interview on 2026-07-28. Shared across all claude-for-customer-success plugins.*

**Style rule (applies to all generated output, internal and customer-facing): never use em dashes or en dashes. Use commas, periods, parentheses, or colons instead.** Source: user preference recorded in `~/bitbucket-hera/CLAUDE.md`.

---

## Who we are

**Company:** Hera Solutions Inc.
**Product:** Hera, an operations platform for Amazon Delivery Service Partners (DSPs). Covers daily rostering, associate (Delivery Associate) management, performance coaching against Amazon scorecards, SMS/email messaging, vehicle and inventory management, counselings, and document handling.
*(Originally derived from the application schema. **Confirmed accurate by the user 2026-08-03.** No longer an open item.)*

**Primary segment:** SMB. Single-vertical: 100% Amazon DSP operators.
**Segment sub-types in use:** ZL (802 of 872 non-test tenants), XL (68), Lite (2).
**Geography:** US (org currency USD, timezone America/New_York, Zoho org `org830066202`).

## CS team

**Size:** 3 people, but only about 1.5 effective account owners. Coverage is NOT split three ways.

- **John Goldman** (john@hera.app), COO. **Acts as the dedicated CSM for all accounts.** Also personally handles accounts needing hands-on attention, and owns identification of at-risk and potential-churn accounts. Primary escalation owner.
- **CSS 1**, hybrid, transitioning into a fuller CSM role. **Will be assigned his own book.** Compensation includes a bonus tied to retention and retention profit on that book. Escalates to John.
- **CSS 2**, hybrid between CEO personal assistant and reactive support. Primarily reactive, can do some proactive work. **Will not be assigned a book.** Functions as a detection layer: spots accounts and people worth flagging, then routes to John.

**Implication for skills:** do not distribute the book three ways. John covers the whole book. Portfolio output should assume one primary owner, one developing sub-owner with a carve-out book, and one detection-only contributor.

**Implication for the retention target:** because CSS 1's bonus is tied to retention of his book, GRR must be computable per book, and the addressable-versus-program-closure split has direct compensation consequences. **An Amazon DSP closing inside his book must not count against his bonus.**

**Reporting / second-tier escalation:** CEO, via the weekly management meeting.

## Book of business (as of 2026-07-30, from live DynamoDB, Paid invoices, verified after a full audit)

| Metric | Value |
|---|---|
| Active paying tenants | **248** (238 Bundle, 10 Premium) |
| **Customers** | **241** (7 run secondary sites as separate tenants) |
| Trials in flight | 67 on Trial status, plus 2 internal accounts to exclude (Hera Deliveries, AI Testing). **Roughly 3/4 are not prospects.** They are AMP partnership customers parked on Trial because rollup billing does not exist yet. Genuine funnel is ~17. See "The AMP cohort" in `csm/CLAUDE.md` |
| Lapsed trials | 54, **probably contaminated.** Some are likely AMP members who left AMP, not prospects who declined. Do not read as lost sales opportunity until split |
| **Customers not counted above** | ~50 AMP accounts are live customers excluded from the 241 because they are unbilled by arrangement. The real served-customer count is nearer 290 |
| Churned (lifetime) | 497 |
| Total tenant rows | 953 (81 test/temporary excluded, leaving 872) |
| **Total monthly revenue** | **$193,080** (last Paid invoice per account) |
| Reporting unit | **Monthly, never annualised.** Month-to-month billing with no contract, so annualising implies a commitment that does not exist |
| **Price** | **$9.00 per active associate per month, $0.30/day, billed one month in arrears** |
| Median customer | $759/mo. Average $801/mo |
| Range | $457/mo (p10) to $2,202/mo (largest). The largest customer pays about 3x the median |
| Median tenure | 40 months paid (p25 26, p75 56, max 64) |
| Billed active associates | 22,638 |
| Median active associates per account | 89 (p25 69, p75 112, p90 138, max 338) |
| Coverage | John carries all 241 customers. See CS team above: ~1.5 effective owners, not 3 |

**Structural fact:** the book is relatively flat. The largest customer pays about **3x** the median. Top 20 customers carry 16.0% of revenue, top 50 carry 33.9%. In most business-to-business software the largest account is 50 to 100x the median and the top decile carries 40 to 60% of revenue, so revenue tiering would still produce buckets that behave similarly here. **But this is not as flat as revisions 1 to 3 claimed (2.0x), so re-check it before applying the same logic in a new market.** Billing is $9 per active associate, so ARR tracks headcount almost exactly (r = 0.963).

## Primary value metric

**Work executed in Hera.** Set by the user on 2026-07-30, replacing "operational time saved" as the primary metric.

**Why it changed.** Time saved was the honest description of the benefit and an impossible thing to measure. Hera knows a roster was built. It cannot know whether that replaced 40 minutes of spreadsheet work or 5. Any hours figure would need a per-unit estimate that only a customer can supply, so the metric was not merely uninstrumented, it was uncomputable from product data.

**What replaces it:** counts of work that demonstrably happened in Hera instead of by hand. Rosters built, Messenger volume (one broadcast in place of texting each associate), counselings logged, automated coaching messages sent. `AuditLog` stays rejected: no date-range index, ~27,000 rows per account, too expensive.

**Time saved is not abandoned, it is reclassified.** It remains the benefit customers care about, gathered as **their words, not our arithmetic**. When a customer says Hera saves them six hours a week, quote them and attribute it. Never generate the figure, never multiply a count by an assumed number of minutes.

Detail and the overlap warning: `csm/CLAUDE.md`, "CS methodology."

## Top churn drivers (from 468 paid churns with `accountCanceledReason` populated)

| Reason | Count | % of paid churn | CS-addressable |
|---|---|---|---|
| DSP Closed | 181 | 38.7% | **No.** Customer left the Amazon DSP program |
| Didn't Fully Utilize or Find Value | 92 | 19.7% | **Yes. Largest addressable driver** |
| (blank) | 60 | 12.8% | Unknown |
| Cost Savings | 48 | 10.3% | Partly (value justification) |
| Switched to Competitor | 56 | 12.0% | Yes |
| Internal processes / build-your-own | 9 | 1.9% | Partly |
| Reduced routes / dropped DAs to 0 / site closure | 12 | 2.6% | No (contraction) |
| Stopped Using, No Explanation | 6 | 1.3% | Yes |

**Roughly 41% of churn is the Amazon DSP program churning, not Hera. Roughly 45% is addressable.**

Do not set a GRR target that treats DSP closure as a CS failure. It will send the team after unwinnable accounts. Track addressable churn separately from program churn.

**Named competitors (from loss data):** DSPworkplace (23 losses), LMDmax (17), Lokiteck (2), Manage my DSP (1), plus 13 unspecified.

**Churn timing:** median tenure at churn was 18 months (p10 5, p25 10). **29% of paid churn happened inside 12 months**, against a 40-month median for survivors. Accounts are lost early or kept for years. Concentrate intervention in year one.

**Lifetime figures:** 721 accounts have ever paid, 253 remain active, 468 churned (65% lifetime churn, of which ~41% is program closure).

## Retention baseline (June 2025 to June 2026)

| Measure | Result |
|---|---|
| **Addressable GRR** | **95.8%** |
| All-causes GRR | 86.3% |
| Program-closure drag | 9.8% (not a CS outcome) |
| Expansion inside surviving accounts | **+17.8%**, with no sales motion |

**Targets, set 2026-07-30, replacing the 90% addressable GRR target from setup:**

1. **Annual guardrail: addressable GRR at 96%.** A guardrail, not the performance target. The book sits 0.2 points under it today, which is deliberate.
2. **Monthly managed number: adoption risk plus stopped scorecards, 62 accounts and $52,512/mo.** Coverage-based for the first quarter (every account in the cohort gets a logged adoption conversation each month), switching to an outcome measure once exit-rate data exists.

**Never targeted, only reported:** all-causes GRR (41% of churn is Amazon closing the DSP) and expansion inside surviving accounts (+17.8%, tracks Amazon's hiring, not CS work). Surviving customers expand on their own because billing follows headcount.

**HeraAi is excluded from every metric, by user decision 2026-07-30.** The 25% attach target is cancelled. Do not track HeraAi adoption, attach rate, or whitespace anywhere, and do not reintroduce it on a later config pass. It is not a measure of customer success at Hera.

Full reasoning: `csm/CLAUDE.md`, "Retention targets."

## Health model

**Two independent axes, never a single band.** Revenue direction (associate count across closed invoices) answers how much they pay. A binary abandonment test (no staffed roster in 30 days and under 5 messages per associate) answers whether they stay. Product engagement was tested and does **not** predict revenue decline.

Current state, 248 tenants / 241 customers, in monthly revenue: healthy 131 ($107,656), stopped scorecards 35 ($28,268), **adoption risk 27 ($24,245)**, business contraction 31 ($22,185), **critical 5 ($3,832)**, watch 3, roster cleanups 10, not entitled to rostering 5, billing reconciliation 1.

Full detail: `~/.claude/plugins/config/claude-for-customer-success/csm/CLAUDE.md` and `/Users/johnjm/github/customer-success/analysis/cs-health-baseline-2026-07/findings.md`

## Outcome Catalog

catalog_path: ~/.claude/plugins/config/claude-for-customer-success/outcome-catalog.md
catalog_version: provisional-1.0
ratified_date: [PENDING, not yet ratified with the CEO]
generation_status: generated 2026-07-30

**16 outcomes across 6 operator jobs:** staff tomorrow's routes, survive the Amazon scorecard, coach defensibly, reach the whole team, keep the fleet legal, run the operation from one place.

**Provisional means inferred, not evidenced.** Built from the product schema, the per-tenant Amazon coaching thresholds, the health model, and the churn reason taxonomy. **No customer has confirmed any entry.** The `accountCanceledNotes` field turned out to be ~10 repeated internal labels rather than customer language, so the corpus was far weaker than expected.

**Validation runs through the 62 monthly adoption conversations.** Each one tests whether these outcomes match what the customer is actually chasing, and collects the attributed quotes the value metric depends on. Promote entries from `inferred` to `evidenced` with the customer's name attached. Ratify at v1.0 after a quarter.

**Do not use any entry in customer-facing material before ratification.**

Regenerate with `/csm:cold-start-interview --generate-outcome-catalog` after a major product release.
