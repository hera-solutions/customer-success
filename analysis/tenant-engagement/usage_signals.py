"""Last meaningful activity per tenant, from the SOURCE tables.

Why not AuditLog: it only records human-initiated GraphQL mutations, so anything
the system generates for a customer is invisible. DBE Logistics shows zero coaching
mutations in AuditLog while the Infraction and Kudo tables show 995 and 8,412 rows
in the same 90 days. See findings-usage-signals.md.

Each signal below has a group+date GSI, so it costs one descending Limit-1 read.
Roster, human-sent message and scorecard are reused from the newest signals-*.json
rather than recomputed, because the roster logic has to join Route to check a route
was actually assigned, and notesDate is a future-dated target date.

Usage:  python3 usage_signals.py [--as-of YYYY-MM-DD]
Writes data/usage-<as-of>.json
"""
import argparse, datetime as dt, glob, json, os, sys
from concurrent.futures import ThreadPoolExecutor
import lib_hera as H

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "data")

# signal -> (table, index, range attribute). All are group+date.
SRC = {
    "staff_status":   ("StaffStatus",  "byGroup",                          "date"),
    "counseling":     ("Counseling",   "byGroupAndDate",                   "date"),
    "infraction":     ("Infraction",   "byGroupAndDate",                   "date"),
    "kudo":           ("Kudo",         "byGroupAndDate",                   "date"),
    "odometer":       ("Vehicle",      "byGroupAndLastOdometerReadingDate","lastOdometerReadingDate"),
    "vehicle_history":("Accident",     "byGroupAndAccidentDate",           "accidentDate"),
    "document":       ("Document",     "byGroup",                          "uploadDate"),
    "attachment":     ("Attachment",   "byGroup",                          "createdAt"),
    "textract":       ("TextractJob",  "byGroupAndDate",                   "date"),
    "daily_log":      ("DailyLog",     "byDate",                           "date"),
}
# Weights are the churn lift per signal, derived in signal_weights.py, NOT chosen.
# See findings-signal-weights.md. Risk score = sum of weights of every signal the
# account is dark on. Cutoff 15 set by the user 08-04-2026.
WEIGHTS = json.load(open(os.path.join(HERE, "signal-weights.json")))
DARK_DAYS = 30
# The four HEARTBEAT signals: the highest-lift signals, weight >= 3.9. An account
# still doing two or more of these is alive whatever else it has dropped.
HEARTBEAT = [s for s, w in WEIGHTS.items() if w >= 3.9]
# RISK = dark on 3 or more heartbeats. Chosen for CORRECTNESS not optimality:
# 2-of-4 has better recall (65.2% vs 48.5%) but flags DBE Logistics, which is
# active on messaging, scorecard, infractions and kudos within 3 days and must
# never read as at-risk. See findings-signal-weights.md for the caveats, which
# are substantial. This is a CALIBRATION STARTING POINT, not a validated model.
HEARTBEAT_DARK_FOR_RISK = 3

ddb = H.client()

def newest_date(group, table, index, attr):
    try:
        r = ddb.query(TableName=H.table(table), IndexName=index,
            KeyConditionExpression="#g = :g",
            ExpressionAttributeNames={"#g": "group"},
            ExpressionAttributeValues={":g": {"S": group}},
            ProjectionExpression="#a", ScanIndexForward=False, Limit=1)
        # ProjectionExpression needs the attr aliased too; some are reserved words
        items = r.get("Items", [])
        if not items: return None
        v = H.flatten(items[0])
        return v.get(attr)
    except Exception:
        return "ERR"

def newest_date_safe(group, table, index, attr):
    try:
        r = ddb.query(TableName=H.table(table), IndexName=index,
            KeyConditionExpression="#g = :g",
            ExpressionAttributeNames={"#g": "group", "#a": attr},
            ExpressionAttributeValues={":g": {"S": group}},
            ProjectionExpression="#a", ScanIndexForward=False, Limit=1)
        items = r.get("Items", [])
        if not items: return None
        return H.flatten(items[0]).get(attr)
    except Exception as e:
        return f"ERR:{str(e)[:40]}"

def to_date(v, ceiling):
    """Several of these are USER-ENTERED event dates, not system timestamps, and some
    are typos: TextractJob has held 8610-07-17, Accident 2030-09-09. A date after the
    as-of point is not evidence of recent activity, so clamp it away. Erring this way
    risks calling an active account quiet, never the reverse."""
    if not v or (isinstance(v, str) and v.startswith("ERR")): return None
    try: d = dt.date.fromisoformat(str(v)[:10])
    except Exception: return None
    return None if d > ceiling else d

def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--as-of")
    a = ap.parse_args()
    as_of = dt.date.fromisoformat(a.as_of) if a.as_of else dt.date.today()

    sig_file = sorted(glob.glob(os.path.join(DATA, "signals-*.json")))[-1]
    base = json.load(open(sig_file))
    print(f"reusing roster/message/scorecard from {os.path.basename(sig_file)}")
    tenants = base["tenants"]
    print(f"{len(tenants)} tenants, {len(SRC)} source-table signals each")

    def work(t):
        g = t["group"]; out = {}
        for name,(tbl,idx,attr) in SRC.items():
            out[name] = newest_date_safe(g, tbl, idx, attr)
        return t, out

    rows = []
    with ThreadPoolExecutor(max_workers=16) as ex:
        for i,(t,out) in enumerate(ex.map(work, tenants), 1):
            rec = {"group": t["group"], "companyName": t.get("companyName") or t["group"],
                   "active_staff": t.get("active_staff"), "can_roster": t.get("can_roster")}
            # TRAP, fixed 08-04-2026: taking the first NON-ZERO invoice walks backwards past
            # every current invoice on a discounted account and reports a stale pre-discount
            # figure. Outlaw, Spears and CV Delivery all read ~$1,100-1,400/mo when they
            # actually bill $0. invoice_series is newest-first and closed-only, so take [0]
            # verbatim. A zero invoice is a fact about the account, not missing data.
            s = t.get("invoice_series") or []
            rec["monthly"] = float(s[0].get("invoiceTotal") or 0) if s else 0.0
            sigs = dict(out)
            sigs["last_staffed_roster"] = t.get("last_staffed_roster")
            sigs["last_message_sent_by_user"] = t.get("last_message_sent_by_user")
            sigs["last_scorecard"] = t.get("last_scorecard")
            rec["signals"] = sigs
            ds = {k: to_date(v, as_of) for k,v in sigs.items()}
            rec["days"] = {k: ((as_of - d).days if d else None) for k,d in ds.items()}
            allv = [d for d in ds.values() if d]
            rec["last_any"] = str(max(allv)) if allv else None
            rec["days_since_any"] = (as_of - max(allv)).days if allv else None
            dark = lambda k: rec["days"].get(k) is None or rec["days"][k] > DARK_DAYS
            rec["dark_signals"] = sorted(k for k,w in WEIGHTS.items() if w and dark(k))
            rec["risk_score"] = round(sum(w for k,w in WEIGHTS.items() if w and dark(k)), 1)
            rec["heartbeats_dark"] = sorted(s for s in HEARTBEAT if dark(s))
            rec["tier"] = ("RISK" if len(rec["heartbeats_dark"]) >= HEARTBEAT_DARK_FOR_RISK
                           else ("ENGAGE" if rec["heartbeats_dark"] else "ACTIVE"))
            rows.append(rec)
            if i % 60 == 0: print(f"  {i}/{len(tenants)}")

    out_path = os.path.join(DATA, f"usage-{as_of}.json")
    json.dump({"as_of": str(as_of), "tenants": rows}, open(out_path,"w"), indent=1)
    errs = sum(1 for r in rows for v in r["signals"].values() if isinstance(v,str) and v.startswith("ERR"))
    print(f"wrote {out_path}  ({len(rows)} tenants, {errs} signal errors)")

if __name__ == "__main__":
    main()
