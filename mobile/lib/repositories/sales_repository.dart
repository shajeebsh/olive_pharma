import '../core/api/api_client.dart';
import '../models/common.dart';
import '../models/sales_log.dart';
import 'pagination.dart';

class SalesRepository {
  SalesRepository(this._client);

  final ApiClient _client;

  Future<PagedResult<SalesLog>> fetch({int page = 1}) async {
    final data = await _client.get('sales/', query: {'page': page})
        as Map<String, dynamic>;
    return parsePaged(data, SalesLog.fromJson);
  }
}
