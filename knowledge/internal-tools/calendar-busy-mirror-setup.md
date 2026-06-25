# Calendar Busy Mirror: Personal to Work Google Calendar

## Problem

Personal Google Calendar (`techbond310@gmail.com`) and a shared "john & matthew" calendar were already layered into the work Google Workspace calendar (`john@hera.app`) for visual reference. However, when coworkers in the organization queried free/busy on the work calendar, they only saw events that physically lived on the work calendar. Personal events overlaid in the work view did not propagate to the org's free/busy lookups. The result: John appeared free to coworkers during times he was actually busy with personal commitments.

## Solution

A Google Apps Script running in the work account (`john@hera.app`) reads events from the two personal calendars and creates corresponding placeholder "Busy" events on the work calendar itself. These mirror events have private visibility, no title beyond "Busy", and an identifying tag in the description so the script can update or delete them when the source event changes.

Combined with a calendar-wide setting that hides event details from the rest of the organization, the result is: coworkers see John as busy at the right times, but never see what any of those events actually are.

Sync cadence: every 15 minutes. Lookahead window: 30 days.

## One-time setup steps

### Step 1: Confirm Calendar IDs

- Personal primary: `techbond310@gmail.com`
- Shared "john & matthew" calendar: `bd5bb814215bd20ac210cfbc50c734a1f2a662890e2e6a094b7654c0542bafd6@group.calendar.google.com`
- Work target: `john@hera.app`

Each ID is found in calendar.google.com, Settings, click the calendar in the left sidebar, scroll to "Integrate calendar," copy "Calendar ID."

### Step 2: Share personal calendars to work account

For each personal calendar (`techbond310@gmail.com` and the "john & matthew" calendar):

1. Log into calendar.google.com as the personal account.
2. Gear icon, Settings, click the calendar in the left sidebar.
3. Scroll to "Share with specific people or groups," click "Add people or groups."
4. Add `john@hera.app` with permission **"See all event details."**
5. Click "Send."

Note: outbound sharing from a Workspace account to an external account may be restricted by the Workspace admin. The reverse direction (personal Gmail to Workspace) is not restricted, which is why the script runs from the work side and reads from the personal side.

### Step 3: Accept shares on the work side

When the personal calendars are shared in, the work account receives invitation emails. Click "Add this calendar" in each. The shared calendars then appear in the work account's left sidebar under "Other calendars."

### Step 4: Create the Apps Script project

1. Log into script.google.com as `john@hera.app`.
2. Click "New project."
3. Delete any starter code.
4. Rename the project to "Calendar Busy Mirror."

### Step 5: Paste in the script

```javascript
const SOURCES = [
  'techbond310@gmail.com',
  'bd5bb814215bd20ac210cfbc50c734a1f2a662890e2e6a094b7654c0542bafd6@group.calendar.google.com',
];
const DAYS_AHEAD = 30;

function syncBusy() {
  const target = CalendarApp.getDefaultCalendar();
  const start = new Date();
  const end = new Date(Date.now() + DAYS_AHEAD * 86400000);

  const wanted = {};
  SOURCES.forEach(id => {
    const cal = CalendarApp.getCalendarById(id);
    if (!cal) return;
    cal.getEvents(start, end).forEach(ev => {
      if (ev.getMyStatus && ev.getMyStatus() === CalendarApp.GuestStatus.NO) return;
      wanted[ev.getId()] = { s: ev.getStartTime(), e: ev.getEndTime() };
    });
  });

  const existing = {};
  target.getEvents(start, end).forEach(ev => {
    const m = (ev.getDescription() || '').match(/\[mirror:([^\]]+)\]/);
    if (m) existing[m[1]] = ev;
  });

  Object.keys(wanted).forEach(id => {
    const w = wanted[id];
    if (existing[id]) {
      const ev = existing[id];
      if (ev.getStartTime().getTime() !== w.s.getTime() ||
          ev.getEndTime().getTime()   !== w.e.getTime()) {
        ev.setTime(w.s, w.e);
      }
      delete existing[id];
    } else {
      target.createEvent('Busy', w.s, w.e, { description: `[mirror:${id}]` })
            .setVisibility(CalendarApp.Visibility.PRIVATE);
    }
  });

  Object.values(existing).forEach(ev => ev.deleteEvent());
}
```

Save the file.

### Step 6: Run once manually to authorize

1. With `syncBusy` selected in the function dropdown, click "Run."
2. Approve the authorization request. The "unverified app" warning is expected for a personal Apps Script; click "Advanced," then "Go to Calendar Busy Mirror (unsafe)," then "Allow."
3. Watch the execution log for "Execution completed."
4. Verify on the work calendar that "Busy" entries now appear at the times of personal events. To isolate the script-created entries from the layered personal calendars, uncheck the personal calendars in the left sidebar.

### Step 7: Add the recurring trigger

1. In the Apps Script editor, click the clock icon ("Triggers") in the left sidebar.
2. Click "Add Trigger."
3. Function: `syncBusy`. Deployment: Head. Event source: Time-driven. Type: Minutes timer. Interval: Every 15 minutes. Failure notifications: Notify me immediately.
4. Save.

### Step 8: Hide event details from the rest of the organization

1. Open calendar.google.com as `john@hera.app`.
2. Gear, Settings, click `john@hera.app` in the left sidebar.
3. Scroll to "Access permissions for events."
4. Keep "Make available for Hera.app" checked so coworkers can still see free/busy.
5. In the dropdown next to it, choose **"See only free/busy (hide details)."**
6. Scroll to "Share with specific people or groups" and review individuals with broader access. Anyone set to "See all event details" or higher will still see full details regardless of the org-wide setting.

## Verification

Open an incognito window or have a coworker on `hera.app` start creating an event with `john@hera.app` as a guest, then use "Find a time." Mirrored "Busy" blocks should appear at the right times with no titles or details.

## Maintenance

- The script is the single source of truth. Edit `SOURCES` to add or remove calendars; edit `DAYS_AHEAD` to change the lookahead window.
- To pause the sync, delete the trigger in the Triggers panel. To resume, recreate it.
- If a scheduled run ever fails, Google sends a failure email to `john@hera.app`.
- Declined events on the personal side are skipped automatically.
- Meeting guests still see full event details because they are guests, not because of calendar access. The hide-details setting does not affect that.
- Events explicitly marked "Public" visibility on the work calendar will still show details to the org. Worth a periodic scan of older recurring events.

## Known limitations

- The mirror only covers the next 30 days at any given moment. Anyone querying availability further out will see John as free even if personal commitments exist. Increase `DAYS_AHEAD` if a longer window is needed.
- The sync runs every 15 minutes, not in real time. A personal event added five minutes before a coworker checks availability may not yet be mirrored.
- If the personal Google account ever revokes calendar sharing to `john@hera.app`, the script will silently stop creating new mirror events for that source. Add a periodic check (or rely on the failure notification email) if this becomes a concern.
