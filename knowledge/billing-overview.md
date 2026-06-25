# Hera Billing Overview

Internal reference for how Hera bills customers. Use this when answering billing questions, drafting customer responses, or working through a dispute.

The customer-facing version of the Associate-status piece lives in Intercom: [Managing Associates Statuses](https://support.hera.app/en/articles/11683057-managing-associates-statuses) (id 11683057).

## The simple version

- Customers are billed **$9 per Active Associate, per month**.
- We bill at the **end of the month for the month that just ended**, not up front.
- Roughly **$0.30 per Active Associate, per day** ($9 ÷ 30).
- Only Associates marked **Active** are billable. Every other status is free.
- There is only one plan, called **Bundle**. Older à la carte options are retired.

## What "Active" actually means for billing

- We use the Associate's status at **end of day** to decide if that day counts.
- If they were Active at EOD, that day is billable. If they were anything else at EOD, that day is free.
- A customer cannot **backdate** a status change in Hera. If they realize they should have marked someone Inactive last month, the product won't let them fix it on their own. Those cases go through the credit process below.

### Billable vs. non-billable statuses

| Status | Billable? |
| --- | --- |
| Active | Yes |
| Onboarding | No |
| Inactive – Failed Onboarding | No |
| Inactive – Terminated | No |
| Inactive – Medical Leave | No |
| Inactive – Personal Time / Vacation | No |
| Inactive – Misc | No |

## How the billing cycle runs

1. On the **1st of each month**, Hera builds the invoice for the month that just ended.
2. We count Active Associate days, apply any discounts on the tenant, and send the final amount to **Stripe**.
3. Stripe charges the card on file.

Customers pay via credit card stored in Stripe.

## Free trial

- New customers get a **45-day free trial**.
- Billing starts the **day after the trial ends**.
- Their first invoice (on the 1st of the next month) only covers from the trial-end date forward, so the first bill is usually partial.
- Example: trial starts May 1, ends June 15, billing starts June 16. The July 1 invoice covers June 16 through June 30.

## When a payment fails

This is still being built out. The official "Unpaid – Grace Period" experience is logged as a Jira ticket and not live yet. Today's process:

1. Stripe runs the charge on the 1st.
2. If it fails, we **manually re-run it**.
3. If it fails again, the customer sees a **payment failed** prompt inside Hera asking them to update their card.
4. If the card isn't fixed after several days, we **temporarily restrict access** while we wait for them to update payment.

Once the official grace-period feature ships, this manual process goes away.

## Credits for inflated bills

The most common reason a customer gets overbilled: a terminated Associate stayed marked Active longer than they should have, so we kept billing for them.

How we handle it:

1. The customer raises it (or we catch it in a review).
2. Matthew or John works directly with the company owner to agree on a credit amount.
3. We apply that credit as a **100% discount at the tenant level in Zoho CRM**.
4. The discount stays in place until the credit is used up. During that window the customer's bill comes out to $0, but their real Active Associate count is still tracked so reporting stays clean.
5. Either Matthew or John can apply credits, so we always have someone available.

Document the agreed credit amount in Zoho so we know when to turn the discount off.

## In-app reminder to clean up the Active list

To cut down on inflated bills, the product shows a popup reminding admins to review their Active Associate list.

- Shows up **twice a month**: once around the middle of the month, once roughly a week before month-end (before billing runs on the 1st).
- Title: **"Don't Pay for Inactive Associates"**
- Links inside the popup: "Learn how to offboard Associates" and "See how Active Associates affect billing"
- Button: **View Associate List**

We don't track who has acknowledged the popup yet. That's on the future-improvements list.

## Where things live

| Information | Where to look |
| --- | --- |
| Active Associate count and status history | Hera (DynamoDB) |
| Plan, contract details, credits and discounts | Zoho CRM |
| Charges, card on file, receipts | Stripe |
| Customer-facing billing policy | [Intercom article 11683057](https://support.hera.app/en/articles/11683057-managing-associates-statuses) |
| Billing-related Intercom tickets | Routed to the **Billing/Cancellations** team in Intercom (team id `8163722`). See [`intercom-billing-tickets-snapshot.md`](intercom-billing-tickets-snapshot.md) for a periodic snapshot of what's been coming in. |

## Still to be done

- Official **Unpaid – Grace Period** feature (Jira ticket logged, not yet released).
- **Acknowledgment tracking** on the "Don't Pay for Inactive Associates" popup.
- Confirm how the in-app **Billing Email** field on Company Settings lines up with the email Stripe uses for receipts.
