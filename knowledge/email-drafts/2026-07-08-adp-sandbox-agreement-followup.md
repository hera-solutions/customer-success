# Follow-up to Tom Lombardi (ADP): middleware question on sandbox agreement

**From:** John
**Date:** 2026-07-08
**Thread:** Re: ADP Follow Up - Developer Dashboard / Sandbox Agreement
**To:** Thomas.Lombardi@adp.com (Tom, ADP Key Account Executive - Amazon)
**Cc:** matthew@hera.app, Jessica.Moody@adp.com
**Channel:** Email
**Status:** Draft, ready for review

## Background

- Tom sent the sandbox agreement and API documentation to Matthew on 2026-06-29.
- John replied on 2026-07-02: thanked Tom, said the API docs look aligned with what we've been working with, floated a rough "next week or so" timeline, and asked about sandbox provisioning turnaround.
- Since then: Bindbee's CSM Sakshi (2026-07-03) said Bindbee runs ~200 active ADP connectors and has never signed an ADP agreement themselves. That is Bindbee's story, not ours to repeat to ADP.
- Matthew's direction (2026-07-08): reach out to Tom directly rather than escalate to Jessica Moody (who is already CC'd on the ADP side).
- This is a follow-up on the same thread, not a first-touch.

## Draft email

**Subject:** Re: ADP Follow Up - Developer Dashboard / Sandbox Agreement
**To:** Thomas.Lombardi@adp.com
**Cc:** matthew@hera.app, Jessica.Moody@adp.com

Hi Tom,

Following up on my note from last week.

One thing we want to make sure we get right before signing. Our ADP WorkforceNow integration is being built through Bindbee, a unified HRIS integration platform we've contracted with as our middleware. In practice, Bindbee is the party actually accessing your APIs on our behalf.

Given that setup, a couple of questions:

1. Does the sandbox agreement still need to be signed by Hera, or does an integration through Bindbee follow a different path on your end?
2. If Hera does need to sign directly, is anything specific about a middleware setup worth factoring into the sandbox environment or the eventual production connection?

We're happy to sign if that's the right path. I just want to make sure we're not putting something in place that's already covered on your side.

The technical call your team offered would be helpful either way. If you can send over a couple of times that work, I'll have Andy Rogers, our Technical Lead, on with me. Andy can go deeper on the Bindbee configuration.

Thanks,
John

## Why this is structured this way

- **Opens as a follow-up, not a first message.** "Following up on my note from last week" acknowledges the July 2 reply and the "next week or so" pace signal already on the record.
- **Explains why the delay before signing is worth it.** The middleware question is a substantive reason for the pause, not a stall.
- **Bindbee framed as a business fact, not a defense.** "We've contracted with Bindbee as our middleware. In practice, Bindbee is the party actually accessing your APIs on our behalf." Neutral and specific.
- **Does not repeat Bindbee's "we've never signed one" claim.** Not our claim to make. If ADP disagrees with Bindbee's read, we don't want to be caught vouching for it.
- **Two specific questions.** Q1 gives Tom a clear answer to give. Q2 protects us if the answer to Q1 is "yes, sign it."
- **"Happy to sign if that's the right path."** Signals no attempt to duck the agreement.
- **Technical call accepted.** Tom offered it in his 6/29 note; John hadn't accepted in the 7/2 reply. Accepting now moves things forward regardless of which answer we get on the agreement.
- **Andy Rogers named correctly.** Fixes the "Andy Mack" error from the July 2 Bindbee reply.
- **No em dashes. No filler. No mention of Jessica** — she stays on the Cc as she was, but escalation to her is not signaled from this email per Matthew's direction.

## Things to confirm before sending

- Whether Matthew wants to stay on Cc or drop off now that John is running point.
- Whether Jessica Moody should stay on Cc. She was already on Tom's original thread, so keeping her there is the default. Removing her would be an active step, and Matthew's guidance was to keep this at Tom's level rather than escalate.
- Whether Andy is the right technical lead to name for the call. He's been the technical lead on the Bindbee thread already, so this is consistent.

## Things NOT to do in this reply

- Don't cite Bindbee's claim that they've never signed an ADP agreement. Bindbee's story, not ours.
- Don't imply ADP got the ask wrong. They're doing what they should — protecting API access with confidentiality and IP terms.
- Don't undo the "next week or so" timeline signal from the July 2 reply without a real reason. This question is the reason.
- Don't over-explain Bindbee. "Unified HRIS integration platform" is enough.
- Don't ask Jessica-level legal questions in this email. If Tom's response introduces material legal exposure, that's when we bring Jessica (or Hera's own counsel) in.

## Follow-up to consider after sending

- If Tom confirms Hera must sign, forward the agreement to Sakshi (per her offer) for Bindbee's review before we sign.
- If Tom confirms Bindbee's setup covers it, capture that in writing in the reply chain and note the outcome in the ADP beta tracker and the Bindbee project file.
- Diary reminder to nudge Tom at 3-4 business days if no reply.
- If the technical call gets scheduled quickly, prep an internal talking-points doc with Andy so the call is efficient and doesn't drift into "let me get back to you on that."
