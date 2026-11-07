# Setup and Installation

This guide provides step-by-step instructions for setting up the OlivePharma development
environment.

## 1. Prerequisites

- Python 3.11+
- Virtualenv
- MySQL 8 (optional, for production parity)
- A modern browser (Chrome/Safari/Firefox) for testing mobile layout with device mode

## 2. Installation

```bash
# Clone the repository
git clone https://github.com/shajeebsh/olive_pharma.git
cd olive_pharma

# Create and activate a virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

## 3. Environment Configuration

Create a `.env` file in the project root:

```env
DEBUG=True
SECRET_KEY=your-secret-key
DATABASE_URL=sqlite:///db.sqlite3
ALLOWED_HOSTS=localhost,127.0.0.1
```

For production, point `DATABASE_URL` at MySQL:

```env
DATABASE_URL=mysql://user:password@localhost:3306/olive_pharma
```

## 4. Database Setup

```bash
# Apply migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser
```

## 5. Running the Server

```bash
# Start development server
python manage.py runserver
```

Access the application at `http://localhost:8000/`. Test the field workflow by opening
the site in a mobile viewport (or on a phone on the same network using
`python manage.py runserver 0.0.0.0:8000`).

## 6. Static Files

```bash
# Collect static files (required for production)
python manage.py collectstatic
```

## 7. Settings Modules

The project uses a settings split. Run management commands against the right module:

```bash
# Development (default via manage.py)
python manage.py runserver

# Production
DJANGO_SETTINGS_MODULE=olivepharma.settings.production python manage.py migrate
```

## 8. Docker (Production)

```bash
docker build -t olive_pharma .
docker run -p 8000:8000 --env-file .env olive_pharma
```
