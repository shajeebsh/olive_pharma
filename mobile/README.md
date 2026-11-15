# OlivePharma Rep App (Flutter)

Material 3 mobile client for pharmaceutical representatives. It talks to the
OlivePharma Django REST API (JWT auth) and covers the field workflow:

- **Auth** – login, JWT stored in `flutter_secure_storage`, auto-logout on `401`
- **Dashboard** – 4 KPI cards (own data), current-month default range, recent 5 visits
- **Meet Doctor** – paginated list (products as badges) + create form
- **Meet Chemist** – paginated list + create form (pharmacy, current products, needed)
- **Sales** – read-only own list
- **Attendance** – paginated own check-in/out list, check-in/out actions (time only, no GPS)
- **Profile** – view/edit phone, employee code, region; logout

Bottom navigation: Dashboard · Visits · Sales · Attendance · Profile.

## Architecture

```
lib/
├── main.dart / app.dart        # ProviderScope + auth-gated root
├── core/
│   ├── api/                    # Dio client, JWT interceptor, error mapping
│   ├── config/env.dart         # API_BASE_URL (dart-define)
│   ├── storage/                # flutter_secure_storage token store
│   ├── theme/                  # "Trusted Innovator" Material 3 theme
│   └── widgets/                # loading/empty/error, paginated list
├── models/                     # JSON models
├── repositories/               # one per API area
├── providers/                  # Riverpod providers (auth, paged lists, masters)
└── features/                   # screens grouped by feature
```

State management is **Riverpod**; HTTP is **dio** with an auth interceptor that
refreshes the access token once and logs the user out when refresh fails.

## Running

The app reads the API base URL from a compile-time define:

```bash
flutter pub get

# Point at a local backend (default is http://localhost:8000/api/)
flutter run --dart-define=API_BASE_URL=http://10.0.2.2:8000/api/   # Android emulator
flutter run --dart-define=API_BASE_URL=http://localhost:8000/api/  # iOS simulator / desktop

# Point at a deployed backend
flutter run --dart-define=API_BASE_URL=https://your-app.onrender.com/api/
```

The backend must be running and the user must have the **Representative** (or
Admin) role. Create a demo rep with `python manage.py seed_demo`
(`rep` / `password123`).

## Platform folders

Only the Dart sources and `pubspec.yaml` are committed. The `android/` and
`ios/` platform folders are generated on demand:

```bash
flutter create --platforms=android,ios --org com.olivepharma .
```

This is done automatically in CI before building the APK.

## Tests & analysis

```bash
flutter analyze
flutter test
```

## CI

`.github/workflows/mobile-ci.yml` builds a release APK on every tag (`v*`) and
attaches it to a GitHub Release. It also runs `flutter analyze` on pull requests.
