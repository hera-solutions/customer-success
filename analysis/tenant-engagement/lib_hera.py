"""
Shared helpers for Hera CS scoring against production DynamoDB.

Read-only. Every function here assumes the `hera-readonly` SSO profile.

This module exists to centralise the field traps documented in
analysis/cs-health-baseline-2026-07/findings.md section 13. Each one produced a
confidently wrong answer at least once. Do not bypass them.
"""
import datetime as dt
import sys

import boto3

REGION = "us-east-2"
PROFILE = "hera-readonly"
SUFFIX = "-zeobggbnyva4padyiddojnmnqy-production"

# $9.00 per Active Associate per month, $0.30/day, billed one month in arrears.
# Source: knowledge/billing-overview.md
RATE_PER_ASSOCIATE_MONTH = 9.00

# customerStatus values that mean "currently paying us"
PAYING = {"Active - Bundle", "Active - Premium"}

# accountCanceledReason values that are NOT a CS failure: the customer's
# business ended or contracted. Excluded from addressable retention.
NON_ADDRESSABLE_CHURN = {
    "DSP Closed",
    "Reduced Route Count",
    "Secondary Site Closure",
    "Dropped Associates to 0",
}

# Not customers. Exclude from every book, trial and revenue figure.
INTERNAL_ACCOUNTS = {"Hera Deliveries", "AI Testing"}


def client():
    """Read-only DynamoDB client. Exits with the login hint if SSO has expired."""
    session = boto3.Session(profile_name=PROFILE, region_name=REGION)
    ddb = session.client("dynamodb")
    try:
        session.client("sts").get_caller_identity()
    except Exception as exc:
        if "sso" in str(exc).lower() or "token" in str(exc).lower():
            sys.exit(f"SSO session expired. Run:\n\n    aws sso login --profile {PROFILE}\n")
        raise
    return ddb


def table(name):
    return name + SUFFIX


def unwrap(value):
    """Deserialise one DynamoDB attribute value."""
    kind = next(iter(value))
    if kind == "S":
        return value[kind]
    if kind == "N":
        return float(value[kind])
    if kind == "BOOL":
        return value[kind]
    if kind == "NULL":
        return None
    if kind == "L":
        return [unwrap(v) for v in value[kind]]
    if kind == "M":
        return {k: unwrap(v) for k, v in value[kind].items()}
    return value[kind]


def flatten(item):
    """Deserialise a whole DynamoDB item."""
    return {k: unwrap(v) for k, v in item.items()}


def query_all(ddb, **kwargs):
    """Query with full pagination. Returns flattened items."""
    out = []
    while True:
        resp = ddb.query(**kwargs)
        out.extend(flatten(i) for i in resp["Items"])
        if "LastEvaluatedKey" not in resp:
            return out
        kwargs["ExclusiveStartKey"] = resp["LastEvaluatedKey"]


def query_count(ddb, **kwargs):
    """Query with Select=COUNT and full pagination. Returns an int."""
    kwargs["Select"] = "COUNT"
    total = 0
    while True:
        resp = ddb.query(**kwargs)
        total += resp["Count"]
        if "LastEvaluatedKey" not in resp:
            return total
        kwargs["ExclusiveStartKey"] = resp["LastEvaluatedKey"]


def scan_all(ddb, **kwargs):
    """Scan with full pagination. Returns flattened items."""
    out = []
    while True:
        resp = ddb.scan(**kwargs)
        out.extend(flatten(i) for i in resp["Items"])
        if "LastEvaluatedKey" not in resp:
            return out
        kwargs["ExclusiveStartKey"] = resp["LastEvaluatedKey"]


# ---------------------------------------------------------------- field traps

def parse_ts(value):
    """
    Parse an ISO timestamp defensively.

    TRAP: User.lastLogin can hold the literal string NOT_YET_LOGGED, which sorts
    ABOVE real ISO timestamps because 'N' > '2'. Any max() over raw lastLogin
    values returns garbage. This returns None for anything unparseable.
    """
    if not value or not str(value).startswith("20"):
        return None
    try:
        return dt.datetime.fromisoformat(str(value).replace("Z", "+00:00")).date()
    except (ValueError, TypeError):
        try:
            return dt.datetime.strptime(str(value)[:10], "%Y-%m-%d").date()
        except (ValueError, TypeError):
            return None


def roster_date(value, as_of):
    """
    Parse DailyRoster.notesDate, rejecting corrupt values.

    TRAP 1: notesDate is the date a roster is built FOR, scheduled in advance,
    not a creation timestamp. A healthy account's most recent notesDate is in
    the FUTURE. Never compute "days since".
    TRAP 2: a handful of tenants carry values thousands of years out of range.
    """
    parsed = parse_ts(value)
    if parsed is None:
        return None
    delta = (parsed - as_of).days
    if not -2000 < delta < 400:
        return None
    return parsed


def is_paying(tenant):
    """
    True if the tenant is currently paying.

    TRAP: firstChurnedDateTime is missing on 267 of 497 churned tenants, and
    firstConvertedToPaidDateTime is sparse. customerStatus is the reliable field.
    """
    return str(tenant.get("customerStatus", "")) in PAYING


def ever_paid(tenant):
    """TRAP: use months-paid, not firstConvertedToPaidDateTime, which is sparse."""
    try:
        return float(tenant.get("totalNumberOfMonthsPaidByTenant") or 0) > 0
    except (TypeError, ValueError):
        return False


def is_real_tenant(tenant):
    """Excludes test, temporary and internal accounts."""
    if tenant.get("isTestingAccount") or tenant.get("isTemporaryAccount"):
        return False
    return tenant.get("companyName") not in INTERNAL_ACCOUNTS


def can_roster(tenant):
    """
    True if the tenant is entitled to the rostering feature.

    TRAP: tenants on legacy module pricing without the rostering module
    physically cannot build rosters. Flagging them for "not rostering" produced
    6 false positives. Check entitlement before judging rostering behaviour.
    """
    premium = tenant.get("accountPremiumStatus") or []
    if isinstance(premium, str):
        premium = [premium]
    premium = set(premium)
    return "bundle" in premium or "rostering" in premium


def base_customer_name(name):
    """
    Strip the Amazon station-code suffix so secondary sites roll up to one
    customer. 7 customers appear as 14 tenants; parentAccountId never links
    them, so name matching is the only route.
    """
    import re

    name = re.sub(r"\s*\|\s*[A-Z0-9]{3,6}\s*$", "", str(name))
    name = re.sub(r"\s*-\s*[A-Z]{3,6}\d?\s*$", "", name)
    name = re.sub(r"\s*(LLC|Inc\.?|LLC\.|L\.L\.C\.)\s*$", "", name, flags=re.I)
    return name.strip().lower()


def days_since(date_value, as_of):
    """Days elapsed, or None."""
    return None if date_value is None else (as_of - date_value).days
