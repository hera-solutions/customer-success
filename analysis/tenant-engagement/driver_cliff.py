"""Detect a driver roster falling off a cliff.

REQUESTED BY JOHN 08-05-2026, as a critical daily signal alongside roster drop-off:
"dropping a significant amount of associates to unsustainable numbers, for example
having consistently 100+ drivers then dropping to sub 5 in the course of a couple of
days or in a single day."

WHY THE EXISTING MEASURES MISS IT

  driver_direction    Reports 30-day change. A fall from 105 to 1 shows as -99%, so
                      the SIZE is visible, but nothing says it happened in ONE DAY.
                      100 -> 2 overnight and 100 -> 2 over three months are the same
                      number and completely different events. The first is a business
                      shock: lost the Amazon contract, sold, closed. The second is a
                      slow bleed.
  roster_maintained   Fires when the count STOPS moving. A cliff is the opposite,
                      violent movement, so it says nothing until afterwards.
  The heartbeats      All days-since. Silent for 30 days.

WHAT THIS MEASURES

Speed and depth together, off the daily InvoiceLineItem.activeStaff series that
staff_history.py already caches. No new queries: this is pure computation.

  CLIFF   A sustained roster of >= MIN_SUSTAINED drivers collapsing to under
          UNSUSTAINABLE within <= FAST_DAYS. Business-ending shape.
  CRASH   A fall of >= CRASH_PCT within <= FAST_DAYS from a sustained roster, but
          still landing above the unsustainable floor. Severe and still operating.

Both report the DATE and the WINDOW, because "lost 103 drivers on 07-14" is
actionable in a way that "-99% over 30 days" is not.

Usage:  python3 driver_cliff.py [--as-of YYYY-MM-DD] [--recent 14]
Writes data/driver-cliff-<as-of>.json
"""
import argparse, datetime as dt, json, os
import lib_hera as H

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "data")

MIN_SUSTAINED = 20     # below this there is no cliff to fall off
UNSUSTAINABLE = 5      # a DSP cannot run on this, John's "sub 5"
CRASH_PCT = 60         # percent lost to count as a crash short of a cliff
FAST_DAYS = 7          # "in the course of a couple of days or a single day"
SUSTAINED_DAYS = 21    # how long they must have held the high level to count as sustained
PERSIST_DAYS = 3       # the fall must STICK this long, or it is a data artifact


def find_cliffs(series, as_of):
    """
    Every fast fall in the series, newest last. Returns a list, because for a DAILY
    alert the most RECENT event matters, while the largest matters for context, and
    an earlier huge one must not hide a recent smaller one.

    `before` is the MAXIMUM in the lookback rather than the value at its start, so a
    two-step fall (100 -> 60 -> 2 across three days) is scored against the 100.
    """
    days = sorted(series)
    if len(days) < SUSTAINED_DAYS + 2:
        return []
    idx = {d: i for i, d in enumerate(days)}
    out = []
    for i, d in enumerate(days):
        if i == 0:
            continue
        lo = max(0, i - FAST_DAYS)
        window = days[lo:i]
        before = max(series[x] for x in window)
        after = series[d]
        if before < MIN_SUSTAINED or after >= before:
            continue
        lost = before - after
        pct = lost / before * 100
        if after < UNSUSTAINABLE:
            state = "CLIFF"
        elif pct >= CRASH_PCT:
            state = "CRASH"
        else:
            continue
        # Was the high level sustained, or a one-day spike?
        pre = [series[x] for x in days[max(0, lo - SUSTAINED_DAYS):lo]]
        if not pre:
            continue
        pre_sorted = sorted(pre)
        if pre_sorted[len(pre_sorted) // 2] < MIN_SUSTAINED:
            continue

        # DID IT STICK? This guard exists because of two real artifacts found
        # 08-05-2026. Cazar Logistics read 113 drivers, then 0 on 07-04
        # (Independence Day, so the billing job evidently wrote a zero), then 113
        # again the next day. Elite OnPoint read 0 for 16 days and is now back at
        # 117. Both would have fired a critical 6am alert about a business that
        # never went anywhere. A cliff that does not persist is not a cliff.
        tail = days[i:i + PERSIST_DAYS]
        persisted = sum(1 for x in tail if series[x] <= after + max(1, after))
        recovered_now = series[days[-1]] >= before * 0.5

        start = max((x for x in window if series[x] == before), default=window[0])
        out.append({
            "state": state, "date": d, "from": before, "to": after,
            "lost": lost, "pct": round(pct, 1),
            "took_days": (dt.date.fromisoformat(d) - dt.date.fromisoformat(start)).days,
            "persisted_days": persisted,
            "held": persisted >= PERSIST_DAYS,
            "recovered_since": recovered_now,
            "days_ago": (as_of - dt.date.fromisoformat(d)).days,
        })
    # Collapse consecutive days describing the same fall: keep the deepest per fall.
    merged = []
    for ev in out:
        if merged and (dt.date.fromisoformat(ev["date"])
                       - dt.date.fromisoformat(merged[-1]["date"])).days <= FAST_DAYS:
            if ev["lost"] > merged[-1]["lost"]:
                merged[-1] = ev
        else:
            merged.append(ev)
    return merged


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--as-of", default=dt.date.today().isoformat())
    ap.add_argument("--recent", type=int, default=14,
                    help="how many days back still counts as actionable")
    a = ap.parse_args()
    as_of = dt.date.fromisoformat(a.as_of)

    hist = json.load(open(H.newest_dated(DATA, "staff-history")))
    print(f"{len(hist['tenants'])} tenants, daily activeStaff from {hist['source']}")
    print(f"cliff = sustained {MIN_SUSTAINED}+ drivers falling under {UNSUSTAINABLE} "
          f"within {FAST_DAYS} days\n")

    rows, artifacts = [], []
    for t in hist["tenants"]:
        evs = find_cliffs(t.get("series") or {}, as_of)
        if not evs:
            continue
        rec = {"companyName": t["companyName"], "group": t["group"],
               "drivers_now": t.get("latest"),
               "per_driver_billing": t.get("per_driver_billing"),
               "events": evs}
        real = [e for e in evs if e["held"] and not e["recovered_since"]]
        if real:
            # newest real event drives the alert; a daily signal cares about now
            rec["event"] = real[-1]
            rec["worst"] = max(real, key=lambda e: e["lost"])
            rows.append(rec)
        else:
            rec["event"] = evs[-1]
            artifacts.append(rec)

    out = os.path.join(DATA, f"driver-cliff-{as_of}.json")
    json.dump({"as_of": str(as_of), "tenants": rows}, open(out, "w"))

    def show(sel, title):
        print(f"{title}  ({len(sel)})\n")
        if not sel:
            print("  none\n")
            return
        print("  {:30s} {:>7} {:>7} {:>6} {:>6} {:>12} {:>8}".format(
            "account", "from", "to", "lost", "days", "on", "now"))
        for r in sel:
            e = r["event"]
            print("  {:30s} {:>7} {:>7} {:>6} {:>6} {:>12} {:>8}".format(
                r["companyName"][:30], e["from"], e["to"], e["lost"],
                e["took_days"], e["date"], str(r["drivers_now"])))
        print()

    rows.sort(key=lambda r: (r["event"]["days_ago"], -r["event"]["lost"]))
    recent = [r for r in rows if r["event"]["days_ago"] <= a.recent]
    older = [r for r in rows if r["event"]["days_ago"] > a.recent]

    show(recent, f"ACT NOW: happened in the last {a.recent} days")
    show(sorted(older, key=lambda r: -r["event"]["lost"])[:20],
         "EARLIER, for context and to show the detector works")

    if artifacts:
        print("EXCLUDED as data artifacts or recovered, NOT alerted  ({})\n".format(len(artifacts)))
        print("  {:30s} {:>7} {:>7} {:>6} {:>12} {:>8} {}".format(
            "account","from","to","held","on","now","why"))
        for r in artifacts:
            e=r["event"]
            print("  {:30s} {:>7} {:>7} {:>6} {:>12} {:>8} {}".format(
                r["companyName"][:30], e["from"], e["to"], str(e["persisted_days"])+"d",
                e["date"], str(r["drivers_now"]),
                "recovered" if e["recovered_since"] else "did not stick"))
        print()

    same_day = [r for r in rows if r["event"]["took_days"] <= 1]
    print(f"wrote {out}")
    print(f"\n{len(rows)} cliff or crash events in the retained window.")
    print(f"{len(same_day)} of them happened in ONE DAY OR LESS.")
    still = [r for r in rows if (r['drivers_now'] or 0) < UNSUSTAINABLE]
    print(f"{len(still)} are STILL under {UNSUSTAINABLE} drivers today, so they never recovered.")


if __name__ == "__main__":
    main()
