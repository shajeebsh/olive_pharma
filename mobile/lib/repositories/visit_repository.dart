import '../core/api/api_client.dart';
import '../models/common.dart';
import '../models/visit.dart';
import 'pagination.dart';

class VisitRepository {
  VisitRepository(this._client);

  final ApiClient _client;

  Future<PagedResult<DoctorVisit>> doctorVisits({int page = 1}) async {
    final data = await _client.get(
      'doctor-visits/',
      query: {'page': page},
    ) as Map<String, dynamic>;
    return parsePaged(data, DoctorVisit.fromJson);
  }

  Future<DoctorVisit> createDoctorVisit(Map<String, dynamic> payload) async {
    final data = await _client.post('doctor-visits/', data: payload)
        as Map<String, dynamic>;
    return DoctorVisit.fromJson(data);
  }

  Future<PagedResult<ChemistVisit>> chemistVisits({int page = 1}) async {
    final data = await _client.get(
      'chemist-visits/',
      query: {'page': page},
    ) as Map<String, dynamic>;
    return parsePaged(data, ChemistVisit.fromJson);
  }

  Future<ChemistVisit> createChemistVisit(Map<String, dynamic> payload) async {
    final data = await _client.post('chemist-visits/', data: payload)
        as Map<String, dynamic>;
    return ChemistVisit.fromJson(data);
  }
}
