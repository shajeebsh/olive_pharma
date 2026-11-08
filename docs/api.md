# REST API (Planned - Not Implemented)

> **Status**: The current build does **not** include a REST API. This document records the
> agreed design for optional future work (Phase 7 in [plan.md](plan.md)). The web app is
> fully usable without it, and no `/api/` routes are currently served.

The planned API would use **Django REST Framework (DRF)** to support a thin field mobile
client. It would mirror the web application and would **not** collect location data.

## 1. Overview

- **Base URL**: `/api/`
- **Authentication**: token authentication for mobile; session authentication for the
  browsable API
- **Format**: JSON

## 2. Planned Endpoints

- **Regions**: `/api/regions/`
- **Hospitals**: `/api/hospitals/`
- **Doctors**: `/api/doctors/`
- **Pharmacies**: `/api/pharmacies/`
- **Products**: `/api/products/`
- **Doctor visits**: `/api/doctor-visits/`
- **Chemist visits**: `/api/chemist-visits/`
- **Sales**: `/api/sales/`
- **Targets**: `/api/targets/`
- **Check-in / Check-out**: `/api/checkin/check-in/`, `/api/checkin/check-out/`

## 3. Planned Usage

### Time-based Check-in

Check-in would record only a server timestamp - **no latitude, longitude, or device
location**. An optional `client_uuid` could support idempotent retries if a client queues
requests:

```bash
curl -X POST http://localhost:8000/api/checkin/check-in/ \
  -H "Authorization: Token <your-token>" \
  -H "Content-Type: application/json" \
  -d '{"client_uuid": "b1f2..."}'
```

### Logging a Doctor Visit

```bash
curl -X POST http://localhost:8000/api/doctor-visits/ \
  -H "Authorization: Token <your-token>" \
  -H "Content-Type: application/json" \
  -d '{"region": 1, "hospital": 4, "doctor": 9, "date": "2026-11-07", "products_introduced": [12, 15]}'
```

## 4. Planned Permissions

- Representatives may log doctor/chemist visits and check in/out; they may read only
  their own records.
- Staff may check in/out and create sales; they have company-wide sales/report
  visibility, matching the web app.
- Admins may read/write all records.
- All endpoints require authentication.

## 5. Planned Documentation

- **API schema**: `/api/schema/`
- **Swagger UI**: `/api/docs/`

Implement token auth, object-level permissions, and tests for each endpoint before
enabling this module.
