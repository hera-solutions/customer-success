# What "actively using Hera" actually means

**Run 08-04-2026.** Scripts: `prevalence.py`, `model.py` (see `analysis/tenant-engagement/`). Data cached under `data/`, which is gitignored because it carries per-tenant customer detail.

## Why this exists

We needed a trigger for CS outreach that fires when a customer stops using the product. Three candidate definitions were tried and the first two were wrong.

| Candidate | Verdict |
|---|---|
| `Last_Active1` on the Zoho Deal | **Too loose.** Any mutation refreshes it, including a notification read receipt. Produced 18 tasks in 14 months |
| Days since a staffed roster | **Too narrow.** Punishes messaging-only and coaching-only customers. DBE Logistics has no rostering module at all |
| Last activity across all workflows | **Correct shape, and harder than expected.** See below |

## AuditLog: what it is

- **6,898,065 rows, 96.7 GB.** Never scan it.
- **TTL is 89 days**, measured directly. Rows older than that move to `AuditLogArchive`, which we do not need. So **every AuditLog figure means "in the last 90 days"**, which is the right window for a usage measure.
- **109 distinct `mutationName` values** across the 241 paying tenants. Median 31 per tenant, max 69.
- Walk distinct values cheaply using the `byGroupAndMutationName` index: `mutationName` is the RANGE key, so one 1-row query per distinct value beats scanning. `prevalence.py` does this for all 241 tenants in about a minute.

## The finding that matters most: AuditLog records human intent, not value

**AuditLog only captures human-initiated GraphQL mutations. Anything the system generates on the customer's behalf is invisible to it.**

The proof is DBE Logistics, inside the same 90-day window:

| Source | Result |
|---|---|
| AuditLog | **Zero** coaching mutations. 3 of 10 workflows touched |
| `Infraction` and `Kudo` tables | **995 infractions and 8,412 kudos created** |

DBE uploads Amazon scorecards, `CreateTextractJob` OCRs the PDF, and a backend process generates thousands of coaching records. No person clicks anything, so nothing is audited. On an AuditLog-only model DBE looked like one of the 14 least-engaged accounts in the book. **It is the opposite: one deliberate action a week produces 9,400 coaching records.**

**Consequence for any usage model:**

| Source | Answers | Blind to |
|---|---|---|
| **AuditLog**, 90 days | Did a **person** deliberately act | Anything generated on their behalf |
| **Source tables** | What records **exist** | Who caused them, and intent |

**Risk requires both.** An account is only genuinely inactive when a human has stopped acting *and* nothing is being produced. **Engagement requires the source tables**, because "you are getting no value from coaching" is about whether records exist, not who typed them.

## Verified workflow prevalence

Share of the 241 paying tenants with at least one human-initiated mutation in that workflow in 90 days. Excludes `UpdateUserNotification` and `CreateOptionsCustomListsStaff` by user decision 08-04-2026, both being system side-effects rather than deliberate acts.

| Prevalence | Workflow | Tier |
|---|---|---|
| 96.3% | Associate management | **CORE.** Absence is a risk signal |
| 93.8% | Messaging | **CORE** |
| 92.5% | Scorecard / OCR | **CORE** |
| 91.7% | Documents | **CORE** |
| 89.2% | Admin and config | **CORE** |
| 88.0% | Coaching and records | **CORE** |
| 87.6% | Rostering and routes | **CORE** |
| 81.7% | Fleet and devices | COMMON, supporting evidence |
| 34.9% | Compliance and HR | **OPTIONAL.** Engagement target, never a risk flag |
| 16.6% | Ops log and tasks | **OPTIONAL** |

**Prevalence is the weight, and it is not a judgment call.** This is the same rule the fleet upside tier already used: a signal firing on most customers means absence is exceptional and therefore triageable. A signal firing on a minority means absence is normal, so it is an expansion conversation instead.

**Associate management is the most universal activity in the book**, ahead of both rostering and messaging, and it is what drives billing.

### Breadth per account

| Workflows touched in 90 days | Accounts |
|---|---|
| 0 | 5 |
| 1 to 3 | 9 |
| 4 to 5 | 8 |
| 6 to 7 | 45 |
| 8 to 10 | 174 |

**Five accounts show nothing in either source** and are the only unambiguous result: Your Express Solutions ($702/mo), Infinite Delivery OPS, New Deal Logistics, Syndicate Logistics, Shandy Holdings.

The 1-to-3 group must **not** be treated as at-risk without checking the source tables. DBE sits in it.

## Traps found, all of which will produce wrong numbers

**1. Three naming conventions for the same operations.** 97 PascalCase, 7 camelCase, 5 SCREAMING_SNAKE, with nine confirmed duplicate pairs. Filtering one spelling silently misses the others.

| Same operation, different spellings |
|---|
| `UpdateStaff` 96% / `updateAssociate` 11% / `updateStaff` 8% |
| `updateCounseling` 80% / `UpdateCounseling` 76% |
| `CreateDocument` 76% / `createDocument` 54% |
| `UpdateTenant` 65% / `UPDATE_TENANT` 3% |
| `UPDATE_DEVICE` 23% / `UpdateDevice` 1% |
| `CREATE_DEVICE` 18% / `CreateDevice` 2% |
| `DELETE_DEVICE` 4% / `DeleteDevice` 1% |
| `CreateValueListItem` 25% / `CREATE_VALUE_LIST_ITEM` 3% |
| `CreateMessagePreferencesHistory` 30% / `createMessagePreferenceHistory` 11% |

Normalise on lowercase, strip non-letters, and map `associate` to `staff` before comparing.

**2. `Select="COUNT"` does not paginate.** A raw query with `Select="COUNT"` returns the count for **one page**, silently. It reported 2,509 infractions for DBE. Paginated properly it is **26,464**. Use `lib_hera.query_count`, which paginates, and never a bare `ddb.query(Select="COUNT")`.

**3. Falsy zero.** `days_since(...) or 999` turns a legitimate 0 into 999. This misread 179 accounts that rostered *today* as roster-dark and produced a 91% dark rate against the real 16%. Use `is not None`.

**4. `AuditLog` misses message sends.** No `CreateMessage` appears for any account, only read receipts and pending-message operations. Message activity must come from the `Message` table.

**5. `CreateDailyRoster` is only 11.6% while `UpdateDailyRoster` is 65.6%.** Rosters are largely not created through the audited path. Do not read low `CreateDailyRoster` as low rostering.

## Corrections to earlier claims

**`UpdateTenant` is 65%, not "one account only."** An earlier four-account sample suggested it was rare and therefore an adoption-depth marker. Two thirds of customers change their own settings. **It is not a depth signal.**

**Fleet reconciles with the July baseline; both numbers were right.** 81.7% touch a fleet mutation, meaning they keep the vehicle list current. 71% logged no odometer in 30 days and no maintenance in 90 days. Different measures. The engagement pitch is "you maintain your van list and never log maintenance," which is sharper than "you do not use fleet."

## Verification performed

Per the standing three-check rule in the root `CLAUDE.md`:

| Check | Result |
|---|---|
| **Input** | Established the TTL empirically at 89 days before interpreting any prevalence figure |
| **Cross-source** | `CreateMessageReadStatus` = 203 accounts by this walk, 203 by `three_signals.py`'s independent query on a different index. Delta zero |
| **Follow-through** | The 241-account run reproduces a 4-account sample exactly (28/9/30/20). No account hit the 200-mutation walk cap, max was 69 |

The DBE contradiction was found by cross-checking this model against a claim already in the CS config, which is the check working as intended.

## Next step, not yet built

Compute **last meaningful activity per account from the source tables**, not AuditLog, covering all nine signals, then derive the outreach trigger threshold from that distribution. AuditLog breadth becomes the second corroborating axis.

Do not set a trigger threshold before that distribution exists. The 7-day figure floated earlier came from the roster distribution alone and does not survive this analysis.
