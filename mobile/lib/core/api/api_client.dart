import 'package:dio/dio.dart';

import '../config/env.dart';
import '../storage/token_storage.dart';
import 'api_exception.dart';
import 'auth_interceptor.dart';

/// Thin wrapper around [Dio] that attaches JWT auth, maps errors to
/// [ApiException], and exposes typed helpers for the repositories.
class ApiClient {
  ApiClient({required TokenStorage storage, required void Function() onUnauthorized})
      : _dio = Dio(
          BaseOptions(
            baseUrl: Env.apiBaseUrl,
            connectTimeout: const Duration(seconds: 20),
            receiveTimeout: const Duration(seconds: 30),
            contentType: Headers.jsonContentType,
            responseType: ResponseType.json,
          ),
        ) {
    _dio.interceptors.add(
      AuthInterceptor(storage: storage, onUnauthorized: onUnauthorized),
    );
  }

  final Dio _dio;

  Future<dynamic> get(String path, {Map<String, dynamic>? query}) =>
      _request(() => _dio.get(path, queryParameters: query));

  Future<dynamic> post(String path, {Object? data}) =>
      _request(() => _dio.post(path, data: data));

  Future<dynamic> patch(String path, {Object? data}) =>
      _request(() => _dio.patch(path, data: data));

  Future<dynamic> _request(Future<Response<dynamic>> Function() send) async {
    try {
      final response = await send();
      return response.data;
    } on DioException catch (error) {
      throw _mapError(error);
    }
  }

  ApiException _mapError(DioException error) {
    final status = error.response?.statusCode;
    final data = error.response?.data;

    String message;
    if (data is Map && data.isNotEmpty) {
      final detail = data['detail'];
      if (detail is String) {
        message = detail;
      } else {
        message = _firstFieldError(data) ?? 'Request failed.';
      }
    } else if (error.type == DioExceptionType.connectionTimeout ||
        error.type == DioExceptionType.receiveTimeout ||
        error.type == DioExceptionType.connectionError) {
      message = 'Cannot reach the server. Check your connection.';
    } else {
      message = error.message ?? 'Unexpected error.';
    }

    return ApiException(message, statusCode: status);
  }

  String? _firstFieldError(Map data) {
    for (final value in data.values) {
      if (value is List && value.isNotEmpty) return value.first.toString();
      if (value is String && value.isNotEmpty) return value;
    }
    return null;
  }
}
