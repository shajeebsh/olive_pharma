# Testing and Quality Assurance

OlivePharma is a small but business-critical application. Tests focus on the daily field
activity loop, role permissions, and the calculations that drive reports.

## 1. Automated Testing

```bash
source .venv/bin/activate
python manage.py test
```

Run tests for a specific app:

```bash
python manage.py test core
python manage.py test accounts
python manage.py test visits
python manage.py test sales
python manage.py test checkin
python manage.py test dashboard
```

### Demo logins for manual testing

Seed the local database once, then start the dev server:

```bash
python manage.py migrate
python manage.py seed_demo
python manage.py runserver
```

Open http://localhost:8000/ and sign in with any of these accounts. The password is
`password123` for all three.

| Username | Role | What to test |
|----------|------|--------------|
| `admin` | Admin | Full access: masters, reports, sales, targets, users |
| `rep` | Representative | Meet Doctor/Chemist, own check-in/out, own visits/sales/reports |
| `staff` | Staff | Sales entry, targets read, check-in/out, company-wide reports |

The seed command is idempotent and also creates a demo region, hospital, doctor, pharmacy,
three products, one doctor visit, one chemist visit, one sale, one target, and a check-in.
Only use these credentials for local development; never seed them in production.

## 2. Test Coverage

The current suite covers:

- **Core**: scoped manager behaviour for reps vs admin/staff; health endpoint.
- **Accounts**: profile auto-creation and role helpers.
- **Visits**: service-layer creation, product M2M assignment, audit signal, role access.
- **Sales**: staff entry, `entered_by`, audit signal, duplicate-reference rejection, rep
  access rules, target attainment math.
- **Check-in**: duplicate check-in rejection, check-out without check-in, duration
  calculation, view-level validation errors.
- **Dashboard**: rep scoping, admin aggregation, all report tabs, filtered CSV export.

## 3. Permission Checks (must always pass)

| Role | Expected behaviour |
|------|--------------------|
| Representative | Can meet doctor/chemist and check in/out; cannot create sales; sees own visits/sales/reports |
| Staff | Can check in/out and create sales; cannot log visits; sees company-wide sales/reports and own attendance history |
| Admin | Can read and write everything; manages masters and users |
| Anonymous | Redirected to login on all app URLs |

Path-level checks live in `core.middleware.RoleAccessMiddleware`; view-level checks use
`core.permissions.RoleRequiredMixin`. Both must stay in sync.

## 4. End-to-End (E2E) Scenarios

### Scenario 1: Meet Doctor
1. Log in as a representative and open **Meet Doctor -> New visit**.
2. Select a region, hospital, and doctor; confirm the date.
3. Select introduced products and save.
4. **Verify**: the visit appears in the representative's list with the right outlets.

### Scenario 2: Meet Chemist
1. Log in as a representative and open **Meet Chemist -> New visit**.
2. Select the region, hospital, and doctor whose locality is being covered.
3. Select a nearby pharmacy, record current products, and add products needed.
4. **Verify**: the visit is saved with the required products and appears in product
   reporting.

### Scenario 3: Check-in / Check-out (time only)
1. Log in as any role and open **Check In/Out**.
2. Check in for today.
3. Attempt to check in again - it should be rejected (one record per user per day).
4. Check out.
5. **Verify**: attendance shows a computed duration; **no location data** is requested or
   stored.

### Scenario 4: Sales Entry
1. Log in as staff and open **Sales -> New entry**.
2. Select representative, region, hospital, doctor, pharmacy, and product; enter quantity,
   amount, and an external reference.
3. Save.
4. **Verify**: the sale appears in sales and report totals update.
5. Re-enter the same reference for the same representative and **verify** it is rejected.

### Scenario 5: Role Separation
1. As a representative, confirm the sales-create action is unavailable and blocked
   server-side (403).
2. As staff, confirm **Meet Doctor** / **Meet Chemist** are blocked server-side.
3. As a representative, confirm another representative's records are not visible.
4. As admin, confirm all records and reports are visible.

### Scenario 6: Reporting & Export
1. Open **Reports** and switch tabs (Monthly, Representatives, Hospitals, Products).
2. Change filters (date range, representative, hospital, product) and apply.
3. Export CSV for the active tab.
4. **Verify**: the CSV headers/rows match the on-screen figures for the selected filters.

## 5. Pre-Commit Checklist

```bash
python manage.py check
python manage.py makemigrations --check --dry-run
python manage.py test
python manage.py collectstatic --no-input   # when changing static files
```
