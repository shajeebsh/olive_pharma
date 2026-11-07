# OlivePharma - Build Plan

> **Last Updated**: November 2026  
> **Status**: Planning complete - implementation not started  
> **Owner**: Development Team

---

## 1. Goal

Build a focused, mobile-first field activity and sales tracking application for
pharmaceutical representatives. A representative should be able to log doctor and chemist
meetings, record sales, check in/out, and see their own progress. An admin should be able
to review monthly, representative-wise, and hospital-wise activity and sales through
dashboards and reports.

**Success criteria**

- A representative can log a doctor meeting with state, hospital, doctor, date, and the
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

- Public marketing/CMS pages
- AI scoring or recommendations
- Background job infrastructure (Celery/Redis)
- Multi-tenant / multi-organisation support
- Invoicing/accounting integration (sales are entered manually)
- GPS or location capture
- Native iOS/Android app (a responsive web app + REST API is sufficient)

---

## 2. Delivery Phases

### Phase 0 - Foundation

Scaffold the project and establish the conventions everything else depends on.

- [ ] Create Django project `olivepharma` with `settings/` split (base/dev/production)
- [ ] Add `requirements.txt` (Django, DRF, PyMySQL, django-environ, gunicorn)
- [ ] Configure SQLite (dev) and MySQL (prod) via `DATABASE_URL`
- [ ] Set up `core` app with `TimeStampedModel` and `AuditLog`
- [ ] Add two-row shell `base.html` and the "Trusted Innovator" theme files
- [ ] Configure static/media, auth redirects, and Django admin
- [ ] Add `.env.example` (no secrets committed)

**Done when**: `python manage.py check` passes and the shell renders a login page.

---

### Phase 1 - Identity & Organisation

Model the people and hierarchy first; everything else references them.

- [ ] `accounts.RepProfile` (OneToOne with `User`): phone, employee code, territory
- [ ] `accounts.Territory` (name, region)
- [ ] Role helpers: `is_admin`, `is_representative`, `is_staff_member`
- [ ] Basic user list/detail views and admin registration

**Done when**: Admin, Representative, and Staff users can be created and their
permissions are testable.

---

### Phase 2 - Outlets & Masters

Define where reps go and the master data they reference.

- [ ] `outlets.State` (name, code)
- [ ] `outlets.Hospital` (name, state) and `outlets.Doctor` (name, speciality, hospital)
- [ ] `outlets.Pharmacy` (name, state, locality, optional hospital link)
- [ ] **No GPS/location fields** anywhere
- [ ] CRUD views, list filters (state, hospital, search), detail pages

**Done when**: State -> Hospital -> Doctor -> Pharmacy masters are usable in forms.

---

### Phase 3 - Products

Define what reps sell.

- [ ] `products.Category` and `products.Product` (name, SKU, form, strength, price)
- [ ] Active/inactive flag
- [ ] CRUD views and admin inlines

**Done when**: Products can be created and selected when logging a meeting.

---

### Phase 4 - Field Activity & Check-in/out

The core loop of the product.

- [ ] `activities.DoctorMeeting`: representative, state, hospital, doctor, date, notes
- [ ] `activities.DoctorMeetingProduct`: products introduced (through model)
- [ ] `activities.ChemistMeeting`: representative, state, hospital, doctor, pharmacy,
      date, current products, notes
- [ ] `activities.ChemistMeetingProduct`: products the pharmacy needs
- [ ] Meet Doctor views (list, create, detail) restricted to Representative/Admin
- [ ] Meet Chemist views (list, create, detail) restricted to Representative/Admin
- [ ] `activities.AttendanceLog`: user, date, check-in time, check-out time, duration
- [ ] Check-in/check-out views: **time-based only, no GPS**; one open log per user
- [ ] "My day" / attendance history view for the current user

**Done when**: A representative can log doctor and chemist meetings; any user can
check in/out and see their attendance.

---

### Phase 5 - Sales & Targets

Connect activity to outcomes.

- [ ] `sales.SalesEntry`: representative, hospital, doctor, pharmacy, product, date,
      quantity, amount, external reference, notes
- [ ] Manual sales entry views restricted to Staff/Admin
- [ ] Duplicate prevention by external invoice/reference
- [ ] `sales.Target` per rep/product for a month or quarter
- [ ] Actual vs. target calculations in a service layer
- [ ] CRUD views and admin

**Done when**: A staff user can record a sale and target attainment is computed correctly
for a rep and period.

---

### Phase 6 - Reporting & Dashboards

Make the data actionable.

- [ ] Dashboard KPI cards (doctor meetings, chemist meetings, check-ins, sales amount)
- [ ] Reports index with HTMX tabs: Monthly, Representatives, Hospitals, Products
- [ ] Filter form shared across tabs (date range/month, rep, state, hospital, product)
- [ ] Chart.js visualisations (monthly trends, rep-wise, hospital-wise, product demand)
- [ ] CSV export per report with filtering
- [ ] Non-HTMX direct access redirects to the full index page

**Done when**: Each report renders, filters, exports, and matches the design system.

---

### Phase 7 - REST API (Optional Mobile)

Support a thin field client if required.

- [ ] DRF serializers and viewsets for masters, meetings, sales, attendance
- [ ] Token authentication
- [ ] Check-in/check-out endpoints (time-only, idempotent where offline sync is needed)
- [ ] Object-level permissions: representatives/staff only touch their own records
- [ ] Browsable API at `/api/` and schema/docs

**Done when**: A user can check in and sync activity through the API.

---

### Phase 8 - Hardening & Deployment

- [ ] Test coverage for models, permissions, check-in/out, targets, reports
- [ ] Production settings: `DEBUG=False`, `ALLOWED_HOSTS`, secure cookies, HSTS
- [ ] `collectstatic` and static serving strategy
- [ ] Docker image + Gunicorn
- [ ] Backup and migration runbook

**Done when**: The app deploys, passes tests, and handles a realistic data volume.

---

## 3. Milestone Checklist

- [ ] M0 - Foundation scaffold and theme
- [ ] M1 - Users, roles, territories
- [ ] M2 - States, hospitals, doctors, pharmacies
- [ ] M3 - Products
- [ ] M4 - Meet Doctor, Meet Chemist, check-in/out
- [ ] M5 - Manual sales entry and targets
- [ ] M6 - Reports and dashboards
- [ ] M7 - REST API for mobile (optional)
- [ ] M8 - Hardening and production deploy

---

## 4. Risks & Mitigations

| Risk | Impact | Mitigation |
|------|--------|-----------|
| Incomplete locality data (doctor/pharmacy) | Wrong pharmacy association | Make locality matching advisory; allow admin correction |
| Manual sales entry errors | Bad reporting | Validate FK consistency; require/encourage external reference; audit log |
| Scope creep toward "enterprise" | Slower delivery | Enforce the complexity budget in `ai_context.md` |
| Poor mobile UX | Low adoption | Mobile-first templates; test the daily logging loop |
| Data visibility leaks | Privacy/compliance | Server-side role checks; test permissions per role |
| Over-building reports | Time sink | Ship CSV + a few charts first; iterate |

---

## 5. Definition of Done (per feature)

- [ ] Model, migration, admin, and tests exist
- [ ] Views enforce authentication and role visibility
- [ ] URL is namespaced and template extends `base.html`
- [ ] Uses theme tokens (no hard-coded colours)
- [ ] `python manage.py check` and `python manage.py test` pass
- [ ] Docs updated when a foundational decision changes

---

## 6. Documentation Deliverables

- [x] `docs/ai_context.md` - canonical context (stack, decisions, conventions)
- [x] `docs/plan.md` - this plan
- [x] `docs/architecture.md` - detailed architecture
- [x] `docs/field-activity.md` - daily field activity feature specification
- [x] `docs/setup.md` - setup and installation
- [x] `docs/testing.md` - testing and QA
- [x] `docs/api.md` - REST API notes
- [x] `README.md` - quick links mirroring OliveCRM style

---

## 7. Next Action

Begin **Phase 0 - Foundation**: scaffold the Django project and settings split,
then land `core.TimeStampedModel`, the base shell, and the theme files. Use
[field-activity.md](field-activity.md) as the authoritative behaviour spec for Phases
1-6.
