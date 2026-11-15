import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../core/api/api_exception.dart';
import '../../core/theme/app_theme.dart';
import '../../core/widgets/paginated_list.dart';
import '../../models/attendance.dart';
import '../../providers/attendance_provider.dart';
import '../../providers/core_providers.dart';

class AttendanceScreen extends ConsumerWidget {
  const AttendanceScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final state = ref.watch(attendanceProvider);

    return Scaffold(
      appBar: AppBar(
        title: const Text('Attendance'),
        actions: [
          IconButton(
            tooltip: 'Check in',
            icon: const Icon(Icons.login),
            onPressed: () => _submit(context, ref, isCheckIn: true),
          ),
          IconButton(
            tooltip: 'Check out',
            icon: const Icon(Icons.logout),
            onPressed: () => _submit(context, ref, isCheckIn: false),
          ),
        ],
      ),
      body: PaginatedList<AttendanceRecord>(
        state: state,
        onRefresh: () => ref.read(attendanceProvider.notifier).refresh(),
        onLoadMore: () => ref.read(attendanceProvider.notifier).loadMore(),
        emptyMessage: 'No attendance records yet.',
        itemBuilder: (context, record) => _AttendanceCard(record: record),
      ),
    );
  }

  Future<void> _submit(
    BuildContext context,
    WidgetRef ref, {
    required bool isCheckIn,
  }) async {
    final notes = await _notesDialog(context, isCheckIn: isCheckIn);
    if (notes == null) return;
    final repository = ref.read(attendanceRepositoryProvider);
    final messenger = ScaffoldMessenger.of(context);
    try {
      if (isCheckIn) {
        await repository.checkIn(notes: notes);
      } else {
        await repository.checkOut(notes: notes);
      }
      ref.read(attendanceProvider.notifier).refresh();
      messenger.showSnackBar(
        SnackBar(content: Text(isCheckIn ? 'Checked in.' : 'Checked out.')),
      );
    } on ApiException catch (error) {
      messenger.showSnackBar(SnackBar(content: Text(error.message)));
    }
  }

  Future<String?> _notesDialog(
    BuildContext context, {
    required bool isCheckIn,
  }) {
    final controller = TextEditingController();
    return showDialog<String>(
      context: context,
      builder: (context) => AlertDialog(
        title: Text(isCheckIn ? 'Check in' : 'Check out'),
        content: Column(
          mainAxisSize: MainAxisSize.min,
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              'The current server time will be recorded. No location is captured.',
              style: Theme.of(context).textTheme.bodySmall,
            ),
            const SizedBox(height: 12),
            TextField(
              controller: controller,
              maxLines: 3,
              decoration: const InputDecoration(labelText: 'Notes (optional)'),
            ),
          ],
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.of(context).pop(),
            child: const Text('Cancel'),
          ),
          FilledButton(
            onPressed: () => Navigator.of(context).pop(controller.text.trim()),
            child: Text(isCheckIn ? 'Check in' : 'Check out'),
          ),
        ],
      ),
    );
  }
}

class _AttendanceCard extends StatelessWidget {
  const _AttendanceCard({required this.record});

  final AttendanceRecord record;

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(14),
        child: Row(
          children: [
            Container(
              width: 44,
              height: 44,
              alignment: Alignment.center,
              decoration: BoxDecoration(
                color: (record.isOpen ? AppTheme.warning : AppTheme.success)
                    .withOpacity(0.12),
                borderRadius: BorderRadius.circular(12),
              ),
              child: Icon(
                record.isOpen ? Icons.timelapse : Icons.check_circle_outline,
                color: record.isOpen ? AppTheme.warning : AppTheme.success,
              ),
            ),
            const SizedBox(width: 12),
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    record.date,
                    style: theme.textTheme.titleMedium
                        ?.copyWith(fontWeight: FontWeight.bold),
                  ),
                  const SizedBox(height: 2),
                  Text(
                    'In ${record.checkIn} · '
                    '${record.checkOut == null ? 'Out —' : 'Out ${record.checkOut}'}',
                    style: theme.textTheme.bodyMedium,
                  ),
                  if (record.notes.isNotEmpty)
                    Text(record.notes, style: theme.textTheme.bodySmall),
                ],
              ),
            ),
            if (record.duration != null)
              Text(record.duration!, style: theme.textTheme.labelLarge),
          ],
        ),
      ),
    );
  }
}
