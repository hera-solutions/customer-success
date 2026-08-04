# CS execution list, reconciled 2026-08-03

Every item below was verified against live DynamoDB and Stripe on 2026-08-03, not carried forward from an earlier list. Counts move: re-verify before acting if more than a day old.

**Ownership note.** Matthew Goldman is CEO, and per the July baseline he (or Liz) marks accounts churned manually. Every "mark churned" item below is therefore a request to Matthew, not something CS can execute.

---

## 1. Stop the meter on JDW. Only real accrual in the list.

| Account | Status | Active staff | August |
|---|---|---|---|
| JDW Logistics | **Active - Bundle** | **338** | Pending, accruing |

Four months uncollected, $10,867. Accruing **$101.40 a day**. Marking the tenant Churned is what stops it: proven by Wilx, which is Churned with 126 active associates and generated no August invoice.

**Owner: Matthew. One field.**

## 2. Five accounts to close for accuracy, not for money

**Correction to what I told you earlier.** I said these would bill again for "roughly $3,100 a month." **That was wrong.** They have zero or one active associate, so they bill about a dollar between them. Essentially all of the $3,100 was JDW.

| Account | Status | Active staff | August invoice |
|---|---|---|---|
| Globalteq Logistics | Active - Bundle | 0 | $0 |
| Focus Logistics | Active - Bundle | 0 | $0 |
| Merica Delivery Service | Active - Bundle | 1 | $1 |
| Envizion Logistics | Active - Bundle | 1 | $0 |
| ~~SkyHook 2~~ | **Churned already** | 0 | done |

The reason to close them is that they inflate the customer count of 241 and sit in health bands they no longer belong in. No financial urgency.

**Owner: Matthew. Four fields.**

## 3. Two phone calls, not three

| Account | Status | Active staff | Owed | Decline reason |
|---|---|---|---|---|
| TriPeaks Logistics | Active, accruing | 83 | $577 | insufficient_funds, twice |
| Kincade Delivery Solutions | Active, accruing | 47 | $440 | insufficient_funds |
| ~~Pure Logistics USA~~ | **Churned** | 95 | $846 | moot as a call, now a collections matter |

Both remaining cards are valid and in date with no money behind them. Phone call about the business, not a payment link. **Owner: John, next business day per the configured SLA.**

## 4. $2,257 of debt has gone invisible

**This is the finding that matters most in this list.**

Marking an account Churned removes it from the paying book, from the health report, and from every list CS looks at. **It does not clear what they owe.**

| Account | Status | Still owed |
|---|---|---|
| PacTrack, Inc | Churned | **$1,411** (July $711 plus an earlier $699.68) |
| Pure Logistics USA | Churned | **$846** (July, insufficient funds) |

Both dropped out of the book on 3 August. Neither will appear in any CS report again. **PacTrack's card was refused at least six times by the issuer, not for lack of funds, so it was probably collectible with a different payment method and nobody asked.**

Wilx is the counter-example and the good case: churned, and their final invoice of $849 was **Paid**.

**Needs a decision from Matthew: chase or write off. Either is fine. Silence means it is written off by accident.**

## 5. Three 100% discounts still running in August

| Account | Active staff | Reason recorded | Monthly at list rate |
|---|---|---|---|
| **Outlaw Logistics** | **195** | Customer Service | **~$1,755** |
| CV Delivery Service | 115 | Customer Service | ~$1,035 |
| Spears Enterprises | 111 | **Non Usage** | ~$999 |

Plus MBB x2 (Internal, deliberate) and Straightaway (Overpayment being worked off).

**Spears is the one to look at.** 111 active associates, credited 100% because they were not using the product. That is the exact profile that just churned: Clark Courier Service left on "Cost Savings" after 661 days without a roster while paying $1,471 a month. Spears has the same shape and is now paying nothing, so the pricing objection has been removed and the adoption problem has not been touched.

Crucial Mile has since churned. Red Stick already had.

## 6. Supreme Delivery DHO3 is effectively gone

The escalation I flagged as the one live item on 30 July, Active Subscriber on Bundle, full at-risk ladder fired in June, never actioned.

**It now has 1 active associate and is billing zero.**

Nothing to save. Worth recording the reason properly, because this is the clearest example available of an unactioned escalation running to completion.

## 7. The AMP dark accounts are real operating businesses

Ten AMP members produce no revenue because they are not using Hera. Between them they carry **807 active associates.**

| Account | Active staff | Days dark |
|---|---|---|
| MKL Logistics & Transportation | **170** | 106 |
| Gamma Ray Express | **110** | never recorded |
| Deal Logistics | 104 | never recorded |
| Swift Pace Logistics | 87 | 152 |
| Miracle Mile DSP | 81 | 152 |
| AMLO Logistics | 73 | 146 |
| Gold Link Logistics | 72 | never recorded |
| Sparkle Logistics | 67 | 133 |
| Lumana | 43 | never recorded |

**At Hera's list rate of $9 per associate that would be roughly $7,263 a month. Treat that as an upper bound, not a figure to quote: the AMP per-member rate is not confirmed and may not be $9.** `[estimate, rate unconfirmed]`

MKL has 170 drivers and has not touched Hera in over three months. Gamma Ray has 110 and never started.

## 8. Deep roster-dark, still paying, no action taken yet

| Account | Active staff | Days since a staffed roster |
|---|---|---|
| DC1 Transport | 137 | **861** |
| Frontline Logistics | 90 | **559** |
| Sinaro Logistics | 151 | **477** |

Same shape as Clark Courier at 661 days, which churned on Cost Savings. These are the top of the validated roster-dark list. See `findings-roster-dark-validation.md`.

---

## Data trap found during this reconciliation

**Invoice IDs are not reliably prefixed with the usage month.** Most read `2026-08...`, but Deliver2U's latest is `3cfba4d...`. Parse the usage month from `InvoiceLineItem.date` or from `year#month`, never from a string slice of the id.
