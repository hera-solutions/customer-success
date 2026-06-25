# Intercom Mentions: Scheduler / Driver Scheduling / Group Messaging

Search date: 2026-05-26
Scope: Intercom conversations (all states), keyword searches across source bodies.
Keywords run: scheduler, scheduling, schedule, "schedule drivers", shift, shifts, roster,
calendar, "when i work", connecteam, sling, deputy, "driver app", "hera scheduling",
broadcast, "group message", "group messaging", "group chat", "group text", "mass message",
"mass text", blast, "text all", "text drivers", "message drivers", "all drivers",
"send all", "send a message", messenger, announcement, "work block", availability,
"time off", dispatch.

## Bottom line

- **Direct customer asks for an in-Hera scheduler: 1 confirmed.** (Aloha Logistics)
- **Customer cited a competing scheduling/comms tool as the reason for churning: 1 confirmed.** (NHBlacklabs / Connecteam)
- **Direct customer asks for group messaging or mass-send to drivers: 0 found.**
- The "scheduler" and "group chat" references appearing in many other threads are
  outbound — Matthew's retention/roadmap reply listing "Hera Scheduling with Updated
  Daily Roster" and the "Driver App ... optional group chat" as upcoming features.
  They are not customer-originated demand signals.

## Customer-originated demand signals

### Scheduling — Aloha Logistics (Robert McCullough Jr)
- Conversation: [215469865457343](https://app.intercom.com/a/inbox/_/inbox/conversation/215469865457343)
- Date: 2025-07-15
- Trigger: Re-engagement email ("Your Hera account's been quiet")
- Quote: "No issues to speak of. It would be great if scheduling could be done
  through HERA. We currently use When I Work and have no issues with it but would
  prefer for it to be on the HERA platform."
- Response: Matthew sent the full roadmap including "Hera Scheduling with Updated
  Daily Roster" (Cortex integration, work blocks, service-type compliance, ADP sync).
- Note: This customer later sent a DSP-closure notice in April 2026
  ([215473781938193](https://app.intercom.com/a/inbox/_/inbox/conversation/215473781938193)) —
  closure was business-wind-down, not feature-related.

### Competing scheduler cited at churn — NHBlacklabs Delivery (Jeff Falkingham)
- Conversation: [215474050408242](https://app.intercom.com/a/inbox/_/inbox/conversation/215474050408242)
- Date: 2026-04 (account closed 2026-04-14)
- Quote: "I am consolidating process and Hera is the odd man out. Paycom has
  turned on texting along with performance discussions all tied to the employee
  record... Connecteam is also in the mix since scheduling, recognition, help
  desks are all working with the team."
- Signal: Lost customer to a stack consolidation where Connecteam covers
  scheduling and Paycom covers texting/performance — i.e., the two adjacent
  features (driver scheduling and driver messaging) Hera is building toward
  were already covered by competitors he chose to standardize on.

## Outbound mentions only (not customer demand)

The phrases "Hera Scheduling," "Driver App," and "optional group chat" appear
in Matthew's retention / roadmap reply, which he has sent to multiple customers
including:

- Robert McCullough / Aloha Logistics — [215469865457343](https://app.intercom.com/a/inbox/_/inbox/conversation/215469865457343)
- Alesha Gonzales / Spot On Delivery (Penn Enterprises) — [215472098347741](https://app.intercom.com/a/inbox/_/inbox/conversation/215472098347741) — cancelled anyway, cost was the reason, not features
- Edgar (Retention Offer) — [215469327929303](https://app.intercom.com/a/inbox/_/inbox/conversation/215469327929303)

Roadmap copy used in those emails (for reference):

> **Hera Scheduling with Updated Daily Roster 📆:** Hera Scheduling will integrate
> with Cortex, incorporating work blocks and ensuring service type compliance. It
> will also sync with ADP/Paycom to improve the import of your time punches and
> reconcile drivers' hours.
>
> **Driver App 📱:** No password is needed. Drivers will receive a 2FA code via
> text/email, eliminating the need for password resets. Drivers can access past
> performance data, counseling, routes, schedules, checklists, and an optional
> group chat.

## Internal / Jira noise (not relevant)

JIRA ticket #1431 surfaced under "shift" searches but is unrelated:
- "Feature Request: 'Deferred Send' for a Counseling… write up the Counseling as
  it occurs (e.g. Speeding), but queue it up to send after the shift is over."
  — That's about delaying a counseling message until after a driver's shift,
  not about scheduling drivers or group messaging.

## Search caveats

- Intercom's free-text search only matches the source (initial) body of each
  thread. Customer replies inside long threads may not be indexed, so genuine
  asks could exist that this sweep missed.
- "When I Work," "Connecteam," "Sling," and "Deputy" returned no hits by name
  except via the Aloha and NHBlacklabs quotes above.
- If we want to be exhaustive, the next step is to export Intercom conversations
  to JSON and grep the full transcript bodies offline.
