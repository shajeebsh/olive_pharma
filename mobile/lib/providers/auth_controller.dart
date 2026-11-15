import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../core/api/api_exception.dart';
import '../models/user_profile.dart';
import '../repositories/auth_repository.dart';
import 'core_providers.dart';

enum AuthStatus { unknown, authenticated, unauthenticated }

class AuthState {
  const AuthState({
    this.status = AuthStatus.unknown,
    this.user,
    this.loading = false,
    this.error,
  });

  final AuthStatus status;
  final UserProfile? user;
  final bool loading;
  final String? error;

  AuthState copyWith({
    AuthStatus? status,
    UserProfile? user,
    bool? loading,
    String? error,
    bool clearError = false,
  }) {
    return AuthState(
      status: status ?? this.status,
      user: user ?? this.user,
      loading: loading ?? this.loading,
      error: clearError ? null : (error ?? this.error),
    );
  }
}

class AuthController extends StateNotifier<AuthState> {
  AuthController(this._repository) : super(const AuthState()) {
    _restore();
  }

  final AuthRepository _repository;

  Future<void> _restore() async {
    final user = await _repository.cachedUser();
    state = state.copyWith(
      status: user == null ? AuthStatus.unauthenticated : AuthStatus.authenticated,
      user: user,
    );
  }

  Future<bool> login(String username, String password) async {
    state = state.copyWith(loading: true, clearError: true);
    try {
      final result = await _repository.login(
        username: username,
        password: password,
      );
      state = AuthState(status: AuthStatus.authenticated, user: result.user);
      return true;
    } on ApiException catch (error) {
      state = state.copyWith(
        loading: false,
        error: error.message,
        status: AuthStatus.unauthenticated,
      );
      return false;
    }
  }

  void setUser(UserProfile user) {
    state = state.copyWith(user: user);
  }

  Future<void> logout() async {
    await _repository.logout();
    state = const AuthState(status: AuthStatus.unauthenticated);
  }

  void handleUnauthorized() {
    state = const AuthState(status: AuthStatus.unauthenticated);
  }
}

final authControllerProvider =
    StateNotifierProvider<AuthController, AuthState>((ref) {
  return AuthController(ref.watch(authRepositoryProvider));
});
