# Hera + Intercom: orientation notes

Snapshot of Hera's product, customer base, and support patterns as observed in the connected Intercom workspace (`baat8a8r`) on 2026-04-30. Refresh this file when conventions shift.

## What Hera is

Hera is a SaaS platform built for **Amazon Delivery Service Partners (DSPs)** — the third-party companies that contract with Amazon to operate last-mile delivery stations. The product gives a DSP owner / operations team a single tool for the daily ops loop around drivers and vehicles.

Domain: `hera.app`. Help center: `support.hera.app`. Support inbox: `support@hera.app`.

Public-facing team identifiers seen in conversations:
- **Matthew Goldman**, Founder & CEO (`matthew@hera.app`) — also closes prospect calls personally; signs as "Proud USMC Veteran".
- **John @ Hera** (`john@hera.app`) — handles account creation / data ingestion.
- **Hera Support** (`support@hera.app`) — front-line CS, triage, training scheduling.
- **Fin AI Agent** ("Hera AI Agent") — first-line bot on the Intercom messenger.

## Product surface (from help-center articles)

Articles span both published and draft state. Functional areas:

- **Daily Roster.** Core operational view; how/why to use it, roster status, checklists & templates, messaging company devices and associates, scheduled messages, exports.
- **Vehicle Photo Log.** Start-of-shift inspection photos; AI-assisted verification is in draft. Includes troubleshooting (e.g., "Not Enough Memory" when uploading photos).
- **Performance data ingestion.** Daily/weekly uploads from Amazon AMZL, Netradyne, eMentor; Proper Parking Sequence (PPS); Customer Delivery Negative Feedback.
- **Inventory Management.** Orders, item types, inventory list, dashboard.
- **Coaching & counseling.** Create/manage counseling records, automated coaching, OSHA 301 logs.
- **Associate management.** Display name, statuses, custom roster statuses, rankings, offboarding, expiring driver's-license report.
- **Vehicle management.** Importing/adding vehicles, photo-log requirements, labels.
- **Devices.** Wireless support devices, importing devices, messaging company devices.
- **Hera AI Chat (draft).** Natural-language Q&A scoped to data synced via the Hera Amazon plugin.
- **Integrations.** Hera Amazon plugin, Paycom, ADP, Miradore (MDM API key flow).
- **Admin.** Roles, user permissions, company settings, second-station support, custom lists, labels, global search, notifications.
- **Security articles.** "Why Shared Logins Are a Serious Risk", "Can I Store Sensitive HR Data in Hera?"

## Customer base

- **646 companies** in Intercom (11 pages × 60). Effectively all Amazon DSPs — every record carries a `dsp_short_code` and counts of `active_vehicles` and `active_das` (delivery associates).
- Fleet sizes in the page-1 sample range roughly **25–130 vehicles** and **50–270 associates** per DSP.
- Lifetime invoiced spans **$0 to ~$68k** per DSP; `months_invoiced` ranges 2 to 63+.

### Customer-status mix (page 1 sample, 60 companies)

The status distribution is striking and worth flagging:

- **"Unpaid - Grace Period"** is the dominant status — ~50 of 60 on the first page.
- A handful of **"Active - Bundle"** customers (e.g., WZB Logistics, Bay Tire Mobile, SkyHook 2, G Logistics, Pinpoint Logistics, Add Logistics).
- Some plain **"Unpaid"** (no grace period) — e.g., The Last Mile Company, Marathon Logistics, Apcore Logistics, Active Transportation Services.
- Many companies carry a **"To Be Archived"** tag.
- Some companies show `trial_expiration_date` years in the past (2022–2024) yet `months_invoiced` continues climbing — suggests the data model carries trial-era timestamps even after a customer is on a paid bundle, or that "Grace Period" is the catch-all label for anything not currently paying.

If the goal is collections / win-back / churn-classification work, the company list is a good first place to dig — that distribution looks like it's hiding signal.

## Support volume and shape

Pulled compact samples on 2026-04-30:

- **~2,325 closed conversations** (93 pages × 25). **~125 open** (5 pages × 25).
- Of a 50-conversation sample of recently closed: **34 had Fin AI Agent participation, 16 did not.** Of AI-touched conversations: **38 "Assumed Resolution", 6 "Confirmed Resolution", 6 "Escalated"** — Fin is doing real first-line deflection but most resolutions are inferred, not confirmed.
- Active ticket types: **Onboarding** (🚀), **Bug Report**, **Billing Issue**, **General**.
- Inbox noise: recurring `mailer-daemon@amazonses.com` bounces and `notification@zohocrm.com` duplicate-lead pings — worth filtering out of triage queues if not already.

### Topic clusters (from AI-generated conversation titles, 100 sampled)

- **Daily roster operations:** rostering issues, roster date errors, duplicate roster messages, dispatcher checklist access, daily roster date error.
- **Counseling / coaching:** counseling creation issue, counseling access issue, sent counseling deletion, remove OSHA 301.
- **Messaging:** send group text, schedule message feature, chat message export, export all messages, invalid phone number, change driver phone number.
- **Scorecards / performance:** upload daily performance, upload netradyne data, update Hera scorecard, duplicate scorecard entry, Hera performance issue.
- **Vehicles:** assign checklists to vehicles, delete returned vehicle, associate vehicle assignment.
- **Account / access:** login loop, disable account unauthorized, password reset (seen in sampled email subjects), app not working, app issues report, sites down, site troubles, site issue with associates visibility.
- **Onboarding:** onboarding list error, training checklist request, custom spreadsheet template request, edit company time zone, driver app rollout.
- **Billing / lifecycle:** cancel or downgrade plan, add credit card, careers email inquiry.
- **Devices:** enable wireless support.

## Onboarding workflow (observed pattern)

Reconstructed from a representative onboarding conversation:

1. Prospect responds to "Hera Solutions | Ready To Discover the Difference?" outbound email or otherwise lands in the inbox.
2. Hera Support points them to [Gather Your Onboarding Data](https://support.hera.app/en/articles/10139790-gather-your-onboarding-data).
3. Customer sends three files: Vehicles export, Associates export (unedited from Amazon — common issue is customers trimming columns), payroll file from their HR vendor.
4. Matthew Goldman frequently jumps in personally on a quick call to align expectations.
5. Training is **split into two sessions** by deliberate design: a kick-off call, then a comprehensive session two-to-three weeks later once the team has hands-on time. This is intentional pedagogy worth preserving in CS playbooks.

## Things to verify before acting on this snapshot

- The page-1 status distribution is suggestive but not the whole picture — pull all 11 pages before drawing conclusions about the paid/unpaid mix or churn risk.
- "AI Title" fields are AI-generated summaries, not ground-truth ticket categorizations; use as a topic signal, not a metric.
- Fin AI Agent "Assumed Resolution" is not a confirmed-by-customer outcome; it likely overstates true deflection rate.
- The `customer_status` attribute language ("Unpaid - Grace Period", "Active - Bundle", "Unpaid") and the `To Be Archived` tag should be reconciled with whatever lives in Zoho CRM (each company carries a `Company Zoho CRM ID`) before reading the data as billing truth.
