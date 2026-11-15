class Region {
  const Region({
    required this.id,
    required this.name,
    this.code = '',
    this.state = '',
    this.country = '',
  });

  final int id;
  final String name;
  final String code;
  final String state;
  final String country;

  String get label {
    final location = [state, country].where((p) => p.isNotEmpty).join(', ');
    return location.isEmpty ? name : '$name ($location)';
  }

  factory Region.fromJson(Map<String, dynamic> json) => Region(
        id: json['id'] as int,
        name: json['name'] as String? ?? '',
        code: json['code'] as String? ?? '',
        state: json['state'] as String? ?? '',
        country: json['country'] as String? ?? '',
      );
}

class Hospital {
  const Hospital({
    required this.id,
    required this.name,
    required this.region,
    this.regionName = '',
    this.city = '',
  });

  final int id;
  final String name;
  final int region;
  final String regionName;
  final String city;

  factory Hospital.fromJson(Map<String, dynamic> json) => Hospital(
        id: json['id'] as int,
        name: json['name'] as String? ?? '',
        region: json['region'] as int,
        regionName: json['region_name'] as String? ?? '',
        city: json['city'] as String? ?? '',
      );
}

class Doctor {
  const Doctor({
    required this.id,
    required this.name,
    required this.hospital,
    this.hospitalName = '',
    this.speciality = '',
  });

  final int id;
  final String name;
  final int hospital;
  final String hospitalName;
  final String speciality;

  String get displayName => 'Dr. $name';

  factory Doctor.fromJson(Map<String, dynamic> json) => Doctor(
        id: json['id'] as int,
        name: json['name'] as String? ?? '',
        hospital: json['hospital'] as int,
        hospitalName: json['hospital_name'] as String? ?? '',
        speciality: json['speciality'] as String? ?? '',
      );
}

class Pharmacy {
  const Pharmacy({
    required this.id,
    required this.name,
    required this.region,
    this.regionName = '',
    this.hospital,
    this.hospitalName,
    this.locality = '',
  });

  final int id;
  final String name;
  final int region;
  final String regionName;
  final int? hospital;
  final String? hospitalName;
  final String locality;

  factory Pharmacy.fromJson(Map<String, dynamic> json) => Pharmacy(
        id: json['id'] as int,
        name: json['name'] as String? ?? '',
        region: json['region'] as int,
        regionName: json['region_name'] as String? ?? '',
        hospital: json['hospital'] as int?,
        hospitalName: json['hospital_name'] as String?,
        locality: json['locality'] as String? ?? '',
      );
}

class Product {
  const Product({
    required this.id,
    required this.name,
    this.sku = '',
    this.form = '',
    this.strength = '',
    this.active = true,
  });

  final int id;
  final String name;
  final String sku;
  final String form;
  final String strength;
  final bool active;

  String get label => strength.isEmpty ? name : '$name ($strength)';

  factory Product.fromJson(Map<String, dynamic> json) => Product(
        id: json['id'] as int,
        name: json['name'] as String? ?? '',
        sku: json['sku'] as String? ?? '',
        form: json['form'] as String? ?? '',
        strength: json['strength'] as String? ?? '',
        active: json['active'] as bool? ?? true,
      );
}
