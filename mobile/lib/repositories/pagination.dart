import '../models/common.dart';

/// Parses a DRF paginated response into a [PagedResult].
PagedResult<T> parsePaged<T>(
  Map<String, dynamic> data,
  T Function(Map<String, dynamic>) fromJson,
) {
  final results = (data['results'] as List<dynamic>? ?? [])
      .map((e) => fromJson(e as Map<String, dynamic>))
      .toList();
  return PagedResult(items: results, hasMore: data['next'] != null);
}
