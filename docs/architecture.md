# Architecture Overview

OlivePharma implements a **modular monolith** architecture tuned for a small internal
audience (under 100 users). It prioritises clarity, fast iteration, and a mobile-first
field workflow over distributed-systems complexity.

> **Implementation note (November 2026)**: The sections below describe the agreed
> architecture. The shipped build uses `config/` as the project package and these apps:
> `core`, `accounts`, `visits`, `sales`, `checkin`, `dashboard`, and optional `cms`.
> Naming mappings: `outlets` + `products` live in `core` (`Region`, `Hospital`, `Doctor`,
> `Pharmacy`, `Product`); `activities` is split into `visits` (`DoctorVisit`,
> `ChemistVisit`) and `checkin` (`CheckInOut`); `reporting` is `dashboard`; the DRF `api`
> app is not implemented. Production uses PostgreSQL (not MySQL), and reports are
> server-rendered tabs with Chart.js rather than HTMX fragments.

---

## 1. Core Architectural Patterns

### 1.1 Modular Monolith (Primary Pattern)

The application is a single deployable Django project divided into independent,
loosely-coupled apps, each representing a bounded context:

```
config/            # Project package (settings, urls, wsgi, asgi)
core/              # Masters, managers, audit, navigation, permissions, health
accounts/          # Users and roles (Admin/Representative/Staff)
visits/            # DoctorVisit, ChemistVisit, services, audit signals
sales/             # SalesLog, Target, services, audit signals
checkin/           # CheckInOut (time-only)
dashboard/         # KPIs, filters, reports, CSV export
cms/               # Optional Wagtail pages and snippet
```

**Benefits**

- One codebase, one deploy - easy to run and reason about at this scale
- Clear boundaries so features do not bleed into each other
- Can be split later only if genuinely needed (it is not, at under 100 users)
- Multiple developers can work on separate apps with minimal conflict

### 1.2 Model-View-Template (MVT) with Progressive Enhancement

Follows Django's native architecture with light frontend enhancement:

- **Models**: data structure and invariants (`visits/models.py`, `sales/models.py`)
- **Views**: request handling and data retrieval (`visits/views.py`, `dashboard/views.py`)
- **Templates**: presentation (`templates/visits/doctor_list.html`)
- **Chart.js**: client-side charts fed by server-rendered data; no SPA or HTMX dependency

### 1.3 Domain-Driven Design Influences

Each app is a bounded context that owns its:
- Data models and business rules
- Views and URL routing
- Templates and UI components
- Tests

Cross-context interaction happens through foreign keys and service functions, never
through direct writes into another app's internals.

### 1.4 Service Layer Pattern

Complex or multi-model logic is encapsulated in a `services.py` module inside the
owning app, keeping models and views thin:

```python
# sales/services.py
def target_attainment(rep, period):
    """Compute actual vs. target for a rep and period."""
    target = Target.objects.filter(rep=rep, period=period).aggregate(...)
    actual = SalesEntry.objects.filter(rep=rep, period=period).aggregate(...)
    return {...}
```

**Benefits**: testable business logic, thin models/views, clear ownership.

### 1.5 RESTful API Layer

A Django REST Framework API serves the mobile client:

- Token authentication for the app
- Session authentication for the browsable API
- ViewSets per resource, with object-level permissions
- Time-based check-in/check-out endpoints (no location data); idempotent if offline
  retries are needed

---

## 2. Domain Model

### 2.1 Bounded Contexts

| App | Responsibility | Key Models |
|-----|----------------|-----------|
| `core` | Shared foundations | `TimeStampedModel`, `AuditLog` |
| `accounts` | People & roles | `RepProfile`, `Territory` |
| `outlets` | Places reps visit | `State`, `Hospital`, `Doctor`, `Pharmacy` |
| `products` | What reps sell | `Category`, `Product` |
| `activities` | What reps do | `DoctorMeeting`, `ChemistMeeting`, `AttendanceLog` |
| `sales` | Outcomes | `SalesEntry`, `Target` |
| `reporting` | Insight | (aggregations over other apps) |
| `api` | Mobile access | Serializers, ViewSets |

### 2.2 Entity Relationships

```
State 1--* Hospital
Hospital 1--* Doctor
State 1--* Pharmacy
Hospital 0--1 Pharmacy            # locality link (optional)

DoctorMeeting *--1 User (representative)
DoctorMeeting *--1 State / Hospital / Doctor
DoctorMeeting 1--* DoctorMeetingProduct *--1 Product

ChemistMeeting *--1 User (representative)
ChemistMeeting *--1 State / Hospital / Doctor / Pharmacy
ChemistMeeting 1--* ChemistMeetingProduct *--1 Product

SalesEntry *--1 User (representative)
SalesEntry *--1 Hospital / Doctor / Pharmacy / Product
Target *--1 User (representative) / Product

AttendanceLog *--1 User
```

### 2.3 Conventions

- All domain models inherit `core.models.TimeStampedModel`.
- Every foreign key has an explicit `related_name`.
- Choice lists are module-level constants in `SCREAMING_SNAKE_CASE`.
- `Meta.indexes` are added for fields used in list filters and dashboards.
- `Meta.ordering` is set where a stable default order matters.
- Money uses `DecimalField(max_digits=15, decimal_places=2)`; never floats.
- Dates use `DateField`; timestamps use `DateTimeField` stored in UTC.
- **No coordinate/location fields**: check-in/out is time-based only.

---

## 3. Field Workflow: Daily Activity & Time Logging

The central flows are deliberately simple. Check-in/out is a **time-based log only**;
there is no GPS or location capture anywhere in the product.

### 3.1 Daily activity loop

```
Representative opens My Day
      │
      ├─► Meet Doctor   ──► state → hospital → doctor → date → products introduced
      │
      ├─► Meet Chemist  ──► state → hospital → doctor → pharmacy → products needed
      │
      └─► Check In / Check Out ──► server timestamps → duration
      │
      ▼
Activity appears in the user's list and in reports (scoped by role)
```

### 3.2 Check-in / check-out flow

```
User opens Check-In / Check-Out
      │
      ▼
Check In  ──► POST /activities/check-in/  ──► AttendanceLog(open, server time)
      │
      ▼
Work during the day
      │
      ▼
Check Out ──► POST /activities/check-out/ ──► AttendanceLog(closed), duration computed
      │
      ▼
Appears in My Attendance and attendance reports
```

**Design rules**

- Check-in and check-out are timestamped **server-side** in UTC; display in local time.
- **No coordinates, geofencing, or device location are requested or stored.**
- A user may have at most one open attendance log at a time (enforced in the service
  layer).
- A check-out without an open check-in is rejected.
- Admin may view and correct attendance; other roles see only their own.
- If an optional mobile/offline client is added later, the check-in endpoint may accept
  a client-supplied `client_uuid` for idempotent retries - still with no location data.

### 3.3 Meeting logging rules

- **Meet Doctor** captures state, hospital, doctor, date, and introduced products.
- **Meet Chemist** captures the pharmacy near the doctor's locality, current products,
  and the products the pharmacy needs.
- **Update Sales** is a manual entry by Staff/Admin matched on representative, hospital,
  doctor, pharmacy, and product.
- Only Representatives (and Admins) may log meetings; only Staff (and Admins) may update
  sales.

---

## 4. Data Architecture

### 4.1 Persistence

- **Relational database**: SQLite (dev) / MySQL 8 (prod)
- **Foreign keys** with proper `on_delete` semantics (`PROTECT` for reference data,
  `SET_NULL` for optional links)
- **Strategic denormalisation** only where dashboards need it (e.g. cached totals)
- **JSON fields** sparingly, for flexible metadata only - not for queryable core data
- **Audit logging** for significant actions via `core.AuditLog`

### 4.2 Indexing

- Index foreign keys used in list filters (`rep`, `hospital`, `doctor`, `pharmacy`,
  `product`, `period`)
- Composite indexes for meeting/attendance lookup: `(rep, date)` and
  `(hospital, date)`; `(user, date)` for attendance
- Index target/sales period fields used by attainment queries

### 4.3 Data Volume

At under 100 users the expected volume is modest:

| Entity | Rough annual scale |
|--------|--------------------|
| Visits | tens of thousands |
| Sales lines | tens of thousands |
| Outlets | low thousands |
| Products | hundreds |

This comfortably fits a single MySQL instance; no sharding or caching layer needed.

---

## 5. Frontend Architecture

### 5.1 Progressive Enhancement

- **Server-rendered templates** for all core functionality
- **HTMX** for partial updates (tabs, filters, inline lists) without full reloads
- **Mobile-first** responsive layouts; field screens optimised for touch
- **No SPA framework** - the complexity budget does not justify it

### 5.2 UI Component Architecture

- **Template inheritance**: everything extends `base.html` (two-row shell)
- **Reusable partials**: `templates/<app>/partials/*.html`
- **Design tokens**: `static/css/theme.css` (CSS variables) + `olive-theme.css`
- **KPI cards**: shared `.kpi-card` pattern with a vertical accent bar
- **Charts**: Chart.js rendered from server-provided JSON

### 5.3 Two-Row Shell Layout

- **Row 1** (~56px): utility bar - brand, search, user menu
- **Row 2** (~48px): module navigation ribbon
- **Mobile**: collapses to a hamburger menu

### 5.4 Theme: "Trusted Innovator"

| Role | Token | Hex |
|------|-------|-----|
| Primary action | `--color-primary` | `#008080` |
| Navigation | `--color-nav` | `#003566` |
| Background | `--color-bg` | `#F8F9FA` |
| Surface | `--color-surface` | `#FFFFFF` |
| Border | `--color-border` | `#E9ECEF` |
| Success | `--color-success` | `#10b981` |
| Danger | `--color-danger` | `#c2412c` |
| Warning | `--color-warning` | `#f59e0b` |

Colours are defined once in `theme.css`; templates and components reference the
variables, never raw hex values.

### 5.5 HTMX Patterns

Tab switching and the non-HTMX redirect fallback:

```html
<a hx-get="{% url 'reporting:monthly' %}?period={{ period }}"
   hx-target="#report-content"
   class="nav-link">Monthly</a>
```

```python
class MonthlyReportView(LoginRequiredMixin, View):
    def get(self, request):
        if not request.headers.get("HX-Request"):
            return redirect(f"{reverse('reporting:index')}?tab=monthly")
        # ... render partial
```

---

## 6. Security Architecture

### 6.1 Built-in Protections

- **CSRF**: Django CSRF middleware enabled on all state-changing requests
- **XSS**: automatic template escaping; no `|safe` on user input
- **SQL injection**: ORM-only query construction
- **Clickjacking**: `XFrameOptionsMiddleware`
- **HTTPS / secure cookies**: enforced in production settings

### 6.2 Access Control

Three roles, enforced server-side:

| Role | Sees | Can do |
|------|------|--------|
| Representative | Own activity and reports | Meet Doctor, Meet Chemist, check in/out |
| Staff | Own attendance and sales reports | Check in/out, update sales |
| Admin | All data | Everything: manage users/masters, view all reports |

- Authentication: Django Auth (sessions for web, tokens for the API)
- Authorisation: role checks in views, querysets, and DRF permissions
- Object permissions: representatives/staff can only read/write their own records

### 6.3 Activity Data Handling

- No GPS or location data exists to protect - check-in/out is time-based only.
- Attendance and activity records are visible only to their owner unless the user is an
  Admin.
- Admin corrections to attendance are recorded in the audit log.
- Aggregated reports never expose another user's individual records to non-admins.

---

## 7. Deployment Architecture

### 7.1 Runtime

- **Gunicorn** serving the WSGI app
- **MySQL 8** in production (SQLite in development)
- **Static files** collected via `collectstatic` and served by the web server/CDN
- **Environment-based config** through `django-environ` (`.env` locally)

### 7.2 Settings Split

```
settings/
├── base.py          # shared configuration and INSTALLED_APPS
├── dev.py           # DEBUG=True, console email, ALLOWED_HOSTS=["*"]
└── production.py    # DEBUG=False, secure cookies, HSTS, real hosts
```

### 7.3 Containerisation

- Docker image builds from `requirements.txt`
- `collectstatic` at build time
- `migrate` then `gunicorn olivepharma.wsgi:application` at runtime
- No Celery/Redis workers required in the MVP

---

## 8. Scalability & Why This Fits OlivePharma

| Challenge | Architectural Response |
|-----------|------------------------|
| Small team, fast delivery | Modular monolith - one codebase, one deploy |
| Field reps on phones | Mobile-first templates + HTMX (+ optional DRF API) |
| Time-based attendance | Server timestamps + one open log per user |
| Doctor/chemist activity | Master data + meeting link models |
| Manual sales from accounting | Validated sales entry matched on rep/hospital/doctor/pharmacy/product |
| Admin oversight | Role-based querysets (own data vs all data) |
| Fast reporting | Indexed queries + CSV export + Chart.js |
| Keeping it simple | Explicit complexity budget in `ai_context.md` |

---

## 9. Explicitly Out of Scope

The following are intentionally excluded until a new decision record justifies them:

- Wagtail CMS / public content pages
- Celery / Redis / background workers
- AI scoring or recommendations
- Multi-tenancy
- Microservices or service mesh
- Real-time websockets
- Native mobile app (responsive web + API is sufficient)
- **GPS / geolocation / geofencing**
- Invoicing/accounting integration (manual entry only)
