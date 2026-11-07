# OlivePharma

Mobile-first field activity and sales tracking for pharmaceutical representatives.
Built with **Django 5.0**, **Bootstrap 5**, and **HTMX** for teams of under 100 users.

---

## Quick Links

- [🚀 Setup & Installation](docs/setup.md)
- [🏗️ Architecture Overview](docs/architecture.md)
- [🧪 Testing & QA](docs/testing.md)
- [📡 REST API Documentation](docs/api.md)
- [📝 AI Context Documentation](docs/ai_context.md)
- [🗺️ Build Plan](docs/plan.md)

---

## Project Overview

**OlivePharma** helps field reps check in and out at doctors, pharmacies, and hospitals,
log visits and products discussed, record sales, and track progress against targets.
Managers get dashboards and reports for their team. A small, focused modular monolith -
no CMS, no background workers, no unnecessary infrastructure.

### Key Modules
- **Accounts**: Users, reps, managers, territories
- **Outlets**: Doctors, pharmacies, hospitals
- **Products**: Product catalog and categories
- **Activities**: Check-in/out, visits, field activity
- **Sales**: Sales records and targets
- **Reporting**: Dashboards, reports, and CSV export
- **API**: DRF token API for the mobile client

---

## Tech Stack

- **Backend**: Django 5.0+, Django Rest Framework
- **Frontend**: Bootstrap 5.3, HTMX, Chart.js, mobile-first
- **Database**: SQLite (Dev), MySQL 8 (Production)
- **Auth**: Django Auth (sessions + API tokens)
- **Server**: Gunicorn, Docker

---

## Setup (Quick Start)

```bash
# Install dependencies
pip install -r requirements.txt

# Database setup
python manage.py migrate
python manage.py createsuperuser

# Run server
python manage.py runserver
```

For detailed instructions, see [docs/setup.md](docs/setup.md).

---

## Documentation

All project context lives in [`docs/`](docs/):

| Document | Purpose |
|----------|---------|
| [ai_context.md](docs/ai_context.md) | Canonical context: stack, decisions, conventions |
| [plan.md](docs/plan.md) | Phased build plan and milestones |
| [architecture.md](docs/architecture.md) | Architecture patterns and domain model |
| [setup.md](docs/setup.md) | Setup and installation |
| [testing.md](docs/testing.md) | Testing and QA |
| [api.md](docs/api.md) | REST API usage |

---

## License

Copyright © 2026 OlivePharma Team. All rights reserved.
