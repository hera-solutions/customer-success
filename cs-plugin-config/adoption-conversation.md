# The RISK call

**Rewritten 08-04-2026 against the decisions actually agreed. Still PRE-ROLLOUT: no customer contact is authorised.**

Replaces the 08-03-2026 draft, which was written for a 62-account cohort (adoption risk 27 plus stopped scorecards 35) that the heartbeat model superseded. That cohort definition is gone. **Amazon scorecard is no longer a cohort at all**, by decision: the upload is a weak adoption indicator at weight 2.4, not a heartbeat, and the score is never a metric.

**Scope.** This is the script for the **RISK tier only**: accounts dark 30+ days on 3 or more of the four heartbeats, above the value floor. On 08-04-2026 that is **three accounts, $1,509/mo**. The ENGAGE tier is email-first and its call format is at the bottom. Confirm-or-close belongs to Matthew and is not in this file.

---

## Read this before the first call: all three are dark on all four

**Every one of the three is dark on all four heartbeats.** Not two, not three. Four.

That breaks the central rule of the previous draft, "open with what they are doing," because **there is nothing they are doing.** No messages, no paperwork, no schedules, no driver changes. Do not manufacture an opener out of a weak signal like an odometer reading. It is transparent and it wastes the goodwill you get in the first minute.

### The fact that makes these calls winnable

| Account | Pays | Associates | Revenue direction | Days since trigger fired |
|---|---|---|---|---|
| **TPE Logistics Solutions** | $931 | 115 | **growing +17%** | 21 |
| Probyn Inc | $357 | 41 | **growing +55%** | 58 |
| Divine Package | $221 | 43 | flat +1% | 46 |

**All three are growing or flat while touching nothing.** They are hiring drivers and their invoice is rising, so **the business has not closed.** That rules out the single most common reason accounts go dark, and it is why these three are worth calling: something replaced Hera, or nobody was ever trained, or the one person who used it left. All three of those are fixable. A closed DSP is not.

**Say the growth out loud.** "You've added drivers since March and your invoice has gone up" is true, verifiable, and it is the honest reason for the call.

### Call order

**Do all three in one day, it is three calls.** If only one gets made, make it **TPE**: most revenue at $931, most people at 115, and at 21 days past trigger it is still inside the window where **no comparable account has ever churned.** Best odds and the biggest number.

**Probyn has the least runway at 58 days past trigger**, in the band where 38% of comparable accounts were gone by day 60. Most urgent, and also most likely already decided.

**Divine Package cannot roster.** It has no rostering entitlement, one of only 4 accounts in 241. **Never raise driver schedules with them.** Flagging a customer for not using something they cannot access costs you the call in the first minute.

---

## Step 1: Pre-call, 5 minutes, data only

The task description already carries these. **Never open this call without them.** Guessing in front of a customer about their own usage is worse than not calling.

| Check | Source | Why |
|---|---|---|
| **Entitlement** | `can_roster`, derived from `Tenant.accountPremiumStatus` | Accounts without `bundle` or `rostering` **physically cannot roster** |
| **Revenue direction** | last four **closed** invoices | Never the current accruing month, it is a partial average and it produced two fake 36% declines |
| **Real headcount now** | `Staff` on `byGroupStatus`, `status = 'Active'` | The number to say out loud |
| **Discount and billing state** | `Invoice.discountPercentLabel`, invoice status | Walking in unaware of a live credit or a failed payment is avoidable |
| **Which heartbeat is closest to coming back** | days-since per signal | This is your ask. See step 5 |

**Two hard stops before dialling.** `Payment Error` or `Written Off` in the last three invoices makes it Matthew's billing call, and it goes first, separately. This is now enforced by the generator rather than left to judgment. AMP accounts have no invoice and no revenue axis, so score on engagement only and never reference billing (`amp-cohort.md`).

---

## Step 2: Open on their operation, not on Hera

**Do not open by asking whether they still use Hera.** With an account 51 days dark and paying $931, that question invites "no, cancel it," and you will have talked a growing customer into churning. The old draft's instruction to "ask straight out whether they are still using Hera at all" is wrong for that reason and is withdrawn.

Open on the business. It is safe, it is genuinely interesting, and it tells you within a minute whether this is fixable.

> "How's the operation running right now, are you still on [N] routes? I ask because you've added drivers since [month] and I wanted to make sure the billing side of that is actually matching what you're getting."

That does three things: gets them talking about themselves, states a verifiable fact, and gives an honest reason for the call that is on their side of the table.

**Never open with:**

- "We noticed you're not using..." Accusatory, about something they pay for.
- "I wanted to check in." No purpose, burns two minutes.
- "Are you getting value from Hera?" Invites a yes and ends the conversation.
- **Anything that sounds like a renewal.** There is no renewal event at Hera. Month to month, no contract. Implying one is dishonest.
- **Anything that sounds like a save play.** Nobody has threatened to leave. Do not teach them to think about cancelling.

---

## Step 3: Name the gap once, plainly, then stop talking

One sentence. Then silence, and let them fill it.

> "The reason I'm calling is that as far as I can see nothing's been happening in Hera on your side since about [month]. No messages, no schedules, nothing. That's usually a sign something changed at your end, and I'd rather ask than guess."

**"I'd rather ask than guess" is the whole posture of this call.** You are not there to correct them.

Map whatever comes back to one of the six jobs in `outcome-catalog.md`:

| They describe | Job | Likely gap |
|---|---|---|
| Staffing tomorrow, callouts, texting people at night | Job 1, get routes staffed | Rostering, replacements, checklists |
| Amazon reviews, tier, scores, being blindsided | Job 2, survive the scorecard | Scorecard upload stopped |
| Firing someone, warnings, paperwork | Job 3, coach defensibly | Counselings, infractions, kudos |
| Telling everyone something, drivers not reading | Job 4, reach the team | Messenger, recurring messages |
| Vans, maintenance, damage | Job 5, keep the fleet legal | **Upside only, never framed as risk** |
| Handover, what happened yesterday | Job 6, run from one place | Daily log, notes |

**If they name something Hera does not do,** write it verbatim and stop selling. Product feedback is worth more than a save.

**If they only want one part of the product,** that is the partial-value profile. Do not run an adoption play. Confirm the one job, score them on it alone, and **route the pricing question to Matthew.** Live example in the book: a 66% discount labelled "Customer Service - Only using Texting and Coaching."

---

## Step 4: The blocker question

> "When it stopped, what got in the way?"

Classify the answer. This is the field that will eventually tell you what actually works, and across enough calls the pattern is worth more than any single outcome.

| Blocker | What it means | The ask |
|---|---|---|
| **Nobody was shown how** | Onboarding gap | 20 minute walkthrough, **named** person, this week |
| **The person who did it left** | Ownership gap, very common in DSPs | Find the replacement, add and train them. **Stop contacting the old one** |
| **It broke or was slow** | Product issue | Get specifics, open a ticket, **come back with a date** |
| **They do it somewhere else now** | Displaced. Ask what the other tool does better. **Do not argue** |
| **They forgot it existed** | Cheapest fix there is. Show them on the call |
| **The drivers will not use it** | Driver-side, **currently unmeasured**. Get the complaint verbatim |

---

## Step 5: One ask, one owner, one date

**One change per call.** Two is a to-do list, and a to-do list gets ignored.

**Getting out of RISK takes exactly one heartbeat coming back.** Every signal is days-since against a 30-day threshold, so the moment they send one message or build one schedule, that signal resets to zero and a 4-of-4 account drops below the line. **Ask for whichever one is easiest for them, not the most important one.** For most accounts that is sending a single message to the team.

> "Can Maria send one message to the drivers this week, and I'll check back Monday?"

**Never offer a discount as the answer to non-adoption.** This has already happened: Spears Enterprises took a **100% credit labelled "Non Usage"**, roughly $1,040 a month, with no adoption conversation ever held. Crediting a customer for not using the product turns a solvable problem into permanent lost revenue and hides it from the churn data. Pricing goes to Matthew, and you say you will come back to them.

---

## Step 6: Get the quote

Before you hang up:

> "Last thing before I let you go. If Hera disappeared tomorrow, what would you actually miss?"

Write it **verbatim**, with the name and the date. From a 4-of-4 dark account the answer may be "nothing," and **that is the single most valuable sentence you can bring back.** Record it exactly.

- A customer saying "this saves me about six hours a week" is quotable and attributable. Use it, name them.
- **Never generate an hours figure yourself, and never multiply a usage count by assumed minutes.** The primary value metric is work executed in Hera, counted. Time saved is the customer's sentence, never your arithmetic.

---

## Step 7: Log it

**Seven custom fields on the Task.** The generator pre-fills `Next Action`; the caller fills the other six.

| Field | Content |
|---|---|
| `Contact Outcome` | Connected, left message, no answer, wrong number, declined to talk |
| `Job Named` | One of the six, or "not covered by Hera" |
| `Blocker` | One of the six categories in step 4 |
| `Ask Made` | The ask, with owner and date |
| `Outcome Evidence` | Catalog entry confirmed or contradicted, by ID. **This is how `outcome-catalog.md` moves from inferred to evidenced** |
| `Customer Quote` | Verbatim, with name and date |
| `Next Action` | Ladder position, set by the generator |

**Never write, edit or delete a Zoho Note.** Hard rule. The structured record lives in these fields; the narrative lives in Notes, written by people. Two records, two jobs, no overlap.

**An attempted call counts toward coverage.** Record the attempt. Coverage is the Q1 target, not outcome.

---

## When they do not answer: the ladder

**Business days, because the routine runs Monday to Friday.** Weekend activity counts toward Monday.

| Business day | Action |
|---|---|
| 0 | Trigger fires, task created with the pre-call facts |
| **1** | Call the owner, leave a voicemail |
| **3** | Text the owner |
| **5** | Email, **and try a second person at the account** |
| **8** | Final attempt to the second contact |
| **10** | Score unchanged and still unreached: **escalate to Matthew** |

**The second contact on day 5 matters more than the channel change.** "The person who did it left" is one of the six blockers, and no number of texts to a departed owner will work.

### Any contact ends the ladder

**The ladder is a protocol for silence.** The moment they tell you anything, stop working the calendar and work the information. A text back is contact. "Can't talk, call me Thursday" is contact. Do not fire attempts 3 and 4 at someone who already responded.

| What they tell you | Pivot to |
|---|---|
| Nobody was shown how | Walkthrough, **named** person, this week |
| The person who did it left | Find the replacement. Stop contacting the old one |
| It broke or was slow | **Ticket. Engineering owns it.** CS returns with a date |
| They do it somewhere else now | **Displaced.** Product feedback, not a save |
| They forgot it existed | Show them on the call |
| The drivers will not use it | Get the complaint verbatim |
| They only want part of the product | **Pricing. Matthew.** Not an adoption play |
| Hera does not do what they need | **Product feedback. Stop selling** |

### Escalation triggers

- **Day 10, score unchanged, never reached.** A CEO-to-owner call reaches people a CSM cannot.
- **First "declined to talk": escalate immediately, no waiting.** Someone actively refusing contact while dark on four heartbeats is not merely busy.
- **Reached, ask made, score does not move in 30 days.** The ask did not stick. **Change the approach, do not re-run the same ask.**
- **Three months of no movement while still paying and reachable.** Drop to quarterly watch. p90 runway is 1,480 days, and calling monthly forever is waste.

### Nobody grades their own homework

**The next daily run is the scorecard.** No "did it work" field, no self-reporting. Account reads ACTIVE next run means it worked or they recovered anyway. Still RISK and was reached means the ask did not stick. Still RISK and never reached counts toward escalation.

---

## The ENGAGE call, when someone books from the email

Different conversation, and it must not borrow this tone. **ENGAGE accounts are healthy daily users with one feature gap.** All 33 covered by `csm/engage-message-templates.md` sent a message within 11 days, and 30 within 3.

- **They self-selected by booking, so skip discovery.** They already know which feature the email named.
- **Go almost straight to step 4**, the blocker. That is the entire point of the call.
- **15 minutes, and end early if you can.** The email promised 15.
- **No ladder, no escalation, one outreach per quarter.** If the call does not happen, it closes at quarter end and recurs.
- **"We do it in a spreadsheet and it works" is a complete and successful outcome.** Log it and close. Do not push twice.

---

## Still undecided, and not resolved by this file

- **QBR format and template.** Open.
- **Success plan format and template.** Open.
- **Stakeholder map template.** Open.
- **Renewal conversation style.** Open. Whatever is chosen must not imply a renewal event, because there is not one.

An earlier draft argued all four were not applicable at a $759 median account value. **That argument was not accepted and is not policy.** It is recorded so the reasoning is not lost if the question returns.
