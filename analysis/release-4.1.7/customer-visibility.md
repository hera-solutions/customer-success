# 4.1.7 — What customers will actually see

Snapshot date: 2026-07-15
Basis: 229 tickets in column 9 (Ready for RQA)

The 229 tickets don't ship to everyone equally. Broken down by customer visibility:

- **~55 tickets** ship to every tenant immediately (fixes and small improvements to live features)
- **~110 tickets** are gated behind feature flags — only the pilot / opt-in tenants with the flag on will see anything
- **~65 tickets** have no customer-visible surface at all (backend infra, test automation, MQA regressions, dev tooling)

Numbers are approximate — some tickets touch multiple areas, and Andy should confirm any borderline ones.

---

## 1. Ships to ALL customers immediately (~55 tickets)

Bug fixes and small improvements to features that are already live in production for everyone. This is the slice you can safely reference in a general-audience release note.

### Daily Roster fixes
- **HERA-8630 (Emergency)** — Roster Checklists Save & Submit error on VPL items
- **HERA-8506** — Sending roster assignments doesn't include incomplete checklist links
- **HERA-8534** — Roster reloads when Standup/General/Fleet notes are edited
- **HERA-8592** — VPL link send failures affecting Daily Roster
- **HERA-8627** — Don't show "empty" Standby Associates when replacing a Rostered Associate

### Roster Checklists
- **HERA-7269** — Duplicated checklists when Associate rostered twice on same day
- **HERA-7520** — General save-and-submit issues
- **HERA-6764** — Ability to send checklists to Hera Users (not just Associates)
- **HERA-8206** — Default templates now disabled when first assigned to a tenant

### Vehicle Photo Log (live feature)
- **HERA-8613** — Newly created VPL record not visible in filtered list

### Vehicle Management
- **HERA-4314** — New DashboardCard/Report: Vehicle Expirations & Renewals
- **HERA-6757** — Odometer reading validation

### Inventory Management
- **HERA-8502** — "Marking Orders Received" from action menu now adds the items
- **HA-2583** — Filters work on Manage Item Types page
- **HA-2628** — Inactive Items action menu no longer limited to View History
- **HA-2643** — Add/Edit Order drawer item count preserved

### Device Management
- **HA-1615** — "Remote" options now work for devices added by IMEI to Miradore
- **HA-2582** — "Not Connected" devices no longer show remote actions
- **HA-2671** — "No Phone Number Assigned" message for devices without a number

### Notifications
- **HERA-8159** — Notification exports no longer expire after one day
- **HERA-8231** — Browser Notifications delivered independently of Sms/Email

### Counselings
- **HERA-7612** — Document updates when marked refused to sign from selection menu
- **HERA-8409** — Deleted scheduled counselings no longer send Email/Text
- **HERA-8519** — Counseling Issued By column populates on Associate Record

### Performance & Coaching
- **HERA-7936** — Updated coaching template for DSB Count column
- **HERA-8587** — DC DPMO settings re-enabled in Company Settings > Coaching

### Associate Management / Records
- **HERA-8454** — Filters preserved when using Go Back button on Associate List
- **HERA-8588** — Update Conflict error fixed when editing Personal Info
- **HA-27 / HERA-7214** — UI reads displayName wherever Associate names are shown

### Company Settings / Admin
- **HERA-8178** — Phone Automation tab restored in Company Settings
- **HERA-8603** — Service Users Menu removed
- **HERA-8446** — Tenant Plan Selection fix

### Custom List / Imports
- **HERA-8455 / HA-2496** — Custom List Alternate Import Values
- **HERA-8487** — Import table no longer truncates names and shift types with ellipsis

### Miscellaneous UI/bug fixes
- **HERA-8507** — Edit Driving Info dialog crash
- **HERA-7504** — Rescue Reports missing data
- **HERA-5609** — Login token expiration handling
- **HA-915** — Phone Tree Details new entry
- **HA-2300** — Wrong selection menu
- **HA-2550** — Access-denied page instead of login redirect

### Invisible but everyone benefits (performance)
- **HA-2495** — RDS row-lock fix removing 2–29s slow queries on InvItemTypes image updates

---

## 2. Behind feature flags — pilot / opt-in tenants only (~110 tickets)

Big new functional areas. Each is gated by a tenant-level feature flag, so only customers with the flag turned on will see any of this. Confirm with Andy or CS ops which tenants have which flag before telling any specific customer their functionality is "in this release."

### Messenger V2 (largest cluster — ~55 tickets)
Flag: Messenger V2 enabled per tenant. Includes:
- Group management, read receipts, avatars, templates
- System announcement styling, clickable URLs
- Bidirectional lazy loading, responsiveness fixes
- In-app messaging for individual/bulk associates and devices (HERA-8408)
- Athena overlay bridge for group creation/member mgmt
- Mobile app parity (HAPP tickets for read receipts, group cover images, tenant name display, member count visibility, etc.)
- Backend: DynamoDB stream handler, IAM route for Associate Lambda, delivery status

Note: **Automated Coaching messages not triggering in web + mobile app messenger (HERA-8505)** — if the FF is on today, this bug affects them.

### Associate App / mobile app (~15 tickets)
Flag: Associate App enabled per tenant. Includes:
- Company-level on/off toggle (HERA-8253)
- Tenant status checks in permissions middleware (HAPP-403)
- PermissionAssociateApp flag on tenant creation (HERA-8378)
- Schedule feature (HAPP-416)
- Magic link handling, locale settings, "Please Download App" banner gating
- Mobile app ships on its own version stream (1.0.1), not 4.1.7

### Document Signing (Documenso) (~6 tickets)
Flag: Signature Requests permission FF (HERA-8267). Includes:
- Full Documenso integration (HA-858, HAPP-378, HERA-8212)
- Manage Contacts UI (HERA-8158, HA-2194) — required for signature workflows
- Magic Link support for all recipient types (HERA-8067)

### New Scheduler & Rostering (~20 tickets)
Flag: "Scheduling & Rostering" FF (HERA-8541, HERA-8542). This is the new Athena-based scheduler, not the existing Daily Roster.
- New shift cards, planning table export, shift drawer route types
- Vehicle Photo Log Flow (HA-2541)
- Associate Request document upload (HA-2576)
- Generic Messages Module with EventBridge dispatch (HA-2549)
- ETL workflow integration (HERA-8411)
- "Imported from" badge (Chrome Plugin vs Spreadsheet) (HERA-8509)
- Base component consolidation, dead code cleanup

### Hierarchical Permissions / Reporting Chain (~12 tickets)
Flag: Hierarchical Permissions FF. Phase 1/2 landing:
- Reporting Chain API and Data Model
- Role-Permission Linking, Built-in Role Defaults
- Frontend schema, Org Chart, Visibility Filtering
- Public API Permissions Sync
- Scope-based visibility filtering
- Fix: "Reports To" field displaying UUID (HERA-8585)

### GenAI / Hera AI (2 tickets)
- HA-2452 — Update UI of Associate Match Review Screen
- AI-228 — Chrome Plugin Shifts-Only Feature Flag support

### Bindbee integration (1 ticket)
- HERA-8270 — Schema for Bindbee integration (new HRIS partner)

---

## 3. Not customer-visible (~65 tickets)

No direct customer surface. These improve stability, developer velocity, or fix pre-production QA environments.

- **~13 MQA-tagged bugs** — regressions in the pre-prod QA environment. Fixing them unblocks feature-flagged features from reaching production, but no customer sees the fixes.
- **~15 Playwright / E2E test tickets** — mostly MSG project. Test automation infrastructure.
- **Kiro spec docs, steering files, onboarding documentation** — internal dev tooling
- **Env var fixes** (VITE_MESSENGER_APP_URL, SENDBIRD_WEBHOOK_URL, hlayerutil layer) — deployment configuration
- **Storybook / uilib migration, base component work** — internal component library
- **Backend Lambda / TypeScript validation / VPC config fixes** — infrastructure
- **Audit logging for CompanyScoreCard / StaffScoreCard** (HERA-8125) — backend only
- **Migrate specificPhotos field from DailyLog to RDS** (HERA-7900) — data migration

---

## Recommended customer communication approach

- **General release note (all customers):** lead with Section 1 fixes. The Daily Roster bug fixes, Vehicle Management dashboard, Inventory/Device fixes, and Notifications fixes are the safest ground.
- **Targeted comms (flag-gated tenants):** hold Messenger V2, Associate App, Documenso, new Scheduler, and Hierarchical Permissions announcements until Andy or CS ops confirms which tenants are ready to be flipped. Don't reference these broadly.
- **Do not include:** MQA fixes, test/infra work, backend-only changes. They're operationally important but confusing to reference externally.

Open question for Andy: are Messenger V2, Documenso, and Hierarchical Permissions going to be turned on for new tenants by default in 4.1.7, or is each still an opt-in per tenant? That answer changes how broadly Section 2 can be talked about.
