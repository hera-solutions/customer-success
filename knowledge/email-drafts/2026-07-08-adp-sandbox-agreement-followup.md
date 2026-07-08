# Follow-up to Tom Lombardi (ADP): request DocuSign of sandbox agreement

**From:** John
**Date:** 2026-07-08
**Thread:** Re: ADP Follow Up - Developer Dashboard / Sandbox Agreement
**To:** Thomas.Lombardi@adp.com (Tom, ADP Key Account Executive - Amazon)
**Cc:** matthew@hera.app, Jessica.Moody@adp.com
**Channel:** Email
**Status:** Sent 2026-07-08

## Background

- Tom sent the sandbox agreement and API documentation to Matthew on 2026-06-29.
- John's July 2 reply committed to a "next week or so" turnaround and asked about sandbox provisioning speed.
- **Middleware question considered but set aside.** After Bindbee's Sakshi said Bindbee runs ~200 active ADP connectors without a signed ADP agreement, we drafted a pushback to Tom asking whether Hera specifically needs to sign given Bindbee's middleware role. That draft was set aside after Andy Rogers reviewed the agreement and cleared it: standard sandbox doc, $10 liability cap, no IP claim on what Hera builds, standard confidentiality clauses. Signing became the faster and lower-risk path than debating whether we needed to.
- This email is the "ready to sign" follow-up.

## Sent email

**Subject:** Re: ADP Follow Up - Developer Dashboard / Sandbox Agreement
**To:** Thomas.Lombardi@adp.com
**Cc:** matthew@hera.app, Jessica.Moody@adp.com

Hi Tom,

Following up on my note from last week. We've wrapped the internal initiative I mentioned and reviewed the sandbox agreement on our side. It looks in order, and we're ready to move forward on signing.

Whenever you're ready, please send over the DocuSign version of the agreement. Either myself (john@hera.app) or Matthew Goldman (matthew@hera.app) can sign on Hera's behalf.

One question before we get started: does the sandbox come pre-populated with employee/test data we can work against, or do we need to manually load our own data to start testing?

Thanks again!

Best,
John

## Why this is structured this way

- **Ties back to the July 2 pace signal.** "Wrapped the internal initiative I mentioned" closes the loop on the prior commitment without over-explaining.
- **No mention of the middleware question.** Raising it now would muddy a clean "send the DocuSign" ask. If it becomes relevant later, we can address it then.
- **Two signers named, Tom picks.** Cleaner than making him ask who should receive the DocuSign.
- **Data question is operational, not technical.** Tom is a Key Account Executive, not a dev — plain-language framing gets the fastest useful answer.
- **No technical call requested.** Andy has cleared the doc; the call was overkill.
- **No em dashes. No filler.**

## Andy Rogers' review of the sandbox agreement (for the record)

Andy's verdict on the document itself, worth keeping durable:

> No red flags in terms of IP exposure. This doc is really just ADP protecting their IP from us and prevents us from trying to "reverse engineer" their systems. Nothing in here makes a claim that ADP owns what we build with their APIs. There are some confidentiality clauses, which makes sense. A liability cap is set at $10. I struggle to see a world where access to a Free Sandbox can cause Hera damage, but if that does happen, they would pay us $10. All in all, pretty standard sandbox access doc.

Useful reference if a customer or partner ever asks whether we've reviewed ADP's sandbox terms, or if a similar sandbox agreement comes up with another payroll provider down the line.

## Follow-up to consider

- If Tom returns a DocuSign quickly, decide same-day whether John or Matthew signs. Default assumption: John, since he's running point on the thread.
- Track sandbox provisioning turnaround so we can set realistic expectations with beta customers (Mike, MBB, and others) on when actual end-to-end testing resumes.
- If the sandbox is NOT pre-populated, we need a data-loading plan before we can run meaningful end-to-end tests. Loop Andy in early on that.
- Update the ADP beta tracker: sandbox agreement requested via DocuSign, signature pending.
- Once signed and sandbox is provisioned, revisit whether the earlier middleware question is worth raising with Bindbee's Sakshi (as a "how does this actually work in practice" question, not a legal one).
