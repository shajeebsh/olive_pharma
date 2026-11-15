import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../models/user_profile.dart';
import 'core_providers.dart';

/// Fetches the freshest profile from the API (falls back to the cached user in
/// the auth state if the request fails).
final profileProvider = FutureProvider.autoDispose<UserProfile>((ref) {
  return ref.watch(profileRepositoryProvider).fetch();
});
