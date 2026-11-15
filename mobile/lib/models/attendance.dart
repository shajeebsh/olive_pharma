class AttendanceRecord {
  const AttendanceRecord({
    required this.id,
    required this.date,
    required this.checkIn,
    this.checkOut,
    this.notes = '',
    this.duration,
    this.isOpen = true,
  });

  final int id;
  final String date;
  final String checkIn;
  final String? checkOut;
  final String notes;
  final String? duration;
  final bool isOpen;

  factory AttendanceRecord.fromJson(Map<String, dynamic> json) =>
      AttendanceRecord(
        id: json['id'] as int,
        date: json['date'] as String? ?? '',
        checkIn: json['check_in'] as String? ?? '',
        checkOut: json['check_out'] as String?,
        notes: json['notes'] as String? ?? '',
        duration: json['duration'] as String?,
        isOpen: json['is_open'] as bool? ?? false,
      );
}
