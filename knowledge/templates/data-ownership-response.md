# Template: Responding to data ownership and retention questions

Use this when a customer asks any version of:

- "What happens to my data if I cancel?"
- "Will I still have access after I leave?"
- "Can you delete my data?" (proceed with caution, see escalation rules)
- "How do I get my data?"
- "Is my data safe with Hera?"

For the position behind this template see [`../data-ownership-stance.md`](../data-ownership-stance.md).

## The three scenarios

Most data questions fall into one of three buckets. Match the customer's situation to the right scenario before drafting.

---

### Scenario A: Active customer asking about data ownership or safety

**Use when:** the customer is still using Hera and is asking out of curiosity, due diligence, or before a renewal decision.

**Subject:** Your data, and how we treat it

Hi [Name],

Good question, and one we want to be direct about.

The data you put into Hera is yours. It's stored on AWS S3 with encryption at rest and in transit, and we don't delete it on any kind of schedule. As long as you're with us, you have full access through Hera. If you ever decide to move on, your data doesn't disappear with the subscription. We hold onto it, and you can request anything you need from us at any time.

If you'd like to read up on how we handle data security specifically, here's the article: [Can I Store Sensitive HR Data in Hera?](https://support.hera.app/en/articles/11503527-can-i-store-sensitive-hr-data-in-hera).

Anything else you want me to walk you through?

Best,
[Sender]

---

### Scenario B: Customer in a cancellation flow, asking about post-cancellation data access

**Use when:** the customer is canceling and wants to know what happens to their data after the account closes.

**Subject:** Confirming cancellation, and your data

Hi [Name],

Thanks for letting us know. Confirming your cancellation now, and want to make sure you walk away with a clear picture of what happens to your data.

Your data isn't going anywhere. We don't delete it when an account closes. Right now there's one limitation we want to be upfront about: once the account is closed, the Hera interface locks up, so you can't download data directly yourself. We're actively building self-service access for former customers, but it isn't live yet.

In the meantime, if you ever need anything (coaching messages, counseling documents, performance history, anything else), email us at `support@hera.app`. We typically turn requests around in 1 to 2 business days.

If you do want to grab a copy of anything while you still have the UI, you're welcome to. There's no deadline driving it. We'll still have your data either way.

Let me know if anything else would help.

Best,
[Sender]

---

### Scenario C: Former customer requesting data after cancellation

**Use when:** the account is already closed and the customer is reaching out for a specific data pull (usually unemployment claim or legal).

**Subject:** We can pull that for you

Hi [Name],

Happy to get that pulled together for you. Quick question so we send the right thing: what do you need this for? Most former-customer requests are one of these:

- Coaching messages from Scorecards (often for unemployment claims)
- Signed Counseling documents
- Associate records and dates of employment
- A general data export for accounting or records

If you can tell me which one fits, or describe the situation, I'll make sure we send everything you need on the first round. Our standard turnaround is 1 to 2 business days from when we acknowledge the request.

Best,
[Sender]

---

## Tone and rules across all three

- Plain English. No legalese. No corporate filler.
- No em dashes. Use commas, periods, or hyphens.
- Lead with reassurance, not policy. The customer wants to hear "your data is safe and yours," not "per section 4.2 of our terms."
- Be honest about the self-service limitation. Don't dance around it. Acknowledging it builds more trust than hiding it.
- Don't invent retention timelines or deletion schedules. We don't have them.
- Always end with a clear path: email `support@hera.app` for requests, 1-2 business day turnaround.

## When to escalate to Matthew before sending

- Customer asks for a **written data retention policy** or a **DPA** (Data Processing Agreement).
- Customer's legal counsel is making the request directly (subpoena, discovery).
- Customer is asking us to **delete** their data outright (right to be forgotten, GDPR-style request).
- Customer is implying we've lost their data or are stonewalling them.

In those cases, send a short holding reply ("Let me loop in Matthew on this and get back to you within a day") and escalate.

## Variables to fill in

- `[Name]` — customer's first name. Check Intercom or their signature.
- `[Sender]` — your name, plain. No "Best regards" or other filler.
