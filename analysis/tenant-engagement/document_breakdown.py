"""What the "driver paperwork" heartbeat actually measures.

RAISED BY JOHN 08-05-2026: "for the paperwork heartbeat, I want to know what that
actually includes, because I think combining multiple actions for a simple upload
might throw off the numbers."

He is right, and it is worse than a labelling problem.

The signal is "newest uploadDate on the Document table". Document is a single table
holding EVERY file in the product, 20.3 million rows, and across the 25 largest
tenants it breaks down as:

    96.8%   daily-log vehicle photos       photo-log-images/<group>/vehicles/...
     2.3%   counseling images
     0.9%   everything else, including the actual driver paperwork

So a heartbeat labelled "driver paperwork uploaded", carrying the second-highest
churn weight in the model at 4.5, is overwhelmingly measuring **drivers
photographing vans during the daily vehicle check**. That is a different action, by
a different kind of person, than a manager filing a licence.

Two consequences, and the second is the reason this matters:

  1  The LABEL is wrong on every task a CSM reads.
  2  The signal is probably not independent. Photo-log documents hang off a
     DailyLog, which hangs off the daily roster flow, so this may be largely a
     restatement of the rostering heartbeat (weight 4.3) rather than a second
     piece of evidence. Two correlated signals inside a 3-of-4 rule means an
     account can trip two heartbeats for one underlying behaviour.

This script measures the last upload per SUBTYPE per tenant, so the components can
be weighted separately instead of as one blob.

Subtypes are keyed off which foreign key is set, checked in priority order because a
row can carry more than one:

    documentDailyLogId          daily-log photo, taken during a vehicle check
    documentImageCounselingId   evidence attached to a coaching record
    documentStaffId             FILED AGAINST A PERSON. This is driver paperwork
    documentInfractionId        evidence on an infraction
    documentVehicleId           vehicle document
    documentMaintenanceId       maintenance record
    documentIncidentId/InjuryId incident or injury evidence
    folderPath only             deliberately filed into a folder
    nothing set                 unlinked upload

Usage:  python3 document_breakdown.py [--as-of YYYY-MM-DD] [--days 90]
Writes data/document-breakdown-<as-of>.json
"""
import argparse, datetime as dt, glob, json, os
from concurrent.futures import ThreadPoolExecutor
import lib_hera as H

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "data")

# Priority order matters: a counseling image can also carry a staff id, and we want
# it counted as coaching evidence rather than as filed paperwork.
KINDS = [
    ("daily_log_photo",   "documentDailyLogId"),
    ("counseling_image",  "documentImageCounselingId"),
    ("staff_file",        "documentStaffId"),
    ("infraction_doc",    "documentInfractionId"),
    ("vehicle_doc",       "documentVehicleId"),
    ("maintenance_doc",   "documentMaintenanceId"),
    ("incident_doc",      "documentIncidentId"),
    ("injury_doc",        "documentInjuryId"),
]
PROJ = "uploadDate," + ",".join(fk for _, fk in KINDS) + ",folderPath"

# What a human filing paperwork looks like, as opposed to a byproduct of the daily
# vehicle check. This is the candidate replacement for the "document" heartbeat.
REAL_PAPERWORK = {"staff_file", "vehicle_doc", "maintenance_doc", "foldered", "unlinked"}


def classify(r):
    for name, fk in KINDS:
        if r.get(fk):
            return name
    return "foldered" if r.get("folderPath") else "unlinked"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--as-of", default=dt.date.today().isoformat())
    ap.add_argument("--days", type=int, default=90)
    a = ap.parse_args()
    as_of = dt.date.fromisoformat(a.as_of)
    since = (as_of - dt.timedelta(days=a.days)).isoformat()

    usage = json.load(open(H.newest_dated(DATA, "usage")))
    tenants = usage["tenants"]
    print(f"{len(tenants)} tenants, Document rows since {since}")
    ddb = H.client()

    def work(t):
        counts, newest = {}, {}
        try:
            for r in H.query_all(
                ddb, TableName=H.table("Document"), IndexName="byGroup",
                KeyConditionExpression="#g = :g AND #u >= :s",
                ExpressionAttributeNames={"#g": "group", "#u": "uploadDate"},
                ExpressionAttributeValues={":g": {"S": t["group"]}, ":s": {"S": since}},
                ProjectionExpression=PROJ,
            ):
                k = classify(r)
                d = str(r.get("uploadDate") or "")[:10]
                counts[k] = counts.get(k, 0) + 1
                if d and (k not in newest or d > newest[k]):
                    newest[k] = d
        except Exception as e:                                  # noqa: BLE001
            return t, {}, {}, f"{type(e).__name__}: {e}"
        return t, counts, newest, None

    rows, errors = [], []
    with ThreadPoolExecutor(max_workers=16) as ex:
        for i, (t, counts, newest, err) in enumerate(ex.map(work, tenants), 1):
            if err:
                errors.append((t.get("companyName"), err))
            real = [d for k, d in newest.items() if k in REAL_PAPERWORK]
            rows.append({
                "companyName": t["companyName"], "group": t["group"],
                "counts": counts, "newest": newest,
                # the two competing definitions of the heartbeat
                "last_any_document": max(newest.values()) if newest else None,
                "last_real_paperwork": max(real) if real else None,
            })
            if i % 60 == 0:
                print(f"  {i}/{len(tenants)}")

    out = os.path.join(DATA, f"document-breakdown-{as_of}.json")
    json.dump({"as_of": str(as_of), "days": a.days, "tenants": rows}, open(out, "w"))
    print(f"\nwrote {out}")
    if errors:
        print(f"{len(errors)} errors, first: {errors[0]}")

    total = {}
    for r in rows:
        for k, v in r["counts"].items():
            total[k] = total.get(k, 0) + v
    grand = sum(total.values()) or 1
    print(f"\nCOMPOSITION of the paperwork heartbeat, {grand:,} rows in {a.days} days")
    for k, v in sorted(total.items(), key=lambda x: -x[1]):
        mark = "  <- real paperwork" if k in REAL_PAPERWORK else ""
        print(f"  {k:20s} {v:>9,}  {v/grand*100:5.1f}%{mark}")
    real_share = sum(v for k, v in total.items() if k in REAL_PAPERWORK) / grand * 100
    print(f"\n  actual paperwork is {real_share:.1f}% of the signal by volume")

    # How many tenants would change side if the heartbeat used real paperwork only?
    dark_any = dark_real = flip = 0
    for r in rows:
        def days(d):
            return None if not d else (as_of - dt.date.fromisoformat(d)).days
        a_, b_ = days(r["last_any_document"]), days(r["last_real_paperwork"])
        da = a_ is None or a_ > 30
        dr = b_ is None or b_ > 30
        dark_any += da
        dark_real += dr
        if da != dr:
            flip += 1
    print(f"\nIMPACT at the 30-day threshold, {len(rows)} tenants")
    print(f"  dark on ANY document (today's rule):   {dark_any}")
    print(f"  dark on REAL paperwork only:           {dark_real}")
    print(f"  tenants that change side:              {flip}")


if __name__ == "__main__":
    main()
