"""Derive a weight per usage signal from actual churn, not judgment.

For every paid churn in the last 12 months, measure days-since-each-signal AT the
churn date. Compare against surviving customers measured today. The lift
(share of churns dark / share of survivors dark) is the weight: a signal that
churned customers went dark on far more often than survivors is predictive.
Lift near 1.0 means the signal carries no information and gets weight 0.

Usage: python3 signal_weights.py
"""
import datetime as dt, json, os, sys
from concurrent.futures import ThreadPoolExecutor
import lib_hera as H

HERE=os.path.dirname(os.path.abspath(__file__)); DATA=os.path.join(HERE,"data")
AS_OF=dt.date(2026,8,4)
SRC = {
 "staff_status":   ("StaffStatus","byGroup","date"),
 "counseling":     ("Counseling","byGroupAndDate","date"),
 "infraction":     ("Infraction","byGroupAndDate","date"),
 "kudo":           ("Kudo","byGroupAndDate","date"),
 "odometer":       ("Vehicle","byGroupAndLastOdometerReadingDate","lastOdometerReadingDate"),
 "vehicle_history":("Accident","byGroupAndAccidentDate","accidentDate"),
 "document":       ("Document","byGroup","uploadDate"),
 "attachment":     ("Attachment","byGroup","createdAt"),
 "textract":       ("TextractJob","byGroupAndDate","date"),
 "daily_log":      ("DailyLog","byDate","date"),
}
ddb=H.client()
def newest(group, tbl, idx, attr):
    try:
        r=ddb.query(TableName=H.table(tbl), IndexName=idx,
            KeyConditionExpression="#g = :g",
            ExpressionAttributeNames={"#g":"group","#a":attr},
            ExpressionAttributeValues={":g":{"S":group}},
            ProjectionExpression="#a", ScanIndexForward=False, Limit=1)
        it=r.get("Items",[])
        return H.flatten(it[0]).get(attr) if it else None
    except Exception:
        return None
def to_date(v, ceiling):
    if not v: return None
    try: d=dt.date.fromisoformat(str(v)[:10])
    except Exception: return None
    return None if d > ceiling else d      # clamp: future-dated is not activity

churn=json.load(open(os.path.join(DATA,"roster-dark-validation.json")))
print(f"{len(churn)} paid churns in the 12 months to {AS_OF}")
def work(c):
    g=c["group"]; ceil=dt.date.fromisoformat(c["churn"])
    out={}
    for k,(tbl,idx,attr) in SRC.items():
        out[k]=to_date(newest(g,tbl,idx,attr), ceil)
    out["last_staffed_roster"]=to_date(c.get("last_roster"), ceil)
    out["last_scorecard"]=to_date(c.get("last_scorecard"), ceil)
    return c, out, ceil
res=[]
with ThreadPoolExecutor(max_workers=16) as ex:
    for i,(c,out,ceil) in enumerate(ex.map(work,churn),1):
        res.append({"name":c["name"],"reason":c["reason"],"churn":c["churn"],
                    "days":{k:((ceil-d).days if d else None) for k,d in out.items()}})
        if i%40==0: print(f"  {i}/{len(churn)}")
json.dump(res, open(os.path.join(DATA,"churn-signal-days.json"),"w"), indent=1)
print(f"wrote data/churn-signal-days.json")
