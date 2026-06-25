# Intercom Billing Tickets Snapshot

A point-in-time review of every Intercom conversation that touched billing in some form. Pulled 2026-05-13.

This is not a live view. It was built by combining: every conversation routed to the **Billing/Cancellations** team in Intercom (team id `8163722`), plus keyword searches for "billing", "invoice", "refund", "charged", "credit card", "credit", "Stripe", "payment", "overcharged", "scorecard", and "cancel" across conversation bodies and subjects.

## Headline numbers

| Bucket | Count |
| --- | --- |
| Routed to **Billing/Cancellations** team | 51 |
| Additional billing-adjacent tickets found via keyword search | ~13 |
| **Estimated total touching billing in some way** | ~64 |

Of the 51 in the Billing/Cancellations queue, **most carry the `Billing Issue` ticket type** (the credit-card emoji 💳). A handful are typed `General` or have no ticket type. The user's note holds: many but not all billing tickets are typed `Billing Issue`.

## Quick category breakdown

| Category | Notes |
| --- | --- |
| **Account cancellations** | The biggest bucket. Customers leaving the platform (often because they exited Amazon DSP) and asking us to stop billing. |
| **Active driver / overcharge disputes** | Customers realizing they were billed for Inactive associates. The Straightaway Delivery case is the clearest example. |
| **Invoice questions or records** | Customers asking for past invoices (for taxes), reporting incorrect addresses on invoices, or forwarding their monthly invoice with a question. |
| **Failed payments (Hera-initiated outreach)** | Tom-led outreach to customers whose May 2025 charge failed. Batch of 7+ tickets on 2025-06-03. |
| **Pricing inquiries from prospects** | Returning leads asking about cost or whether services chargeback to an insurance program (DelivRE). |

## Notable specific cases

These are the ones worth flagging for context the next time something similar comes in.

### Straightaway Delivery — overcharge dispute (Erica Stone)
- **Conversation:** [215470627810375](https://app.intercom.com/a/apps/baat8a8r/conversations/215470627810375) (2025-09-02) "Active Employee Charges"
- **Follow-up:** [215470643939597](https://app.intercom.com/a/apps/baat8a8r/conversations/215470643939597) (2025-09-03) "Let's Schedule a Call to Review"
- **What happened:** Customer thought uploading their weekly scorecard would auto-update Associate statuses. It didn't. They paid for inactive employees for months. Matthew had spoken with Charity at the company back in April flagging this, but it wasn't fixed.
- **Outcome:** Matthew committed to making it right and reviewing the historical amounts.
- **Pattern:** Classic inflated-bill case — customers assume statuses update automatically from upstream data. They don't. The credit process in `billing-overview.md` exists exactly for this.

### ICS Delivery Solutions — incorrect address on invoice (Justin Woods)
- **Conversation:** [215469257574691](https://app.intercom.com/a/apps/baat8a8r/conversations/215469257574691) (2025-06-02)
- **What happened:** Address on the May 2025 invoice was the station address, not their billing address.
- **Outcome:** Per ticket description, we noted an upcoming change to remove the address field from invoices entirely.

### Go Ground Xpress — winddown / final invoice (Kym & Ric Ramsey)
- **Conversation:** [215471093061265](https://app.intercom.com/a/apps/baat8a8r/conversations/215471093061265) (2025-10-01) "Fwd: Hera: Invoice for September 2025"
- **Follow-up:** [215471631353549](https://app.intercom.com/a/apps/baat8a8r/conversations/215471631353549) (2025-11-05)
- **What happened:** Customer winding down operations, wanted confirmation that September was their last billable month and that they'd move to "free mode" with continued data access.
- **Pattern:** Worth confirming we have a written cancellation / free-mode acknowledgment workflow so this doesn't get fuzzy.

### Brian Higginbotham — historical invoices for taxes
- **Conversation:** [215470203479868](https://app.intercom.com/a/apps/baat8a8r/conversations/215470203479868) (2025-08-06)
- **What happened:** Asked how to pull prior invoices for tax purposes.
- **Pattern:** Recurring need — customers don't have an obvious self-service way to retrieve past invoices.

### May 2025 failed-payment batch
- **Conversations:** 215469273006661, 215469272786282, 215469272923313, 215469272978986, 215469272755605, 215469272773517, 215469272646526 (all 2025-06-03, subject "May Failed Payment")
- **What happened:** Hera-initiated outreach to multiple customers whose May charges failed, asking them to re-enter their card.
- **Pattern:** This is the manual stopgap referenced in `billing-overview.md`. When the official Unpaid – Grace Period feature ships, this batch outreach should mostly go away.

### Jeffrey Moore / DelivRE — captive insurance chargeback (prospect)
- **Conversation:** [215474036490837](https://app.intercom.com/a/apps/baat8a8r/conversations/215474036490837) (2026-03-22)
- **What happened:** Returning customer asked whether his cost is paid by the DelivRE captive insurance, not him directly.
- **Pattern:** Confirm our process for handling captive-funded customers so the right Stripe charge target is set up day-one.

## Full list — Billing/Cancellations team queue (51)

Date is conversation creation date. Many of the queue entries have blank subjects, which usually means an in-app chat rather than an email thread.

| Created | Conversation | Subject | Company | Ticket type |
| --- | --- | --- | --- | --- |
| 2026-04-28 | 215474101521882 | — | Saisha Logistics Inc | Billing Issue |
| 2026-04-16 | 215473936791773 | — | First Touch Logistics | Billing Issue |
| 2026-04-10 | 215473860448384 | — | Fast Apple Logistics | Billing Issue |
| 2026-04-08 | 215473817689887 | Cancellation | Aurimas Delivery | Billing Issue |
| 2026-04-02 | 215473755105503 | — | — | none |
| 2026-04-01 | 215473735449516 | — | AIX Transport LLC | Billing Issue |
| 2026-03-31 | 215473723950570 | — | NHBlacklabs Delivery | Billing Issue |
| 2026-02-27 | 215473285948362 | Service Cancellation | RBJO Logistics | Billing Issue |
| 2026-02-09 | 215473027413554 | Fwd: Cancel subscription | Hamlett Logistics | Billing Issue |
| 2026-02-05 | 215472982750427 | — | Red Stick Logistics & Transportation | Billing Issue |
| 2026-02-04 | 215472960473415 | — | H2 (H-Squared) Logistics LLC | Billing Issue |
| 2026-01-30 | 215472884942145 | — | Motaur Express | Billing Issue |
| 2026-01-19 | 215472740815903 | — | Twenty3 Logistics | Billing Issue |
| 2026-01-11 | 215472628093297 | Re: Re: Hera Solutions \| Ready To Discover the Difference? | Agile Logistics LLC | Billing Issue |
| 2026-01-08 | 215472600005820 | Cancellation Request – Both Bradwood Sites | — | Billing Issue |
| 2026-01-02 | 215472511537866 | Cancellation - Bluebox Logistics LLC | Bluebox Logistics LLC | Billing Issue |
| 2026-01-02 | 215472510721806 | Cancelation | — | Billing Issue |
| 2025-12-13 | 215472252341124 | — | Rowan Logistics LLC | Billing Issue |
| 2025-12-10 | 215472207445791 | — | Prime Pace Logistics LLC | Billing Issue |
| 2025-12-02 | 215472098347741 | Re: FW: Hera: Invoice for November 2025 | Spot On Delivery, Inc. | Billing Issue |
| 2025-12-01 | 215472063550712 | — | Alston Transportation LLC | Billing Issue |
| 2025-11-15 | 215471784532553 | Discontinue Trial at Final Mile Deliverables (FINL) | Final Mile Deliverables | Billing Issue |
| 2025-11-06 | 215471635165955 | Subscription Cancellation | Level Up Logistics LLC | Billing Issue |
| 2025-11-05 | 215471620490922 | EJBS Logistics | — | Billing Issue |
| 2025-11-01 | 215471563743131 | — | Delco Deadline Deliveries, LLC | Billing Issue |
| 2025-10-28 | 215471496736108 | — | — | none |
| 2025-10-22 | 215471411895081 | — | ICS Delivery Solutions | Billing Issue |
| 2025-10-14 | 215471296522126 | — | Meraki Logistix | Billing Issue |
| 2025-10-11 | 215471252857354 | — | Cypri Logistics LLC | Billing Issue |
| 2025-10-02 | 215471106511175 | Cancellation | AJ3 Industries | Billing Issue |
| 2025-09-30 | 215471077431575 | — | M and S Enterprise LLC | Billing Issue |
| 2025-09-26 | 215471020199420 | — | — | none |
| 2025-09-18 | 215470894187486 | — | — | none |
| 2025-09-15 | 215470838432490 | Cancel account | Pack-Em LLC | Billing Issue |
| 2025-09-15 | 215470835333338 | — | TruJacodi Delivery Express | Billing Issue |
| 2025-09-13 | 215470801868310 | Cancel | — (EPIC Lightning Fast) | Billing Issue |
| 2025-09-05 | 215470684801704 | — | Advanced Delivery Service \| NJ DJZ5 | Billing Issue |
| 2025-09-03 | 215470643939597 | Let's Schedule a Call to Review | — (Straightaway) | none |
| 2025-09-02 | 215470627810375 | Active Employee Charges | — (Straightaway) | none |
| 2025-08-28 | 215470552721473 | — | ACE Premier Logistics | Billing Issue |
| 2025-08-24 | 215470473346072 | — | — | none |
| 2025-08-16 | 215470351281362 | — | Aylo Logistics, LLC | Billing Issue |
| 2025-07-10 | 215469804410828 | Contract | — | Billing Issue |
| 2025-07-01 | 215469678940288 | Re: Your Hera account's been quiet—need assistance? | SJ Logistics | Billing Issue |
| 2025-06-25 | 215469587850200 | Cancel Company Subscription | Powerhouse Logistics Services | Billing Issue |
| 2025-06-25 | 215469587822078 | — | Powerhouse Logistics Services | Billing Issue |
| 2025-06-13 | 215469421932181 | — | Agora Logistics | Billing Issue |
| 2025-06-11 | 215469387559415 | Re: Hera \| Update Call | — | none |
| 2025-06-05 | 215469315010297 | Cancel subscription. PRIA logistics (PRAL) | PRIA Logistics | Billing Issue |
| 2025-05-20 | 215469071789542 | — | Apcore Logistics LLC \| WWG1 | Billing Issue |
| 2025-05-19 | 215469049972416 | — | Your Express Solutions LLC | Billing Issue |
| 2025-03-25 | 24 (legacy id) | Request to Discontinue HERA Service - MTSL DLN8 | — | General |

## Additional billing-adjacent tickets found via keyword search (not routed to Billing/Cancellations)

| Created | Conversation | Subject | Company | Ticket type | Why it shows up |
| --- | --- | --- | --- | --- | --- |
| 2026-03-22 | 215474036490837 | Re: Hera Solutions \| Ready To Discover the Difference? | — (DelivRE prospect) | General | Asked about insurance chargeback pricing |
| 2026-03-10 | 215473912298944 | Account Cancellation Request | Blue Leaf Logistics LLC | Billing Issue | Cancellation + stop billing |
| 2026-02-22 | 215473653265078 | Immediate Vendor Cancellation Notice | — (JKG Logistics) | none | Bulk vendor cancellation, mentions billing in passing |
| 2025-11-05 | 215471631353549 | Fw: Fwd: Fw: Hera: Invoice for September 2025 | — (Go Ground Xpress) | General | Forwarded invoice with employment verification ask |
| 2025-10-01 | 215471093061265 | Fwd: Fw: Hera: Invoice for September 2025 | — (Go Ground Xpress) | none | Winddown / final billing confirmation |
| 2025-08-06 | 215470203479868 | Billing Invoices | — (Brian Higginbotham) | none | Historical invoices for tax purposes |
| 2025-06-03 | 215469273006661 | May Failed Payment | — | none | Hera-initiated failed-pay outreach |
| 2025-06-03 | 215469272786282 | May Failed Payment | — | none | Hera-initiated failed-pay outreach |
| 2025-06-03 | 215469272923313 | May Failed Payment | — | none | Hera-initiated failed-pay outreach |
| 2025-06-03 | 215469272978986 | May Failed Payment | — | none | Hera-initiated failed-pay outreach |
| 2025-06-03 | 215469272755605 | May Failed Payment | — | none | Hera-initiated failed-pay outreach |
| 2025-06-03 | 215469272773517 | May Failed Payment | — | none | Hera-initiated failed-pay outreach |
| 2025-06-03 | 215469272646526 | May Failed Payment | — | none | Hera-initiated failed-pay outreach |
| 2025-06-02 | 215469257574691 | Fw: Hera: Invoice for May 2025 | ICS Delivery Solutions | Billing Issue | Address on invoice wrong |
| 2025-05-12 | 215468946098499 | Your AutoPay Payment has been scheduled | — | none | AutoPay notice |
| 2025-05-09 | 215468919309266 | 1147457-10001 - Group Contact Update | — (Principal Life) | none | Internal/vendor, not a customer billing ticket |

## How this snapshot was built

Searches run against the Intercom MCP API (workspace `baat8a8r`):

- `team_assignee_id: 8163722` (Billing/Cancellations team)
- `source_body`: billing, invoice, refund, charged, credit card, credit, payment, Stripe, overcharged, scorecard, double charged, autopay, subscription, cancel my account
- `source_subject`: billing, invoice, Invoice for, Cancel

Some search terms returned zero matches (`credit card`, `payment` in subject, `subscription` in body, `autopay`, `cancel my account`, `double charged`, `Invoice for` in subject) — those phrases either don't appear or the search is matching narrower than expected.

## Patterns and recommendations

1. **Cancellations dominate the billing queue.** Many are DSPs exiting Amazon, not unhappy customers. A clean cancellation playbook (confirm effective date, last billable month, data-access state) would speed these up and create a paper trail.
2. **The Straightaway pattern repeats.** Customers assume scorecard or Amazon data updates Associate status automatically. It doesn't. The in-app popup helps, but onboarding could call this out more directly.
3. **Customers need a way to pull historical invoices themselves.** Brian Higginbotham's ask is going to keep coming back at year-end and tax season.
4. **The May 2025 failed-payment batch shows what manual reprocessing looks like at scale.** Once the Unpaid – Grace Period feature ships, this should drop sharply. Worth measuring before/after to validate.
5. **There's no `Billing Issue` tag applied consistently.** Some clearly-billing conversations end up `General` or have no type. If reporting on billing volume matters, the team could benefit from a quick triage rule to set ticket type on creation.
