import 'package:fl_chart/fl_chart.dart';
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:intl/intl.dart';

import '../../core/theme/app_theme.dart';
import '../../core/widgets/state_views.dart';
import '../../models/dashboard.dart';
import '../../providers/dashboard_provider.dart';

class DashboardScreen extends ConsumerWidget {
  const DashboardScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final range = ref.watch(dashboardRangeProvider);
    final dashboard = ref.watch(dashboardProvider);
    final dateFormat = DateFormat('d MMM');

    return Scaffold(
      appBar: AppBar(
        title: const Text('Dashboard'),
        actions: [
          TextButton.icon(
            onPressed: () => _pickRange(context, ref, range),
            icon: const Icon(Icons.date_range, color: Colors.white, size: 18),
            label: Text(
              '${dateFormat.format(range.start)} – ${dateFormat.format(range.end)}',
              style: const TextStyle(color: Colors.white),
            ),
          ),
        ],
      ),
      body: RefreshIndicator(
        onRefresh: () async => ref.refresh(dashboardProvider.future),
        child: dashboard.when(
          loading: () => const LoadingView(),
          error: (error, _) => ListView(
            children: [
              SizedBox(
                height: MediaQuery.of(context).size.height * 0.6,
                child: ErrorView(
                  message: '$error',
                  onRetry: () => ref.invalidate(dashboardProvider),
                ),
              ),
            ],
          ),
          data: (data) => _DashboardBody(data: data),
        ),
      ),
    );
  }

  Future<void> _pickRange(
    BuildContext context,
    WidgetRef ref,
    DateTimeRange current,
  ) async {
    final picked = await showDateRangePicker(
      context: context,
      firstDate: DateTime(2020),
      lastDate: DateTime.now(),
      initialDateRange: current,
    );
    if (picked != null) {
      ref.read(dashboardRangeProvider.notifier).state = picked;
    }
  }
}

class _DashboardBody extends StatelessWidget {
  const _DashboardBody({required this.data});

  final DashboardData data;

  @override
  Widget build(BuildContext context) {
    final currency = NumberFormat.currency(symbol: '₹', decimalDigits: 0);

    return ListView(
      padding: const EdgeInsets.all(16),
      children: [
        GridView.count(
          crossAxisCount: 2,
          shrinkWrap: true,
          physics: const NeverScrollableScrollPhysics(),
          mainAxisSpacing: 12,
          crossAxisSpacing: 12,
          childAspectRatio: 1.5,
          children: [
            _KpiCard(
              label: 'Doctor Visits',
              value: '${data.doctorVisits}',
              icon: Icons.person_badge_outlined,
              color: AppTheme.primary,
            ),
            _KpiCard(
              label: 'Chemist Visits',
              value: '${data.chemistVisits}',
              icon: Icons.local_pharmacy_outlined,
              color: AppTheme.navigation,
            ),
            _KpiCard(
              label: 'Check-ins',
              value: '${data.checkins}',
              icon: Icons.access_time,
              color: AppTheme.warning,
            ),
            _KpiCard(
              label: 'Sales Amount',
              value: currency.format(data.salesAmount),
              icon: Icons.currency_rupee,
              color: AppTheme.success,
            ),
          ],
        ),
        const SizedBox(height: 24),
        _KpiChart(data: data),
        const SizedBox(height: 24),
        Text(
          'Recent Visits',
          style: Theme.of(context)
              .textTheme
              .titleMedium
              ?.copyWith(fontWeight: FontWeight.bold),
        ),
        const SizedBox(height: 12),
        if (data.recentVisits.isEmpty)
          Card(
            child: SizedBox(
              height: 140,
              child: EmptyView(message: 'No visits in this period.'),
            ),
          )
        else
          Card(
            child: Column(
              children: [
                for (final visit in data.recentVisits)
                  ListTile(
                    leading: CircleAvatar(
                      backgroundColor:
                          (visit.isDoctor ? AppTheme.primary : AppTheme.navigation)
                              .withOpacity(0.12),
                      child: Icon(
                        visit.isDoctor
                            ? Icons.person_badge_outlined
                            : Icons.local_pharmacy_outlined,
                        color:
                            visit.isDoctor ? AppTheme.primary : AppTheme.navigation,
                      ),
                    ),
                    title: Text(visit.title),
                    subtitle: Text('${visit.subtitle} · ${visit.date}'),
                  ),
              ],
            ),
          ),
      ],
    );
  }
}

class _KpiCard extends StatelessWidget {
  const _KpiCard({
    required this.label,
    required this.value,
    required this.icon,
    required this.color,
  });

  final String label;
  final String value;
  final IconData icon;
  final Color color;

  @override
  Widget build(BuildContext context) {
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(14),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          mainAxisAlignment: MainAxisAlignment.spaceBetween,
          children: [
            Icon(icon, color: color),
            Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  value,
                  style: Theme.of(context)
                      .textTheme
                      .titleLarge
                      ?.copyWith(fontWeight: FontWeight.bold),
                ),
                Text(label, style: Theme.of(context).textTheme.bodySmall),
              ],
            ),
          ],
        ),
      ),
    );
  }
}

class _KpiChart extends StatelessWidget {
  const _KpiChart({required this.data});

  final DashboardData data;

  @override
  Widget build(BuildContext context) {
    final maxValue = [
      data.doctorVisits,
      data.chemistVisits,
      data.checkins,
    ].fold<int>(1, (a, b) => a > b ? a : b);

    return Card(
      child: Padding(
        padding: const EdgeInsets.fromLTRB(16, 20, 16, 12),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              'Activity',
              style: Theme.of(context)
                  .textTheme
                  .titleMedium
                  ?.copyWith(fontWeight: FontWeight.bold),
            ),
            const SizedBox(height: 16),
            SizedBox(
              height: 160,
              child: BarChart(
                BarChartData(
                  maxY: (maxValue + 1).toDouble(),
                  gridData: const FlGridData(show: false),
                  borderData: FlBorderData(show: false),
                  titlesData: FlTitlesData(
                    leftTitles: const AxisTitles(
                      sideTitles: SideTitles(showTitles: false),
                    ),
                    rightTitles: const AxisTitles(
                      sideTitles: SideTitles(showTitles: false),
                    ),
                    topTitles: const AxisTitles(
                      sideTitles: SideTitles(showTitles: false),
                    ),
                    bottomTitles: AxisTitles(
                      sideTitles: SideTitles(
                        showTitles: true,
                        getTitlesWidget: (value, meta) {
                          const labels = ['Doctor', 'Chemist', 'Check-in'];
                          if (value.toInt() >= labels.length) {
                            return const SizedBox.shrink();
                          }
                          return Padding(
                            padding: const EdgeInsets.only(top: 6),
                            child: Text(
                              labels[value.toInt()],
                              style: const TextStyle(fontSize: 11),
                            ),
                          );
                        },
                      ),
                    ),
                  ),
                  barGroups: [
                    _bar(0, data.doctorVisits, AppTheme.primary),
                    _bar(1, data.chemistVisits, AppTheme.navigation),
                    _bar(2, data.checkins, AppTheme.warning),
                  ],
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }

  BarChartGroupData _bar(int x, int value, Color color) {
    return BarChartGroupData(
      x: x,
      barRods: [
        BarChartRodData(
          toY: value.toDouble(),
          color: color,
          width: 28,
          borderRadius: BorderRadius.circular(6),
        ),
      ],
    );
  }
}
