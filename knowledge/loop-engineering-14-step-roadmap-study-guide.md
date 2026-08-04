# Loop Engineering: The 14-Step Roadmap from Prompter to Loop Designer

**Author:** Codez (@0xCodez) · Posted Jun 9
**Source:** X (Twitter) long-form article
**Engagement shown:** 126 replies · 1.2K reposts · 6.5K likes · 7.8M views
**Author bio:** Content creator | AI researcher & builder | AI insights from 2030 | @zscdao

> **[Screenshot — Header / cover image]**
> A light cream banner that sits at the very top of the article. On the upper-left in small orange text: a starburst/asterisk logo followed by "CLAUDE CODE DEEP DIVE." Below it, in very large bold black text, the title "Loop engineering" stacked on two lines. Underneath, in small monospace orange/gray text: "14-step roadmap from 0 to loop designer." On the right side is a dark "terminal window" mockup with red/yellow/green traffic-light dots. Inside the terminal, a prompt reads `> /loop` in green. Below the prompt is an orange pixel-art robot mascot, and to its right a numbered list: "1. Plan — Define the loop", "2. Build — Create the system", "3. Run — Execute & observe", "4. Learn — Iterate & improve." To the right of the terminal, four small labeled callout chips connect out via lines: "/goal" (target icon), "skill.md" (document icon), "Worktrees" (branch icon), and "MCP" (the label reads "MPC" in the image, a typo). This image appears directly above the article title.

---

## Introduction

The article opens by arguing that most developers still drive their coding agents manually: they type a prompt, wait, read the resulting diff, then type again. The claim is that roughly nine out of ten builders have never written a loop that prompts the agent on their behalf — no automation, no state file, no verifier, no schedule.

The central thesis: the point of leverage has shifted away from *typing prompts* toward *designing systems that prompt for you*. This piece presents itself as a 14-step roadmap for making the transition from "prompter" to "loop designer."

A callout invites readers to follow the author's LinkedIn for AI content.

> **Callout (blockquote in original):** "Follow my Linkedin to get fresh AI alpha: linkedin.com/in/lev-deviatkin"

The roadmap is described as sourced from Anthropic's engineering docs, Addy Osmani's long-form writing on loop engineering, and recent measurement studies. It is organized into three tiers: (1) determine whether you actually need a loop, (2) learn the five building blocks, and (3) build the smallest loop that works without harming you. The tagline: **"14 steps. 3 tiers. Stop prompting. Start designing."**

> **[Screenshot — "What a loop actually does" diagram]**
> A light-background flow diagram titled "What a loop actually does." Across the top is a row of six labeled tab/header chips: AUTOMATIONS, WORKTREES, SKILLS, CONNECTORS, SUB-AGENTS, and STATE FILE (the last one highlighted in orange). Below that is a left-to-right pipeline of five boxes connected by arrows, each with a bold title and an italic gray subtitle:
> 1. **Find work** — *A loop finds the work*
> 2. **Hand it to the agent** — *Bounded job, right context*
> 3. **Check result** — *Test, type error, failing build*
> 4. **Record what happened** — *State survives between runs*
> 5. **Decide next move** — *Stop, retry, or hand off*
> An orange "NEXT MOVE" arrow loops from the last box back around to the first, indicating the cycle repeats. At the bottom, inside bracket marks, a separate wide bar shows an orange square icon labeled "State file" with the italic note "The agent forgets each run. The file does not." This image appears in the intro, just before the "14 steps. 3 tiers." tagline.

> **Caption beneath the diagram:** "14 steps. 3 tiers. Stop prompting. Start designing."

---

# PART 1 · The Why & The Test

## 01. Loop engineering is replacing yourself as the prompter.

For about two years, the workflow with a coding agent has been: write a prompt, supply context, read the output, write the next prompt — with the human holding the tool the entire time. The author argues that era is ending.

Loop engineering is defined as building a small system that **finds** the work, **hands** it to the agent, **checks** the result, **records** what happened, and **decides** the next move — autonomously. You design that system once, and from then on the system does the prompting.

The article notes that Addy Osmani breaks loop engineering into six parts (shown in the table below).

> **[Screenshot — Six-part primitives comparison table]**
> A clean four-column table on a white background comparing loop primitives across two tools. Column headers: **Primitive**, **Job in the loop**, **Codex app**, **Claude Code**. The rows:
>
> | Primitive | Job in the loop | Codex app | Claude Code |
> |---|---|---|---|
> | Automations | discovery + triage on a schedule | **Automations tab**: pick project, prompt, cadence, environment; results land in a Triage inbox; `/goal` for run-until-done | Scheduled tasks and cron, `/loop`, `/goal`, hooks, GitHub Actions |
> | Worktrees | isolate parallel features | Built-in worktree per thread | `git worktree`, `--worktree`, `isolation: worktree` on a subagent |
> | Skills | codify project knowledge | **Agent Skills** (`SKILL.md`), invoked with `$name` or implicitly | **Agent Skills** (`SKILL.md`) |
> | Plugins / connectors | connect your tools | Connectors (MCP) plus plugins for distribution | MCP servers plus plugins |
> | Sub-agents | ideate and verify | **Subagents** defined as TOML in `.codex/agents/` | Task subagents in `.claude/agents/`, agent teams |
> | State | track what's done | Markdown or Linear via a connector | Markdown (`AGENTS.md`, progress files) or Linear via MCP |
>
> Certain product names ("Automations tab," "Agent Skills," "Subagents") are rendered in blue as if they were links. This image appears in section 01.

The article then cites that Anthropic engineers now merge roughly eight times as much code per day as in 2024 — while noting Anthropic itself describes this as "almost certainly an overstatement of the true productivity gain." The author concedes the number is debated, but argues the underlying mechanism is not: the leverage point moved from typing prompts to designing the loop that prompts.

## 02. Run the 4-condition test *before* you build anything.

The argument here is that loops only justify their cost under four conditions, and missing any one makes the loop cost more than it returns. This framing is attributed to AlphaSignal's analysis.

> **[Screenshot — "So do you actually need one?" decision flow]**
> A light-background decision diagram titled "So do you actually need one?" A left-to-right row of five small numbered boxes (01–05) connected by solid arrows, each with a bold title and italic gray subtitle:
> - **01 The task repeats** — *Happens at least weekly*
> - **02 Verification is automated** — *Test, type check, build, linter*
> - **03 Token budget absorbs the waste** — *Retries cost even when no ship*
> - **04 Agent has senior engineer tools** — *Logs, repro env, run the code*
> - **05 Answer yes to all four** — with an orange "PASS" chip
> The flow then leads to a dark box on the far right labeled "Build the loop." Below the main row, dashed lines branch down to two more boxes: "Miss one box" → "Manual prompt." A small legend in the lower-left reads: "SOLID = all conditions pass" and "DASHED = keep manual." Lower-right text: "Run the test before you build." This appears in section 02.

**The four conditions in plain English:**

1. **The task repeats.** A loop spreads its setup cost across many runs. For a one-off job, a good single prompt is faster and cheaper. If work doesn't recur at least weekly, it's a script you ran once — not a loop.
2. **Verification is automated.** The loop needs something that can fail the work without you present — a test suite, type checker, linter, or build. Without an automated check, you're back to reading every diff manually, which is exactly the job the loop was meant to remove.
3. **Your token budget can absorb the waste.** Loops re-read context, retry, and explore, burning tokens regardless of whether a run ships. The technique scales with budget — obvious to those with effectively free tokens, reckless to those on a metered plan.
4. **The agent has a senior engineer's tools.** Logs, a reproduction environment, and the ability to run code and see what breaks. Without these, the loop iterates blind.

## 03. Who wins, who loses. Loops favor whoever can spend.

The economics aren't universal. People who call loop engineering "obvious" usually have unmetered tokens; those for whom it's "reckless" are typically on a ~$20 consumer plan running heavy verification loops, risking limits or a surprise bill.

**Who benefits in practice:**
- Teams with repetitive, machine-checkable work *and* the budget to run it — continuous test triage, dependency bumps, lint-and-fix passes, issue-to-PR drafts on a codebase with strong test coverage.
- Codebases with strong existing test suites. The heuristic: if a junior engineer could do the task from a checklist and a test suite would catch their mistakes, a loop fits.
- Async-first teams already using multi-agent patterns, for whom routines supply the missing orchestration layer.

**Who should skip it today:**
- Solo builders on consumer plans — the token bill arrives before the productivity gain.
- Anyone working on code with no automated verification (a loop with no real check is just the agent agreeing with itself repeatedly).
- Teams whose real bottleneck is review capacity, not typing speed — a loop generates more code and only lengthens the review queue.

For one-off tasks, exploratory work, or anything where "done" is a judgment call, a single well-aimed prompt still wins. The author's "honest version": loop engineering is real, but most developers don't need it yet.

## 04. The 30-second loop check.

Where step 2 was the strategic decision, this is the tactical checklist to run on a specific task before turning it into a loop. Miss one box and keep it as a manual prompt.

1. **The task happens at least weekly.** Less than weekly → setup cost never amortizes.
2. **A test, type check, build, or linter can reject bad output.** No automated gate → the agent grades its own homework.
3. **The agent can run the code it changes.** No reproduction environment → iteration is blind.
4. **The loop has a hard stop** (token budget, iteration count, or time limit). Without one, it runs until someone notices the bill.
5. **A human reviews before merge, deploy, or dependency changes.** Anything irreversible needs a human approval gate before action.

**Good first loops:**
- **CI failure triage** — nightly; scan failures, classify causes, draft fix PRs for the easy ones.
- **Dependency bump PRs** — weekly; scan for updates, test compatibility, open PRs.
- **Lint-and-fix passes** — on every PR-open event, apply style fixes automatically.
- **Flaky test reproduction** — loop until a theory survives the test.
- **Issue-to-PR drafts** on code with strong tests, where bad output gets rejected by the suite.

**Bad first loops (these need a human in the chair):**
- Architecture rewrites
- Auth or payments code
- Production deploys
- Vague product work
- Anything where "done" is a judgment call

---

# PART 2 · The 5 Building Blocks

## 05. Automations: the heartbeat.

Automations are what make a loop an actual loop rather than a single run. They fire on a schedule, on an event, or on a trigger condition — the heartbeat everything else hangs off.

**How it looks in the two tools that matter:**
- **Codex.** The Automations tab — pick a project, set a prompt, set a cadence, and choose local checkout or a background worktree. Runs that find something land in a Triage inbox; runs that find nothing archive themselves.
- **Claude Code.** Three primitives that compose into the same shape: `/loop` for session-scoped cadence, Desktop scheduled tasks for restart-survival, and Routines for laptop-off cloud runs — paired with hooks for lifecycle events.

**Two primitives that separate working loops from expensive ones:**
- `/loop` re-runs on a cadence — use it when you want regular checks regardless of state.
- `/goal` keeps going until a condition you wrote is actually true. A separate small model checks completion, so the agent that wrote the code isn't the one grading it. This is the **maker-vs-checker split applied to the stop condition itself.**

> **[Screenshot — "/loop vs /goal" comparison infographic, credited @linas.beliunas]**
> A light-cream infographic split into two stacked panels, each titled with an orange starburst icon.
> **Top panel — "Without /goal — You Are the Loop":** a winding sequence of orange-outlined boxes representing a manual back-and-forth: "You prompt" → "Claude works" → "Claude stops" → "You review" → "You prompt again" → "Claude works" → "Claude stops" → "You review again." A pink summary bar at the bottom reads: "You are the bottleneck. Every turn requires your input to continue."
> **Bottom panel — "With /goal — Claude Closes the Loop":** a green-outlined flow: "You set the goal" → "Claude works" → "Evaluator checks" → branches "Done ✓" → "Goal cleared", or "Not done" → "Claude starts next turn" (which loops back to "Claude works"). A green summary bar reads: "You are removed from the loop. Claude works until the condition is met."
> At the very bottom is the orange starburst "Claude" wordmark and an attribution avatar/handle "@linas.beliunas." This appears in section 05.

> **Caption beneath the infographic:** "This is the maker-vs-checker split applied to the stop condition itself."

**Code block (labeled `python` in the original; content is a Claude Code command transcript):**

```python
> /loop 30m /goal All tests in test/auth pass and lint is clean.
Scan src/auth for new failures, propose fixes in claude/auth-fixes,
open draft PR when goal condition holds.

▲ Claude
CronCreate(*/30 * * * * : auth quality loop)
Stop condition: tests pass + lint clean (verified by checker)
✓ Scheduled. Will continue past intermediate completions
until /goal condition is met by independent checker.
```

## 06. Worktrees: parallel without chaos.

As soon as more than one agent runs, files start colliding — the same problem as two engineers committing to the same lines without coordinating. A **git worktree** fixes this: a separate working directory on its own branch that shares the same repo history, so one agent's edits literally cannot touch another's checkout.

> **[Screenshot — "Git Worktrees" animated GIF / video thumbnail]**
> A dark-themed diagram (marked with a "GIF" badge and a play button in the lower-left corner) titled "Git Worktrees." At the top-left is a folder icon labeled "Repo." Dashed lines branch out to three labeled branches: "main branch" (folder `.../main`), "feature-a branch" (folder `.../feature-a`), and "feature-b branch" (folder `.../feature-b`). Below each is a shaded panel — blue for main, green for feature-a, tan/yellow for feature-b — each showing a checked branch label ("✓ main", "✓ feature-a", "✓ feature-b") with small commit-node graphs (colored dots connected by vertical lines) representing independent commit histories. The animation implies parallel work happening across the three isolated checkouts. This appears in section 06.

**How it shows up in both tools:**
- **Codex** builds in worktree support — several threads hit the same repo at once without bumping into each other.
- **Claude Code** exposes `git worktree` directly, a `--worktree` flag to open a session in its own checkout, and an `isolation: worktree` setting on subagents so each helper gets a fresh, self-cleaning checkout.

The closing caveat: worktrees remove the mechanical collision, but **you are still the ceiling** — your review bandwidth decides how many parallel agents you can actually run, not the tool.

## 07. Skills: write project knowledge once. Read on every run.

A Skill lets you stop re-explaining the same project context every session. Both tools use the same format: a folder containing a `SKILL.md` with instructions and metadata, plus optional scripts, references, and assets.

Why this matters for loops specifically: without skills, a loop re-derives the whole project context from zero every cycle. With skills, intent compounds — conventions, build steps, and hard-won "we don't do it this way because of that one incident" lessons are written once on the outside and read by every run.

**Code block (labeled `python` in the original; content is a `SKILL.md` file):**

```python
name: ci-triage
description: Classify CI failures by root cause (env, flake, real bug,
dependency, infra), draft fixes for the easy ones, escalate the rest.
Trigger whenever a workflow run fails or on the morning triage loop.
---

# CI triage skill

## Classification rules
- env: missing secret, wrong env var, infra not provisioned. # human
- flake: passes on retry without code change. # retry once, then file
- bug: deterministic failure tied to recent commit. # draft fix
- dependency: failure tied to a version bump. # draft rollback
- infra: timeout, OOM, runner issue. # escalate

## Fix patterns
- Auth tests → check src/auth/middleware first
- Database tests → verify migration applied in CI env
- E2E tests → check selectors against the latest UI snapshot

## Never do
- Disable failing tests — always file as escalation instead
- Modify CI config without human approval
- Touch src/payments/ or src/billing/ (in claude/permissions.md)

## State
Update STATE.md after each run: file paths checked, classifications,
PRs opened, items escalated.
```

## 08. Connectors: the loop touches your real tools. Via MCP.

A loop that can only see the filesystem is tiny. **Connectors**, built on the Model Context Protocol (MCP), let the agent read your issue tracker, query a database, hit a staging API, or drop a message in Slack. Both Codex and Claude Code speak MCP, so a connector written for one usually works in the other.

This is the difference between an agent that says "here is the fix" and a loop that opens the PR, links the Linear ticket, and pings the channel once CI is green. Connectors are what let the loop act inside your actual environment rather than just describe what it would do.

> **[Screenshot — "Connectors" settings panel UI]**
> A screenshot of a "Connectors" modal/dialog over an orange app background (looks like the Claude desktop app). The dialog header reads "Connectors" with subtext "Unlock more with Claude when you connect your favorite tools" and a "Manage connectors" link. There are two tabs — "Web" (active) and "Desktop extensions" — plus a search box on the right. Below is a two-column grid of connector cards, each with a logo, a name, and a one-line description, and a "+" button (some show a checkmark indicating already connected):
> - **Asana** — Connect to Asana to coordinate tasks, projects, and goals
> - **Atlassian** — Access Jira & Confluence from Claude
> - **Canva** — Search, create, autofill, and export Canva designs from a prompt
> - **Cloudflare** — Build applications with compute, storage, and AI
> - **Gmail** — Draft replies, summarize threads, & search your inbox
> - **Google Calendar** — Understand your schedule and optimize your time (shows a checkmark)
> - **Google Drive** — Find and analyze files instantly (shows a checkmark)
> - **Intercom** — AI access to Intercom data for better customer insights
> - **Linear** — Manage issues, projects & team workflows in Linear
> - **Notion** — Connect your Notion workspace to summarize, search, and move faster
> - **PayPal** — Access PayPal payments platform using PayPal's MCP server
> - **Plaid** — Monitor, debug, and optimize your Plaid integration
> This appears in section 08.

**The connectors that pay back fastest for loop work, in order:**
1. **GitHub** — read repos, create branches, open PRs, comment on issues, react to webhook events. The single biggest day-one win for any code loop.
2. **Linear or Jira** — update tickets as the loop progresses, link PRs back to issues, auto-close items when verification passes.
3. **Slack** — post triage results, ping humans on escalations, summarize overnight runs in the morning.
4. **Sentry / your error tracker** — let the loop investigate live alerts and draft fixes for high-frequency ones.

## 09. Sub-agents: keep the maker away from the checker.

The most useful structural move in a loop is splitting the agent that *writes* from the agent that *checks*. Osmani's framing: the model that wrote the code is "way too nice grading its own homework." A second agent with different instructions — and sometimes a different model — catches what the first one talked itself into.

The author identifies this as the **evaluator-optimizer pattern** from Anthropic's December 2024 engineering post, now circulating under a new name: one model generates, another critiques, repeat. The point made is that vocabulary going viral in 2026 was documented eighteen months earlier.

> **[Screenshot — Evaluator-optimizer pattern diagram]**
> A light-background flow diagram. On the far left, a pink rounded node labeled "In." An arrow points to a green box "LLM Call Generator." A curved arrow labeled "Solution" leads to a second green box "LLM Call Evaluator." From the evaluator, an arrow labeled "Accepted" points to a pink node "Out" on the far right. A return loop labeled "Rejected + Feedback" curves back from the evaluator to the generator, indicating the cycle repeats until acceptance. This appears in section 09.

**How sub-agents land in both tools:**
- **Codex** only spawns subagents when you ask, runs them concurrently, then folds their results back into one answer. You define your own agents as TOML files in `.codex/agents/` — name, description, instructions, and optional model and reasoning effort. (Example given: a security reviewer can be a strong model on high effort while the explorer is a fast read-only model.)
- **Claude Code** does the same with subagents in `.claude/agents/` and agent teams that pass work between them. The usual split: one agent explores, one implements, one verifies against the spec.

Why it matters inside a loop: the loop runs while you aren't watching, so a verifier you actually trust is the only reason you can walk away. The trade-off: sub-agents burn more tokens because each runs its own model and tool work — spend them where a second opinion is worth paying for.

---

# PART 3 · Build It Right or Don't Build It

## 10. The state file. The agent forgets. The file does not.

This is described as the piece that "sounds too dumb to matter" but is actually the spine of every working loop — a markdown file, a Linear board, or a JSON state that lives outside the single conversation and holds what's done and what's next.

Why it matters: agents have short memory by default, so what they learn this session is gone tomorrow unless it's written down. Osmani's rule, paraphrased: the agent forgets, the repo does not. A loop without persistent state restarts every run; a loop with state resumes.

**Code block (labeled `json` in the original; content is a markdown-style state file):**

```json
# Loop state · ci-triage

## Last run
2026-06-09 03:30 UTC · 7 failures classified, 3 fixes drafted, 4 escalated

## In progress
- claude/fix-auth-token-refresh — tests passing locally, awaiting CI
- claude/fix-flaky-payment-webhook — retry pattern applied, monitoring

## Completed today
- claude/bump-axios-1.7.4 → merged (CI green, deps loop verified)
- claude/lint-fix-pass-june-9 → merged

## Escalated to humans
- src/billing/refund.ts — tests failing in 3 ways, root cause unclear
- ci/staging-runner — infra timeouts, not a code issue

## Lessons learned (write here, not in chat)
- 2026-06-08: PowerShell hits TLS 1.2 issue on this Windows runner. Use bash.
- 2026-06-07: tests/e2e/checkout requires Stripe webhook secret in env. Skip if missing.

## Stop conditions met since last review
- /goal "all tests pass + lint clean" achieved on commit 3a7b8c1 at 02:14 UTC
```

**Two patterns for where the state file lives:**
- **Markdown in the repo** — `STATE.md` at the root or inside `.claude/`. Version-controlled, simple, diff-readable. Best for solo or small-team work.
- **External system** (Linear, GitHub Issues, a database) — survives across repos, queryable, supports team-wide visibility. Best for production loops where multiple humans need to see what the loop is doing.

For long-running loops at risk of drifting, the article advises pairing the state file with a standing high-level spec — `VISION.md` or `AGENTS.md` — that the agent rereads each run. The distinction: **state tells the agent where it is; the spec tells it where to go.**

## 11. The minimum viable loop.

If you passed the 4-condition test in step 2, build the smallest loop that works before adding anything fancy — four parts, no swarm.

> **[Screenshot — "The minimum viable loop" diagram]**
> A light-background diagram titled "The minimum viable loop" with an orange subtitle chip "FOUR PARTS, NO SWARM." A left-to-right row of four numbered boxes (01–04) connected by arrows, each with a bold title, an italic gray subtitle, and a small inset chip:
> - **01 One automation** — *Scheduled run, cadence, stop condition* — chip: `/loop · /goal`
> - **02 One skill** — *Project context the agent would otherwise re-derive* — chip: `SKILL.md`
> - **03 One state file** — *What is done and what is next* — chip: `Markdown / Linear`
> - **04 One gate** — *Test, type check, or build fails bad work* — chip: `CAN SAY NO` (highlighted orange)
> An orange "NEXT RUN" arrow loops from box 04 back to box 01. Below the row: "Get one manual run reliable, turn it into a skill, wrap it in a loop, then schedule it." At the bottom is a metrics bar with an orange chart icon labeled "Measure cost per accepted change" (subtitle: *not tokens spent or tasks attempted*) showing sample figures: COST / ACCEPTED = $12.37, ACCEPTED = 128, REJECT RATE = 17%, MTTA (MIN) = 14.2, LEAD (HR) = 6.8. This appears in section 11.

**The four parts, in plain language:**
- **One automation.** A scheduled run that fires on a cadence and stops on a clear condition. Use `/loop` in Claude Code or an automation in Codex; pair with `/goal` when it should run until a stated condition holds.
- **One skill.** A single `SKILL.md` storing the project context the agent would otherwise re-derive every run.
- **One state file.** A markdown file or Linear board recording what's done and what's next, so tomorrow's run resumes instead of restarting.
- **One gate.** The test, type check, or build that automatically fails bad work — the part that decides whether the loop helps or just spends.

**Order matters:** get one manual run reliable first → turn it into a skill → wrap it in a loop → then schedule it. Skipping ahead is how loops fail in production.

The key metric stressed: **cost per accepted change** — not tokens spent, tasks attempted, or loops scheduled. If your accepted-change rate is below 50%, you're doing the review work the loop was supposed to save, and the loop is losing.

## 12. The Ralph Wiggum loop. Loops that fail quietly.

Engineer Geoffrey Huntley documented and named this failure mode: an agent meant to emit a completion token only when finished emits it early, so the loop exits on a half-done result. The loop looks like it succeeded because the gate said "pass," but the work is incomplete. Named after the Simpsons character who cheerfully declares "I'm helping!" while contributing nothing.

**Note:** The source extraction cut off mid-section 12. Sections 13 and 14 were not captured. Based on the article's trajectory, these likely cover measurement/metrics and a closing iteration framework. If the full article is accessed later, this file should be updated with the remaining content.
