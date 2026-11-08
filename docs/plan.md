# OlivePharma - Build Plan

> **Last Updated**: November 2026
> **Status**: Phases 0-6 implemented; optional API (Phase 7) and hardening (Phase 8) remain
> **Owner**: Development Team

---

## 1. Goal

Build a focused, mobile-first field activity and sales tracking application for
pharmaceutical representatives. A representative should be able to log doctor and chemist
meetings, record sales, check in/out, and see their own progress. An admin should be able
to review monthly, representative-wise, and hospital-wise activity and sales through
dashboards and reports.

**Success criteria**

- A representative can log a doctor meeting with region, hospital, doctor, date, and the
  products introduced.
- A representative can log a chemist meeting near a doctor, including current products
  and the products the pharmacy needs.
- A staff user can add a sales entry matched to representative, hospital, doctor,
  pharmacy, and product.
- Any user can check in and check out (time-based only, no GPS) and see their attendance.
- An admin can see monthly, representative-wise, and hospital-wise reports with filters.
- Reports export to CSV for the chosen filters.
- The app runs comfortably for under 100 users on a single server.

**Non-goals (MVP)**

- Public marketing/CMS pages required for the core workflow (Wagtail is optional)
- AI scoring or recommendations
- Background job infrastructure (Celery/Redis)
- Multi-tenant / multi-organisation support
- Invoicing/accounting integration (sales are entered manually)
- GPS or location capture
- Native iOS/Android app (a responsive web app is sufficient for now)

---

## 2. Delivery Phases

### Phase 0 - Foundation ✅

- [x] Create Django project with `config/settings/` split (`base`, `dev`, `prod`)
- [x] Add `requirements.txt` (Django 5.0, Wagtail 6.0, psycopg2, dj-database-url,
      python-decouple, gunicorn, whitenoise, weasyprint, Pillow)
- [x] Configure SQLite (dev) and PostgreSQL (prod) via `DATABASE_URL`
- [x] Set up `core` app with `TimeStampedModel`, `AuditLog`, masters, managers
- [x] Add two-row shell `base.html` and the "Trusted Innovator" theme
- [x] Configure static/media, auth redirects, Django admin, health check
- [x] Add `.env.example` (no secrets committed)

**Done when**: `python manage.py check` passes and the shell renders a login page. ✅

---

### Phase 1 - Identity & Organisation ✅

- [x] `accounts.UserProfile` (OneToOne with `User`): role, phone, employee code, region
- [x] Role helpers: `is_admin`, `is_representative`, `is_staff_member`
- [x] Auto-create profile via signal; profile view and admin registration
- [x] Redirects and role-aware navigation registry

**Done when**: Admin, Representative, and Staff users behave differently and permissions
are tested. ✅

---

### Phase 2 - Outlets & Masters ✅

- [x] `core.Region` (name, code)
- [x] `core.Hospital` (name, region, city, address)
- [x] `core.Doctor` (name, hospital, speciality, phone)
- [x] `core.Pharmacy` (name, region, optional hospital, locality, phone)
- [x] **No GPS/location fields** anywhere
- [x] Django admin CRUD for all masters; used by visit/sales forms

**Done when**: Region -> Hospital -> Doctor -> Pharmacy masters are usable in forms. ✅

---

### Phase 3 - Products ✅

- [x] `core.Product` (name, SKU, form, strength, active flag)
- [x] Django admin CRUD and active-product filtering in forms

**Done when**: Products can be created and selected when logging a meeting. ✅

---

### Phase 4 - Field Activity & Check-in/out ✅

- [x] `visits.DoctorVisit`: rep, region, hospital, doctor, date, products introduced, notes
- [x] `visits.ChemistVisit`: rep, region, hospital, doctor context, pharmacy, date,
      current products, products needed, notes
- [x] Meet Doctor views (list, create) restricted to Representative/Admin
- [x] Meet Chemist views (list, create) restricted to Representative/Admin
- [x] `checkin.CheckInOut`: user, date, check-in time, check-out time, notes, duration
- [x] Check-in/check-out views: time-based only; one record per user per day
- [x] Attendance history view for the current user
- [x] Audit signals for doctor and chemist visits

**Done when**: A representative can log doctor and chemist meetings; any user can
check in/out and see their attendance. ✅

---

### Phase 5 - Sales & Targets ✅

- [x] `sales.SalesLog`: representative, region, hospital, doctor, pharmacy, product, date,
      quantity, amount, external reference, notes, entered_by
- [x] Manual sales entry views restricted to Staff/Admin
- [x] Duplicate prevention by external reference per representative
- [x] `sales.Target` per rep/product for a month or quarter
- [x] Actual vs. target calculations in `services.target_attainment()`
- [x] List/create views, admin, and audit signal

**Done when**: A staff user can record a sale and target attainment is computed correctly
for a rep and period. ✅

---

### Phase 6 - Reporting & Dashboards ✅

- [x] Dashboard KPI cards (doctor visits, chemist visits, check-ins, sales amount)
- [x] Reports tabs: Monthly, Representatives, Hospitals, Products
- [x] Shared filter form (date range, representative, hospital, product)
- [x] Chart.js visualisations (monthly/rep/hospital/product)
- [x] CSV export per report with filtering
- [x] Server-rendered tabs (no HTMX dependency)

**Done when**: Each report renders, filters, exports, and matches the design system. ✅

---

### Phase 7 - REST API (Optional Mobile)

- [ ] Add DRF serializers and viewsets for masters, visits, sales, attendance
- [ ] Token authentication
- [ ] Check-in/check-out endpoints (time-only, idempotent where offline sync is needed)
- [ ] Object-level permissions: representatives/staff only touch their own records
- [ ] Browsable API at `/api/` and schema/docs

**Done when**: A user can check in and sync activity through the API.

---

### Phase 8 - Hardening & Deployment (partial)

- [x] Test coverage for scoped managers, permissions, check-in/out, sales, targets, reports
- [x] Production settings: `DEBUG=False`, secure cookies, HSTS, allowed hosts
- [x] `collectstatic` and WhiteNoise static serving
- [x] Render Blueprint + Gunicorn (`render.yaml`, `build.sh`)
- [ ] Backup and migration runbook
- [ ] Optional Docker image

**Done when**: The app deploys, passes tests, and handles a realistic data volume.

---

## 3. Milestone Checklist

- [x] M0 - Foundation scaffold and theme
- [x] M1 - Users and roles
- [x] M2 - Regions, hospitals, doctors, pharmacies
- [x] M3 - Products
- [x] M4 - Meet Doctor, Meet Chemist, check-in/out
- [x] M5 - Manual sales entry and targets
- [x] M6 - Reports and dashboards
- [ ] M7 - REST API for mobile (optional)
- [ ] M8 - Hardening and production deploy (Render configured; runbook pending)

---

## 4. Risks & Mitigations

| Risk | Impact | Mitigation |
|------|--------|-----------|
| Incomplete locality data (doctor/pharmacy) | Wrong pharmacy association | Make locality matching advisory; allow admin correction |
| Manual sales entry errors | Bad reporting | Validate FK consistency; duplicate-reference protection; audit log |
| Scope creep toward "enterprise" | Slower delivery | Enforce the complexity budget in `ai_context.md` |
| Poor mobile UX | Low adoption | Mobile-first templates; test the daily logging loop |
| Data visibility leaks | Privacy/compliance | Server-side role checks; scoped managers; tests per role |
| Over-building reports | Time sink | Ship CSV + a few charts first; iterate |

---

## 5. Definition of Done (per feature)

- [x] Model, migration, admin, and tests exist
- [x] Views enforce authentication and role visibility
- [x] URL is namespaced and template extends `base.html`
- [x] Uses theme tokens (no hard-coded colours in templates)
- [x] `python manage.py check` and `python manage.py test` pass
- [x] Docs updated when a foundational decision changes

---

## 6. Documentation Deliverables

- [x] `docs/ai_context.md` - canonical context (stack, decisions, conventions)
- [x] `docs/plan.md` - this plan
- [x] `docs/architecture.md` - detailed architecture
- [x] `docs/field-activity.md` - daily field activity feature specification
- [x] `docs/setup.md` - setup, configuration, and Render deployment
- [x] `docs/testing.md` - testing and QA
- [x] `docs/api.md` - REST API notes (optional future work)
- [x] `README.md` - project overview and quick links

---

## 7. Next Action

Optionally add the DRF API (Phase 7) for a mobile client, then complete the Phase 8
runbook (backups, restore drill, deployment checklist). Re-run `manage.py check`,
`manage.py test`, and `collectstatic` before each deploy.
