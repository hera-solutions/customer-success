"""
Classify tenants from the signal data and write the weekly report.

Two independent axes, because engagement does not predict revenue direction.
Tested in the July 2026 baseline: 6 of 15 declining accounts scored ABOVE the
healthy average on engagement, and the highest-engagement account in the pilot
was losing 15% of its associates. Blending them hides both problems.

  Axis 1, ENGAGEMENT: the three-signal pattern from the daily-review skill.
    HEALTHY_BOTH / MSG_ONLY / SCORECARD_ONLY / BOTH_DARK on a 14-day window.
  Axis 2, REVENUE: active-associate direction across the last 4 CLOSED invoices.
    growing > +5%, declining < -5%, else flat.

Usage:
    python3 classify.py                      # newest signals file
    python3 classify.py --as-of 2026-07-29
Writes reports/<as-of>-cs-health.md
"""
import argparse
import datetime as dt
import glob
import json
import os

import lib_hera as H

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "data")
REPORTS = os.path.join(HERE, "reports")

ENGAGEMENT_WINDOW = 14     # days, per the daily-review skill
STRATEGIC_SCORECARD = 60   # days: workflow has actually left Hera, not "missed a week"
ROSTER_WINDOW = 30         # days without a staffed roster counts as roster-dark
TREND_INVOICES = 4         # closed invoices to measure revenue direction over
TREND_BAND = 0.05          # +/- 5% is flat
UNDER10_RUN = 3            # consecutive days below 10 active associates
CLEANUP_CONCENTRATION = 0.40
CLEANUP_MIN_PEAK = 8
SHELL_RATIO = 0.50
SHELL_MIN_ROSTERS = 3
MSG_PER_ASSOCIATE = 5.0


def classify(t, as_of):
    r = dict(t)
    d = lambda s: H.days_since(H.parse_ts(s), as_of)
    r["days_msg_sent"] = d(t.get("last_message_sent_by_user"))
    r["days_msg_read"] = d(t.get("last_message_read"))
    r["days_scorecard"] = d(t.get("last_scorecard"))
    r["days_roster"] = d(t.get("last_staffed_roster"))

    recent = lambda v, w: v is not None and v <= w
    msg_recent = recent(r["days_msg_sent"], ENGAGEMENT_WINDOW) or recent(
        r["days_msg_read"], ENGAGEMENT_WINDOW
    )
    sc_recent = recent(r["days_scorecard"], ENGAGEMENT_WINDOW)
    r["pattern"] = {
        (True, True): "HEALTHY_BOTH",
        (True, False): "MSG_ONLY",
        (False, True): "SCORECARD_ONLY",
        (False, False): "BOTH_DARK",
    }[(msg_recent, sc_recent)]
    r["strategic_risk"] = (
        r["pattern"] == "MSG_ONLY"
        and r["days_scorecard"] is not None
        and r["days_scorecard"] >= STRATEGIC_SCORECARD
    )
    # roster-dark only means something if they are entitled to roster
    r["roster_dark"] = bool(t.get("can_roster")) and not recent(
        r["days_roster"], ROSTER_WINDOW
    )

    # ---- revenue axis, from CLOSED invoices only
    series = [
        s["associates"]
        for s in t.get("invoice_series", [])[:TREND_INVOICES]
        if s.get("associates")
    ]
    series = list(reversed(series))  # oldest -> newest
    if len(series) >= 2 and series[0]:
        r["assoc_change"] = (series[-1] - series[0]) / series[0]
        r["assoc_delta"] = series[-1] - series[0]
    else:
        r["assoc_change"] = None
        r["assoc_delta"] = None
    r["assoc_series"] = series
    closed = [s for s in t.get("invoice_series", []) if s.get("invoiceTotal") is not None]
    r["monthly"] = closed[0]["invoiceTotal"] if closed else 0.0
    r["arr"] = r["monthly"] * 12

    ch = r["assoc_change"]
    r["direction"] = (
        "unknown" if ch is None
        else "growing" if ch > TREND_BAND
        else "declining" if ch < -TREND_BAND
        else "flat"
    )

    # a decline explained by a bulk roster cleanup is a data correction,
    # not lost business
    c = t.get("cleanup") or {}
    r["is_cleanup"] = bool(
        r["direction"] == "declining"
        and c.get("concentration", 0) >= CLEANUP_CONCENTRATION
        and c.get("peak_count", 0) >= CLEANUP_MIN_PEAK
    )
    r["cleanup_day"] = c.get("peak_day")
    r["cleanup_count"] = c.get("peak_count")
    if r["is_cleanup"]:
        r["direction_adjusted"] = "data-hygiene"
    else:
        r["direction_adjusted"] = r["direction"]

    # ---- under 10 active associates, consecutive most-recent days
    daily = t.get("daily_active_staff") or {}
    run = 0
    for day in sorted(daily, reverse=True):
        if daily[day] < 10:
            run += 1
        else:
            break
    r["under10_run"] = run
    r["under10"] = run >= UNDER10_RUN
    r["peak_associates"] = max(daily.values()) if daily else None
    # billing that has already stopped: they are under 10 now but the last
    # closed invoice was substantial, so the next one will be near zero
    r["revenue_already_gone"] = r["under10"] and r["monthly"] > 100

    # ---- empty roster shells
    rw, ew = t.get("rosters_in_window", 0), t.get("empty_rosters_in_window", 0)
    r["shell_ratio"] = (ew / rw) if rw else None
    r["shell_flag"] = bool(rw >= SHELL_MIN_ROSTERS and (ew / rw) >= SHELL_RATIO)

    # ---- triage bucket, the single field to act on
    #
    # "Disengaged" means BOTH_DARK (no human messaging AND no scorecard) or
    # roster_dark (entitled to roster but no staffed roster in the window).
    # MSG_ONLY on its own is NOT disengagement: it means comms are in use and
    # the performance workflow moved elsewhere. Treating it as disengagement
    # put accounts that rostered today into CRITICAL and inflated the adoption
    # list to 30% of ARR, which is not a triage list.
    disengaged = r["pattern"] == "BOTH_DARK" or r["roster_dark"]
    declining = r["direction_adjusted"] == "declining"

    if not t.get("can_roster"):
        r["bucket"] = "NOT_ENTITLED"
    elif r["is_cleanup"]:
        r["bucket"] = "DATA_HYGIENE"
    elif r["pattern"] == "BOTH_DARK" and (t.get("active_staff") or 0) == 0:
        r["bucket"] = "BILLING_RECONCILIATION"
    elif declining and disengaged:
        r["bucket"] = "CRITICAL"
    elif disengaged:
        # paying, not declining, but not using the core workflow
        r["bucket"] = "ADOPTION_RISK"
    elif declining:
        r["bucket"] = "CONTRACTION"
    elif r["strategic_risk"]:
        # scorecard workflow has left Hera while comms continue
        r["bucket"] = "STRATEGIC_RISK"
    elif r["shell_flag"] or r["pattern"] == "SCORECARD_ONLY":
        r["bucket"] = "WATCH"
    else:
        r["bucket"] = "HEALTHY"
    return r


def plural(n, word):
    return f"{n} {word}" + ("" if n == 1 else "s")


def money(v):
    return f"${v:,.0f}"


def build_report(rows, as_of, window):
    total_arr = sum(r["arr"] for r in rows)
    total_assoc = sum(r.get("active_staff") or 0 for r in rows)
    L = []
    w = L.append
    w("# CS Health Weekly")
    w("")
    w(f"**As of {as_of}.** {len(rows)} paying tenants, "
      f"{len(set(H.base_customer_name(r['companyName']) for r in rows))} customers, "
      f"{money(total_arr)} ARR, {total_assoc:,} active associates.")
    w("")
    w(f"Engagement window {ENGAGEMENT_WINDOW} days, roster window {ROSTER_WINDOW} days, "
      f"revenue direction over the last {TREND_INVOICES} closed invoices. "
      f"Billing is {money(H.RATE_PER_ASSOCIATE_MONTH)} per active associate per month.")
    w("")
    w("Generated by `analysis/tenant-engagement/classify.py`. "
      "Model rationale: `analysis/cs-health-baseline-2026-07/findings.md`.")
    w("")
    w("---")
    w("")

    # triage headline
    w("## Triage")
    w("")
    order = ["CRITICAL", "ADOPTION_RISK", "BILLING_RECONCILIATION", "STRATEGIC_RISK",
             "CONTRACTION", "WATCH", "DATA_HYGIENE", "NOT_ENTITLED", "HEALTHY"]
    reading = {
        "CRITICAL": "Declining revenue and disengaged. Work these first.",
        "ADOPTION_RISK": "Paying, not declining, not using it. Adoption conversation, not a save.",
        "BILLING_RECONCILIATION": "Dark with zero active associates. Confirm or cancel, do not sell.",
        "STRATEGIC_RISK": "Comms current, scorecard workflow gone 60+ days. Ask what happened, do not sell.",
        "CONTRACTION": "Losing associates but still engaged. Their business is shrinking, not a CS failure.",
        "WATCH": "One soft signal only. No action, review next week.",
        "DATA_HYGIENE": "Associate drop explained by a bulk roster cleanup. Billing self-corrected.",
        "NOT_ENTITLED": "No rostering module. Judge on coaching and scorecard only.",
        "HEALTHY": "No flags.",
    }
    w("| Bucket | Tenants | ARR | Share | Reading |")
    w("|---|---|---|---|---|")
    for b in order:
        sel = [r for r in rows if r["bucket"] == b]
        if not sel:
            continue
        arr = sum(r["arr"] for r in sel)
        share = (arr / total_arr * 100) if total_arr else 0
        w(f"| **{b}** | {len(sel)} | {money(arr)} | {share:.1f}% | {reading[b]} |")
    w("")

    # engagement pattern table, the meeting-ready summary from the daily skill
    w("## Engagement patterns")
    w("")
    w("| Pattern | Tenants | Active associates | Monthly | Share of MRR |")
    w("|---|---|---|---|---|")
    mrr = sum(r["monthly"] for r in rows)
    for p in ("HEALTHY_BOTH", "MSG_ONLY", "SCORECARD_ONLY", "BOTH_DARK"):
        sel = [r for r in rows if r["pattern"] == p]
        if not sel:
            continue
        m = sum(r["monthly"] for r in sel)
        w(f"| {p} | {len(sel)} | {sum(r.get('active_staff') or 0 for r in sel):,} | "
          f"{money(m)} | {(m/mrr*100) if mrr else 0:.1f}% |")
    w("")

    def table(sel, title, note, cols="full"):
        if not sel:
            return
        arr = sum(r["arr"] for r in sel)
        w(f"## {title}")
        w("")
        w(f"**{plural(len(sel), 'tenant')}, {money(arr)} ARR.** {note}")
        w("")
        w("| Account | Assoc | Monthly | Assoc change | Msg sent | Msg read | Scorecard | Roster | Pattern |")
        w("|---|---|---|---|---|---|---|---|---|")
        fmt = lambda v: "n/a" if v is None else f"{v}d"
        for r in sorted(sel, key=lambda x: -x["monthly"]):
            ch = "n/a" if r["assoc_change"] is None else f"{r['assoc_change']*100:+.0f}%"
            nm = str(r["companyName"]).replace("|", "\\|")
            w(f"| {nm} | {r.get('active_staff') or 0} | {money(r['monthly'])} | {ch} | "
              f"{fmt(r['days_msg_sent'])} | {fmt(r['days_msg_read'])} | "
              f"{fmt(r['days_scorecard'])} | {fmt(r['days_roster'])} | {r['pattern']} |")
        w("")

    table([r for r in rows if r["bucket"] == "CRITICAL"], "Critical",
          "Revenue falling and engagement gone. Sorted by monthly revenue.")
    table([r for r in rows if r["bucket"] == "BILLING_RECONCILIATION"],
          "Billing reconciliation",
          "Dark with zero active associates. Their next invoice is already near zero.")
    table([r for r in rows if r["bucket"] == "ADOPTION_RISK"], "Adoption risk",
          "Paying and not declining, but not using the core workflow. "
          "Adoption conversation, never a save play.")
    table([r for r in rows if r["bucket"] == "CONTRACTION"], "Business contraction",
          "Losing associates while still engaged. Their operation is shrinking. "
          "Forecast the loss rather than chasing it.")

    strat = [r for r in rows if r["strategic_risk"]]
    if strat:
        w("## Strategic risk: scorecard workflow has left Hera")
        w("")
        w(f"**{plural(len(strat), 'tenant')}, {money(sum(r['arr'] for r in strat))} ARR.** "
          f"Messaging is current but no scorecard in {STRATEGIC_SCORECARD}+ days. "
          "They are doing performance management somewhere else. Ask, do not sell.")
        w("")
        w("| Account | Assoc | Monthly | Days since scorecard |")
        w("|---|---|---|---|")
        for r in sorted(strat, key=lambda x: -x["monthly"]):
            nm = str(r["companyName"]).replace("|", "\\|")
            w(f"| {nm} | {r.get('active_staff') or 0} | {money(r['monthly'])} | "
              f"{r['days_scorecard']} |")
        w("")

    gone = [r for r in rows if r["revenue_already_gone"]]
    if gone:
        w("## Revenue that has already stopped")
        w("")
        w(f"**{plural(len(gone), 'tenant')}, {money(sum(r['arr'] for r in gone))} of annualised ARR.** "
          "Under 10 active associates now, but the last closed invoice was over $100. "
          "The next invoice will be near zero. Do not count this as ARR at risk.")
        w("")
        w("| Account | Peak associates | Now | Days under 10 | Last closed invoice |")
        w("|---|---|---|---|---|")
        for r in sorted(gone, key=lambda x: -x["monthly"]):
            nm = str(r["companyName"]).replace("|", "\\|")
            w(f"| {nm} | {r['peak_associates']:.0f} | {r.get('active_staff') or 0} | "
              f"{r['under10_run']} | {money(r['monthly'])} |")
        w("")

    shells = [r for r in rows if r["shell_flag"]]
    if shells:
        w("## Empty roster shells")
        w("")
        w(f"**{plural(len(shells), 'tenant')}, {money(sum(r['arr'] for r in shells))} ARR.** "
          f"At least {int(SHELL_RATIO*100)}% of rosters opened in the window contain no "
          "routes. Somebody opens the tool and does nothing with it. Note that most "
          "tenants have the odd empty roster, so only the ratio is meaningful.")
        w("")
        w("| Account | Empty / total | Assoc | Monthly | Bucket |")
        w("|---|---|---|---|---|")
        for r in sorted(shells, key=lambda x: -x["monthly"]):
            nm = str(r["companyName"]).replace("|", "\\|")
            w(f"| {nm} | {r['empty_rosters_in_window']}/{r['rosters_in_window']} | "
              f"{r.get('active_staff') or 0} | {money(r['monthly'])} | {r['bucket']} |")
        w("")

    cleanups = [r for r in rows if r["is_cleanup"]]
    if cleanups:
        w("## Roster cleanups, not churn")
        w("")
        w(f"**{plural(len(cleanups), 'tenant')}.** Associate count fell, but the drop is "
          "concentrated on a single day, which is a customer tidying stale records "
          "rather than losing drivers. Billing corrected itself. Do not run a save play.")
        w("")
        w("| Account | Assoc | Monthly | Assoc change | Moved inactive on |")
        w("|---|---|---|---|---|")
        for r in sorted(cleanups, key=lambda x: -x["monthly"]):
            nm = str(r["companyName"]).replace("|", "\\|")
            ch = "n/a" if r["assoc_change"] is None else f"{r['assoc_change']*100:+.0f}%"
            w(f"| {nm} | {r.get('active_staff') or 0} | {money(r['monthly'])} | {ch} | "
              f"{r['cleanup_count']} on {r['cleanup_day']} |")
        w("")

    # multi-site rollup
    groups = {}
    for r in rows:
        groups.setdefault(H.base_customer_name(r["companyName"]), []).append(r)
    multi = {k: v for k, v in groups.items() if len(v) > 1}
    if multi:
        w("## Multi-site customers")
        w("")
        w(f"**{len(multi)} customers across {sum(len(v) for v in multi.values())} tenants.** "
          "Secondary sites appear as separate tenants and `parentAccountId` does not "
          "link them, so these are matched by name. Treat each group as one relationship.")
        w("")
        w("| Customer | Tenants | Combined ARR | Buckets |")
        w("|---|---|---|---|")
        for k, v in sorted(multi.items(), key=lambda kv: -sum(x["arr"] for x in kv[1])):
            b = ", ".join(sorted(set(x["bucket"] for x in v)))
            w(f"| {k} | {len(v)} | {money(sum(x['arr'] for x in v))} | {b} |")
        w("")

    w("## Caveats")
    w("")
    w("- Monthly figures come from the last **closed** invoice. The current month is "
      "still accruing as `Pending` and must never be used for revenue.")
    w("- Thresholds were set from the July 2026 distribution and are **not seasonally "
      "adjusted**. Peak season is not yet accounted for, so a summer decline cannot be "
      "separated from a seasonal trough.")
    w("- Revenue direction uses associate counts, which the customer controls via "
      "Active status and updates late. Declines are checked for bulk cleanups; the "
      "check is heuristic, not certain.")
    w("- `NOT_ENTITLED` tenants lack the rostering module and are scored only on "
      "coaching and scorecard activity.")
    errs = [r for r in rows if r.get("errors")]
    if errs:
        w(f"- **{len(errs)} tenants had at least one signal lookup fail** and are "
          "reported with `n/a` in that column rather than dropped.")
    w("")
    return "\n".join(L)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--as-of", default=None)
    args = ap.parse_args()
    if args.as_of:
        path = os.path.join(DATA, f"signals-{args.as_of}.json")
    else:
        files = sorted(glob.glob(os.path.join(DATA, "signals-*.json")))
        if not files:
            raise SystemExit("no signals file found. Run three_signals.py first.")
        path = files[-1]
    payload = json.load(open(path))
    as_of = dt.date.fromisoformat(payload["as_of"])
    rows = [classify(t, as_of) for t in payload["tenants"]]
    os.makedirs(REPORTS, exist_ok=True)
    out = os.path.join(REPORTS, f"{as_of}-cs-health.md")
    with open(out, "w") as fh:
        fh.write(build_report(rows, as_of, payload["window"]))
    print(f"wrote {out}")
    for b in ("CRITICAL", "ADOPTION_RISK", "BILLING_RECONCILIATION", "STRATEGIC_RISK",
              "CONTRACTION", "WATCH", "DATA_HYGIENE", "NOT_ENTITLED", "HEALTHY"):
        n = sum(1 for r in rows if r["bucket"] == b)
        if n:
            print(f"  {b:<24}{n:>4}  {money(sum(r['arr'] for r in rows if r['bucket']==b))}")


if __name__ == "__main__":
    main()
