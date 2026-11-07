# OlivePharma - Project Context Documentation

> **Last Updated**: November 2026  
> **Status**: Greenfield - documentation foundation complete, implementation not started  
> **Maintained by**: Development Team

> **Current state**: This repository currently contains documentation only. The
> `olivepharma/` application package, models, views, and templates described below are
> the agreed target architecture and have not been implemented yet. Begin with
> [plan.md](plan.md) Phase 0.

---

## 1. Project Overview

**OlivePharma** is a field activity and sales tracking application for pharmaceutical
representatives (medical reps / MRs). It provides check-in/check-out at field locations,
visit and activity tracking, sales and target tracking, reporting, and dashboards.

### Scope & Constraints

| Constraint | Value |
|-----------|-------|
| Target users | Under 100 users |
| Deployment | Single organisation, single deployable unit |
| Primary device | Mobile-first (reps work in the field) |
| Secondary device | Desktop/tablet (managers and admins) |
| Offline tolerance | Visits captured on mobile may be queued and synced |
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
        ├── activities/       # Check-in/out, visit list/detail
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
| `/outlets/` | outlets | Doctors, pharmacies, facilities |
| `/products/` | products | Product catalog |
| `/activities/` | activities | Check-in/out, visits, field activity |
| `/sales/` | sales | Orders, sales records, targets |
| `/reports/` | reporting | Reports (index, activity, sales, targets) |
| `/api/` | api | REST API endpoints for the mobile app |

### Namespace Usage

- Use `reporting:index`, `reporting:activity`, etc. (namespace required)
- Use `activities:visit_list`, `activities:check_in`, etc.
- Use `outlets:outlet_list`, `outlets:doctor_list`, etc.
- Use `sales:order_list`, `sales:target_list`, etc.
- Use `core:settings` for settings pages

---

## 4. Key Features

### 4.1 Dashboard
- KPI cards with vertical-accent styling (visits today, active reps, sales MTD, target %)
- Recent visits table
- Sales vs. target progress
- Period filters (today, week, month, quarter)

### 4.2 Check-in / Check-out
- Rep checks in at an outlet (doctor, pharmacy, hospital) with GPS coordinates
- Server records timestamp, rep, outlet, and optional geofence match
- Notes, visit purpose, products discussed
- Check-out closes the visit and stores duration
- Offline queue on mobile syncs queued visits via the API

### 4.3 Field Activity Tracking
- Visit log per rep, per outlet, per day
- Activity types (visit, call, meeting, training, stock check)
- Managers can review team activity by territory and period

### 4.4 Sales & Targets
- Product catalog and categories
- Sales/order records tied to outlets and reps
- Monthly/quarterly targets per rep and product
- Actual vs. target progress

### 4.5 Reporting Module
- HTMX-powered tab switching (Activity, Sales, Targets, Reps)
- CSV export with date filtering
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
- GPS coordinates are personal data: expose them only to the owning rep and their manager chain.
- Never commit `.env`, secrets, database files, or credentials.

### 5.7 Testing
- Every app has tests in `tests.py` (or a `tests/` package as it grows).
- Test models, permissions, and critical flows (check-in/out, targets, reports).
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
| D7 | DRF token API for mobile | Reps need a thin mobile client; tokens are simple |
| D8 | Role-based access (admin, manager, rep) | Matches the pharma field hierarchy; simpler than per-module toggles |
| D9 | GPS captured on check-in, geofence optional | Proof of visit; allows tolerant matching without blocking offline work |
| D10 | `TimeStampedModel` for shared timestamps | Consistency across all domain models |

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
7. **Complexity budget**: do not introduce Wagtail, Celery, Redis, microservices,
   or multi-tenancy without a new ADR in Section 6.
8. **Data ownership**: reps see their own data; managers see their team; admins see all.
9. **No secrets in the repository**: `.env`, credentials, and DB files stay out of git.

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
