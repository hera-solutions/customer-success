"""
Pull the engagement and revenue signals for every paying tenant.

Signals 1 to 3 are the three-signal model specified in the daily review skill
(analysis/logrocket-error-investigation/skill/SKILL.md, Part 4). Signals 4 to 7
were added from the July 2026 baseline
(analysis/cs-health-baseline-2026-07/findings.md).

  1. last_message_sent_by_user   Message, senderId populated. A human typed something.
  2. last_message_read           AuditLog CreateMessageReadStatus. A human read something.
  3. last_scorecard              CompanyScoreCard. Weekly operational discipline.
  4. last_staffed_roster         DailyRoster with at least one route assigned to an associate.
  5. associate_trend             Active-associate count across the last 4 CLOSED invoices.
  6. under_10_run                Consecutive recent days below 10 active associates.
  7. empty_roster_ratio          Rosters opened in the window that contain no routes.

Usage:
    python3 three_signals.py                 # all paying tenants
    python3 three_signals.py --limit 20      # sample
    python3 three_signals.py --as-of 2026-07-29
Writes raw signal data to data/signals-<as-of>.json
"""
import argparse
import datetime as dt
import json
import os
from concurrent.futures import ThreadPoolExecutor

import lib_hera as H

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "data")

# Message types that can carry a human sender. Verified 2026-07-30 by sampling
# 40 tenants over 11 days: userNotification (18,895 rows) and taskReminder and
# billingError carry ZERO senderId values and are correctly excluded. Every type
# below does carry human sends.
#
# An earlier version queried only broadcast, messenger and roster. That missed
# recurring, standUpAnnouncements and coaching, which together held 12,056 human
# sends in that sample, comparable to broadcast alone. 59 of 252 tenants read as
# darker than they were, 14 of them by 7+ days. DBE Logistics read as 1,205 days
# dark while messaging that same day.
ROSTER_SCAN_CAP = 45   # past-dated rosters to examine when finding the last staffed one

# Fleet event types on the Accident table, which despite its name holds all vehicle
# history. Production distribution over a 24,860-row sample: Odometer Reading 22,274,
# Maintenance 2,000, Vehicle Damage 291, Accident 155, Incident 140.
FLEET_USAGE_TYPES = ("Odometer Reading", "Maintenance")
FLEET_INCIDENT_TYPES = ("Accident", "Incident", "Vehicle Damage")

# Retained for reference only: the search below is type-agnostic and does not use
# this list. Kept because it documents which types can carry a human sender.
_HUMAN_MESSAGE_TYPES_REFERENCE = (
    "broadcast",
    "messenger",
    "roster",
    "recurring",
    "standUpAnnouncements",
    "coaching",
    "wireless-support",
)
MESSAGE_LOOKBACK_DAYS = 120  # how far back to look for a human send
MESSAGE_PAGE_CAP = 40        # bound the read; sets message_search_truncated if hit



def signals_for(ddb, tenant, as_of, window_days):
    """All signals for one tenant. Never raises: failures land in ['errors']."""
    group = tenant.get("group")
    out = {
        "id": tenant.get("id"),
        "group": group,
        "companyName": tenant.get("companyName"),
        "customerStatus": tenant.get("customerStatus"),
        "accountPremiumStatus": tenant.get("accountPremiumStatus"),
        "can_roster": H.can_roster(tenant),
        "last_message_sent_by_user": None,
        "last_message_read": None,
        "last_scorecard": None,
        "last_staffed_roster": None,
        "active_staff": None,
        "invoice_series": [],
        "daily_active_staff": {},
        "rosters_in_window": 0,
        "empty_rosters_in_window": 0,
        # UPSIDE ONLY. Nothing in this dict may ever lower a health band. Fleet
        # adoption is 10% for odometer readings and 28% for maintenance among
        # entitled tenants, so 70% use neither. A signal that fires on 70% of the
        # book carries no information about which accounts are at risk: it is a
        # company-level product adoption gap, not 168 individual problems.
        # Revisit making it scored only once a majority are using it, so that
        # absence becomes the exception rather than the rule.
        "upside": {},
        "errors": [],
    }
    if not group:
        out["errors"].append("tenant has no group")
        return out

    window_start = (as_of - dt.timedelta(days=window_days)).isoformat()

    # 1. last human-sent message.
    #
    # Roster and coaching messages are delivered PER ASSOCIATE in bursts, and those
    # per-associate rows carry no senderId. A tenant with 100 associates emits 100+
    # sender-less rows in a single minute, so ANY fixed row limit can be swamped and
    # the human-sent message pushed out of the page. Limit 25 missed real sends on 4
    # tenants; Limit 60 happened to catch them. Neither is principled.
    #
    # So: walk back by TIME, newest first, across all message types, and stop at the
    # first row with a senderId. Bounded by a page cap, and if the cap is hit we say
    # so rather than silently reporting the tenant as dark.
    try:
        found = None
        pages = 0
        truncated = False
        kw = dict(
            TableName=H.table("Message"),
            IndexName="byGroup",
            KeyConditionExpression="#g = :g AND createdAt BETWEEN :a AND :b",
            ExpressionAttributeNames={"#g": "group"},
            ExpressionAttributeValues={
                ":g": {"S": group},
                ":a": {"S": (as_of - dt.timedelta(days=MESSAGE_LOOKBACK_DAYS)).isoformat()},
                ":b": {"S": as_of.isoformat() + "T23:59:59.999Z"},
            },
            ProjectionExpression="createdAt,senderId,messageType",
            ScanIndexForward=False,
        )
        while True:
            resp = ddb.query(**kw)
            pages += 1
            for item in (H.flatten(i) for i in resp["Items"]):
                if item.get("senderId"):
                    found = item.get("createdAt")
                    out["last_message_type"] = item.get("messageType")
                    break
            if found or "LastEvaluatedKey" not in resp:
                break
            if pages >= MESSAGE_PAGE_CAP:
                truncated = True
                break
            kw["ExclusiveStartKey"] = resp["LastEvaluatedKey"]
        out["last_message_sent_by_user"] = found
        out["message_search_truncated"] = truncated
        out["message_pages_read"] = pages
    except Exception as exc:
        out["errors"].append(f"msg:{exc}"[:90])

    # 2. last message read.
    # The GSI range is mutationName, so ScanIndexForward cannot order by date.
    # Paginate fully and take the max, as the daily-review skill prescribes.
    try:
        newest = None
        for item in H.query_all(
            ddb,
            TableName=H.table("AuditLog"),
            IndexName="byTenantIDAndMutationName",
            KeyConditionExpression="tenantID = :t AND mutationName = :m",
            ExpressionAttributeValues={
                ":t": {"S": tenant["id"]},
                ":m": {"S": "CreateMessageReadStatus"},
            },
            ProjectionExpression="createdAt",
        ):
            stamp = item.get("createdAt")
            if stamp and (newest is None or stamp > newest):
                newest = stamp
        out["last_message_read"] = newest
    except Exception as exc:
        out["errors"].append(f"read:{exc}"[:90])

    # 3. last scorecard. yearWeek is null on some rows, so take max(createdAt).
    try:
        rows = ddb.query(
            TableName=H.table("CompanyScoreCard"),
            IndexName="byTenantByYearWeek",
            KeyConditionExpression="tenantId = :t",
            ExpressionAttributeValues={":t": {"S": tenant["id"]}},
            ProjectionExpression="createdAt,yearWeek",
            ScanIndexForward=False,
            Limit=10,
        )["Items"]
        stamps = [H.flatten(i).get("createdAt") for i in rows]
        stamps = [s for s in stamps if s]
        out["last_scorecard"] = max(stamps) if stamps else None
    except Exception as exc:
        out["errors"].append(f"scorecard:{exc}"[:90])

    # 4. last roster that actually contains a staffed route, plus empty-shell count.
    # Only meaningful if the tenant is entitled to rostering.
    if out["can_roster"]:
        try:
            rosters = H.query_all(
                ddb,
                TableName=H.table("DailyRoster"),
                IndexName="byGroupAndNotesDate",
                KeyConditionExpression="#g = :g",
                ExpressionAttributeNames={"#g": "group"},
                ExpressionAttributeValues={":g": {"S": group}},
                ProjectionExpression="id,notesDate",
            )
            dated = []
            for r in rosters:
                parsed = H.roster_date(r.get("notesDate"), as_of)
                if parsed:
                    dated.append((parsed, r["id"]))
            dated.sort(reverse=True)
            # Window is [window_start, as_of]. Future-dated rosters are planning,
            # not work done, and counting them inflated the denominator of the
            # empty-shell ratio.
            out["rosters_in_window"] = sum(
                1 for d, _ in dated if window_start <= d.isoformat() and d <= as_of
            )
            # Planning horizon: rosters dated ahead of today. Kept as context only.
            out["future_rosters"] = sum(1 for d, _ in dated if d > as_of)
            # Only rosters dated today or earlier can tell us whether real work
            # happened. Tenants plan weeks ahead, so their newest rosters by
            # notesDate are future shells with no routes assigned yet. Scanning
            # from the newest without this filter burned the whole cap on empty
            # future rosters: 23 tenants read as having NO staffed roster, and 6
            # of them had actually staffed one within the previous three days.
            past = [(d, rid) for d, rid in dated if d <= as_of]
            for parsed, rid in past[:ROSTER_SCAN_CAP]:
                routes = H.query_all(
                    ddb,
                    TableName=H.table("Route"),
                    IndexName="gsi-RouteDailyRoster",
                    KeyConditionExpression="routeDailyRosterId = :r",
                    ExpressionAttributeValues={":r": {"S": rid}},
                    ProjectionExpression="routeStaffId",
                )
                if parsed.isoformat() >= window_start and not routes:
                    out["empty_rosters_in_window"] += 1
                if any(r.get("routeStaffId") for r in routes):
                    if out["last_staffed_roster"] is None:
                        out["last_staffed_roster"] = parsed.isoformat()
                        # we scan newest-first, so the first hit is the answer;
                        # keep going only while we still owe empty-shell counts
                        if parsed.isoformat() < window_start:
                            break
        except Exception as exc:
            out["errors"].append(f"roster:{exc}"[:90])

    # 5. active associates now. Only status == 'Active' bills.
    try:
        out["active_staff"] = H.query_count(
            ddb,
            TableName=H.table("Staff"),
            IndexName="byGroupStatus",
            KeyConditionExpression="#g = :g AND #s = :s",
            ExpressionAttributeNames={"#g": "group", "#s": "status"},
            ExpressionAttributeValues={":g": {"S": group}, ":s": {"S": "Active"}},
        )
    except Exception as exc:
        out["errors"].append(f"staff:{exc}"[:90])

    # 6 and 7. Invoice history for the revenue axis, plus daily activeStaff.
    # TRAP: status 'Pending' is the in-progress month, still accruing. Comparing
    # it against closed months makes every account look like it is shrinking.
    try:
        invoices = H.query_all(
            ddb,
            TableName=H.table("Invoice"),
            IndexName="byGroup",
            KeyConditionExpression="#g = :g",
            ExpressionAttributeNames={"#g": "group", "#st": "status"},
            ExpressionAttributeValues={":g": {"S": group}},
            ProjectionExpression=(
                "id,createdAt,#st,invoiceTotal,variableTotal,averageActiveDriverCount"
            ),
        )
        closed = sorted(
            (i for i in invoices if i.get("status") and i["status"] != "Pending"),
            key=lambda i: i.get("createdAt") or "",
            reverse=True,
        )
        out["invoice_series"] = [
            {
                "createdAt": i.get("createdAt"),
                "status": i.get("status"),
                "invoiceTotal": i.get("invoiceTotal"),
                "variableTotal": i.get("variableTotal"),
                "associates": i.get("averageActiveDriverCount"),
            }
            for i in closed[:6]
        ]
        # daily activeStaff from line items on the 3 most recent invoices,
        # including the Pending one, since the under-10 rule wants recency
        recent = sorted(
            invoices, key=lambda i: i.get("createdAt") or "", reverse=True
        )[:3]
        for inv in recent:
            for line in H.query_all(
                ddb,
                TableName=H.table("InvoiceLineItem"),
                IndexName="gsi-InvoiceInvoiceLineItems",
                KeyConditionExpression="invoiceLineItemInvoiceId = :i",
                ExpressionAttributeValues={":i": {"S": inv["id"]}},
                ProjectionExpression="#dt,activeStaff",
                ExpressionAttributeNames={"#dt": "date"},
            ):
                day = str(line.get("date") or "")[:10]
                if day and line.get("activeStaff") is not None:
                    out["daily_active_staff"][day] = float(line["activeStaff"])
    except Exception as exc:
        out["errors"].append(f"invoice:{exc}"[:90])

    # ---- UPSIDE SIGNALS. Value-conversation material, never scored.
    up = {}
    premium = tenant.get("accountPremiumStatus") or []
    if isinstance(premium, str):
        premium = [premium]
    up["fleet_entitled"] = ("vehicles" in set(premium)) or ("bundle" in set(premium))
    # Inventory and document signing both live in the Athena (Amplify Gen 2) app and
    # have no table in this DynamoDB account, so USAGE is not measurable here. Only
    # the entitlement flags on Tenant are visible. Paused by decision 2026-07-30.
    # Both inventory flags are `true` on 949 of 954 tenant rows including churned ones,
    # so they are a global default rather than a per-tenant entitlement and carry no
    # information. Captured only so a future reader does not repeat the check. Document
    # signing has no field on Tenant at all.
    up["inventory_enabled"] = bool(tenant.get("featureEnabledInventoryManagement"))
    up["inventory_flag_is_global_default"] = True
    up["inventory_usage"] = None   # not measurable: Athena
    up["doc_signing_usage"] = None  # not measurable: Athena
    if up["fleet_entitled"]:
        since30 = (as_of - dt.timedelta(days=30)).isoformat()
        since90 = (as_of - dt.timedelta(days=90)).isoformat()

        def fleet_count(kind, since):
            return H.query_count(
                ddb,
                TableName=H.table("Accident"),
                IndexName="byGroupByHistoryType",
                KeyConditionExpression="#g = :g AND #sk BETWEEN :a AND :b",
                ExpressionAttributeNames={
                    "#g": "group",
                    "#sk": "vehicleHistoryType#accidentDate",
                },
                ExpressionAttributeValues={
                    ":g": {"S": group},
                    ":a": {"S": kind + "#" + since},
                    ":b": {"S": kind + "#9999"},
                },
            )

        try:
            up["vehicles"] = H.query_count(
                ddb, TableName=H.table("Vehicle"), IndexName="byGroup",
                KeyConditionExpression="#g = :g",
                ExpressionAttributeNames={"#g": "group"},
                ExpressionAttributeValues={":g": {"S": group}},
            )
        except Exception as exc:
            out["errors"].append(f"veh:{exc}"[:80]); up["vehicles"] = None
        try:
            up["odometer_30d"] = fleet_count("Odometer Reading", since30)
            up["maintenance_90d"] = fleet_count("Maintenance", since90)
            up["incidents_90d"] = sum(
                fleet_count(k, since90) for k in FLEET_INCIDENT_TYPES
            )
        except Exception as exc:
            out["errors"].append(f"fleet:{exc}"[:80])
        try:
            # vehicles carrying an odometer reading inside 30 days
            up["vehicles_fresh_odometer"] = H.query_count(
                ddb, TableName=H.table("Vehicle"),
                IndexName="byGroupAndLastOdometerReadingDate",
                KeyConditionExpression="#g = :g AND lastOdometerReadingDate >= :a",
                ExpressionAttributeNames={"#g": "group"},
                ExpressionAttributeValues={":g": {"S": group}, ":a": {"S": since30}},
            )
        except Exception as exc:
            out["errors"].append(f"odofresh:{exc}"[:80]); up["vehicles_fresh_odometer"] = None
        # Reminders have no createdAt index, so a byGroup count is lifetime-ever and
        # reaches back to 2022. That inflates the signal badly: it counts a reminder
        # somebody completed three years ago as current usage. Count OPEN (Pending)
        # reminders instead, which means maintenance tracking is live right now.
        try:
            up["reminders_open"] = H.query_count(
                ddb, TableName=H.table("VehicleMaintenanceReminder"),
                IndexName="byGroupByStatus",
                KeyConditionExpression="#g = :g AND begins_with(#sk, :p)",
                ExpressionAttributeNames={"#g": "group", "#sk": "status#dueBySort"},
                ExpressionAttributeValues={":g": {"S": group}, ":p": {"S": "Pending#"}},
            )
        except Exception as exc:
            out["errors"].append(f"rem:{exc}"[:80]); up["reminders_open"] = None
        try:
            up["reminders_lifetime"] = H.query_count(
                ddb, TableName=H.table("VehicleMaintenanceReminder"), IndexName="byGroup",
                KeyConditionExpression="#g = :g",
                ExpressionAttributeNames={"#g": "group"},
                ExpressionAttributeValues={":g": {"S": group}},
            )
        except Exception as exc:
            up["reminders_lifetime"] = None
    out["upside"] = up
    return out


def bulk_cleanup(ddb, group, as_of, lookback_days=240):
    """
    Detect a roster cleanup: many Active -> Inactive transitions on one day.

    A customer who lets the roster go stale and then tidies it produces a single
    day holding most of the transitions. Genuine attrition spreads out. Without
    this check, 13 of 30 declining accounts read as churn risk when they had
    simply corrected their data.

    TRAP: the fields are currentStatus and previousStatus. There is no 'status'
    field on StaffStatus. Projecting 'status' returns nothing and looks like
    "no transitions exist".
    """
    since = (as_of - dt.timedelta(days=lookback_days)).isoformat()
    by_day = {}
    try:
        for row in H.query_all(
            ddb,
            TableName=H.table("StaffStatus"),
            IndexName="byGroup",
            KeyConditionExpression="#g = :g AND #d >= :since",
            ExpressionAttributeNames={"#g": "group", "#d": "date"},
            ExpressionAttributeValues={":g": {"S": group}, ":since": {"S": since}},
            ProjectionExpression="#d,currentStatus,previousStatus",
        ):
            if row.get("previousStatus") != "Active":
                continue
            if not str(row.get("currentStatus") or "").startswith("Inactive"):
                continue
            day = str(row.get("date") or "")[:10]
            by_day[day] = by_day.get(day, 0) + 1
    except Exception:
        return None
    if not by_day:
        return {"total": 0, "peak_day": None, "peak_count": 0, "concentration": 0.0}
    peak_day, peak_count = max(by_day.items(), key=lambda kv: kv[1])
    total = sum(by_day.values())
    return {
        "total": total,
        "peak_day": peak_day,
        "peak_count": peak_count,
        "concentration": peak_count / total,
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--as-of", default=None, help="YYYY-MM-DD, defaults to today")
    ap.add_argument("--window", type=int, default=30, help="engagement window in days")
    ap.add_argument("--limit", type=int, default=0, help="sample N tenants")
    ap.add_argument("--workers", type=int, default=12)
    args = ap.parse_args()

    as_of = (
        dt.date.fromisoformat(args.as_of) if args.as_of else dt.date.today()
    )
    ddb = H.client()
    os.makedirs(DATA, exist_ok=True)

    tenants = H.scan_all(
        ddb,
        TableName=H.table("Tenant"),
        ProjectionExpression=(
            "id,#g,companyName,customerStatus,accountPremiumStatus,"
            "isTestingAccount,isTemporaryAccount,totalNumberOfMonthsPaidByTenant,"
            "featureEnabledInventoryManagement,featureAccessInventoryManagement"
        ),
        ExpressionAttributeNames={"#g": "group"},
    )
    scope = [t for t in tenants if H.is_real_tenant(t) and H.is_paying(t)]
    if args.limit:
        scope = scope[: args.limit]
    print(f"{len(tenants)} tenant rows, {len(scope)} paying and in scope, as of {as_of}")

    def work(t):
        return signals_for(ddb, t, as_of, args.window)

    with ThreadPoolExecutor(args.workers) as pool:
        results = list(pool.map(work, scope))

    # cleanup detection only where the revenue trend is falling: cheaper and it
    # is the only place the answer changes a decision
    def trend(row):
        series = [s["associates"] for s in row["invoice_series"] if s["associates"]]
        if len(series) < 2 or not series[-1]:
            return None
        return (series[0] - series[-1]) / series[-1]

    declining = [r for r in results if (trend(r) or 0) < -0.05]
    print(f"checking {len(declining)} declining tenants for roster cleanups")
    with ThreadPoolExecutor(args.workers) as pool:
        cleanups = list(
            pool.map(lambda r: bulk_cleanup(ddb, r["group"], as_of), declining)
        )
    for row, info in zip(declining, cleanups):
        row["cleanup"] = info

    path = os.path.join(DATA, f"signals-{as_of}.json")
    with open(path, "w") as fh:
        json.dump({"as_of": as_of.isoformat(), "window": args.window, "tenants": results}, fh)
    failed = sum(1 for r in results if r["errors"])
    print(f"wrote {path}  ({len(results)} tenants, {failed} with errors)")
    if failed:
        for r in results:
            if r["errors"]:
                print(f"  {r['companyName']}: {r['errors'][0]}")
                break


if __name__ == "__main__":
    main()
