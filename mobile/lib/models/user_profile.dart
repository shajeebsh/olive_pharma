class UserProfile {
  const UserProfile({
    required this.id,
    required this.username,
    required this.role,
    this.email = '',
    this.firstName = '',
    this.lastName = '',
    this.phone = '',
    this.employeeCode = '',
    this.region,
    this.regionName,
  });

  final int id;
  final String username;
  final String role;
  final String email;
  final String firstName;
  final String lastName;
  final String phone;
  final String employeeCode;
  final int? region;
  final String? regionName;

  bool get isAdmin => role == 'admin';
  bool get isRepresentative => role == 'rep';

  String get displayName {
    final name = '$firstName $lastName'.trim();
    return name.isEmpty ? username : name;
  }

  String get roleLabel {
    switch (role) {
      case 'admin':
        return 'Admin';
      case 'staff':
        return 'Staff';
      default:
        return 'Representative';
    }
  }

  factory UserProfile.fromJson(Map<String, dynamic> json) => UserProfile(
        id: json['id'] as int,
        username: json['username'] as String? ?? '',
        role: json['role'] as String? ?? 'rep',
        email: json['email'] as String? ?? '',
        firstName: json['first_name'] as String? ?? '',
        lastName: json['last_name'] as String? ?? '',
        phone: json['phone'] as String? ?? '',
        employeeCode: json['employee_code'] as String? ?? '',
        region: json['region'] as int?,
        regionName: json['region_name'] as String?,
      );

  Map<String, dynamic> toJson() => {
        'id': id,
        'username': username,
        'role': role,
        'email': email,
        'first_name': firstName,
        'last_name': lastName,
        'phone': phone,
        'employee_code': employeeCode,
        'region': region,
        'region_name': regionName,
      };
}
