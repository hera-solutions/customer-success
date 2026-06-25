# Using Claude on the Hera Support Team

This is a quick orientation for support team members who are starting to use Claude in their day-to-day work. The goal is to make sure everyone uses Claude in a way that matches how we communicate with customers, where our knowledge lives, and how we get good answers without rework.

Read this once, then come back to it when you hit something new.

---

## 1. The writing voice rules (most important)

Claude can draft anything: customer replies, escalation briefs, KB articles, follow-ups. To make sure the draft sounds like Hera and not like a chatbot, expect these rules to apply, and call Claude out if they slip:

- **No em dashes (—) and no en dashes (–), ever.** Substitute a comma, period, colon, semicolon, parentheses, or a standard hyphen (-).
- **Warm, direct, accountable, customer-first.** Acknowledge the issue or impact first, then explain what is happening, then state the next step.
- **No corporate filler.** Never use "We appreciate your feedback," "Per our records," "As soon as possible," "We take this very seriously," "Kindly," "Please don't hesitate," "Per our policy," "Unfortunately." If you see any of those in a draft Claude gives you, reject and ask for a rewrite.
- **No fake empathy.** "I understand your frustration" reads as canned. Acknowledge the specific impact instead.
- **Be specific.** Names, timelines, owners. If you do not have a real timeline, say so honestly. Never invent one.
- **Plain English.** Sound like a capable colleague explaining the situation, not a lawyer.
- **One purpose per message.** One clear ask. Subject line should describe the substance, never "Quick question" or "Following up."

The full voice rules live in the project [CLAUDE.md](../../CLAUDE.md). Skim it once.

---

## 2. What Claude can help with on this team

| Task | What Claude does |
|---|---|
| **Drafting customer replies** | Customer complaints, bug updates, cancellation responses, feature request replies, how-to answers, post-meeting follow-ups, hard emails, pushback emails. |
| **Drafting internal docs** | Escalation briefs, KB articles, meeting summaries, status updates. |
| **Looking up Jira tickets** | Search by keyword, get full ticket details, status, priority, description, linked tickets. |
| **Looking up Intercom conversations** | Pull a specific conversation by ID, search by author or keyword, list a customer's recent conversations. |
| **Looking up Intercom articles** | Search the help center, fetch full article content. |
| **Converting customer onboarding files** | Convert AMZL vehicle exports and HRIS rosters into Hera's import templates. See `knowledge/onboarding/`. |
| **Research questions** | Pull together info from the repo, Intercom, Jira, and the web into a focused briefing. |
| **Code review or technical Qs** | Light technical assistance, mostly for understanding what engineering is doing. |

---

## 3. What Claude already knows about Hera

Claude has been trained on this project's docs, drafts, and prior conversations. You do not need to re-explain every basic. Claude already knows:

### The product

- Hera is a SaaS platform built primarily for Amazon DSPs (Delivery Service Partners) and similar last-mile delivery operations.
- Core features Hera customers use: associate management, vehicle management, daily roster, counselings, kudos, scorecards, and integrations with Amazon Logistics and Netradyne.
- "Associate" and "Driver" mean the same person in our world. The customer-facing term is usually "associate."

### The terminology

- **Associate / Driver**: the person making deliveries.
- **Counseling**: a corrective-action or feedback record on an associate. Can be negative (disciplinary), neutral (documentation), or positive (kudo-style).
- **Kudo**: a positive feedback record.
- **Daily Roster**: the day's schedule of associates, vehicles, and wave times.
- **Wave time**: the scheduled departure wave at the Amazon station.
- **Transporter ID**: Amazon's unique identifier for an associate (looks like `A39DX7EJYCK2DZ`).
- **Station code**: Amazon's facility identifier (e.g., `DRC6`).
- **Service type / Vehicle type**: the Hera taxonomy for what kind of van an associate is qualified to drive: Standard Parcel Small, Standard Parcel, Standard Parcel Large, Standard Parcel XL, Custom Delivery Van, EDV, 10,000lbs Van.

### The integrations and source systems

- **Amazon Logistics (AMZL)**: customers' master roster for both associates and vehicles. We treat AMZL as the source of truth for who drives and what they drive.
- **HRIS systems we accept imports from**: ADP, Paycom, Uzio. Each has its own export format, all documented in `knowledge/onboarding/`.
- **Netradyne**: driver telematics. Customers subscribe to Netradyne's daily alerts email, which we then import to Hera so Hera can send coaching messages automatically. There is no real-time API integration today; it is on the roadmap.
- **Documenso**: handles counseling signatures.

### The release process

Engineering tickets in Jira move through workflow steps. The ones you will see most often:

- **01) Under Construction**: dev is still writing it.
- **08) Dev QA**: dev is checking their own work.
- **09) Ready for Manager QA**: waiting for engineering management review.
- **11) Ready for Release QA**: ready for our final verification.
- **12) Release QA**: in our final verification stage before push to production.
- **Released**: shipped.

When a customer asks about a bug, the status tells you what to say: "we are looking at it," "fix is written and being verified," "shipping next release," etc. The release-qa folder has the current gameplan for what is in the next release.

### The stance on customer data

Hera does not share customer data with Amazon. This is documented in `knowledge/data-ownership-stance.md`. When customers ask about data sharing, AMZL audits, or "is Amazon seeing this," the answer is no. Pull the stance doc if you need exact language.

### Pricing and billing

Pricing, billing cycle, trial period, credits, and failed-payment flow live in `knowledge/billing-overview.md`. If a customer asks about billing, read that first. Do not improvise on pricing or refunds.

---

## 4. Files and formats Claude can read, write, and convert

A lot of support work is "the customer sent me a thing, what do I do with it." Claude can handle most file formats end to end, no manual conversion needed on your part.

| Format | Claude can |
|---|---|
| **Excel (`.xlsx`, `.xlsm`)** | Read, edit cells, add columns, fix data, write a new file, convert to CSV. Used heavily for the customer onboarding imports. |
| **CSV / TSV** | Read, parse, clean, merge, deduplicate, validate against rules, write back out. |
| **PDF** | Read text and tables, fill in form fields, place signatures or initials, merge several PDFs into one, split a PDF, rotate pages, extract images, OCR scanned PDFs to make them searchable, redact. |
| **Word (`.docx`)** | Create, read, edit, replace text, insert images, work with tracked changes, generate letterheads and memos. |
| **PowerPoint (`.pptx`)** | Create slide decks, read existing decks, edit slides, combine or split presentations. |
| **Screenshots / Images** | Look at PNGs and JPGs the customer attached. Tell you what the screenshot shows, what error is on the screen, or what a form looks like. Useful for bug reports where the customer sends a screenshot. |
| **Email threads (Gmail)** | Read full threads, search by sender or subject, list drafts, apply labels. |
| **Zoom recordings and transcripts** | Pull recent recordings, read transcripts, summarize action items from a call. |
| **Markdown, plain text, code** | Native. This is how repo docs are stored. |
| **DynamoDB CSV exports (messages, etc.)** | Read raw exports from the AWS console, convert UTC timestamps to the associate's local timezone (with DST handling), clean up phone numbers and line breaks, sort chronologically, and turn the result into a branded Hera PDF (Communication Export or Personnel Record). The full process is documented in [`reporting/pdf-generation-process.md`](../../reporting/pdf-generation-process.md). |

### File system access

- **Local filesystem**: Claude can read and write anywhere on the machine. Permissions are scoped per session.
- **Google Drive shared drives**: visible to Claude through the locally synced Drive folder at `/Users/<user>/Library/CloudStorage/GoogleDrive-...`. Saving a file there syncs it back to Drive automatically.
- **The repo**: `customer-success` at Bitbucket. Claude can read, edit, commit, and push.

### Common file workflows

- **"Convert this AMZL vehicle file for {company}"**: Claude runs the locked conversion, saves the output to `Imports/Tenants/{company}/`, flags anything questionable.
- **"Read this PDF the customer sent and tell me what it says about X"**: extract text and pull out the relevant section.
- **"Fill out this form with these values"**: works for PDF forms and Word templates.
- **"Look at this screenshot and tell me what error they are seeing"**: useful when the customer attaches a screenshot to an Intercom message.
- **"Take the action items out of this Zoom transcript"**: summarize what we committed to in a call.
- **"Merge these three signed counseling PDFs into one document"**: PDF tooling handles it.

If you have a file format that is not listed, ask Claude. It can usually handle anything text-based, and many binary formats with the right tooling.

---

## 5. What Claude should NOT do

- **Send anything customer-facing without your review.** Claude drafts. You send. Always read and edit before clicking send.
- **Invent commitments.** Refund amounts, ship dates, policy text, comp offers, integration timelines. If you have not been told it, do not let Claude write it.
- **Guess at facts.** If Claude does not know the answer, it should look it up or say so. If you see Claude making things up, push back.
- **Skip the apology when we are late.** If we missed an SLA or delayed a reply, the email owns it in the opening sentence. No burying it.
- **Use legalese unless required.** "Pursuant to," "in furtherance of," "as per our terms," etc. We are not lawyers.
- **Promise an integration, feature, or release date.** Roadmap status: planned, under consideration, or not planned. Nothing more specific unless engineering has given you a date.

---

## 6. Where our knowledge lives in the repo

Claude can read all of these. So can you.

### The repo (Bitbucket: `customer-success`)

Cloned locally at `/Users/<your-user>/bitbucket/customer-success/`.

- **[CLAUDE.md](../../CLAUDE.md)**: Project instructions. Working style, voice rules, communication logic for every scenario. The master.
- **`knowledge/onboarding/`**: All the customer onboarding work:
  - `import-templates.md`: The three customer import templates (Vehicles, Staff, Devices), required fields, global rules (dates are always MM/DD/YYYY).
  - `vehicles-amazon-dsp-mapping.md`: How AMZL vehicle exports map to our Vehicles template.
  - `staff-import-mapping.md`: How HRIS + AMZL Associates files merge into our Staff template.
  - `*-convert.py`: Reusable conversion scripts.
- **`knowledge/billing-overview.md`**: Pricing, billing cycle, trial, credits, failed-pay flow.
- **`knowledge/intercom-overview.md`**: How we use Intercom.
- **`knowledge/templates/`**: Canned response templates for common scenarios.
- **`knowledge/email-drafts/`**: Drafts of customer emails (kept after sending, named by date and topic).
- **`knowledge/release-qa/`**: Release plans and bug tracking notes for upcoming releases.

### Google Drive

- **`Shared drives/Imports/Templates/`**: The blank Hera import templates (Vehicles, Staff, Devices).
- **`Shared drives/Imports/Tenants/<Company Name>/`**: Every customer's converted import files. One folder per customer. Files named `<Company Name> - Vehicles.csv`, `<Company Name> - Staff.csv`, `<Company Name> - Devices.csv`.

### External systems Claude can read

- **Intercom**: conversations, contacts, companies, articles, search.
- **Jira (`herasolutions.atlassian.net`)**: search, full ticket details, links.
- **Confluence**: pages and spaces.
- **Gmail**: drafts, labels, threads.
- **Zoom**: recordings and transcripts.
- **PDF and Office files**: read, fill, sign, convert.

---

## 7. How to ask Claude productively

The quality of the answer depends almost entirely on what you give Claude up front.

### Always include (when relevant)

- **The customer name and company.** Spelled out.
- **The Intercom conversation ID or URL** (find it in the Intercom URL bar, looks like `https://app.intercom.com/a/inbox/_/inbox/conversation/21547...`).
- **The Jira ticket key or URL** if engineering already has one.
- **What you are trying to do.** "Draft a reply" vs "tell me what is going on" vs "find the related ticket" produce very different outputs.
- **Any constraints.** "Keep it under 6 sentences." "Do not promise a date." "Match this customer's tone." "Make it shorter."

### Useful phrases

- "Draft a reply to {customer} in conversation {id}."
- "Look up Jira ticket {key} and summarize the status in plain English."
- "What is going on with {topic}? Pull everything we know."
- "Convert this customer's onboarding file for {company name}." (Claude will ask the company name if you forget.)
- "Save this to memory."
- "Forget what we discussed about X."
- "That is wrong. The correct rule is Y."

### When Claude gets it wrong

- Tell it. "No, the status is `Inactive - Misc`, not `Inactive`."
- Ask Claude to save the correction. "Commit that to memory so we never have this conversation again."
- Real corrections become durable rules. Repeated corrections mean Claude is missing context. Add the context to the repo or to memory.

---

## 8. Common workflows

### Drafting a customer reply

1. Open the Intercom conversation. Note the ID and the customer's name.
2. Ask Claude: "Draft a reply to {customer} in Intercom conversation {id}."
3. Add any constraints up front: keep it short, do not invent timelines, etc.
4. Claude will read the conversation, ask for anything missing, and produce a draft.
5. Read the draft. Edit. Send.

### Responding to a customer bug report

1. Get the conversation context (Intercom ID).
2. Ask Claude to find the matching Jira ticket. "Customer is reporting X. Find the matching Jira ticket."
3. Claude will search Jira and report status (under construction, in dev QA, in release QA, etc.).
4. Ask Claude to draft a reply that explains the bug in plain language, says where it is in our process, and offers a workaround if one exists.
5. Never include the Jira ticket number in the customer reply. Internal-only.

### Converting an onboarding file (Vehicles or Staff)

1. Confirm the company name with the customer.
2. Send Claude the AMZL export (and HRIS export for Staff).
3. Claude will ask for the company name if you have not given it.
4. Claude runs the conversion using the rules in `knowledge/onboarding/`, validates the output, and saves the file to `Imports/Tenants/<Company Name>/<Company Name> - Vehicles.csv` (or Staff).
5. Claude flags anything questionable: missing fields, duplicates, mismatched emails between HRIS and AMZL, possible same-person records under different names.
6. You review the flags and decide.

### Escalating a bug to engineering

1. Ask Claude to write an escalation brief using the format in CLAUDE.md (escalation header, account, value, severity, situation, root cause, actions taken, current risk, recommended action).
2. Provide: the Intercom conversation ID, any prior support history, the customer impact, and what you have already tried.
3. Send the brief to the right channel (usually Jira or chat with engineering).

### Generating a Communication Export PDF (DynamoDB messages)

1. Pull the messages CSV from the DynamoDB console for the associate (or have engineering send it).
2. Give Claude: the CSV file, the associate's full name, the DSP name, and the associate's timezone (Pacific, Eastern, etc.).
3. Claude will: convert UTC timestamps to the local timezone with the right DST rules, strip the `+1` from phone numbers, replace `\n` with `*line break*` inline, mark incoming messages, sort chronologically, and produce a landscape, Hera-branded PDF with logo, header, alternating row colors, and a footer.
4. The file lands in the customer's reporting folder. Review and send.
5. Claude does the work end to end. You will not be handed a Python command to run.

### Generating a Personnel Record PDF

1. Gather the source data Claude needs for the associate: communications, counselings, kudos, Netradyne events, scorecards, attendance, etc. Whatever sources HR or legal asked for.
2. Tell Claude the associate's name, DSP, status (active or terminated), and what sections to include.
3. Claude builds one Hera-branded landscape PDF with section-bar headers, color-coded data, and `KeepTogether` rules so sections do not break across pages.
4. Hand the PDF to whoever requested it (HR, legal, the customer).

The full design rules (palette, layout, field mapping, sort order) live in [`reporting/pdf-generation-process.md`](../../reporting/pdf-generation-process.md). If anything ever looks off in a generated PDF, that doc is the source of truth.

### Drafting a hard email

1. Tell Claude what is true (the situation), what you want to communicate (the position or ask), and any sensitive context.
2. Claude will produce a draft that names the issue, owns what is ours to own, and has a clear ask.
3. Read it. The hard-email logic in CLAUDE.md keeps these tight, but you know the relationship better than Claude does. Edit accordingly.

---

## 9. Things to watch for

- **Em dashes and en dashes.** They sneak in. Call them out.
- **Filler phrases.** "We appreciate your patience." "We take this very seriously." Reject and rewrite.
- **Vague timelines.** "Soon," "as soon as possible," "in the coming weeks." Reject. Either specific or honestly unknown.
- **Over-promising.** Refunds, credits, features, dates. If you did not say it, do not let Claude write it.
- **Wrong status terms.** Hera Staff `Inactive` should be `Inactive - Misc`. Hera vehicle types are: Standard Parcel Small, Standard Parcel, Standard Parcel Large, Standard Parcel XL, Custom Delivery Van, EDV, 10,000lbs Van. If Claude uses something off-list, flag it.
- **Stale information.** Claude reads the current state of files, but memory can get out of date. If a fact looks wrong, ask Claude to verify against the actual source.

---

## 10. Three things to remember

1. **Claude drafts; you send.** Always review.
2. **Specifics in, specifics out.** Give Claude the IDs, names, and context. Vague asks produce vague answers.
3. **Correct Claude when it is wrong, and tell it to save the correction.** That is how Claude gets better at this project over time.

If you hit something this guide does not cover, ask John, and we will add it here.
