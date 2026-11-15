import '../core/api/api_client.dart';
import '../models/user_profile.dart';

class ProfileRepository {
  ProfileRepository(this._client);

  final ApiClient _client;

  Future<UserProfile> fetch() async {
    final data = await _client.get('profile/') as Map<String, dynamic>;
    return UserProfile.fromJson(data);
  }

  Future<UserProfile> update({
    String? phone,
    String? employeeCode,
    int? region,
  }) async {
    final payload = <String, dynamic>{};
    if (phone != null) payload['phone'] = phone;
    if (employeeCode != null) payload['employee_code'] = employeeCode;
    payload['region'] = region;
    final data = await _client.patch('profile/', data: payload)
        as Map<String, dynamic>;
    return UserProfile.fromJson(data);
  }
}
