"""Did the ADOPTION_RISK shape (roster-dark, messaging, revenue not falling)
precede churn? Retrospective test against every tenant churned in the last 12 months."""
import datetime as dt, json, os, sys
from concurrent.futures import ThreadPoolExecutor
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import lib_hera as H

DATA = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")

AS_OF = dt.date(2026, 8, 3)
CUTOFF = dt.date(2025, 8, 3)

ddb = H.client()
tenants = H.scan_all(ddb, TableName=H.table("Tenant"),
    ProjectionExpression="#g,companyName,customerStatus,accountCanceledReason,firstChurnedDateTime,accountPremiumStatus,totalNumberOfMonthsPaidByTenant",
    ExpressionAttributeNames={"#g": "group"})
rows = tenants  # scan_all already flattens

churned = []
for t in rows:
    if (t.get("customerStatus") or "") != "Churned": continue
    if not H.ever_paid(t): continue
    d = H.parse_ts(t.get("firstChurnedDateTime"))
    if d is None: continue
    d = d.date() if hasattr(d, "date") else d
    if d < CUTOFF or d > AS_OF: continue
    churned.append(dict(group=t["group"], name=t.get("companyName") or t["group"],
                        churn=d, reason=t.get("accountCanceledReason") or "(blank)",
                        can_roster=H.can_roster(t)))
print(f"{len(churned)} paid tenants churned between {CUTOFF} and {AS_OF} with a usable churn date")

def last_staffed_roster(group):
    """Newest roster with a staffed route, scanning back from newest."""
    rs = H.query_all(ddb, TableName=H.table("DailyRoster"), IndexName="byGroup",
        KeyConditionExpression="#g = :g", ExpressionAttributeNames={"#g": "group"},
        ExpressionAttributeValues={":g": {"S": group}},
        ProjectionExpression="id,notesDate,createdAt", ScanIndexForward=False)
    best = None
    for r in rs[:45]:
        f = r
        d = H.roster_date(f.get("notesDate") or f.get("createdAt"), AS_OF)
        if d is None: continue
        routes = H.query_all(ddb, TableName=H.table("Route"), IndexName="gsi-RouteDailyRoster",
            KeyConditionExpression="routeDailyRosterId = :r",
            ExpressionAttributeValues={":r": {"S": f["id"]}},
            ProjectionExpression="id,routeStaffId")
        if any(x.get("routeStaffId") for x in routes):
            if best is None or d > best: best = d
    return best

def last_scorecard(group):
    rs = H.query_all(ddb, TableName=H.table("CompanyScoreCard"), IndexName="byGroup",
        KeyConditionExpression="#g = :g", ExpressionAttributeNames={"#g": "group"},
        ExpressionAttributeValues={":g": {"S": group}},
        ProjectionExpression="createdAt", ScanIndexForward=False, Limit=1)
    if not rs: return None
    d = H.parse_ts(rs[0].get("createdAt"))
    return d.date() if hasattr(d, "date") else d

def work(c):
    try:
        c["last_roster"] = last_staffed_roster(c["group"])
        c["last_scorecard"] = last_scorecard(c["group"])
    except Exception as e:
        c["err"] = str(e)[:80]
    return c

with ThreadPoolExecutor(max_workers=8) as ex:
    out = list(ex.map(work, churned))

for c in out:
    for k in ("last_roster", "last_scorecard"):
        v = c.get(k)
        c[k + "_days_before_churn"] = (c["churn"] - v).days if v else None

json.dump([{**c, "churn": str(c["churn"]),
            "last_roster": str(c.get("last_roster")), "last_scorecard": str(c.get("last_scorecard"))}
           for c in out], open(os.path.join(DATA, "roster-dark-validation.json"), "w"), indent=1)
errs = [c for c in out if c.get("err")]
print(f"wrote data/roster-dark-validation.json  ({len(out)} tenants, {len(errs)} errors)")
