import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../core/widgets/paginated_list.dart';
import '../../models/visit.dart';
import '../../providers/visit_providers.dart';
import 'doctor_visit_form_screen.dart';
import 'widgets/product_badges.dart';

class DoctorVisitsTab extends ConsumerWidget {
  const DoctorVisitsTab({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final state = ref.watch(doctorVisitsProvider);

    return Scaffold(
      backgroundColor: Colors.transparent,
      floatingActionButton: FloatingActionButton.extended(
        onPressed: () async {
          final created = await Navigator.of(context).push<bool>(
            MaterialPageRoute(builder: (_) => const DoctorVisitFormScreen()),
          );
          if (created == true) {
            ref.read(doctorVisitsProvider.notifier).refresh();
          }
        },
        icon: const Icon(Icons.add),
        label: const Text('New visit'),
      ),
      body: PaginatedList<DoctorVisit>(
        state: state,
        onRefresh: () => ref.read(doctorVisitsProvider.notifier).refresh(),
        onLoadMore: () => ref.read(doctorVisitsProvider.notifier).loadMore(),
        emptyMessage: 'No doctor visits yet. Tap + to log one.',
        itemBuilder: (context, visit) => _DoctorVisitCard(visit: visit),
      ),
    );
  }
}

class _DoctorVisitCard extends StatelessWidget {
  const _DoctorVisitCard({required this.visit});

  final DoctorVisit visit;

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
                    visit.doctorName.isEmpty
                        ? 'Doctor visit'
                        : 'Dr. ${visit.doctorName}',
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
            if (visit.products.isNotEmpty) ...[
              const SizedBox(height: 10),
              ProductBadges(products: visit.products),
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
