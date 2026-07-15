# Release 4.1.7 candidate ticket summary

Snapshot date: 2026-07-15
Source: Jira `status = "09) Ready for RQA"` (229 tickets)
Full list: [`column-9-full-list.tsv`](column-9-full-list.tsv)

## Scope

Per John's direction, treat everything in column 9 (Ready for RQA) as the candidate release manifest for 4.1.7, regardless of whether the ticket carries an explicit `fixVersion` tag.

Only 18 of the 229 tickets have `fixVersion = 4.1.7` set today. The rest are untagged. Andy should confirm which of these ship together vs stay held.

## Breakdown

### By project

| Project | Count | Notes |
|---|---:|---|
| HERA | 121 | Main Hera web app |
| HA | 77 | Athena / Hera micro-frontends |
| HAPP | 19 | Associate mobile app (some tagged `1.0.1`, likely separate release stream) |
| MSG | 11 | Messenger micro-frontend (likely separate release stream) |
| AI | 1 | Chrome plugin |

### By issue type

- New Feature/Story: 153
- Bug: 75
- Technical Debt: 1

### By priority

- Emergency - Fix Today: 1
- Urgent - Stop Other Work: 24
- Priority (See Target Release): 30
- Less Important: 1
- None (unset): 173

## Top themes (by keyword scan of summaries)

| Theme | Tickets |
|---|---:|
| Messenger V2 / chat | 59 |
| Scheduler / Roster / VPL / Checklists | 40 |
| Permissions / Roles / Reporting Chain | 18 |
| Associate App / mobile | 17 |
| Billing / Tenant / trial state | 16 |
| Playwright / E2E testing infra | 13 |
| Inventory Management | 6 |
| Device Management | 6 |
| Document Signing (Documenso) | 5 |
| Gen AI / Hera AI | 2 |
| Contacts | 2 |

## Highest-priority items

### Emergency (1)

- **HERA-8630** — Roster Checklists: Error with "Save & Submit" for VPL checklist items (unassigned)

### Urgent — Stop Other Work (24)

Cluster is dominated by Messenger V2 rollout and Associate App enablement.

- **HERA-8253** — Company Settings: Add Associate App On/Off Toggle for Company-Level Control
- **HERA-8270** — Implement Schema for Bindbee Integration
- **HERA-8408** — Messenger: Enable in-app messaging for individual/bulk associates and devices
- **HAPP-376** — Enable Messaging Feature in Associate App (read credentials from DynamoDB)
- **HAPP-407** — Mobile: Show Tenant/Company Name in Single Associate Chat
- **HAPP-413** — Mobile: Show group cover image in channel list and group header
- **HAPP-421** — Read receipt indicators + notification title shows company name for 1:1 channels
- **HA-2303** — Add IAM-Protected Internal Route for Associate Lambda to Access Messenger APIs
- **HA-2368** — Fix Responsiveness Issues in Messenger *(Bug)*
- **HA-2385** — Upload onboarding documentation for Messenger module
- **HA-2388** — Messenger: Remove unnecessary counseling permission check from New group button *(Bug)*
- **HA-2408** — Messenger: Enlarge avatar size in group info associate list
- **HA-2412** — Messenger: Show "Group Conversation" label in group chat header
- **HA-2413** — Messenger: Redesign template dropdown
- **HA-2414** — Messenger: Update icons
- **HA-2416** — Messenger: Bidirectional lazy loading for conversation list and message view
- **HA-2417** — Messenger: System Announcement styling, clickable URLs
- **HA-2419** — Messenger: Fix attachment drawer labels *(Bug)*
- **HA-2425** — Athena Messenger: Add startTyping/endTyping to CustomMessageInput *(Bug)*
- **HA-2426** — Messenger: Add/remove group members via Athena overlay bridge
- **HA-2428** — Messenger: Redesign group creation flow using Athena overlay bridge
- **HA-2435** — Messenger: Show sender's display name for user-triggered system messages
- **HA-2452** — Update UI of Associate Match Review Screen of Gen AI
- **HA-2495** — Fix InvItemTypes image UPDATE row lock contention causing 2s–29s slow RDS queries *(Bug, Shahzaib)*

### Priority (30)

Full list in TSV. Highlights:

**Daily Roster / Rostering bug fixes**
- HERA-8506 — Sending roster assignments doesn't send incomplete checklists links
- HERA-8534 — Reloads when Standup/General/Fleet notes edited
- HERA-8601 — Scheduling & Rostering accessible even with FFs off (MQA)
- HERA-8602 — Uploaded photo to a single VPL updates multiple VPLs (MQA)
- HERA-8613 — Vehicle Photo Log record not visible in filtered list

**Tenant creation / feature flags**
- HERA-8596 — CreateTenantInput error when creating tenant with feature flags (MQA)
- HERA-8594 — Roster Checklist Drawer missing fields (MQA)
- HERA-8575 — Daily Report tab shows Unknown error (MQA)

**Notifications**
- HERA-8159 — Notifications: Exports expired after one day (Hisham)

**Permissions / hierarchical roles (Phase 1/2)**
- HERA-8142, HERA-8143, HERA-8144, HA-2315

**Audit logging**
- HERA-8125 — Audit logging for CompanyScoreCard and StaffScoreCard (Shahzaib)

**Mobile app UI (HAPP)**
- HAPP-338, HAPP-377, HAPP-402, HAPP-403, HAPP-404, HAPP-406, HAPP-408, HAPP-409, HAPP-411, HAPP-412

**Messenger**
- HA-2369, HA-2399, HA-2405, HA-2406, HA-2463

## What this means for customer communication

Customer-facing changes in 4.1.7, if the full column 9 ships:

- **Messenger V2 general availability** — Big surface area: group management, read receipts, avatars, templates, system announcements, mobile parity, notifications, in-app associate messaging. This is the single biggest theme.
- **Associate App expansion** — Feature-flag toggle for company-level control, tenant status handling, magic link fixes, messaging enablement.
- **Document Signing (Documenso)** — Signature Requests permission, magic link support for all recipient types, Manage Contacts.
- **Daily Roster / VPL fixes** — Emergency VPL Save & Submit fix, checklist link sending, photo log filter fix, reload-on-edit fix, standby associate handling.
- **Scheduler & Rostering feature flag work** — Access control, feature-enabled visibility, permission defaults.
- **Inventory / Device Management** — Filters on Manage Item Types, add/edit order drawer counts, "Not Connected" device action menu, IMEI-added device remote options.
- **Billing / Tenant state** — Athena access mirrors Vue for trial-expired / churned / unpaid / unpaid-grace tenants.
- **Miscellaneous fixes** — Notifications export expiry, browser notifications gating, associate record filters, import table truncation, edit driving info crash, coaching messages not triggering, counseling document handling.

Recommendation: before drafting release notes, ask Andy to confirm the split — Hera core (HERA + relevant HA), Associate App (HAPP), and Messenger micro-frontend (MSG) likely ship on different version numbers, so the 4.1.7 tag should probably only apply to the HERA + HA subset.
