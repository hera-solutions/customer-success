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

# Message types that represent a human typing. userNotification is system-generated.
HUMAN_MESSAGE_TYPES = ("broadcast", "messenger", "roster")


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
        "errors": [],
    }
    if not group:
        out["errors"].append("tenant has no group")
        return out

    window_start = (as_of - dt.timedelta(days=window_days)).isoformat()

    # 1. last human-sent message.
    # The GSI range is messageType#createdAt, so a begins_with prefix on the
    # message type lets ScanIndexForward=False sort by date within that type.
    # Querying the hash alone does NOT order by date.
    newest = None
    for mtype in HUMAN_MESSAGE_TYPES:
        try:
            rows = ddb.query(
                TableName=H.table("Message"),
                IndexName="byGroupAndMessageType",
                KeyConditionExpression="#g = :g AND begins_with(#sk, :p)",
                ExpressionAttributeNames={"#g": "group", "#sk": "messageType#createdAt"},
                ExpressionAttributeValues={":g": {"S": group}, ":p": {"S": mtype + "#"}},
                ProjectionExpression="createdAt,senderId",
                ScanIndexForward=False,
                Limit=10,
            )["Items"]
            for item in (H.flatten(i) for i in rows):
                if not item.get("senderId"):
                    continue
                stamp = item.get("createdAt")
                if stamp and (newest is None or stamp > newest):
                    newest = stamp
        except Exception as exc:
            out["errors"].append(f"msg:{mtype}:{exc}"[:90])
    out["last_message_sent_by_user"] = newest

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
            out["rosters_in_window"] = sum(
                1 for d, _ in dated if d.isoformat() >= window_start
            )
            for parsed, rid in dated[:14]:
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
                    if out["rosters_in_window"] == 0:
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
            "isTestingAccount,isTemporaryAccount,totalNumberOfMonthsPaidByTenant"
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
