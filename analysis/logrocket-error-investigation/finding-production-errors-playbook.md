# Finding Production Errors in LogRocket — Investigation Playbook

Evergreen instructions for investigating Hera production errors in LogRocket. Use this
for **ad-hoc, session-level** investigations: a customer reports "it broke around 7:15
this morning," or you need every error a specific user or session hit. For the
scheduled **24-hour production health sweep**, use `/daily` instead (see
[`README.md`](README.md) and [`skill/SKILL.md`](skill/SKILL.md)).

This file is the source of truth for the ad-hoc flow. Update it when the process changes.

---

## The one rule that matters most

**LogRocket's aggregated "issues" view only shows triaged SEVERE issues. It does NOT
show most console-level errors.** A session can be full of `console.error` output,
failed requests, and thrown exceptions while the issues feed and the "errors for this
user" summary report **0**.

So: **a "0 errors" answer from an aggregate query is not proof the session was clean.**
When you are chasing a specific user-reported problem, the authoritative source is the
**raw console of the specific session**, reviewed directly. Always drill into the
session before you tell anyone there was nothing wrong.

> Real example (2026-07-08): the aggregate "errors for user X" query returned 0. Pulling
> the same session's console returned 45 error-level events, including a `TypeError`
> that fired 36 times on the core Daily Roster workflow (→ HERA-8632). The aggregate
> view was not lying — the error just wasn't triaged as a "severe issue." The console
> was the truth.

---

## The tool and how it behaves

- Tool: `mcp__logrocket__use_logrocket` (natural-language queries).
- Project: `kdsnjf/hera-solutions`.
- Queries are **async**. A call returns either:
  - `status: "thinking"` with progress `messages` — keep polling.
  - `status: "completed"` with the final answer.
- To poll: call the tool again with the returned `chatID` and `pollForResult: true`
  (no new `query`). Repeat until `status: "completed"`. Queries can take up to ~10 min.
- **Include every link the tool returns in your answer to John.** Session links,
  error links, timestamped-moment links. Do not filter or consolidate them — they are
  how findings get grounded and verified. Reshape the link text if you like, but keep
  the link.
- Screenshots/keyframes come back as image URLs; surface the useful ones.

---

## Timezone handling (do this every time)

- John and most customers are Eastern. LogRocket stores/queries in **UTC**.
- Convert before querying, and state the conversion in your query so the assistant
  scopes correctly:
  - **EDT (Mar–Nov, daylight): ET + 4 = UTC.** 7:15 AM ET → 11:15 UTC.
  - **EST (Nov–Mar, standard): ET + 5 = UTC.** 7:15 AM ET → 12:15 UTC.
- Always query a **window, not a point** — pad ±30 min around the reported time
  (people report approximate times). Widen if nothing lands.
- Sanity-check the date against today's date; "today" in a stale prompt is a trap.

---

## Workflow: a specific user / time was reported

1. **Confirm what was actually reported.** What did the user see, on what page, doing
   what, at roughly what time and timezone? Get the user ID or email if you can. Don't
   start querying on an assumed time — an unconfirmed time is the most common reason a
   clean result is wrong.
2. **Find the sessions.** Query for the user + padded time window (below). Note each
   session's start/end, device/browser, and starting page.
3. **Drill into EACH session's full console** — this is the step that finds the real
   errors. Do not stop at the aggregate result.
4. **Group and count** the console errors by message. Report counts as
   "N in the reviewed session," not as a global total (the tool's counts are
   session-scoped and AI-summarized — treat them as approximate; the raw console is
   authoritative if an exact count matters).
5. **Classify** each finding: JS exception / console.error / failed network request
   (4xx/5xx) / warning. Separate the headline bug from incidental noise.
6. **Attribute to a repo** if you'll hand it to engineering (see "Repo attribution").
7. **Report** with all links + timestamped moments, then offer next steps (ticket,
   widen window, check adjacent sessions).

---

## Copy-paste query templates

Fill in the bracketed parts. Run, then poll with `pollForResult: true` until completed.

### A. All errors for a user in a time window
```
Show me all errors, exceptions, and network errors for the user with ID [USER_ID]
that occurred on [DATE] between [START] and [END] UTC (this is roughly [TIME] ET).
For each error include the message/name, the time, the page or action the user was
on, any stack trace or request detail, and a link to the session and to the error.
Also include a link to the user's session(s) in that window.
```

### B. Full console review of ONE session (the important one)
```
For this specific session: [SESSION_URL] — review the FULL browser console log for
the entire session. List every console error and warning, including console.error and
console.warn output, JavaScript exceptions, unhandled promise rejections, and any
failed network requests (4xx/5xx). For each, give the exact message text, the
timestamp, how many times it repeated, and what the user was doing when it fired.
Do NOT filter to only "severe" issues — include everything logged to the console.
Group by message with counts if there are many.
```

### C. 24-hour production error scan (ad-hoc, not the full /daily routine)
```
List all errors in the production environment in the last 24 hours. For each: the
error message/name, occurrences, affected users, first and last seen in the window,
and a link to the error in LogRocket.
```

### D. Widen / adjacent windows when a search comes back clean
```
Search the same user [USER_ID] across all sessions on [DATE] (full day), and also the
day before and after. For each session list any console errors, failed requests, and
exceptions, with links.
```

---

## Interpreting what comes back

- **Console errors vs severe issues:** the console review (template B) is complete;
  the aggregate issues feed is not. Trust B for "was this session actually clean."
- **Counts are session-scoped and approximate.** "36" means 36 in that one reviewed
  session, not across the user's day or all users. Say so.
- **Separate signal from noise.** Router "redundant navigation" rejections, Moment.js
  deprecation warnings, and third-party console spam are usually not the bug. The bug
  is the one that (a) fires on the action the user reported and (b) repeats.
- **Network 4xx/5xx** are often backend/infra, not frontend. A 403 pattern usually
  means auth/IAM; a 504 means a backend timeout. Group identical-endpoint failures as
  one issue, not many.

---

## Repo attribution (before handing to engineering)

Hera has two frontends. Decide which repo an error lives in by its URL:

| URL contains | App | Repo (local) | Jira prefix | Prod branch |
|---|---|---|---|---|
| `/ath/` | Athena (Vue 3) | `/Users/johnjm/bitbucket/hera/athena` | `HA-` | `origin/main` |
| no `/ath/` | Legacy Hera (Vue 2) | `/Users/johnjm/bitbucket/hera/hera` | `HERA-` | `origin/master` |

The `customer-success` repo (where this file lives) does **not** contain app source, so
you cannot read the actual code from here. See "Proposing a fix" for how to handle that.

---

## Creating the Jira ticket (HERA board)

- Atlassian cloud: `herasolutions.atlassian.net`, cloudId
  `4775898e-b315-4836-8e3f-bc92d132b7bd`.
- **HERA** project key maps to the "Hera Vue2" project. Use it for legacy/Vue2 bugs.
  Athena/Vue3 bugs use the **HA** prefix — confirm the project key before filing.
- Issue type **Bug** (id `10004`). New Bugs open in status "01) Under Construction".
- Useful labels: `logrocket`, `production`, plus the feature area (e.g. `daily-roster`).
- Description template (markdown) — include all of this:
  - **Summary** of the error + where it fires.
  - **Impact** (occurrences, which workflow, user-facing effect).
  - **Error detail** (exact message, level, trigger, suspected cause).
  - **Affected user / tenant / env** (name, tenant slug, user ID, date/time ET,
    device/browser, "Production").
  - **LogRocket session link** + timestamped occurrence links.
  - **Steps to reproduce** from the recording.
  - **Related-but-separate errors** seen in the same session, clearly labeled as
    context so engineering doesn't conflate them.
  - **Source line**: "Identified via LogRocket console review on [DATE]. Reported by
    [name] (Customer Success)."
- Leave assignee/priority to John unless told otherwise, but recommend them
  (e.g. "hits a daily prod workflow → suggest High + assign Andy").

---

## Proposing a fix (recommendation discipline)

The app source is not in this repo, so **any proposed fix written from LogRocket alone
is a hypothesis, not a verified diagnosis.** Follow the working-style rules: don't
assume, don't invent, verify against source or say you can't.

When adding a proposed solution to a ticket:
- **Label confidence up front.** State it's derived from the console signature only,
  not from reading the code.
- **Do NOT invent** file paths, line numbers, function names, or a definitive root
  cause you haven't seen. Describe the *pattern* the signature points to and the
  *plausible* causes.
- **Give layered guidance:** the minimal stop-the-bleeding guard AND the real
  underlying fix (timing vs data), so engineering doesn't just mask a data bug.
- **List what to verify before shipping** and the regression surface.
- **Close** by noting this is CS-side analysis for engineering to validate.

To turn the hypothesis into a real, code-verified proposal, hand this prompt to a
Claude Code session opened in the relevant app repo (`hera` or `athena`):

```
I'm investigating production bug [TICKET]. Find the root cause in this codebase and
propose a concrete, code-level fix.

ERROR: [exact message], thrown during [context/action]. Fires [N]x. Trigger: [actions].
Env: production, [browser/OS]. Tenant: [tenant]. LogRocket session: [SESSION_URL].

HYPOTHESES (from the console signature only — verify against the code):
1. [hypothesis 1]
2. [hypothesis 2]

DO:
1. Find where the failing property/call is read in or downstream of [the relevant
   render/handler path]; cite the file(s) and line(s).
2. Determine which hypothesis is correct, with evidence from the source.
3. Propose a fix in two layers: the minimal guard that stops the throw, and the real
   underlying fix (fix the timing, or default the missing data upstream).
4. Call out regression risks and what to test.
Also check MQA/DQA branches to see if a fix already exists but isn't promoted; if so,
give the branch, commit hash, and HERA-/HA- ticket. Don't guess — show me the actual
code. I don't have a coding background, so explain in plain language.
```

---

## Common pitfalls (learned the hard way)

- **Trusting a "0 errors" aggregate.** Always confirm against the session console.
- **Querying a point time, or the wrong timezone.** Pad the window; convert ET→UTC
  with the right DST offset.
- **Reporting the tool's count as a global total.** It's session-scoped.
- **Filing on the wrong board.** `/ath/` in the URL → HA/Athena, otherwise HERA/Vue2.
- **Inventing a root cause in the ticket.** No app source here → hypothesis only.
- **Dropping links.** Every session/error/moment link the tool returns goes in the
  answer and the ticket.

---

## Related files

- [`README.md`](README.md) — the scheduled 24h daily-review routine and setup.
- [`skill/SKILL.md`](skill/SKILL.md) — canonical logic for the `/daily` routine.
- [`2026-06-05-prompt.md`](2026-06-05-prompt.md) — a worked example of a multi-error
  code-investigation prompt run against the app repos.
- Dated `YYYY-MM-DD-report.md` files — routine output.
