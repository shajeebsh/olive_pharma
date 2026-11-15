class RecentVisit {
  const RecentVisit({
    required this.kind,
    required this.id,
    required this.date,
    required this.title,
    required this.subtitle,
  });

  final String kind;
  final int id;
  final String date;
  final String title;
  final String subtitle;

  bool get isDoctor => kind == 'doctor';

  factory RecentVisit.fromJson(Map<String, dynamic> json) => RecentVisit(
        kind: json['kind'] as String? ?? 'doctor',
        id: json['id'] as int,
        date: json['date'] as String? ?? '',
        title: json['title'] as String? ?? '',
        subtitle: json['subtitle'] as String? ?? '',
      );
}

class DashboardData {
  const DashboardData({
    required this.startDate,
    required this.endDate,
    required this.doctorVisits,
    required this.chemistVisits,
    required this.checkins,
    required this.salesAmount,
    required this.salesCount,
    required this.recentVisits,
  });

  final String startDate;
  final String endDate;
  final int doctorVisits;
  final int chemistVisits;
  final int checkins;
  final double salesAmount;
  final int salesCount;
  final List<RecentVisit> recentVisits;

  factory DashboardData.fromJson(Map<String, dynamic> json) {
    final kpis = json['kpis'] as Map<String, dynamic>? ?? {};
    return DashboardData(
      startDate: json['start_date'] as String? ?? '',
      endDate: json['end_date'] as String? ?? '',
      doctorVisits: kpis['doctor_visits'] as int? ?? 0,
      chemistVisits: kpis['chemist_visits'] as int? ?? 0,
      checkins: kpis['checkins'] as int? ?? 0,
      salesAmount: double.tryParse('${kpis['sales_amount']}') ?? 0,
      salesCount: kpis['sales_count'] as int? ?? 0,
      recentVisits: (json['recent_visits'] as List<dynamic>? ?? [])
          .map((e) => RecentVisit.fromJson(e as Map<String, dynamic>))
          .toList(),
    );
  }
}
