# OlivePharma - Features by Menu

> **Last Updated**: November 2026
> **Scope**: Every user-facing feature in the current implementation, grouped by the
> menu it is reached from.
> **Source of truth**: The code in this repository. Where the build differs from the
> original specification, this document describes the implemented behaviour and the
> deviation is noted in [Known gaps](#known-gaps).

---

## 1. Roles and Menu Map

OlivePharma has three application roles, stored on `accounts.UserProfile`:

| Role | Description |
|------|-------------|
| **Admin** | Full access: masters, users, visits, sales, targets, reports, attendance. Superusers are treated as admins. |
| **Representative** | Field worker: logs doctor/chemist visits, checks in/out, views own reports. |
| **Staff** | Office user: enters sales, checks in/out, views company-wide sales/report data. |

A `UserProfile` is created automatically whenever a Django user is created. New
superusers get the `admin` role; all other new users default to `rep`.

### Main navigation by role

Main navigation is defined in `core/navigation.py` and rendered by
`templates/base.html`. Menu links are filtered server-side by role.

| Menu item | Route | Admin | Representative | Staff |
|-----------|-------|:-----:|:--------------:|:-----:|
| Dashboard | `/` | Yes | Yes | Yes |
| Reports | `/reports/` | Yes | Yes | Yes |
| Meet Doctor | `/visits/doctor/` | Yes | Yes | No |
| Meet Chemist | `/visits/chemist/` | Yes | Yes | No |
| Sales | `/sales/` | Yes | No* | Yes |
| Check In/Out | `/checkin/` | Yes | Yes | Yes |
| Help | `/help/` | Yes | No** | No** |

\* Representatives can still open `/sales/` directly and see their own sales; the Sales
entry is simply not shown in their main navigation.
\** Help is available to every authenticated user from the user menu (see
[User Menu](#8-user-menu)).

### User menu (available on every authenticated page)

| Item | Route |
|------|-------|
| Profile | `/profile/` |
| Help | `/help/` |
| Logout | `POST /accounts/logout/` |

### Access control layers

- `RoleRequiredMixin` checks the role in every protected view.
- `core.middleware.RoleAccessMiddleware` enforces path-level rules:
  - `/sales/new/` - Admin, Staff
  - `/sales/` - Admin, Staff, Representative
  - `/visits/` - Admin, Representative
  - `/checkin/` - Admin, Staff, Representative
- `ScopedQuerySet.for_user()` filters data:
  - Admin/superuser: all records.
  - Staff: company-wide for sales, visits and dashboard reports; own records only for
    attendance.
  - Representative: own records only.
- Unauthorised access returns `403 Forbidden`; unauthenticated access redirects to login.

---

## 2. Dashboard

**Menu**: Dashboard
**Route**: `/` (`dashboard:home`)
**Roles**: Admin, Representative, Staff (data scoped by role)
**Template**: `templates/dashboard/home.html`
**View**: `dashboard.views.DashboardView`
**Service layer**: `dashboard/services.py`

### Purpose
Landing page after login. Gives an at-a-glance view of field activity, attendance and
sales for the selected period.

### Features

#### Filters
Shared filter form (`dashboard/forms.py`, rendered by `dashboard/_filters.html`):

| Filter | Behaviour |
|--------|-----------|
| Start date | Defaults to the first day of the current month. |
| End date | Defaults to today. |
| Representative | Visible to Admin/Staff only. Representatives are always scoped to themselves. |
| Hospital | Optional; all hospitals. |
| Product | Optional; all products. |

- **Apply** submits the filters.
- **Reset** clears back to the default date range.
- Start date after end date triggers a validation error.
- Filters apply to KPI cards, charts, breakdown tables and the export link.

#### KPI cards
Four colour-accented `.kpi-card` tiles:

| KPI | Description |
|-----|-------------|
| Doctor Visits | Count of doctor visits in range. |
| Chemist Visits | Count of chemist visits in range. |
| Check-ins | Count of attendance records in range. |
| Sales Amount | Sum of sales amounts; shows the number of sales entries as metadata. |

#### Charts (Chart.js bar charts)
- **Representative-wise sales** - sales amount per representative (top 10).
- **Hospital-wise sales** - sales amount per hospital (top 10).

Charts are server-rendered as JSON and drawn with Chart.js; they are responsive and
start at zero on the Y axis.

#### Breakdown tables
- **Representative breakdown** (top 10 by sales amount): representative, doctor visits,
  chemist visits, check-ins, sales amount.
- **Hospital breakdown** (top 10 by sales amount): hospital, doctor visits, chemist
  visits, sales amount.
- **Recent activity**: latest 5 doctor/chemist visits combined, showing type, date,
  representative, outlet (doctor or pharmacy) and hospital.

Each table has an empty state ("No activity in this period." / "No recent activity.").

#### Page actions
- **Reports** button navigates to the Reports page.
- **Export** button downloads the Monthly report as CSV using the active date range,
  representative, hospital and product filters.

---

## 3. Reports

**Menu**: Reports
**Route**: `/reports/` (`dashboard:reports`)
**Roles**: Admin, Representative, Staff (data scoped by role)
**Template**: `templates/dashboard/reports.html`
**View**: `dashboard.views.ReportsView`
**Definitions**: `dashboard/reports.py`

### Purpose
Detailed, tabbed reporting with charts and CSV export, using one shared filter set.

### Features

#### Report tabs
The active tab is driven by the `?tab=` query parameter and defaults to `monthly`.
Tab switching preserves the active filters.

| Tab | Columns |
|-----|---------|
| **Monthly** | Month, Doctor Visits, Chemist Visits, Quantity, Sales Amount |
| **Representatives** | Representative, Doctor Visits, Chemist Visits, Check-ins, Quantity, Sales Amount |
| **Hospitals** | Hospital, Doctor Visits, Chemist Visits, Quantity, Sales Amount |
| **Products** | Product, Doctors Introduced, Chemist Demand, Quantity, Sales Amount |

Behaviour per tab:
- **Monthly** merges sales, doctor visits and chemist visits by calendar month and sorts
  chronologically.
- **Representatives** combines sales, visit counts and check-ins per representative,
  sorted by sales amount then doctor visits (descending).
- **Hospitals** combines sales and visit counts per hospital, sorted by sales amount then
  doctor visits (descending).
- **Products** combines sales totals, the number of distinct doctors each product was
  introduced to, and the number of distinct chemist visits where the product was needed,
  sorted by sales amount then introductions (descending).

#### Filters
Same shared filters as the Dashboard: date range, representative (Admin/Staff only),
hospital and product. Filters apply consistently across every tab and to CSV export.

#### Chart
A Chart.js bar chart above the detail table:
- Monthly: doctor visits and chemist visits per month (two datasets).
- Representatives/Hospitals/Products: sales amount for each row.

#### CSV export
- Button on the page exports the **currently active tab**.
- Honours all active filters.
- File name format: `<report>-<YYYY-MM-DD>.csv`.
- First row contains the column labels; one row per report row.
- Empty report still exports the header row.

#### Pagination
Report tables are rendered in full for the selected period (no page-size limit);
pagination applies to the list screens described below.

---

## 4. Meet Doctor

**Menu**: Meet Doctor
**Routes**:
- `/visits/doctor/` (`visits:doctor_list`)
- `/visits/doctor/new/` (`visits:doctor_create`)
**Roles**: Admin, Representative
**Templates**: `templates/visits/doctor_list.html`, `doctor_form.html`
**Views**: `visits.views.DoctorVisitListView`, `DoctorVisitCreateView`
**Model**: `visits.models.DoctorVisit`
**Service**: `visits.services.log_doctor_visit`

### Purpose
Log every doctor meeting: who was met, where, when, and which products were introduced.

### List page features
- Table columns: Date, Doctor, Hospital, Region, Representative, Products.
- Products are shown as badges; `—` when none are recorded.
- Ordered by date descending, then newest first.
- Paginated at 20 records per page.
- Empty state: "No doctor visits logged yet."
- **New visit** button opens the create form.
- Data scoping: Admin sees all visits; Representatives see only their own.

### Create page features
Form fields (`visits/forms.py`):

| Field | Type | Notes |
|-------|------|-------|
| Date | Date picker | Required. Rejects dates after today (Admin exempt). |
| Region | Select | Required; all regions. |
| Hospital | Select | Required; filtered by the selected region. |
| Doctor | Select | Required; filtered by the selected hospital. |
| Products introduced | Multi-select | Optional at the form level; active products only. |
| Notes | Textarea | Optional; 3 rows. |

- **Dependent dropdowns**: changing Region reloads and resets Hospital and Doctor;
  changing Hospital reloads and resets Doctor. The options come from the JSON endpoint
  `/visits/filter-options/` (`visits:filter_options`), backed by `visits.views.filter_options`.
- **Future-date validation**: representatives cannot log a visit dated after today;
  admins are exempt so they can correct or pre-enter records.
- Submit creates the visit through `log_doctor_visit()`, which sets the logged-in user as
  the representative and attaches the selected products.
- Emits the `doctor_visit_logged` signal.
- A receiver writes an `AuditLog` entry (`action=doctor_visit_logged`,
  `object_type=DoctorVisit`) containing the date and doctor ID.
- Success message: "Doctor visit logged." and redirect to the list.
- **Back** and **Cancel** return to the list.

---

## 5. Meet Chemist

**Menu**: Meet Chemist
**Routes**:
- `/visits/chemist/` (`visits:chemist_list`)
- `/visits/chemist/new/` (`visits:chemist_create`)
**Roles**: Admin, Representative
**Templates**: `templates/visits/chemist_list.html`, `chemist_form.html`
**Views**: `visits.views.ChemistVisitListView`, `ChemistVisitCreateView`
**Model**: `visits.models.ChemistVisit`
**Service**: `visits.services.log_chemist_visit`

### Purpose
Log pharmacy/chemist visits: what the pharmacy currently stocks and what it needs,
in the context of a doctor's locality.

### List page features
- Table columns: Date, Pharmacy, Doctor, Hospital, Representative, Products needed.
- Products are shown as badges; `—` when none are recorded.
- Ordered by date descending, then newest first.
- Paginated at 20 records per page.
- Empty state: "No chemist visits logged yet."
- **New visit** button opens the create form.
- Data scoping: Admin sees all visits; Representatives see only their own.

### Create page features
Form fields (`visits/forms.py`):

| Field | Type | Notes |
|-------|------|-------|
| Date | Date picker | Required. Rejects dates after today (Admin exempt). |
| Region | Select | Required; all regions. |
| Hospital | Select | Required; filtered by the selected region. |
| Doctor | Select | Required; filtered by the selected hospital. |
| Pharmacy | Select | Required; filtered by the selected hospital. |
| Current products | Textarea | Optional; what the pharmacy currently stocks. |
| Products needed | Multi-select | Optional at the form level; active products only. |
| Notes | Textarea | Optional; 3 rows. |

- **Dependent dropdowns**: changing Region reloads and resets Hospital, Doctor and
  Pharmacy; changing Hospital reloads and resets Doctor and Pharmacy. Options come from
  `/visits/filter-options/` (`visits:filter_options`).
- **Future-date validation**: representatives cannot log a visit dated after today;
  admins are exempt.
- Submit creates the visit through `log_chemist_visit()`, which sets the logged-in user
  as the representative and attaches the needed products.
- Emits the `chemist_visit_logged` signal.
- A receiver writes an `AuditLog` entry (`action=chemist_visit_logged`,
  `object_type=ChemistVisit`) containing the date and pharmacy ID.
- Success message: "Chemist visit logged." and redirect to the list.
- **Back** and **Cancel** return to the list.

---

## 6. Sales

**Menu**: Sales (Admin, Staff; Representatives can open the URL but the menu item is
hidden)
**Routes**:
- `/sales/` (`sales:list`)
- `/sales/new/` (`sales:create`)
- `/sales/targets/` (`sales:target_list`)
- `/sales/targets/new/` (`sales:target_create`)
**Templates**: `templates/sales/list.html`, `form.html`, `target_list.html`,
`target_form.html`
**Views**: `sales.views.SalesLogListView`, `SalesLogCreateView`,
`TargetListView`, `TargetCreateView`
**Models**: `sales.models.SalesLog`, `sales.models.Target`
**Service**: `sales.services.log_sales`, `sales.services.target_attainment`

### 6.1 Sales list

**Roles**: Admin, Staff, Representative (scoped)

- Table columns: Date, Representative, Product, Qty, Amount, Pharmacy, Hospital,
  Reference.
- Quantity and amount are right-aligned; amount is formatted to 2 decimals.
- Missing reference is shown as `—`.
- Ordered by sale date descending, then newest first.
- Paginated at 20 records per page.
- Empty state: "No sales recorded yet."
- Page actions:
  - **Targets** - opens the Targets sub-page.
  - **New entry** - visible and permitted only for Admin and Staff.
- Data scoping: Admin/Staff see all sales; Representatives see only their own.

### 6.2 New sales entry

**Roles**: Admin, Staff

Form fields (`sales/forms.py`):

| Field | Type | Notes |
|-------|------|-------|
| Representative | Select | Required; active users. |
| Sales date | Date picker | Required. Rejects dates after today (Admin exempt). |
| Region | Select | Required. |
| Hospital | Select | Required. |
| Doctor | Select | Required. |
| Pharmacy | Select | Required. |
| Product | Select | Required; active products only. |
| Quantity | Number | Required; minimum 1. |
| Amount | Number | Required; minimum 0, 2-decimal step. |
| Reference | Text | Optional; external invoice/reference. |
| Notes | Textarea | Optional; 3 rows. |

Features and rules:
- Submit creates the entry through `log_sales()`, recording the logged-in user as
  `entered_by`.
- Emits the `sales_logged` signal; a receiver writes an `AuditLog` entry
  (`action=sales_logged`, `object_type=SalesLog`) with representative, amount and
  quantity.
- **Duplicate protection**: when a reference is supplied it must be unique per
  representative. Enforced in the form and by the database constraint
  `unique_sales_reference_per_rep`.
- **Future-date validation**: staff cannot log a sale dated after today; admins are
  exempt.
- Success message: "Sales entry logged." and redirect to the list.
- **Back** and **Cancel** return to the list.

### 6.3 Targets

**Roles**: List - Admin, Staff, Representative (scoped); Create - Admin only
**Route**: reached from the Sales page via the **Targets** button.

List page features:
- Table columns: Representative, Period, Start, End, Product, Amount target,
  Quantity target.
- A target without a product is labelled **Overall**.
- Ordered by start date descending, then newest first.
- Paginated at 20 records per page.
- Empty state: "No targets defined."
- **Back to sales** button.
- **New target** button visible to Admin only.
- Data scoping: Admin/Staff see all targets; Representatives see only their own.

Create page features:

| Field | Type | Notes |
|-------|------|-------|
| Representative | Select | Required; active users. |
| Period | Select | Month or Quarter. |
| Start date | Date picker | Required. |
| End date | Date picker | Required. |
| Product | Select | Optional; blank means an overall target. |
| Amount target | Number | Minimum 0, 2-decimal step. |
| Quantity target | Number | Minimum 0. |

- Unique per representative + product + start date + end date
  (`unique_target_per_rep_product_period`).
- Success message: "Target saved." and redirect to the Targets list.

### 6.4 Target attainment (service-level)

`target_attainment(rep, start_date, end_date, product=None)` computes:
- Target and actual amount.
- Target and actual quantity.
- Amount attainment percentage and quantity attainment percentage (rounded to 1
  decimal; `None` when the target is zero).

This service is implemented and testable but is not currently surfaced on a page.

---

## 7. Check In/Out

**Menu**: Check In/Out
**Routes**:
- `/checkin/` (`checkin:list`)
- `/checkin/in/` (`checkin:check_in`)
- `/checkin/out/` (`checkin:check_out`)
**Roles**: Admin, Representative, Staff
**Templates**: `templates/checkin/list.html`, `check_in.html`, `check_out.html`
**Views**: `checkin.views.CheckInListView`, `CheckInView`, `CheckOutView`
**Model**: `checkin.models.CheckInOut`
**Services**: `checkin.services.check_in`, `checkin.services.check_out`

> **Privacy**: This is a **time-based attendance log only**. No GPS, geolocation,
> geofencing, route tracking or device location is collected, requested or stored.

### 7.1 Attendance list

- Table columns: Date, User, Check in, Check out, Duration, Status, Notes.
- Times are displayed as `H:i`.
- Status badge: **Open** (green) when there is no check-out, **Closed** otherwise.
- Duration is computed from check-in/check-out and supports overnight shifts.
- Notes preserve line breaks.
- Ordered by date descending, then newest first.
- Paginated at 30 records per page.
- Empty state: "No check-ins recorded yet."
- Page actions:
  - **Check in** - opens the check-in form.
  - **Check out** - opens the check-out form.
- Data scoping: Admin sees all records; Representatives and Staff see only their own
  (`staff_company_wide=False`).

### 7.2 Check in

- Fields: Date (defaults to today), Check-in time (defaults to the current local time,
  seconds removed), Notes (optional).
- Creating a second check-in for the same user and date is rejected with:
  "You have already checked in for this date."
- Enforced by the `unique_checkin_per_user_per_day` constraint.
- Success message: "Checked in." and redirect to the attendance list.
- **Back** and **Cancel** return to the list.

### 7.3 Check out

- Fields: Date (defaults to today), Check-out time (defaults to the current local time),
  Notes (optional).
- Requires an existing check-in for that user and date, otherwise:
  "No check-in found for this date."
- Rejects a second check-out with: "You have already checked out for this date."
- Submitted notes are appended to any existing notes.
- Success message: "Checked out." and redirect to the attendance list.
- **Back** and **Cancel** return to the list.

---

## 8. Help

**Menu**: Help (main navigation for Admin; user menu for every role)
**Route**: `/help/` (`help`)
**Roles**: Public (not login-protected)
**Template**: `templates/help.html`

Displays four quick-guide cards:

| Card | Content |
|------|---------|
| Meet Doctor | Record region, hospital, doctor, date and products introduced. |
| Meet Chemist | Log the pharmacy near the doctor, current products and products needed. |
| Check In / Out | Record time-based check-ins/outs; no location data is captured. |
| Sales | Staff and admins enter manual sales against a representative, outlet and product. |

---

## 9. User Menu

The header user menu is available on every authenticated page. It is opened by the
avatar/name button and closed by clicking outside it.

- Header shows the user's full name (or username) and role.
- Dropdown header shows the full name and email (or `—`).
- **Profile** - opens `/profile/`.
- **Help** - opens `/help/`.
- **Logout** - submits a CSRF-protected POST form to `/accounts/logout/`.

### 9.1 Profile

**Route**: `/profile/` (`accounts:profile`)
**Roles**: Any authenticated user
**Template**: `templates/accounts/profile.html`
**View**: `accounts.views.ProfileView`

Features:
- Shows the read-only username.
- Shows the role badge.
- Editable fields:
  - Phone
  - Employee code
  - Region
- **Save profile** updates the `UserProfile` and stays on the page.
- A profile is created automatically if one is missing.

---

## 10. Authentication Screens

### 10.1 Login

**Route**: `/accounts/login/` (`login`)
**Template**: `templates/registration/login.html`

- Branded sign-in card with username and password fields.
- Shows "Invalid username or password." when authentication fails.
- Supports the `next` redirect parameter.
- Redirects to the Dashboard on success (`LOGIN_REDIRECT_URL = dashboard:home`).

### 10.2 Logout

**Route**: `/accounts/logout/` (`logout`), POST only from the user menu.

- Logs the user out and redirects to the signed-out screen.
- Signed-out screen (`templates/registration/logged_out.html`) confirms the logout and
  offers **Sign in again**.

---

## 11. Master Data, Admin and CMS

These screens are not part of the role-based main navigation but are part of the
application.

### 11.1 Django admin

**Route**: `/django-admin/`
**Access**: Django staff/superuser accounts.

Registered models and features:
- **Region** - list name/code, search.
- **Hospital** - list name/region/city, filter by region, search.
- **Doctor** - list name/hospital/speciality, filter by hospital, search.
- **Pharmacy** - list name/region/hospital/locality, filter by region, search.
- **Product** - list name/SKU/form/strength/active, filter by active/form, search.
- **AuditLog** - list action/object/user/time, filter by action/object type, read-only.
- **UserProfile** - list user/role/employee code/region, filter by role/region, search.
- **DoctorVisit** - list rep/date/doctor/hospital/region, date/region/hospital filters,
  horizontal product picker.
- **ChemistVisit** - list rep/date/pharmacy/doctor/hospital/region, filters, horizontal
  product picker.
- **SalesLog** - list rep/date/product/quantity/amount/pharmacy/entered_by, date/region/
  product filters, search, date drill-down.
- **Target** - list rep/period/dates/product/targets, period/date filters, search.
- **CheckInOut** - list user/date/times, date filter, search, date drill-down.

### 11.2 DB profiling

**Routes**:
- `/django-admin/db-profiling/` (`admin_db_profiling`; also mounted under the Region
  admin as `admin:db_profiling`)
- `/django-admin/db-profiling/seed/` (`admin_db_profiling_seed`; also
  `admin:db_profiling_seed`)
**Access**: Django staff/superuser only (`admin.site.admin_view`).
**Templates**: `templates/admin/index.html`, `templates/admin/core/db_profiling.html`
**Views**: `core.admin_views.db_profiling_view`, `seed_table_view`
**Services**: `core.services.profiling.get_table_stats`,
`core.services.seeding.seed_rows`, `seedable_models`

Features:
- Added to the Django admin index as a **Database tools → DB Profiling** module.
- Table statistics for every project model (`accounts`, `checkin`, `cms`, `core`,
  `dashboard`, `sales`, `visits`): app, model, database table, row count and latest
  timestamp. Framework tables (auth, sessions, admin, Wagtail internals, etc.) are
  skipped.
- Latest timestamp uses `updated_at`, then `created_at`, then the first available
  `DateTimeField`.
- Inline **Seed sample data** form: choose a supported project model and row count
  (1-1000), then submit. Rows are generated with Faker; related masters/users are reused
  or created as needed.
- Seedable models: Region, Hospital, Doctor, Pharmacy, Product, AuditLog, DoctorVisit,
  ChemistVisit, SalesLog, Target and CheckInOut.
- Success and error feedback appears as Django admin messages.
- CLI equivalent: `python manage.py seed_table <app.Model> --rows <n>`.

### 11.3 Wagtail CMS

**Route**: `/cms/` (Wagtail admin)
**Access**: Wagtail permissions.

- `CMSHomePage` - a single optional home content page (intro + body).
- `CMSPage` - nested optional content pages (intro + body).
- `SiteSetting` - registered snippet with site name and tagline.
- Wagtail documents are served under `/documents/`.
- CMS pages are served from the root URL after all application routes.

---

## 12. Cross-Cutting Features

### Layout and navigation
- Two-row application shell: utility/header row with brand and user menu; module
  navigation row.
- Role-filtered navigation links with Bootstrap Icons.
- Active navigation link highlighting based on the current path.
- Mobile navigation toggle with accessible expanded state and icon swap.
- Bootstrap 5.3, Chart.js 4.4 and the "Trusted Innovator" theme tokens from
  `static/css/theme.css`.
- Mobile-first layout; tables use responsive wrappers.

### Audit logging
- Doctor visits, chemist visits and sales entries write `AuditLog` rows through Django
  signals.
- Audit rows capture the acting user, action, object type/ID and a JSON `changes` payload.
- Audit logs are visible in the Django admin and are read-only there.

### Pagination
Shared `templates/partials/pagination.html`:
- Previous/Next controls with disabled states.
- Numbered page links.
- Used by visit, sales, target and attendance lists.

### Forms
Shared `templates/partials/form_fields.html`:
- Required-field marker.
- Help text.
- Field-level validation errors.
- Non-field errors as an alert.

### Messages
Django messages render as dismissible Bootstrap alerts after create actions.

### Data integrity
- Shared timestamps from `core.models.TimeStampedModel`.
- Foreign-key protection keeps historical records intact (`PROTECT` on masters).
- Unique constraints for sales references, targets and daily attendance.
- Indexes on the fields used by lists, filters and dashboards.

---

## 13. Operational Features (not menu screens)

| Feature | Command / Route | Purpose |
|---------|-----------------|---------|
| Health check | `/health/` | JSON report of database connectivity and applied migrations; returns `200` when healthy and `503` with `"migrations": "missing"` otherwise. |
| Seed demo data | `python manage.py seed_demo` | Creates demo users (`admin`, `rep`, `staff` / `password123`), masters, visits, a sale, a target and a check-in. |
| Seed a table | `python manage.py seed_table <app.Model> --rows <n>` | Creates Faker-based sample rows for a supported project model (1-1000 rows). |
| Ensure superuser | `python manage.py ensure_superuser` | Creates/updates a deployment admin from `DJANGO_SUPERUSER_*` environment variables and sets the `admin` role. |
| Filter options API | `/visits/filter-options/` | JSON endpoint used by the dependent dropdowns. Accepts `type=hospital&region=<id>`, `type=doctor&hospital=<id>` or `type=pharmacy&hospital=<id>`. |

---

## 14. Feature-to-Code Map

| Feature | App / module | Key files |
|---------|--------------|-----------|
| Dashboard | `dashboard` | `views.py`, `services.py`, `forms.py`, `templates/dashboard/home.html` |
| Reports | `dashboard` | `reports.py`, `views.py`, `templates/dashboard/reports.html` |
| CSV export | `dashboard` | `views.CSVExportView` |
| Meet Doctor | `visits` | `models.DoctorVisit`, `views.py`, `forms.py`, `services.py`, `receivers.py` |
| Meet Chemist | `visits` | `models.ChemistVisit`, `views.py`, `forms.py`, `services.py`, `receivers.py` |
| Sales | `sales` | `models.SalesLog`, `views.py`, `forms.py`, `services.py`, `receivers.py` |
| Targets | `sales` | `models.Target`, `views.py`, `forms.py`, `services.target_attainment` |
| Check In/Out | `checkin` | `models.CheckInOut`, `views.py`, `forms.py`, `services.py` |
| Help | `config` / `templates` | `config/urls.py`, `templates/help.html` |
| Profile | `accounts` | `models.UserProfile`, `views.ProfileView`, `forms.ProfileForm` |
| Menu and access | `core` | `navigation.py`, `permissions.py`, `middleware.py`, `managers.py` |
| Masters and audit | `core` | `models.py`, `admin.py` |
| Dependent dropdowns | `visits` | `views.filter_options`, `visits/urls.py`, `visits/doctor_form.html`, `visits/chemist_form.html` |
| DB profiling | `core` | `services/profiling.py`, `admin_views.py`, `admin.py`, `templates/admin/core/db_profiling.html` |
| Sample-data seeding | `core` | `services/seeding.py`, `management/commands/seed_table.py` |
| Login/logout | Django auth | `config/urls.py`, `templates/registration/` |
| CMS | `cms` | `models.py`, `wagtail_hooks.py` |

---

## 15. Known Gaps

The following behaviours are specified in `docs/field-activity.md` but are not fully
implemented in the current UI. They are documented here so the docs match the code.

- **Dependent dropdowns on Sales**: the cascade is wired only on the Meet Doctor and Meet
  Chemist forms. The Sales entry form still lists all masters independently.
- **Required products**: Products introduced/needed are optional at the form level even
  though the specification marks them as required.
- **Target attainment UI**: `target_attainment()` is implemented but not displayed on a
  page.
- **CMS templates**: `cms.CMSHomePage` and `cms.CMSPage` reference
  `templates/cms/home_page.html` and `templates/cms/cms_page.html`, which are not present
  in the repository, so serving a created CMS page will currently fail with a template
  error.
- **Report pagination**: Report tables render all rows; only list screens paginate.
