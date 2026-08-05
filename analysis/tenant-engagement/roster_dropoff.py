"""Catch a tenant abandoning the daily roster in DAYS, not thirty days.

REQUESTED BY JOHN 08-05-2026: "those tenants that are not using daily roster, we
need to know sooner. especially if they were using it heavily before."

The heartbeat model cannot do this, and it is not a tuning problem. Every heartbeat
is days-since-last-event against a 30-day line, so a customer who assigned 60 routes
a day for a year and then stops looks IDENTICAL to one who assigns a route every
three weeks, until day 31. Both read "fine" on day 20. That is the wrong shape of
measurement for a collapse.

This measures the RATE against the tenant's OWN baseline, so:

  - A heavy user who stops is caught in about a week.
  - Severity is the volume they lost, not a yes/no. Dropping from 60 routes a day
    to zero is not the same event as dropping from 1 a week to zero, and the old
    model treated them the same.
  - A tenant who was always light is not flagged, because their baseline is light.
    No new false positives from customers who simply do not work this way.

DATA PATH, and why it is this one:

  Route.byGroupAndTime is useless here: `time` is a TIME OF DAY, "21:25". There is
  no group+date index on Route at all, and Route is 16.3M rows so scanning per
  tenant is out.

  The route ties to a roster by routeDailyRosterId, which embeds the date:
  "2026-08-10daybreak-logistics-94". And DailyRoster has byGroupAndNotesDate, only
  554,716 rows. So: list the tenant's rosters in the window by date, then count the
  routes on each one that carry a routeStaffId.

  Future-dated rosters are EXCLUDED. Tenants build rosters days ahead, so counting
  them would score planning as work done. Only notesDate <= as_of counts.

Usage:  python3 roster_dropoff.py [--as-of YYYY-MM-DD] [--days 90] [--limit N]
Writes data/roster-dropoff-<as-of>.json
"""
import argparse, datetime as dt, json, os, statistics
from concurrent.futures import ThreadPoolExecutor
import lib_hera as H

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "data")

RECENT_DAYS = 7        # the window we judge
GAP_DAYS = 3           # skipped between recent and baseline, so a drop does not
                       # contaminate its own baseline
BASELINE_DAYS = 60     # how much history the baseline is drawn from
MIN_BASELINE_WEEKLY = 5    # below this they were never a real roster user
COLLAPSE = 0.25        # recent under 25% of expected = collapsed
DECLINE = 0.60         # under 60% = declining


def series(ddb, group, since, as_of):
    """{date: routes_assigned} for rosters dated on or before as_of."""
    rosters = []
    for r in H.query_all(
        ddb, TableName=H.table("DailyRoster"), IndexName="byGroupAndNotesDate",
        KeyConditionExpression="#g = :g AND #n >= :s",
        ExpressionAttributeNames={"#g": "group", "#n": "notesDate"},
        ExpressionAttributeValues={":g": {"S": group}, ":s": {"S": since}},
        ProjectionExpression="id,notesDate",
    ):
        d = str(r.get("notesDate") or "")[:10]
        # Future rosters are planning, not work. Counting them scores intent.
        if d and d <= as_of:
            rosters.append((d, r["id"]))

    out = {}
    for d, rid in rosters:
        n = 0
        for rt in H.query_all(
            ddb, TableName=H.table("Route"), IndexName="gsi-RouteDailyRoster",
            KeyConditionExpression="routeDailyRosterId = :r",
            ExpressionAttributeValues={":r": {"S": rid}},
            ProjectionExpression="routeStaffId",
        ):
            if rt.get("routeStaffId"):
                n += 1
        out[d] = out.get(d, 0) + n
    return dict(sorted(out.items()))


def assess(s, as_of):
    """Recent rate against the tenant's own baseline."""
    recent_from = (as_of - dt.timedelta(days=RECENT_DAYS - 1)).isoformat()
    base_to = (as_of - dt.timedelta(days=RECENT_DAYS + GAP_DAYS)).isoformat()
    base_from = (as_of - dt.timedelta(days=RECENT_DAYS + GAP_DAYS + BASELINE_DAYS)).isoformat()

    recent = sum(v for d, v in s.items() if d >= recent_from)
    base_days = {d: v for d, v in s.items() if base_from <= d <= base_to}
    if not base_days:
        return None

    # Weekly rate from the baseline period. Uses elapsed days rather than the number
    # of rosters found, so a tenant who rosters 3 days a week is not scored as though
    # they roster 7. A missing day is a real zero.
    span = (dt.date.fromisoformat(base_to) - dt.date.fromisoformat(base_from)).days + 1
    base_weekly = sum(base_days.values()) / span * 7
    expected = base_weekly / 7 * RECENT_DAYS
    if base_weekly < MIN_BASELINE_WEEKLY:
        return None                      # never a real roster user, nothing to lose

    ratio = recent / expected if expected else 1.0
    if recent == 0:
        state = "STOPPED"
    elif ratio <= COLLAPSE:
        state = "COLLAPSED"
    elif ratio <= DECLINE:
        state = "DECLINING"
    else:
        return None

    # Days since the last route was actually assigned, so the alert can say how long.
    assigned = [d for d, v in s.items() if v > 0]
    last = max(assigned) if assigned else None
    return {
        "state": state,
        "routes_last_7d": recent,
        "expected_7d": round(expected, 1),
        "ratio": round(ratio, 2),
        "baseline_weekly": round(base_weekly, 1),
        "weekly_routes_lost": round(base_weekly - recent / RECENT_DAYS * 7, 1),
        "last_assigned": last,
        "days_since_assigned": (as_of - dt.date.fromisoformat(last)).days if last else None,
        "peak_day": max(s.values()) if s else 0,
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--as-of", default=dt.date.today().isoformat())
    ap.add_argument("--days", type=int, default=90)
    ap.add_argument("--limit", type=int)
    a = ap.parse_args()
    as_of = dt.date.fromisoformat(a.as_of)
    since = (as_of - dt.timedelta(days=a.days)).isoformat()

    usage = json.load(open(H.newest_dated(DATA, "usage")))
    tenants = usage["tenants"]
    # A roster drop only means an ADOPTION problem if the drivers are still there.
    # If the billed driver count collapsed too, the business is shrinking and this is
    # not a CS failure. 5 of the 19 alerts on 08-04-2026 were exactly that, including
    # GNC Transportation at 105 drivers down to 1. Calling them about rostering would
    # be tone deaf.
    hist = {t["companyName"]: t for t in
            json.load(open(H.newest_dated(DATA, "staff-history")))["tenants"]}
    if a.limit:
        tenants = sorted(tenants, key=lambda t: -(t.get("monthly") or 0))[:a.limit]
    print(f"{len(tenants)} tenants, rosters since {since}, judging the last {RECENT_DAYS} days")
    ddb = H.client()

    def work(t):
        try:
            return t, series(ddb, t["group"], since, as_of.isoformat()), None
        except Exception as e:                                  # noqa: BLE001
            return t, {}, f"{type(e).__name__}: {e}"

    rows, alerts, errors = [], [], []
    with ThreadPoolExecutor(max_workers=16) as ex:
        for i, (t, s, err) in enumerate(ex.map(work, tenants), 1):
            if err:
                errors.append((t.get("companyName"), err))
            v = assess(s, as_of) if s else None
            h = hist.get(t["companyName"]) or {}
            cur = h.get("latest")
            pct = ((h.get("change") or {}).get("30") or {}).get("pct")
            shrinking = (pct is not None and pct <= -25) or (cur is not None and cur < 5)
            if v:
                v["drivers_now"] = cur
                v["drivers_30d_pct"] = pct
                v["drivers_peak"] = h.get("peak")
                v["cause"] = "business shrinking" if shrinking else "adoption"
            rec = {"companyName": t["companyName"], "group": t["group"],
                   "monthly": t.get("monthly"), "billed_drivers": cur,
                   "series": s, "alert": v}
            rows.append(rec)
            if v:
                alerts.append(rec)
            if i % 40 == 0:
                print(f"  {i}/{len(tenants)}")

    out = os.path.join(DATA, f"roster-dropoff-{as_of}.json")
    json.dump({"as_of": str(as_of), "recent_days": RECENT_DAYS,
               "baseline_days": BASELINE_DAYS, "tenants": rows}, open(out, "w"))
    print(f"\nwrote {out}")
    if errors:
        print(f"{len(errors)} errors, first: {errors[0]}")

    order = {"STOPPED": 0, "COLLAPSED": 1, "DECLINING": 2}
    alerts.sort(key=lambda r: (order[r["alert"]["state"]], -(r["alert"]["weekly_routes_lost"])))

    def show(sel, title):
        print(f"\n{title}  ({len(sel)})\n")
        print("  {:30s} {:>9} {:>7} {:>7} {:>8} {:>8} {:>6}".format(
            "account", "state", "was/wk", "now/7d", "drivers", "$/mo", "quiet"))
        for r in sel:
            v = r["alert"]
            print("  {:30s} {:>9} {:>7.0f} {:>7} {:>8} {:>8,.0f} {:>6}".format(
                r["companyName"][:30], v["state"], v["baseline_weekly"], v["routes_last_7d"],
                "{} ({:+.0f}%)".format(v["drivers_now"], v["drivers_30d_pct"])
                if v.get("drivers_30d_pct") is not None else str(v.get("drivers_now")),
                r["monthly"] or 0,
                "-" if v["days_since_assigned"] is None else str(v["days_since_assigned"]) + "d"))

    adopt = [r for r in alerts if r["alert"]["cause"] == "adoption"]
    shrink = [r for r in alerts if r["alert"]["cause"] != "adoption"]
    print(f"\n{len(alerts)} tenants dropping off the daily roster")
    show(adopt, "ADOPTION. Drivers still on the books, so this is a CS call")
    show(shrink, "BUSINESS SHRINKING. Driver count collapsed too. NOT a CS failure")

    early = [r for r in adopt if (r["alert"]["days_since_assigned"] or 99) <= 30]
    print(f"\nWHAT THIS CATCHES THAT THE 30-DAY HEARTBEAT DOES NOT")
    print(f"  {len(early)} adoption cases are still inside the 30-day line, worth "
          f"${sum(r['monthly'] or 0 for r in early):,.0f}/mo.")
    print(f"  The heartbeat reads every one of them as healthy today.")


if __name__ == "__main__":
    main()
