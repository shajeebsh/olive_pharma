# REST API Documentation

OlivePharma provides a REST API built with **Django REST Framework (DRF)** to support
the field mobile client and integrations.

## 1. Overview

The API lets a thin mobile client fetch reference data and sync field activity
(check-ins, visits, sales) reliably.

- **Base URL**: `/api/`
- **Authentication**: Token-based authentication for the mobile app; session
  authentication for the browsable API.
- **Format**: JSON

## 2. API Endpoints

The API is organised by business resource:

- **Outlets**: `/api/outlets/`
- **Products**: `/api/products/`
- **Visits**: `/api/visits/`
- **Check-in / Check-out**: `/api/visits/check-in/`, `/api/visits/{id}/check-out/`
- **Sales**: `/api/sales/`
- **Targets**: `/api/targets/`

## 3. Usage

### Browsable API

The REST API is available at `/api/` in your browser. Use the interactive interface to
explore and test the endpoints.

### Mobile Client / cURL

Authenticate with a token and call endpoints with `curl` or any HTTP client:

```bash
curl -X GET http://localhost:8000/api/outlets/ \
  -H "Authorization: Token <your-token>"
```

### Offline-Friendly Check-in

Check-in accepts a client-generated `client_uuid`. Retrying the same check-in is
idempotent and returns the existing visit instead of creating a duplicate:

```bash
curl -X POST http://localhost:8000/api/visits/check-in/ \
  -H "Authorization: Token <your-token>" \
  -H "Content-Type: application/json" \
  -d '{"outlet": 12, "client_uuid": "b1f2...", "latitude": "6.9271", "longitude": "79.8612"}'
```

## 4. Permissions

- Reps may read/write only their own visits and sales.
- Managers may read their team's records.
- Admins may read/write all records.
- All endpoints require authentication.

## 5. Documentation

Detailed API documentation is generated from the DRF schema:
- **API Schema**: `/api/schema/`
- **Swagger UI**: `/api/docs/`
