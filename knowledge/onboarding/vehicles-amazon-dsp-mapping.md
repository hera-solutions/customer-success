# Amazon DSP Vehicle Export → Hera Vehicles Import Mapping

Reusable spec for converting an Amazon-generated DSP vehicle export (typical filename: `VehiclesData (N).xlsx`) into the Hera Vehicles import template.

The Amazon export structure is consistent across DSPs, so this mapping should apply to every new customer onboarding from Amazon. Update this file only if Amazon changes their export schema or Hera changes the import template.

Related docs:
- [import-templates.md](import-templates.md) — canonical Hera template definitions and global rules.

---

## Source file shape

- Single sheet, 28 columns. First row is the header.
- One row per vehicle.
- All dates arrive as `YYYY-MM-DD` strings.
- Many rows have blanks in `serviceType`, `vehicleName`, and `registrationExpiryDate` (rentals usually have no registration expiry).

## Column mapping

| Amazon column | Hera column | Transform |
|---|---|---|
| `vin` | VIN | direct |
| `vehicleName` | Vehicle Name | direct (blanks allowed; flag in pre-import notes) |
| `licensePlateNumber` | License Plate | direct |
| `make` | Make | direct |
| `model` | Model | direct |
| `year` | Year | direct |
| `ownershipStartDate` | Start Date | `YYYY-MM-DD` → `MM/DD/YYYY` |
| `ownershipEndDate` | End Date | `YYYY-MM-DD` → `MM/DD/YYYY` |
| `registrationExpiryDate` | License Plate Expiration | `YYYY-MM-DD` → `MM/DD/YYYY` (blanks allowed) |
| `registeredState` | State | extract 2-letter code (`VA - Virginia` → `VA`) |
| `status` + `operationalStatus` | Status | see Status rules below |
| `ownershipType` | Ownership | see Ownership rules below |
| `serviceType` (fallback: `serviceTier`) | Vehicle Type | see Vehicle Type rules below |
| `vehicleProvider` | Company | see Company rules below |

### Hera columns left blank (Amazon export has no source)

- Gas Card (Last 6)
- Mileage
- Parking Space
- Description
- Rent Agreement Number

If the customer wants these tracked in Hera, request them separately before import.

### Amazon columns that are dropped

- `subModel`, `statusPriority`, `statusReasonCode`, `statusReasonMessage`, `statusSearchValue`, `subcontractorName`, `vehicleRegistrationType`, `type` (use `ownershipType` instead), `pmStats`, `serviceTier` (only used as Vehicle Type fallback), `stationCode`, `payload`, `cubicCapacity`

## Mapping rules

### Status

| Amazon `status` | Amazon `operationalStatus` | Hera Status |
|---|---|---|
| `ACTIVE` | `OPERATIONAL` | Active |
| `ACTIVE` | `READY_FOR_AUDIT` | Active |
| `ACTIVE` | `GROUNDED` | Inactive - Grounded |
| `INACTIVE` | (any) | Inactive |

`READY_FOR_AUDIT` is a paperwork state — the vehicle is still operational. No Amazon source maps to `Inactive - Maintenance` — leave that status unused for Amazon imports.

### Ownership

| Amazon `ownershipType` | Hera Ownership |
|---|---|
| `RENTAL` | Rent |
| `AMAZON_OWNED` | Lease |
| `AMAZON_RENTAL` | Lease |
| `LEASE` | Lease |
| `SELF_OWNED` | Own |

Rationale: The DSP doesn't own Amazon-owned vehicles — they hold them on terms set by Amazon, which behaves like a lease. `AMAZON_RENTAL` is the same pattern: Amazon-managed fleet (often Rivian EDVs via Merchants Fleet or LP) on Amazon's terms, distinct from a short-term commercial rental. `LEASE` is used for third-party leases (e.g., via Zeeba), where the DSP holds the vehicle on a multi-year contract. `SELF_OWNED` covers vehicles the DSP owns outright.

### Vehicle Type

**Primary source: `serviceType`.**

| Amazon `serviceType` | Hera Vehicle Type |
|---|---|
| `Standard Parcel - Extra Large Van - US` | Standard Parcel XL |
| `Standard Parcel - Large Van` | Standard Parcel Large |
| `Standard Parcel - Medium Van` | Standard Parcel |
| `Standard Parcel - Small Van` | Standard Parcel Small |
| `Standard Parcel - Custom Delivery Van 14ft` | Custom Delivery Van |
| `Standard Parcel - Custom Delivery Van 16ft` | Custom Delivery Van |
| `Standard Parcel Electric - Rivian MEDIUM` | EDV |
| `Box Truck Parcel (Large)` | 10,000lbs Van |

**Fallback: `serviceTier`** (used when `serviceType` is blank — common for non-Rivian vehicles in this export).

| Amazon `serviceTier` | Hera Vehicle Type |
|---|---|
| `EXTRA_LARGE_CARGO_VAN` | Standard Parcel XL |
| `LARGE_CARGO_VAN` | Standard Parcel Large |
| `STANDARD_CARGO_VAN` | Standard Parcel |
| `SMALL_CARGO_VAN` | Standard Parcel Small |
| `CUSTOM_DELIVERY_VAN_FOURTEEN_FT` | Custom Delivery Van |
| `CUSTOM_DELIVERY_VAN_SIXTEEN_FT` | Custom Delivery Van |
| `ELECTRIC_RPV_MEDIUM` | EDV |
| `BOX_TRUCK_LARGE` | 10,000lbs Van |

Hera's full Vehicle Type taxonomy: Standard Parcel Small, Standard Parcel, Standard Parcel Large, Standard Parcel XL, Custom Delivery Van, EDV, 10,000lbs Van. Box trucks come through Amazon as `Box Truck Parcel (Large)` / `BOX_TRUCK_LARGE` and map to `10,000lbs Van`, matching the staff `AMXL_BOX_TRUCK` and `Step Van` qualifications.

### Company

| Amazon `vehicleProvider` | Hera Company |
|---|---|
| `BUDGET` | Budget |
| `ELEMENT` | Element |
| `Enterprise` | Enterprise |
| `LP` | Lease Plan |
| `MERCHANTS` | Merchants Fleet |
| `U Haul` | U-Haul |
| `Zeeba` | Zeeba |
| `Kingbee` | Kingbee |
| `Ryder` | Ryder |

Note: `U-Haul`, `Kingbee`, and `Ryder` are not in Hera's currently-documented allowed list. Hera will add them; do not block the import on this.

For Amazon-owned vehicles, populate Company from `vehicleProvider` anyway (these are usually `LP`, `ELEMENT`, `MERCHANTS`, etc. — Amazon's fleet manager partner).

## Pre-import validation checklist

Run every time before handing the converted file to the customer or to the import tool:

1. **Row count** matches source (1 Hera row per Amazon row).
2. **VIN uniqueness** — no duplicates across rows. Flag any duplicates.
3. **License Plate uniqueness** — no duplicates. Flag any duplicates.
4. **VIN length** — every VIN is 17 characters.
5. **Date format** — every populated date matches `MM/DD/YYYY`.
6. **Blank Vehicle Names** — list every row with no name in the pre-import notes so the customer can confirm.
7. **Vehicle Type fallback used** — note every row that used `serviceTier` instead of `serviceType` so the customer knows we made a categorization call on their behalf.
8. **No blank required fields** — Status, License Plate, State, VIN, Start Date, Ownership, Vehicle Type, Make, Model, Year should all be populated.

## Conversion script

A Python script driving the mapping above is checked in at [vehicles-amazon-dsp-convert.py](vehicles-amazon-dsp-convert.py). Usage:

```bash
python3 knowledge/onboarding/vehicles-amazon-dsp-convert.py \
  --input "/path/to/VehiclesData.xlsx" \
  --output "/Users/johnjm/Library/CloudStorage/GoogleDrive-john@hera_app/Shared drives/Imports/Tenants/<Company Name>/<Company Name> - Vehicles.csv"
```

The script prints per-row notes (blank names, serviceTier fallbacks) and a final validation summary.

Output file naming follows the canonical template convention: `<Company Name> - Vehicles.csv` (same pattern as the source templates `Hera - Vehicles.csv`).
