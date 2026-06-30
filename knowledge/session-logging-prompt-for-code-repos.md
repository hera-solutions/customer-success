# Session Logging Prompt for Code Repos

Drop this into a project's CLAUDE.md (or equivalent) so Claude Code saves conversation context alongside the code.

---

## Prompt

```markdown
## Session logging

At the end of each session (or at natural stopping points), save a detailed log of the conversation to a `.claude/sessions/` directory in the project root. Use the filename format `YYYY-MM-DD-short-description.md`.

Err on the side of too much detail. Information that seems minor during the session may turn out to be critical later. If something was discussed, it goes in the log.

Each log should include all of the following sections:

### 1. Date, time, and scope
- The date of the session.
- What triggered the session (a bug report, a feature request, a question, a review, a follow-up from a prior session, etc.).
- One to three sentences summarizing what the session covered.

### 2. What changed
- Every file added, modified, or deleted. Include the file path.
- For each file, describe what changed and why. Not just "updated utils.js" but "added retry logic to the API call in utils.js because the third-party endpoint was returning intermittent 503s."
- If nothing changed (pure discussion or review), say so explicitly.

### 3. What was discussed but not changed
- Topics that came up but did not result in a code change. These are easy to lose and often matter later.
- Include alternative approaches that were considered and why they were rejected.
- Include questions that were asked and how they were answered, even if the answer was obvious at the time.

### 4. Decisions made
- Every decision, no matter how small. Include:
  - What the decision was.
  - What the alternatives were.
  - Why this direction was chosen over the others.
  - Who made the call (the user, Claude, mutual agreement).
- If a decision was made by default (no one explicitly chose, it just happened), note that too.

### 5. Technical details and implementation notes
- Specific function names, variable names, API endpoints, database tables, config keys, or file paths that were referenced or relevant.
- Any constraints discovered during the session (rate limits, browser compatibility, library limitations, version requirements).
- Error messages encountered and how they were resolved.
- Workarounds applied and what the ideal fix would look like if time/resources allowed.
- Dependencies added, removed, or updated, and why.

### 6. Things that almost went wrong
- Bugs or issues caught during the session before they shipped.
- Misunderstandings that were corrected mid-conversation.
- Assumptions that turned out to be wrong.
- Anything that required backtracking or a change in approach.

### 7. Open items and follow-ups
- Anything unresolved, deferred, or flagged for later.
- For each item, include enough context that a future session can pick it up cold without re-reading this entire log.
- If an open item depends on someone else (a response from a colleague, a third-party fix, a deploy), note who and what you are waiting on.

### 8. Connections to other work
- References to prior session logs, PRs, issues, tickets, or conversations that are related.
- If this session continues or builds on previous work, link back to it.
- If this session creates work that needs to happen in a different repo or project, note it.

### 9. Context that matters later
- Anything a future reader would need to understand why things are the way they are.
- Business context, user requirements, or constraints that shaped the technical decisions.
- Temporary states ("this is a stopgap until X ships"), time-sensitive factors ("this API is being deprecated in Q3"), or environment-specific notes ("only reproduces on staging, not local").

Do not include raw chat transcripts. Write in plain language. Use headers and bullet points so the log is scannable. But do not sacrifice detail for brevity. A log that is too long but complete is more useful than a log that is short and missing something.

Commit the session log with the rest of the changes. If nothing was committed during the session (pure discussion or review), commit the session log on its own.

The goal is to build a complete, searchable history of why things were built the way they were, not just what was built. Git history shows what changed. Session logs capture everything else: the reasoning, the context, the rejected alternatives, the near-misses, and the loose ends.
```

---

## Notes

- The `.claude/sessions/` directory keeps logs separate from source code and docs.
- The filename convention makes logs sortable by date and searchable by topic.
- "Context that matters later" is the most important section. That's where you capture the things that don't show up in a diff or a commit message.
