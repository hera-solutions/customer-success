# Daily Production Health Review — Setup Guide

This folder holds the **daily production health reports** for Hera. Each report covers three things:

1. **LogRocket production errors** in the last 24 hours, with code source attribution and MQA/DQA fix status.
2. **Open Intercom bug trackers + their linked JIRA tickets** — JIRA status, assignee, days since updated, whether code has been pushed to MQA/DQA/prod, and flag conditions like "JIRA done but Intercom still open" or "5+ customer reports and JIRA hasn't moved."
3. **Abram's nightly wrap-up email** — pulls his most recent wrap-up, extracts every JIRA ticket he mentioned, and cross-references against Section B. Surfaces (a) tickets the routine expects in the wrap-up but Abram didn't cover, and (b) any place where Abram's description disagrees with current JIRA status.

The investigation logic lives in a skill — the canonical, version-controlled copy is at [`skill/SKILL.md`](skill/SKILL.md) in this folder. Claude Code discovers skills from `.claude/skills/<name>/SKILL.md`, which is gitignored in this repo, so the working setup is to **symlink** the tracked copy into `.claude/skills/` (one-time, per machine — see "Wiring the skill" below).

This README explains how to set up the **daily routine** so the report runs on its own and lands in this folder.

---

## What the routine does, end to end

**Section A — LogRocket errors**

1. Pulls the last 24 hours of production errors from LogRocket (project `hera-solutions`).
2. For each unique error, decides which repo it lives in:
   - URL contains `/ath/` → `/Users/johnjm/bitbucket/hera/athena` (HA- prefix, prod branch `origin/main`)
   - URL does NOT contain `/ath/` → `/Users/johnjm/bitbucket/hera/hera` (HERA- prefix, prod branch `origin/master`)
3. Finds the source on the production branch, reading via `git show` so uncommitted local work doesn't pollute the read.
4. Compares against `origin/mqa` and `origin/dqa` to see if a fix is already in a lower environment. If yes, captures branch + commit hash + Jira ticket.

**Section B — Intercom trackers + JIRA**

5. Pulls all open conversations from the Intercom Support team (id `8163703`), keeps only bug-typed tracker tickets (where `Ticket category == "Tracker ticket"` and `ticket_type` contains "Bug").
6. For each tracker, reads the linked JIRA ticket key from `custom_attributes.jira_issue_key`.
7. Fetches the JIRA ticket (status, assignee, days-since-updated, priority) from herasolutions.atlassian.net.
8. Cross-references with the right code repo: is there an active feature branch? Are there commits on MQA / DQA / production?
9. Flags conditions worth attention:
   - JIRA done but Intercom tracker still open → **CLOSE-IN-INTERCOM**
   - ≥ 5 customer reports + JIRA hasn't started → **ESCALATE**
   - JIRA stale > 7 days → **STALE**
   - JIRA in Dev QA / Release Approved but no DQA commit → **STATUS MISMATCH**
   - Open tracker with no JIRA link → **NEEDS JIRA LINK**

**Section C — Abram's wrap-up cross-check**

10. Searches Gmail for the most recent message from `abram@hera.app` (last 24h; widens to 3 days if nothing found).
11. Extracts every `HERA-` / `HA-` ticket key from the body via regex.
12. Compares the keys Abram covered against the "in-flight" set the routine identified in Section B (plus any ticket with a JIRA-`updated` timestamp or a commit on MQA/DQA in the last 24 hours).
13. Produces three lists: what Abram covered, what was expected but missing, and any place his description disagrees with current JIRA status.

**Output**

14. Writes a dated markdown report into this folder: `YYYY-MM-DD-report.md`.
15. Posts a short chat summary: top actions, any "close in Intercom" candidates, any escalations, any wrap-up gaps to mention to Abram tomorrow, and what's new today vs yesterday.

The full step-by-step is in [`skill/SKILL.md`](skill/SKILL.md). To trigger it in a session, just type **`/daily`** — that's the entire prompt.

---

## Running it (the short version)

In a fresh terminal:

```sh
cd /Users/johnjm/bitbucket/customer-success
claude
```

Then in Claude, type:

```
/daily
```

That's the whole prompt. The `/daily` slash command expands to "Run the logrocket-daily-review skill." and the skill handles everything from there.

Equivalent natural-language phrasings also trigger the skill if you'd rather type:
- `run the daily review`
- `what's the production health today`
- `review Abram's wrap-up`

---

## Wiring the skill and slash command (one-time, per machine)

Because `.claude/` is gitignored in this repo, the canonical files live under `analysis/logrocket-error-investigation/`. To make Claude Code discover them, symlink them into the expected locations:

```sh
cd /Users/johnjm/bitbucket/customer-success

# Skill (the investigation logic)
mkdir -p .claude/skills/logrocket-daily-review
ln -sf ../../../analysis/logrocket-error-investigation/skill/SKILL.md \
       .claude/skills/logrocket-daily-review/SKILL.md

# Slash command (the /daily shortcut)
mkdir -p .claude/commands
ln -sf ../../analysis/logrocket-error-investigation/commands/daily.md \
       .claude/commands/daily.md
```

Confirm:
- `ls -la .claude/skills/logrocket-daily-review/` — should show the SKILL.md symlink.
- `ls -la .claude/commands/` — should show `daily.md` symlink.

From now on, edits to the tracked files in `skill/` and `commands/` take effect immediately.

Do this once on every machine where you want the routine available. If you open a Claude Code session here and `/daily` isn't autocompleting, the symlinks are the first thing to check.

---

## The setup constraint, and why it matters

You said it well: **report needs to land in `customer-success`, but the investigation has to read `/Users/johnjm/bitbucket/hera/{hera,athena}`.** Both of those are local Git repos on your laptop. The Intercom and JIRA data come from MCP servers configured in your Claude Code setup.

That rules out a fully remote scheduled agent (which would have neither directory). It leaves two viable patterns:

| | Local schedule (recommended) | Remote schedule |
|---|---|---|
| Where Claude runs | On your Mac | Anthropic's infra |
| Reads local Hera repos | Yes (direct file access) | No — would need to clone both repos via Bitbucket every run, plus SSH/app-password setup |
| Reads LogRocket MCP | Yes (same MCP you have today) | Yes, if MCP credentials are mirrored |
| Writes to customer-success folder | Yes (direct write + commit) | Would need to push commits — credential setup |
| Runs when your laptop is asleep | No (need it awake at the scheduled hour) | Yes |
| Setup effort | ~10 minutes | A couple of hours of plumbing |

**Recommendation: start with the local schedule.** It's the lowest-overhead path that actually meets your constraint, and it works today. If you find you want it to run while you're away, graduate to the remote pattern later — the skill itself doesn't change, only the trigger does.

---

## Option A — Local schedule via macOS launchd (recommended)

This fires Claude Code in headless mode every morning. It reads both repos, writes the report into this folder, and (optionally) commits and pushes.

### One-time setup

1. **Confirm prerequisites:**
   - Both repos cloned at `/Users/johnjm/bitbucket/hera/hera` and `/Users/johnjm/bitbucket/hera/athena`.
   - **MCP connectors all healthy** in your Claude Code config:
     - LogRocket — for Section A.
     - Intercom — for Section B.
     - Atlassian (JIRA) — for Sections B and C.
     - Gmail — for Section C (Abram's wrap-up). **If Gmail is invalidated, the routine still runs Sections A and B and tells you to reconnect.** Reconnect at chat.com → Settings → Connectors.
   - `claude` CLI on your `PATH` (run `which claude` to confirm; if missing, install from <https://claude.ai/code>).

2. **Create the launchd plist** at `~/Library/LaunchAgents/com.hera.logrocket-daily-review.plist`:

   ```xml
   <?xml version="1.0" encoding="UTF-8"?>
   <!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
   <plist version="1.0">
   <dict>
     <key>Label</key>
     <string>com.hera.logrocket-daily-review</string>

     <key>ProgramArguments</key>
     <array>
       <string>/bin/zsh</string>
       <string>-lc</string>
       <string>cd /Users/johnjm/bitbucket/customer-success &amp;&amp; /usr/local/bin/claude code --headless --prompt "/daily — then commit the new report file with message 'logrocket: daily report YYYY-MM-DD' (today's date) and push to origin/main" &gt;&gt; /tmp/logrocket-daily-review.log 2&gt;&amp;1</string>
     </array>

     <key>StartCalendarInterval</key>
     <dict>
       <key>Hour</key><integer>8</integer>
       <key>Minute</key><integer>0</integer>
     </dict>

     <key>RunAtLoad</key><false/>
     <key>StandardOutPath</key><string>/tmp/logrocket-daily-review.log</string>
     <key>StandardErrorPath</key><string>/tmp/logrocket-daily-review.log</string>
   </dict>
   </plist>
   ```

   Adjust `Hour`/`Minute` to whatever time you want the run. Adjust the path to `claude` if `which claude` shows a different location.

3. **Load it:**
   ```sh
   launchctl load ~/Library/LaunchAgents/com.hera.logrocket-daily-review.plist
   ```

4. **Test it without waiting until tomorrow:**
   ```sh
   launchctl start com.hera.logrocket-daily-review
   tail -f /tmp/logrocket-daily-review.log
   ```
   You should see Claude churn for a few minutes and then a new dated file should appear in this folder.

5. **Optional — skip the auto-commit.** If you'd rather review the report before it's committed, change the `--prompt` value to just `"/daily"` (no commit instructions). The file appears in this folder as a working-tree change and stays there until you commit it yourself.

### Daily operations

- **Where to look each morning:** Open the newest file in this folder. The top of the file has a summary table; the per-error sections are sorted by priority.
- **If it didn't run:** check `/tmp/logrocket-daily-review.log`. The launchd schedule only fires when your Mac is awake — if you closed your laptop, today's run won't happen. Either run it manually with `launchctl start com.hera.logrocket-daily-review` or move to Option B.
- **Pause the routine:** `launchctl unload ~/Library/LaunchAgents/com.hera.logrocket-daily-review.plist`. To resume, `launchctl load ...` again.

---

## Option B — Manual / on-demand invocation

If you don't want a schedule yet, you can invoke the same skill ad-hoc from any Claude Code session pointed at this repo. Type:

> `/daily`

That's the whole prompt. The skill knows where both Hera repos live, what branches to compare, and where to drop the report. Natural-language equivalents like "run the daily review" also work.

---

## Option C — Remote scheduled agent (graduate to this later)

If you eventually want the routine to fire when your Mac is asleep, you'd use the built-in `schedule` skill (or `CronCreate` tool) to register a recurring remote agent. The trade is plumbing: the remote agent has no local files, so the routine would need to:

1. Clone `hera` and `athena` from Bitbucket on each run (Bitbucket app password or SSH key stored as a routine secret).
2. Clone `customer-success`, write the report, commit, and push back.
3. Have the LogRocket MCP credentials configured in the agent.

Worth it only if you find Option A skipping runs often. The skill file itself is portable — the only thing that changes is the trigger.

---

## Files in this folder

- `YYYY-MM-DD-prompt.md` — the original prompt I used for that day's investigation (kept for traceability when a routine isn't running yet).
- `YYYY-MM-DD-report.md` — the dated report. Routine output lands here.
- `README.md` (this file) — setup guide.

## Related files

- [`skill/SKILL.md`](skill/SKILL.md) — the canonical (tracked) skill that defines how the investigation runs. Edit this if the process needs to evolve (different priority threshold, different repos to check, different report shape, etc.). After editing, no rebuild is needed — the symlink in `.claude/skills/` picks it up automatically.
- [`commands/daily.md`](commands/daily.md) — the canonical (tracked) slash command that maps `/daily` to the skill. Edit this if you want a different short trigger (e.g., add a `/morning` alias by creating a second file).
