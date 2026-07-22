#!/usr/bin/env python3
"""Clean the Music City Supply Chain onboarding files (already in Hera template
shape) into import-ready Staff and Vehicles CSVs, and print pre-import flags.

Scope of cleanup (data only; header lines preserved verbatim so the Hera importer
still matches its columns):
  - Excel serial dates -> MM/DD/YYYY (Hired Date, DOB, DL Expiration)
  - garbage dates (0, 00/01/1900) -> blank
  - phone -> last 10 digits, 0/blank -> blank
  - names -> trim + collapse internal whitespace
  - Authorized to Drive -> trim, drop trailing ';'
  - Vehicle Type / Company -> trim; Company case-normalized to allowed list
Flags are printed, not silently applied, for anything needing a human decision.
"""
import csv, io, re
from datetime import datetime, timedelta

SRC = "/private/tmp/claude-501/-Users-johnjm-github-customer-success/38c32ec0-1741-4385-bff8-b0a7eb2131ec/scratchpad/"
OUT = SRC  # write cleaned files next to sources; we copy into the repo afterward

EXCEL_EPOCH = datetime(1899, 12, 30)

def norm_ws(s):
    return re.sub(r"\s+", " ", (s or "").strip())

def conv_date(raw):
    """Return (value, note). value is MM/DD/YYYY or '' ; note flags what happened."""
    v = (raw or "").strip()
    if v == "":
        return "", None
    if v.isdigit():
        n = int(v)
        if n <= 0:
            return "", "garbage"      # bare 0
        if 1 < n < 60000:
            d = EXCEL_EPOCH + timedelta(days=n)
            return d.strftime("%m/%d/%Y"), "serial"
        return "", "garbage"
    # looks like a date string
    m = re.match(r"^(\d{1,2})/(\d{1,2})/(\d{2,4})$", v)
    if m:
        mo, day, yr = int(m.group(1)), int(m.group(2)), int(m.group(3))
        if mo == 0 or day == 0 or yr <= 1900:
            return "", "garbage"      # 00/01/1900 etc.
        if yr < 100:
            yr += 2000
        try:
            d = datetime(yr, mo, day)
        except ValueError:
            return v, "unparsed"
        return d.strftime("%m/%d/%Y"), None
    return v, "unparsed"

def phone10(raw):
    d = re.sub(r"\D", "", raw or "")
    if d in ("", "0"):
        return ""
    return d[-10:] if len(d) >= 10 else d

# ----------------------------------------------------------------------------- STAFF
with open(SRC + "staff_raw.csv", newline="", encoding="utf-8") as f:
    rows = list(csv.reader(f))
sheader, sdata = rows[0], rows[1:]

flags = {k: [] for k in
         ["serial","garbage","missing_tid","dup_tid","dup_person","no_phone",
          "no_email","active_no_auth","active_no_dl","under18","phone_note"]}

seen_tid, seen_person = {}, {}
clean_staff = []
for r in sdata:
    if not any(c.strip() for c in r):
        continue
    r = (r + [""]*14)[:14]
    (status, first, last, tid, email, phone, hired, gender,
     pronouns, dob, auth, dlexp, mvr, hourly) = r
    first, last = norm_ws(first), norm_ws(last)
    name = f"{first} {last}".strip()
    tid = tid.strip()
    email = email.strip()
    ph = phone10(phone)
    if ph == "" and phone.strip() not in ("", "0"):
        flags["phone_note"].append(f"{name}: raw phone '{phone.strip()}'")
    hired_v, hn = conv_date(hired)
    dob_v, dn = conv_date(dob)
    dl_v, dln = conv_date(dlexp)
    for col, note in (("Hired Date", hn), ("DOB", dn), ("DL Expiration", dln)):
        if note == "serial":
            flags["serial"].append(f"{name} [{col}]")
        elif note in ("garbage", "unparsed"):
            flags["garbage"].append(f"{name} [{col}]='{(hired if col=='Hired Date' else dob if col=='DOB' else dlexp).strip()}'")
    auth = norm_ws(auth).rstrip(";").strip()
    auth = norm_ws(auth.replace(" ;", ";"))

    if not tid:
        flags["missing_tid"].append(f"{name} ({email or 'no email'})")
    else:
        seen_tid.setdefault(tid, []).append(name)
    seen_person.setdefault(name.lower(), []).append(tid or "(no TID)")
    if not ph:
        flags["no_phone"].append(name)
    if not email:
        flags["no_email"].append(name)
    active = status.strip().lower() == "active"
    if active and not auth:
        flags["active_no_auth"].append(name)
    if active and not dl_v:
        flags["active_no_dl"].append(name)
    if hired_v and dob_v:
        try:
            hd = datetime.strptime(hired_v, "%m/%d/%Y")
            bd = datetime.strptime(dob_v, "%m/%d/%Y")
            age = (hd - bd).days / 365.25
            if age < 18:
                flags["under18"].append(f"{name} (age {age:.1f} at hire)")
        except ValueError:
            pass

    clean_staff.append([status.strip(), first, last, tid, email, ph, hired_v,
                        gender.strip(), pronouns.strip(), dob_v, auth, dl_v,
                        mvr.strip(), hourly.strip()])

for tid, names in seen_tid.items():
    if len(names) > 1:
        flags["dup_tid"].append(f"{tid}: {', '.join(names)}")
for person, tids in seen_person.items():
    if len(tids) > 1:
        flags["dup_person"].append(f"{person} -> {len(tids)} rows ({', '.join(tids)})")

with open(OUT + "Music City Supply Chain - Staff.csv", "w", newline="", encoding="utf-8") as f:
    w = csv.writer(f)
    w.writerow(sheader)
    w.writerows(clean_staff)

# ----------------------------------------------------------------------------- VEHICLES
ALLOWED_CO = {"alamo":"Alamo","avis":"Avis","budget":"Budget","dollar":"Dollar",
              "element":"Element","enterprise":"Enterprise","fluid truck":"Fluid Truck",
              "hertz":"Hertz","lease plan":"Lease Plan","merchants fleet":"Merchants Fleet",
              "national":"National","thrifty":"Thrifty","zeeba":"Zeeba"}
with open(SRC + "vehicles_raw.csv", newline="", encoding="utf-8") as f:
    vrows = list(csv.reader(f))
vheader, vdata = vrows[0], vrows[1:]

vflags = {k: [] for k in
          ["bad_company","no_mileage","no_plate_exp","dup_vin","bad_vin","dup_plate"]}
seen_vin, seen_plate = {}, {}
clean_veh = []
for r in vdata:
    if not any(c.strip() for c in r):
        continue
    r = (r + [""]*19)[:19]
    (status, vname, plate, plexp, state, vin, gas, miles, park, start, end,
     own, vtype, desc, make, model, year, company, rent) = r
    vname = norm_ws(vname); plate = plate.strip().upper(); vin = vin.strip().upper()
    vtype = norm_ws(vtype)
    co = company.strip()
    if co:
        key = co.lower()
        if key in ALLOWED_CO:
            co = ALLOWED_CO[key]
        else:
            vflags["bad_company"].append(f"{vname}: '{company.strip()}'")
    if not miles.strip():
        vflags["no_mileage"].append(vname)
    if own.strip().lower() in ("lease","rent") and not plexp.strip():
        vflags["no_plate_exp"].append(f"{vname} ({own.strip()})")
    if vin:
        if len(vin) != 17:
            vflags["bad_vin"].append(f"{vname}: '{vin}' ({len(vin)} chars)")
        seen_vin.setdefault(vin, []).append(vname)
    if plate:
        seen_plate.setdefault(plate, []).append(vname)
    clean_veh.append([status.strip(), vname, plate, plexp.strip(), state.strip(),
                     vin, gas.strip(), miles.strip(), park.strip(), start.strip(),
                     end.strip(), own.strip(), vtype, desc.strip(), make.strip(),
                     model.strip(), year.strip(), co, rent.strip()])
for vin, names in seen_vin.items():
    if len(names) > 1:
        vflags["dup_vin"].append(f"{vin}: {', '.join(names)}")
for plate, names in seen_plate.items():
    if len(names) > 1:
        vflags["dup_plate"].append(f"{plate}: {', '.join(names)}")

with open(OUT + "Music City Supply Chain - Vehicles.csv", "w", newline="", encoding="utf-8") as f:
    w = csv.writer(f)
    w.writerow(vheader)
    w.writerows(clean_veh)

# ----------------------------------------------------------------------------- REPORT
def section(title, items, cap=None):
    print(f"\n## {title} ({len(items)})")
    show = items if cap is None else items[:cap]
    for it in show:
        print("  -", it)
    if cap and len(items) > cap:
        print(f"  ... and {len(items)-cap} more")

print("="*70)
print(f"STAFF: {len(clean_staff)} rows written (from {len(sdata)} source rows)")
active_ct = sum(1 for r in clean_staff if r[0].lower()=="active")
print(f"  Active: {active_ct}   Inactive: {len(clean_staff)-active_ct}")
section("Serial dates converted", flags["serial"], 8)
section("Garbage dates blanked", flags["garbage"])
section("Missing Transporter ID (required)", flags["missing_tid"])
section("Duplicate Transporter IDs", flags["dup_tid"])
section("Same person, multiple rows/TIDs", flags["dup_person"])
section("Active with NO Authorized-to-Drive", flags["active_no_auth"])
section("Active with NO DL Expiration", flags["active_no_dl"])
section("Blank phone", flags["no_phone"], 12)
section("Blank email", flags["no_email"])
section("DOB implies age <18 at hire", flags["under18"])
print("\n" + "="*70)
print(f"VEHICLES: {len(clean_veh)} rows written (from {len(vdata)} source rows)")
vact = sum(1 for r in clean_veh if r[0].lower()=="active")
print(f"  Active: {vact}   Inactive/Grounded: {len(clean_veh)-vact}")
section("Company not in allowed list", vflags["bad_company"])
section("Blank mileage (required)", vflags["no_mileage"], 100)
section("Lease/Rent with blank plate expiration", vflags["no_plate_exp"], 100)
section("Bad VIN (not 17 chars)", vflags["bad_vin"])
section("Duplicate VINs", vflags["dup_vin"])
section("Duplicate plates", vflags["dup_plate"])
