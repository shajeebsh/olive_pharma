import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../models/common.dart';
import '../models/sales_log.dart';
import '../repositories/sales_repository.dart';
import 'core_providers.dart';
import 'paged_list.dart';

class SalesController extends PagedListController<SalesLog> {
  SalesController(this._repository);

  final SalesRepository _repository;

  @override
  Future<PagedResult<SalesLog>> fetchPage(int page) =>
      _repository.fetch(page: page);
}

final salesProvider =
    StateNotifierProvider.autoDispose<SalesController, PagedListState<SalesLog>>(
        (ref) {
  return SalesController(ref.watch(salesRepositoryProvider));
});
