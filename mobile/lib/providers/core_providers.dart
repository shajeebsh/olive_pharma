import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../core/api/api_client.dart';
import '../core/storage/token_storage.dart';
import '../repositories/attendance_repository.dart';
import '../repositories/auth_repository.dart';
import '../repositories/dashboard_repository.dart';
import '../repositories/masters_repository.dart';
import '../repositories/profile_repository.dart';
import '../repositories/sales_repository.dart';
import '../repositories/visit_repository.dart';
import 'auth_controller.dart';

final tokenStorageProvider = Provider<TokenStorage>((ref) => TokenStorage());

final apiClientProvider = Provider<ApiClient>((ref) {
  return ApiClient(
    storage: ref.watch(tokenStorageProvider),
    onUnauthorized: () {
      ref.read(authControllerProvider.notifier).handleUnauthorized();
    },
  );
});

final authRepositoryProvider = Provider<AuthRepository>((ref) {
  return AuthRepository(
    client: ref.watch(apiClientProvider),
    storage: ref.watch(tokenStorageProvider),
  );
});

final profileRepositoryProvider = Provider<ProfileRepository>(
  (ref) => ProfileRepository(ref.watch(apiClientProvider)),
);

final dashboardRepositoryProvider = Provider<DashboardRepository>(
  (ref) => DashboardRepository(ref.watch(apiClientProvider)),
);

final mastersRepositoryProvider = Provider<MastersRepository>(
  (ref) => MastersRepository(ref.watch(apiClientProvider)),
);

final visitRepositoryProvider = Provider<VisitRepository>(
  (ref) => VisitRepository(ref.watch(apiClientProvider)),
);

final salesRepositoryProvider = Provider<SalesRepository>(
  (ref) => SalesRepository(ref.watch(apiClientProvider)),
);

final attendanceRepositoryProvider = Provider<AttendanceRepository>(
  (ref) => AttendanceRepository(ref.watch(apiClientProvider)),
);
