import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../core/api/api_exception.dart';
import '../models/common.dart';

class PagedListState<T> {
  PagedListState({
    this.items = const [],
    this.page = 0,
    this.hasMore = true,
    this.initialLoading = true,
    this.loadingMore = false,
    this.error,
  });

  final List<T> items;
  final int page;
  final bool hasMore;
  final bool initialLoading;
  final bool loadingMore;
  final String? error;

  PagedListState<T> copyWith({
    List<T>? items,
    int? page,
    bool? hasMore,
    bool? initialLoading,
    bool? loadingMore,
    String? error,
    bool clearError = false,
  }) {
    return PagedListState<T>(
      items: items ?? this.items,
      page: page ?? this.page,
      hasMore: hasMore ?? this.hasMore,
      initialLoading: initialLoading ?? this.initialLoading,
      loadingMore: loadingMore ?? this.loadingMore,
      error: clearError ? null : (error ?? this.error),
    );
  }
}

/// Generic cursor-free pagination controller backed by a page-number API.
abstract class PagedListController<T> extends StateNotifier<PagedListState<T>> {
  PagedListController() : super(PagedListState<T>()) {
    Future.microtask(refresh);
  }

  Future<PagedResult<T>> fetchPage(int page);

  Future<void> refresh() async {
    state = state.copyWith(initialLoading: true, clearError: true);
    try {
      final result = await fetchPage(1);
      state = PagedListState<T>(
        items: result.items,
        page: 1,
        hasMore: result.hasMore,
        initialLoading: false,
      );
    } on ApiException catch (error) {
      state = state.copyWith(initialLoading: false, error: error.message);
    }
  }

  Future<void> loadMore() async {
    if (state.loadingMore || !state.hasMore || state.initialLoading) return;
    state = state.copyWith(loadingMore: true, clearError: true);
    final next = state.page + 1;
    try {
      final result = await fetchPage(next);
      state = state.copyWith(
        items: [...state.items, ...result.items],
        page: next,
        hasMore: result.hasMore,
        loadingMore: false,
      );
    } on ApiException catch (error) {
      state = state.copyWith(loadingMore: false, error: error.message);
    }
  }
}
