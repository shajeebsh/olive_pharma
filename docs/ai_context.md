# OlivePharma - Project Context Documentation

> **Last Updated**: November 2026
> **Status**: Implementation complete for Phases 0-6 (foundation, roles, masters,
> field activity, sales/targets, dashboards/reports). Optional API and hardening next.
> **Maintained by**: Development Team

> **Current state**: The Django application is implemented and runnable. Documentation
> below reflects the code in this repository, not a future target.

---

## 1. Project Overview

**OlivePharma** is a field activity and sales tracking application for a pharmaceutical
company that acquires/manufactures medicines in bulk and supplies them to pharmacies. The
company employs medical representatives (MRs), and the application's main purpose is to
**log the daily activity of each worker**.

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
| CMS | Wagtail (optional pages) | 6.0.x |
| Database | SQLite (dev) / PostgreSQL (prod) | — |
| DB driver | psycopg2-binary + dj-database-url | 2.9 / 2.1 |
| Config | python-decouple | 3.8+ |
| Sample data | Faker (admin seeding tool) | 25+ |
| Frontend | Django Templates, Bootstrap 5.3, Chart.js | — |
| Icons / Font | Bootstrap Icons, Inter (Google Fonts) | — |
| Authentication | Django Auth (session-based) | — |
| App server | Gunicorn + WhiteNoise | 21+ / 6.6+ |
| Deployment | Render Blueprint (`render.yaml`) | — |
| PDF (future) | WeasyPrint | 61+ |

### Deliberate Omissions

| Omitted | Why |
|---------|-----|
| Django REST Framework / API | The responsive web app covers the field workflow; the API remains optional future work |
| Celery + Redis | Workload is small; synchronous exports are sufficient |
| OpenAI integration | No AI features in the MVP |
| Multi-tenancy | Single organisation, under 100 users |
| Microservices | Modular monolith is simpler and sufficient |
| HTMX / SPA framework | Server-rendered tabs and forms are sufficient at this scale |

Wagtail **is** included, but only for optional CMS pages under `/cms/`; it is not part of
the core field workflow. If any omission becomes necessary, record the decision in
Section 6 before adding it.

---

## 2. Project Structure

```
olive_pharma/
├── manage.py                 # Django management script (config.settings.dev)
├── requirements.txt          # Python dependencies
├── render.yaml               # Render Blueprint (web service + PostgreSQL)
├── build.sh                  # Render build: install, collectstatic, migrate, superuser
├── start.sh                  # Render start: migrate, superuser, collectstatic, gunicorn
├── .python-version           # Pins Render to Python 3.11.11
├── .env.example              # Environment template (no secrets)
├── db.sqlite3                # Development database (git-ignored)
│
├── config/                   # Project package
│   ├── settings/
│   │   ├── base.py           # Shared settings
│   │   ├── dev.py            # Development overrides
│   │   └── prod.py           # Production overrides
│   ├── urls.py               # Root URL routing
│   ├── wsgi.py               # WSGI config (config.settings.prod)
│   └── asgi.py               # ASGI config (config.settings.dev)
│
├── core/                     # Shared masters, managers, audit, navigation, health
│   ├── models.py             # TimeStampedModel, AuditLog, Region, Hospital, Doctor,
│   │                         # Pharmacy, Product
│   ├── managers.py           # ScopedQuerySet/ScopedManager, get_user_role
│   ├── permissions.py        # role_required, RoleRequiredMixin
│   ├── navigation.py         # NAV_REGISTRY + nav_for_role
│   ├── context_processors.py # NAV_ITEMS + USER_ROLE
│   ├── middleware.py         # RoleAccessMiddleware (path-level role checks)
│   ├── bootstrap.py          # WSGI startup migrate + ensure_superuser safety net
│   ├── admin_views.py        # DB profiling + sample-seed admin views
│   ├── services/profiling.py # Project table row counts + latest timestamps
│   ├── services/seeding.py   # Faker-based sample row generators
│   ├── management/commands/seed_demo.py
│   ├── management/commands/seed_table.py
│   └── views.py              # health (DB + migrations), help redirect
│
├── accounts/                 # UserProfile (roles), profile view, signals
├── visits/                   # DoctorVisit, ChemistVisit, services, signals, receivers
├── sales/                    # SalesLog, Target, services, signals, receivers
├── checkin/                  # CheckInOut, check-in/out services and views
├── dashboard/                # KPIs, filters, reports, charts, CSV export
│   └── templatetags/         # get_item filter for report rows
├── cms/                      # Optional Wagtail pages + snippet
│
├── static/
│   ├── css/theme.css         # "Trusted Innovator" design tokens + components
│   └── js/navigation.js      # User menu, mobile nav, active-link state
│
└── templates/
    ├── base.html             # Two-row shell layout
    ├── partials/             # form_fields, pagination
    ├── registration/         # login, logged_out
    ├── dashboard/            # home, reports, _filters, _kpi_card
    ├── visits/               # doctor_list/form, chemist_list/form
    ├── sales/                # list/form, target_list/form
    ├── checkin/              # list, check_in, check_out
    ├── accounts/             # profile
    ├── admin/                # Django admin index override + DB profiling page
    ├── cms/                  # Wagtail page templates
    └── help.html
```

---

## 3. URL Routing

| Path | App | Purpose |
|------|-----|---------|
| `/` | dashboard | Dashboard (`dashboard:home`) |
| `/reports/` | dashboard | Reports with tabs (`dashboard:reports`) |
| `/reports/export/` | dashboard | CSV export (`dashboard:export`) |
| `/accounts/` | django.contrib.auth | Login/logout |
| `/profile/` | accounts | User profile (`accounts:profile`) |
| `/django-admin/` | admin | Django admin |
| `/django-admin/db-profiling/` | core | DB profiling page (`admin_db_profiling`) |
| `/django-admin/db-profiling/seed/` | core | Seed sample rows (`admin_db_profiling_seed`) |
| `/cms/` | wagtail.admin | Wagtail CMS admin |
| `/visits/filter-options/` | visits | Dependent-dropdown JSON (`filter_options`) |
| `/visits/doctor/` | visits | Meet Doctor list/create (`doctor_list`, `doctor_create`) |
| `/visits/chemist/` | visits | Meet Chemist list/create (`chemist_list`, `chemist_create`) |
| `/sales/` | sales | Sales list/create (`list`, `create`) |
| `/sales/targets/` | sales | Targets list/create (`target_list`, `target_create`) |
| `/checkin/` | checkin | Attendance list + check in/out (`list`, `check_in`, `check_out`) |
| `/health/` | core | Health check JSON |
| `/help/` | core | Help page |
| `/` (fallback) | wagtail | Optional CMS page serving |

### Namespace Usage

- `dashboard:home`, `dashboard:reports`, `dashboard:export`
- `visits:doctor_list`, `visits:doctor_create`, `visits:chemist_list`,
  `visits:chemist_create`, `visits:filter_options`
- `admin_db_profiling`, `admin_db_profiling_seed`
- `admin:db_profiling`, `admin:db_profiling_seed` (Region admin mount)
- `sales:list`, `sales:create`, `sales:target_list`, `sales:target_create`
- `checkin:list`, `checkin:check_in`, `checkin:check_out`
- `accounts:profile`
- Django auth names are unnamespaced: `login`, `logout`

---

## 4. Key Features

### 4.1 Dashboard
- KPI cards with vertical-accent styling (doctor visits, chemist visits, check-ins,
  sales amount)
- Recent activity table (doctor and chemist visits)
- Representative-wise and hospital-wise breakdown tables
- Filters: date range, representative (admin/staff), hospital, product
- Chart.js bar charts for representative- and hospital-wise sales

### 4.2 Check-in / Check-out
- **Time-based log only - no GPS or location capture**
- Server records date, check-in time, and check-out time
- Duration computed on check-out
- One check-in record per user per day (`unique_checkin_per_user_per_day`)
- Users see their own history; staff/admin use the dashboard for company-wide views

### 4.3 Field Activity Tracking
- **Meet Doctor**: log region, hospital, doctor, date, products introduced, notes
- **Meet Chemist**: log region, hospital, doctor context, pharmacy, current products,
  products needed, notes
- Service-layer creation (`log_doctor_visit`, `log_chemist_visit`) emits
  `doctor_visit_logged` / `chemist_visit_logged`
- Receivers write `AuditLog` rows
- Reps/admins access visit screens; reps are scoped to their own records
- Dependent dropdowns on both visit forms: hospital by region, doctor/pharmacy by
  hospital, served by `visits:filter_options`; child selects reset on parent change
- Future-date validation on doctor/chemist visit and sales forms; admins are exempt

### 4.4 Sales & Targets
- **Manual Sales**: staff/admin enter sales matched by representative, region, hospital,
  doctor, pharmacy, product, quantity, amount, and external reference
- `sales_logged` signal writes an audit entry
- Duplicate external reference per representative is rejected
- Monthly/quarterly `Target` records per rep and optional product
- `target_attainment()` service computes actual vs target amount/quantity and percentages

### 4.5 Reporting
- Server-rendered tabs: Monthly, Representatives, Hospitals, Products
- Filters shared across tabs: date range, representative, hospital, product
- CSV export per report honouring the active filters
- Chart.js visualisation for each tab
- Scoping via `ScopedManager.for_user`: reps see their own data; admin/staff company-wide

### 4.6 CMS (Optional)
- Wagtail `CMSHomePage` and `CMSPage` for optional public pages
- `SiteSetting` snippet
- Admin at `/cms/`; page serving falls back at the root after app URLs

### 4.7 DB Profiling and Sample Data
- Django admin index has a **Database tools → DB Profiling** link
- `/django-admin/db-profiling/` shows row count and latest timestamp per project model,
  skipping framework tables
- Inline seed form generates Faker-based sample rows for supported project models
- `python manage.py seed_table <app.Model> --rows <n>` provides the same seeding from
  the CLI

### 4.8 "Trusted Innovator" Theme

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
- One Django app per **bounded context** at the repository root.
- Every app owns its `models.py`, `views.py`, `urls.py`, `forms.py`, `admin.py`, `tests.py`.
- Complex business logic goes in a `services.py` module inside the owning app; keep models
  and views thin.
- Cross-module side effects use Django signals; receivers live in `receivers.py` and are
  imported from `AppConfig.ready()`.
- Templates live under `templates/<app>/`; shared fragments under `templates/partials/`.

### 5.2 Models
- Shared base model is `core.models.TimeStampedModel` (`created_at`, `updated_at`).
- Use `models.BigAutoField` (`DEFAULT_AUTO_FIELD`); do not change it.
- Use `related_name` on every non-trivial FK.
- Use `choices` lists at module level in `SCREAMING_SNAKE_CASE` (or class constants).
- Add `Meta.indexes` for fields used in list filters and dashboards.
- `__str__` must return a human-readable label for every model.

### 5.3 Views
- Class-based views (`ListView`, `CreateView`, `UpdateView`, `FormView`, `TemplateView`)
  for CRUD and dashboards.
- Use `RoleRequiredMixin` in views **and** `RoleAccessMiddleware` for path-level checks.
- Use `LoginRequiredMixin` / `@login_required` on all non-public views.
- Representatives are filtered through `ScopedManager.for_user`.

### 5.4 URLs
- Declare `app_name` in every app `urls.py`.
- URL names are `snake_case` (`doctor_list`, `check_in`, `target_create`).

### 5.5 Templates & Frontend
- All pages extend `base.html` (two-row shell layout).
- Use Bootstrap 5 classes and the `.kpi-card` pattern for dashboards.
- Theme colours come from CSS variables in `static/css/theme.css`; never hard-code hex
  values in templates.
- Mobile-first: field screens must be usable on small touch screens.

### 5.6 Security
- CSRF protection stays enabled; never use `@csrf_exempt` without documented reason.
- Role checks are enforced server-side, not only by hiding UI.
- **No GPS or location data is collected, requested, or stored anywhere.**
- Activity and attendance records are visible only to their owner unless the user is an
  admin (staff have company-wide sales/report visibility per the role matrix).
- Never commit `.env`, secrets, database files, or credentials.

### 5.7 Testing
- Every app has tests in `tests.py` (or a `tests/` package as it grows).
- Test models, permissions, and critical flows (visits, sales entry, check-in/out,
  targets, dashboard reports/CSV).
- Run `python manage.py test` and `python manage.py check` before committing.

---

## 6. Decisions (Architecture Decision Records)

| # | Decision | Rationale |
|---|----------|-----------|
| D1 | Modular monolith (single Django project) | Under 100 users; avoids distributed-systems overhead |
| D2 | Django templates + Bootstrap, no SPA | Fast to build, server-rendered, low JS complexity |
| D3 | Bootstrap 5 + shared theme tokens | Matches OliveCRM design system for consistency |
| D4 | SQLite for dev, PostgreSQL for production | Zero-setup dev; managed Postgres on Render via `DATABASE_URL` |
| D5 | Wagtail included for optional CMS pages only | Content pages may be useful; core workflow does not depend on it |
| D6 | No Celery/Redis in MVP | Exports and dashboards are synchronous at this scale |
| D7 | No DRF API in current build | The responsive web app covers the field workflow; API is optional future work |
| D8 | Role-based access (Admin, Representative, Staff) | Matches the operational roles; enforced server-side |
| D9 | Check-in/out is a time-based log only (no GPS) | Spec requires time logs, not location; avoids privacy complexity |
| D10 | `TimeStampedModel` for shared timestamps | Consistency across all domain models |
| D11 | Sales are entered manually from the external accounting app | Accounting is out of scope; staff match rep/hospital/doctor/pharmacy/product |
| D12 | Signals for cross-module audit logging | Keeps sales/visit views thin and side effects decoupled |
| D13 | Render Blueprint for deployment | Single web service + managed PostgreSQL, no container overhead |

---

## 7. What Must Not Change

The following are foundational and must not be changed without an explicit,
documented decision:

1. **Stack**: Django 5.0.x, Bootstrap 5, Chart.js, PostgreSQL production database.
2. **Project layout**: `config/` project package with one app per bounded context.
3. **Base model contract**: `TimeStampedModel` remains the shared timestamp base.
4. **Design system**: "Trusted Innovator" colour tokens and the two-row shell layout.
5. **URL namespaces**: existing `app_name` values and named routes.
6. **Auth model**: Django's built-in user plus `UserProfile` role extension (no custom
   user swap).
7. **Role model**: Admin, Representative, and Staff with the permissions in
   [field-activity.md](field-activity.md#6-permissions-matrix).
8. **No GPS/location capture**: check-in/check-out is a time-based log only.
9. **Complexity budget**: do not introduce Celery, Redis, microservices, or
   multi-tenancy without a new ADR in Section 6.
10. **Data ownership**: representatives see their own data; admins/staff see company-wide
    data; enforced server-side.
11. **No secrets in the repository**: `.env`, credentials, and DB files stay out of git.

---

## 8. Development Commands

```bash
# Activate the project virtualenv
source .venv/bin/activate

# Run the development server
python manage.py runserver

# Django system checks
python manage.py check

# Apply migrations
python manage.py migrate

# Create migrations after model changes
python manage.py makemigrations

# Provision the deployment admin from DJANGO_SUPERUSER_* env vars
python manage.py ensure_superuser

# Seed demo users and sample data
python manage.py seed_demo

# Seed Faker-based rows for a specific project model
python manage.py seed_table visits.DoctorVisit --rows 10

# Run tests
python manage.py test
```

Demo logins after `seed_demo`: `admin`, `rep`, `staff` / `password123`.

---

## 9. Related Documentation

- [Build Plan](plan.md) - Phased delivery plan and milestones
- [Architecture Overview](architecture.md) - Detailed architectural patterns
- [Field Activity Feature](field-activity.md) - Daily activity, roles, and permissions
- [Features by Menu](features.md) - Every implemented feature grouped by menu, route,
  role access, and known gaps
- [Setup and Installation](setup.md) - Local setup and Render deployment
- [Testing and QA](testing.md) - Automated and manual testing
- [REST API Documentation](api.md) - Optional future API notes
- `static/css/theme.css` - Design tokens and component styles
- `templates/base.html` - Two-row shell layout

---

## 10. Notes for New Team Members

1. Start with [plan.md](plan.md) to see what is being built and in what order.
2. Read [architecture.md](architecture.md) before adding a new app or integration.
3. Follow the conventions in Section 5; consistency matters more than cleverness.
4. This project is intentionally small - resist enterprise patterns until they are needed.
5. Keep this file updated whenever architecture, stack, or a foundational decision changes.

---

## 11. Change Log

### November 2026 - Dependent Dropdowns, Date Validation, DB Profiling
- Added `visits:filter_options` JSON endpoint and vanilla JS on the Meet Doctor and Meet
  Chemist forms so hospital options follow the region and doctor/pharmacy options follow
  the hospital; child selects reset when a parent changes.
- Added future-date validation to doctor visits, chemist visits and sales entries.
  Admins are exempt so they can correct or pre-enter records.
- Added `core.services.profiling.get_table_stats()` and the admin DB profiling page at
  `/django-admin/db-profiling/`, linked from the Django admin index. It lists row counts
  and latest timestamps for project models only.
- Added `core.services.seeding` plus `python manage.py seed_table` and the profiling
  page's inline seed form for Faker-based sample rows.
- Added `templates/admin/index.html` and `templates/admin/core/db_profiling.html`.
- Added `Faker` to `requirements.txt` and updated `docs/features.md`.

### November 2026 - Features by Menu Documentation
- Added `docs/features.md` documenting every implemented feature grouped by navigation
  menu: Dashboard, Reports, Meet Doctor, Meet Chemist, Sales (including Targets),
  Check In/Out, Help, user menu (Profile/Help/Logout), authentication, Django admin, and
  Wagtail CMS.
- Included role/menu visibility, routes, data scoping, form fields, validation, audit
  logging, CSV export, pagination, operational commands, a feature-to-code map, and
  known gaps where the implementation differs from the specification.

### November 2026 - Deployment Fixes
- Pinned Render to Python 3.11.11 via `PYTHON_VERSION` and `.python-version`
  (`pythonVersion` in `render.yaml` is not a Render setting). This avoids source builds
  for `pillow-heif`/Pillow on Python 3.14.
- Added `start.sh` so migrations and `collectstatic` run at boot before Gunicorn.
- Production now uses `whitenoise.storage.CompressedStaticFilesStorage` with
  `WHITENOISE_USE_FINDERS = True`, so missing `staticfiles/` output or manifest entries
  cannot cause a 500 on template render.
- Added `accounts.services.ensure_superuser_from_env()` and the
  `python manage.py ensure_superuser` command. It creates or updates an admin from
  `DJANGO_SUPERUSER_EMAIL` / `DJANGO_SUPERUSER_PASSWORD` (username = email) and sets
  `UserProfile.role = admin`.
- Provisioning runs from `build.sh`, `start.sh`, and a `post_migrate` receiver, so any
  successful migration also provisions the admin. Both variables are declared in
  `render.yaml` (`sync: false`) and `.env.example`.
- Expanded `docs/setup.md` with the full local/Render environment variable table, exact
  Render Build/Start commands, step-by-step `build.sh`/`start.sh` behavior, superuser
  provisioning/troubleshooting, and WhiteNoise static-file notes.
- Added `core.bootstrap.run_startup_tasks()`, called from `config/wsgi.py` under
  production settings (or when Render sets `RENDER=true`). It runs `migrate` and
  `ensure_superuser` once per container before the first request, so a stale Render
  Build/Start command cannot leave the database unmigrated (login 500) or the admin
  unprovisioned. `start.sh` sets `RUN_STARTUP_TASKS=0` after doing the work itself;
  `RUN_STARTUP_TASKS=1` enables it elsewhere.
- `/health/` now verifies the database connection and that `django_migrations` is
  populated, returning `503` with `"migrations": "missing"` instead of a false `ok`.
- The Render service deploys from the default `main` branch. Merge
  `feature/postgres-build` into `main` (or retarget Render) and deploy the latest commit
  before verifying fixes on the live URL; auto-deploy may be disabled.

### November 2026 - Implementation (Phases 0-6)
- Implemented Django project with `config.settings` split (base/dev/prod).
- Added `core` masters and infrastructure: `TimeStampedModel`, `AuditLog`, `Region`,
  `Hospital`, `Doctor`, `Pharmacy`, `Product`, scoped managers, role permissions,
  navigation registry, role middleware, health check.
- Added `accounts` roles (Admin/Representative/Staff) with auto-created profiles.
- Added `visits` (DoctorVisit, ChemistVisit) with services and audit signals.
- Added `sales` (SalesLog, Target) with duplicate-reference protection, `sales_logged`
  signal, and target attainment service.
- Added `checkin` (CheckInOut) with time-only check-in/out and one record per day.
- Added `dashboard` KPIs, shared filters, four report tabs, Chart.js, and CSV export.
- Added optional Wagtail `cms` pages and snippet.
- Added two-row Bootstrap shell, KPI cards, module templates, demo seed command, tests,
  `render.yaml`, `build.sh`, and `.env.example`.
- Reconciled this context with the implemented PostgreSQL/Wagtail build.

### November 2026 - Field Activity Feature Specification
- Added `docs/field-activity.md`: Meet Doctor, Meet Chemist, Update Sales,
  time-only Check-In/Check-Out, dashboards, and the Admin/Representative/Staff
  permission model.
- Reconciled the canonical context with the feature spec:
  - Check-in/out is **time-based only** (removed GPS/geofence); decision D9 updated.
  - Roles are **Admin, Representative, Staff**; decision D8 updated.
  - Sales are **manually entered** from the external accounting application; decision
    D11 added.
  - Dashboard/reporting adjusted to monthly, representative-wise, and hospital-wise views.

### November 2026 - Documentation Foundation
- Created `docs/ai_context.md`, `docs/plan.md`, `docs/architecture.md`.
- Mirrored OliveCRM documentation structure and the "Trusted Innovator" design system.
- Added `docs/setup.md`, `docs/testing.md`, `docs/api.md` and updated `README.md`.

---

*This document is a live reference. Append new changes above with date and description.*
