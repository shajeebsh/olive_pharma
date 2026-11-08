# Testing and Quality Assurance

OlivePharma is a small but business-critical application. Tests focus on the daily field
activity loop, role permissions, and the calculations that drive reports.

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

# Masters: states, hospitals, doctors, pharmacies, products
python manage.py test olivepharma.outlets olivepharma.products

# Field activity (meet doctor, meet chemist, check-in/out)
python manage.py test olivepharma.activities

# Manual sales entry and targets
python manage.py test olivepharma.sales

# Reports and exports
python manage.py test olivepharma.reporting

# API (optional mobile client)
python manage.py test olivepharma.api
```

## 2. Test Coverage

The suite should cover:

- **Core**: `TimeStampedModel` timestamps and audit logging.
- **Accounts**: role helpers for Admin, Representative, and Staff.
- **Outlets**: state -> hospital -> doctor -> pharmacy consistency and search filters.
- **Products**: catalog invariants (SKU uniqueness, active flag).
- **Activities**: doctor meeting fields, chemist meeting required products, check-in/out
  timestamps, one-open-log rule, duration calculation, and **no location fields**.
- **Sales**: manual entry validation, duplicate prevention by external reference, target
  attainment math, period filtering.
- **Reporting**: date-range filtering, monthly/rep/hospital aggregations, CSV contents,
  HTMX redirect fallback.
- **API**: token auth and object-level permissions.

## 3. Permission Checks (must always pass)

| Role | Expected behaviour |
|------|--------------------|
| Representative | Can meet doctor/chemist and check in/out; cannot update sales; sees only own data |
| Staff | Can check in/out and update sales; cannot log meetings; sees only own data |
| Admin | Can read and write everything; manages users and masters |
| Anonymous | Redirected to login on all app URLs |

## 4. End-to-End (E2E) Scenarios

Validate the full system integration by following these core workflows.

### Scenario 1: Meet Doctor
1. Log in as a representative and open **Meet Doctor -> New**.
2. Select a state, hospital, and doctor; confirm the date.
3. Select at least one introduced product and save.
4. **Verify**: the meeting appears in the representative's activity list, and the
   state/hospital/doctor match.

### Scenario 2: Meet Chemist
1. Log in as a representative and open **Meet Chemist -> New**.
2. Select the state, hospital, and doctor whose locality is being covered.
3. Select a nearby pharmacy, record current products, and add products the pharmacy
   needs.
4. **Verify**: the chemist meeting is saved with the required products and appears in
   product-demand reporting.

### Scenario 3: Check-in / Check-out (time only)
1. Log in as any role and open **Check-In / Check-Out**.
2. Check in.
3. Attempt to check in again - it should be rejected (one open log).
4. Check out.
5. **Verify**: attendance shows a computed duration and server timestamps; **no
   location data** is requested or stored.

### Scenario 4: Update Sales
1. Log in as staff and open **Sales -> Update**.
2. Select representative, hospital, doctor, pharmacy, and product; enter quantity and
   amount.
3. Save.
4. **Verify**: the sale appears in sales reports and totals update.
5. Re-enter the same external reference and **verify** it is rejected as a duplicate.

### Scenario 5: Role Separation
1. As a representative, confirm the **Update Sales** action is unavailable and blocked
   server-side.
2. As staff, confirm **Meet Doctor** / **Meet Chemist** are unavailable and blocked.
3. As a representative, confirm another representative's records are not visible.
4. As admin, confirm all records and reports are visible.

### Scenario 6: Reporting & Export
1. Open the Reports index and switch tabs (Monthly, Representatives, Hospitals,
   Products).
2. Change filters (date range, representative, state, hospital, product) and confirm the
   data updates via HTMX.
3. Export CSV.
4. **Verify**: the CSV matches the on-screen figures for the selected filters.

## 5. Pre-Commit Checklist

```bash
python manage.py check
python manage.py makemigrations --check --dry-run
python manage.py test
```
