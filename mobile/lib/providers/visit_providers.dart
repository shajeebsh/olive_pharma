import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../models/common.dart';
import '../models/visit.dart';
import '../repositories/visit_repository.dart';
import 'core_providers.dart';
import 'paged_list.dart';

class DoctorVisitsController extends PagedListController<DoctorVisit> {
  DoctorVisitsController(this._repository);

  final VisitRepository _repository;

  @override
  Future<PagedResult<DoctorVisit>> fetchPage(int page) =>
      _repository.doctorVisits(page: page);
}

class ChemistVisitsController extends PagedListController<ChemistVisit> {
  ChemistVisitsController(this._repository);

  final VisitRepository _repository;

  @override
  Future<PagedResult<ChemistVisit>> fetchPage(int page) =>
      _repository.chemistVisits(page: page);
}

final doctorVisitsProvider = StateNotifierProvider.autoDispose<
    DoctorVisitsController, PagedListState<DoctorVisit>>((ref) {
  return DoctorVisitsController(ref.watch(visitRepositoryProvider));
});

final chemistVisitsProvider = StateNotifierProvider.autoDispose<
    ChemistVisitsController, PagedListState<ChemistVisit>>((ref) {
  return ChemistVisitsController(ref.watch(visitRepositoryProvider));
});
