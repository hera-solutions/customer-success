#!/usr/bin/env python3
"""
Pull Giddy Up Logistics checklist response data from DynamoDB.
Joins RosterChecklist, RosterChecklistItem, RosterChecklistSubject,
and RosterChecklistSubjectItem tables, resolves staff names and
checklist item questions, and writes a flat CSV.
"""

import boto3
import csv
import json
import sys
from collections import defaultdict

PROFILE = "hera-readonly"
REGION = "us-east-2"
SUFFIX = "-zeobggbnyva4padyiddojnmnqy-production"
GIDD_GROUP = "5c99f2ef-2eba-4253-b07a-092b55d9c37c"
GIDD_TENANT = "7954de93-80c5-44b4-961d-b72a12813a90"

session = boto3.Session(profile_name=PROFILE, region_name=REGION)
ddb = session.resource("dynamodb")


def query_all(table_name, index_name, key_expr, expr_names, expr_values, filter_expr=None):
    table = ddb.Table(table_name + SUFFIX)
    kwargs = {
        "IndexName": index_name,
        "KeyConditionExpression": key_expr,
        "ExpressionAttributeValues": expr_values,
    }
    if expr_names:
        kwargs["ExpressionAttributeNames"] = expr_names
    if filter_expr:
        kwargs["FilterExpression"] = filter_expr
    items = []
    while True:
        resp = table.query(**kwargs)
        items.extend(resp["Items"])
        if "LastEvaluatedKey" not in resp:
            break
        kwargs["ExclusiveStartKey"] = resp["LastEvaluatedKey"]
    return items


def get_item(table_name, key):
    table = ddb.Table(table_name + SUFFIX)
    resp = table.get_item(Key=key)
    return resp.get("Item")


def batch_get(table_name, keys, key_name="id"):
    table_full = table_name + SUFFIX
    results = {}
    key_batches = [keys[i:i+100] for i in range(0, len(keys), 100)]
    for batch in key_batches:
        resp = ddb.batch_get_item(
            RequestItems={
                table_full: {
                    "Keys": [{key_name: k} for k in batch]
                }
            }
        )
        for item in resp.get("Responses", {}).get(table_full, []):
            results[item[key_name]] = item
        unprocessed = resp.get("UnprocessedKeys", {}).get(table_full)
        if unprocessed:
            print(f"  Warning: {len(unprocessed['Keys'])} unprocessed keys", file=sys.stderr)
    return results


print("1. Fetching GIDD checklists...", file=sys.stderr)
checklists = query_all(
    "RosterChecklist", "byGroup",
    "#g = :gid", {"#g": "group"}, {":gid": GIDD_GROUP}
)
checklist_map = {c["id"]: c for c in checklists}
print(f"   Found {len(checklists)} checklists", file=sys.stderr)
for c in checklists:
    status = c.get("status", "?")
    print(f"   - {c['name']} ({status}, {c.get('totalSimpleItems',0)} items)", file=sys.stderr)

print("\n2. Fetching checklist items for all checklists...", file=sys.stderr)
item_map = {}
for cid in checklist_map:
    items = query_all(
        "RosterChecklistItem", "byRosterChecklist",
        "rosterChecklistId = :cid", {}, {":cid": cid}
    )
    for item in items:
        item_map[item["id"]] = item
print(f"   Found {len(item_map)} checklist items total", file=sys.stderr)

print("\n3. Fetching all checklist subjects (DA assignments)...", file=sys.stderr)
subjects = query_all(
    "RosterChecklistSubject", "byGroup",
    "#g = :gid", {"#g": "group"}, {":gid": GIDD_GROUP}
)
print(f"   Found {len(subjects)} subject records", file=sys.stderr)

staff_ids = list(set(s["staffId"] for s in subjects))
print(f"   {len(staff_ids)} unique staff members", file=sys.stderr)

print("\n4. Fetching staff names...", file=sys.stderr)
staff_map = batch_get("Staff", staff_ids)
print(f"   Resolved {len(staff_map)} staff names", file=sys.stderr)

print("\n5. Fetching all subject item responses...", file=sys.stderr)
subject_items_by_subject = defaultdict(list)
total_responses = 0
for i, subj in enumerate(subjects):
    if i % 50 == 0:
        print(f"   Processing subject {i+1}/{len(subjects)}...", file=sys.stderr)
    items = query_all(
        "RosterChecklistSubjectItem", "byRosterChecklistSubject",
        "rosterChecklistSubjectId = :sid", {}, {":sid": subj["id"]}
    )
    subject_items_by_subject[subj["id"]] = items
    total_responses += len(items)
print(f"   Found {total_responses} total item responses", file=sys.stderr)

print("\n6. Building flat CSV...", file=sys.stderr)

all_checklist_items_by_checklist = defaultdict(list)
for item_id, item in item_map.items():
    cid = item["rosterChecklistId"]
    all_checklist_items_by_checklist[cid].append(item)
for cid in all_checklist_items_by_checklist:
    all_checklist_items_by_checklist[cid].sort(key=lambda x: int(x.get("order", 0)))

active_checklist_ids = sorted(
    [c["id"] for c in checklists],
    key=lambda cid: checklist_map[cid].get("name", "")
)

headers = [
    "Date", "Associate Name", "Transporter ID", "Staff ID",
    "Checklist Name", "Checklist Status", "Items Completed", "Items Incomplete",
    "Vehicle Items Completed", "Vehicle Items Incomplete", "Submitted At"
]

all_item_columns = []
for cid in active_checklist_ids:
    cl_name = checklist_map[cid]["name"].strip()
    for item in all_checklist_items_by_checklist.get(cid, []):
        col_name = f"{cl_name} | {item.get('titleQuestion', '?')[:80]}"
        all_item_columns.append((cid, item["id"], col_name, item.get("status", "?")))

headers.extend([col for _, _, col, _ in all_item_columns])

output_file = "analysis/gidd-checklist-export/gidd-checklist-responses-raw.csv"
rows = []
for subj in sorted(subjects, key=lambda s: (s.get("notesDate", ""), s.get("staffId", ""))):
    staff = staff_map.get(subj["staffId"], {})
    first = staff.get("firstName", "?")
    last = staff.get("lastName", "?")
    tid = staff.get("transporterId", "?")
    cl = checklist_map.get(subj["rosterChecklistId"], {})

    response_map = {}
    for si in subject_items_by_subject.get(subj["id"], []):
        response_map[si["rosterChecklistItemId"]] = si.get("value", "")

    submitted_at = ""
    for si in subject_items_by_subject.get(subj["id"], []):
        ts = si.get("updatedAt", "")
        if ts > submitted_at:
            submitted_at = ts

    row = {
        "Date": subj.get("notesDate", ""),
        "Associate Name": f"{first} {last}",
        "Transporter ID": tid,
        "Staff ID": subj["staffId"],
        "Checklist Name": cl.get("name", "?").strip(),
        "Checklist Status": cl.get("status", "?"),
        "Items Completed": str(subj.get("simpleItemsCompleted", 0)),
        "Items Incomplete": str(subj.get("simpleItemsIncomplete", 0)),
        "Vehicle Items Completed": str(subj.get("vehicleItemsCompleted", 0)),
        "Vehicle Items Incomplete": str(subj.get("vehicleItemsIncomplete", 0)),
        "Submitted At": submitted_at,
    }

    for cid, item_id, col_name, _ in all_item_columns:
        if cid == subj["rosterChecklistId"]:
            row[col_name] = response_map.get(item_id, "")
        else:
            row[col_name] = ""

    rows.append(row)

with open(output_file, "w", newline="") as f:
    writer = csv.DictWriter(f, fieldnames=headers)
    writer.writeheader()
    writer.writerows(rows)

print(f"\nDone. Wrote {len(rows)} rows to {output_file}", file=sys.stderr)
print(f"Columns: {len(headers)}", file=sys.stderr)

dates = sorted(set(r["Date"] for r in rows))
if dates:
    print(f"Date range: {dates[0]} to {dates[-1]}", file=sys.stderr)
names = sorted(set(r["Associate Name"] for r in rows))
print(f"Associates: {len(names)}", file=sys.stderr)
for n in names:
    count = sum(1 for r in rows if r["Associate Name"] == n)
    print(f"  {n}: {count} entries", file=sys.stderr)
