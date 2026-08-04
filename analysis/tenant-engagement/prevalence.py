"""Distinct AuditLog mutationName per account, across the whole paying book.

Uses byGroupAndMutationName (group HASH, mutationName RANGE) and walks the sort key,
so cost is ~1 query per distinct mutation per account rather than scanning 96 GB.
"""
import json, os, sys, time
from collections import Counter, defaultdict
from concurrent.futures import ThreadPoolExecutor
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import lib_hera as H
ddb = H.client(); TBL = H.table("AuditLog")

def distinct(group, cap=200):
    out, last = [], None
    while len(out) < cap:
        kce = "#g = :g" if last is None else "#g = :g AND mutationName > :m"
        vals = {":g":{"S":group}}
        if last is not None: vals[":m"]={"S":last}
        try:
            r = ddb.query(TableName=TBL, IndexName="byGroupAndMutationName",
                KeyConditionExpression=kce, ExpressionAttributeNames={"#g":"group"},
                ExpressionAttributeValues=vals, ProjectionExpression="mutationName",
                Limit=1, ScanIndexForward=True)
        except Exception as e:
            return out, str(e)[:60]
        it = r.get("Items", [])
        if not it: break
        last = it[0]["mutationName"]["S"]; out.append(last)
    return out, None

DATA = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")
import glob
newest = sorted(glob.glob(os.path.join(DATA, "signals-*.json")))[-1]
S = json.load(open(newest))
tenants = [(t.get('companyName') or t['group'], t['group']) for t in S['tenants']]
print(f"walking {len(tenants)} paying tenants")
t0=time.time(); res={}; errs=0
def work(x):
    n,g = x
    m,e = distinct(g)
    return n,g,m,e
with ThreadPoolExecutor(max_workers=16) as ex:
    for i,(n,g,m,e) in enumerate(ex.map(work, tenants),1):
        res[n]={"group":g,"mutations":m,"err":e}
        if e: errs+=1
        if i%60==0: print(f"  {i}/{len(tenants)}  {time.time()-t0:.0f}s")
json.dump(res, open(os.path.join(DATA, "prevalence.json"), "w"), indent=1)
N=len(res)
cnt=Counter()
for v in res.values():
    for m in set(v["mutations"]): cnt[m]+=1
print(f"\ndone in {time.time()-t0:.0f}s, {errs} errors, {len(cnt)} distinct mutationName values across {N} tenants\n")
print(f"{'PREVALENCE':>11}  {'ACCTS':>5}  MUTATION")
for m,c in cnt.most_common():
    print(f"{c/N*100:10.1f}%  {c:5d}  {m}")
