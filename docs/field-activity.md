# OlivePharma - Field Activity Logging (Feature Specification)

> **Last Updated**: November 2026  
> **Status**: Specification - ready for implementation planning  
> **Owner**: Development Team

---

## 1. Purpose

The pharmaceutical company acquires or manufactures medicines in bulk and supplies them
to pharmacies. It employs a large number of **medical representatives**. The primary
purpose of this application is to **log the daily activity of each worker** (medical
representative) so the company can see what was done, where, with whom, and with what
result.

This feature covers the representative's daily field loop:

1. **Meet Doctor** - visit doctors, introduce products, and log the meeting.
2. **Meet Chemist** - visit pharmacies near each doctor and capture what they need.
3. **Update Sales** - manually record sales/accounting details from the external
   accounting application against the right representative.
4. **Check-In / Check-Out** - a time-based attendance log (no location capture).
5. **Dashboard with Visualisations** - monthly reports, trends, rep-wise and
   hospital-wise views, with filters.

---

## 2. Scope

### In Scope

- Doctor visit logging (state, hospital, doctor, date, products introduced)
- Chemist/pharmacy visit logging (nearby pharmacies, current products, required products)
- Manual sales entry sourced from the external accounting application
- Time-based check-in/check-out (no GPS/location)
- Role-based access for Admin, Representative, and Staff
- Dashboard and reports: monthly, trends, representative-wise, hospital-wise, filters
- CSV export of reports

### Out of Scope

- Invoicing and accounting (handled by a separate accounting application)
- GPS, geolocation, geofencing, or route tracking
- Inventory/stock management and procurement
- Payroll, HR, or attendance beyond check-in/check-out timestamps
- Native mobile app (responsive web app is sufficient)
- Multi-company / multi-tenant support

---

## 3. User Roles & Access

| Role | Login | Responsibilities |
|------|-------|------------------|
| **Admin** | Yes | Full access. Manages users, masters, and targets; views all reports; oversees all activity. |
| **Representative** | Yes | Logs doctor meetings and chemist meetings; checks in/out; views reports associated with them. |
| **Staff** | Yes | Checks in/out; updates sales; views reports associated with them. |

> Roles are enforced **server-side** on every view and queryset. Hiding a button in the
> UI is not sufficient authorisation.

---

## 4. Main Use Cases

### 4.1 Meet Doctor

**Goal**: The representative visits doctors one by one to introduce products/medicines
and build relationships, then logs the meeting.

**Actor**: Representative (Admin may do anything).

**Preconditions**

- The representative is logged in.
- The state, hospital, doctor, and products exist in the masters (or can be added by an
  Admin).

**Main flow**

1. Representative opens **Meet Doctor -> New**.
2. Selects **State**.
3. Selects **Hospital** (filtered by the selected state).
4. Selects **Doctor** (filtered by the selected hospital).
5. Confirms the **Date** (defaults to today; cannot be in the future).
6. Selects one or more **Products introduced**.
7. Optionally adds **Notes**.
8. Saves the meeting.

**Logged fields**

| Field | Required | Notes |
|-------|----------|-------|
| Representative | Auto | The logged-in representative |
| State | Yes | Geographic state/province |
| Hospital | Yes | Must belong to the selected state |
| Doctor | Yes | Must belong to the selected hospital |
| Date | Yes | Visit date; default today; not future |
| Products introduced | Yes (>= 1) | Multi-select from the product catalog |
| Notes | No | Free text |

**Postconditions**

- A doctor meeting record exists, linked to the representative and doctor.
- The meeting appears in the representative's activity list and reports.

---

### 4.2 Meet Chemist

**Goal**: After meeting the doctor, the representative visits nearby pharmacies in the
locality of that doctor, enquires about their current products, and records the products
the pharmacy needs.

**Actor**: Representative (Admin may do anything).

**Preconditions**

- A doctor meeting is the usual context (the pharmacy is in that doctor's locality).
- Pharmacies and products exist in the masters.

**Main flow**

1. Representative opens **Meet Chemist -> New**.
2. Selects **State**, **Hospital**, and the **Doctor** whose locality is being covered.
3. Selects the **Pharmacy/Chemist** (ideally filtered to the doctor's locality).
4. Confirms the **Date** (defaults to today; not future).
5. Records the **Current products** the pharmacy already has (optional notes/list).
6. Adds the **Products the pharmacy needs** (required products).
7. Optionally adds **Notes**.
8. Saves the chemist meeting.

**Logged fields**

| Field | Required | Notes |
|-------|----------|-------|
| Representative | Auto | The logged-in representative |
| State | Yes | Geographic state/province |
| Hospital | Yes | Context for the doctor's locality |
| Doctor | Yes | The doctor whose locality was covered |
| Pharmacy/Chemist | Yes | Must be consistent with the state/locality |
| Date | Yes | Visit date; default today; not future |
| Current products | No | What the pharmacy currently stocks (notes/list) |
| Products needed | Yes (>= 1) | Products the pharmacy requires |
| Notes | No | Free text |

**Postconditions**

- A chemist meeting record exists with the required-products list.
- The record appears in the representative's activity list and in product-demand reports.

---

### 4.3 Update Sales

**Goal**: Sales, invoicing, and accounting happen in a separate accounting application.
Those details are **manually entered** in this application for the appropriate
representative by matching **hospital, doctor, pharmacy, and product**.

**Actor**: Staff and Admin.

**Preconditions**

- The representative, hospital, doctor, pharmacy, and product exist in the masters.
- The source figures come from the external accounting application.

**Main flow**

1. Actor opens **Sales -> Update**.
2. Selects the **Representative** the sale belongs to.
3. Selects **Hospital**, then **Doctor**, then **Pharmacy**, then **Product**.
4. Enters the **Sale date**, **Quantity**, and **Amount**.
5. Enters the external **Invoice/Reference number** (optional but recommended).
6. Saves the sales entry.

**Logged fields**

| Field | Required | Notes |
|-------|----------|-------|
| Representative | Yes | The rep credited with the sale |
| Hospital | Yes | Matched from accounting records |
| Doctor | Yes | Matched from accounting records |
| Pharmacy | Yes | Matched from accounting records |
| Product | Yes | Matched from accounting records |
| Sale date | Yes | From the accounting record; not future |
| Quantity | Yes | Whole units, > 0 |
| Amount | Yes | Money, >= 0 |
| Invoice/Reference | No | External document reference |
| Notes | No | Free text |

**Business rules**

- The combination of representative, hospital, doctor, pharmacy, and product must be
  consistent (doctor belongs to hospital; pharmacy in the same state/locality).
- A sale may be linked to the representative who made the corresponding visits, but the
  link is explicit and recorded, not inferred.
- Duplicate entries are prevented by the external invoice/reference number when supplied.

**Postconditions**

- The sale is attributed to the representative and appears in sales reports.
- Hospital-wise, rep-wise, and product-wise totals update.

---

### 4.4 Check-In / Check-Out

**Goal**: Record the working day attendance of a worker. This is a **time-based log
only** - there is **no GPS or location capture**.

**Actor**: Representative, Staff, Admin.

**Main flow**

1. User opens **Check-In / Check-Out**.
2. Clicks **Check In**; the server records the current timestamp.
3. At the end of the day, clicks **Check Out**; the server records the timestamp and
   computes the duration.
4. The day appears in the user's attendance history and reports.

**Logged fields**

| Field | Required | Notes |
|-------|----------|-------|
| User | Auto | The logged-in user |
| Date | Auto | Work date (server time) |
| Check-in time | Auto | Server timestamp |
| Check-out time | Auto | Server timestamp |
| Duration | Computed | Check-out minus check-in |
| Notes | No | Optional reason for late/early or gaps |

**Business rules**

- A user may have at most **one open check-in** at a time.
- A user cannot check out without an open check-in.
- Timestamps are recorded **server-side** in UTC; the UI displays local time.
- No coordinates, geofencing, or device location are collected or stored.
- Admin can view and correct attendance records; Representative and Staff can view their
  own attendance.

---

### 4.5 Dashboard with Visualisations

**Goal**: Give Admins and workers visibility into activity and sales.

**Actor**: All roles (scoped by permission).

**Scope of data**

- Admin: all representatives and hospitals.
- Representative/Staff: only their own data.

**Widgets and reports**

| Report | Description | Charts |
|--------|-------------|--------|
| Monthly summary | Meetings, check-ins, and sales by month | Line/bar trend |
| Representative-wise | Activity and sales per representative | Bar chart |
| Hospital-wise | Meetings and sales per hospital | Bar chart |
| Product demand | Products needed by chemists | Bar/table |
| Trends | Month-over-month change | Line chart |

**Filters**

- Date range (with quick options: this month, last month, this quarter, this year)
- Month
- Representative
- State
- Hospital
- Product

**Behaviour**

- Filters apply consistently across all report tabs.
- Charts are rendered with Chart.js from server-provided data.
- Reports can be exported to CSV for the selected filters.
- Direct URL access to a report tab redirects to the full reports page.

---

## 5. Data Model

### 5.1 Entities

| Entity | Purpose | Key fields |
|--------|---------|-----------|
| `State` | Geographic state/province | name, code |
| `Hospital` | Hospital where doctors practise | name, state (FK) |
| `Doctor` | Doctor visited by reps | name, speciality, hospital (FK) |
| `Pharmacy` | Chemist/pharmacy near a locality | name, state (FK), locality, hospital (FK, optional) |
| `Product` | Medicine/product catalog | name, SKU, form, strength, active |
| `DoctorMeeting` | A representative's doctor visit | rep, state, hospital, doctor, date, notes |
| `DoctorMeetingProduct` | Products introduced at a doctor meeting | meeting (FK), product (FK) |
| `ChemistMeeting` | A representative's pharmacy visit | rep, state, hospital, doctor, pharmacy, date, current_products, notes |
| `ChemistMeetingProduct` | Products a pharmacy needs | meeting (FK), product (FK), quantity (optional) |
| `SalesEntry` | Manually entered sale from accounting | rep, hospital, doctor, pharmacy, product, date, quantity, amount, reference, notes |
| `AttendanceLog` | Time-based check-in/out | user, date, check_in_at, check_out_at, duration, notes |

### 5.2 Relationships

```
State 1--* Hospital
Hospital 1--* Doctor
State 1--* Pharmacy
Hospital 0--1 Pharmacy            # locality link (optional)

User 1--* DoctorMeeting           # representative
DoctorMeeting *--1 State
DoctorMeeting *--1 Hospital
DoctorMeeting *--1 Doctor
DoctorMeeting 1--* DoctorMeetingProduct *--1 Product

User 1--* ChemistMeeting
ChemistMeeting *--1 State
ChemistMeeting *--1 Hospital
ChemistMeeting *--1 Doctor
ChemistMeeting *--1 Pharmacy
ChemistMeeting 1--* ChemistMeetingProduct *--1 Product

User 1--* SalesEntry
SalesEntry *--1 Hospital
SalesEntry *--1 Doctor
SalesEntry *--1 Pharmacy
SalesEntry *--1 Product

User 1--* AttendanceLog
```

### 5.3 Data Rules

- All domain models inherit `core.models.TimeStampedModel`.
- Every FK has an explicit `related_name`.
- Money uses `DecimalField(max_digits=15, decimal_places=2)`.
- Dates use `DateField`; timestamps use `DateTimeField` in UTC.
- Products needed/introduced use explicit through/link models (not free-text only).
- Historical records keep their FK values; masters use `PROTECT` where deletion would
  corrupt history.

---

## 6. Permissions Matrix

| Action | Representative | Staff | Admin |
|--------|:--------------:|:-----:|:-----:|
| Check in / check out | Yes | Yes | Yes |
| Log doctor meeting | Yes | No | Yes |
| Log chemist meeting | Yes | No | Yes |
| Update sales | No | Yes | Yes |
| View own reports | Yes | Yes | Yes |
| View all reports | No | No | Yes |
| Manage users | No | No | Yes |
| Manage masters (state/hospital/doctor/pharmacy/product) | No | No | Yes |
| View all attendance / correct attendance | No | No | Yes |

---

## 7. Business Rules & Validation

### Doctor meeting
- State -> Hospital -> Doctor selections must be consistent.
- Date cannot be in the future.
- At least one product must be introduced.

### Chemist meeting
- The pharmacy should be in the locality of the selected doctor; the match is advisory
  (a warning, not a hard block) because locality data may be incomplete.
- At least one required product must be selected.
- Date cannot be in the future.

### Sales entry
- Representative, hospital, doctor, pharmacy, and product must all be selected.
- Quantity must be greater than zero; amount must be zero or greater.
- Sale date cannot be in the future.
- When an invoice/reference is provided, it must be unique per representative (prevents
  duplicate manual entry).

### Check-in / check-out
- One open attendance log per user.
- Cannot check out without an open check-in.
- Timestamps are server-generated; client-supplied times are ignored.
- No location data is captured, requested, or stored.

### General
- Only authenticated users can access any page.
- Role checks are applied on the server for every create/update/delete.
- Every record is visible only to its owner unless the user is an Admin.

---

## 8. Reporting Requirements

### Monthly reports
- Total doctor meetings per month
- Total chemist meetings per month
- Total check-ins and total hours per month
- Total sales quantity and amount per month

### Trends
- Month-over-month change for meetings, sales, and attendance
- Filterable by representative, state, hospital, and product

### Representative-wise
- Meetings, check-ins, hours, and sales per representative
- Sortable and exportable

### Hospital-wise
- Doctor and chemist meetings per hospital
- Sales amount per hospital
- Product demand per hospital locality

### Output
- On-screen tables and Chart.js visualisations
- CSV export honouring the active filters

---

## 9. Screens

| Screen | Roles | Purpose |
|--------|-------|---------|
| Dashboard | All (scoped) | KPI cards, trends, recent activity |
| Meet Doctor (list + form) | Representative, Admin | Log and review doctor meetings |
| Meet Chemist (list + form) | Representative, Admin | Log and review chemist meetings |
| Update Sales (list + form) | Staff, Admin | Record sales from accounting |
| Check-In / Check-Out | All | Time-based attendance |
| My Attendance / My Reports | Representative, Staff | Own history and reports |
| Reports index | All (scoped) | Tabs with filters and CSV export |
| Admin masters | Admin | States, hospitals, doctors, pharmacies, products, users |

---

## 10. Technical Mapping

| Concern | App | Notes |
|---------|-----|-------|
| Users and roles | `accounts` | Admin / Representative / Staff role helpers |
| State, hospital, doctor, pharmacy | `outlets` | Masters and locality relationships |
| Products | `products` | Catalog and link models |
| Doctor/chemist meetings, check-in/out | `activities` | Core field activity |
| Sales entries | `sales` | Manual entry from accounting |
| Dashboards and CSV | `reporting` | Aggregations and Chart.js data |
| REST endpoints (if mobile is needed) | `api` | Token auth and object permissions |

### Suggested URLs

| Path | Purpose |
|------|---------|
| `/activities/meet-doctor/` | Doctor meeting list/create |
| `/activities/meet-chemist/` | Chemist meeting list/create |
| `/activities/check-in/` | Check in |
| `/activities/check-out/` | Check out |
| `/activities/attendance/` | Attendance history |
| `/sales/update/` | Manual sales entry |
| `/reports/` | Reports index |
| `/reports/monthly/`, `/reports/representatives/`, `/reports/hospitals/` | Report tabs |

### Service layer

- `activities/services.py`: meeting creation, check-in/out state transitions, duration
- `sales/services.py`: sales validation and duplicate detection
- `reporting/services.py`: monthly, rep-wise, hospital-wise aggregations

---

## 11. Non-Functional Requirements

- **Users**: under 100; single deployable Django project.
- **Performance**: reports respond in under a few seconds for a year of data.
- **Privacy**: no GPS or location capture anywhere in the product.
- **Auditability**: significant changes are recorded in `core.AuditLog`.
- **Timezone**: store UTC, display in the organisation's local timezone.
- **Security**: CSRF on all forms; server-side role enforcement; no secrets in the repo.
- **Accessibility/Mobile**: field forms must be usable on a phone; mobile-first layout.

---

## 12. Acceptance Criteria

- [ ] A Representative can log a doctor meeting with state, hospital, doctor, date, and
      at least one introduced product.
- [ ] A Representative can log a chemist meeting near a doctor, including current
      products and the products the pharmacy needs.
- [ ] A Staff user can add a sales entry matched to representative, hospital, doctor,
      pharmacy, and product.
- [ ] A Representative or Staff user can check in and later check out; the duration is
      computed and **no location data** is stored.
- [ ] A Representative cannot update sales; a Staff user cannot log doctor/chemist
      meetings.
- [ ] Admin can manage users and masters and view all reports.
- [ ] Dashboard shows monthly, representative-wise, and hospital-wise views with filters.
- [ ] Reports export to CSV for the active filters.
- [ ] Direct report-tab URLs redirect to the full reports page for non-HTMX requests.

---

## 13. Assumptions & Open Questions

| # | Assumption / Question | Status |
|---|-----------------------|--------|
| A1 | "State" means a geographic state/province, and every hospital belongs to one. | Assumed |
| A2 | A pharmacy belongs to a state and is associated with a doctor's locality (hospital). | Assumed |
| A3 | Sales are entered manually; no integration with the accounting application. | Confirmed |
| A4 | Check-in/out is a simple time log, one open session per user per day. | Confirmed |
| A5 | Staff do not perform doctor or chemist meetings. | Confirmed |
| A6 | Representatives do not update sales. | Confirmed |
| A7 | Admin can perform any action for oversight. | Confirmed |
| Q1 | Should a chemist meeting always reference a doctor, or may it stand alone? | Open |
| Q2 | Are sales amounts per product line or a single total per entry? | Open |
| Q3 | Should check-in/out support multiple sessions per day (break in/out)? | Open |
| Q4 | What is the exact definition of a pharmacy's "locality" (city, area, pincode)? | Open |

---

## 14. Revision History

### November 2026 - Initial specification
- Documented the daily field activity feature: Meet Doctor, Meet Chemist, Update Sales,
  Check-In/Check-Out (time-only, no GPS), dashboards, and roles.
- Established the Admin / Representative / Staff permission model.
