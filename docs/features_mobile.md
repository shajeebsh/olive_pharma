# OlivePharma - Mobile App Features (Flutter Rep App)

> **Last Updated**: November 2026
> **Scope**: Every user-facing feature in the Flutter representative app under
> [`mobile/`](../mobile/README.md), grouped by the bottom-navigation destination it is
> reached from.
> **Source of truth**: The code in `mobile/lib/` and the `api/` Django REST endpoints it
> calls. Where the app differs from the specification, the deviation is noted in
> [Known gaps](#12-known-gaps).

---

## 1. Overview

The mobile app is an online-first Flutter (Material 3) client for pharmaceutical
representatives. It talks to the OlivePharma Django REST API (`/api/`) using JWT auth and
covers the daily field loop: log doctor/chemist meetings, record attendance, view own
sales and dashboard KPIs, and manage the profile.

| Property | Value |
|----------|-------|
| Project | `mobile/` (`olive_rep`) |
| Framework | Flutter 3.x, Material 3 |
| State management | Riverpod (`flutter_riverpod`) |
| HTTP | `dio` with a JWT auth interceptor |
| Secure storage | `flutter_secure_storage` |
| Charts | `fl_chart` |
| API base URL | `--dart-define=API_BASE_URL=...` (default `http://localhost:8000/api/`) |
| Auth | JWT access/refresh (SimpleJWT) |
| Location | **None** - check-in/out is time-only, no GPS |

> **Out of scope**: Admin/Staff screens, CMS, offline sync, and push notifications.

---

## 2. Roles and Navigation

The app targets the **Representative** role. The API enforces role rules server-side, so
the app surface reflects what the signed-in user is allowed to do.

### Bottom navigation

The shell (`features/home/home_shell.dart`) uses a `NavigationBar` with five destinations
kept alive in an `IndexedStack`:

| # | Destination | Screen | Purpose |
|---|-------------|--------|---------|
| 1 | Dashboard | `features/dashboard/dashboard_screen.dart` | KPI cards + recent visits |
| 2 | Visits | `features/visits/visits_hub_screen.dart` | Meet Doctor / Meet Chemist tabs |
| 3 | Sales | `features/sales/sales_screen.dart` | Read-only own sales |
| 4 | Attendance | `features/attendance/attendance_screen.dart` | Check in/out + history |
| 5 | Profile | `features/profile/profile_screen.dart` | View/edit profile, logout |

### Access rules (enforced by the API)

| Capability | Rep | Staff | Admin |
|------------|:---:|:-----:|:-----:|
| Doctor/chemist visit list + create | Yes | No (403) | Yes |
| Read own sales | Yes | Company-wide | Company-wide |
| Attendance list + check in/out | Yes | Yes | Yes |
| Profile get/update | Yes | Yes | Yes |
| Dashboard KPIs | Own | Company-wide | Company-wide |
| Future-dated visit/sale | Rejected | Rejected | Allowed |

---

## 3. Architecture

```
lib/
├── main.dart / app.dart        # ProviderScope + auth-gated root (login vs shell)
├── core/
│   ├── api/                    # Dio client, JWT interceptor, ApiException
│   ├── config/env.dart         # API_BASE_URL (dart-define)
│   ├── storage/                # flutter_secure_storage token store
│   ├── theme/                  # "Trusted Innovator" Material 3 theme
│   └── widgets/                # loading/empty/error views, PaginatedList
├── models/                     # JSON models
├── repositories/               # one per API area
├── providers/                  # Riverpod providers (auth, paged lists, masters)
└── features/                   # screens grouped by feature
```

### Data flow

`Screen` → watches a `Provider` → calls a `Repository` → uses `ApiClient` (`dio`) → hits
`/api/`. List screens use a shared `PagedListController<T>` and render with the shared
`PaginatedList<T>` widget (pull-to-refresh, empty/error states, infinite scroll).

### Authentication flow

1. `LoginScreen` posts credentials to `auth/login/` (`repositories/auth_repository.dart`).
2. Access + refresh tokens and the profile JSON are saved via `TokenStorage`
   (`flutter_secure_storage`).
3. `AuthInterceptor` attaches `Authorization: Bearer <access>` to every request.
4. On a `401`, the interceptor refreshes **once** via `auth/refresh/` and retries; if the
   refresh fails it clears storage and the app returns to login (auto-logout).
5. `AuthController` (`providers/auth_controller.dart`) restores the cached profile on
   launch and gates the root widget (`app.dart`).

---

## 4. Authentication Screen

**Feature**: Auth
**Screen**: `features/auth/login_screen.dart`
**Repository**: `repositories/auth_repository.dart`
**API**: `POST /api/auth/login/`, `POST /api/auth/refresh/`

### Features
- Branded sign-in card with **username** and **password** fields; both required.
- Password visibility toggle.
- Inline error banner for failed sign-in (e.g. "No active account found...").
- Submit button shows an inline spinner while the request is in flight.
- On success the tokens and profile are stored and the app navigates to the shell.
- Session survives app restarts (profile restored from secure storage).
- Automatic logout whenever a request is rejected with `401` and refresh fails.

---

## 5. Dashboard

**Destination**: Dashboard
**Screen**: `features/dashboard/dashboard_screen.dart`
**Provider**: `providers/dashboard_provider.dart`
**Repository**: `repositories/dashboard_repository.dart`
**API**: `GET /api/dashboard/?start=<date>&end=<date>`

### Purpose
Landing screen after login; an at-a-glance view of the representative's own activity for
the selected period.

### Features

#### Date range
- Defaults to the **current month**: start = first day of the month, end = today.
- Tapping the date range in the app bar opens a Material date-range picker
  (`firstDate` 2020, `lastDate` today).
- Changing the range refetches the dashboard and applies to KPIs and recent visits.

#### KPI cards (own data)
Four accent-coloured cards in a 2×2 grid:

| KPI | Description |
|-----|-------------|
| Doctor Visits | Count of the user's doctor visits in range. |
| Chemist Visits | Count of the user's chemist visits in range. |
| Check-ins | Count of the user's attendance records in range. |
| Sales Amount | Sum of the user's sales amounts, formatted as currency. |

#### Activity chart
- `fl_chart` bar chart comparing Doctor visits, Chemist visits and Check-ins.

#### Recent visits
- The latest **5** doctor/chemist visits in the period, each with an icon, outlet
  (doctor/pharmacy), hospital and date.
- Empty state: "No visits in this period."

#### States
- Full-screen loading spinner while fetching.
- Error view with a **Retry** action.
- Pull-to-refresh on the whole page.

---

## 6. Visits (Meet Doctor / Meet Chemist)

**Destination**: Visits
**Screen**: `features/visits/visits_hub_screen.dart` (a two-tab `TabBar`)
**Providers**: `providers/visit_providers.dart`
**Repository**: `repositories/visit_repository.dart`
**API**:
- `GET/POST /api/doctor-visits/`
- `GET/POST /api/chemist-visits/`

The hub has two tabs: **Meet Doctor** and **Meet Chemist**. Each tab is a paginated list
with a **New visit** floating action button that opens the corresponding form.

### 6.1 Meet Doctor list

**Screen**: `features/visits/doctor_visits_tab.dart`

- Paginated own visits (`PagedListController`, 20 per page, infinite scroll).
- Each card shows: doctor name, date, hospital · region, product badges
  (`widgets/product_badges.dart`), and notes.
- Empty state: "No doctor visits yet. Tap + to log one."
- Pull-to-refresh; loading/error states.

### 6.2 Meet Doctor form

**Screen**: `features/visits/doctor_visit_form_screen.dart`

| Field | Widget | Notes |
|-------|--------|-------|
| Date | `DateField` | Required; picker capped at today (no future dates). |
| Region | `RegionDropdown` | Required; all regions. |
| Hospital | `HospitalDropdown` | Required; filtered by region. |
| Doctor | `DoctorDropdown` | Required; filtered by hospital. |
| Products introduced | `ProductMultiSelect` | Optional; active products as toggle chips. |
| Notes | Text field | Optional. |

- **Dependent dropdowns** (`widgets/form_fields.dart`): changing Region resets Hospital and
  Doctor; changing Hospital resets Doctor. Options are fetched from the masters endpoints
  (`masters/hospitals/?region=`, `masters/doctors/?hospital=`).
- Submit posts to `doctor-visits/`; on success the screen pops and the list refreshes.
- API errors (including future-date rejection) are shown inline.

### 6.3 Meet Chemist list

**Screen**: `features/visits/chemist_visits_tab.dart`

- Paginated own visits.
- Each card shows: pharmacy name, date, hospital · region, current products, products
  needed (with total quantity) as badges, and notes.
- Empty state: "No chemist visits yet. Tap + to log one."

### 6.4 Meet Chemist form

**Screen**: `features/visits/chemist_visit_form_screen.dart`

| Field | Widget | Notes |
|-------|--------|-------|
| Date | `DateField` | Required; no future dates. |
| Region | `RegionDropdown` | Required. |
| Hospital | `HospitalDropdown` | Required; filtered by region. |
| Doctor | `DoctorDropdown` | Required; filtered by hospital. |
| Pharmacy | `PharmacyDropdown` | Required; filtered by hospital. |
| Current products | Text field | Optional; what the pharmacy stocks. |
| Products needed | `ProductMultiSelect` | Optional; active products as chips. |
| Quantity | Number | Required; minimum 1. |
| Notes | Text field | Optional. |

- Dependent dropdowns reset children as described above; pharmacy options come from
  `masters/pharmacies/?hospital=`.
- Submit posts to `chemist-visits/`; on success the screen pops and the list refreshes.

---

## 7. Sales

**Destination**: Sales
**Screen**: `features/sales/sales_screen.dart`
**Provider**: `providers/sales_provider.dart`
**Repository**: `repositories/sales_repository.dart`
**API**: `GET /api/sales/`

### Purpose
Read-only view of the representative's own sales (entered by staff/admin in the web app).

### Features
- Paginated list (20 per page, infinite scroll), pull-to-refresh, loading/empty/error
  states.
- Each card shows: product name, amount (currency, right-aligned), hospital · pharmacy,
  quantity, sale date, and reference (when present).
- Empty state: "No sales recorded for you yet."
- **No create/edit** - sales are entered manually from the external accounting system.
- For staff/admin accounts the same endpoint returns company-wide sales.

---

## 8. Attendance (Check In/Out)

**Destination**: Attendance
**Screen**: `features/attendance/attendance_screen.dart`
**Provider**: `providers/attendance_provider.dart`
**Repository**: `repositories/attendance_repository.dart`
**API**:
- `GET /api/checkins/`
- `POST /api/checkins/check-in/`
- `POST /api/checkins/check-out/`

> **Privacy**: This is a **time-based attendance log only**. No GPS, geolocation,
> geofencing, route tracking or device location is collected, requested or stored.

### 8.1 Attendance list

- Paginated own records (20 per page), pull-to-refresh, loading/empty/error states.
- Each card shows: date, check-in time, check-out time (or "Out —"), notes, a status icon
  (open/closed) and the computed duration when closed.
- Empty state: "No attendance records yet."

### 8.2 Check in / Check out

- App-bar actions **Check in** and **Check out** open a dialog with an optional **notes**
  field and a reminder that the current server time is recorded and no location is
  captured.
- The client sends only `notes` (and optionally date/time); the server stamps the time.
- **Check-in** rejects a duplicate for the same user/day: "You have already checked in for
  this date."
- **Check-out** requires an existing check-in and appends the submitted notes.
- Success and error feedback is shown as a SnackBar; the list refreshes after success.

---

## 9. Profile

**Destination**: Profile
**Screen**: `features/profile/profile_screen.dart`
**Providers**: `providers/profile_provider.dart`, `providers/masters_providers.dart`
**Repository**: `repositories/profile_repository.dart`
**API**: `GET/PATCH /api/profile/`, `GET /api/masters/regions/`

### Features
- Header card: avatar initial, display name, username, and role chip
  (Representative / Staff / Admin).
- Editable fields:
  - **Phone**
  - **Employee code**
  - **Region** (dropdown of regions)
- **Save changes** sends a `PATCH` with `phone`, `employee_code` and `region`; on success
  the auth state and profile cache are updated and a SnackBar confirms.
- The profile is fetched fresh from the API; if that request fails the cached auth profile
  is shown instead.
- **Log out** shows a confirmation dialog, clears secure storage and returns to login.
- `role`, `username` and `email` are read-only (the API ignores writes to them).

---

## 10. Cross-Cutting Features

### UI states
Every list and the dashboard implement three states via shared widgets
(`core/widgets/state_views.dart`, `core/widgets/paginated_list.dart`):
- **Loading** - centred spinner (or inline spinner on buttons).
- **Empty** - icon + message specific to the screen.
- **Error** - message with a **Retry** action.

### Pagination
`PagedListController<T>` (`providers/paged_list.dart`) drives page-number pagination with
`page`/`page_size` query parameters and `next`-based "has more" detection. The shared
`PaginatedList<T>` widget triggers **load more** on scroll and supports pull-to-refresh.

### Pull-to-refresh
Dashboard and all list screens support pull-to-refresh (with
`AlwaysScrollableScrollPhysics` so it works even when content is short).

### Theming
Material 3 theme (`core/theme/app_theme.dart`) mirrors the web "Trusted Innovator" tokens:

| Token | Colour |
|-------|--------|
| Primary | Deep Teal `#008080` |
| Navigation / app bar | Dark Indigo `#003566` |
| Background | Cloud Dancer `#F8F9FA` |
| Success | Emerald `#10B981` |
| Danger | Terracotta `#C2412C` |
| Warning | Amber `#F59E0B` |

### Error handling
`ApiClient` maps non-2xx responses and transport failures to `ApiException`
(`core/api/api_exception.dart`), extracting the DRF `detail` or the first field error for a
human-readable message. `401` triggers the refresh/auto-logout path.

### Configuration
The API base URL is a compile-time define (`core/config/env.dart`), so one build can point
at local, staging or production:

```bash
flutter run --dart-define=API_BASE_URL=https://your-app.onrender.com/api/
```

---

## 11. Feature-to-Code Map

| Feature | Screen(s) | Provider / Repository | API endpoint(s) |
|---------|-----------|-----------------------|-----------------|
| Login / session | `auth/login_screen.dart` | `auth_controller`, `auth_repository` | `auth/login/`, `auth/refresh/` |
| Dashboard | `dashboard/dashboard_screen.dart` | `dashboard_provider`, `dashboard_repository` | `dashboard/` |
| Meet Doctor list | `visits/doctor_visits_tab.dart` | `visit_providers`, `visit_repository` | `doctor-visits/` |
| Meet Doctor form | `visits/doctor_visit_form_screen.dart` | `masters_providers`, `visit_repository` | `masters/*`, `doctor-visits/` |
| Meet Chemist list | `visits/chemist_visits_tab.dart` | `visit_providers`, `visit_repository` | `chemist-visits/` |
| Meet Chemist form | `visits/chemist_visit_form_screen.dart` | `masters_providers`, `visit_repository` | `masters/*`, `chemist-visits/` |
| Sales | `sales/sales_screen.dart` | `sales_provider`, `sales_repository` | `sales/` |
| Attendance | `attendance/attendance_screen.dart` | `attendance_provider`, `attendance_repository` | `checkins/`, `checkins/check-in/`, `checkins/check-out/` |
| Profile | `profile/profile_screen.dart` | `profile_provider`, `profile_repository` | `profile/`, `masters/regions/` |
| Bottom nav shell | `home/home_shell.dart` | `auth_controller` | - |
| Shared list UI | `core/widgets/paginated_list.dart` | `providers/paged_list.dart` | - |
| API client / auth | `core/api/` | `core_providers` | all |

---

## 12. Known Gaps

- **Platform folders**: only Dart sources and `pubspec.yaml` are committed; the `android/`
  and `ios/` folders are generated by `flutter create` (done automatically in CI).
- **Sales filters**: the sales list has no date/outlet filters in the app (the API
  supports pagination only on this endpoint).
- **Dashboard scope**: the app requests the current user's own KPIs; company-wide
  breakdowns remain in the web dashboard.
- **No offline mode**: the app requires connectivity; there is no local cache or queued
  sync.
- **No push notifications**.
- **No admin/staff UI**: staff/admin can authenticate but the app is built around the
  representative workflow.

---

## 13. CI and Builds

`.github/workflows/mobile-ci.yml`:

- **Analyze** on pull requests touching `mobile/**`: generates platform folders, runs
  `flutter pub get` and `flutter analyze`.
- **Build release APK** on `v*` tags: builds
  `flutter build apk --release --dart-define=API_BASE_URL=...`, uploads the APK as an
  artifact, and attaches it to a GitHub Release.

Local commands:

```bash
cd mobile
flutter create --platforms=android,ios --org com.olivepharma .
flutter pub get
flutter analyze
flutter run --dart-define=API_BASE_URL=http://localhost:8000/api/
```
