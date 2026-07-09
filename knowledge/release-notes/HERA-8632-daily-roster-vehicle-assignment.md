# Release Note: HERA-8632

**Release:** 4.1.6-1
**Type:** Bug fix
**Priority:** Emergency (fix today)
**Area:** Daily Roster
**Status as of 2026-07-09:** In Release QA (not yet live in production)

---

## Customer-facing release note

**Fixed: Assigned vehicles disappearing from the Daily Roster after refresh**

We fixed an issue on the Daily Roster where a vehicle you assigned to an associate could disappear after refreshing the page, making it look like the assignment never saved.

The problem showed up during normal roster work: assigning a vehicle to an associate, then sorting or filtering the roster. Behind the scenes, an error interrupted the save, so the assignment was lost on the next refresh. The roster now keeps vehicle, device, and parking space assignments intact through sorting, filtering, and reassignment.

No action is needed on your end. If you saw assignments drop off recently, they should hold now.

---

## Internal detail

**Reported symptom:** Daily Roster > assigned vehicle not saving, disappears after refresh.

**Root cause:** A client-side null-reference crash in the roster table (`RoutesTable.vue`), not a backend or save failure. Two code paths set `vehicle` / `device` / `parkingSpace` to `null` instead of keeping them object-shaped, so a later re-render (assign, sort, filter) read `.option` / `.id` / `.deviceName` on `null` and threw `TypeError: Cannot read properties of null`. Because the throw interrupted the update pipeline, the just-assigned vehicle was never persisted, which produced the disappearing-assignment symptom.

**Fix:**
- Keep roster rows object-shaped (`{ id: null, name: '' }`) instead of `null`.
- Added a defensive guard in the shared `parseObjUpdateStandByDriver` helper.
- Hardened `setCheckBoxMessage` to require the new vehicle's `device?.id` / `parkingSpace?.id` and read names via optional chaining.
- Added unit and Playwright E2E regression coverage.

**Not included in this fix (tracked separately):** The `production/get-staffs-unread-messages` 504 Gateway Timeout seen in the same LogRocket session belongs to the Messenger feature and is unrelated to this crash.

**Affected environment at time of report:** Tenant Uptown Fleet, Inc. (`uptown-fleet-inc-13`), user Joshua Ringgold, July 8, 2026.

**References:**
- Jira: https://herasolutions.atlassian.net/browse/HERA-8632
- LogRocket session: https://app.logrocket.com/kdsnjf/hera-solutions/s/6-019f416f-37f8-77a0-922f-1722029bd2a6/0
