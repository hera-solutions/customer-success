# ENGAGE outreach templates

**Status: DRAFT, 08-04-2026. Not approved. Nothing here may be sent to a customer yet.**

**Four live drafts covering 26 of the 41 ENGAGE accounts, $24,102/mo.** A fifth and sixth, gap 3, are WITHDRAWN: 7 accounts and $6,240/mo built on a signal that turned out to be wrong half the time. See gap 3 below. Written for the tier where the account is **healthy and using Hera daily** but has one feature gap. This is not a save motion and must never read like one.

---

## What these are for

An ENGAGE account is active: every one of the 33 originally in scope sent a human message inside the last 11 days, and 30 of them inside the last 3. **They are not at risk and must not be contacted as if they were.** The gap is a single unused capability.

**The purpose of the outreach is to find out why, not to sell the feature.** The most likely answers are that they solved it another way, they never knew it existed, or it does not fit how they run. All three are useful, and only the second one leads to a demo. An email that pitches gets a polite no and teaches us nothing.

Each template asks one question and requests 15 minutes. **Log the answer in `Blocker` and `Customer Quote` on the task.** The blocker picklist exists because the pattern across 33 accounts is worth more than any single call.

## Rules of use

- **One outreach per quarter per account.** ENGAGE is not a ladder. No chase sequence, no escalation to Matthew.
- **Never lead with what they are not doing.** Every template opens with something true about their actual usage. Opening with the gap reads like surveillance.
- **No discount, credit, or commercial offer.** These are not retention conversations, and introducing price invents a problem the customer did not have.
- **If they answer "we do it in a spreadsheet and it works," that is a complete and acceptable outcome.** Record it and close the task. Do not push a second time.
- Send from John's address. Text variant only where a mobile number is on the contact.
- Replace every `[bracket]`. A template sent with a bracket still in it is worse than no outreach.

---

## Gap 1: no route assigned on the daily roster

**14 accounts, $15,374/mo.** These operators run Hera daily but never put a driver on a route in it, so route and van assignments live somewhere else.

**Precision matters in the wording here.** The signal is a `DailyRoster` carrying at least one `Route` with a driver on it. **Several of these accounts DO create rosters and leave them empty**, so "you never build a schedule" would be factually wrong to their face. Say "assigning drivers to routes", not "building a schedule".

### 1a. Never used it (3 accounts, $3,915/mo)

Bison Peak LLC $2,201, Lucky 7 Logistics $1,055, Flash Hub Delivery $659.

> **Subject: How do you build your daily driver schedule?**
>
> Hi [First name],
>
> You and your team are in Hera every day, messaging drivers and keeping your associate list current. One thing I noticed you handle somewhere else is the daily schedule, assigning drivers to routes and vans.
>
> I am asking because I genuinely do not know what you use instead, and that matters to us. If you have a spreadsheet or a whiteboard that works, I would rather understand it than talk you out of it. If it is a hassle every morning, there may be something here worth 15 minutes.
>
> Do you have 15 minutes [this week / week of [MM-DD-YYYY]]? I will keep it to that.
>
> [Sender name]
> Hera Solutions

### 1b. Used it and stopped (11 accounts, $11,459/mo)

Lapsed 31 to 180 days: Express Package System $1,770 (89d), Distant Winds $1,315 (136d), SURF Logistics $1,107 (84d), Leary Logistics $1,070 (57d), RPM Delivery $834 (66d), Infinity Logistics $621 (47d).
Lapsed over 180 days: Sinaro Logistics $1,384 (478d), DC1 Transport $1,275 (862d), JPZ Logistics $878 (248d), Frontline Logistics $795 (560d), On-demand Logistics $409 (608d).

> **Subject: You stopped building schedules in Hera. What changed?**
>
> Hi [First name],
>
> You are in Hera daily, so this is not a nudge about using the product. It is a narrower question.
>
> You were building daily driver schedules in Hera and stopped around [MM-DD-YYYY]. I would like to know what changed. Either something got in the way, or you found a better way to do it. Both are worth hearing, and the first one is something we may be able to fix.
>
> 15 minutes [this week / week of [MM-DD-YYYY]]?
>
> [Sender name]
> Hera Solutions

**For the five accounts over 180 days dark**, soften the date reference to "a while back" rather than naming a date 862 days ago. Naming it reads as an accusation, and the person you are writing to may not have been there.

---

## Gap 2: no driver paperwork on file

**13 accounts. All thirteen build schedules and message drivers daily.**

**Signal correction, 08-05-2026, and it changes which template each account gets.** The gap came from the `document` signal, which turned out to be **94% vehicle photos from the daily check** rather than paperwork. Checked against the real measure (`documentStaffId`, a file filed against a person):

- **All 13 genuinely have filed nothing against a person in 90 days**, so the claim in the email is true.
- **But 5 were flagged because their VEHICLE PHOTO LOG lapsed, not their paperwork**: FKG 39 days, Blue Heron 78, OneLove 49, KJ 32, Rapid Pace 41.
- For those five the date is a photo date. **They never filed paperwork at all, so they get template 2a, "never used it", not 2b.**

**Never quote a date taken from the combined signal.** Only quote a date if it came from a real paperwork upload. This is the same error that got gap 3 withdrawn, caught before sending this time.

### 2a. Never used it

Haskins Premier Logistics $1,217, Prime Pace Logistics $300, **plus the five reassigned above**: FKG Logistics $1,195, Blue Heron $945, OneLove Logistics $943, Rapid Pace Delivery $639, KJ Logistics $324.

> **Subject: Where do you keep driver licences and expiration dates?**
>
> Hi [First name],
>
> You are running schedules and messaging out of Hera every day. The piece you keep somewhere else is driver paperwork, licences, insurance, and the expiration dates that come with them.
>
> Most operators I talk to have this in a filing cabinet or a shared drive, and it works until an expiration is missed or Amazon asks for something on short notice. I would like to hear how you handle it, and whether that is a problem you actually have.
>
> 15 minutes [this week / week of [MM-DD-YYYY]]?
>
> [Sender name]
> Hera Solutions

### 2b. Used it and stopped

**Use this ONLY where the lapse is real paperwork, and do not name a date otherwise.** Timestamp Logistics (130d), Waymaker Enterprises (133d), Aquino Logistics (840d), Elite OnPoint (182d), RBHJAX Consulting (129d), The Pierce Group (382d).

**FKG, Blue Heron, OneLove, Rapid Pace and KJ move to 2a.** Their flag was a lapsed vehicle photo log; they have never filed paperwork.

> **Subject: Driver paperwork stopped coming into Hera around [MM-DD-YYYY]**
>
> Hi [First name],
>
> You are in Hera daily and running schedules, so nothing here is a concern about your account.
>
> The one thing that stopped is driver paperwork. Your last document upload was around [MM-DD-YYYY]. If your documents moved somewhere else, that is fine and I would like to know where. If uploading them was slow or awkward, I would rather hear that, because it is the kind of thing we can change.
>
> 15 minutes [this week / week of [MM-DD-YYYY]]?
>
> [Sender name]
> Hera Solutions

**Aquino Logistics at 840 days and Elite OnPoint at 182:** use "a while back" instead of the date, same reason as 1b.

---

## Gap 3: WITHDRAWN 08-04-2026. Do not send.

**7 accounts, $6,240/mo. This template was based on a signal that does not mean what it says, and sending it would be plainly wrong to the customer's face.**

The gap came from `StaffStatus`, a transition log. It said nobody had been marked as joining or leaving for 41 to 179 days. The **billed driver count from `InvoiceLineItem.activeStaff` says otherwise**, and it is the number we actually invoice:

| Account | Drivers | `StaffStatus` said | Count actually last changed |
|---|---|---|---|
| Town and Country Couriers | 201 | 179 days stale | **2 days ago** |
| South Islander Xpress | 118 | never | **1 day ago** |
| Holy Ship | 105 | 41 days stale | **5 days ago** |
| Josken Solutions | 101 | 63 days stale | **8 days ago** |
| OTW Delivery | 78 | 50 days stale | **6 days ago** |
| Boxes, Boxes & Boxes | 69 | 45 days stale | **6 days ago** |
| Tokeyi Logistics | 66 | 83 days stale | **3 days ago** |

**All seven are maintaining their rosters.** They do it in a way that writes no status transition, most likely creating and removing staff records directly rather than moving anyone through the Onboarding to Active path. Telling an operator with 201 drivers that their list looks stale, when they updated it on Sunday, destroys the credibility of every other thing we say.

**Across the book the signal is wrong half the time:** of 30 accounts it calls stale, 15 had a driver count move within 30 days and 10 within 8 days.

**Replacement, if this conversation is still wanted:** trigger on the billed driver count being unchanged 30+ days AND the account being billed per driver. On 08-04-2026 that is a completely different and much smaller list, and the honest subject line is about over-billing rather than housekeeping. See `../adoption-conversation.md`, "All three rosters are frozen."

## Text variant

Use only where a mobile number exists on the Zoho contact. One message, no follow-up text.

> Hi [First name], [Sender name] at Hera. Quick question, not a support issue: you use Hera daily but handle [driver schedules / driver paperwork] somewhere else. I want to understand why rather than assume. Any chance you have 15 minutes this week?

---

## What to log on the task

| Field | What goes in it |
|---|---|
| `Contact Outcome` | Reached, left message, no answer, declined to talk, rescheduled |
| `Blocker` | Why they do not use it. **The single most valuable field on this task** |
| `Customer Quote` | Their words, not a paraphrase |
| `Ask Made` | The 15 minutes, and whether they took it |
| `Next Action` | Almost always "None, close" or "Book demo" |

**These fields are in the FULL task record, not the popup.** The popup carries only Subject, Priority, Due Date, Status, Related To and Owner. Open the record itself.

**Do not touch Notes.** Standing rule.

---

## 8 accounts these do not cover

All eight have two gaps at once rather than a gap outside the set: four are schedules plus the withdrawn driver-list signal, three are schedules plus paperwork, one is paperwork plus driver list.

**With gap 3 withdrawn, five of the eight collapse into gap 1 or gap 2** and can use those templates directly, since the driver-list half of their flag is unreliable. Open with the schedules or paperwork gap and ignore the other.

**Two gaps is the boundary of this tier.** A third would make it 3-of-4 dark, which is RISK, and it would not be in this list.

## Open question, replacing the one gap 3 raised

The withdrawn gap 3 needed a commercial decision, because telling a customer their roster was stale invited them to deactivate drivers and cut their own invoice. **That question is now moot in this file** and has moved to the RISK call, where the frozen-roster finding lives and where it is a real over-billing issue rather than housekeeping.

**What remains open here is smaller:** gaps 1 and 2 need a writing approval only. Neither has a revenue consequence, neither depends on an unratified outcome catalog, and both can be sent as soon as the wording is agreed.
