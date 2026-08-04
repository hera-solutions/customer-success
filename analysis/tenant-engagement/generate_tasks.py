"""Generate CS outreach tasks in Zoho from the daily usage run.

PRE-ROLLOUT SAFETY: dry-run is the DEFAULT. Nothing is written to Zoho unless
--write is passed explicitly. No customer contact is authorised as of 08-04-2026.

NOT YET IMPLEMENTED, and --write refuses because of it:
  - No Zoho writer exists. This script only produces the plan JSON.
  - Decision 3, the 30-day cooldown, needs to read existing tasks. COOLDOWN_DAYS is
    defined and unused, so a closed task would regenerate the next morning.
  - Decision 5, recovery auto-closing an open task, needs the same read.
  All seven Zoho custom fields DO exist and every picklist value matches the
  constants below, verified live 08-04-2026.

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
    python3 generate_tasks.py --write         # REFUSES: no writer is implemented yet
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


def load_history(as_of):
    """
    Daily activeStaff per tenant from InvoiceLineItem, built by staff_history.py.

    Required by decision 08-04-2026: driver counts come from
    InvoiceLineItem.activeStaff, never Invoice.averageActiveDriverCount (a monthly
    average that cannot show a change inside a month) and no longer from the Staff
    table (current state only, no history).
    """
    f = os.path.join(DATA, f"staff-history-{as_of}.json")
    if not os.path.exists(f):
        cands = sorted(glob.glob(os.path.join(DATA, "staff-history-*.json")))
        if not cands:
            sys.exit("no staff-history-*.json found. Run: python3 staff_history.py")
        f = cands[-1]
    h = json.load(open(f))
    print(f"driver counts from {os.path.basename(f)} (InvoiceLineItem.activeStaff)")
    return {t["companyName"]: t for t in h["tenants"]}


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

def driver_direction(h):
    """
    Change in DRIVER COUNT from the daily series, replacing revenue_direction().

    The old version compared the newest closed invoice against one FOUR MONTHS
    OLDER and read Invoice.averageActiveDriverCount. It produced two false
    readings, both found by John on 08-04-2026:

      TPE     "growing +17%" while the driver list had not moved in 55 days. The
              growth was real but ENDED 06-15-2026. A four-month-old fact stated
              in the present tense.
      Probyn  "growing +55%" for an account that fell 127 -> 26 drivers in April
              and partially rebounded. The window began at the bottom of the
              crash, so a 67% revenue loss printed as growth.

    A daily series fixes both: 30 days is recent enough to be true now, and the
    90-day peak catches a collapse the 30-day window would miss.
    """
    if not h or h.get("latest") is None:
        return "driver count unknown, no billing line items"
    cur = h["latest"]
    c30 = (h.get("change") or {}).get("30")
    if not c30:
        out = f"{cur} drivers, no history 30 days back"
    else:
        pct = c30["pct"] or 0
        word = "growing" if pct > 5 else ("declining" if pct < -5 else "flat")
        out = f"{word}, {c30['then']} -> {cur} drivers in 30 days ({pct:+.0f}%)"
    peak = h.get("peak")
    if peak and cur and (peak - cur) / peak * 100 >= 20:
        out += (f". PEAKED at {peak} drivers on {h.get('peak_date')}, "
                f"down {(peak - cur) / peak * 100:.0f}% since")
    return out


def frozen_roster(h):
    """
    A roster nobody maintains flatlines, and we keep billing it.

    Direct evidence, not inference: activeStaff is recorded daily, so a run of
    identical values means the number literally did not move. TPE changed 28 times
    in 90 days and then sat at EXACTLY 115 for 50 days.

    Two guards, both learned the hard way:
      - Under 10 drivers this is just a dead account, already caught by the value
        floor. Flagging it adds noise.
      - NOT BILLED PER DRIVER means a frozen roster costs the customer nothing.
        Divine Package (43 drivers) and Double Iron (18) are flat-fee, so calling
        them over-billed would be false. This also resolves the "18 drivers at
        $25" figure flagged as impossible on 08-03-2026: it was always correct.
    """
    if not h or not h.get("frozen") or (h.get("latest") or 0) < 10:
        return None
    if not h.get("per_driver_billing"):
        return (f"  Roster unchanged {h['days_frozen']} days at {h['latest']} drivers, but this "
                f"account is NOT billed per driver, so\n"
                f"     there is no over-billing. Treat the frozen list as an adoption signal only.")
    return (f"  ROSTER FROZEN {h['days_frozen']} DAYS at {h['latest']} drivers, after "
            f"{h['changes_in_window']} changes in the prior {h.get('window_days')} days.\n"
            f"     They are billed per driver, so EXPECT OVER-BILLING. Check the roster before "
            f"asking for anything,\n"
            f"     and route it to Matthew if drivers have left without being deactivated.")


def describe(kind, members, sigmap, as_of, hist=None):
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
        h = (hist or {}).get(m["companyName"]) or {}
        cnt = h.get("latest")
        asof_note = "" if (h.get("days_stale") or 0) <= 1 else f", as of {h.get('latest_date')}"
        lines.append(f"  Pays: ${m['monthly']:,.0f}/mo on the last closed invoice. "
                     f"{cnt if cnt is not None else m['active_staff']} drivers billed{asof_note}.")
        lines.append(f"  Driver count: {driver_direction(h)}")
        fz = frozen_roster(h)
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
    hist = load_history(as_of)

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
        # Billed driver count, not the Staff table. They agree on 212 of 241
        # accounts and differ only by the 1-day feed lag, but the billed figure is
        # the one we charge on, so it is the one the value floor should use.
        total_staff = sum((hist.get(m["companyName"], {}) or {}).get("latest")
                          if (hist.get(m["companyName"], {}) or {}).get("latest") is not None
                          else (m["active_staff"] or 0) for m in members)
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
                         description=describe(kind, members, sigmap, as_of, hist)))

    from collections import Counter
    c = Counter(p["kind"] for p in plan)
    print(f"source: {src}   as of {fmt_us(as_of)}")
    if a.write:
        sys.exit("--write REFUSED: no Zoho writer is implemented. This script only "
                 "produces the plan JSON.\n"
                 "Also missing before it can write safely: the 30-day cooldown "
                 "(decision 3) and\nrecovery auto-close (decision 5), both of which "
                 "need to read existing tasks. Without\nthe cooldown, a task closed "
                 "today regenerates tomorrow morning.")
    print("MODE: DRY RUN, nothing will be created\n")
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
    print("\nDRY RUN. No writer exists yet, so this is currently the only mode.")
    return plan

if __name__ == "__main__":
    main()
