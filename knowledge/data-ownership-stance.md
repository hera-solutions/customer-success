# Hera's Data Ownership Stance

Internal reference for what we say (and what we promise) when a customer asks about their data. This is part of Hera's value proposition: customers own their data, and they never lose access to it because they stopped paying.

Use this file as the source of truth for the position. The customer-facing version of the messaging lives in [`templates/data-ownership-response.md`](templates/data-ownership-response.md).

## The position, in one sentence

**Your data is yours. It stays safe in Hera, and we will never delete it without making sure you have everything you need first, whether you're a current customer or not.**

## Core promises we make

1. **The data belongs to the customer.** They put it in. They own it.
2. **We do not delete data on a schedule.** There is no retention clock that wipes a former customer's records after some number of months.
3. **Closing or not paying doesn't terminate access to the data.** It changes how the customer requests it, not whether they can get it.
4. **If we ever needed to delete data, we'd make sure the customer had everything they needed first.** We don't surprise people.
5. **Data is stored on AWS S3 with encryption at rest and in transit.** See [Intercom article 11503527](https://support.hera.app/en/articles/11503527-can-i-store-sensitive-hr-data-in-hera) for the customer-facing security framing.

## Honest limitations we acknowledge

- **Self-service download is not available after an account is closed.** Once an account is closed, Hera locks up the UI and the customer can't pull data themselves. This is a current product limitation, not a policy choice.
- **The fix is in progress.** We're actively building the ability for former customers to access and download everything themselves, even after closing their account.
- **In the meantime, the workaround is fast and free.** They email `support@hera.app` (or use in-app chat while still active), we acknowledge, and we deliver within **1 to 2 business days**.

Never imply that data is unavailable, hard to retrieve, or contingent on anything. The customer experience should feel like: "Just ask, we'll send it."

## What former customers most often request

From the cancellation conversations on file:

- **Coaching messages from Scorecards** — usually to support unemployment claim denials when a former associate left voluntarily.
- **Signed Counseling documents** — supporting the reason for separation, again typically for unemployment hearings.
- **Associate records and timelines** — proof of who worked, when, and what the performance record looked like.
- **General data exports** — for tax purposes, accounting handoffs, or DSP-to-DSP transitions.

Tell the support team: when a request comes in, ask the customer what they actually need it for. That usually narrows the data pull and gets them their answer faster.

## Canonical wording (Matthew's standard)

This wording appears nearly verbatim across multiple Matthew-led cancellation conversations (Go Ground Xpress, Level Up Logistics, and others). Treat it as the house style:

> You don't need to worry about extracting anything from Hera. Your data isn't going anywhere.
>
> Right now, there's a system limitation. Once an account is closed, Hera locks up, and data can't be downloaded directly. But your data is still safe. Please reach out if you need anything later, whether for a legal matter or anything else. We'll get it for you.
>
> We're actively working to remove this limitation. The goal is for customers to access and download everything themselves, even after closing an account.
>
> We'll ensure you have everything you need before any data is deleted.

And John's standard add-on for unemployment-claim cases:

> When a DSP closes, whether voluntarily or involuntarily, we handle each situation individually since every operation is a little different. When an owner reaches out for unemployment-related documentation, they typically request communications that include coaching from Scorecards or signed Counseling documents that support the reason for separation. These requests are handled by our team with a standard turnaround of 1 to 2 business days.

## Things we never say

- "Your data will be deleted after [X months]." We don't have that policy. Don't invent one.
- "We can only hold your data for a limited time." Same reason.
- "Once you cancel, you lose access to your data." We lose self-service access. We do not lose access to the data itself.
- "You should export everything before cancellation." Don't push urgency on customers. The data stays. If they want to grab a copy now while they have the UI, that's fine, but it's not a deadline.
- "Per our data retention policy..." There's no formal published policy yet. If a customer asks for one in writing, escalate to Matthew before responding.

## When to escalate to Matthew

- Customer asks for the **written data retention policy** or a **DPA** (Data Processing Agreement).
- Customer's legal counsel is requesting data directly (subpoena, discovery, etc.).
- Customer is asking us to **delete** their data outright (right to be forgotten / GDPR-style request).
- Customer is implying we've lost their data or are holding it hostage.

These touch areas where we don't have a formal policy yet and where the wrong off-the-cuff answer can create real liability.

## Your data, not Amazon's data

A related angle that comes up often: customers ask whether they can drop a Hera feature because Amazon now collects the same thing (vehicle photos via the Flex app, scorecards, routing, etc.). The answer is usually no, and here is why.

**The structural point:** Amazon is not built to be a DSP's historical record. Their data retention is short (roughly one year for most categories), they don't expose easy historical retrieval to DSPs, and the things they collect can change or disappear when Amazon decides to change a feature. The data sits with them, not with the customer.

**Hera flips that.** The data lives in the customer's account, on their timeline, retrievable whenever they need it. That's the value: not that we're a better collection tool than the Flex app, but that we're the record that's still there a year or two later when they actually need to look at something.

**Where this matters most in conversations:**

- Vehicle photos vs. Flex photo checklist (the common one as of 2026)
- Performance metrics vs. Amazon scorecards going back more than a year
- Routing or stop-level data vs. the DSP Pulse view
- Driver coaching records vs. Amazon-side communications

**Don't position this as anti-Amazon.** The truthful framing is structural. Amazon's tools are operational. Hera is the system of record. Different jobs.

**Don't dismiss the operational friction.** When a customer raises "Amazon now does this too, my drivers are doing it twice," the duplicate workflow is a real complaint. Acknowledge it. Then offer the middle path: reduce Hera's requirements down to essentials rather than dropping the record entirely. Most customers will take that.

**Where this argument gets weak:** for genuinely commodity data the customer can also pull from Amazon at any time (e.g., a current-day fact they only ever need today), the case for keeping it in Hera too is thinner. Save the pushback for data that has a long tail.

## Gap to fill

There is no published Intercom KB article that directly addresses "What happens to my data after I cancel?" or the "your data, not Amazon's data" position. Per the user, no need to write one yet, but keep this in mind. Both are recurring conversations and important parts of the value prop. When the time comes to publish, the language in this file is the starting point.
