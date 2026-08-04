import json, os, re
from collections import Counter, defaultdict
DATA = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")
P=json.load(open(os.path.join(DATA, "prevalence.json"))); N=len(P)

EXCLUDE_SUBSTR = ["userNotification"]           # user decision 08-04-2026: system read receipt
EXCLUDE_EXACT  = {"CreateOptionsCustomListsStaff","DeleteOptionsCustomListsStaff"}

WORKFLOW = [
 ("Associate management", ["staff","associate"]),
 ("Rostering and routes", ["dailyroster","route","rosterchecklist","replaceby","rescuer"]),
 ("Messaging",            ["message","pendingmessage","shortenurl","recurringmessages"]),
 ("Coaching and records", ["counseling","infraction","kudo","coaching"]),
 ("Scorecard / OCR",      ["textract","scorecard"]),
 ("Fleet and devices",    ["vehicle","accident","device"]),
 ("Documents",            ["document","attachment","folder"]),
 ("Compliance and HR",    ["drugtest","physical","uniform","injury","onboard"]),
 ("Ops log and tasks",    ["dailylog","task","note"]),
 ("Admin and config",     ["tenant","user","valuelist","label","optionscustomlists","card","premiumstatus","companynotification","notification"]),
]
def norm(m):
    s=re.sub(r'[^a-z]','',m.lower())
    return s.replace("associate","staff").replace("preferences","preference")
def wf(m):
    s=norm(m)
    for name,keys in WORKFLOW:
        for k in keys:
            if k in s: return name
    return "UNMAPPED"

def keep(m):
    if m in EXCLUDE_EXACT: return False
    n=norm(m)
    return not any(norm(e) in n for e in EXCLUDE_SUBSTR)

cnt=Counter(); unmapped=Counter()
acct_wf={}
for name,v in P.items():
    ms=[m for m in set(v['mutations']) if keep(m)]
    ws=set()
    for m in ms:
        w=wf(m); ws.add(w)
        if w=="UNMAPPED": unmapped[m]+=1
    acct_wf[name]=ws
    for w in ws: cnt[w]+=1

print(f"{N} tenants. Excluded: UpdateUserNotification family, CreateOptionsCustomListsStaff.")
if unmapped: print("UNMAPPED mutations:", dict(unmapped))
print()
print(f"{'PREVALENCE':>11} {'ACCTS':>5}  WORKFLOW                    TIER")
for w,c in cnt.most_common():
    p=c/N*100
    tier = "CORE, absence = risk" if p>=85 else ("COMMON, supporting" if p>=50 else "OPTIONAL, engagement target")
    print(f"{p:10.1f}% {c:5d}  {w:26s}  {tier}")
print()
d=Counter(len(v) for v in acct_wf.values())
print("WORKFLOWS TOUCHED PER ACCOUNT in the last 90 days:")
for k in sorted(d): print(f"   {k:2d} workflows: {d[k]:3d} accounts")
json.dump({k:sorted(v) for k,v in acct_wf.items()}, open(os.path.join(DATA, "acct_workflows.json"), "w"), indent=1)
