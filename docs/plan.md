# OlivePharma - Build Plan

> **Last Updated**: November 2026  
> **Status**: Planning complete - implementation not started  
> **Owner**: Development Team

---

## 1. Goal

Build a focused, mobile-first field activity and sales tracking application for
pharmaceutical representatives. A rep should be able to check in at an outlet, log a
visit, record sales, and see progress against target. A manager should be able to
review team activity and sales through dashboards and reports.

**Success criteria**

- A rep can complete the full field loop on a phone in under two minutes:
  check in -> log visit + products -> check out.
- A manager can see today's visits, MTD sales, and target attainment per rep.
- Reports export to CSV for a chosen date range.
- The app runs comfortably for under 100 users on a single server.

**Non-goals (MVP)**

- Public marketing/CMS pages
- AI scoring or recommendations
- Background job infrastructure (Celery/Redis)
- Multi-tenant / multi-organisation support
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

- [ ] `accounts.RepProfile` (OneToOne with `User`): phone, employee code, territory, manager
- [ ] `accounts.Territory` (name, region, manager)
- [ ] Role helpers: `is_admin`, `is_manager`, `is_rep` on the profile
- [ ] Manager -> rep relationship for team-level visibility
- [ ] Admin registration and basic rep list/detail views

**Done when**: A manager can be assigned reps, and visibility rules are testable.

---

### Phase 2 - Outlets

Define where reps go.

- [ ] `outlets.Outlet` base with type (doctor, pharmacy, hospital), address, GPS point
- [ ] `outlets.Doctor` (speciality, clinic) and pharmacy/hospital specifics
- [ ] Optional assignment of outlets to territories
- [ ] CRUD views, list filters (type, territory, search), detail pages

**Done when**: Reps can browse outlets assigned to their territory.

---

### Phase 3 - Products

Define what reps sell.

- [ ] `products.Category` and `products.Product` (name, SKU, form, strength, price)
- [ ] Active/inactive flag
- [ ] CRUD views and admin inlines

**Done when**: Products can be created and selected during a visit.

---

### Phase 4 - Field Activity & Check-in/out

The core loop of the product.

- [ ] `activities.Visit`: rep, outlet, check-in time, check-out time, GPS, purpose, notes
- [ ] `activities.VisitProduct`: products discussed + samples left
- [ ] Check-in view: captures GPS (browser geolocation), validates optional geofence
- [ ] Check-out view: closes the visit, computes duration
- [ ] Activity types (visit, call, meeting, training, stock check)
- [ ] Rep "My day" view; manager team activity view
- [ ] Offline queue: mobile submits queued check-ins via API (Phase 7)

**Done when**: A rep can check in, log a visit, check out, and see it in their day view.

---

### Phase 5 - Sales & Targets

Connect activity to outcomes.

- [ ] `sales.SalesRecord` / `Order` with lines tied to product, quantity, amount
- [ ] Link sales to rep, outlet, and optional visit
- [ ] `sales.Target` per rep/product for a month or quarter
- [ ] Actual vs. target calculations in a service layer
- [ ] CRUD views and admin

**Done when**: Target attainment is computed correctly for a rep and period.

---

### Phase 6 - Reporting & Dashboards

Make the data actionable.

- [ ] Dashboard KPI cards (visits today, active reps, sales MTD, target %)
- [ ] Reports index with HTMX tabs: Activity, Sales, Targets, Reps
- [ ] Date-range filter form shared across tabs
- [ ] Chart.js visualisations (visits over time, sales by product, target progress)
- [ ] CSV export per report with date filtering
- [ ] Non-HTMX direct access redirects to the full index page

**Done when**: Each report renders, filters, exports, and matches the design system.

---

### Phase 7 - REST API (Mobile)

Support the field mobile client.

- [ ] DRF serializers and viewsets for outlets, products, visits, sales
- [ ] Token authentication
- [ ] Check-in/check-out endpoints with idempotency for offline retries
- [ ] Object-level permissions: reps only touch their own records
- [ ] Browsable API at `/api/` and schema/docs

**Done when**: A rep can check in and sync a visit through the API.

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
- [ ] M2 - Outlets
- [ ] M3 - Products
- [ ] M4 - Check-in/out and visits
- [ ] M5 - Sales and targets
- [ ] M6 - Reports and dashboards
- [ ] M7 - REST API for mobile
- [ ] M8 - Hardening and production deploy

---

## 4. Risks & Mitigations

| Risk | Impact | Mitigation |
|------|--------|-----------|
| Unreliable GPS in the field | Bad check-in data | Accept manual override; log accuracy; optional geofence |
| Offline usage | Lost visits | Client-side queue + idempotent check-in endpoint |
| Scope creep toward "enterprise" | Slower delivery | Enforce the complexity budget in `ai_context.md` |
| Poor mobile UX | Low rep adoption | Mobile-first templates; test the two-minute field loop |
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
- [x] `docs/setup.md` - setup and installation
- [x] `docs/testing.md` - testing and QA
- [x] `docs/api.md` - REST API notes
- [x] `README.md` - quick links mirroring OliveCRM style

---

## 7. Next Action

Begin **Phase 0 - Foundation**: scaffold the Django project and settings split,
then land `core.TimeStampedModel`, the base shell, and the theme files.
