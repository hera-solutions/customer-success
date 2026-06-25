# Reply: Integrated Logistics Solutions — associate data pull (file incomplete)

**From:** John
**Date:** 2026-05-13
**Customer:** [Contact First Name], Integrated Logistics Solutions (ILS)
**Account status:** Onboarding
**Channel:** Email
**Status:** Draft, ready to send

## Background

ILS sent over their associate files for onboarding, but the data is incomplete (missing required fields needed to build the Hera Staff import). We are also late getting back to her, so the reply needs to own the delay before walking through the fix.

The article she should be working from is [Gather Your Onboarding Data](https://support.hera.app/en/articles/10139790-gather-your-onboarding-data). Her associate data should come from two places:

1. Her HRIS (ADP or Paycom) — name, email, phone, DOB, gender, hire date.
2. Amazon Logistics — `TransporterID` and `Qualifications`.

Per John's note, offer a 10-15 minute Zoom walkthrough as a white-glove option if she'd rather do this with us live.

## Draft reply

**Subject:** Wrapping up your ILS onboarding — associate data and a fast option

Hi [Contact First Name],

First, I owe you an apology for the slow turnaround on this. I should have come back to you sooner, and I'm sorry for the wait.

The associate files you sent over are a great start, but they're missing a few fields we need to finish setting up your team in Hera. To get everything in, we actually need data from two places: your payroll/HR system, and Amazon Logistics. The article that walks through both is here:

[Gather Your Onboarding Data](https://support.hera.app/en/articles/10139790-gather-your-onboarding-data)

The short version:

**From ADP or Paycom (whichever you use):**

Pull a report on Active employees with these fields:

- Legal First Name, Legal Last Name
- Personal Email (and Work Email if available)
- Phone (mobile preferred)
- Birth Date
- Gender
- Hire Date

Export as CSV.

**From Amazon Logistics:**

Go to Administration > Associates > My Associates and download. We need this file so we can pull two columns: `TransporterID` and `Qualifications`. Please send it to us without editing those two columns.

Once we have both files, we can match them up on our end and finish your import.

**If you'd rather we just do this live:** Happy to jump on a 10-15 minute Zoom with you and walk through pulling both files together. That's usually the fastest path. Let me know a time that works and I'll send an invite.

Either way, thanks for your patience on this. Looking forward to getting you up and running.

Best,
John

## Why this is structured this way

- **Owns the delay in the opening sentence.** Not buried, not generic ("sorry for the inconvenience"). A real apology with no excuse.
- **Frames the incomplete file positively.** "A great start, but missing a few fields" is honest without making her feel like she did the wrong thing.
- **Explains the two-source requirement clearly.** This is the part she most likely didn't realize. Most customers think one HRIS export = staff data, but Hera needs the AMZL TransporterID + Qualifications layered on top.
- **Gives both the link and the inline summary.** Customers don't always click. The inline summary lets her act without leaving the email.
- **Names the exact fields needed.** Reduces back-and-forth if she chooses to pull them herself.
- **Offers the Zoom path as an equal option, not a fallback.** Framing it as "the fastest path" makes it a strong choice for a busy operator.
- **No em dashes. No "I hope this finds you well." No "per our records." No "as soon as possible."**

## Things NOT to do in this reply

- Don't list every Hera Staff field she'll eventually need (Gas Card PIN, DL Expiration, MVR, Hourly Status). She doesn't need those to start the import, and listing them now will overwhelm her. We can ask for them later if the customer wants those tracked in Hera.
- Don't tell her exactly what was missing field-by-field unless John fills in those specifics. The current draft sidesteps it by sending her the full correct pull list, which works whether one thing or five things were missing.
- Don't promise a specific turnaround time on our end once she sends the corrected files. Stay honest: we'll move fast, but not on a clock she can hold us to.
- Don't apologize twice. Once at the top, once briefly at the close. That's enough.

## Placeholders to fill before sending

- `[Contact First Name]` — her first name.
- Optional: if you know which HRIS she's on (ADP vs Paycom), drop the other option from the "From ADP or Paycom" line for a tighter read.
- Optional: if you want to pre-empt her question about timing, add a line near the close like "Once we have both files, we usually get the import done within [X business days]."

## Follow-up to consider after sending

- If she chooses Zoom, block 20 minutes on the calendar to allow for tech friction.
- After the corrected files come in, run them through the conversion process (HRIS + AMZL Associates join → Hera Staff template) and flag any remaining gaps before importing.
- We still need her Devices source and clarity on Authorized To Drive logic. Those are separate threads from this one — don't bundle them here.
