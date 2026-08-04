# Rollout readiness: what is missing before the first customer call

**Status 08-04-2026: NOT READY, but the two structural blockers are cleared. No customer contact authorised.**

Original assessment set 08-04-2026 after the user said "there is still a substantial amount of setup required before moving and implementing the plan." Updated the same day as work landed.

---

## CLEARED

### ~~Blocker 1: nothing surfaces an at-risk account to a human~~ DONE

The detection, weighting, lifecycle and generation all exist now.

- **Trigger:** dark 30 days on 3 or more of the four heartbeat signals: human-sent message 6.8, document upload 4.5, staffed roster 4.3, and **roster maintained**, measured as the billed driver count not moving. Weights are churn lift, not judgment.
- **The 4th heartbeat was replaced on 08-04-2026 and the weight has NOT been re-derived.** It used to be measured with `StaffStatus`, which was wrong half the time: of 30 accounts it called stale, 15 had a billed driver count that moved inside 30 days. It now comes from `InvoiceLineItem.activeStaff`. The 3-of-4 rule counts signals rather than summing weights, so the rule is unaffected, but **re-run `signal_weights.py` before calling the weight evidenced.**
- **Generator:** `analysis/tenant-engagement/generate_tasks.py`, dry-run by default, `--write` required.
- **Output on 08-04-2026:** 3 RISK to John, 34 ENGAGE to John, 16 Confirm-or-close to Matthew. 53 tasks, down from 61 once the bad roster signal was removed.
- **The five Zoho `Last_Active1` rules still need turning off**, which is Matthew's action. They fired six tasks on 08-04-2026 and not one was for a paying at-risk customer.

### ~~Blocker 2: the adoption conversation has nowhere to be recorded~~ DONE

Eight custom fields on Zoho Tasks, tested with a round trip: Job Named, Blocker, Ask Made, Outcome Evidence, Customer Quote, Contact Outcome, Next Action. Coverage is a single query, since automation tasks never populate Contact Outcome.

### ~~Blocker 4: no owner and no cadence~~ MOSTLY DONE

Assignment is John for every generated task, reassigning to Lizz at his discretion. Cadence is a Mon-Fri scheduled routine with weekend activity rolling into Monday. RISK is monthly with a business-day ladder on days 1, 3, 5, 8 and escalation on day 10. ENGAGE is quarterly, single outreach.

**Still missing:** Abram's carve-out book is undefined, and no account may be assigned to him until it is, because his compensation depends on which accounts he holds.

---

## STILL OPEN

### Blocker 3: the conversation format is rewritten, awaiting one read

**Rewritten 08-04-2026** against the decisions actually agreed: heartbeat tiers, the business-day ladder, the pivot table, seven Zoho fields, MM-DD-YYYY dates. The superseded 62-account cohort and the scorecard cohort are gone, and the broken `../` links to the catalog and AMP files are fixed.

**Two substantive changes, not just tidying:**

- **All three RISK accounts are dark on all four heartbeats**, so the old rule "open with what they are doing" is impossible. Replaced with an opener on the customer's operation.
- **The old instruction to "ask straight out whether they are still using Hera" is withdrawn.** Asked of a growing account paying $931/mo, that question invites a cancellation. It would have caused the outcome it was written to prevent.

**Needs one read from John, not a rebuild.** Still marked DRAFT, still referenced by no skill.

### Blocker 5: seven config fields still unset

QBR format, success plan format, renewal conversation style, and the CS playbook, QBR, success plan and stakeholder map template sources. Open by non-decision since 07-30-2026. Nothing is blocked today, but a skill asked for a QBR will print `[NOT SET]` into a customer-facing draft.

### Blocker 6: the outcome catalog cannot be used with customers

`provisional-1.0`, unratified, **barred from customer-facing material until Matthew signs it off** at the weekly management meeting. The adoption conversation depends on it for the six jobs.

### Blocker 7: two plugins have no configuration at all

`onboarding` 1.0.1 and `cs-ops` 1.0.1, no `CLAUDE.md` for either. Roughly 20 skills and three scheduled agents would run with no profile. **Largest remaining gap in the install.** When it is done, take the onboarding milestone framework out of the existing Zoho new-deal sequence (Check In 1 at +27 days, Check In 2 at +37, Comprehensive Follow Up at +40, Mid Trial Review at +47, Product Fruits at +53) rather than the plugin's generic M1-M5 template.

### New, from building the generator

- **ENGAGE message templates, four live and two withdrawn.** No driver schedules (14 accounts, $15,374/mo) and no driver paperwork (12, $8,728) are drafted and need a writing approval only. **The driver-list gap (7 accounts, $6,240/mo) is WITHDRAWN**: all seven had changed their billed driver count within 8 days, so the email would have been wrong to their face.
- **Two accounts are probably being over-billed, and the largest is not on the urgent list.** Last Mile Logistics, $1,219/mo, 140 drivers, roster frozen 34 days after 75 changes in the prior year. TPE Logistics, $931/mo, 115 drivers, frozen 50 days. Both billed per driver. Needs a decision from Matthew on whether CS raises it or he does.
- **Where Matthew's escalation flow records anything.** The `Cases` module is permission-denied to the CS connector. Ask him. If his flow lives outside Zoho, escalated accounts have no CRM record at all.
- ~~**Double Iron Car Care: 18 associates, $25/mo.**~~ **RESOLVED 08-04-2026. Nothing was wrong.** They are on a flat monthly fee: `flatMonthlyBillingAmount` 25, `variableTotal` 0, and every per-driver line charge 0. 11 accounts are not billed per driver, which also means a frozen roster costs them nothing.

---

## Not blockers, but they will bite

**Four revenue totals that do not reconcile.** $199,177 invoiced for July, $190,594 collected, $193,080 in the CEO deck, $187,274 in the health report. All defensible, all different populations. **Do not quote any of them externally until reconciled.**

**Do not quote the signal lift figures outside the team either.** The comparison is structurally biased: survivors measured today, churns at their churn date. The ranking survives it, the magnitudes do not.

**The AMP per-member rate is unknown**, so that opportunity cannot be sized. 807 active associates across ten dark accounts is the only firm number.

**Nobody has confirmed what happens when a trial lapses.** Extension is manual and monthly, 46 live AMP customers behind it.

**~~Debt disappears when an account is churned~~ MITIGATED.** The Confirm-or-close task now carries the last two invoices and any balance, and requires a note before closing. $2,257 already went invisible this way (PacTrack $1,411, Pure Logistics $846) and still needs a chase-or-write-off decision from Matthew.

**627 active associates bill nothing** across MBB 321 (deliberate), Outlaw 195 and Spears 111 (credits granted without CS involvement). Worth Matthew seeing the three together.

**Two connectors that would help are unauthenticated.** LogRocket, the best adoption diagnostic available since per-company session URLs already sit in Intercom. Google Calendar, for cadence. Stripe is now connected.

**No customer call recordings exist.** Zoom holds only internal meetings, so there is no baseline for what these conversations sound like.
