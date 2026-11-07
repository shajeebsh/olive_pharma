# OlivePharma - Project Context Documentation

> **Last Updated**: November 2026  
> **Status**: Greenfield - docs foundation and field-activity spec complete, implementation not started  
> **Maintained by**: Development Team

> **Current state**: This repository currently contains documentation only. The
> `olivepharma/` application package, models, views, and templates described below are
> the agreed target architecture and have not been implemented yet. Begin with
> [plan.md](plan.md) Phase 0.

---

## 1. Project Overview

**OlivePharma** is a field activity and sales tracking application for a pharmaceutical
company that acquires/manufactures medicines in bulk and supplies them to pharmacies. The
company employs a large number of medical representatives (MRs), and the application's
main purpose is to **log the daily activity of each worker**.

It covers doctor meetings, chemist/pharmacy meetings, manual sales updates sourced from
an external accounting system, time-based check-in/check-out (no GPS), and dashboards
with monthly, representative-wise, and hospital-wise reporting.

### Scope & Constraints

| Constraint | Value |
|-----------|-------|
| Target users | Under 100 users |
| Deployment | Single organisation, single deployable unit |
| Primary device | Mobile-first (reps work in the field) |
| Secondary device | Desktop/tablet (staff and admins) |
| Check-in/out | Time-based log only - **no GPS/location capture** |
| Complexity budget | Small: prefer boring, proven patterns over distributed systems |

> **Guiding principle**: This is a small internal application. Optimise for clarity,
> fast iteration, and maintainability over enterprise-scale infrastructure.

### Technology Stack

| Layer | Technology | Version |
|-------|-----------|---------|
| Backend | Django | 5.0.x |
| REST API | Django REST Framework | 3.14+ |
| Database | SQLite (dev) / MySQL 8 (prod) | — |
| DB driver | PyMySQL (MySQL DB-API shim) | 1.1+ |
| Config | django-environ | 0.11+ |
| Frontend | Django Templates, Bootstrap 5.3, HTMX | — |
| Charts | Chart.js | 4.x |
| Icons / Font | Bootstrap Icons, Inter (Google Fonts) | — |
| Authentication | Django Auth (sessions for web, tokens for mobile) | — |
| App server | Gunicorn | 21+ |

### Deliberate Omissions (vs. OliveCRM)

OlivePharma intentionally does **not** include the following at this stage:

| Omitted | Why |
|---------|-----|
| Wagtail CMS | No public content-marketing requirement |
| Celery + Redis | Workload is small; synchronous exports are sufficient |
| OpenAI integration | No AI features in the MVP |
| Multi-tenancy | Single organisation, under 100 users |
| Microservices | Modular monolith is simpler and sufficient |

If any of these becomes necessary, record the decision in Section 6 before adding it.

---

## 2. Project Structure

```
olive_pharma/
├── manage.py                 # Django management script
├── requirements.txt          # Python dependencies
├── db.sqlite3                # Development database (git-ignored)
├── .env                      # Local environment variables (git-ignored)
├── Dockerfile                # Container build (production)
│
├── docs/                     # Documentation (this folder)
│   ├── ai_context.md         # Canonical project context (this file)
│   ├── plan.md               # Build plan and milestones
│   ├── architecture.md       # Detailed architecture
│   ├── field-activity.md     # Daily field activity feature specification
│   ├── setup.md              # Setup and installation
│   ├── testing.md            # Testing and QA
│   └── api.md                # REST API documentation
│
└── olivepharma/              # Main project package
    ├── settings/             # Django settings split
    │   ├── base.py           # Shared settings
    │   ├── dev.py            # Development overrides
    │   └── production.py     # Production overrides
    ├── urls.py               # Root URL routing
    ├── wsgi.py               # WSGI config
    ├── asgi.py               # ASGI config
    │
    ├── core/                 # Shared base models, dashboard, profile, settings
    ├── accounts/             # Users, roles, rep profiles, territories
    ├── outlets/              # Doctors (HCPs), pharmacies, hospitals/facilities
    ├── products/             # Product catalog and categories
    ├── activities/           # Check-in/out, visits, field day, activity log
    ├── sales/                # Orders, sales records, targets
    ├── reporting/            # Reports, dashboards, CSV export
    ├── api/                  # REST API (DRF)
    │
    ├── static/               # CSS, JS, images
    │   ├── css/
    │   │   ├── theme.css         # "Trusted Innovator" design tokens
    │   │   ├── olive-theme.css   # Component styles
    │   │   └── index.css         # Utility styles
    │   └── js/
    │
    └── templates/            # Django templates
        ├── base.html         # Two-row shell layout
        ├── core/             # Dashboard, profile, settings
        ├── accounts/         # Rep list/detail/forms
        ├── outlets/          # HCP/pharmacy list/detail/forms
        ├── products/         # Product list/detail/forms
        ├── activities/       # Meet Doctor, Meet Chemist, check-in/out, attendance
        ├── sales/            # Orders, targets
        └── reporting/        # Reports with HTMX partials
```

---

## 3. URL Routing

| Path | App | Purpose |
|------|-----|---------|
| `/` | core | Dashboard (`dashboard`) |
| `/accounts/` | django.contrib.auth | Login/logout |
| `/django-admin/` | admin | Django admin |
| `/profile/` | core | User profile |
| `/settings/` | core:settings | Settings pages |
| `/reps/` | accounts | Rep list, detail, targets |
| `/outlets/` | outlets | States, hospitals, doctors, pharmacies |
| `/products/` | products | Product catalog |
| `/activities/` | activities | Meet Doctor, Meet Chemist, check-in/out, attendance |
| `/sales/` | sales | Manual sales entry and targets |
| `/reports/` | reporting | Reports (index, monthly, representatives, hospitals) |
| `/api/` | api | REST API endpoints for the mobile app |

### Namespace Usage

- Use `reporting:index`, `reporting:monthly`, `reporting:representatives`, etc.
- Use `activities:meet_doctor`, `activities:meet_chemist`, `activities:check_in`,
  `activities:check_out`, `activities:attendance`
- Use `outlets:state_list`, `outlets:hospital_list`, `outlets:doctor_list`,
  `outlets:pharmacy_list`
- Use `sales:entry_list`, `sales:entry_create`, `sales:target_list`
- Use `core:settings` for settings pages

---

## 4. Key Features

### 4.1 Dashboard
- KPI cards with vertical-accent styling (doctor meetings, chemist meetings, check-ins,
  sales amount)
- Recent activity table (doctor and chemist meetings)
- Monthly and month-over-month trends
- Representative-wise and hospital-wise breakdowns
- Filters: date range/month, representative, state, hospital, product

### 4.2 Check-in / Check-out
- **Time-based log only - no GPS or location capture**
- User clicks Check In/Check Out; the server records timestamps
- Duration computed on check-out
- One open check-in per user at a time
- Attendance history and reports per user

### 4.3 Field Activity Tracking
- **Meet Doctor**: log state, hospital, doctor, date, and products introduced
- **Meet Chemist**: log the pharmacy near the doctor's locality, current products, and
  the products the pharmacy needs
- Activity list per representative and per day
- Admin can review all activity; users see their own

### 4.4 Sales & Targets
- **Update Sales**: manual entry of accounting data, matched by representative,
  hospital, doctor, pharmacy, and product
- Product catalog and categories
- Monthly/quarterly targets per rep and product
- Actual vs. target progress

### 4.5 Reporting Module
- HTMX-powered tab switching (Monthly, Representatives, Hospitals, Products)
- Monthly reports, trends, representative-wise and hospital-wise data
- Filters shared across tabs (date range, rep, state, hospital, product)
- CSV export with filtering
- Direct URL access redirects to the full index page
- Chart.js visualisation

### 4.6 "Trusted Innovator" Theme

| Role | Color | Hex |
|------|-------|-----|
| Primary Action | Deep Teal | `#008080` |
| Navigation | Dark Indigo | `#003566` |
| Background | Cloud Dancer | `#F8F9FA` |
| Card Border | Subtle Gray | `#E9ECEF` |
| Success | Emerald | `#10b981` |
| Danger | Terracotta | `#c2412c` |
| Warning | Amber | `#f59e0b` |

---

## 5. Conventions

### 5.1 Project & Code Layout
- One Django app per **bounded context** under `olivepharma/`.
- Apps are lowercase, plural where it reads naturally (`outlets`, `products`, `activities`, `sales`).
- Every app owns its `models.py`, `views.py`, `urls.py`, `forms.py`, `admin.py`, `tests.py`.
- Complex business logic goes in a `services.py` module inside the owning app; keep models and views thin.
- Templates live under `olivepharma/templates/<app>/`; report fragments under `<app>/partials/`.

### 5.2 Models
- Shared base model is `olivepharma.core.models.TimeStampedModel` (`created_at`, `updated_at`).
- Use `models.BigAutoField` (`DEFAULT_AUTO_FIELD`); do not change it.
- Use `related_name` on every non-trivial FK.
- Use `choices` lists at module level in `SCREAMING_SNAKE_CASE`.
- Add `Meta.indexes` for fields used in list filters and dashboards.
- `__str__` must return a human-readable label for every model.

### 5.3 Views
- Class-based views (`ListView`, `DetailView`, `CreateView`, `UpdateView`, `DeleteView`) for CRUD.
- Function views or thin `TemplateView`s for dashboards.
- Use `LoginRequiredMixin` / `@login_required` on all non-public views.
- HTMX fragments: check `request.headers.get("HX-Request")`, otherwise redirect to the full page.

### 5.4 URLs
- Declare `app_name` in every app `urls.py`.
- Include app URLs with an explicit namespace where required.
- URL names are `snake_case` (`visit_list`, `check_in`, `order_create`).

### 5.5 Templates & Frontend
- All pages extend `base.html` (two-row shell layout).
- Use Bootstrap 5 classes and the existing `.kpi-card` pattern for dashboards.
- Use HTMX for partial updates; do not introduce a SPA framework.
- Theme colours come from CSS variables in `theme.css`; never hard-code hex values in templates.
- Mobile-first: field screens must be usable on small touch screens.

### 5.6 Security
- CSRF protection stays enabled; never use `@csrf_exempt` without documented reason.
- Role checks are enforced server-side, not only by hiding UI.
- **No GPS or location data is collected, requested, or stored anywhere.**
- Activity and attendance records are visible only to their owner unless the user is an Admin.
- Never commit `.env`, secrets, database files, or credentials.

### 5.7 Testing
- Every app has tests in `tests.py` (or a `tests/` package as it grows).
- Test models, permissions, and critical flows (doctor/chemist meetings, sales entry,
  check-in/out, reports).
- Run `python manage.py test` and `python manage.py check` before committing.

---

## 6. Decisions (Architecture Decision Records)

| # | Decision | Rationale |
|---|----------|-----------|
| D1 | Modular monolith (single Django project) | Under 100 users; avoids distributed-systems overhead |
| D2 | Django templates + HTMX, no SPA | Fast to build, server-rendered, low JS complexity |
| D3 | Bootstrap 5 + shared theme tokens | Matches OliveCRM design system for consistency |
| D4 | SQLite for dev, MySQL for production | Zero-setup dev; production parity via PyMySQL |
| D5 | No Wagtail CMS | No public-content requirement |
| D6 | No Celery/Redis in MVP | Exports and dashboards are synchronous at this scale |
| D7 | DRF token API for mobile | A thin mobile client may be added; tokens are simple |
| D8 | Role-based access (Admin, Representative, Staff) | Matches the operational roles; enforced server-side |
| D9 | Check-in/out is a time-based log only (no GPS) | Spec requires time logs, not location; avoids privacy complexity |
| D10 | `TimeStampedModel` for shared timestamps | Consistency across all domain models |
| D11 | Sales are entered manually from the external accounting app | Accounting is out of scope; staff match rep/hospital/doctor/pharmacy/product |

---

## 7. What Must Not Change

The following are foundational and must not be changed without an explicit,
documented decision:

1. **Stack**: Django 5.0.x, Bootstrap 5, HTMX, Chart.js, DRF, SQLite/MySQL.
2. **Project layout**: `olivepharma/` package with one app per bounded context.
3. **Base model contract**: `TimeStampedModel` remains the shared timestamp base.
4. **Design system**: "Trusted Innovator" colour tokens and the two-row shell layout.
5. **URL namespaces**: existing `app_name` values and named routes.
6. **Auth model**: Django's built-in user plus role/profile extension (no custom user swap).
7. **Role model**: Admin, Representative, and Staff with the permissions in
   [field-activity.md](field-activity.md#6-permissions-matrix).
8. **No GPS/location capture**: check-in/check-out is a time-based log only.
9. **Complexity budget**: do not introduce Wagtail, Celery, Redis, microservices,
   or multi-tenancy without a new ADR in Section 6.
10. **Data ownership**: representatives and staff see their own data; admins see all.
11. **No secrets in the repository**: `.env`, credentials, and DB files stay out of git.

---

## 8. Development Commands

```bash
# Run the development server
python manage.py runserver

# Django system checks
python manage.py check

# Apply migrations
python manage.py migrate

# Create migrations after model changes
python manage.py makemigrations

# Run tests
python manage.py test
```

---

## 9. Related Documentation

- [Build Plan](plan.md) - Phased delivery plan and milestones
- [Architecture Overview](architecture.md) - Detailed architectural patterns
- [Field Activity Feature](field-activity.md) - Daily activity, roles, and permissions
- [Setup and Installation](setup.md) - Getting started guide
- [Testing and QA](testing.md) - Automated and E2E testing
- [REST API Documentation](api.md) - API endpoints and usage
- `olivepharma/static/css/theme.css` - Design tokens
- `olivepharma/templates/base.html` - Shell layout

---

## 10. Notes for New Team Members

1. Start with [plan.md](plan.md) to see what is being built and in what order.
2. Read [architecture.md](architecture.md) before adding a new app or integration.
3. Follow the conventions in Section 5; consistency matters more than cleverness.
4. This project is intentionally small - resist enterprise patterns until they are needed.
5. Keep this file updated whenever architecture, stack, or a foundational decision changes.

---

## 11. Change Log

### November 2026 - Field Activity Feature Specification
- Added `docs/field-activity.md`: Meet Doctor, Meet Chemist, Update Sales,
  time-only Check-In/Check-Out, dashboards, and the Admin/Representative/Staff
  permission model.
- Reconciled the canonical context with the feature spec:
  - Check-in/out is **time-based only** (removed GPS/geofence); decision D9 updated.
  - Roles are **Admin, Representative, Staff** (replaced the earlier manager/rep model);
    decision D8 updated.
  - Sales are **manually entered** from the external accounting application; decision
    D11 added.
  - Dashboard/reporting adjusted to monthly, representative-wise, and hospital-wise views.
- **Task checkpoint (end)**: feature specification complete; application code not started.

### November 2026 - Documentation Foundation
- Created `docs/ai_context.md`, `docs/plan.md`, `docs/architecture.md`.
- Mirrored OliveCRM documentation structure and the "Trusted Innovator" design system.
- Defined domain bounded contexts: core, accounts, outlets, products, activities, sales, reporting, api.
- Recorded initial architecture decisions (D1-D10) and the "must not change" list.
- Added `docs/setup.md`, `docs/testing.md`, `docs/api.md` and updated `README.md` to
  match the OliveCRM documentation style.
- **Task checkpoint (end)**: documentation foundation is complete and internally
  consistent; no application code has been written yet. Next step is Phase 0 in
  [plan.md](plan.md).

---

*This document is a live reference. Append new changes above with date and description.*
