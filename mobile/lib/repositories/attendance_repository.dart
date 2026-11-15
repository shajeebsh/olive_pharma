import '../core/api/api_client.dart';
import '../models/attendance.dart';
import '../models/common.dart';
import 'pagination.dart';

class AttendanceRepository {
  AttendanceRepository(this._client);

  final ApiClient _client;

  Future<PagedResult<AttendanceRecord>> fetch({int page = 1}) async {
    final data = await _client.get('checkins/', query: {'page': page})
        as Map<String, dynamic>;
    return parsePaged(data, AttendanceRecord.fromJson);
  }

  Future<AttendanceRecord> checkIn({
    String? date,
    String? time,
    String notes = '',
  }) async {
    final data = await _client.post(
      'checkins/check-in/',
      data: {
        if (date != null) 'date': date,
        if (time != null) 'check_in': time,
        'notes': notes,
      },
    ) as Map<String, dynamic>;
    return AttendanceRecord.fromJson(data);
  }

  Future<AttendanceRecord> checkOut({
    String? date,
    String? time,
    String notes = '',
  }) async {
    final data = await _client.post(
      'checkins/check-out/',
      data: {
        if (date != null) 'date': date,
        if (time != null) 'check_out': time,
        'notes': notes,
      },
    ) as Map<String, dynamic>;
    return AttendanceRecord.fromJson(data);
  }
}
