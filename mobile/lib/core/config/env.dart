/// Compile-time configuration for the OlivePharma rep app.
///
/// Override at build/run time with:
///   flutter run --dart-define=API_BASE_URL=https://your-host/api/
class Env {
  const Env._();

  static const String apiBaseUrl = String.fromEnvironment(
    'API_BASE_URL',
    defaultValue: 'http://localhost:8000/api/',
  );
}
