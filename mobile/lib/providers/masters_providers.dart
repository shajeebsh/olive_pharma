import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../models/masters.dart';
import 'core_providers.dart';

final regionsProvider = FutureProvider.autoDispose<List<Region>>((ref) {
  return ref.watch(mastersRepositoryProvider).regions();
});

final hospitalsProvider =
    FutureProvider.autoDispose.family<List<Hospital>, int?>((ref, region) {
  return ref.watch(mastersRepositoryProvider).hospitals(region: region);
});

final doctorsProvider =
    FutureProvider.autoDispose.family<List<Doctor>, int?>((ref, hospital) {
  return ref.watch(mastersRepositoryProvider).doctors(hospital: hospital);
});

final pharmaciesProvider =
    FutureProvider.autoDispose.family<List<Pharmacy>, int?>((ref, hospital) {
  return ref.watch(mastersRepositoryProvider).pharmacies(hospital: hospital);
});

final productsProvider = FutureProvider.autoDispose<List<Product>>((ref) {
  return ref.watch(mastersRepositoryProvider).products();
});
