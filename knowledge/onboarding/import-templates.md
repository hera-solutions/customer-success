# Customer Onboarding Import Templates

When a new customer is onboarded to Hera, three CSV templates are used to bulk-load their operating data: **Devices**, **Staff**, and **Vehicles**. The canonical copies live in Google Drive at:

`Shared drives/Imports/Templates/`

- `Hera - Devices.csv`
- `Hera - Staff.csv`
- `Hera - Vehicles.csv`

This document captures the column structure, allowed values, and known quirks of each template so the onboarding team and Claude can work from a single source of truth.

---

## Global rules (apply to all three templates)

- **Date format: MM/DD/YYYY.** Every date field across every template must be in `MM/DD/YYYY` format. If the customer file uses a different format (e.g., `YYYY-MM-DD`, `M/D/YY`, Excel serial dates), convert before import.

---

## Devices

Used to import the customer's fleet of cell phones (one row per device).

| Column | Required | Allowed values / format | Notes |
|---|---|---|---|
| Name | Yes | Free text | Internal name for the device (often the assigned driver or unit number). |
| Phone Number | Yes | Phone number | Line assigned to the device. |
| Carrier | Yes | AT&T, Boost, Cricket, Google Fi, H20, Metro by T-Mobile, Spectrum Mobile, Sprint, T-Mobile, US Cellular, Verizon, Xfinity Mobile | Pick from the allowed list. |
| Notes | No | Free text | Anything that doesn't fit elsewhere. |
| Status | Yes | Active, Inactive | |
| IMEI | Yes | Device IMEI | |

---

## Staff

Used to import the customer's driver/associate roster (one row per person).

| Column | Required | Allowed values / format | Notes |
|---|---|---|---|
| Status | Yes | `Active`, `Inactive - Misc` (other inactive variants may exist) | Hera uses `Inactive - Misc` (with hyphen and space) for the generic inactive case — NOT bare `Inactive`. |
| First Name | Yes | | |
| Last Name | Yes | | |
| Hera Display Name | No | | Name shown in the Hera app. Leave blank on import — Hera generates this automatically from First + Last. Only populate if the customer wants a non-default display (nickname, initial-style). |
| Nickname | No | | |
| Transporter ID | Yes for Amazon DSPs | Amazon Transporter ID | |
| Email | Yes | Email address | |
| Phone | Yes | Phone number | |
| Hire Date | Yes | MM/DD/YYYY | |
| Gender | No | | Sensitive PII — only collect if the customer actively uses it. |
| Pronouns | No | | |
| DOB | No | MM/DD/YYYY | Sensitive PII — only collect if the customer actively uses it. |
| Gas Card PIN | No | PIN | Treat as sensitive; do not include in screenshots or share over email. |
| Authorized To Drive | Yes | Yes / No (confirm format) | |
| DL Expiration | Yes for drivers | MM/DD/YYYY | Driver's license expiration. |
| Motor Vehicle Report | No | MM/DD/YYYY or status | MVR pull date or result. |
| Hourly Status | No | | E.g., hourly vs. salary classification. |

**PII note:** Gender, DOB, and Gas Card PIN are sensitive. Confirm the customer actually intends to manage these in Hera before requiring them in the import. If they don't, leave the columns blank rather than collecting data the customer doesn't need.

---

## Vehicles

Used to import the customer's vehicle fleet (one row per vehicle).

| Column | Required | Allowed values / format | Notes |
|---|---|---|---|
| Status | Yes | Active, Inactive, Inactive - Maintenance, Inactive - Grounded | |
| Vehicle Name | No | Free text | Customer's internal label (often a unit number). Missing names are acceptable — but flag every blank row in the pre-import notes so the customer can confirm. |
| License Plate | Yes, **unique** | Plate number | Must be unique across the file. Flag any duplicates before presenting the final import. |
| License Plate Expiration | Yes | MM/DD/YYYY | |
| State | Yes | US state | Plate state. |
| VIN | Yes, **unique** | 17-char VIN | Must be unique across the file. Flag any duplicates before presenting the final import. |
| Gas Card (Last 6) | No | Last 6 digits | |
| Mileage | Yes | Integer | Odometer at import. |
| Parking Space | No | Free text | |
| Start Date | Yes | MM/DD/YYYY | When the vehicle entered the fleet. |
| End Date | No | MM/DD/YYYY | When the vehicle exited the fleet. |
| Ownership | Yes | Lease, Own, Rent | |
| Vehicle Type | Yes | | E.g., Step Van, Cargo Van, Box Truck. Confirm the customer's taxonomy. |
| Description | No | Free text | |
| Make | Yes | | |
| Model | Yes | | |
| Year | Yes | YYYY | |
| Company | If Lease/Rent | Alamo, Avis, Budget, Dollar, Element, Enterprise, Fluid Truck, Hertz, Lease Plan, Merchants Fleet, National, Thrifty, Zeeba | Leasing/rental company. |
| Rent Agreement Number | If Lease/Rent | Free text | |

---

## Known template quirks

- **Vehicles CSV has leading spaces in most headers** (e.g., ` Vehicle Name`, ` License Plate`). Importers that match on exact header strings will miss these columns. Either fix the template or strip whitespace on import.
- **Staff CSV "Status" column has no allowed-values list in the header.** Devices and Vehicles both enumerate their status options inline; Staff does not. Confirm the customer's intended values (e.g., Active / Inactive / On Leave / Terminated) before each import.
- **Devices template assumes US carriers only.** No slot for international carriers or eSIM-only providers.

## Process notes

- Templates should be sent to the customer with example rows filled in for the first 2-3 records so they can pattern-match.
- Before import, spot-check for: VINs that aren't 17 characters, duplicate phone numbers, plates without states, and hire dates in the future.
- Keep the customer's filled-in copy in the customer's onboarding folder, not in the shared template folder.
