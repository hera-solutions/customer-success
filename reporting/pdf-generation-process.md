# Hera Solutions — PDF Generation Process Documentation

## Overview
This document captures the full process developed across this conversation for transforming raw DynamoDB exports into formatted PDF reports using Python and ReportLab. Two output types were built: **Communication Exports** and **Personnel Records**.

> Brand colors and the Aglet Slab typeface used in these reports are defined in [`branding/brand-guidelines.md`](../branding/brand-guidelines.md). Treat that file as the source of truth; the palette tables below are the working subset used by these specific reports.

---

## 1. Communication Export PDFs

### Purpose
A formatted, printable log of all SMS and email communications sent to and received from a specific associate, exported from Hera's messaging system.

### Input
- DynamoDB CSV console dump (one associate at a time)
- Associate name, DSP name, timezone

### Transformation Steps

#### Timestamp Conversion
- DynamoDB timestamps are in ISO 8601 UTC format (e.g., `2025-10-25T00:05:22.981Z`)
- Convert to local timezone using manual DST rules (no external libraries required)
- **Pacific Time:** DST ends first Sunday in November (UTC-7 PDT → UTC-8 PST)
- **Eastern Time:** DST ends first Sunday in November (UTC-4 EDT → UTC-5 EST)
- Output format: `M/D/YYYY H:MM AM/PM TZ` (e.g., `10/24/2025 5:05 PM PT`)
- Note: Midnight UTC in October/November can flip back a calendar day in Pacific time

#### Field Mapping
| CSV Field | Output Column |
|---|---|
| `createdAt` | Sent |
| `bodyText` | Text Message |
| `destinationNumber` | Number |
| `smsStatus` | SMS Status |
| `destinationEmail` | Email |
| `emailStatus` | Email Status |

#### Data Cleaning Rules
- **Incoming messages** (`channelType = RESPONSE`): Fill Number, SMS Status, Email, Email Status all with `Incoming`
- **Phone numbers**: Normalize any stored format to `(xxx) xxx-xxxx` (e.g., `+12135886546`, `2135886546`, and `(213) 588-6546` all render as `(213) 588-6546`). Strip to digits, drop a leading `1` country code, then reformat; if the result is not a standard 10-digit US number, leave the raw value untouched.
- **Line breaks**: Replace `\n` and `\\n` with ` *line break* ` inline in message text
- **Sort**: All rows sorted chronologically by `createdAt`
- **No-wrap rule**: Only the Text Message column wraps — all other columns are single-line

### PDF Layout
- **Orientation:** Landscape (11" × 8.5")
- **Margins:** 0.5" all sides → 10" usable width
- **Logo:** Hera horizontal logo, top left
- **Header:** Associate name | DSP name | Hera address and phone
- **Column widths (inches):** Sent: 1.35 | Text Message: remainder | Number: 1.05 | SMS Status: 0.9 | Email: 1.85 | Email Status: 0.9
- **Table header:** Hera Blue `#0067bc`, white bold text
- **Incoming rows:** Light blue background `#e8f2fb`
- **Alternating rows:** White / light grey `#fafafa`
- **Footer:** "Powered by Hera Solutions Inc" left, page number right

### Color Palette
| Element | HEX |
|---|---|
| Hera Blue (header) | `#0067bc` |
| Hera Blue Dark (accent) | `#00509a` |
| Incoming row background | `#e8f2fb` |
| Alternating row | `#fafafa` |

### Files Produced
| Associate | DSP | Timezone | File |
|---|---|---|---|
| Juan Gonzalez | Add Logistics LLC | Pacific | `Juan_Gonzalez_Communications.pdf` |
| Jodi Lee Montoya | Merica Delivery Service | Eastern | `Jodi_Montoya_Communications.pdf` |
| Arthur Meyer | Merica Delivery Service | Eastern | `Arthur_Meyer_Communications.pdf` |
| Detronai Rigmaiden | HK Logistics LLC | Pacific | `Detronai_Rigmaiden_Communications.pdf` |

---

## 2. Personnel Record PDFs

### Purpose
A comprehensive, formatted personnel record combining multiple data sources into a single document for HR and legal use. The system is a data repository — it presents data as-is without editorializing, advising, or providing guidance on best practices.

### Design Principles
- Modern, clean layout — minimal grid lines, card-style section headers
- Color-coded by data type and severity
- Alternating light row backgrounds for readability
- `KeepTogether` used on sections with large tables to prevent orphaned headers
- Only the Comment/Text Message column wraps — all other columns single-line
- Footer includes a thin rule line above it

### PDF Layout
- **Orientation:** Landscape (11" × 8.5")
- **Margins:** 0.5" all sides → 10" usable width
- **Logo:** Hera horizontal logo, top left
- **Status badge:** Red pill ("INACTIVE · TERMINATED") top right
- **Section bars:** Full-width Hera Blue rounded bars with section number prefix (01, 02…)
- **Footer:** Powered by Hera | "Confidential Personnel Record" | Associate name | Page number

### Color Palette
| Element | HEX |
|---|---|
| Hera Blue | `#0067bc` |
| Hera Blue Dark | `#00509a` |
| Hera Blue Light (row highlight) | `#e8f2fb` |
| Flag Red (violations) | `#c0392b` |
| Flag Red Light (row background) | `#fdecea` |
| Amber (moderate/warning) | `#e67e22` |
| Amber Light (row background) | `#fef9f0` |
| Orange Light (Netradyne rows) | `#fff8f0` |
| Green (positive values) | `#1a7a3c` |
| Green Light (row highlight) | `#edf7f1` |
| Grey Light (alternating row) | `#f7f8fa` |
| Grey Mid (grid lines) | `#e2e6ea` |
| Grey Dark (labels, footer) | `#6c757d` |
| Near Black (cell text) | `#1c2b3a` |

### Section Structure

#### 01 · Associate Demographics
- Source: Associate JSON from DynamoDB
- Layout: 4-column label/value grid (no table header)
- Fields: Full Legal Name, DOB, Email, Phone, Hire Date, Termination Date, Tenure, DSP, Transporter ID, DL Expiration, Key Focus Area, Fantastic Scorecards, Times Rescued, Status

#### 02 · Attendance Record
- Source: Attendance system export (provided as raw text, one month at a time)
- Layout: Two side-by-side tables (left/right columns), each exactly half of usable width with a 0.2" gap
- Use `KeepTogether` to prevent section bar from orphaning on a separate page from the table
- **Status color coding:**
  - Called Out → Red background `#fdecea`, red bold text, red border above/below row
  - Route Cut → Amber background `#fef9f0`, amber text
  - No Status → Light grey background, grey text
  - Rostered → White/alternating grey
- Attendance and infractions are kept as separate sources — if the company chose not to create an infraction for a call-out, that is reflected as-is
- Source date range noted in section bar subtitle

#### 03 · Weekly Scorecard Summary
- Source: Weekly scorecard DynamoDB export
- Columns: Week, Date, DCR, Tier, Delivered, DNRs, DSB, CDF DPMO, POD, Distractions, Sign/Signal, Following Distance, Speeding
- **Flagged values:** Red bold text
- **DCR values (good):** Green text
- **Tier values:** Fantastic = green, Great = amber
- **Worst performing week:** Red background row with red top border
- **Amber rows:** Weeks with moderate performance dips

#### 04 · POD Quality *(Arthur Meyer only)*
- Source: POD quality DynamoDB export
- Columns: Week, Date, Opportunities, Success, Rejects, Reject Detail, individual reject type counts
- Reject detail column wraps
- Rows with rejects: red background, reject count in red bold
- Week 42 (10/22) had no POD record — noted as data gap

#### 05 · Netradyne Safety Events
- Source: Netradyne DynamoDB export
- Columns: Date, Time (ET), Alert Type, Severity, Description, Vehicle, Video
- **Severe events:** Red background, red bold text, red top border
- **Moderate events:** Standard alternating rows, amber severity text
- **Video available:** Green text; "Available for Request" = amber text
- Video footage noted as available for all events — important for legal documentation

#### 06 · Infractions & Kudos
Two sub-sections within one section bar:

**Infractions**
- Columns: Date, Source, Type, Comment
- Left-edge color stripe by source (3pt `LINEAFTER` on Date column):
  - Manual → Red stripe + red light background
  - Netradyne → Amber stripe + orange light background
  - Scorecard → Grey stripe + grey background
- Comment column wraps

**Kudos**
- Columns: Date, Kudo Type, Value
- DCR kudos → Green light background, green left stripe, green value text
- Consecutive Tier kudos → Blue light background, blue left stripe
- All other kudos → Standard alternating rows

---

## 3. Data Source Reference

### DynamoDB Field Mappings

#### Communications (`channelType`, `bodyText`, etc.)
- `channelType = RESPONSE` → inbound message from associate
- `channelType` anything else → outbound from Hera

#### Kudos (`kudoTypeId`)
| ID Ending | Metric Name |
|---|---|
| `ea45d50b` | Scorecard DCR |
| `078cd11c` | Scorecard Sign/Signal Violation Rate |
| `8ff3e543` | Scorecard Seatbelt-Off Rate |
| `81b9d418` | Scorecard Following Distance Rate |
| `219ad5f9` | Scorecard Distractions Rate |
| `b35f2f75` | Scorecard Speeding Event Rate |
| `4946d664...` | CDF DPMO |
| `d7768e20...` | Scorecard Consecutive Tier |

#### Associate JSON Key Fields
| Field | Use |
|---|---|
| `displayName` | Header name |
| `alternateNames` | Legal name (most common value) |
| `hireDate` | Demographics |
| `terminationDate` | Demographics + tenure calc |
| `status` | Status badge |
| `scoreCardsFantasticCounter` | Demographics |
| `timesRescuedCounter` | Demographics |
| `keyFocusArea` | Demographics (if present) |
| `transporterId` | Demographics |
| `dlExpiration` | Demographics |

---

## 4. Technical Stack

- **Language:** Python 3
- **PDF Library:** ReportLab (`reportlab`)
- **Timezone handling:** Manual DST rules (no `pytz` — not available in environment)
- **No external dependencies** beyond ReportLab
- **Output path:** `/mnt/user-data/outputs/`

### Key ReportLab Patterns

```python
# Prevent orphaned section headers
from reportlab.platypus import KeepTogether
section = KeepTogether([section_bar(...), Spacer(1,5), table])

# Left-edge color stripe by source
TableStyle([('LINEAFTER', (0, i+1), (0, i+1), 3, SOURCE_COLOR)])

# Alternating row backgrounds
TableStyle([('ROWBACKGROUNDS', (0,1), (-1,-1), [WHITE, GREY_LT])])

# Repeat header row on every page
Table(data, colWidths=cws, repeatRows=1)
```

---

## 5. Personnel Records Produced

| Associate | DSP | Hire | Termination | Sections | File |
|---|---|---|---|---|---|
| Jodi Lee Montoya | Merica Delivery Service | 10/22/2025 | 01/31/2026 | Demographics, Attendance, Scorecard, Netradyne, Infractions/Kudos | `Jodi_Montoya_Personnel_Record.pdf` |
| Arthur Joseph Meyer III | Merica Delivery Service | 08/06/2025 | 12/03/2025 | Demographics, Attendance, Scorecard, POD Quality, Netradyne, Infractions/Kudos | `Arthur_Meyer_Personnel_Record.pdf` |

---

*Originally generated April 30, 2026.*
