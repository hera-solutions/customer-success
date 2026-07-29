---
name: cs-health-weekly
description: Weekly CS health and revenue-risk report for Hera. Scores every paying tenant on two independent axes, engagement (three-signal pattern plus rostering) and revenue direction (active-associate trend across closed invoices), then assigns one triage bucket per tenant. Produces the CRITICAL, ADOPTION_RISK, STRATEGIC_RISK and BILLING_RECONCILIATION work queues with dollar exposure, plus roster-cleanup and already-stopped-revenue callouts. Saves a dated markdown report to customer-success/analysis/tenant-engagement/reports/. Use when the user asks "run the weekly health report", "who is at risk", "which accounts need attention", "run CS scoring", "what is our revenue at risk", or when invoked by the scheduled routine. This is the authoritative CS health model; the daily review's Part 4 defers to it.
---

# CS Health Weekly

Score every paying tenant, produce the work queues, save a dated report.

Read-only against production DynamoDB. Never writes to Hera.

## Why two axes and not one health score

**Engagement does not predict revenue direction.** This was measured, not assumed. In
the July 2026 baseline pilot, 6 of 15 declining accounts scored *above* the healthy
average on engagement, the single most engaged account was losing 15% of its
associates, and the least engaged healthy account was growing 20%.

A blended score hides both failure modes: the deeply engaged account whose business
is shrinking, and the account that pays more every month while using nothing.

- **Engagement** answers *will they stay at all*.
- **Revenue direction** answers *how much will they pay*.

Full rationale and the rejected alternatives: `analysis/cs-health-baseline-2026-07/findings.md`.

## Hard requirements

- **SSO session.** `aws sts get-caller-identity --profile hera-readonly` must succeed.
  If it fails, tell the user to run `aws sso login --profile hera-readonly` and stop.
  The scripts exit with that instruction rather than a traceback.
- **Today's date** comes from the `currentDate` context, never `Date.now()`.
- **No RDS.** Everything runs on DynamoDB, which needs no VPN. `Invoice`,
  `InvoiceLineItem`, `StaffStatus`, `DailyRoster` and `Message` are not synced to the
  RDS mirror anyway, and the mirror has drifted silently before (HERA-8631).

## Run it

```bash
export AWS_PROFILE=hera-readonly AWS_REGION=us-east-2
cd /Users/johnjm/github/customer-success/analysis/tenant-engagement
python3 three_signals.py --as-of <YYYY-MM-DD>
python3 classify.py      --as-of <YYYY-MM-DD>
```

Step 1 takes a few minutes for the full book and writes `data/signals-<date>.json`.
Step 2 is instant, reads that cache, and writes
`reports/<date>-cs-health.md`. **If you only want to change thresholds or report
shape, re-run step 2 alone.** It costs nothing and hits no API.

Cost is roughly 250,000 read request units, about $0.03. Every table is
`PAY_PER_REQUEST` and reads spread across 250+ partition keys, so this cannot
throttle the production app.

## The buckets, and what to do with each

| Bucket | Meaning | Action |
|---|---|---|
| `CRITICAL` | Declining **and** disengaged | Work first, sorted by monthly revenue |
| `ADOPTION_RISK` | Paying, not declining, not using the core workflow | Adoption conversation. **Never a save play** |
| `BILLING_RECONCILIATION` | Dark with zero active associates | Confirm or cancel. Do not sell |
| `STRATEGIC_RISK` | Comms current, no scorecard in 60+ days | Ask what happened to their scorecard workflow. Do not oversell |
| `CONTRACTION` | Declining but still engaged | Their operation is shrinking. Forecast it, do not chase |
| `WATCH` | One soft signal only | No action, review next week |
| `DATA_HYGIENE` | Associate drop is a bulk roster cleanup | Billing self-corrected. No action |
| `NOT_ENTITLED` | No rostering module | Score on coaching and scorecard only |
| `HEALTHY` | No flags | |

**Disengaged means `BOTH_DARK` or roster-dark.** It does **not** mean `MSG_ONLY`.
MSG_ONLY is a scorecard-workflow gap while comms continue, which is why it has its
own `STRATEGIC_RISK` bucket. Conflating the two put accounts that rostered *that
morning* into CRITICAL and inflated the adoption list to 30% of ARR.

## Reading the report to the user

Lead with the triage table, then the CRITICAL list. Those are the only two things
that change what anyone does on Monday.

Then, in order of usefulness:

1. **Revenue that has already stopped.** Tenants under 10 active associates whose
   last closed invoice was over $100. Their next invoice is near zero. **Never
   present this as ARR at risk**, it is already gone, and saying otherwise
   overstates what a save could recover.
2. **STRATEGIC_RISK.** The scorecard workflow has left Hera. This whole band can
   leave together, so it is worth more attention than its bucket size suggests.
3. **ADOPTION_RISK.** Frame as expansion of usage, not rescue. These customers are
   growing and paying more. A save play here reads as confusing at best.
4. **DATA_HYGIENE.** Explicitly tell the user these are *not* problems, so the
   associate drop does not get mistaken for churn.
5. **Multi-site customers.** Secondary sites appear as separate tenants. Treat each
   group as one relationship and one conversation.

## Things that will make you wrong

Every one of these produced a confidently wrong answer at least once. They are
enforced in `lib_hera.py`; do not work around them.

- **Never use a `Pending` invoice for revenue.** It is the in-progress month, still
  accruing. Comparing it against closed months once produced a fake $193,000
  book-wide decline.
- **Never use `Tenant.averageMonthlyInvoiceTotal`.** It is a lifetime average.
- **Never read a declining associate count as churn without the cleanup check.**
  Customers control Inactive status and Hera reminds them twice a month to tidy up,
  so a drop is often a data correction. 13 of 30 declining accounts were cleanups.
- **Never flag a tenant for not rostering without checking entitlement.** Tenants on
  legacy module pricing without the rostering module physically cannot roster.
- **Never count empty rosters raw.** Most tenants have the odd empty roster; only
  the ratio is meaningful.
- **`StaffStatus` has no `status` field.** It is `currentStatus` and `previousStatus`.
- **`AuditLog.byGroupAndMutationName` cannot sort by date**, because its range key
  *is* `mutationName`. Use `byTenantIDAndMutationName` and paginate to the max.

## Caveats to state in every report

- **Not seasonally adjusted.** Thresholds come from a July 2026 distribution. A
  summer decline cannot yet be separated from a seasonal trough. Peak season is a
  known gap.
- **No outcome log.** Nothing records what intervention was tried or whether it
  worked, so no threshold has been calibrated against a real result.
- Monthly figures are the last **closed** invoice, so they lag by up to a month
  under arrears billing.

## After the report

Offer, do not do automatically:

1. Draft outreach for the CRITICAL list
2. Open Zoho tasks for CRITICAL and BILLING_RECONCILIATION
3. Compare against last week's report to surface movement between buckets
4. Investigate a specific tenant in depth

Escalation routing per bucket is **not yet configured**. Until it is, route CRITICAL
and BILLING_RECONCILIATION to John as a Zoho task, with the weekly management
meeting with Matthew as the second tier.
