# Setup and Installation

Step-by-step instructions for running OlivePharma locally and on Render.

## 1. Prerequisites

- Python 3.11+
- Git
- PostgreSQL 14+ **only if** you want to match production locally (SQLite is the default)
- A modern browser for testing the mobile layout with device mode

## 2. Installation

```bash
git clone https://github.com/shajeebsh/olive_pharma.git
cd olive_pharma

python3 -m venv .venv
source .venv/bin/activate

pip install -r requirements.txt
```

## 3. Environment Configuration

Copy the example environment file and adjust values:

```bash
cp .env.example .env
```

Key variables (`python-decouple` reads `.env` automatically):

| Variable | Local default | Purpose |
|----------|---------------|---------|
| `DJANGO_SETTINGS_MODULE` | `config.settings.dev` | Settings module |
| `DEBUG` | `True` | Debug mode |
| `SECRET_KEY` | dev-only value | Django secret |
| `DATABASE_URL` | `sqlite:///db.sqlite3` | Database connection |
| `ALLOWED_HOSTS` | `localhost,127.0.0.1` | Comma-separated hosts |
| `TIME_ZONE` | `UTC` | Display/storage time zone |

To use PostgreSQL locally, point `DATABASE_URL` at it:

```env
DATABASE_URL=postgres://user:password@localhost:5432/olive_pharma
```

## 4. Database Setup

```bash
python manage.py migrate

# Optional: demo users and sample field data
python manage.py seed_demo
```

`seed_demo` creates `admin`, `rep`, and `staff` users (password `password123`), a region,
hospital, doctor, pharmacy, products, a doctor visit, a chemist visit, a sale, a target,
and a check-in.

Create a real superuser when you are ready:

```bash
python manage.py createsuperuser
```

## 5. Running the Server

```bash
python manage.py runserver
```

- App: http://localhost:8000/
- Django admin: http://localhost:8000/django-admin/
- Wagtail CMS admin: http://localhost:8000/cms/
- Health check: http://localhost:8000/health/

## 6. Static and Media Files

```bash
# Production only: build the manifest for WhiteNoise
python manage.py collectstatic --no-input
```

In development the app serves plain static files from `static/` without collectstatic.

## 7. Settings Modules

| Module | Use |
|--------|-----|
| `config.settings.dev` | Local development (default via `manage.py`) |
| `config.settings.prod` | Render/production (`DEBUG=False`, secure cookies, HSTS) |

Production commands:

```bash
DJANGO_SETTINGS_MODULE=config.settings.prod python manage.py migrate
DJANGO_SETTINGS_MODULE=config.settings.prod gunicorn config.wsgi:application
```

## 8. Tests and Checks

```bash
python manage.py check
python manage.py test
```

## 9. Deploying to Render

The repository includes `render.yaml`, `build.sh`, and `start.sh`. Create a Blueprint from
the repo; Render provisions PostgreSQL and sets `DATABASE_URL`. The build script installs
dependencies, collects static files, and applies migrations. The start script runs
`collectstatic` again before Gunicorn, then serves via `gunicorn config.wsgi:application`.
`/health/` is the health-check path.

Production uses WhiteNoise with `WHITENOISE_USE_FINDERS = True` and
`CompressedStaticFilesStorage` (no manifest), so static files are served even if the
`staticfiles/` output is missing at runtime.

Render is pinned to Python 3.11.11 via the `PYTHON_VERSION` env var and
`.python-version` file. Do not use `pythonVersion` in `render.yaml`; Render ignores it.
If you created the service manually, set `PYTHON_VERSION=3.11.11` in the dashboard and
use `./start.sh` as the start command.
