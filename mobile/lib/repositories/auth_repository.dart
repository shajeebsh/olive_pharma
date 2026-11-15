import '../core/api/api_client.dart';
import '../core/api/api_exception.dart';
import '../core/storage/token_storage.dart';
import '../models/user_profile.dart';

class AuthResult {
  const AuthResult({
    required this.access,
    required this.refresh,
    required this.user,
  });

  final String access;
  final String refresh;
  final UserProfile user;
}

class AuthRepository {
  AuthRepository({required ApiClient client, required TokenStorage storage})
      : _client = client,
        _storage = storage;

  final ApiClient _client;
  final TokenStorage _storage;

  Future<AuthResult> login({
    required String username,
    required String password,
  }) async {
    final data = await _client.post(
      'auth/login/',
      data: {'username': username, 'password': password},
    );
    if (data is! Map<String, dynamic>) {
      throw ApiException('Unexpected login response.');
    }
    final access = data['access'] as String?;
    final refresh = data['refresh'] as String?;
    final userJson = data['user'] as Map<String, dynamic>?;
    if (access == null || refresh == null || userJson == null) {
      throw ApiException('Login response is missing tokens.');
    }
    final user = UserProfile.fromJson(userJson);
    await _storage.saveTokens(access: access, refresh: refresh);
    await _storage.saveUser(userJson);
    return AuthResult(access: access, refresh: refresh, user: user);
  }

  Future<UserProfile?> cachedUser() async {
    final json = await _storage.getUser();
    return json == null ? null : UserProfile.fromJson(json);
  }

  Future<void> logout() => _storage.clear();
}
