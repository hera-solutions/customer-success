# Nobody can tell who to call, and churn is not an early-life problem

**Run 08-05-2026, in answer to "is there anything we're missing?" Two checks, both of which change what to do next.**

---

## 1. The task says "call the owner." Zoho cannot tell you who that is.

**This blocks day one of the ladder and it is not a data-quality problem, it is a missing join.**

Zoho `Contacts` for the 15 urgent accounts returned over 100 rows and was still truncated. Per account:

- **Delivering Delights: ~25 contacts.** Names like `brayden.redden.dede@gmail.com`, `keyala.foster.dede@gmail.com`, `jamika.odelldede@gmail.com`
- **TPE Logistics: ~20 contacts**, `@tpelsi.com` and `@tpeldsp.com`
- **GNC Transportation: ~10**

**These are overwhelmingly drivers and dispatchers.** There is no role field populated, no primary-contact flag. Whoever works the task has to guess, and **guessing wrong means calling a driver, which is explicitly forbidden.**

Several also carry a `Support Administrator` contact on `sysadmin-<group>@herasolution.app`, which is a system account, not a person.

### Dynamo can answer it, and does so completely

`Tenant.ownerUserId` resolves through the `User` table. **15 of 15 urgent accounts returned a named owner with an email:**

| Account | Owner | Email |
|---|---|---|
| Leary Logistics | Dan Leary | `dan@learylogistics.com` |
| Tala Logistics | Beckie Rich | `beckie@talalogistics.com` |
| TPE Logistics | Tyron Woodard | `tyronwoodard@yahoo.com` |
| Derby Deliveries | Michael Palmieri | `palms0424@aol.com` |
| Probyn Inc | Rotimi Adeshina | `operations@probyninc.com` |
| GNC Transportation | Kendra Britt | `kbrittamzl@gmail.com` |
| Next Phase Logistics | Eric Montalvo | `eric@nplogistics.org` |
| Divine Package | Stephen Afolabi | `admin@divinepackage.org` |
| NAFE LLC | Natalia Nash | `natalia.nash@nafelogistics.com` |
| Upside Delivers | Brian Geraghty | `brian@upsidedelivers.com` |
| Pazzy Logistics | Mark Passerotti | `markpasserotti@aol.com` |
| Orad Logistics | Sadiq Ali | `sadiqyrm@gmail.com` |
| Cargo To You | Tristan Courtney | `tcourtcargo@gmail.com` |
| Delivering Delights | Corinne Anderson | `corinne.anderson.dede@gmail.com` |
| GNC Transportation \| TKU | Brenda Ramirez | `brenda.gnct+tku@gmail.com` |

**But Dynamo holds no phone number.** `User.phoneNumber` was empty on all 15.

### The fix, which is not built

**Dynamo names the owner. Zoho has the phone. Match on email.**

Spot-checked against the Zoho pull, the join lands a phone number for roughly 10 of 15:

| Account | Matched | Phone |
|---|---|---|
| Leary Logistics | Dan Leary | `+15162654424` |
| Tala Logistics | Beckie Rich | `+15205763909` |
| TPE Logistics | Tyron Woodard | `+19129771129` |
| Derby Deliveries | Michael Palmieri | `+17189385854` |
| Probyn Inc | Rotimi Adeshina | `9192154308` |
| GNC Transportation | Kendra Britt | `+16615991082` |
| Divine Package | Stephen Afolabi | `+16083208259` |
| Delivering Delights | Corinne Anderson | `+16173141118` |
| Next Phase Logistics | Eric Montalvo | **no phone in Zoho** |
| Cargo To You | **no match.** Zoho has James Courtney, Dynamo says Tristan Courtney | |

**Put the owner name, email and phone on every task.** The pre-call brief currently says everything about the account and nothing about who to ring.

### One caveat before trusting `ownerUserId` blindly

**Delivering Delights' owner reads `corinne.anderson.dede@gmail.com`, which matches the pattern of every driver email on that account.** Compare Dan Leary at `learylogistics.com`, who is obviously the principal.

So `ownerUserId` may point at whoever administers the Hera account rather than the business owner. **Verify it against the Zoho contact before using it as "the owner" in conversation**, and never open a call by assuming the person named is the principal.

---

## 2. Churn is not an early-life problem, so onboarding instrumentation can wait

Tenure at churn, all 279 churned tenants holding both a `createdAt` and a `firstChurnedDateTime`:

| Tenure at churn | Count | Share |
|---|---|---|
| 0 to 90 days | 6 | **2.2%** |
| 91 to 180 days | 23 | 8.2% |
| 181 to 365 days | 31 | 11.1% |
| 1 to 2 years | 60 | 21.5% |
| **2 years or more** | **159** | **57.0%** |

**Only 2.2% churn inside the first 90 days. 57% churn after two years or more.**

**This validates aiming the whole motion at mature accounts**, and it de-prioritises the largest remaining configuration gap: `onboarding` has no config at all, and on this evidence that is not where the losses are.

**Caveats.** `Tenant.createdAt` is when the record was created, which for any migrated account is not the true start date. Trials that never converted may not carry `Churned` status and so would be absent entirely. The direction is strong enough to act on; the exact percentages are not.

---

## What this leaves as the ranked gaps

| | Gap | Why it matters |
|---|---|---|
| **1** | **Owner name and phone are not on the task** | The ladder cannot start. Fix is a join, not new data |
| **2** | **Messaging drop-off is unmeasured** | Message is the strongest signal at 6.8 lift and has the exact blind spot just fixed for rostering |
| **3** | **VPL fulfilment ratio is unmeasured** | The only driver-side signal that exists. Requests weigh 1.3, responses 4.5, and the gap between them is the information |
| **4** | **The 30-day cooldown, before any writer ships** | Without it, tasks regenerate every morning |
| 5 | **Support tickets are absent from the model** | Intercom is connected. Five unresolved tickets is a churn risk no usage signal catches, and the only place customers complain in their own words |
| 6 | **Seasonality will break the new detectors** | Amazon peak runs Nov-Dec, then January collapses. A 60-day baseline would read January as the whole book falling off a cliff. **Backtest against last January before Q4** |
| 7 | **No holdout group** | Coverage is the Q1 target, but with no control we cannot tell whether any of this changed retention |
| 8 | The 35 stopped-scorecard accounts, $28,268/mo | That cohort was superseded by the heartbeat model and never re-homed |
