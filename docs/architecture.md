# Architecture Overview

OlivePharma implements a **modular monolith** architecture tuned for a small internal
audience (under 100 users). It prioritises clarity, fast iteration, and a mobile-first
field workflow over distributed-systems complexity.

---

## 1. Core Architectural Patterns

### 1.1 Modular Monolith (Primary Pattern)

The application is a single deployable Django project divided into independent,
loosely-coupled apps, each representing a bounded context:

```
olivepharma/
├── core/          # Shared base models, dashboard, profile, settings
├── accounts/      # Users, roles, rep profiles, territories
├── outlets/       # Doctors, pharmacies, hospitals/facilities
├── products/      # Product catalog and categories
├── activities/    # Check-in/out, visits, field activity
├── sales/         # Orders, sales records, targets
├── reporting/     # Dashboards, reports, CSV export
└── api/           # REST API (DRF) for the mobile client
```

**Benefits**

- One codebase, one deploy - easy to run and reason about at this scale
- Clear boundaries so features do not bleed into each other
- Can be split later only if genuinely needed (it is not, at under 100 users)
- Multiple developers can work on separate apps with minimal conflict

### 1.2 Model-View-Template (MVT) with HTMX Enhancement

Follows Django's native architecture with progressive frontend enhancement:

- **Models**: data structure and invariants (`activities/models.py`)
- **Views**: request handling and data retrieval (`activities/views.py`)
- **Templates**: presentation (`templates/activities/visit_list.html`)
- **HTMX**: partial updates for an SPA-like feel while keeping MVT simplicity

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
    actual = SalesRecord.objects.filter(rep=rep, period=period).aggregate(...)
    return {...}
```

**Benefits**: testable business logic, thin models/views, clear ownership.

### 1.5 RESTful API Layer

A Django REST Framework API serves the mobile client:

- Token authentication for the app
- Session authentication for the browsable API
- ViewSets per resource, with object-level permissions
- Idempotent check-in endpoints to support offline retries

---

## 2. Domain Model

### 2.1 Bounded Contexts

| App | Responsibility | Key Models |
|-----|----------------|-----------|
| `core` | Shared foundations | `TimeStampedModel`, `AuditLog` |
| `accounts` | People & hierarchy | `RepProfile`, `Territory` |
| `outlets` | Places reps visit | `Outlet`, `Doctor`, `Pharmacy` |
| `products` | What reps sell | `Category`, `Product` |
| `activities` | What reps do | `Visit`, `VisitProduct`, `ActivityType` |
| `sales` | Outcomes | `SalesRecord`, `SalesLine`, `Target` |
| `reporting` | Insight | (aggregations over other apps) |
| `api` | Mobile access | Serializers, ViewSets |

### 2.2 Entity Relationships

```
User 1--1 RepProfile *--1 Territory
RepProfile (*--1 User)         # manager relationship (self FK on RepProfile)
Territory 1--* Outlet
Outlet 1--* Doctor / Pharmacy
Visit *--1 RepProfile
Visit *--1 Outlet
Visit 1--* VisitProduct *--1 Product
SalesRecord *--1 RepProfile
SalesRecord *--1 Outlet
SalesRecord 1--* SalesLine *--1 Product
Target *--1 RepProfile
Target *--1 Product
```

### 2.3 Conventions

- All domain models inherit `core.models.TimeStampedModel`.
- Every foreign key has an explicit `related_name`.
- Choice lists are module-level constants in `SCREAMING_SNAKE_CASE`.
- `Meta.indexes` are added for fields used in list filters and dashboards.
- `Meta.ordering` is set where a stable default order matters.
- Money uses `DecimalField(max_digits=15, decimal_places=2)`; never floats.
- Coordinates use `DecimalField(max_digits=9, decimal_places=6)` for latitude and
  longitude (portable across SQLite and MySQL; no PostGIS dependency).

---

## 3. Field Workflow: Check-in / Check-out

The central flow is deliberately simple and resilient.

```
Rep opens My Day
      │
      ▼
Select outlet ──► Check in (capture GPS + timestamp)
      │                 │
      │                 ├─ online  ──► POST /activities/check-in/ ──► Visit(open)
      │                 └─ offline ──► queue locally ──► sync later (idempotent)
      ▼
Log visit: purpose, notes, products, samples
      │
      ▼
Check out ──► Visit(closed), duration computed
      │
      ▼
Appears in My Day, manager views, and reports
```

**Design rules**

- Check-in is timestamped **server-side**; the client time is stored as a hint only.
- GPS is optional: if unavailable, the visit is still valid but flagged `gps_missing`.
- Geofence matching is advisory, not blocking - field conditions vary.
- The check-in endpoint is idempotent on a client-supplied `client_uuid` so offline
  retries cannot create duplicates.
- A rep may have at most one open visit at a time (enforced in the service layer).

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

- Index foreign keys used in list filters (`rep`, `outlet`, `product`, `period`)
- Composite index on visit lookup: `(rep, check_in_at)` and `(outlet, check_in_at)`
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
<a hx-get="{% url 'reporting:activity' %}?period={{ period }}"
   hx-target="#report-content"
   class="nav-link">Activity</a>
```

```python
class ActivityReportView(LoginRequiredMixin, View):
    def get(self, request):
        if not request.headers.get("HX-Request"):
            return redirect(f"{reverse('reporting:index')}?tab=activity")
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
| Rep | Own visits, sales, targets | Check in/out, log visits and sales |
| Manager | Their team's data | Rep duties + review team reports |
| Admin | All data | Manage users, outlets, products, targets |

- Authentication: Django Auth (sessions for web, tokens for the API)
- Authorisation: role checks in views, querysets, and DRF permissions
- Object permissions: a rep can only read/write their own records

### 6.3 Privacy of Field Data

GPS coordinates are personal data:

- Only the owning rep and their manager chain may see precise coordinates
- Aggregated reports may show counts/areas, not individual traces
- Coordinates are stored with accuracy and source metadata

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
| Field reps on phones | Mobile-first templates + HTMX + DRF token API |
| Intermittent connectivity | Offline queue + idempotent check-in endpoint |
| Proof-of-visit needs | Server timestamps + optional GPS/geofence |
| Manager oversight | Role-based querysets scoped by territory/team |
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
