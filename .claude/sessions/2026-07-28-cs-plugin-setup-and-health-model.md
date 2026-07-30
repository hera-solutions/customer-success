# CS plugin setup, health model build, and full data audit

## 1. Date, time, and scope

**28 July 2026 15:55 through 30 July 2026 09:29.** Roughly 42 hours elapsed across one continuous session.

**Trigger.** John installed three plugins from the `claude-for-customer-success` marketplace (`csm`, `onboarding`, `cs-ops`) and ran `/csm:cold-start-interview` to configure the CSM plugin.

**What it turned into.** The interview surfaced that Hera's production data could answer the configuration questions directly rather than by self-report, so the session became: a full data analysis of the CS book, the design and implementation of a two-axis health model, a shared scorer committed to this repo, two published artifacts for internal and CEO audiences, and a full audit that found five measurement bugs in my own work and corrected every published figure.

Three plugins were installed. Only `csm` was configured. `onboarding` and `cs-ops` remain unconfigured.

---

## 2. What changed

### New: `analysis/cs-health-baseline-2026-07/`

- **`findings.md`** (598 lines). The baseline analysis. Went through four revisions during the session as errors were found. Contains a revision history at the top, plain-language glossary, book composition, retention decomposition, churn mining, the tested-and-rejected signals, the proposed band definitions, and a data-quality register.
- **`.gitignore`** excluding `data/`. The cached DynamoDB pulls are 3.5 MB and reproducible, and they hold per-tenant customer data.
- **`data/`** (gitignored, 11 JSON files). Cached query output preserved out of `/tmp`, which was the only copy at one point and would have been lost on reboot.

### New: `analysis/tenant-engagement/`

Deliberately created at the paths the daily-review skill already referenced but which had never existed in the repo.

- **`lib_hera.py`**. Read-only boto3 session pinned to the `hera-readonly` profile, table-name helper for the `-zeobggbnyva4padyiddojnmnqy-production` suffix, DynamoDB deserialisers, and every field trap centralised as a named function (`parse_ts`, `roster_date`, `is_paying`, `ever_paid`, `can_roster`, `base_customer_name`). Exits with the `aws sso login` instruction rather than a boto3 traceback when the token expires.
- **`three_signals.py`**. Pulls all signals per tenant with a 12-worker thread pool. Writes `data/signals-<date>.json`.
- **`classify.py`**. Reads the cached signal file and assigns one triage bucket per tenant, then writes the weekly markdown report. Deliberately separated from the pull so threshold changes re-run instantly with zero API calls.
- **`README.md`**. How to run, why two axes, bucket definitions, signal sources with index names, field traps, known limitations.
- **`reports/2026-07-29-cs-health.md`** and **`reports/2026-07-30-cs-health.md`**. The 29 July report contains pre-audit figures and was kept deliberately as a record.
- **`.gitignore`** excluding `data/` and `__pycache__/`.

### New: `analysis/cs-health-weekly/`

- **`skill/SKILL.md`**. The `cs-health-weekly` skill. Symlinked from `.claude/skills/cs-health-weekly/SKILL.md`, matching how `logrocket-daily-review` is wired.
- **`finalized.html`**. Internal summary page. Published as a private artifact.
- **`exec-brief.html`**. 13-slide deck for the CEO conversation. Published as a private artifact. Rewritten three times: once for the churn and projection additions, once to switch from ARR to monthly revenue, once to remove the cents analogy and break out churn reasons.

### Modified: `analysis/logrocket-error-investigation/skill/SKILL.md`

Part 4 was reduced from a full classification spec (137 lines) to a tripwire (63 lines) that reads the newest weekly report, flags if it is stale, and lists only tenants newly gone dark. It no longer classifies, computes revenue at risk, or recommends saves.

Also removed **two stale generations of spec** from that file. The top-of-file summary described a three-signal model with a pattern matrix, and further down the Section D output template still used an even older vocabulary (`TRULY_DARK`, `DARK_BUT_BILLABLE`, `ZERO_STAFF_BUT_LOGGING_IN`) from a prior version. Both contradicted the current model.

### Modified: `.gitignore`

`.claude/` was excluded on two lines. Replaced with `.claude/*` plus `!.claude/sessions/` so session logs commit while `settings.local.json` and `worktrees/` stay ignored. Git cannot re-include a path inside an excluded *directory*, which is why the pattern had to change from `.claude/` to `.claude/*`.

### Modified: plugin config (outside this repo)

`~/.claude/plugins/config/claude-for-customer-success/company-profile.md` and `csm/CLAUDE.md`. Written from scratch during the interview, then updated three times as figures were corrected.

### Commits

```
eeb6d20  Add CS health baseline analysis for July 2026
92f3851  Revise CS health baseline: billing is per-active-driver
601bab3  Revise CS health baseline again: verify pricing at $9 per active associate
9b9e184  Revise CS health baseline to a two-axis model
aa480b3  Add shared CS health scorer, make it single-source
83daeb8  Add finalized CS health summary as a branded artifact page
4cc4fa1  Add executive brief deck for the CEO conversation
b050065  Add twelve-month churn breakdown and July invoice projection to exec brief
d0e154d  Fix five measurement bugs found in audit; re-verify all data
99889ee  Report in monthly revenue; add plain-language explanations throughout
15fe679  Rework exec brief: whole dollars, churn broken out, explanations in the body
```

---

## 3. What was discussed but not changed

- **RDS access.** Established that 11 of 17 tables I depend on are synced to the Aurora MySQL mirror via DynamoDB streams and Glue, but the five most important ones are not (`Invoice`, `InvoiceLineItem`, `StaffStatus`, `DailyRoster`, `Message`). `Route` is synced, which is the only expensive query. Decided to stay entirely on DynamoDB. No read-only MySQL user was created.
- **Ultraplan session.** A plan was sent to Ultraplan for remote refinement. It timed out after 90 minutes without approval. Its one genuinely useful contribution was catching that having figures in both `findings.md` and a separate HTML viewer would drift, which led to dropping the viewer. Its other output was discarded because the remote container had no AWS CLI, no boto3 and no credentials, so it could not verify a single number.
- **The `onboarding` and `cs-ops` plugins.** Scoped but not configured. `cs-ops` is roughly 80% pre-fillable from the baseline work and needs only three answers. `onboarding` has the stronger business case because 29% of paid churn happens inside 12 months.
- **Onboarding funnel measurement.** Proposed measuring actual time-to-value from `Tenant` lifecycle fields against first-value events, to set targets from evidence rather than intuition. Not run.
- **Seasonality.** Repeatedly flagged as the one input that could move every threshold. John said peak season exists and he would supply detail later. Not yet supplied.
- **PDF output.** Considered and rejected. `reporting/pdf-generation-process.md` is scoped to Communication Exports and Personnel Records built from data exports, which is a different format.
- **Embedding Aglet Slab in the artifacts.** Rejected. Three weights at ~300 KB each would add roughly 800 KB of base64. `branding/brand-guidelines.md` explicitly sanctions a system slab-serif fallback, so the font stack names Aglet Slab first (picking it up if installed locally) and falls back.

---

## 4. Decisions made

| Decision | Alternatives | Why | Who |
|---|---|---|---|
| CS motion recorded as hybrid/segmented, segmented on **engagement state, not revenue** | Pure tech-touch, pure high-touch, ARR tiers | The book is flat: largest customer pays about 3x the median, top 20 hold 16% of revenue. Revenue tiers would create buckets that behave identically | Mutual; John asked to be talked through it first |
| **Two independent axes, never one blended health score** | Single band with weighted components | Tested: 6 of 15 declining accounts scored *above* the healthy average on engagement, the most engaged account was losing 15% of associates, the least engaged healthy account was growing 20% | Claude proposed, John approved |
| Count red flags rather than weight percentages | Weighted scoring (usage 40%, support 20%, etc.) | Weights are hard to explain, impossible to tune at this data volume, and produce a number nobody can reason about | Claude proposed, John approved |
| **Report monthly revenue, never annualised** | ARR, industry standard | Hera bills month to month with no contract. Annualising implies a commitment that does not exist and inflates every figure twelvefold | **John** |
| Whole dollars instead of a cents-on-the-dollar analogy | "We keep 96 cents on the dollar" | An abstraction on top of an abstraction. The dollar waterfall shows where the money actually went | **John** |
| Break out every churn reason individually | Group into Amazon / competitor / everything else | Lumping buried the reasons we can act on. Broken out, "did not find it useful" at $10,941/mo becomes the second-largest line | **John** |
| Explanations in the slide body, not sub-boxes | "In plain terms" callouts under each slide | Nothing to skip past, and Matthew reading alone gets the same thing as Matthew being presented to | **John** |
| Drop the associates-to-routes ratio from scoring | Keep as a scored factor | Cannot distinguish part-timers from incomplete route entry. The two healthiest large accounts sit at 5.4x and 5.5x while Whiterecon shows 23x from missing data | **John** |
| Weight the eight daily rostering actions rather than any-one-counts | Binary "did they touch it" | John's call. Attendance weighted 2 because it can only happen on the day itself | **John** |
| Under-10-associate rule: flag immediately but require 3 consecutive days | Single day, or a week | All 20 current cases have run 7+ days so nothing real is delayed, and 3 accounts dipped for one day and recovered. The rule prevents 3 false positives at no cost | Claude proposed, John had said both "consecutive days" and "flag right away", so this reconciles them |
| Stay on DynamoDB, no RDS | Hybrid using the RDS mirror for the synced tables | The mirror is VPN-only, has drifted silently before (HERA-8631), and does not carry the five tables that matter most. Cost is negligible either way at about $0.03 a run | **John** |
| Single shared scorer; daily Part 4 becomes a tripwire | Fix the bug in Part 4 only and keep two models; or fold everything into the daily skill | Two overlapping models would give contradictory answers | **John**, chose option A of three |
| Multi-site tenants roll up to one customer | Treat each tenant separately | John confirmed they are secondary sites of the same customer, some permanent, some temporary | **John** |
| Twelve-month churn measured on the last **full** month before the final stub | Final paid invoice; max of last 3; value at window start | 25 of 88 accounts have a partial stub final invoice. Using it understated the loss by $126,757/yr | Claude proposed after computing all four bases |
| Session log written per the existing convention, and `.gitignore` amended so it commits | Save to `.claude/sessions/` per convention and leave it untracked; or put it somewhere non-ignored | The convention names `.claude/sessions/` but that path was ignored, so following it literally meant the log never reached GitHub | Claude proposed |

**Decided by default:** the `csm` plugin's escalation SLAs, GRR/NRR targets, QBR format and outcome catalog were left as explicit `[NOT SET]` markers rather than given invented defaults. John deferred them; they were not skipped.

---

## 5. Technical details and implementation notes

### Environment

- **AWS account `530079012632`, region `us-east-2`**, SSO profile `hera-readonly`, read-only.
- DynamoDB table suffix: `-zeobggbnyva4padyiddojnmnqy-production`.
- SSO tokens expire every few hours. This happened four times during the session. Scripts now exit with the `aws sso login --profile hera-readonly` instruction.
- All 16 tables are `PAY_PER_REQUEST`, so scoring cannot throttle the production app and reads spread across 248 partition keys with no hot-partition risk.
- Read cost of a full scoring run: roughly 250,000 read request units, about **$0.03**.

### Billing model, verified

**$9.00 per active associate per month, charged as $0.30 per associate per day, billed one month in arrears.** July usage invoices on 1 August.

Verified from `InvoiceLineItem`, which holds one row per calendar day carrying that day's `activeStaff` and `bundleCost: 9`. Express Package System's June invoice, day 26: `activeStaff` 203, `bundleCostExt` 60.9, which is exactly 203 x 0.30. Closed invoices bill $8.963 to $9.042 per associate. 179 of 248 tenants bill within 5 cents of $9.00.

Module price list from the line items: bundle $9, standard $2, performance $3, rostering $1, staff $3, vehicles $1. A la carte sums to $10, so bundle is a 10% discount. Nine legacy customers still pay the module sum ($5 to $7).

**This was documented in `knowledge/billing-overview.md` line 9 the whole time.** I derived it from invoice line items across three revisions because I read `CLAUDE.md`, `brand-guidelines.md` and the GraphQL schema but never grepped `knowledge/` for billing. That single miss caused the wrong revenue figures in revisions 1 and 2.

### Indexes used

| Signal | Table | Index |
|---|---|---|
| Human-sent message | `Message` | `byGroup` (group + createdAt), time-bounded |
| Message read | `AuditLog` | `byTenantIDAndMutationName`, full pagination |
| Scorecard freshness | `CompanyScoreCard` | `byTenantByYearWeek` |
| Roster dates | `DailyRoster` | `byGroupAndNotesDate` |
| Staffed routes | `Route` | `gsi-RouteDailyRoster` |
| Active associates | `Staff` | `byGroupStatus` |
| Daily activeStaff | `InvoiceLineItem` | `gsi-InvoiceInvoiceLineItems` |
| Bulk cleanups | `StaffStatus` | `byGroup` (group + date) |
| Coaching activity | `Counseling` / `Infraction` / `Kudo` | `byGroupAndDate` |

### Constraints discovered

- **`Route` has no date field.** `byGroupAndTime` sorts on `time`, which is a clock time like `18:30`. Routes are only reachable through `DailyRoster` then `gsi-RouteDailyRoster`.
- **`AuditLog.byGroupAndMutationName` cannot order by date**, because its range key *is* `mutationName`. The daily-review skill already documented this correctly; I initially "discovered" it by testing the method the skill tells you not to use, and wrongly reported it as a bug. Use `byTenantIDAndMutationName` with full pagination.
- **Counting `AuditLog` over a window per account is infeasible.** The only group-scoped index has `email#createdAt` as its range, so there is no date range query across all users. Roughly 27,000 rows per account. Ruled out. "Most recent X" lookups are cheap at 0.5 RCU, so my original blanket dismissal was too broad.
- **No contract, term, renewal or expiration field exists anywhere on `Tenant`.** Hera is month-to-month. There is no renewal event and no 90/60/30-day runway. `/csm:renewal-readiness` has nothing to anchor to.
- **Aurora MySQL is VPN-only.** The instance is `PubliclyAccessible: true` with a `0.0.0.0/0` security group rule on 3306, which looks alarming, but the DB subnets route `0.0.0.0/0` to a **NAT gateway, not an internet gateway**, so there is no inbound path. The private subnets are the real control. See section 6.

### Errors encountered and resolved

- `TypeError: '<' not supported between instances of 'datetime.date' and 'NoneType'` when sorting roster tuples containing `None`. Filter before sorting.
- `ValidationException: Invalid ProjectionExpression` from using `#st` without declaring it in `ExpressionAttributeNames`.
- `SyntaxError: f-string expression part cannot include a backslash` on Python 3.9. Extracted the string to a variable.
- `SyntaxError: keyword argument repeated: ExpressionAttributeNames` from a copy-paste.
- `nohup ... &` inside a backgrounded Bash tool call is killed when the call returns. The log was 0 bytes and the results were silently stale. Ran in the foreground with a long timeout instead.
- `timeout` is not available on macOS by default.

---

## 6. Things that almost went wrong

This is the most important section of this log. Most of the session's value came from catching my own errors, and several were caught only because a check was run rather than assumed.

### Five measurement bugs found in the 30 July audit

1. **Message search swamped by automated sends.** Roster and coaching messages are delivered *per associate* and those rows carry no `senderId`. A tenant with 100 associates emits 100+ sender-less rows in one minute, pushing the human-sent message off any fixed page. I was also querying only 3 of 7 types carrying human sends, missing `recurring`, `standUpAnnouncements`, `coaching` and `wireless-support`, which held 12,056 human sends in an 11-day sample. **59 of 252 tenants read as darker than they were, 14 by 7+ days. DBE Logistics read as 1,205 days dark while messaging that same day.** Fixed with a time-bounded search across all types that stops at the first human send and sets `message_search_truncated` rather than silently reporting dark.

2. **Roster scan cap consumed by future-dated shells.** Tenants plan rosters weeks ahead, so their newest rosters by `notesDate` are future-dated shells with no routes assigned yet, and a 14-record cap ran out before reaching real work. **23 tenants showed "no staffed roster" and 6 had staffed one within three days**, three that same day. Fixed by considering only rosters dated today or earlier.

3. **Uncollected revenue counted as ARR.** Filtered only `Pending`, letting `Written Off` and `Payment Error` through as if collected.

4. **Twelve-month churn understated by half.** Each account's final invoice is often a partial stub for the days before cancellation, then written off. **25 of 88 accounts had one.** GOAT Logistics showed $71/yr against a real $13,598/yr. Total was $328,323 against a true $781,176.

5. **A negative invoice subtracting from revenue.** Next Level Logistics carries a $10 fixed Veteran discount against a $9 charge for one associate, invoicing **-$1.00**. A genuine billing defect, trivial in value.

### Errors in the earlier revisions

- **Revision 1** used `Tenant.averageMonthlyInvoiceTotal`, a **lifetime average**. Every revenue figure was wrong.
- **Revision 2** used `Invoice.invoiceTotal` from invoices that were all status `Pending`, meaning in-progress months still accruing. Comparing a 26-day partial month against full months **manufactured a fake $193,298 book-wide decline** and a fake 7.0% survivor shrinkage. Both were artifacts. The real figures were +$160,133 and +17.8%.
- **Bucket logic conflated MSG_ONLY with disengagement.** That put Midloc (rostered that morning, messaged the day before) into CRITICAL, filed Spears under a "declining revenue" heading while it grew 7%, and inflated adoption risk to 30% of ARR. The report itself exposed it. Fixed so disengaged means BOTH_DARK or roster-dark only, and CRITICAL fell from 23 to 6.

### Claims I made that were wrong and had to be retracted

- **"The `featureAccess`/`featureEnabled` triad is an adoption model sitting in your database."** It is not. `featureAccessAssociateApp` is 0 on all 253 active accounts while `featureEnabledAssociateApp` is 146, so access is not a superset of enabled and "access minus enabled" is not a gap.
- **"78 accounts churned after paying."** Derived from the sparse `firstConvertedToPaidDateTime`. The real figure is 468.
- **"Your production database is open to the internet."** Read `PubliclyAccessible: true` plus a `0.0.0.0/0` security group rule and concluded exposure without checking the routing. The DB subnets route to a NAT gateway, so there is no inbound path. Retracted. What remains is a mild defence-in-depth observation.
- **"I found a bug in your daily review's AuditLog query."** The skill already documents that exact pitfall at step 4.2b and prescribes the correct fix. I tested the method it tells you not to use and called the failure a discovery.
- **"My per-user AuditLog approach is a meaningful optimisation."** Measured: 5x fewer RCU at best on a $0.003 operation. Not worth the complexity. Used the documented method.
- **"The largest account is 2.0x the median."** True of the lifetime-average field, wrong on real invoices where it is about 3x. The homogeneity conclusion held but was overstated.

### Process failures worth remembering

- **I over-built the response to a simple request.** John asked how to see data that was truncating in his terminal. I produced a plan with cleaned-up scripts, a `metrics.json` layer, a branded HTML viewer and a remote planning handoff. He asked for the simplest path and the answer was one markdown file.
- **I did not read the repo before analysing it.** `knowledge/billing-overview.md` had the $9 rate. `knowledge/session-logging-prompt-for-code-repos.md` had the logging convention. The daily-review skill had a three-signal engagement model with sharper ideas than mine. All were found late.
- **A background job silently did not run.** `nohup` inside a backgrounded tool call was killed on return, the log was empty, and the classifier happily re-read a stale cache producing byte-identical output. Caught only by checking the file's mtime against the run time.

---

## 7. Open items and follow-ups

> **Superseded by [`analysis/OPEN-QUESTIONS.md`](../../analysis/OPEN-QUESTIONS.md) on
> 2026-07-30.** That file is the canonical list and uses stable IDs (A1 through G1).
> The 16 items below are kept as the original record. Five questions were missing from
> this list entirely: the retention target, expansion routing, legal routing, success
> plan format, and renewal conversation style.


### Waiting on John

1. **Seasonality / peak season.** Every threshold comes from a mid-summer window. A July decline cannot be separated from a seasonal trough. John said he would supply peak-season detail. **This is the single input that could move numbers.**
2. **Routing and ownership per bucket.** The config currently sends At Risk and Critical to John as a Zoho task. There are now nine buckets. Adoption risk plausibly belongs with CSS 1 as an adoption conversation rather than with John as a save. Nobody owns the empty-shell list.
3. **Escalation response times.** Now answerable because the queues are small: 5 Critical, 27 adoption risk, 35 stopped-scorecards, 19 empty-shell, 17 under-10.
4. **QBR format.** At 241 customers per 1.5 people, month-to-month with no renewal event, standing per-account QBRs may not be viable at all.

### Waiting on the CEO conversation

5. **Three unexplained billing accounts,** about $1,400/mo. Philosophe LLC and Integrated Logistics Solutions each bill $0 with 70+ associates and no discount label. Crucial Mile has `accountPremiumStatus: ['None']` and 175 associates.
6. **Seven comped accounts** beyond MBB, which is intentional and earns it through internal support.
7. **Legacy module pricing migration.** Nine customers on $5 to $7. "Too expensive" already cost $6,614/mo this year, so sequence carefully.
8. **Whether anyone works the trial funnel.** 67 trials worth $59,832/mo, currently nobody's job. Competes directly with the 67 at-risk customers.

### Not measurement, but urgent

9. **JDW Logistics has had its last three invoices written off.** April, May, June, about $2,883/mo. Largest customer at 338 associates, healthy, growing, using the product daily. PacTrack has two consecutive `Payment Error` months, Pure Logistics one. **$4,449/mo delivered and not collected.** Nobody appears to have noticed.

### Still unmeasured

10. **Phantom billing exposure.** How many currently-Active associates across the book have not been on a route in months. This is what a customer would discover. Measurable against `Route`.
11. **Is $9 above or below market?** Competitor switching is $17,525/mo and "too expensive" $6,614/mo, but what DSPworkplace and LMDmax charge is unknown. Determines whether this is a pricing or a value-communication problem.
12. **Associate decline versus Amazon route cuts.** Separates unfixable viability from an operational problem Hera's coaching tools address.
13. **The unnamed competitor.** 12 customers, $8,533/mo, recorded only as "Other". The answer is probably in the 312 populated `accountCanceledNotes` records.
14. **Support signal.** Intercom holds conversations and sentiment per company. Never pulled.
15. **No intervention outcome log.** Nothing records what was tried on an account or whether it worked, so no threshold here has been calibrated against a real result. Six months of logging turns this from informed judgement into something calibrated.
16. **Onboarding and cs-ops plugins unconfigured.** `cs-ops` needs three answers. `onboarding` has the stronger case: 29% of paid churn happens inside 12 months.

---

## 8. Connections to other work

- **`analysis/logrocket-error-investigation/skill/SKILL.md`** Part 4 now defers to this scorer. Its Section D reads the newest weekly report rather than classifying. Its references to `analysis/tenant-engagement/three_signals.py` and `classify.py` now resolve, having been dangling since the file was written.
- **`knowledge/billing-overview.md`** is the authoritative source for the $9 rate. `lib_hera.RATE_PER_ASSOCIATE_MONTH` cites it.
- **`branding/brand-guidelines.md`** supplied the palette for both artifacts and sanctioned the system slab-serif fallback.
- **`knowledge/session-logging-prompt-for-code-repos.md`** is the convention this log follows.
- **`~/bitbucket-hera/CLAUDE.md`** carries the no-em-dashes rule and the bug-diagnosis rules from HERA-8631, which directly informed the audit discipline: absence of a signal is not evidence of absence, observe the target state rather than the trigger.
- **HERA-8631** (Pride Delivery Messenger crash, 2026-07-07) is the reason the revenue axis stays on DynamoDB rather than the RDS mirror.
- **`~/bitbucket-hera/hera/amplify/backend/api/hera/schema.graphql`** (3,902 lines) is the authoritative field reference.
- **Plugin config** lives outside this repo at `~/.claude/plugins/config/claude-for-customer-success/`.
- **Raw transcript appendix:** `.claude/sessions/transcripts/2026-07-28-cs-plugin-setup-and-health-model.jsonl`. Complete but redacted, and it contains retracted claims and wrong figures presented as right at the time. This log is the record; that file is only for reconstructing exactly what was run. See `transcripts/README.md`.

---

## 9. Context that matters later

**Why two axes and not one score.** This is the load-bearing design decision and it was tested, not assumed. In a 20-account pilot, 6 of 15 declining accounts scored *above* the healthy average on engagement. Proactive Logistics scored 7.6 of 9, the highest in the pilot, while losing 15% of its associates. Pure Deliver scored 4.0, the lowest healthy account, while growing 20%. Any future attempt to simplify this into one number will reintroduce both failure modes.

**Why engagement is a binary test rather than a graded score.** The graded rostering-depth score separates deep from shallow usage, which is useful for ranking adoption-coaching targets, but it does not predict decline. Abandonment, by contrast, is absolute: abandoned accounts sit at 0.0 to 0.8 messages per associate while every other account is 25 or higher. There is no middle ground, which makes it reliable.

**Why revenue must never be annualised here.** Hera bills month to month with no contract or term. Annualising implies a commitment that does not exist. John made this call and it is right. It also makes the numbers legible: "$24,245 arrives each month from customers who barely use us" lands where "$290,937 ARR" does not.

**Why the customer, not the tenant, is the unit.** Seven customers run secondary sites that appear as separate tenants via `| STATION` suffixes. `parentAccountId` exists in the schema but is never populated, so name matching is the only route. 248 tenants roll up to 241 customers.

**Why declining associate counts are ambiguous.** Customers control `Active` status and Hera reminds them twice a month to tidy up. A drop is often a data correction rather than lost drivers: 13 of 30 declining accounts were bulk cleanups, 1,109 associates moved to Inactive on a single day. **Never read a decline as churn without the `StaffStatus` cleanup check.**

**Why "revenue already stopped" is separated from "revenue at risk."** Six accounts are already below 10 active associates but their last closed invoice exceeded $100, so their next invoice will be near zero. That $4,459/mo has gone. Reporting it as recoverable inflates the risk number and makes any save rate look worse than reality.

**Why the addressable/program-closure split has compensation consequences.** CSS 1's bonus depends on retention of his book. 40% of churn is Amazon closing DSPs. Any per-book retention figure must strip program closures or he is penalised for something nobody could prevent.

**The strategic tension nobody has decided.** Because billing follows Active status and the customer controls it, an account that has not cleaned up is paying for associates who already left. Proactively helping customers tidy their roster therefore *reduces* Hera's revenue. Good service costs money here. Conversely, a customer who works it out independently has a refund conversation rather than a renewal one, and "too expensive" is already $6,614/mo of churn. This should be decided deliberately rather than stumbled into.

**Business-model constraint that shapes everything.** Revenue equals associates times a fixed $9, so Hera grows only when customers hire. There is no pricing lever inside an account: only 4 of 248 customers pay any flat fee. The only way to raise revenue per associate is to sell something not priced per associate, and HeraAi sits at 13% adoption. Expansion here means modules, not seats.

**Temporary states.** The `2026-07-29-cs-health.md` report contains pre-audit figures and is kept deliberately as a record of what was wrong. The 12 `[NOT SET]` markers in the plugin config are deliberate deferrals, not oversights, and skills are instructed to say "[SLA not configured]" rather than invent one.

**Style constraints that apply to all output.** No em dashes or en dashes, ever, per `~/bitbucket-hera/CLAUDE.md`. John prefers prose multiple-choice blocks over the AskUserQuestion widget; he declined it twice during the interview and answered in prose. Both are recorded in the plugin config.

**Team shape, which is not what an org chart would suggest.** Three people but about 1.5 effective account owners. John is COO and acts as dedicated CSM for the entire book. CSS 1 is transitioning toward owning a carve-out book with a retention bonus. CSS 2 is a hybrid CEO assistant and reactive support who functions as a detection layer and will not be assigned a book. Do not propose workflows that assume three equal CSMs.
