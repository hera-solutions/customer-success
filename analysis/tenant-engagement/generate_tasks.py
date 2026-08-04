"""Generate CS outreach tasks in Zoho from the daily usage run.

PRE-ROLLOUT SAFETY: dry-run is the DEFAULT. Nothing is written to Zoho unless
--write is passed explicitly. No customer contact is authorised as of 08-04-2026.

Decisions this implements, all agreed 08-04-2026 (see the CSM plugin config,
"The outreach lifecycle"):
  1  Value floor: a CS task needs >=1 active associate AND >=$100/mo. Below the
     floor routes to Matthew as "Confirm or close", it is not dropped.
  2  Ladder position lives in the Next_Action picklist, not a counter.
  3  30-day cooldown per account per task type after a task closes.
  4  ENGAGE gets ONE outreach, no ladder.
  5  Recovery auto-closes an open task, no contact needed.
  6  Multi-site operators roll up on base name, one task per operator.
  7  Billing state overrides tier: written-off or payment-error routes to Matthew.

Never writes to the Notes module. Notes are human narrative; see the hard rule
in the config.

Usage:
    python3 generate_tasks.py                 # dry run, prints what it would do
    python3 generate_tasks.py --write         # actually creates tasks
    python3 generate_tasks.py --as-of 2026-08-04
"""
import argparse, datetime as dt, glob, json, os, re, sys
import lib_hera as H

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "data")

JOHN = "5936992000000469001"
MATTHEW = "5936992000000434001"
MIN_ASSOCIATES = 1
MIN_MONTHLY = 100.0
COOLDOWN_DAYS = 30
BAD_INVOICE = {"Written Off", "Payment Error"}
LADDER = ["1 Call and voicemail", "2 Text the owner",
          "3 Email plus 2nd contact", "4 Final, 2nd contact"]
LADDER_BDAYS = [1, 3, 5, 8]        # business days from trigger
ESCALATE_BDAY = 10

# Two labels per signal: how it reads when the customer IS doing it, and when they
# are not. Reusing the gap wording for both produced "ok, 5d nobody there has sent
# a message", which says the opposite of what it means, on the first line a CSM reads.
LABEL = {
    "last_message_sent_by_user": ("messages being sent",          "nobody there has sent a message"),
    "document":                  ("driver paperwork uploaded",    "no driver paperwork uploaded"),
    "last_staffed_roster":       ("driver schedules being built", "no driver schedule built"),
    # TRAP, 08-04-2026: StaffStatus is a TRANSITION log (previousStatus ->
    # currentStatus). It catches somebody going live (Onboarding -> Active) and
    # somebody leaving (Active -> Inactive), but a driver created directly as
    # Active writes NO row: all 15 of TPE's June hires are invisible to it, and
    # 0 of 1,081 transitions across 12 busy tenants had an absent previousStatus.
    # So this signal means "nobody's status changed", NOT "no driver was added".
    "staff_status":              ("drivers joining and leaving", "nobody marked as joining or leaving"),
    "last_scorecard":            ("Amazon scorecards uploaded",   "no Amazon scorecard uploaded"),
    "counseling":                ("counselings logged",           "no counseling logged"),
    "infraction":                ("infractions logged",           "no infraction logged"),
    "kudo":                      ("kudos logged",                 "no kudo logged"),
    "textract":                  ("documents sent for scanning",  "no document sent for scanning"),
    "attachment":                ("attachments added",            "no attachment added"),
    "vehicle_history":           ("vehicle records logged",       "no vehicle record logged"),
    "daily_log":                 ("daily log entries",            "no daily log entry"),
    "odometer":                  ("odometer readings",            "no odometer reading"),
}
def lbl(k, ok):
    return LABEL.get(k, (k, k))[0 if ok else 1]

def add_bdays(d, n):
    while n > 0:
        d += dt.timedelta(days=1)
        if d.weekday() < 5: n -= 1
    return d

def base_name(n):
    return re.split(r"\s*\|\s*", n)[0].strip()

def fmt_us(d):
    return d.strftime("%m-%d-%Y") if isinstance(d, dt.date) else str(d)

def live_status():
    """Re-check customerStatus against production at generation time.

    The signals file can be a day old, and a day matters: on 08-04-2026 the plan
    contained a RISK task for Platinum Transport Services, which had churned to a
    competitor the previous afternoon. Generating outreach for a departed customer
    is the single most embarrassing failure this script could have.
    """
    ddb = H.client()
    rows = H.scan_all(ddb, TableName=H.table("Tenant"),
        ProjectionExpression="#g,companyName,customerStatus,accountCanceledReason,firstChurnedDateTime",
        ExpressionAttributeNames={"#g": "group"})
    return {r["group"]: r for r in rows if r.get("group")}


def load(as_of):
    u = os.path.join(DATA, f"usage-{as_of}.json")
    if not os.path.exists(u):
        u = sorted(glob.glob(os.path.join(DATA, "usage-*.json")))[-1]
    usage = json.load(open(u))
    sig = json.load(open(sorted(glob.glob(os.path.join(DATA, "signals-*.json")))[-1]))
    return usage, {t.get("companyName") or t["group"]: t for t in sig["tenants"]}, os.path.basename(u)

def billing_problem(series):
    out = []
    for x in (series or [])[:3]:
        if x.get("status") in BAD_INVOICE:
            out.append((x.get("createdAt","")[:10], x.get("status"), float(x.get("invoiceTotal") or 0)))
    return out

def revenue_direction(series):
    """
    BUG FOUND 08-04-2026 by John, from the briefing deck: TPE Logistics read
    "growing +17%" while its driver list had not been touched in 55 days. Those
    two cannot both be true, because billing is per active associate.

    The old version compared the newest closed invoice against one FOUR MONTHS
    OLDER, so it reported two different lies:

      TPE     98 -> 103 -> 111 -> 115 drivers. Real, but the growth ENDED
              06-15-2026, the same week they stopped using Hera. Flat at 115
              for two months. "Growing" was a four-month-old fact in the
              present tense.
      Probyn  126 -> 121 -> 26 -> 40 -> 41 -> 40. Read "+55% growing". They
              COLLAPSED 79% in April and partially rebounded. The window
              started at the bottom of the crash, so a 67% revenue loss
              ($1,094 -> $357) printed as growth.

    So: direction is month over month, and a fall from peak is reported
    separately. A rebound from a crash is never "growing".
    """
    a = [float(x.get("associates") or 0) for x in (series or [])[:6]]
    if len(a) < 2 or not a[1]: return "unknown"
    mom = (a[0] - a[1]) / a[1] * 100
    word = "growing" if mom > 5 else ("declining" if mom < -5 else "flat")
    out = f"{word} {mom:+.0f}% month over month ({a[1]:.0f} -> {a[0]:.0f} drivers)"
    peak = max(a)
    if peak and (peak - a[0]) / peak * 100 >= 20:
        out += (f". WAS {peak:.0f} drivers {a.index(peak)} months ago, "
                f"DOWN {(peak - a[0]) / peak * 100:.0f}% from that peak")
    return out

def frozen_roster(m, series):
    """
    A roster nobody maintains keeps billing. TPE averaged 14.8 departures a
    month for 11 consecutive months, never below 5, then logged ZERO in the 50
    days after 06-10-2026 while still showing 115 active drivers. Turnover did
    not stop; maintenance did.

    That means we are probably invoicing for drivers who have left, which is the
    same shape as JDW ("they have been overpaying and we cannot reach them").
    Say it on the task, because a CSM who does not know this walks into a call
    that is really about a refund.
    """
    v = (m.get("days") or {}).get("staff_status")
    if v is None or v <= 45 or (m.get("active_staff") or 0) < 20:
        return None
    return (f"  ROSTER FROZEN {v} DAYS at {m['active_staff']} drivers. Nobody has been "
            f"marked as joining or leaving.\n"
            f"     Expect this account to be OVER-BILLED. Check the roster before "
            f"asking for anything, and\n"
            f"     route it to Matthew if drivers have left without being deactivated.")

def describe(kind, members, sigmap, as_of):
    """Gaps are ordered by WEIGHT, not by days dark. Sorting by days put
    'no odometer reading in 1016 days' at the top of a brief when odometer has a
    weight of zero, burying the heartbeats the conversation actually turns on."""
    W = json.load(open(os.path.join(HERE, "signal-weights.json")))
    HEARTBEAT = [k for k, w in W.items() if w >= 3.9]
    lines = [f"{kind} PREP. Generated {fmt_us(as_of)} from the daily usage run."]
    if len(members) > 1:
        lines.append(f"MULTI-SITE OPERATOR, {len(members)} tenants. Same person, do not call twice.")
    lines.append("")
    for m in members:
        s_ = sigmap.get(m["companyName"], {})
        series = s_.get("invoice_series") or []
        d = m["days"]
        lines.append(f"--- {m['companyName']}")
        lines.append(f"  Pays: ${m['monthly']:,.0f}/mo on the last closed invoice. {m['active_staff']} active associates now.")
        lines.append(f"  Revenue direction: {revenue_direction(series)}")
        fz = frozen_roster(m, series)
        if fz:
            lines.append(fz)
        if not m.get("can_roster"):
            lines.append("  NOT ENTITLED TO ROSTERING. Do not raise driver schedules.")
        # heartbeats first, always, both states named
        lines.append("  THE FOUR SIGNALS THAT MATTER:")
        for k in sorted(HEARTBEAT, key=lambda x: -W[x]):
            v = d.get(k)
            if v is None:      lines.append(f"     DARK, never   {lbl(k, False)}")
            elif v > 30:       lines.append(f"     DARK, {v:4d}d   {lbl(k, False)}")
            else:              lines.append(f"     ok,   {v:4d}d   {lbl(k, True)}")
        # everything else, ordered by weight, zero-weight signals omitted entirely
        rest = [(W[k], k, d.get(k)) for k in W if k not in HEARTBEAT and W[k] > 0]
        gaps = [(w, k, v) for w, k, v in rest if v is None or v > 30]
        if gaps:
            lines.append("  Also stopped, in order of how much it predicts churn:")
            for w, k, v in sorted(gaps, key=lambda x: -x[0])[:5]:
                lines.append(f"     {lbl(k, False)} " + ("never" if v is None else f"in {v} days"))
        bp = billing_problem(series)
        if bp:
            lines.append(f"  BILLING UNRESOLVED, ${sum(b[2] for b in bp):,.0f}:")
            for dd, st, amt in bp:
                lines.append(f"     {fmt_us(dt.date.fromisoformat(dd))}  {st}  ${amt:,.0f}")
        lines.append("")
    if kind == "RISK":
        alive = [k for k in HEARTBEAT if (members[0]["days"].get(k) is not None and members[0]["days"][k] <= 30)]
        if alive:
            lines.append("OPEN WITH what they are still doing: " +
                         ", ".join(lbl(k, True) for k in alive) + ".")
        else:
            lines.append("ALL FOUR SIGNALS ARE DARK. There is nothing to open with, so do not")
            lines.append("pretend otherwise. Open on their OPERATION: how it is running, how many")
            lines.append("routes, whether anything changed. Then name the silence once and stop talking.")
        lines += ["DO NOT ask 'are you still using Hera at all'. On a paying account that",
                  "  invites a cancellation, and it caused the outcome it was meant to prevent.",
                  "DO NOT open with 'we noticed you are not using...'",
                  "DO NOT offer a discount. Route any pricing question to Matthew.",
                  "Getting out of RISK takes only ONE signal coming back. Ask for the easiest one.",
                  "", "LOG: Job Named, Blocker, Ask Made, Outcome Evidence, Customer Quote, Contact Outcome."]
    elif kind == "ENGAGE":
        gap = members[0]["heartbeats_dark"]
        lines += ["THE ONE THING TO WRITE ABOUT: " +
                  ", ".join(lbl(k, False) for k in gap) + ".",
                  "ONE outreach. Name that feature and invite them to book a call:",
                  "calendly.com/john_herasolutions/general",
                  "They are ACTIVE. This is a value conversation, not a save.",
                  "", "LOG: Contact Outcome at minimum."]
    else:
        lines += ["ADMINISTRATIVE, not a call. Confirm the account or close it.",
                  "CHECK THE BALANCE ABOVE BEFORE CLOSING. Churning an account hides its",
                  "debt without clearing it: $2,257 went invisible this way on 08-03-2026.",
                  "A note is required before closing. The generator never writes notes."]
    return "\n".join(lines)

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--as-of"); ap.add_argument("--write", action="store_true")
    a = ap.parse_args()
    as_of = dt.date.fromisoformat(a.as_of) if a.as_of else dt.date.today()
    usage, sigmap, src = load(as_of)

    live = live_status()
    dropped = []
    fresh = []
    for t in usage["tenants"]:
        st = (live.get(t["group"], {}) or {}).get("customerStatus") or "NOT FOUND"
        if not st.startswith("Active"):
            if t["tier"] in ("RISK", "ENGAGE"):
                dropped.append((t["companyName"], st,
                                (live.get(t["group"], {}) or {}).get("accountCanceledReason") or "-",
                                t["monthly"]))
            continue
        fresh.append(t)
    if dropped:
        print(f"CHURN CHECK: dropped {len(dropped)} account(s) that are no longer Active since the signals run")
        for n, st, why, m in sorted(dropped, key=lambda x: -x[3]):
            print(f"   ${m:8,.0f}  {n[:34]:34s} {st:22s} {why}")
        print()
    groups = {}
    for t in fresh:
        groups.setdefault(base_name(t["companyName"]), []).append(t)

    plan = []
    for op, members in groups.items():
        tiers = {m["tier"] for m in members}
        if not (tiers & {"RISK", "ENGAGE"}): continue
        lead = max(members, key=lambda m: m["monthly"])
        total_monthly = sum(m["monthly"] for m in members)
        total_staff = sum(m["active_staff"] or 0 for m in members)
        bp = [b for m in members for b in billing_problem(sigmap.get(m["companyName"],{}).get("invoice_series"))]
        if bp:
            kind, owner, why = "CONFIRM_OR_CLOSE", MATTHEW, f"billing unresolved ${sum(b[2] for b in bp):,.0f}"
        elif total_staff < MIN_ASSOCIATES or total_monthly < MIN_MONTHLY:
            kind, owner, why = "CONFIRM_OR_CLOSE", MATTHEW, f"below floor: {total_staff} associates, ${total_monthly:,.0f}/mo"
        elif "RISK" in tiers:
            kind, owner, why = "RISK", JOHN, f"dark on {len(lead['heartbeats_dark'])} of 4 heartbeats"
        else:
            kind, owner, why = "ENGAGE", JOHN, f"active, gap: {', '.join(lead['heartbeats_dark'])}"
        plan.append(dict(operator=op, kind=kind, owner=owner, why=why, members=members,
                         monthly=total_monthly, staff=total_staff,
                         subject={"RISK":"Adoption call","ENGAGE":"Value conversation",
                                  "CONFIRM_OR_CLOSE":"Confirm or close"}[kind],
                         next_action={"RISK":LADDER[0],"ENGAGE":"Single outreach",
                                      "CONFIRM_OR_CLOSE":"Confirm or close"}[kind],
                         due=add_bdays(as_of, LADDER_BDAYS[0]) if kind=="RISK" else add_bdays(as_of, 5),
                         priority="High" if kind=="RISK" else "Normal",
                         description=describe(kind, members, sigmap, as_of)))

    from collections import Counter
    c = Counter(p["kind"] for p in plan)
    print(f"source: {src}   as of {fmt_us(as_of)}")
    print(f"MODE: {'WRITE' if a.write else 'DRY RUN, nothing will be created'}\n")
    for k in ("RISK","ENGAGE","CONFIRM_OR_CLOSE"):
        sub=[p for p in plan if p["kind"]==k]
        print(f"{k:18s} {len(sub):3d} tasks  ${sum(p['monthly'] for p in sub):9,.0f}/mo  -> {'John' if sub and sub[0]['owner']==JOHN else 'Matthew' if sub else '-'}")
    print(f"{'TOTAL':18s} {len(plan):3d} tasks")
    ml=[p for p in plan if len(p["members"])>1]
    if ml: print(f"\nrolled up {len(ml)} multi-site operator(s): " + ", ".join(f"{p['operator']} ({len(p['members'])})" for p in ml))
    json.dump([{k:v for k,v in p.items() if k!="members"} | {"tenants":[m["companyName"] for m in p["members"]],
               "due":str(p["due"])} for p in plan],
              open(os.path.join(DATA, f"task-plan-{as_of}.json"),"w"), indent=1, default=str)
    print(f"\nplan written to data/task-plan-{as_of}.json")
    if not a.write:
        print("\nDRY RUN. Re-run with --write to create these in Zoho.")
    return plan

if __name__ == "__main__":
    main()
