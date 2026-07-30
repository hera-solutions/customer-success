# Open questions blocking the CS build

Canonical list. **The IDs are stable, so cite them instead of re-lettering.** Earlier
sessions used ad-hoc numbering that existed only in chat and did not survive; that is
what this file fixes.

Last updated 2026-07-30. Source for the numbers is
[`tenant-engagement/reports/2026-07-30-cs-health.md`](tenant-engagement/reports/) and
[`cs-health-baseline-2026-07/findings.md`](cs-health-baseline-2026-07/findings.md).

Status values: **OPEN**, **ANSWERED**, **BLOCKED** (waiting on someone else), or
**PAUSED** (deliberately deferred, with the reason).

---

## A. Config fields, answerable by John

These map to the remaining `[NOT SET]` markers in the plugin config: 12 markers across
8 lines, plus A3, which is not a `[NOT SET]` marker but a target the config explicitly
flags as already exceeded and needing replacement. Nothing else blocks the CSM plugin
from being fully configured.

| ID | Question | Status | Why it matters |
|---|---|---|---|
| A1 | Escalation response times per tier. Hours or days on each hop from Zoho task to the weekly management meeting | OPEN | Now answerable because the queues are small: 5 CRITICAL, 27 ADOPTION_RISK, 35 STRATEGIC_RISK, 19 empty-shell, 17 under-10 |
| A2 | Who owns each bucket, given roughly 1.5 effective owners across three people | OPEN | Nine buckets exist and the config still routes only At Risk and Critical to John. Nobody owns the empty-shell list. ADOPTION_RISK plausibly belongs with a CSS as an adoption conversation, not with John as a save |
| A3 | Retention target to hold | OPEN | The 90% addressable GRR target set on 2026-07-28 **is already exceeded** at 95.8%, so it is meaningless. Candidates offered, none chosen: 96 to 97% addressable, a target on all-causes GRR (86.3%), or a target on the unworked trial funnel. Until one is picked, no skill can say whether a month was good |
| A4 | Where a qualified expansion signal routes, and how | OPEN | There is no AE. Fleet upside alone identifies $131,156/mo of untapped value with nowhere to send it |
| A5 | Where a contract or legal question routes | OPEN | Low frequency, but the escalation matrix has a hole |
| A6 | QBR format, if QBRs run at all | OPEN | At 241 customers per 1.5 people, month-to-month with no renewal event, standing per-account QBRs may not be viable. A decision not to run them is a valid answer and unblocks three skills |
| A7 | Success plan format | OPEN | Same viability question as A6 |
| A8 | Renewal conversation style | OPEN | **Recommend deleting the field.** Hera is month-to-month with no contract, so there is no renewal event to prepare for. Every renewal-shaped skill needs rewiring to a monthly retention motion or disabling |
| A9 | Peak season and seasonality | OPEN | **The single input that could move existing numbers.** Every threshold in the model comes from a mid-summer window, so a July decline cannot currently be separated from a seasonal trough. Amazon peak is presumably November and December, which should change how a December associate drop is read |

---

## B. Needs the CEO conversation

Billing and pricing decisions that are not John's to make alone.

| ID | Question | Status | Exposure |
|---|---|---|---|
| B1 | Three unexplained billing accounts. Philosophe LLC and Integrated Logistics Solutions each bill $0 with 70+ associates and no discount label. Crucial Mile has `accountPremiumStatus: ['None']` and 175 associates | BLOCKED | About $1,400/mo |
| B2 | Seven comped accounts beyond MBB, which is intentional and earns it through internal support | BLOCKED | Unquantified |
| B3 | Legacy module pricing migration. Nine customers on $5 to $7 rather than $9 | BLOCKED | "Too expensive" already cost $6,614/mo this year, so sequence carefully |
| B4 | Whether anyone works the trial funnel | BLOCKED | 67 trials worth $59,832/mo, currently nobody's job. Competes directly for attention with the 67 at-risk paying customers |

---

## C. Urgent, not a measurement question

| ID | Item | Status | Exposure |
|---|---|---|---|
| C1 | **JDW Logistics has had its last three invoices written off** (April, May, June). Largest customer at 338 associates, healthy, growing, using the product daily. PacTrack has two consecutive `Payment Error` months, Pure Logistics one | OPEN | **$4,449/mo delivered and not collected.** Nobody appears to have noticed |

---

## D. Measurable, needs a go-ahead

Each is a bounded piece of analysis against data already reachable.

| ID | Question | Status | Notes |
|---|---|---|---|
| D1 | Phantom billing exposure: how many currently-Active associates across the book have not been on a route in months | OPEN | This is what a customer would discover on their own. Measurable against `Route` |
| D2 | The unnamed competitor: 12 customers, $8,533/mo, recorded only as "Other" | OPEN | The answer is probably in the 312 populated `accountCanceledNotes` records |
| D3 | Associate decline versus Amazon route cuts | OPEN | Separates unfixable viability from an operational problem Hera's coaching tools address. Directly relevant to how CONTRACTION is framed |
| D4 | Support signal from Intercom, which holds conversations and sentiment per company | OPEN | Never pulled. The MCP connector is available |
| D5 | Onboarding funnel: where new customers stall before first value | OPEN | 29% of paid churn happens inside 12 months, which is the strongest argument for configuring the `onboarding` plugin |
| D6 | Is $9 above or below market? | OPEN | Competitor switching is $17,525/mo and "too expensive" $6,614/mo, but DSPworkplace and LMDmax pricing is unknown. Determines whether this is a pricing problem or a value-communication problem |

---

## E. Other plugins

| ID | Item | Status | Notes |
|---|---|---|---|
| E1 | `cs-ops` plugin unconfigured | OPEN | Needs three answers and is effectively answerable now from work already done |
| E2 | `onboarding` plugin unconfigured | OPEN | Needs its own interview. Stronger case than E1 because of D5 |

---

## F. Paused by decision

Recorded so they are not rediscovered as gaps.

| ID | Item | Paused because | Revisit when |
|---|---|---|---|
| F1 | Inventory management usage as a health signal | Lives in the Athena (Amplify Gen 2) app with no table in this DynamoDB account, so usage is not measurable. The entitlement flags do not substitute: `featureEnabledInventoryManagement` and `featureAccessInventoryManagement` are both `true` on 949 of 954 tenant rows including long-churned ones, making them a global default rather than a purchase record | RDS access or the Athena API becomes available |
| F2 | Document signing usage as a health signal | Same Athena problem, and worse: there is no field on `Tenant` at all. Too new | Same as F1 |
| F3 | Fleet as a **scored** signal | 70% of entitled tenants use no fleet feature, so scoring it would flag most of the book and tell you nothing about which accounts are at risk. Shipped as upside-only on 2026-07-30 | A majority are using it, so that absence becomes the exception rather than the rule |
| F4 | Associates-to-routes ratio | Cannot distinguish part-timers from incomplete route entry. The two healthiest large accounts sit at 5.4x and 5.5x while Whiterecon shows 23x from missing data | Route entry completeness can be verified independently |
| F5 | RDS / Aurora MySQL mirror as a data source | VPN-only and not all tables are synced from DynamoDB | A hybrid approach is worth the setup cost, most likely driven by F1 and F2 |

---

## G. Structural gap, no owner

| ID | Item | Status | Notes |
|---|---|---|---|
| G1 | **No intervention outcome log exists** | OPEN | Nothing records what was tried on an account or whether it worked, so no threshold in the health model has been calibrated against a real result. Every number in it is informed judgement. Six months of logging changes that. This is the highest-leverage unglamorous thing on the list |
