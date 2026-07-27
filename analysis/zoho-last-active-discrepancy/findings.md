# Zoho "Last Active" vs. Hera login discrepancy

**Date:** 2026-07-27
**Trigger:** Liz flagged that Zoho CRM "Last Active" (7/22) for Amazing Customer Experience Logistics LLC did not match the Hera Users page, where no one appeared to log in on 7/22. Her read: "they're not using the platform."
**Account:** Amazing Customer Experience Logistics LLC | Short Code MUXL | Tenant_ID `4d92e8ad-73b9-4eda-b440-8d903abbc673` | Group `f4c3f44e-3c93-406c-8af7-13748dec927f` | Status: Trial (expires 2026-09-10) | AMP Customer

## Conclusion

Zoho's "Last Active" and the Hera Users-page login date measure different things, so they disagree by design. The account is **not** idle: one user is actively entering data.

## Where each field comes from

| Signal | Value (2026-07-27) | Source of truth |
|---|---|---|
| Zoho custom field `Last_Active1` (display label "Last Hera Activity" as of 2026-07-27, was "Last Active") | 7/24 (was 7/22 when Liz looked) | Last **activity/action** on the tenant, i.e. max AuditLog `createdAt`. Written by the Hera -> Zoho sync. API name `Last_Active1` unchanged by the label rename, verified still resolving. |
| Zoho native `Last_Activity_Time` | 7/27 07:01 | Last touch of the **CRM record itself**, including our own automated sync (Modified_By = Hera Solutions / no-reply@hera.app). Not a usage signal. Ignore. |
| Hera Users page `User.lastLogin` | 7/17 (Jose Latorraca); all others Jan 2026 or never | Last **fresh authentication**. Does not update during an active session. |
| Hera AuditLog activity | 7/17, 7/22, 7/24 (Jose Latorraca) | Real in-app UI actions. |

`Last_Active1` matched the latest AuditLog action date on both observations (7/22, then 7/24). That confirms the sync reads last activity, not last login.

## Why the Users page showed "no login on 7/22"

`User.lastLogin` only updates on a new sign-in. Jose Latorraca's last actual login was 2026-07-17. He stayed in an active session and continued working on 7/22 and 7/24 without re-authenticating, so no new login event was recorded even though he was active.

## Evidence (DynamoDB, prod, us-east-2)

User table (`User-...-production`), 9 users for this tenant. Most recent `lastLogin`:
- Jose Latorraca (jlatorraca.amp+muxl@gmail.com): 2026-07-17T14:46:24
- Everyone else: 2026-01-30/31 or "never"/"NOT_YET_LOGGED"

AuditLog (`AuditLog-...-production`, GSI `byGroup`, group `f4c3f44e-...`), activity since 7/15: 120 actions, all by jlatorraca.amp+muxl@gmail.com from IP 38.137.234.134, mutations `CreateStaff` / `CreateOptionsCustomListsStaff`, pageUrl `https://go.hera.app/da-management/associate-list`. Latest bursts: 7/17 15:33-15:34, 7/22 15:40-15:44, 7/24 16:39-16:40. This is genuine manual staff entry (roster/onboarding setup).

## Reusable takeaways

- Zoho `Last_Active1` = last tenant **activity** (max AuditLog `createdAt`), NOT last login.
- Zoho `Last_Activity_Time` = CRM record touch, inflated by our own sync. Never use it to judge customer usage.
- Hera Users page = last **login/auth**, which lags activity for anyone in a persistent session.
- To judge whether a customer is actually using Hera, check AuditLog activity (by group), not just User.lastLogin.

## Query notes

- AuditLog has no usable scan path at this size; use GSI `byGroup` (hash `group`) with a `createdAt >=` filter.
- User table: filter on `userTenantId`. AuditLog and most data tables key on `group`.
