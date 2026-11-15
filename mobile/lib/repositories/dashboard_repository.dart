import '../core/api/api_client.dart';
import '../models/dashboard.dart';

class DashboardRepository {
  DashboardRepository(this._client);

  final ApiClient _client;

  Future<DashboardData> fetch({required String start, required String end}) async {
    final data = await _client.get(
      'dashboard/',
      query: {'start': start, 'end': end},
    ) as Map<String, dynamic>;
    return DashboardData.fromJson(data);
  }
}
