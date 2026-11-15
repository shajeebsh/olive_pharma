import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:intl/intl.dart';

import '../../core/theme/app_theme.dart';
import '../../core/widgets/paginated_list.dart';
import '../../models/sales_log.dart';
import '../../providers/sales_provider.dart';

class SalesScreen extends ConsumerWidget {
  const SalesScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final state = ref.watch(salesProvider);

    return Scaffold(
      appBar: AppBar(title: const Text('Sales')),
      body: PaginatedList<SalesLog>(
        state: state,
        onRefresh: () => ref.read(salesProvider.notifier).refresh(),
        onLoadMore: () => ref.read(salesProvider.notifier).loadMore(),
        emptyMessage: 'No sales recorded for you yet.',
        itemBuilder: (context, sale) => _SalesCard(sale: sale),
      ),
    );
  }
}

class _SalesCard extends StatelessWidget {
  const _SalesCard({required this.sale});

  final SalesLog sale;

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final currency = NumberFormat.currency(symbol: '₹', decimalDigits: 2);
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(14),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                Expanded(
                  child: Text(
                    sale.productName,
                    style: theme.textTheme.titleMedium
                        ?.copyWith(fontWeight: FontWeight.bold),
                  ),
                ),
                Text(
                  currency.format(sale.amount),
                  style: theme.textTheme.titleMedium?.copyWith(
                    fontWeight: FontWeight.bold,
                    color: AppTheme.success,
                  ),
                ),
              ],
            ),
            const SizedBox(height: 4),
            Text(
              '${sale.hospitalName} · ${sale.pharmacyName}',
              style: theme.textTheme.bodySmall,
            ),
            const SizedBox(height: 8),
            Row(
              children: [
                Text('Qty ${sale.quantity}', style: theme.textTheme.bodyMedium),
                const Spacer(),
                Text(sale.salesDate, style: theme.textTheme.bodySmall),
              ],
            ),
            if (sale.reference.isNotEmpty) ...[
              const SizedBox(height: 4),
              Text('Ref: ${sale.reference}', style: theme.textTheme.bodySmall),
            ],
          ],
        ),
      ),
    );
  }
}
