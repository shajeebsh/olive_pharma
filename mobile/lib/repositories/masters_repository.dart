import '../core/api/api_client.dart';
import '../models/masters.dart';

class MastersRepository {
  MastersRepository(this._client);

  final ApiClient _client;

  Future<List<Region>> regions() async {
    final data = await _client.get('masters/regions/', query: {'page_size': 100})
        as Map<String, dynamic>;
    return (data['results'] as List<dynamic>)
        .map((e) => Region.fromJson(e as Map<String, dynamic>))
        .toList();
  }

  Future<List<Hospital>> hospitals({int? region}) async {
    final data = await _client.get(
      'masters/hospitals/',
      query: {'page_size': 100, if (region != null) 'region': region},
    ) as Map<String, dynamic>;
    return (data['results'] as List<dynamic>)
        .map((e) => Hospital.fromJson(e as Map<String, dynamic>))
        .toList();
  }

  Future<List<Doctor>> doctors({int? hospital}) async {
    final data = await _client.get(
      'masters/doctors/',
      query: {'page_size': 100, if (hospital != null) 'hospital': hospital},
    ) as Map<String, dynamic>;
    return (data['results'] as List<dynamic>)
        .map((e) => Doctor.fromJson(e as Map<String, dynamic>))
        .toList();
  }

  Future<List<Pharmacy>> pharmacies({int? hospital}) async {
    final data = await _client.get(
      'masters/pharmacies/',
      query: {'page_size': 100, if (hospital != null) 'hospital': hospital},
    ) as Map<String, dynamic>;
    return (data['results'] as List<dynamic>)
        .map((e) => Pharmacy.fromJson(e as Map<String, dynamic>))
        .toList();
  }

  Future<List<Product>> products() async {
    final data = await _client.get(
      'masters/products/',
      query: {'page_size': 100, 'active': 'true'},
    ) as Map<String, dynamic>;
    return (data['results'] as List<dynamic>)
        .map((e) => Product.fromJson(e as Map<String, dynamic>))
        .toList();
  }
}
