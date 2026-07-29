# Tenant engagement and CS health scoring

The shared scorer behind the weekly CS health report and Part 4 (Section D) of the
daily production review. Read-only against production DynamoDB.

## Run it

```bash
export AWS_PROFILE=hera-readonly AWS_REGION=us-east-2
cd analysis/tenant-engagement
python3 three_signals.py --as-of 2026-07-29     # pull signals  -> data/signals-<date>.json
python3 classify.py      --as-of 2026-07-29     # classify      -> reports/<date>-cs-health.md
```

Add `--limit 20` to `three_signals.py` for a fast sample. If SSO has expired the
script exits with the `aws sso login --profile hera-readonly` instruction rather
than a traceback.

Takes a few minutes for the full book. Roughly 250,000 read request units, about
$0.03 at current on-demand pricing. Every table is `PAY_PER_REQUEST`, and reads
spread across 253 partition keys, so this cannot throttle the app.

## Why two axes

Engagement does not predict revenue direction. Measured in the July 2026 baseline:
6 of 15 declining accounts scored **above** the healthy average on engagement, the
highest-engagement account in the pilot was losing 15% of its associates, and the
lowest-scoring healthy account was growing 20%. A single blended health score hides
both failure modes.

- **Engagement** answers *will they stay at all*. Three signals, 14-day window,
  producing the four patterns from the daily-review skill.
- **Revenue** answers *how much will they pay*. Active-associate direction across
  the last four **closed** invoices, since billing is $9 per active associate.

The `bucket` field crosses the two and is the only field you need to act on.

## Buckets

| Bucket | Meaning | Action |
|---|---|---|
| `CRITICAL` | Revenue falling and engagement gone | Work first |
| `ADOPTION_RISK` | Paying, not declining, not using it | Adoption conversation, never a save play |
| `BILLING_RECONCILIATION` | Dark with zero active associates | Confirm or cancel. Do not sell |
| `CONTRACTION` | Losing associates but still engaged | Their business is shrinking. Forecast it, do not chase |
| `DATA_HYGIENE` | Associate drop is a bulk roster cleanup | Billing self-corrected. No action |
| `NOT_ENTITLED` | No rostering module | Score on coaching and scorecard only |
| `HEALTHY` | No flags | |

## Signals

| Signal | Source | Index | Note |
|---|---|---|---|
| `last_message_sent_by_user` | `Message` | `byGroupAndMessageType` | `begins_with` on the message type, `senderId` must be populated. A human typed it |
| `last_message_read` | `AuditLog` | `byTenantIDAndMutationName` | `CreateMessageReadStatus`. Range key is `mutationName`, so paginate fully and take the max |
| `last_scorecard` | `CompanyScoreCard` | `byTenantByYearWeek` | `yearWeek` is null on some rows, so take `max(createdAt)` |
| `last_staffed_roster` | `DailyRoster` + `Route` | `byGroupAndNotesDate`, `gsi-RouteDailyRoster` | A roster with at least one route assigned to an associate. Empty shells do not count |
| `active_staff` | `Staff` | `byGroupStatus` | Only `status = 'Active'` bills |
| `assoc_change` | `Invoice` | `byGroup` | `averageActiveDriverCount` across closed invoices |
| `under10_run` | `InvoiceLineItem` | `gsi-InvoiceInvoiceLineItems` | Daily `activeStaff`, consecutive recent days below 10 |
| `cleanup` | `StaffStatus` | `byGroup` | Bulk `Active` to `Inactive` transitions on one day |

## Field traps

All centralised in `lib_hera.py`. Each one produced a confidently wrong answer at
least once. Full history in `../cs-health-baseline-2026-07/findings.md` section 13.

- **`Invoice.status = 'Pending'`** is the in-progress month, still accruing.
  Comparing it against closed months makes every account look like it is shrinking.
  This alone produced a fake $193,000 book-wide decline.
- **`Tenant.averageMonthlyInvoiceTotal`** is a lifetime average, not current billing.
- **`StaffStatus`** uses `currentStatus` and `previousStatus`. There is no `status`
  field. Projecting `status` returns nothing and looks like "no data exists".
- **`DailyRoster.notesDate`** is the date a roster is built *for*, scheduled ahead,
  so a healthy account's newest value is in the future. Never compute "days since".
  A few tenants also carry values thousands of years out of range.
- **`User.lastLogin`** can hold the literal string `NOT_YET_LOGGED`, which sorts
  above real ISO timestamps because `N` > `2`.
- **Rostering entitlement**: tenants without `bundle` or `rostering` in
  `accountPremiumStatus` physically cannot roster. Flagging them for not rostering
  produced 6 false positives.
- **Empty roster shells are normal.** 133 of 253 tenants have at least one in a
  30-day window, so only the ratio is meaningful.
- **Multi-site tenants**: 7 customers appear as 14 tenants via `| STATION`
  suffixes. `parentAccountId` is never populated, so roll up by name.
- **`AuditLog.byGroupAndMutationName`** cannot order by date, because its range key
  *is* `mutationName`. Use `byTenantIDAndMutationName` with full pagination.

## Known limitations

- **Not seasonally adjusted.** Thresholds come from a July 2026 distribution. A
  summer decline cannot yet be separated from a seasonal trough.
- **No outcome log.** Nothing records what intervention was tried or whether it
  worked, so no threshold here has been calibrated against a real result.
- Cleanup detection is heuristic: 40% of transitions on one day with at least 8
  records. It will miss a cleanup spread over two days.

## Consumers

- `analysis/cs-health-weekly/skill/SKILL.md`, the weekly report skill
- `analysis/logrocket-error-investigation/skill/SKILL.md` Part 4, which defers to
  this scorer rather than reimplementing the classification
