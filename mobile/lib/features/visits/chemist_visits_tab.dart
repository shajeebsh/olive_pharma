import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../core/widgets/paginated_list.dart';
import '../../models/visit.dart';
import '../../providers/visit_providers.dart';
import 'chemist_visit_form_screen.dart';
import 'widgets/product_badges.dart';

class ChemistVisitsTab extends ConsumerWidget {
  const ChemistVisitsTab({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final state = ref.watch(chemistVisitsProvider);

    return Scaffold(
      backgroundColor: Colors.transparent,
      floatingActionButton: FloatingActionButton.extended(
        onPressed: () async {
          final created = await Navigator.of(context).push<bool>(
            MaterialPageRoute(builder: (_) => const ChemistVisitFormScreen()),
          );
          if (created == true) {
            ref.read(chemistVisitsProvider.notifier).refresh();
          }
        },
        icon: const Icon(Icons.add),
        label: const Text('New visit'),
      ),
      body: PaginatedList<ChemistVisit>(
        state: state,
        onRefresh: () => ref.read(chemistVisitsProvider.notifier).refresh(),
        onLoadMore: () => ref.read(chemistVisitsProvider.notifier).loadMore(),
        emptyMessage: 'No chemist visits yet. Tap + to log one.',
        itemBuilder: (context, visit) => _ChemistVisitCard(visit: visit),
      ),
    );
  }
}

class _ChemistVisitCard extends StatelessWidget {
  const _ChemistVisitCard({required this.visit});

  final ChemistVisit visit;

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
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
                    visit.pharmacyName.isEmpty ? 'Chemist visit' : visit.pharmacyName,
                    style: theme.textTheme.titleMedium
                        ?.copyWith(fontWeight: FontWeight.bold),
                  ),
                ),
                Text(visit.date, style: theme.textTheme.bodySmall),
              ],
            ),
            const SizedBox(height: 4),
            Text(
              '${visit.hospitalName} · ${visit.regionName}',
              style: theme.textTheme.bodySmall,
            ),
            if (visit.currentProducts.isNotEmpty) ...[
              const SizedBox(height: 8),
              Text('Current: ${visit.currentProducts}',
                  style: theme.textTheme.bodyMedium),
            ],
            if (visit.productsNeeded.isNotEmpty) ...[
              const SizedBox(height: 10),
              Text('Needed (qty ${visit.quantity})',
                  style: theme.textTheme.labelMedium),
              const SizedBox(height: 6),
              ProductBadges(products: visit.productsNeeded),
            ],
            if (visit.notes.isNotEmpty) ...[
              const SizedBox(height: 10),
              Text(visit.notes, style: theme.textTheme.bodyMedium),
            ],
          ],
        ),
      ),
    );
  }
}
