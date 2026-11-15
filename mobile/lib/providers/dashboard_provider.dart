import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:intl/intl.dart';

import '../models/dashboard.dart';
import 'core_providers.dart';

final _isoDate = DateFormat('yyyy-MM-dd');

/// Default range is the current month up to today.
final dashboardRangeProvider = StateProvider<DateTimeRange>((ref) {
  final now = DateTime.now();
  return DateTimeRange(
    start: DateTime(now.year, now.month, 1),
    end: DateTime(now.year, now.month, now.day),
  );
});

final dashboardProvider = FutureProvider.autoDispose<DashboardData>((ref) {
  final range = ref.watch(dashboardRangeProvider);
  return ref.watch(dashboardRepositoryProvider).fetch(
        start: _isoDate.format(range.start),
        end: _isoDate.format(range.end),
      );
});
