# Testing and Quality Assurance

OlivePharma is a small but business-critical application. Tests focus on the field
workflow, permissions, and the calculations that drive reports.

## 1. Automated Testing

Run the full suite:

```bash
source venv/bin/activate
python manage.py test
```

Run tests for a specific app:

```bash
# Foundation & shared models
python manage.py test olivepharma.core

# People, roles, territories
python manage.py test olivepharma.accounts

# Outlets and products
python manage.py test olivepharma.outlets olivepharma.products

# Field activity (check-in/out, visits)
python manage.py test olivepharma.activities

# Sales and targets
python manage.py test olivepharma.sales

# Reports and exports
python manage.py test olivepharma.reporting

# API
python manage.py test olivepharma.api
```

## 2. Test Coverage

The suite should cover:

- **Core**: `TimeStampedModel` timestamps and audit logging.
- **Accounts**: rep/manager hierarchy and role helpers.
- **Outlets**: outlet types, territory assignment, search filters.
- **Products**: catalog invariants (SKU uniqueness, active flag).
- **Activities**: check-in/out timestamps, one-open-visit rule, GPS missing flag,
  idempotent check-in by `client_uuid`.
- **Sales**: target attainment math, sales totals, period filtering.
- **Reporting**: date-range filtering, CSV contents, HTMX redirect fallback.
- **API**: token auth, object-level permissions, offline retry idempotency.

## 3. Permission Checks (must always pass)

| Role | Expected behaviour |
|------|--------------------|
| Rep | Cannot read or write another rep's visits or sales |
| Manager | Can read their team's data, not other teams' |
| Admin | Can read and write everything |
| Anonymous | Redirected to login on all app URLs |

## 4. End-to-End (E2E) Scenarios

Validate the full system integration by following these core workflows.

### Scenario 1: Check-in / Check-out Loop
1. Log in as a rep and open **My Day**.
2. Select an outlet and check in (allow or deny GPS).
3. Add visit notes and products discussed.
4. Check out.
5. **Verify**: the visit appears in My Day with a computed duration and correct
   server timestamp; a second open visit is rejected.

### Scenario 2: Sales & Target Attainment
1. Create monthly targets for a rep and product.
2. Record a sales entry for that rep and product.
3. Open the Targets report for the period.
4. **Verify**: actual, target, and attainment percentage compute correctly.

### Scenario 3: Manager Oversight
1. Log in as a manager with two reps.
2. Open team activity for today.
3. **Verify**: both reps' visits appear, and another team's visits do not.

### Scenario 4: Reporting & Export
1. Open the Reports index and switch tabs (Activity, Sales, Targets, Reps).
2. Change the date range and confirm the data updates via HTMX.
3. Export CSV.
4. **Verify**: the CSV matches the on-screen figures for the selected range.

### Scenario 5: Offline Sync
1. Simulate an offline check-in queued on the client.
2. Reconnect and sync.
3. **Verify**: a single visit is created (no duplicate on retry).

## 5. Pre-Commit Checklist

```bash
python manage.py check
python manage.py makemigrations --check --dry-run
python manage.py test
```
