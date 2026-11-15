import 'package:flutter/material.dart';

import '../../providers/paged_list.dart';
import 'state_views.dart';

/// Renders a [PagedListState] with pull-to-refresh, empty/error states and
/// infinite scroll ("load more") support.
class PaginatedList<T> extends StatelessWidget {
  const PaginatedList({
    super.key,
    required this.state,
    required this.onRefresh,
    required this.onLoadMore,
    required this.itemBuilder,
    required this.emptyMessage,
    this.padding = const EdgeInsets.all(16),
  });

  final PagedListState<T> state;
  final Future<void> Function() onRefresh;
  final VoidCallback onLoadMore;
  final Widget Function(BuildContext context, T item) itemBuilder;
  final String emptyMessage;
  final EdgeInsets padding;

  @override
  Widget build(BuildContext context) {
    if (state.initialLoading && state.items.isEmpty) {
      return const LoadingView();
    }
    if (state.error != null && state.items.isEmpty) {
      return RefreshIndicator(
        onRefresh: onRefresh,
        child: ListView(
          physics: const AlwaysScrollableScrollPhysics(),
          children: [
            SizedBox(
              height: MediaQuery.of(context).size.height * 0.6,
              child: ErrorView(
                message: state.error!,
                onRetry: onRefresh,
              ),
            ),
          ],
        ),
      );
    }
    if (state.items.isEmpty) {
      return RefreshIndicator(
        onRefresh: onRefresh,
        child: ListView(
          physics: const AlwaysScrollableScrollPhysics(),
          children: [
            SizedBox(
              height: MediaQuery.of(context).size.height * 0.6,
              child: EmptyView(message: emptyMessage),
            ),
          ],
        ),
      );
    }

    return RefreshIndicator(
      onRefresh: onRefresh,
      child: NotificationListener<ScrollNotification>(
        onNotification: (notification) {
          if (notification.metrics.pixels >=
              notification.metrics.maxScrollExtent - 200) {
            onLoadMore();
          }
          return false;
        },
        child: ListView.separated(
          padding: padding,
          physics: const AlwaysScrollableScrollPhysics(),
          itemCount: state.items.length + (state.hasMore ? 1 : 0),
          separatorBuilder: (_, __) => const SizedBox(height: 10),
          itemBuilder: (context, index) {
            if (index >= state.items.length) {
              return const Padding(
                padding: EdgeInsets.symmetric(vertical: 16),
                child: Center(child: CircularProgressIndicator()),
              );
            }
            return itemBuilder(context, state.items[index]);
          },
        ),
      ),
    );
  }
}
