# Code-check prompt: Zoho "Last Active" source + lastLogin/session behavior

Paste the block below into the project that has the Hera codebase.

---

I need you to confirm two things from the Hera code. Context: we investigated why Zoho CRM's "Last Active" date for an account (tenant) disagreed with the Hera Users page login date. From production DynamoDB (read-only) we found: the Zoho field value equals the tenant's most recent AuditLog action date, NOT the most recent user login, and NOT the Tenant record's own updatedAt. We want the code to confirm the mechanism, not just the correlation.

Environment facts we already have:
- AWS account 530079012632, region us-east-2, Amplify backend suffix `zeobggbnyva4padyiddojnmnqy-production`.
- Zoho Accounts custom field API name `Last_Active1` (we just renamed its display label to "Last Hera Activity"; API name unchanged). The Account record also has a native `Last_Activity_Time` field we do NOT care about.
- Tenant table `Tenant-...-production` has `zohoCrmAccountRecordId` and `group`, but NO stored last-activity or last-login field.
- AuditLog table `AuditLog-...-production`, GSI `byGroup` (hash `group`), records `mutationName`/`mutationNameText`, `email`, `createdAt`, `tenantID`, `ipAddress`.
- User table `User-...-production` has `lastLogin`, `userTenantId`, `cognitoSub`.
- Auth is AWS Cognito, production user pool `us-east-2_Lt8dKaptb` (`hera4e362e32_userpool_..._production`), web app client `1pr832o5u6s4jl1hsiuucoh0av` (`hera4e362e32_app_clientWeb`).
- Observed: for one tenant, `Last_Active1` = 2026-07-24 (matches the latest AuditLog action, a CreateStaff/CreateOptionsCustomListsStaff by the customer), while that user's `User.lastLogin` = 2026-07-17 and never updated despite the user taking UI actions on 7/22 and 7/24.

## Investigation 1: What populates the Zoho "Last Active" field

1. Find the Hera -> Zoho sync code that writes the Accounts field `Last_Active1`. Point me to the file(s) and function(s), and whether it's a Lambda, cron/scheduled job, resolver, or event-driven.
2. Confirm the exact source of the value it writes. Specifically: does it derive from the AuditLog table (max `createdAt` per tenant/group), or from something else (a User field, a Tenant field, a computed "last activity" value)? Show the query or field it reads.
3. If it reads AuditLog, does it count every mutation type as "activity," or only certain ones? List any included/excluded mutation types. We want to be able to tell a colleague exactly what counts as "activity."
4. How often does the sync run (so we know the field's freshness/lag)?
5. Confirm nothing downstream reads `Last_Active1` back in a way that a display-label rename could affect (it shouldn't, since API name is unchanged, but please verify).

## Investigation 2: How `User.lastLogin` is written, and real session length

1. Find where `User.lastLogin` is set. What event triggers the write: an explicit credential sign-in only, every new session, every token refresh, app open, or something else? Point me to the code.
2. Given that trigger, explain why a user (Jose, lastLogin 7/17) could take authenticated UI actions on 7/22 and 7/24 without `lastLogin` updating. Confirm whether that is expected behavior (silent token refresh, no new login event) or a gap/bug in how lastLogin is recorded.
3. Cognito token settings for the production web client (`hera4e362e32_app_clientWeb`, pool `us-east-2_Lt8dKaptb`): report the AccessToken validity, IdToken validity, and RefreshToken validity (with units). We could not read these from AWS with a read-only role (DescribeUserPoolClient was AccessDenied), so pull them from the Amplify/Cognito config in the repo or infra code.
4. Bottom line we need: how long can a user stay signed in and active WITHOUT re-entering credentials? We had assumed the session was ~24 hours; we suspect that's the access-token TTL while the refresh token keeps them signed in much longer. Confirm the actual numbers.

## Deliverable

For each investigation, give me: the file/function references, the confirmed answer in plain language, and flag anything that looks like a bug (e.g., lastLogin not updating when it should). Keep it specific enough that I can explain it to a non-engineer.
