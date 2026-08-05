# How to fill in a CS task

**Set 08-05-2026. Field names and every picklist value verified live against Zoho on 08-04-2026.**

Seven custom fields on the Tasks module, plus two standard ones you also touch. **You fill six of them; the generator sets `Next Action` and `Description`.**

**Where they are:** the **full task record**, not the popup. The popup that opens from a list view carries only Subject, Priority, Due Date, Status, Related To and Owner. The last two custom fields sit below `Customer Quote`, which is a tall text box, so keep scrolling.

---

## The one rule that matters more than any single field

**An empty field is a fact. A guessed field is a lie that gets averaged into a decision.**

These fields are the only record of what customers actually tell us, and the plan is to use one quarter of them to decide whether the 30-day trigger is right. **A guess is worse than a blank**, because a blank is visibly missing and a guess is not.

So: if you did not reach the customer, only two fields get filled. If you reached them and they did not answer something, leave that one empty.

---

## Fill order

**`Contact Outcome` first, always.** It is the gate. What you fill after it depends entirely on what it says.

| `Contact Outcome` | Then fill | Leave empty |
|---|---|---|
| **Reached** | `Job Named`, `Blocker`, `Ask Made`, `Customer Quote`, `Next Action` | `Outcome Evidence` if you are unsure |
| **Left message** | `Next Action` only | Everything else |
| **No answer** | `Next Action` only | Everything else |
| **Rescheduled** | `Next Action`, and `Customer Quote` if they said why | Everything else |
| **Declined to talk** | `Next Action` = `Escalate to Matthew`, and `Customer Quote` verbatim | Everything else |

---

## 1. Contact Outcome

**Picklist. Always filled. Never left empty on a worked task.**

| Value | Use it when |
|---|---|
| `Reached` | You spoke to a human who can act. **Not** a receptionist, not a driver who says they will pass it on |
| `Left message` | Voicemail left, or a text sent with no reply yet |
| `No answer` | Rang out, no voicemail, or the line failed |
| `Rescheduled` | They picked up and asked for another time. **This counts as contact and it stops the chase sequence** |
| `Declined to talk` | They actively refused. **Escalate immediately, do not wait for the ladder** |

**There is no "wrong number" value.** If the number is dead, use `No answer` and put the detail in `Ask Made`, for example `number disconnected, need a new contact`.

**Why it matters:** this is the only field that separates our tasks from the old automation's, so it is how coverage gets counted. An attempted call with `No answer` still counts as coverage. A task with this field blank counts as nothing.

---

## 2. Next Action

**Picklist. Always filled. The generator pre-sets it; you change it as you go.**

| Value | Meaning |
|---|---|
| `1 Call and voicemail` | Where a RISK task starts |
| `2 Text the owner` | Business day 3 |
| `3 Email plus 2nd contact` | Business day 5. **Try a different person here, not just a different channel** |
| `4 Final, 2nd contact` | Business day 8 |
| `Escalate to Matthew` | Business day 10 with no contact and no change, or immediately on `Declined to talk` |
| `Single outreach` | ENGAGE tier. One touch a quarter, no chase |
| `Confirm or close` | Matthew's queue. Not a CS call |

**This field is the ladder position. There is no counter anywhere else**, so if you do not move it, the next person cannot tell which attempt they are on.

**The moment you reach someone, stop advancing it.** Any contact ends the chase. Set it to whatever genuinely happens next, or leave it where it is and close the task.

---

## 3. Job Named

**Picklist. Fill only if `Contact Outcome = Reached`.**

**What it captures: the part of their day the customer told you was hardest.** Not the feature they are missing, and not what you think their problem is. Their words, mapped to the nearest job.

| They talk about | Pick |
|---|---|
| Staffing tomorrow, callouts, texting people at night to fill routes | `1 Staff the routes` |
| Amazon reviews, tier, being blindsided by a score | `2 Amazon scorecard` |
| Firing someone, warnings, paperwork that has to hold up | `3 Coach and document` |
| Telling everyone something at once, drivers not reading it | `4 Reach the whole team` |
| Vans, maintenance, damage, devices | `5 Keep the fleet legal` |
| Handover, what happened yesterday, one place to look | `6 One place to run ops` |
| They only want one part of the product and not the rest | `Wants only part of it` |
| What they need, Hera does not do | `Hera does not do it` |

**The last two are the valuable ones, not the failures.** `Wants only part of it` is a pricing conversation for Matthew, not an adoption play. `Hera does not do it` is product feedback and is worth more to the company than saving the account.

**If they never named a hardest part, leave it empty.** Do not infer it from which feature they stopped using.

---

## 4. Blocker

**Picklist. Fill only if `Contact Outcome = Reached`. This is the single most valuable field on the task.**

**What it captures: why they stopped, in their explanation, not yours.**

| Value | Use it when they say |
|---|---|
| `Nobody was shown how` | They never had a walkthrough, or the person who did has gone |
| `Person who did it left` | The individual who used Hera has left the company |
| `It broke or was slow` | A product problem. **Get specifics, raise a ticket, and come back with a date** |
| `They do it elsewhere now` | Another tool or a spreadsheet replaced it. **Ask what it does better. Do not argue** |
| `They forgot it existed` | Awareness only. The cheapest fix there is: show them on the call |
| `Drivers will not use it` | Driver-side resistance. **Get the driver's actual complaint word for word** |
| `Other, see Description` | None of the six fit. **You must then write the reason in Description** |

**Why it matters more than the outcome of any single call:** across enough calls the pattern here tells us what to build and what to fix. One account's blocker is an anecdote. Forty accounts' blockers are a roadmap.

**Do not reach for `Other` to avoid choosing.** Six categories came out of real churn analysis and cover almost everything. If you use `Other`, the Description is not optional.

---

## 5. Ask Made

**Text, 255 characters. Fill only if `Contact Outcome = Reached` and you asked for something.**

**What it captures: the one change you asked for, who owns it, and by when.** All three parts, or it is not an ask.

**Good:**
- `Maria to send one message to drivers by Fri 08-08. I check back Mon 08-11.`
- `Owner to add replacement for Steph (departed May) and book 20min walkthrough w/e 08-11.`
- `Number disconnected. Owner to send a working mobile for the ops manager.`

**Bad:**
- `Discussed getting back on Hera` — no owner, no date, no specific change
- `Will follow up` — that is your action, not theirs
- `Sent them the help docs` — no change was requested of anyone

**One ask per call.** Two is a to-do list and a to-do list gets ignored. Getting an account out of RISK takes only **one** signal coming back, so ask for whichever one is easiest for them, usually a single message to their drivers.

**Never ask for, or offer, money off.** Any pricing question goes to Matthew and you say you will come back to them.

---

## 6. Customer Quote

**Long text. Fill whenever the customer said anything worth keeping, even on a `Rescheduled` or `Declined to talk`.**

**What it captures: their words, verbatim, with who said it and the date.** Not your summary.

**Format:** `"<exact words>" — <name>, <role if known>, MM-DD-YYYY`

**Good:**
- `"Honestly, Steph handled all that and she left in May. I've been doing the schedule on paper since." — Dave Kerrigan, owner, 08-05-2026`
- `"Nothing. We'd be fine without it." — owner, 08-05-2026`
- `"It saves me about six hours a week on the coaching side." — Angela Ruiz, ops manager, 08-05-2026`

**Bad:**
- `Customer seemed happy with the product` — that is an impression, not a quote
- `Said they save a lot of time` — paraphrase, and unusable
- `Frustrated with load times` — no words, no name, no date

**"Nothing, we'd be fine without it" is the most valuable sentence you can bring back.** Record it exactly. Do not soften it and do not leave it out because it is bad news.

**This is the only legitimate source of a time-saved claim.** If a customer says a number, we can quote it with their name on it. **Never calculate one yourself and never multiply a usage count by assumed minutes.**

---

## 7. Outcome Evidence

**Text, 255 characters. Optional. Fill only if `Contact Outcome = Reached` and you are confident.**

**What it captures: whether what the customer said matched what we assumed they wanted.** We have a catalog of 16 outcomes we believe operators care about, written from the product and the data rather than from talking to anyone. **No customer has ever been asked.** This field is how it stops being guesswork.

**Format:** the outcome ID, then `confirmed` or `contradicted`, then a few words.

- `O-1.2 confirmed - said the 5am callout is the worst part of the week`
- `O-2.1 contradicted - does not care about the scorecard, Amazon rep handles it`
- `O-4.3 confirmed - drivers ignore it, wants read receipts`

The IDs, by job:

| Job | Outcomes |
|---|---|
| 1, staff the routes | `O-1.1` roster built ahead, `O-1.2` same-day callout covered, `O-1.3` van and driver ready |
| 2, Amazon scorecard | `O-2.1` no surprises at review, `O-2.2` tier does not slip, `O-2.3` quality caught at the photo |
| 3, coach and document | `O-3.1` defensible documentation, `O-3.2` good work recognised, `O-3.3` compliance records current |
| 4, reach the team | `O-4.1` tell everyone once, `O-4.2` routine comms without remembering, `O-4.3` drivers actually use it |
| 5, fleet | `O-5.1` maintenance before breakdown, `O-5.2` damage recorded with evidence, `O-5.3` fleet gets attention |
| 6, one place | `O-6.1` problems written where the next shift sees them |

**If you do not know the ID, leave it blank and put what they said in `Customer Quote` instead.** A good quote is worth more than a wrong ID. This is the one field where blank is genuinely fine.

**The catalog is `provisional-1.0` and Matthew has not signed it off**, so nothing from it goes in front of a customer yet. Using the IDs internally on a task is fine and is how it earns ratification.

---

## 8. Status, a standard field you still have to set

| Value | Use it when |
|---|---|
| `Not Started` | How the task arrives |
| `In Progress` | You have made an attempt and the ladder is still running |
| `Waiting for input` | You asked for something and are waiting on the customer |
| `Completed` | The ask landed, or the account recovered, or it escalated to Matthew |
| `Deferred` | Do not use. Use `Waiting for input` or close it |

**Close a task when your part is done, not when the customer is fixed.** Whether it worked is answered by the next morning's run, not by you. **There is deliberately no "did it work?" field.**

---

## 9. Description, which the generator writes

**Read it, do not overwrite it.** It carries the pre-call facts: what they pay, driver count and direction, whether the roster is frozen, which of the four signs of life are quiet and for how long, and any entitlement or billing warning.

**Add to the bottom if you need to**, particularly when `Blocker = Other, see Description`. Never delete what was there, because it is the evidence for why the task existed.

---

## Never touch Notes

**No script, automation or CS process writes, edits or deletes a Zoho Note. Ever.**

Notes are the human narrative, written by John, Matthew and Lizz, with an established convention of the interaction date as the title. **The nine fields above are the structured record; Notes are the story.** Two records, two jobs, no overlap. If automation started writing notes alongside people, nobody could trust the customer history again.

---

## A filled-in example

TPE Logistics, $931/mo, 115 drivers, roster frozen 50 days, dark on all four signs of life.

| Field | Value |
|---|---|
| `Contact Outcome` | `Reached` |
| `Job Named` | `1 Staff the routes` |
| `Blocker` | `Person who did it left` |
| `Ask Made` | `Owner to name Steph's replacement and add them by Fri 08-08. 20min walkthrough booked w/e 08-11.` |
| `Customer Quote` | `"Steph handled all that and she left in May. I've been doing the schedule on paper since." — Dave Kerrigan, owner, 08-05-2026` |
| `Outcome Evidence` | `O-1.1 confirmed - building the roster is the job, just not in Hera` |
| `Next Action` | `Escalate to Matthew` |
| `Status` | `Waiting for input` |
| Description | untouched, plus one line: `Roster frozen 50d at 115 billed drivers, likely over-billed. Flagged to Matthew.` |

**Why `Escalate to Matthew` on a call that went well:** the roster has been frozen 50 days on per-driver billing, so they are probably paying for people who left. That is a refund question and it is not CS's to answer.

And the same account if nobody picks up:

| Field | Value |
|---|---|
| `Contact Outcome` | `No answer` |
| `Next Action` | `2 Text the owner` |
| `Status` | `In Progress` |
| Everything else | **empty** |
