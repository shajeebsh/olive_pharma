import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../models/attendance.dart';
import '../models/common.dart';
import '../repositories/attendance_repository.dart';
import 'core_providers.dart';
import 'paged_list.dart';

class AttendanceController extends PagedListController<AttendanceRecord> {
  AttendanceController(this._repository);

  final AttendanceRepository _repository;

  @override
  Future<PagedResult<AttendanceRecord>> fetchPage(int page) =>
      _repository.fetch(page: page);
}

final attendanceProvider = StateNotifierProvider.autoDispose<
    AttendanceController, PagedListState<AttendanceRecord>>((ref) {
  return AttendanceController(ref.watch(attendanceRepositoryProvider));
});
