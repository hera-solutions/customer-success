"""Daily active driver count per tenant, from InvoiceLineItem.

WHY THIS TABLE, decided by John 08-04-2026: "never use averageActiveDriverCount,
use InvoiceLineItem.activeStaff for the staff counts."

The alternatives are both worse:

  Invoice.averageActiveDriverCount  A MONTHLY AVERAGE, and the only count field on
                                    the Invoice table. On the accruing month it
                                    covers only the days elapsed, which is what
                                    produced two fake 36% declines on 08-03-2026.
                                    It also cannot show a change WITHIN a month.
  Staff on byGroupStatus            Current state only, no history at all, so no
                                    way to see a driver count move.

InvoiceLineItem is ONE ROW PER TENANT PER DAY, holding that day's activeStaff and
that day's charge. So it is both the billed figure and a real time series, which is
what makes change detection possible at all.

WHAT IT REVEALS THAT NOTHING ELSE DOES: a roster nobody maintains flatlines. TPE
Logistics moved 30 times in the 76 days to 06-15-2026, bouncing between 93 and 115
drivers, then sat at EXACTLY 115 for the next 50 days. That is not a stable
operation, it is an abandoned list, and we keep billing it. Detecting it needs a
daily series; a monthly average hides it completely.

BILLING NOTE, corrected here: the daily charge is the monthly rate divided by the
days in that month, NOT a flat $0.30/day. 115 drivers costs $34.50/day in June (30
days) and $33.39/day in August (31 days). $0.30 is only right in a 30-day month.

WINDOW: 400 days by default. 120 was too short and it hid the worst account in the
book: Probyn Inc fell from 127 drivers to 26 during MARCH, so a 120-day window opens
after the collapse and the task stops mentioning it. 400 days also stops days_frozen
being silently censored by the window on long-dead accounts.

Usage:  python3 staff_history.py [--as-of YYYY-MM-DD] [--days 400]
Writes data/staff-history-<as-of>.json
"""
import argparse, datetime as dt, glob, json, os
from concurrent.futures import ThreadPoolExecutor
import lib_hera as H

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "data")

# A roster this many consecutive days unchanged is treated as unmaintained.
# 30 matches the darkness threshold used everywhere else, so the two are comparable.
FROZEN_DAYS = 30
# Windows for change detection, in days.
WINDOWS = (30, 60, 90)


def daily_series(ddb, group, since):
    """
    ({'YYYY-MM-DD': activeStaff}, billing) for one tenant. One paginated query.

    `billing` matters because a frozen roster only costs the CUSTOMER money if they
    are billed per driver. Double Iron Car Care sits at 18 drivers on a flat $25/mo
    (flatMonthlyBillingAmount 25, variableTotal 0, every per-driver charge 0), which
    also explains the "18 drivers at $25" figure that has been flagged as impossible
    since 08-03-2026. Nothing was wrong with it. Telling that customer they are
    over-billed would be flatly false, so detect it here rather than downstream.

    bundleCostExt is the per-driver charge for that day. Zero on every recent day
    while drivers exist means the account is not charged by headcount.

    Judge this on RECENT days only. Over a 401-day window, "ever billed per driver"
    is far too loose: Your Express Solutions read as per-driver because it billed
    that way months ago, which would have put a false over-billing warning on the
    task. Pricing changes, so only the current arrangement matters.
    """
    out, ext, trial = {}, {}, False
    for f in H.query_all(
        ddb,
        TableName=H.table("InvoiceLineItem"),
        IndexName="byGroup",
        KeyConditionExpression="#g = :g AND #c >= :s",
        ExpressionAttributeNames={"#g": "group", "#c": "createdAt", "#d": "date"},
        ExpressionAttributeValues={":g": {"S": group}, ":s": {"S": since}},
        ProjectionExpression="#d,activeStaff,bundleCostExt,isTrial",
    ):
        d = str(f.get("date") or "")[:10]
        if not d or d == "None":
            continue
        v = f.get("activeStaff")
        if v is None:
            continue
        # One row per tenant per day, but keep the max if a day ever duplicates
        # rather than letting pagination order decide.
        n = int(round(float(v)))
        out[d] = max(out.get(d, n), n)
        ext[d] = max(ext.get(d, 0.0), float(f.get("bundleCostExt") or 0))
        trial = trial or bool(f.get("isTrial"))
    return dict(sorted(out.items())), dict(sorted(ext.items())), trial


def at_or_before(series, target):
    """activeStaff on `target`, else the newest earlier day. None if the tenant
    has no row that old. Never interpolates forward: a missing recent day must not
    be filled in from an older one, because that invents a count."""
    keys = [d for d in series if d <= target]
    return series[max(keys)] if keys else None


BILLING_LOOKBACK = 35   # slightly over a month, so a full billing cycle is covered


def summarise(series, ext, as_of):
    """Everything downstream needs, computed once."""
    recent = [v for d, v in (ext or {}).items()
              if d >= str(as_of - dt.timedelta(days=BILLING_LOOKBACK))]
    per_driver = any(v > 0 for v in recent)
    if not series:
        return {"latest": None, "latest_date": None, "days_stale": None,
                "days_frozen": None, "frozen": False, "changes_in_window": 0,
                "window_days": 0, "peak": None, "peak_date": None,
                "trough": None, "change": {}, "per_driver_billing": per_driver}
    days = sorted(series)
    last = days[-1]
    cur = series[last]

    # Trailing run of identical values. This is the frozen-roster test, and it is
    # direct evidence rather than inference: the number literally did not move.
    frozen = 0
    for d in reversed(days):
        if series[d] == cur:
            frozen += 1
        else:
            break

    change = {}
    for w in WINDOWS:
        then = at_or_before(series, str(as_of - dt.timedelta(days=w)))
        if then is None:
            change[str(w)] = None
        else:
            change[str(w)] = {"then": then, "now": cur, "delta": cur - then,
                              "pct": round((cur - then) / then * 100, 1) if then else None}

    # Peak over the WHOLE retained series, not 90 days. Probyn Inc collapsed from
    # 127 drivers to 26 in April; a 90-day peak window puts that outside the range
    # and the task silently stops mentioning the worst thing about the account.
    peak = max(series.values())
    peak_date = max((d for d in days if series[d] == peak))
    return {
        "latest": cur,
        "latest_date": last,
        # The feed is generated overnight, so 1 day stale is normal and healthy.
        "days_stale": (as_of - dt.date.fromisoformat(last)).days,
        "days_frozen": frozen,
        "frozen": frozen >= FROZEN_DAYS,
        # Named for the actual window, not 90. Calling this changes_90d alongside
        # "frozen 90 days" printed the self-contradictory line "frozen 90 days after
        # 11 changes in 90 days", because the counter spanned the full 120.
        "window_days": len(days),
        "changes_in_window": sum(1 for a, b in zip(days, days[1:]) if series[a] != series[b]),
        "peak": peak,
        "peak_date": peak_date,
        "trough": min(series.values()),
        "change": change,
        "per_driver_billing": per_driver,
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--as-of", default=dt.date.today().isoformat())
    ap.add_argument("--days", type=int, default=400)
    a = ap.parse_args()
    as_of = dt.date.fromisoformat(a.as_of)
    since = (as_of - dt.timedelta(days=a.days)).isoformat()

    src = H.newest_dated(DATA, "signals")
    tenants = json.load(open(src))["tenants"]
    print(f"tenant list from {os.path.basename(src)}: {len(tenants)} tenants")
    print(f"InvoiceLineItem.activeStaff, {a.days} days back to {since}")

    ddb = H.client()

    def work(t):
        try:
            series, ext, trial = daily_series(ddb, t["group"], since)
            return t, series, ext, trial, None
        except Exception as e:                      # noqa: BLE001
            return t, {}, {}, False, f"{type(e).__name__}: {e}"

    rows, errors = [], []
    with ThreadPoolExecutor(max_workers=16) as ex:
        for i, (t, series, ext, trial, err) in enumerate(ex.map(work, tenants), 1):
            if err:
                errors.append((t.get("companyName"), err))
            rec = {"group": t["group"],
                   "companyName": t.get("companyName") or t["group"],
                   "series": series}
            rec.update(summarise(series, ext, as_of))
            rec["trial"] = trial
            rows.append(rec)
            if i % 50 == 0:
                print(f"  {i}/{len(tenants)}")

    out = os.path.join(DATA, f"staff-history-{as_of}.json")
    json.dump({"as_of": str(as_of), "days": a.days, "frozen_days": FROZEN_DAYS,
               "source": "InvoiceLineItem.activeStaff", "tenants": rows},
              open(out, "w"))
    print(f"\nwrote {out}")

    have = [r for r in rows if r["latest"] is not None]
    frozen = [r for r in have if r["frozen"]]
    print(f"{len(have)}/{len(rows)} tenants have a daily series")
    if errors:
        print(f"{len(errors)} query errors, first: {errors[0]}")
    stale = [r["days_stale"] for r in have]
    print(f"feed lag: min {min(stale)}d, median {sorted(stale)[len(stale)//2]}d, max {max(stale)}d")
    flat = [r for r in have if not r.get("per_driver_billing")]
    print(f"{len(flat)} tenants are NOT billed per driver, so a frozen roster costs them nothing")

    # Only a frozen roster WITH real headcount AND per-driver billing implies
    # over-billing. Everything else in the frozen list is a dead or flat-fee account.
    print(f"\nFROZEN {FROZEN_DAYS}+ DAYS: {len(frozen)} tenants")
    print("  days_frozen is capped by the query window, so a value near "
          f"{a.days} means 'at least that long'")
    for label, sel in (("billed per driver, 10+ drivers: LIKELY OVER-BILLED",
                        [r for r in frozen if r.get("per_driver_billing") and (r["latest"] or 0) >= 10]),
                       ("flat fee or under 10 drivers: not an over-billing case",
                        [r for r in frozen if not (r.get("per_driver_billing") and (r["latest"] or 0) >= 10)])):
        print(f"\n  {label}  ({len(sel)})")
        for r in sorted(sel, key=lambda x: -(x["latest"] or 0)):
            print("     {:34s} {:>4} drivers frozen {:>4}d  {:>3} changes/{}d  {}".format(
                r["companyName"][:34], r["latest"], r["days_frozen"], r["changes_in_window"], r["window_days"],
                "per-driver" if r.get("per_driver_billing") else "FLAT FEE"))


if __name__ == "__main__":
    main()
