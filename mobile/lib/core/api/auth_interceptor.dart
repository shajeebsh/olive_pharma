import 'package:dio/dio.dart';

import '../config/env.dart';
import '../storage/token_storage.dart';

/// Attaches the JWT access token to every request and transparently refreshes
/// it once on a `401`. If the refresh fails the stored tokens are cleared and
/// [onUnauthorized] is invoked so the app can log out.
class AuthInterceptor extends Interceptor {
  AuthInterceptor({
    required TokenStorage storage,
    required void Function() onUnauthorized,
  })  : _storage = storage,
        _onUnauthorized = onUnauthorized;

  final TokenStorage _storage;
  final void Function() _onUnauthorized;

  static const _retriedFlag = '_retried';

  @override
  Future<void> onRequest(
    RequestOptions options,
    RequestInterceptorHandler handler,
  ) async {
    final token = await _storage.accessToken;
    if (token != null && token.isNotEmpty) {
      options.headers['Authorization'] = 'Bearer $token';
    }
    handler.next(options);
  }

  @override
  Future<void> onError(
    DioException err,
    ErrorInterceptorHandler handler,
  ) async {
    final response = err.response;
    final options = err.requestOptions;
    final isAuthCall = options.path.contains('auth/login') ||
        options.path.contains('auth/refresh');

    if (response?.statusCode != 401 || isAuthCall) {
      return handler.next(err);
    }

    final alreadyRetried = options.extra[_retriedFlag] == true;
    final refresh = await _storage.refreshToken;
    if (alreadyRetried || refresh == null || refresh.isEmpty) {
      await _storage.clear();
      _onUnauthorized();
      return handler.next(err);
    }

    try {
      final refreshed = await _refreshToken(refresh);
      if (refreshed == null) {
        await _storage.clear();
        _onUnauthorized();
        return handler.next(err);
      }

      options.extra[_retriedFlag] = true;
      options.headers['Authorization'] = 'Bearer $refreshed';
      final retryDio = Dio(BaseOptions(baseUrl: Env.apiBaseUrl));
      final clone = await retryDio.fetch<dynamic>(options);
      return handler.resolve(clone);
    } on DioException {
      await _storage.clear();
      _onUnauthorized();
      return handler.next(err);
    }
  }

  Future<String?> _refreshToken(String refresh) async {
    final dio = Dio(BaseOptions(baseUrl: Env.apiBaseUrl));
    final response = await dio.post<Map<String, dynamic>>(
      'auth/refresh/',
      data: {'refresh': refresh},
    );
    final access = response.data?['access'] as String?;
    if (access != null) {
      await _storage.saveAccess(access);
    }
    return access;
  }
}
