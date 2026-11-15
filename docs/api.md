# REST API

> **Status**: Implemented (`api/`). The API powers the Flutter representative app in
> [`mobile/`](../mobile/README.md). It mirrors the web application, reuses the same
> service layer and scoped managers, and **never** collects location data.

## 1. Overview

- **Base URL**: `/api/`
- **Authentication**: JWT (`Authorization: Bearer <access>`); session auth is also
  enabled for the browsable API and local testing.
- **Format**: JSON
- **Pagination**: page-number, `?page=` and `?page_size=` (max 100), default 20. List
  responses use DRF's `{count, next, previous, results}` envelope.

## 2. Authentication

| Method | Endpoint | Purpose |
|--------|----------|---------|
| POST | `/api/auth/login/` | Obtain `access` + `refresh` tokens and the profile |
| POST | `/api/auth/refresh/` | Exchange a refresh token for a new access token |
| POST | `/api/auth/verify/` | Verify a token |

```bash
curl -X POST http://localhost:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"username": "rep", "password": "password123"}'
```

The app stores tokens in `flutter_secure_storage`, attaches the access token to every
request, refreshes once on `401`, and logs out if refresh fails.

## 3. Endpoints

| Method | Endpoint | Purpose | Access |
|--------|----------|---------|--------|
| GET/PATCH | `/api/profile/` | Own profile (phone, employee code, region) | Any authenticated |
| GET | `/api/dashboard/` | KPI cards + recent 5 visits (`?start=&end=`) | Any authenticated |
| GET | `/api/filter-options/` | Dependent dropdowns (`?type=hospital&region=`, `type=doctor/pharmacy&hospital=`) | Any authenticated |
| GET/POST | `/api/doctor-visits/` | List own / create doctor visit | Rep, Admin |
| GET/POST | `/api/chemist-visits/` | List own / create chemist visit | Rep, Admin |
| GET | `/api/sales/` | Read-only own sales (staff/admin: company-wide) | Any authenticated |
| GET | `/api/checkins/` | Paginated own attendance | Any authenticated |
| POST | `/api/checkins/check-in/` | Check in (one per day; time only) | Any authenticated |
| POST | `/api/checkins/check-out/` | Check out (requires check-in; appends notes) | Any authenticated |
| GET | `/api/masters/regions/` | Regions | Any authenticated |
| GET | `/api/masters/hospitals/` | Hospitals (`?region=`) | Any authenticated |
| GET | `/api/masters/doctors/` | Doctors (`?hospital=`) | Any authenticated |
| GET | `/api/masters/pharmacies/` | Pharmacies (`?hospital=`, `?region=`) | Any authenticated |
| GET | `/api/masters/products/` | Products (`?active=true`) | Any authenticated |

### Logging a doctor visit

```bash
curl -X POST http://localhost:8000/api/doctor-visits/ \
  -H "Authorization: Bearer <access>" \
  -H "Content-Type: application/json" \
  -d '{"date": "2026-11-07", "region": 1, "hospital": 4, "doctor": 9, "products_introduced": [12, 15], "notes": "Intro"}'
```

### Time-based check-in

Check-in records only the server timestamp — **no latitude, longitude, or device
location**. One record per user per day.

```bash
curl -X POST http://localhost:8000/api/checkins/check-in/ \
  -H "Authorization: Bearer <access>" \
  -H "Content-Type: application/json" \
  -d '{"notes": "Starting the day"}'
```

## 4. Permissions

- Representatives may log doctor/chemist visits and check in/out; they read only their
  own records (`ScopedManager.for_user`).
- Staff may check in/out and read company-wide sales; they cannot use visit endpoints.
- Admins may read/write all records and are exempt from the future-date rule.
- All endpoints require authentication.

## 5. Business rules

- **Future-date validation**: doctor visits, chemist visits, and sales reject future
  dates for representatives; admins are exempt.
- **Duplicate check-in**: a second check-in for the same user and date is rejected.
- **Check-out**: requires an existing check-in for the date and appends notes.
- **Audit**: visit/sales creation emits the same signals as the web app, writing
  `AuditLog` rows.

## 6. Tests

```bash
python manage.py test api
```

Coverage includes login/tokens, profile read/update, scoped lists, future-date rules,
role gating, check-in/out state transitions, filter options, masters, and dashboard KPIs.
