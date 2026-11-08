# REST API Documentation

OlivePharma provides a REST API built with **Django REST Framework (DRF)** to support a
thin field mobile client and integrations. The API mirrors the web application; it does
**not** collect location data.

## 1. Overview

The API lets a client fetch master data, log doctor/chemist meetings, record manual
sales, and manage time-based attendance (check-in/check-out).

- **Base URL**: `/api/`
- **Authentication**: Token-based authentication for the mobile app; session
  authentication for the browsable API.
- **Format**: JSON

## 2. API Endpoints

The API is organised by business resource:

- **States**: `/api/states/`
- **Hospitals**: `/api/hospitals/`
- **Doctors**: `/api/doctors/`
- **Pharmacies**: `/api/pharmacies/`
- **Products**: `/api/products/`
- **Doctor Meetings**: `/api/doctor-meetings/`
- **Chemist Meetings**: `/api/chemist-meetings/`
- **Sales Entries**: `/api/sales/`
- **Targets**: `/api/targets/`
- **Check-in / Check-out**: `/api/attendance/check-in/`, `/api/attendance/check-out/`

## 3. Usage

### Browsable API

The REST API is available at `/api/` in your browser. Use the interactive interface to
explore and test the endpoints.

### Client / cURL

Authenticate with a token and call endpoints with `curl` or any HTTP client:

```bash
curl -X GET http://localhost:8000/api/doctors/?hospital=4 \
  -H "Authorization: Token <your-token>"
```

### Time-based Check-in

Check-in records only a server timestamp - **no latitude, longitude, or device
location**. An optional `client_uuid` supports idempotent retries if a client queues
requests:

```bash
curl -X POST http://localhost:8000/api/attendance/check-in/ \
  -H "Authorization: Token <your-token>" \
  -H "Content-Type: application/json" \
  -d '{"client_uuid": "b1f2..."}'
```

### Logging a Doctor Meeting

```bash
curl -X POST http://localhost:8000/api/doctor-meetings/ \
  -H "Authorization: Token <your-token>" \
  -H "Content-Type: application/json" \
  -d '{"state": 1, "hospital": 4, "doctor": 9, "date": "2026-11-07", "products": [12, 15]}'
```

## 4. Permissions

- Representatives may log doctor/chemist meetings and check in/out; they may read only
  their own records.
- Staff may check in/out and update sales; they may read only their own records.
- Admins may read/write all records.
- All endpoints require authentication.

## 5. Documentation

Detailed API documentation is generated from the DRF schema:
- **API Schema**: `/api/schema/`
- **Swagger UI**: `/api/docs/`
