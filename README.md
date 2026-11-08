# OlivePharma

Mobile-first field activity and sales tracking for pharmaceutical representatives.
Built with **Django 5.0**, **PostgreSQL**, **Bootstrap 5**, and **Chart.js** for teams of
under 100 users.

---

## Quick Links

- [🚀 Setup & Installation](docs/setup.md)
- [🏗️ Architecture Overview](docs/architecture.md)
- [📍 Field Activity Feature](docs/field-activity.md)
- [🧪 Testing & QA](docs/testing.md)
- [📡 REST API Documentation](docs/api.md)
- [📝 AI Context Documentation](docs/ai_context.md)
- [🗺️ Build Plan](docs/plan.md)

---

## Project Overview

**OlivePharma** helps medical representatives log their daily field activity: meeting
doctors, meeting nearby chemists, recording manual sales from the accounting system, and
checking in/out with a **time-based log (no GPS)**. Admins get monthly,
representative-wise, and hospital-wise dashboards and reports with CSV exports.

### Key Modules

- **Core**: shared models (regions, hospitals, doctors, pharmacies, products), scoped
  managers, audit log, role middleware, and navigation registry
- **Accounts**: users and roles (Admin, Representative, Staff) via `UserProfile`
- **Visits**: Meet Doctor and Meet Chemist logging with product selections
- **Sales**: manual sales entry, duplicate-reference protection, targets, and attainment
- **Check-in**: time-based check-in/check-out with one log per user per day
- **Dashboard**: KPI cards, filters, monthly/representative/hospital/product reports,
  Chart.js visualisations, and CSV export
- **CMS**: optional Wagtail pages at `/cms/`

### Roles

| Role | Can do |
|------|--------|
| Admin | Everything, company-wide visibility |
| Representative | Meet Doctor, Meet Chemist, Check In/Out, own activity/sales reports |
| Staff | Manual sales entry, Check In/Out, company-wide reports |

---

## Tech Stack

- **Backend**: Django 5.0, Wagtail 6.0 (optional CMS)
- **Frontend**: Django Templates, Bootstrap 5.3, Chart.js, mobile-first
- **Database**: SQLite (development), PostgreSQL (production via `DATABASE_URL`)
- **Config**: python-decouple, dj-database-url, psycopg2-binary
- **Serving**: Gunicorn, WhiteNoise, Render
- **Exports**: WeasyPrint available for PDF extension; CSV export implemented

---

## Setup (Quick Start)

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

cp .env.example .env
python manage.py migrate
python manage.py seed_demo      # optional demo data
python manage.py runserver
```

Demo logins after `seed_demo`: `admin`, `rep`, `staff` with password `password123`.
App: http://localhost:8000/ · Wagtail admin: `/cms/` · Django admin: `/django-admin/`.

For detailed instructions, see [docs/setup.md](docs/setup.md).

---

## Tests

```bash
python manage.py check
python manage.py test
```

Coverage includes scoped managers, role access, visit/sales services and signals,
duplicate-reference protection, target attainment, check-in/out state transitions,
dashboard filtering, reports, and CSV exports.

---

## Deployment

The repo includes `render.yaml` and `build.sh` for a Render Blueprint with managed
PostgreSQL. Set `DJANGO_SETTINGS_MODULE=config.settings.prod`; the build script runs
collectstatic and migrations, and Gunicorn serves `config.wsgi:application`.

---

## Documentation

All project context lives in [`docs/`](docs/):

| Document | Purpose |
|----------|---------|
| [ai_context.md](docs/ai_context.md) | Canonical context: stack, decisions, conventions |
| [plan.md](docs/plan.md) | Phased build plan and milestones |
| [architecture.md](docs/architecture.md) | Architecture patterns and domain model |
| [field-activity.md](docs/field-activity.md) | Daily field activity feature specification |
| [setup.md](docs/setup.md) | Setup, configuration, and Render deploy |
| [testing.md](docs/testing.md) | Testing and QA |
| [api.md](docs/api.md) | REST API notes (optional future work) |
