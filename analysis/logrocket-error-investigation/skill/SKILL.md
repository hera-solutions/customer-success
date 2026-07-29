---
name: logrocket-daily-review
description: Daily production health report for Hera. Pulls (a) the last 24h of LogRocket production errors with code-source attribution and MQA/DQA fix status, (b) open Intercom tracker tickets with their linked JIRA tickets and code-progress status, and (c) on weekdays only, Abram's most recent nightly wrap-up email — comparing the JIRA tickets he mentioned against what the routine itself identified as in-flight. Abram doesn't work weekends, so on Saturday/Sunday runs Part 3 is skipped and only LogRocket + Intercom/JIRA run. Saves a dated markdown report to customer-success/analysis/logrocket-error-investigation/. Use when the user asks "run the daily review", "what's the status of customer-reported bugs", "what broke in production yesterday", "what did Abram cover last night", "review Abram's wrap-up", or when invoked by the scheduled routine.
---

# Daily Production Health Review

You are running the daily production health review for Hera Solutions. There are **three parts**:

**Part 1 — LogRocket errors.** What broke in production in the last 24 hours, where is the code, and is a fix already in MQA or DQA waiting to promote.

**Part 2 — Intercom trackers + JIRA.** What customer-reported bugs are open in Intercom, what JIRA ticket each one is linked to, what the JIRA status is, and whether code progress matches the JIRA status.

**Part 3 — Abram's nightly wrap-up.** What JIRA tickets Abram covered in his most recent wrap-up email. Cross-reference against Part 2: surface tickets the routine expects Abram to mention but he didn't, and any place where Abram's description disagrees with current JIRA status. **Weekdays only — skipped on Saturday and Sunday because Abram does not work weekends.**

**Part 4: Tenant engagement tripwire.** A cheap check for tenants that have gone dark since the last weekly scoring run. **This part does not classify tenants.** Classification is owned by the `cs-health-weekly` skill and the shared scorer at [`analysis/tenant-engagement/`](../../tenant-engagement/README.md), which has the revenue axis, the roster-cleanup check and rostering entitlement. Section D reports the weekly triage headline, flags how stale that report is, and lists anything newly dark. See Part 4 below.

Save the combined report to `/Users/johnjm/bitbucket/customer-success/analysis/logrocket-error-investigation/YYYY-MM-DD-report.md`.

## Hard requirements before you start

- **Both code repos must exist locally.** Confirm `ls /Users/johnjm/bitbucket/hera/hera` and `ls /Users/johnjm/bitbucket/hera/athena`. If either is missing, stop and tell the user.
- **MCP servers connected:**
  - LogRocket (id prefix `mcp__b73f35c0-…__use_logrocket`)
  - Intercom (`mcp__048d1487-…__search_conversations`, `…__get_conversation`, `…__search`)
  - Atlassian/JIRA (`mcp__c757fcc7-…__getJiraIssue`, `…__searchJiraIssuesUsingJql`)
  - Gmail (`mcp__f4829b4a-…__search_threads`, `…__get_thread`) — for Part 3
  Use `ToolSearch` with `select:` to load schemas before calling. If Gmail is invalidated, Parts 1 and 2 still run; Part 3 reports "Gmail connector unavailable — reconnect and re-run for Section C" and continues.
- **Today's date** comes from the `currentDate` context. Do not call `Date.now()` for the filename.
- **`git fetch --all --quiet`** in each repo at the start of the run so origin/* is fresh.
- **Day of week** also comes from `currentDate`. Compute it before starting. If today is **Saturday or Sunday**, skip Part 3 entirely — Abram does not work weekends, so there will be no wrap-up email. Parts 1 and 2 still run as normal.

## Repo / environment map

Memorize this — every routing and branch-comparison decision depends on it.

| App | URL pattern | Repo path | Production branch | MQA branch | DQA branch | JIRA project | JIRA prefix |
|---|---|---|---|---|---|---|---|
| Legacy Hera (Vue 2) | URL does NOT contain `/ath/` | `/Users/johnjm/bitbucket/hera/hera` | `origin/master` | `origin/mqa` | `origin/dqa` | `HERA` (Hera Vue2) | `HERA-` |
| Athena (Vue 3) | URL contains `/ath/` | `/Users/johnjm/bitbucket/hera/athena` | **`origin/main`** | `origin/mqa` | `origin/dqa` | `HA` (Hera Athena) | `HA-` |

⚠️ **Athena's production branch is `origin/main`, not `origin/master`.** Common mistake — don't make it.

**Always read code via `git show origin/<branch>:<path>`**, never the working tree. Both repos commonly have uncommitted work in progress on disk that does NOT match production.

## Constants you can hard-code

Verified on 2026-06-05. If a call fails because one changed, re-discover and update this skill.

- **JIRA cloudId:** `4775898e-b315-4836-8e3f-bc92d132b7bd` (herasolutions.atlassian.net)
- **Intercom Support team ID:** `8163703` (this is where customer support routes; tracker tickets live here)
- **LogRocket project slug:** `hera-solutions`
- **Abram's email address:** `abram@hera.app` (sender of the nightly wrap-up — note: `abram`, not `abrams`)
- **JIRA key regex:** `\b(HERA|HA)-\d{1,5}\b` (use this to extract ticket keys from any free-text body)

---

# Part 1 — LogRocket production errors

## Step 1.1 — Pull errors

Use the LogRocket MCP. Pull errors from the **last 24 hours**, **production environment only**.

For each error, capture:
- Exact message and type (`TypeError`, HTTP code, `AccessDeniedException`, etc.)
- URL/route where it fired
- Hit count, unique users, first/last seen
- Stack trace top frame (file + line) if available
- Endpoint or GraphQL operation name embedded in the error message

Group by root identity — same message + same top stack frame is one entry, not many.

## Step 1.2 — Route to the right repo

URL contains `/ath/` → Athena repo, HA- prefix. URL does not → Legacy Hera, HERA- prefix.

Ambiguous? Lean on the endpoint name or check both repos.

## Step 1.3 — Find the source on the production branch

In the correct repo:
- `git grep -in '<error message or unique token>' origin/<prod>` — find call sites
- `git show origin/<prod>:src/path/to/File.vue` — read a file at production
- `git ls-tree -r --name-only origin/<prod> | grep -i pattern` — find files by name

For Amplify-served HTTP errors:
- Frontend call site: `src/views/**` or `src/components/**`
- Backend handler: `amplify/backend/function/<NAME>/src/`
- API Gateway / IAM permissions: `amplify/backend/api/<API_NAME>/cli-inputs.json`

For minified JS exceptions, identify the function name and the shape (`state.userInfo.tenant` etc.), then grep for those identifiers. Don't stop at the file that throws — follow the call chain.

## Step 1.4 — Check MQA and DQA for an existing fix

```
git log origin/mqa --oneline -- <suspected files> | head -20
git log origin/dqa --oneline -- <suspected files> | head -20
git log origin/mqa --oneline | grep -iE '<keywords or HERA-/HA- prefix>'
git log origin/dqa --oneline | grep -iE '<keywords or HERA-/HA- prefix>'
git diff origin/<prod>..origin/mqa -- <file>
```

Keywords: function name, file basename, error fragments, route segments, ticket prefix, `fix`, `retry`, `null`, `guard`, `timeout`, `refresh`, `expir`, status codes.

If you find a fix, **verify it** — `git show <hash> --stat` and confirm the diff actually addresses the error. Don't claim a fix that isn't real. Record branch, hash, ticket, one-line summary.

## Step 1.5 — Priority

- HIGH: ≥ 25 hits OR ≥ 3 distinct users in 24h
- MED: 5-24 hits or 2 distinct users
- LOW: < 5 hits AND 1 user (observe-don't-fix)

---

# Part 2 — Intercom trackers + JIRA

## Step 2.1 — Pull open tracker tickets from Intercom

```
search_conversations(state=open, team_assignee_id=8163703, per_page=150)
```

Page through with `starting_after` until exhausted. For each conversation, **filter in code** to keep only:

- `custom_attributes["Ticket category"] == "Tracker ticket"`
- `ticket.ticket_type` contains `"Bug"` (matches `"Bug Report"` and `"General Bug"`)

For each kept tracker, capture:
- `id` — Intercom conversation ID. Build URL: `https://app.intercom.com/a/apps/baat8a8r/conversations/<id>`
- `ticket.custom_attributes._default_title_.value` — the bug title
- `custom_attributes["Customer reports"]` — number of individual customer tickets linked to this tracker
- `ticket.ticket_custom_state_admin_label` — e.g. `"Developing Fix"`, `"Fix in Testing"`
- `custom_attributes.jira_issue_key` — linked JIRA ticket (e.g. `"HERA-8506"` or `"HA-2322"`)
- `linked_objects.total_count` — cross-check vs `Customer reports`

**Skip any tracker without a `jira_issue_key`** — note it in the report as `NEEDS JIRA LINK` so someone hooks it up.

## Step 2.2 — Fetch each JIRA ticket

For each unique JIRA key:

```
getJiraIssue(
  cloudId="4775898e-b315-4836-8e3f-bc92d132b7bd",
  issueIdOrKey="<key>",
  fields=["summary", "status", "assignee", "updated", "priority", "issuetype"]
)
```

Capture: `status.name`, `assignee.displayName`, `updated`, `priority.name`, `summary`.

Hera's status uses numbered states like `"05) In Progress"`, `"08) Dev QA"`, `"13) Release Approved"`. Preserve the number prefix in the report — it shows ordering at a glance.

## Step 2.3 — Cross-reference with the right code repo

Routing:
- Key starts with `HERA-` → `/Users/johnjm/bitbucket/hera/hera`, prod branch `origin/master`
- Key starts with `HA-` → `/Users/johnjm/bitbucket/hera/athena`, prod branch `origin/main`

In that repo, run:

```
# Active branch with the ticket prefix
git branch -a | grep -i "<ticket>"

# Already in MQA?
git log origin/mqa --oneline | grep -i "<ticket>" | head -3

# Already in DQA?
git log origin/dqa --oneline | grep -i "<ticket>" | head -3

# Already in production?
git log origin/<prod> --oneline | grep -i "<ticket>" | head -3
```

Row fields: branch existence (Y/N), MQA (Y + commit hash), DQA (Y + commit hash), Prod (Y + commit hash).

## Step 2.4 — Flag conditions

Set a flag if any condition hits. Be specific in the flag column.

| Condition | Flag |
|---|---|
| JIRA shows `Done` / `Closed` / `Released` but Intercom tracker is still open | **CLOSE-IN-INTERCOM** — fix shipped, tracker forgotten |
| Intercom has ≥ 5 customer reports and JIRA status is `To Do` / `Open` / pre-`In Progress` | **ESCALATE** — high customer impact, no movement |
| JIRA `updated` more than 7 days ago AND status is not terminal | **STALE** — no JIRA activity in over a week |
| JIRA shows `Dev QA` / `Release Approved` but no DQA commit exists | **STATUS MISMATCH** — JIRA claims done-ish but no code evidence |
| Tracker has no `jira_issue_key` | **NEEDS JIRA LINK** |

Compute "days since updated" from JIRA `updated` vs the current run date.

## Step 2.5 — Skip rules

To keep the report scannable:
- Skip resolved Intercom states (`Resolved`, `Released`, `Closed`) — they fall off naturally.
- Skip JIRA `Done` / `Closed` UNLESS the Intercom tracker is still open (then surface as **CLOSE-IN-INTERCOM**).

---

# Part 3 — Abram's nightly wrap-up

**Weekend skip.** If today is Saturday or Sunday, do not run any step in Part 3. Abram does not work weekends, so no wrap-up email exists. In the report file, replace Section C with a single line: `## Section C — Abram's nightly wrap-up\n\n_Skipped — Abram does not work weekends._` Then jump straight to Step 4. The user brief (Step 5) should not list any Section C items.

**Who Abram is and what this part is for.** Abram (Yrigoyen) is the **Customer Support Specialist** — not an engineering lead. His nightly wrap-up is a personal accountability log of *his own work*: which calls he took, how he split his time, customer touches, JIRA tickets *he created* (he files bugs surfaced by customers), tickets *he tested*, what's on deck for tomorrow, and any blockers or help requests. He does **not** report status on every in-flight engineering ticket — that's an engineering function.

Section C's job is therefore:
1. Show what Abram did in a parsed, scannable form (his structured sections, summarized).
2. Surface follow-up risks coming out of his work — newly-filed tickets with no priority/assignee, customer issues he investigated but couldn't capture as JIRAs, manual-QA backlog when his testing throughput was zero, and any tracker waiting on him.
3. Flag the rare case where his description of a ticket disagrees with current JIRA reality.

## Step 3.1 — Find the most recent wrap-up

```
search_threads(query='from:abram@hera.app subject:"Daily Wrap-Up" newer_than:1d', pageSize=5)
```

If the search returns nothing within 1 day, widen to `newer_than:3d` and note the gap (e.g., "No wrap-up from Abram in the last 24 hours — most recent was N days ago"). The subject pattern `"Daily Wrap-Up"` matches both `"Daily Wrap-Up Email"` (the current default) and minor variations.

If Gmail returns auth/invalidated, write Section C as "**Gmail connector unavailable — reconnect at chat.com → Settings → Connectors and re-run.** Parts 1 and 2 are unaffected." Then continue to Step 4.

Pick the most recent matching thread. If multiple match, take the latest by `date`.

## Step 3.2 — Fetch the full body

```
get_thread(threadId=<id>, messageFormat="FULL_CONTENT")
```

Use `plaintext_body` (not `htmlBody`). If the thread has replies after Abram's, you want Abram's original message specifically — match by `sender == "abram@hera.app"`.

## Step 3.3 — Parse the structured sections

Abram's wrap-up has a **fixed template**. Section headers are bare lines (no markdown), each section is bullet-list-style with `•` prefixes in plaintext. Parse these sections by header text:

| Header (exact substring match) | What it contains |
|---|---|
| `Calls` | Meeting log — one bullet per call/meeting with duration + outcome |
| `Time split (rough %)` | Five labeled buckets: Calls / Ticket testing / Intercom support / CSM / Investigating bugs |
| `Customer touches` | Four counters: Intercom conversations handled / Tickets created / Tickets tested / Accounts set up |
| `What I accomplished` | Free-form bullets, often containing JIRA links |
| `On deck tomorrow` | Free-form bullets (may be empty — just `•` on a line) |
| `Blockers/Issues` | Free-form bullets (may be empty) |
| `Help needed` | Free-form bullets (may be empty) |

For each section, capture the raw bullet text. For `Time split` and `Customer touches`, also parse the numeric values (`Calls: 20%` → `calls_pct: 20`; `Tickets created: 2` → `tickets_created: 2`). Treat any bullet that's just an empty `•` as "section explicitly empty."

If a header is missing entirely (Abram skipped a section), note that — don't fail.

## Step 3.4 — Extract JIRA keys and classify by section

Run the JIRA-key regex `\b(HERA|HA)-\d{1,5}\b` over `plaintext_body`. JIRA links come through as `https://herasolutions.atlassian.net/browse/HERA-XXXX` so the regex catches both bare keys and full URLs.

For each key, capture:
- The key itself
- Which parsed section it appeared in (e.g., `What I accomplished > Tickets created`)
- The surrounding line (and the previous line if it's a continuation indented under a parent bullet)

This classification matters: a key under `Tickets created` is Abram filing new work; a key under `What I accomplished` not nested under "Tickets created" is something he worked on or tested.

## Step 3.5 — Look up JIRA for each key

For every unique key, fetch:

```
getJiraIssue(
  cloudId="4775898e-b315-4836-8e3f-bc92d132b7bd",
  issueIdOrKey="<key>",
  fields=["summary", "status", "assignee", "updated", "priority", "issuetype", "reporter", "created"]
)
```

Reuse Section B results for any key already fetched there.

## Step 3.6 — Produce the three lists

### List A. Summary of wrap-up (parsed)

A scannable digest of his structured sections:

- **Calls today:** count + one-line per call (drop signatures/boilerplate)
- **Time split:** the five percentages, one row each
- **Customer touches:** the four counters
- **Tickets created today:** for each JIRA key found under `What I accomplished > Tickets created`, show: key (clickable), issuetype, summary, current status, priority, assignee
- **Other tickets discussed:** any other JIRA keys found, with the same shape, plus the section/sentence where they appeared
- **On deck tomorrow:** verbatim bullets (or "(empty)" if Abram left it blank)
- **Blockers / Help needed:** verbatim, prominently displayed if non-empty

### List B. Watch items / follow-ups

Flag each of these when the condition holds. Each row gives the item, why it's flagged, and the recommended action.

| Condition | Flag |
|---|---|
| A ticket Abram created today has `priority == "None"` | **NEEDS PRIORITY** — sits in triage indefinitely otherwise |
| A ticket Abram created today has no `assignee` for >24h | **NEEDS ASSIGNEE** — nobody owns it yet |
| Abram's narrative describes a customer issue he investigated, but no JIRA key appears in that bullet | **FLOATING ISSUE** — investigated, not captured. Recommend Abram file a ticket (even a spike) so it doesn't drop off |
| `Customer touches > Tickets tested == 0` AND any Section B tracker has JIRA status in `09) Manual QA` / similar (testing-stage) | **QA BACKLOG** — manual QA queue not drained today |
| Abram filed a ticket today (in `Tickets created`) AND the issuetype is `Bug` AND no Intercom tracker exists yet that links to it | **NEEDS INTERCOM TRACKER** — bug filed but no customer-visible tracker; reach out to the affected customers via Intercom |
| Abram's wrap-up says "Customer is unresponsive" or "can't replicate" for a JIRA ticket | **UNRESOLVED REPRO** — note for follow-up next week if customer re-engages |
| `Blockers/Issues` or `Help needed` is non-empty | **HELP NEEDED** — surface the verbatim ask, that's the action |

Compare-cross with Section B for the QA backlog check.

### List C. Status mismatches

For each ticket Abram described, compare his language to current JIRA status. Examples of mismatch:
- Abram: "I created and tested HERA-X" / "fix verified" → JIRA says `01) Under Construction` → MISMATCH (Abram may have tested an earlier version)
- Abram: "HERA-X is blocked" → JIRA shows recent activity progressing → MISMATCH

Only flag substantive disagreements, not paraphrase noise. Each row: key, Abram's exact quote, current JIRA status, one-line note, who to ask.

## Step 3.7 — Skip rules

- Don't flag MISMATCH on `Spike` issuetype tickets where Abram says "can't replicate" and JIRA is `01) Under Construction` — that's the normal state of a spike.
- Don't flag MISSING for Section B trackers — Abram is not expected to status-report engineering tickets. (The QA-backlog flag in List B is the only legitimate "Abram should have touched this" condition.)
- Don't include the email signature/disclaimer in any list. Common boilerplate lines to drop: `Abram Yrigoyen`, `Customer Support Specialist`, `Book Time with Me`, `Facebook`, `LinkedIn`, `hera.app`.

---

# Part 4: Tenant engagement tripwire (Section D in the report)

**This part no longer classifies tenants.** Classification lives in one place now:
the `cs-health-weekly` skill and the shared scorer at
[`analysis/tenant-engagement/`](../../tenant-engagement/README.md). Two competing
models produced contradictory answers, so the daily review keeps a cheap tripwire
and defers anything that requires judgement.

## What the daily run does

Read the newest weekly report in
[`analysis/tenant-engagement/reports/`](../../tenant-engagement/reports/) and surface
three things in Section D:

1. **The triage headline from that report**, unchanged. Bucket, tenant count, ARR,
   share. Do not recompute it.
2. **How stale the weekly report is.** If the newest report is more than 8 days old,
   say so at the top of Section D and recommend running `cs-health-weekly`.
3. **New BOTH_DARK tenants since the weekly ran.** This is the tripwire, and the only
   thing Part 4 computes itself. See below.

## The tripwire

The point is to catch a tenant going dark between weekly runs, not to reclassify
anything. Cheap check, no judgement:

For each tenant listed as `HEALTHY`, `WATCH` or `STRATEGIC_RISK` in the newest weekly
report, confirm at least one of these is within 14 days:

- most recent `Message` with `senderId` populated, via the `byGroupAndMessageType`
  GSI with a `begins_with` prefix on `broadcast#`, `messenger#` or `roster#`
- most recent `CreateMessageReadStatus` in AuditLog, via
  `byTenantIDAndMutationName`, **paginated fully** and taking the max, because that
  GSI's range key is `mutationName` and cannot sort by date
- most recent `CompanyScoreCard` via `byTenantByYearWeek`

Any tenant where all three are older than 14 days has gone dark since the weekly
run. List those, with monthly revenue, and recommend a `cs-health-weekly` run. **Do
not assign them a bucket** and do not describe them as CRITICAL; the weekly scorer
decides that, because it also has the revenue axis and the roster-cleanup check that
this tripwire deliberately skips.

The helpers are importable rather than reimplemented:

```python
import sys; sys.path.insert(0, 'analysis/tenant-engagement')
import lib_hera as H
from three_signals import signals_for
```

## Why the split

The weekly scorer needs the revenue axis (active-associate trend across closed
invoices), the roster-cleanup check, and rostering entitlement. Without all three it
mislabels accounts: a customer who tidied a stale roster looks like churn, a customer
without the rostering module looks disengaged, and a customer who rostered that
morning can land in CRITICAL. None of that belongs in a daily run.

**Revenue at risk stays out of Section D entirely.** It requires closed-invoice data
and the already-stopped-revenue adjustment, and reporting it from a daily snapshot
overstated it before.


# Step 4 — Write the report

Save to: `/Users/johnjm/bitbucket/customer-success/analysis/logrocket-error-investigation/YYYY-MM-DD-report.md`

If today's file exists, append a "Run 2" section rather than overwriting.

Use this structure:

```markdown
# Daily Production Health Report — YYYY-MM-DD

**Window:** last 24 hours
**LogRocket project:** hera-solutions (production)
**Intercom team:** Support (id 8163703)
**JIRA site:** herasolutions.atlassian.net
**Repos checked:** hera (HERA-, prod=master) and athena (HA-, prod=main)

---

## Section A — LogRocket production errors

### Summary table

| # | Route | Error (short) | Hits | Users | Repo | Owner | Already fixed in MQA/DQA? | Ticket | Recommended action |
|---|---|---|---|---|---|---|---|---|---|

### Per-error detail

[For each error, sorted by priority then hits, use the structure from Part 1.]

---

## Section B — Open customer-reported bug trackers (Intercom + JIRA)

### Summary table — at a glance

| Intercom title | Reports | Intercom state | JIRA | JIRA status | Assignee | Updated | Branch | In MQA | In DQA | In Prod | Flag |
|---|---|---|---|---|---|---|---|---|---|---|---|

Sort: flags first (ESCALATE, STALE, CLOSE-IN-INTERCOM, STATUS MISMATCH, NEEDS JIRA LINK), then by Customer Reports count descending.

### Per-tracker detail (only flagged or top-5 by reports)

For each, give:
- Intercom title, link to conversation, customer reports count, Intercom state
- JIRA key (clickable to https://herasolutions.atlassian.net/browse/<KEY>), status, assignee, days-since-updated, priority
- Code progress: which branches exist, which envs have commits, hash(es)
- Flag (if any) and what to do about it

---

## Section C — Abram's nightly wrap-up

### Wrap-up at a glance

| Subject | Sent | Calls | Tickets created | Tickets tested | Intercom convos | Watch items | Status mismatches |
|---|---|---|---|---|---|---|---|

### List A — Summary (parsed)

**Calls**
- (one row per call, with duration and one-line outcome)

**Time split**
| Calls | Ticket testing / QA | Intercom support | CSM / setup | Investigating bugs |
|---|---|---|---|---|

**Customer touches**
| Intercom convos | Tickets created | Tickets tested | Accounts set up |
|---|---|---|---|

**Tickets Abram created today**
| JIRA | Type | Summary | Status | Priority | Assignee |
|---|---|---|---|---|---|

**Other tickets discussed** (any JIRA keys outside the "Tickets created" bullet)
| JIRA | Where it appeared | What Abram said | Current JIRA status |
|---|---|---|---|

**On deck tomorrow** — verbatim bullets (or "(none)")
**Blockers / Issues** — verbatim bullets (or "(none)")
**Help needed** — verbatim bullets (or "(none)")

### List B — Watch items / follow-ups

| Item | Flag | Recommended action |
|---|---|---|

(Empty if no flags fire — say "None — all of today's work is clean.")

Flag types: **NEEDS PRIORITY**, **NEEDS ASSIGNEE**, **FLOATING ISSUE**, **QA BACKLOG**, **NEEDS INTERCOM TRACKER**, **UNRESOLVED REPRO**, **HELP NEEDED**.

### List C — Status mismatches

| JIRA | Abram's quote | Current JIRA status | Note | Who to ask |
|---|---|---|---|---|

(Empty if none — say "None — Abram's descriptions match JIRA.")

---

## Section D: Tenant engagement tripwire

### Method

Read the newest report in [`analysis/tenant-engagement/reports/`](../../tenant-engagement/reports/).
Do not recompute the classification: that is the `cs-health-weekly` skill's job.

1. Reproduce its triage table verbatim (bucket, tenants, ARR, share).
2. State the report date. **If it is more than 8 days old, say so here and recommend
   running `cs-health-weekly`.**
3. Run the tripwire from Part 4 and list any tenant that has gone dark since.

### Triage headline (from the weekly report)

| Bucket | Tenants | ARR | Share |
|---|---|---|---|

Carry the weekly report's numbers straight across. Add one line naming the report file.

### Newly dark since the weekly run

| Account | Monthly | Days since msg sent | Days since msg read | Days since scorecard |
|---|---|---|---|---|

Tenants previously `HEALTHY`, `WATCH` or `STRATEGIC_RISK` whose three engagement
signals are now all older than 14 days. **Do not assign a bucket and do not call them
CRITICAL.** State that a `cs-health-weekly` run is needed to classify them, because
the tripwire has no revenue axis and no roster-cleanup check.

If none: "None. No tenant has gone dark since the weekly run."

### What not to put here

- **No revenue-at-risk figure.** It needs closed-invoice data and the
  already-stopped-revenue adjustment. Reporting it from a daily snapshot overstated
  it before.
- **No bucket assignments** beyond what the weekly report already said.
- **No save recommendations.** Adoption risk and business contraction need different
  handling, and only the weekly scorer distinguishes them.


## Day-over-day delta

If yesterday's report exists in the same folder:
- **New today** — errors/trackers/wrap-up items that weren't in yesterday's report
- **Cleared today** — items from yesterday that are gone
- **Moved forward** — any tracker whose JIRA status advanced
- **Carried over** — Abram's blockers or help-needed items that persist from yesterday
```

# Step 5 — Brief the user

After writing the file, post a short summary in the chat (~15 lines max):

- Path of the report
- Top 1-3 actions for the day, lowest-effort-highest-impact first
- Any **CLOSE-IN-INTERCOM** trackers (one click each)
- Any **ESCALATE** trackers (high customer impact, no movement)
- Any **Section C watch items** — NEEDS PRIORITY / NEEDS ASSIGNEE / FLOATING ISSUE / HELP NEEDED. These are concrete asks coming out of Abram's wrap-up.
- **Section D asks**: any tenant newly dark since the weekly run, plus a prompt to run `cs-health-weekly` if its report is over 8 days old. Bucket-level actions come from the weekly report, not from here.
- Anything new today vs yesterday

Detail lives in the file.

# Style rules

- Plain English. The reader does not code.
- `[file](path:line)` style for source citations so they're clickable.
- Code snippets: max 5 lines, only when they clarify.
- Every claimed fix has a branch + commit hash + ticket. No "I think MQA has this."
- If you cannot confirm something, say so. Do not guess.
- Never edit or commit in the `hera` repos. Read-only there.
- For the customer-success repo, you may write the report file; commit and push only if the user asked the routine to auto-commit (it's an option in the README setup).

# Common failure modes

- Intercom returned 0 open trackers (rare). Section B says "No open bug trackers in Support team."
- Tracker has no `jira_issue_key`. Surface as `NEEDS JIRA LINK`.
- JIRA call fails for one ticket. Note as "JIRA lookup failed — verify manually" and continue.
- A fix appears to exist in MQA/DQA but the diff doesn't address the failing code path. Say so — don't claim a real fix that isn't.
- LogRocket returned an error you can't find in code. Note: "Could not locate source — investigate manually." Don't invent a file path.
- Working tree has uncommitted changes. Ignore. Read only from `git show origin/<branch>:...`.
- Gmail connector returns an auth/invalidated error. Section C says: "Gmail connector unavailable — reconnect at chat.com → Connectors and re-run for Section C." Continue with Sections A and B.
- No Abram email in the last 24h. Search widens to 3d; report the gap explicitly: "No wrap-up from Abram in the last 24h. Most recent was N days ago." Then proceed with the older email if found, clearly noting the date.
- Abram's email mentions no JIRA keys at all. Section C Summary says "Abram's wrap-up did not reference any JIRA keys. Body snippet for context: ..." (first 200 chars) so the user can decide if that's expected or if Abram's format changed.
